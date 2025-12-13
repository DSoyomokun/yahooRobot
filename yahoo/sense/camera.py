import cv2
from typing import Optional
from yahoo.config.cameras import CameraConfig


def _is_raspberry_pi() -> bool:
    """Check if running on Raspberry Pi."""
    try:
        with open('/proc/cpuinfo', 'r') as f:
            return 'Raspberry Pi' in f.read()
    except:
        return False


class CameraWrapper:
    """Wrapper for OpenCV VideoCapture (compatible interface)."""
    
    def __init__(self, cap):
        self.cap = cap
    
    def read(self):
        """Read a frame, compatible with OpenCV VideoCapture interface."""
        return self.cap.read()
    
    def isOpened(self):
        """Check if camera is opened."""
        return self.cap is not None and self.cap.isOpened()
    
    def release(self):
        """Release camera resources."""
        if self.cap:
            self.cap.release()


def open_camera(cfg: CameraConfig) -> Optional[CameraWrapper]:
    """
    Open a camera using a CameraConfig.
    Uses OpenCV VideoCapture directly (works with old picamera library on Raspberry Pi).
    Returns a CameraWrapper (compatible with OpenCV VideoCapture interface) or None if it fails.
    """
    # Use OpenCV VideoCapture directly (same approach as gesture detection)
    cap = cv2.VideoCapture(cfg.index)

    if not cap.isOpened():
        print(f"[ERROR] Could not open camera '{cfg.name}' at index {cfg.index}")
        if _is_raspberry_pi() and cfg.name == "pi_csi":
            print(f"[ERROR] For CSI camera on Pi, ensure camera is enabled: sudo raspi-config")
        return None

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, cfg.width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, cfg.height)

    print(f"[CAMERA] Using OpenCV VideoCapture for '{cfg.name}' ({cfg.width}x{cfg.height})")
    return CameraWrapper(cap=cap)