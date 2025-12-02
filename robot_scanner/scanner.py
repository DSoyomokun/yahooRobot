"""
Main scanner module for the robot.
Orchestrates the entire scanning pipeline.
"""
import cv2
import logging
from typing import Optional, Dict
from datetime import datetime

from .bubble_detector import BubbleDetector
from .name_reader import NameReader
from .grader import Grader
from .storage import Storage

# Try to import config, fallback to defaults
try:
    from . import config
except ImportError:
    config = None

logger = logging.getLogger(__name__)


def capture_image(camera_index: int = 0, save_path: str = "scan.jpg") -> str:
    """
    Simple camera capture function.
    
    Args:
        camera_index: Camera device index (default: 0)
        save_path: Path to save the captured image (default: "scan.jpg")
        
    Returns:
        Path to saved image
        
    Raises:
        Exception: If camera fails to capture image
    """
    cam = cv2.VideoCapture(camera_index)
    ret, frame = cam.read()
    cam.release()
    
    if ret and frame is not None:
        cv2.imwrite(save_path, frame)
        return save_path
    else:
        raise Exception("Camera failed to capture image")


class RobotScanner:
    """Main scanner that coordinates all scanning components."""
    
    def __init__(self, camera_index: int = 0):
        """
        Initialize the robot scanner.
        
        Args:
            camera_index: Camera device index
        """
        self.camera_index = camera_index
        self.camera = None
        self.bubble_detector = BubbleDetector()
        self.name_reader = NameReader()
        self.grader = Grader()
        
        # Initialize storage based on config
        if config:
            db_type = getattr(config, 'DATABASE_TYPE', 'sqlite')
            if db_type == "sqlite":
                self.storage = Storage(db_type="sqlite", db_path=getattr(config, 'SQLITE_DB_PATH', None))
            elif db_type == "postgresql":
                self.storage = Storage(db_type="postgresql", **getattr(config, 'POSTGRESQL_CONFIG', {}))
            elif db_type == "mysql":
                self.storage = Storage(db_type="mysql", **getattr(config, 'MYSQL_CONFIG', {}))
            elif db_type == "mongodb":
                self.storage = Storage(db_type="mongodb", **getattr(config, 'MONGODB_CONFIG', {}))
            elif db_type == "json":
                self.storage = Storage(db_type="json", json_path=getattr(config, 'JSON_FILE_PATH', None))
            else:
                self.storage = Storage(db_type="sqlite")
        else:
            # Default to SQLite (no setup required)
            self.storage = Storage(db_type="sqlite")
        
    def capture_image(self, save_path: Optional[str] = None) -> Optional[cv2.typing.MatLike]:
        """
        Simple camera capture function.
        
        Args:
            save_path: Optional path to save the captured image
            
        Returns:
            Captured image or None if failed
        """
        cam = cv2.VideoCapture(self.camera_index)
        ret, frame = cam.read()
        cam.release()
        
        if ret and frame is not None:
            if save_path:
                cv2.imwrite(save_path, frame)
                logger.info(f"Image saved to {save_path}")
            return frame
        else:
            raise Exception("Camera failed to capture image")
    
    def scan_paper(self, image: Optional[cv2.typing.MatLike] = None) -> Optional[Dict]:
        """
        Complete scanning pipeline.
        
        Args:
            image: Optional pre-captured image (if None, captures from camera)
            
        Returns:
            Dictionary with scan results or None if failed
        """
        try:
            # Step 1: Capture image
            if image is None:
                logger.info("Capturing image from camera...")
                image = self.capture_image()
            
            if image is None:
                logger.error("Failed to capture image")
                return None
            
            # Step 2: Extract student name
            logger.info("Extracting student name...")
            student_name = self.name_reader.extract_name(image)
            
            # Step 3: Extract answers
            logger.info("Extracting answers from bubbles...")
            answers = self.bubble_detector.extract_answers(image)
            
            if not answers:
                logger.error("Failed to extract answers")
                return None
            
            # Step 4: Auto grading pipeline
            logger.info("Grading test...")
            grading_result = self.grader.grade(answers)  # answers_dict format: {"1": "B", "2": "D", ...}
            
            # Step 5: Prepare result data
            result = {
                'student_name': student_name or 'Unknown',
                'answers': answers,
                'score': grading_result.get('score', 0),
                'total_questions': grading_result.get('total_questions', 0),
                'correct': grading_result.get('correct', 0),
                'incorrect': grading_result.get('incorrect', 0),
                'unanswered': grading_result.get('unanswered', 0),
                'percentage': grading_result.get('percentage', 0.0),
                'scanned_at': datetime.now().isoformat()
            }
            
            # Step 6: Store results
            logger.info("Storing results...")
            self.storage.save_result(result)
            
            logger.info(f"Scan complete: {student_name} - {result['percentage']:.1f}%")
            return result
            
        except Exception as e:
            logger.error(f"Error in scan pipeline: {e}", exc_info=True)
            return None
    
    def release(self):
        """Release camera resources."""
        if self.camera is not None:
            self.camera.release()
            self.camera = None
            logger.info("Camera released")

