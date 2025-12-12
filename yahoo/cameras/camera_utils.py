from typing import Optional
from yahoo.cameras.camera_config import CameraConfig

def open_camera(cfg: CameraConfig) -> Optional['Picamera2']:
    """
    Open camera using PiCamera2 (GoPiGo only - no USB/webcam support).
    Returns Picamera2 object or None if failed.
    """
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
        print(f"[ERROR] PiCamera2 not available. This scanner requires GoPiGo with Raspberry Pi Camera Module.")
        print(f"[ERROR] Install with: pip3 install picamera2")
        return None
    except Exception as e:
        print(f"[ERROR] Failed to initialize PiCamera2: {e}")
        print(f"[ERROR] Check camera is enabled: sudo raspi-config → Interface Options → Camera")
        return None

