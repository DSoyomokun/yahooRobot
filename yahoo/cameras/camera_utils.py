import cv2
from typing import Optional
from yahoo.cameras.camera_config import CameraConfig

def open_camera(cfg: CameraConfig) -> Optional[cv2.VideoCapture]:
    """
    Open camera using OpenCV VideoCapture (works with old picamera library).
    Returns VideoCapture object or None if failed.
    """
    cap = cv2.VideoCapture(cfg.index)
    
    if not cap.isOpened():
        print(f"[ERROR] Could not open camera '{cfg.name}' at index {cfg.index}")
        print(f"[ERROR] For CSI camera on Pi, ensure camera is enabled: sudo raspi-config")
        return None
    
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, cfg.width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, cfg.height)
    
    print(f"[CAMERA] Using OpenCV VideoCapture for '{cfg.name}' ({cfg.width}x{cfg.height})")
    return cap

