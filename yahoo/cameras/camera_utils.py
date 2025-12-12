import cv2
from typing import Optional
from yahoo.cameras.camera_config import CameraConfig

def open_camera(cfg: CameraConfig) -> Optional[cv2.VideoCapture]:
    cap = cv2.VideoCapture(cfg.index)
    if not cap.isOpened():
        print(f"[ERROR] Could not open camera '{cfg.name}' at index {cfg.index}")
        return None
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, cfg.width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, cfg.height)
    return cap

