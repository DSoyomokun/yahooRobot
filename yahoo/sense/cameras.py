# sense/cameras.py

import cv2
import numpy as np

class CameraDetector:
    """
    Handles:
    - frame grabbing
    - object detection (person, backpack, obstacles)
    """

    def __init__(self, camera_index=0, conf=0.5):
        self.cap = cv2.VideoCapture(camera_index)
        self.confidence = conf

    def get_frame(self):
        ret, frame = self.cap.read()
        return frame

    def detect_blockage(self, frame):
        """
        Simplified version:
        Detects any large moving object in the path.
        """

        # Convert to grayscale + blur
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(gray, (15, 15), 0)

        # Threshold to find blobs
        _, thresh = cv2.threshold(blur, 120, 255, cv2.THRESH_BINARY_INV)

        # Count white pixel sum in middle of frame
        h, w = thresh.shape
        roi = thresh[int(h*0.3):int(h*0.7), int(w*0.3):int(w*0.7)]
        area = np.sum(roi == 255)

        if area > 4000:
            return True

        return False
