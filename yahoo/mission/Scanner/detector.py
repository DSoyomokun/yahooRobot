"""
Edge-triggered brightness-based paper detection
Only triggers on transition from no-paper to paper (brightness increase)
"""
import cv2
import numpy as np

class PaperDetector:
    """
    Edge-triggered paper detector.
    Only detects transitions from baseline (no paper) to bright (paper inserted).
    Prevents multiple triggers from the same paper insertion.
    """
    def __init__(self, threshold=30):
        self.baseline = None
        self.threshold = threshold
        self._last_brightness = None
        self._triggered = False  # Prevents multiple triggers from same insertion

    def compute_brightness(self, frame):
        """Compute average brightness in center ROI."""
        h, w, _ = frame.shape
        roi = frame[h//3:2*h//3, w//3:2*w//3]
        gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        return np.mean(gray)

    def paper_detected(self, frame):
        """
        Edge-triggered detection: only returns True on transition from no-paper to paper.
        Returns False if already triggered (prevents duplicates).
        """
        brightness = self.compute_brightness(frame)
        
        # Initialize baseline on first frame
        if self.baseline is None:
            self.baseline = brightness
            self._last_brightness = brightness
            return False
        
        # If already triggered, don't trigger again until reset
        if self._triggered:
            return False
        
        # Edge detection: check for transition from baseline to bright
        brightness_increase = brightness - self.baseline
        
        # Trigger only on significant brightness increase (paper inserted)
        if brightness_increase > self.threshold:
            self._triggered = True
            return True
        
        self._last_brightness = brightness
        return False

    def reset(self):
        """
        Reset detector for next paper insertion.
        Updates baseline to current brightness and clears trigger flag.
        """
        if self._last_brightness is not None:
            self.baseline = self._last_brightness
        else:
            self.baseline = None
        self._triggered = False
        self._last_brightness = None
