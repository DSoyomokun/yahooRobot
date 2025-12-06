"""
Unified camera interface for Mac (development) and Raspberry Pi (production).
Supports both OpenCV VideoCapture and PiCamera2.
"""
import cv2
import logging
import time
import numpy as np
from typing import Optional, Tuple
from PIL import Image

logger = logging.getLogger(__name__)


class PiCam:
    """Unified camera interface for cross-platform use."""
    
    def __init__(self, device_index: int = 0, width: int = 640, height: int = 480, simulate: bool = False):
        """
        Initialize camera.
        
        Args:
            device_index: Camera device index (0 for Pi, 1 for Mac typically)
            width: Frame width
            height: Frame height
            simulate: If True, return dummy frames (for testing without camera)
        """
        self.device_index = device_index
        self.width = width
        self.height = height
        self.simulate = simulate
        self.cap = None
        self._is_pi = self._detect_platform()
        
        if not simulate:
            self._initialize()
    
    def _detect_platform(self) -> bool:
        """Detect if running on Raspberry Pi."""
        try:
            with open('/proc/cpuinfo', 'r') as f:
                if 'Raspberry Pi' in f.read():
                    return True
        except:
            pass
        return False
    
    def _initialize(self):
        """Initialize camera based on platform."""
        if self._is_pi:
            # Try PiCamera2 first, fallback to OpenCV
            try:
                from picamera2 import Picamera2
                self.picam = Picamera2()
                self.picam.configure(self.picam.create_preview_configuration(
                    main={"size": (self.width, self.height)}
                ))
                self.picam.start()
                self.camera_type = "picamera2"
                logger.info("Initialized PiCamera2")
                return
            except ImportError:
                logger.warning("PiCamera2 not available, using OpenCV")
            except Exception as e:
                logger.warning(f"PiCamera2 failed: {e}, using OpenCV")
        
        # Use OpenCV (works on Mac and Pi)
        if self._is_pi:
            # On Pi, try /dev/video0
            self.cap = cv2.VideoCapture(0)
        else:
            # On Mac, use AVFoundation backend
            self.cap = cv2.VideoCapture(self.device_index, cv2.CAP_AVFOUNDATION)
        
        if not self.cap or not self.cap.isOpened():
            logger.error(f"Failed to open camera at index {self.device_index}")
            self.cap = None
            return
        
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
        self.camera_type = "opencv"
        
        # Warm up camera
        time.sleep(0.5)
        logger.info(f"Initialized OpenCV camera (device {self.device_index})")
    
    def capture(self) -> Optional[np.ndarray]:
        """
        Capture a single frame from camera.
        
        Returns:
            numpy array (BGR format) or None if failed
        """
        if self.simulate:
            # Return dummy frame for testing
            return np.zeros((self.height, self.width, 3), dtype=np.uint8)
        
        if self.camera_type == "picamera2":
            try:
                frame = self.picam.capture_array()
                # Convert RGB to BGR for OpenCV compatibility
                if len(frame.shape) == 3:
                    frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
                return frame
            except Exception as e:
                logger.error(f"PiCamera2 capture failed: {e}")
                return None
        
        if self.cap is None or not self.cap.isOpened():
            logger.error("Camera not initialized")
            return None
        
        ret, frame = self.cap.read()
        if not ret or frame is None:
            logger.warning("Failed to read frame from camera")
            return None
        
        return frame
    
    def capture_pil(self) -> Optional[Image.Image]:
        """
        Capture frame as PIL Image.
        
        Returns:
            PIL Image or None if failed
        """
        frame = self.capture()
        if frame is None:
            return None
        
        # Convert BGR to RGB for PIL
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        return Image.fromarray(frame_rgb)
    
    def release(self):
        """Release camera resources."""
        if self.camera_type == "picamera2" and hasattr(self, 'picam'):
            try:
                self.picam.stop()
                self.picam.close()
            except:
                pass
        
        if self.cap is not None:
            self.cap.release()
            self.cap = None
        
        logger.info("Camera released")
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.release()


