import cv2
from typing import Optional
from yahoo.config.cameras import CameraConfig


def open_camera(cfg: CameraConfig) -> Optional[cv2.VideoCapture]:
    """
    Open a camera using a CameraConfig.
    Returns an opened cv2.VideoCapture or None if it fails.
    """
    cap = cv2.VideoCapture(cfg.index)

    if not cap.isOpened():
        print(f"[ERROR] Could not open camera '{cfg.name}' at index {cfg.index}")
        return None

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, cfg.width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, cfg.height)

    return cap