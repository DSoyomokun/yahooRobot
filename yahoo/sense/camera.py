import cv2
import numpy as np
from typing import Optional, Union
from yahoo.config.cameras import CameraConfig


def _is_raspberry_pi() -> bool:
    """Check if running on Raspberry Pi."""
    try:
        with open('/proc/cpuinfo', 'r') as f:
            return 'Raspberry Pi' in f.read()
    except:
        return False


class CameraWrapper:
    """Wrapper to support both PiCamera2 and OpenCV VideoCapture."""
    
    def __init__(self, picam=None, cap=None):
        self.picam = picam
        self.cap = cap
        self.camera_type = "picamera2" if picam else "opencv"
    
    def read(self):
        """Read a frame, compatible with OpenCV VideoCapture interface."""
        if self.camera_type == "picamera2":
            try:
                frame = self.picam.capture_array()
                # PiCamera2 returns RGB, convert to BGR for OpenCV
                if len(frame.shape) == 3:
                    frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
                return True, frame
            except Exception as e:
                print(f"[ERROR] PiCamera2 capture failed: {e}")
                return False, None
        else:
            return self.cap.read()
    
    def isOpened(self):
        """Check if camera is opened."""
        if self.camera_type == "picamera2":
            return self.picam is not None
        return self.cap is not None and self.cap.isOpened()
    
    def release(self):
        """Release camera resources."""
        if self.camera_type == "picamera2" and self.picam:
            try:
                self.picam.stop()
                self.picam.close()
            except:
                pass
        elif self.cap:
            self.cap.release()


def open_camera(cfg: CameraConfig) -> Optional[CameraWrapper]:
    """
    Open a camera using a CameraConfig.
    For CSI cameras on Raspberry Pi, tries PiCamera2 first, then falls back to OpenCV.
    Returns a CameraWrapper (compatible with OpenCV VideoCapture interface) or None if it fails.
    """
    # For CSI camera on Raspberry Pi, try PiCamera2 first
    if cfg.name == "pi_csi" and _is_raspberry_pi():
        try:
            from picamera2 import Picamera2
            picam = Picamera2()
            # Use still configuration for high resolution scanning
            picam.configure(picam.create_still_configuration(
                main={"size": (cfg.width, cfg.height)}
            ))
            picam.start()
            print(f"[CAMERA] Using PiCamera2 for '{cfg.name}' ({cfg.width}x{cfg.height})")
            return CameraWrapper(picam=picam)
        except ImportError:
            print(f"[WARN] PiCamera2 not available, trying OpenCV VideoCapture")
        except Exception as e:
            print(f"[WARN] PiCamera2 failed: {e}, trying OpenCV VideoCapture")
    
    # Fallback to OpenCV VideoCapture
    cap = cv2.VideoCapture(cfg.index)

    if not cap.isOpened():
        print(f"[ERROR] Could not open camera '{cfg.name}' at index {cfg.index}")
        print(f"[ERROR] For CSI camera on Pi, ensure camera is enabled: sudo raspi-config")
        return None

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, cfg.width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, cfg.height)

    print(f"[CAMERA] Using OpenCV VideoCapture for '{cfg.name}' ({cfg.width}x{cfg.height})")
    return CameraWrapper(cap=cap)