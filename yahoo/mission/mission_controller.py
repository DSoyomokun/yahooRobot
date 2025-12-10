"""
Mission controller for test paper scanning.
Coordinates scanner, camera, LED feedback, and robot movement.
"""
import logging
import time
import cv2
import numpy as np
from typing import Optional, Dict

from .scanner.scan_control import ScanControl
from yahoo.io.camera import PiCam
from yahoo.io.leds import LEDController

logger = logging.getLogger(__name__)


class MissionController:
    """Main mission controller that coordinates test scanning operations."""
    
    def __init__(self, robot=None, camera_index: int = 0, simulate: bool = False):
        """
        Initialize mission controller.
        
        Args:
            robot: Robot instance (from yahoo.robot.Robot)
            camera_index: Camera device index
            simulate: If True, run in simulation mode
        """
        self.robot = robot
        self.simulate = simulate or (robot is None or getattr(robot, 'simulate', False))
        
        # Initialize components
        self.scanner = ScanControl(camera_index=camera_index)
        self.camera = PiCam(device_index=camera_index, simulate=self.simulate)
        self.leds = LEDController(robot=robot, simulate=self.simulate)
        
        # State management
        self.running = False
        self.current_desk = None
        
        logger.info("Mission controller initialized")
    
    def paper_detected(self, image: Optional[np.ndarray] = None) -> bool:
        """
        Detect if paper is present in the camera view.
        Uses simple edge detection and contour analysis.
        
        Args:
            image: Optional pre-captured image (if None, captures from camera)
            
        Returns:
            True if paper is detected, False otherwise
        """
        if image is None:
            image = self.camera.capture()
            if image is None:
                return False
        
        # Convert to grayscale
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image
        
        # Apply edge detection
        edges = cv2.Canny(gray, 50, 150)
        
        # Find contours
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if not contours:
            return False
        
        # Check for large rectangular contours (paper-like shapes)
        h, w = gray.shape
        min_area = (w * h) * 0.1  # At least 10% of image
        
        for contour in contours:
            area = cv2.contourArea(contour)
            if area < min_area:
                continue
            
            # Check if roughly rectangular
            peri = cv2.arcLength(contour, True)
            approx = cv2.approxPolyDP(contour, 0.02 * peri, True)
            
            if len(approx) >= 4:  # Has at least 4 corners (rectangle-like)
                return True
        
        return False
    
    def process_test(self, image: Optional[np.ndarray] = None, save_visualizations: bool = True) -> Optional[Dict]:
        """
        Process a test paper: scan, grade, and return results.
        Saves processed images to detection_visualization folder.
        
        Args:
            image: Optional pre-captured image (if None, captures from camera)
            save_visualizations: If True, save detection visualizations (default: True)
            
        Returns:
            Dictionary with scan results or None if failed
        """
        try:
            # Set LED to analyzing
            self.leds.analyzing()
            
            # If saving visualizations, set up folder structure
            if save_visualizations and image is not None:
                from pathlib import Path
                from datetime import datetime
                import cv2
                
                # Create organized folder structure
                base_dir = Path(__file__).parent.parent / "scanner" / "tests" / "captured_images"
                vis_dir = base_dir / "detection_visualization"
                vis_dir.mkdir(parents=True, exist_ok=True)
                
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                
                # Save processed image ready for grading
                processed_path = vis_dir / f"processed_{timestamp}.jpg"
                cv2.imwrite(str(processed_path), image)
                logger.info(f"Processed image saved to: {processed_path}")
            
            # Scan the paper using new pipeline
            result = self.scanner.process_test(image=image, store=False)
            
            if result is None:
                self.leds.fail()
                logger.error("Failed to process test")
                return None
            
            # Save visualizations if requested
            if save_visualizations and image is not None:
                try:
                    self._save_detection_visualizations(image, result, timestamp)
                except Exception as e:
                    logger.warning(f"Failed to save visualizations: {e}")
            
            # Set LED based on result
            if result.get('percentage', 0) >= 0:
                self.leds.success()
            else:
                self.leds.fail()
            
            return result
            
        except Exception as e:
            logger.error(f"Error processing test: {e}", exc_info=True)
            self.leds.fail()
            return None
    
    def _save_detection_visualizations(self, image: np.ndarray, result: Dict, timestamp: str):
        """Save detection visualizations to detection_visualization folder."""
        from pathlib import Path
        import cv2
        
        base_dir = Path(__file__).parent.parent / "scanner" / "tests" / "captured_images"
        vis_dir = base_dir / "detection_visualization"
        vis_dir.mkdir(parents=True, exist_ok=True)
        
        # Save name region
        try:
            from yahoo.mission.scanner.name_reader import NameReader
            name_reader = NameReader()
            name_region = name_reader.extract_name_region(image)
            if name_region.size > 0:
                name_path = vis_dir / f"name_region_{timestamp}.jpg"
                cv2.imwrite(str(name_path), name_region)
                logger.debug(f"Name region saved: {name_path}")
        except Exception as e:
            logger.warning(f"Failed to save name region: {e}")
        
        # Save bubble detection visualization
        try:
            from yahoo.mission.scanner.bubble_detector import BubbleDetector
            bubble_detector = BubbleDetector()
            
            processed = bubble_detector.preprocess(image)
            bubbles = bubble_detector.detect_bubbles(processed)
            
            if bubbles:
                vis_frame = image.copy()
                if len(image.shape) == 3:
                    gray_frame = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                else:
                    gray_frame = image
                
                # Draw bubbles
                for bubble in bubbles[:50]:
                    x, y, w, h = bubble['bounding_rect']
                    fill = bubble_detector.calculate_fill(gray_frame, bubble)
                    color = (0, 255, 0) if fill >= bubble_detector.fill_threshold else (0, 0, 255)
                    cv2.rectangle(vis_frame, (x, y), (x+w, y+h), color, 2)
                    cv2.putText(vis_frame, f"{fill:.0%}", (x, y-5),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.4, color, 1)
                
                # Draw name region
                h, w = image.shape[:2]
                name_top = int(h * 0.05)
                name_bottom = int(h * 0.15)
                name_left = int(w * 0.10)
                name_right = int(w * 0.50)
                cv2.rectangle(vis_frame, (name_left, name_top), (name_right, name_bottom), (255, 255, 0), 3)
                cv2.putText(vis_frame, "NAME REGION", (name_left, name_top - 10),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
                
                bubble_path = vis_dir / f"bubble_detection_{timestamp}.jpg"
                cv2.imwrite(str(bubble_path), vis_frame)
                logger.debug(f"Bubble detection visualization saved: {bubble_path}")
        except Exception as e:
            logger.warning(f"Failed to save bubble visualization: {e}")
    
    def update_led(self, results: Optional[Dict]):
        """
        Update LED status based on scan results.
        
        Args:
            results: Scan results dictionary or None
        """
        if results is None:
            self.leds.fail()
        elif results.get('percentage', 0) >= 70:
            self.leds.success()
            # Blink green for high score
            self.leds.blink("green", times=2, duration=0.15)
        elif results.get('percentage', 0) >= 0:
            self.leds.success()
        else:
            self.leds.fail()
    
    def store_results(self, results: Dict) -> bool:
        """
        Store scan results to database.
        
        Args:
            results: Scan results dictionary
            
        Returns:
            True if stored successfully, False otherwise
        """
        try:
            success = self.scanner.storage.save_result(results)
            if success:
                logger.info(f"Results stored: {results.get('student_name')} - {results.get('percentage'):.1f}%")
            return success
        except Exception as e:
            logger.error(f"Error storing results: {e}")
            return False
    
    def move_to_next_desk(self):
        """
        Move robot to the next desk.
        This should integrate with navigation system.
        """
        if self.simulate:
            logger.info("SIMULATION: Moving to next desk")
            time.sleep(1)  # Simulate movement time
            return
        
        if self.robot is None:
            logger.warning("No robot instance, cannot move")
            return
        
        try:
            # Stop robot first (should already be stopped, but ensure)
            if hasattr(self.robot, 'stop'):
                self.robot.stop()
            
            # TODO: Integrate with navigation system
            # Example: self.robot.nav.move_to_desk(self.current_desk + 1)
            # For now, just log
            logger.info("Moving to next desk (navigation not yet integrated)")
            
        except Exception as e:
            logger.error(f"Error moving to next desk: {e}")
    
    def run(self, continuous: bool = True):
        """
        Main mission loop.
        
        Args:
            continuous: If True, run continuously (default: True)
        """
        self.running = True
        logger.info("Starting mission controller")
        
        try:
            while self.running:
                # Step 1: Check for paper
                if self.paper_detected():
                    logger.info("Paper detected!")
                    
                    # Step 2: Stop robot
                    if self.robot and hasattr(self.robot, 'stop'):
                        self.robot.stop()
                        logger.info("Robot stopped")
                    
                    # Step 3: Set LED to scanning
                    self.leds.scanning()
                    
                    # Step 4: Capture image
                    image = self.camera.capture()
                    if image is None:
                        logger.error("Failed to capture image")
                        self.leds.fail()
                        time.sleep(1)
                        continue
                    
                    # Step 5: Process test
                    results = self.process_test(image)
                    
                    # Step 6: Update LED
                    self.update_led(results)
                    
                    # Step 7: Store results
                    if results:
                        self.store_results(results)
                    
                    # Step 8: Move to next desk
                    if continuous:
                        time.sleep(0.5)  # Brief pause
                        self.move_to_next_desk()
                
                else:
                    # No paper detected, continue moving/searching
                    if not continuous:
                        break
                    
                    time.sleep(0.1)  # Small delay before next check
                    
        except KeyboardInterrupt:
            logger.info("Mission controller stopped by user")
        except Exception as e:
            logger.error(f"Error in mission loop: {e}", exc_info=True)
        finally:
            self.stop()
    
    def stop(self):
        """Stop the mission controller."""
        self.running = False
        self.leds.off()
        if self.camera:
            self.camera.release()
        logger.info("Mission controller stopped")
    
    def scan_single_paper(self) -> Optional[Dict]:
        """
        Scan a single paper (non-continuous mode).
        Useful for testing or manual triggering.
        
        Returns:
            Scan results or None if failed
        """
        try:
            # Capture image
            image = self.camera.capture()
            if image is None:
                logger.error("Failed to capture image")
                return None
            
            # Process test
            results = self.process_test(image)
            
            # Update LED
            self.update_led(results)
            
            # Store results
            if results:
                self.store_results(results)
            
            return results
            
        except Exception as e:
            logger.error(f"Error in single paper scan: {e}", exc_info=True)
            self.leds.fail()
            return None

