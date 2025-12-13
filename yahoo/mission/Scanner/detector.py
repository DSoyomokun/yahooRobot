"""
Brightness-based paper detection
"""
import cv2
import numpy as np

class PaperDetector:
    def __init__(self, threshold=30):
        self.baseline = None
        self.threshold = threshold

    def compute_brightness(self, frame):
        h, w, _ = frame.shape
        roi = frame[h//3:2*h//3, w//3:2*w//3]
        gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        return np.mean(gray)

    def paper_detected(self, frame):
        brightness = self.compute_brightness(frame)
        if self.baseline is None:
            self.baseline = brightness
            return False
        return (brightness - self.baseline) > self.threshold

    def reset(self):
        self.baseline = None

