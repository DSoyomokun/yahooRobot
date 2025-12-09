"""
Main scanner control module - orchestrates the complete pipeline.
This is the central entry point for the scanning system.
"""
import cv2
import numpy as np
import logging
from typing import Optional, Dict, Union
from pathlib import Path

from .alignment.aligner import align_form, align_form_simple
from .alignment.roi_extractor import extract_rois
from .name.name_pipeline import NamePipeline
from .bubbles.bubble_detector import BubbleDetector
from .grading.score import ScoreCalculator
from .grading.formatter import format_result
from .grading.saver import ResultSaver

# Use centralized AI services
try:
    from yahoo.ai.service import AIService
    from yahoo.ai.vectordb import VectorDB
    AI_SERVICES_AVAILABLE = True
except ImportError:
    AI_SERVICES_AVAILABLE = False

logger = logging.getLogger(__name__)


class ScanControl:
    """
    Main scanner control - orchestrates the complete pipeline.
    
    Pipeline:
    1. Capture/load image
    2. Align form to template
    3. Extract ROIs (name + bubbles)
    4. Extract name (OCR → Vector DB → LLM)
    5. Extract answers (bubble detection)
    6. Calculate score
    7. Save results
    """
    
    def __init__(self, 
                 camera_index: int = 0,
                 use_paddleocr: bool = True,
                 openai_client=None,
                 vector_db=None):
        """
        Initialize scan control.
        
        Args:
            camera_index: Camera device index
            use_paddleocr: If True, use PaddleOCR (better for handwriting)
            openai_client: OpenAI client instance (if None, uses centralized AIService)
            vector_db: Vector database instance (if None, uses centralized VectorDB if available)
        """
        self.camera_index = camera_index
        self.camera = None
        
        # Get centralized AI services if not provided
        if openai_client is None and AI_SERVICES_AVAILABLE:
            ai_service = AIService()
            openai_client = ai_service.openai
        
        if vector_db is None and AI_SERVICES_AVAILABLE:
            try:
                vector_db = VectorDB()
                if not vector_db.is_available():
                    vector_db = None
            except Exception as e:
                logger.warning(f"Vector DB initialization failed: {e}")
                vector_db = None
        
        # Initialize pipeline components
        self.name_pipeline = NamePipeline(
            use_paddleocr=use_paddleocr,
            openai_client=openai_client,
            vector_db=vector_db
        )
        self.bubble_detector = BubbleDetector()
        self.score_calculator = ScoreCalculator()
        self.result_saver = ResultSaver(vector_db=vector_db)
        
        logger.info("ScanControl initialized")
    
    def capture_image(self) -> Optional[np.ndarray]:
        """
        Capture image from camera.
        
        Returns:
            Captured image (BGR) or None if failed
        """
        try:
            if self.camera is None:
                self.camera = cv2.VideoCapture(self.camera_index)
            
            ret, frame = self.camera.read()
            
            if ret and frame is not None:
                return frame
            else:
                logger.error("Camera capture failed")
                return None
                
        except Exception as e:
            logger.error(f"Camera capture error: {e}")
            return None
    
    def release_camera(self):
        """Release camera resources."""
        if self.camera is not None:
            self.camera.release()
            self.camera = None
    
    def process_test(self, 
                     image: Optional[Union[np.ndarray, str, Path]] = None,
                     store: bool = True) -> Optional[Dict]:
        """
        Process a test paper through the complete pipeline.
        
        Args:
            image: Input image (numpy array, file path, or None to capture from camera)
            store: If True, save results to database
            
        Returns:
            Dictionary with scan results or None if failed
            Format: {
                'student_name': str,
                'answers': {"1": "A", "2": "B", ...},
                'score': float,
                'total_questions': int,
                'correct': int,
                'incorrect': int,
                'unanswered': int,
                'percentage': float,
                'scanned_at': str
            }
        """
        try:
            # ============================================================
            # STEP 1: CAPTURE/LOAD IMAGE
            # ============================================================
            if image is None:
                logger.info("Capturing image from camera...")
                img = self.capture_image()
                if img is None:
                    logger.error("Failed to capture image")
                    return None
            elif isinstance(image, (str, Path)):
                logger.info(f"Loading image from file: {image}")
                img = cv2.imread(str(image))
                if img is None:
                    logger.error(f"Failed to load image: {image}")
                    return None
            else:
                img = image.copy()
            
            logger.info(f"Image loaded: {img.shape}")
            
            # ============================================================
            # STEP 2: ALIGN FORM
            # ============================================================
            logger.info("Aligning form to template...")
            h, w = img.shape[:2]
            
            # Check if image needs rotation (camera might be landscape)
            # Template is portrait: 2550x3300 (width x height)
            # If camera image is landscape, rotate it to portrait
            if w > h:
                logger.info(f"Rotating landscape image ({w}x{h}) to portrait")
                # Rotate 90 degrees clockwise
                img = cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE)
                h, w = img.shape[:2]
                logger.info(f"After rotation: {w}x{h}")
            
            # Try perspective alignment first (more accurate for camera captures)
            # Only fallback to simple resize if perspective transform fails
            aligned = align_form(img)
            
            if aligned is None:
                logger.warning("Form alignment failed, using simple alignment")
                aligned = align_form_simple(img)  # img is already rotated if needed
            # If perspective transform succeeded, use it (it's more accurate)
            # Don't override with simple alignment - the perspective transform is better
            
            logger.info(f"Form aligned: {aligned.shape}")
            
            # ============================================================
            # STEP 3: EXTRACT ROIs (dynamic detection only - no fallbacks)
            # ============================================================
            logger.info("Extracting ROIs with dynamic detection (no fallbacks)...")
            try:
                name_roi, bubbles_dict, bubble_positions = extract_rois(aligned)
                logger.info(f"✅ Name ROI: {name_roi.shape}, Bubbles: {len(bubbles_dict)}")
                logger.info(f"✅ Dynamically detected bubble positions for {len(bubble_positions)} questions")
            except ValueError as e:
                logger.error(f"Dynamic detection failed: {e}")
                raise ValueError(f"Cannot process form - dynamic detection required: {e}")
            
            # ============================================================
            # STEP 4: EXTRACT NAME (OCR → Vector DB → LLM)
            # ============================================================
            logger.info("Extracting student name...")
            student_name = self.name_pipeline.extract_name(name_roi)
            
            if not student_name:
                logger.warning("Name extraction failed, using 'Unknown'")
                student_name = "Unknown"
            
            logger.info(f"Detected name: {student_name}")
            
            # ============================================================
            # STEP 5: EXTRACT ANSWERS (Bubble Detection)
            # ============================================================
            logger.info("Detecting bubble answers...")
            detected_answers = self.bubble_detector.extract_answers(aligned, bubble_positions)
            logger.info(f"Detected {len([a for a in detected_answers.values() if a])} answers")
            
            # ============================================================
            # STEP 6: CALCULATE SCORE
            # ============================================================
            logger.info("Calculating score...")
            score_info = self.score_calculator.calculate_score(detected_answers)
            answer_pattern = self.score_calculator.format_answer_pattern(detected_answers)
            
            logger.info(f"Score: {score_info['score']}/{score_info['total_questions']} "
                       f"({score_info['percentage']:.1f}%)")
            
            # ============================================================
            # STEP 7: FORMAT RESULT
            # ============================================================
            result = format_result(
                student_name=student_name,
                answers=detected_answers,
                score_info=score_info,
                answer_pattern=answer_pattern
            )
            
            # ============================================================
            # STEP 8: SAVE RESULTS
            # ============================================================
            if store:
                logger.info("Saving results...")
                self.result_saver.save_result(result)
            
            logger.info("✅ Pipeline complete!")
            return result
            
        except Exception as e:
            logger.error(f"Pipeline failed: {e}", exc_info=True)
            return None
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - release camera."""
        self.release_camera()

