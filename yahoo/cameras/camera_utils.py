import cv2
from typing import Optional, Union
from yahoo.cameras.camera_config import CameraConfig

def open_camera(cfg: CameraConfig) -> Optional[Union[cv2.VideoCapture, 'Picamera2']]:
    """
    Open camera - tries PiCamera2 on Raspberry Pi, falls back to OpenCV VideoCapture.
    Returns camera object (Picamera2 or cv2.VideoCapture) or None if failed.
    """
    # Try PiCamera2 first (Raspberry Pi only)
    try:
        from picamera2 import Picamera2
        picam = Picamera2()
        picam.configure(picam.create_preview_configuration(
            main={"size": (cfg.width, cfg.height)}
        ))
        picam.start()
        print(f"[CAMERA] Using PiCamera2 for '{cfg.name}' ({cfg.width}x{cfg.height})")
        return picam
    except ImportError:
        # Not on Raspberry Pi or picamera2 not installed
        pass
    except Exception as e:
        print(f"[WARNING] PiCamera2 failed: {e}, falling back to OpenCV")
    
    # Fallback to OpenCV VideoCapture
    cap = cv2.VideoCapture(cfg.index)
    if not cap.isOpened():
        print(f"[ERROR] Could not open camera '{cfg.name}' at index {cfg.index}")
        return None
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, cfg.width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, cfg.height)
    print(f"[CAMERA] Using OpenCV VideoCapture for '{cfg.name}' (index {cfg.index})")
    return cap

