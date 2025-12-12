"""
Camera capture module for paper scanning.
Supports both Raspberry Pi camera and USB webcam.
"""
import cv2
import os
import time

class CameraCapture:
    """Handles camera initialization and image capture."""
    
    def __init__(self, camera_index=0, use_picam=False):
        """
        Args:
            camera_index: Camera device index (0, 1, 2, etc.)
            use_picam: Use Raspberry Pi camera (requires picamera2)
        """
        self.camera_index = camera_index
        self.use_picam = use_picam
        self.cap = None
        self.picam = None
        
    def initialize(self):
        """Initialize camera."""
        if self.use_picam:
            # TODO: Use picamera2 for Raspberry Pi
            try:
                from picamera2 import Picamera2
                self.picam = Picamera2()
                self.picam.start()
                print(f"✅ PiCamera initialized")
            except ImportError:
                raise Exception("picamera2 not installed. Install with: pip install picamera2")
            except Exception as e:
                raise Exception(f"Failed to initialize PiCamera: {e}")
        else:
            self.cap = cv2.VideoCapture(self.camera_index)
            if not self.cap.isOpened():
                raise Exception(f"Failed to open camera {self.camera_index}")
            
            # Set camera properties for better quality
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
            
            # Wait for camera to stabilize
            time.sleep(1)
            
            print(f"✅ Camera initialized (index {self.camera_index})")
    
    def capture_image(self):
        """
        Capture a single image from camera.
        
        Returns:
            BGR image array (numpy array)
        """
        if self.use_picam:
            if not self.picam:
                self.initialize()
            # TODO: Capture from PiCamera
            # frame = self.picam.capture_array()
            # return cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            raise NotImplementedError("PiCamera capture not yet implemented")
        else:
            if not self.cap or not self.cap.isOpened():
                self.initialize()
            
            ret, frame = self.cap.read()
            if not ret:
                raise Exception("Failed to capture image from camera")
            
            return frame
    
    def release(self):
        """Release camera resources."""
        if self.cap:
            self.cap.release()
            self.cap = None
        if self.picam:
            self.picam.stop()
            self.picam = None


def capture_image(camera_index=0, use_picam=False):
    """
    Convenience function to capture a single image.
    
    Args:
        camera_index: Camera device index
        use_picam: Use Raspberry Pi camera
    
    Returns:
        BGR image array
    """
    camera = CameraCapture(camera_index, use_picam)
    try:
        camera.initialize()
        image = camera.capture_image()
        return image
    finally:
        camera.release()
