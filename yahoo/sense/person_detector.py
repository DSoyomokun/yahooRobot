"""
Person Detector - Story 2.1

Detects person presence in camera frame, optimized for back-view detection
(robot looking at students from behind/aisle).

Uses MediaPipe Pose to detect shoulders and upper body visible from behind.
"""

import logging
from typing import Optional

import cv2
import mediapipe as mp


logger = logging.getLogger(__name__)
mp_pose = mp.solutions.pose


class PersonDetector:
    """
    Detects person presence from back view using MediaPipe Pose.

    Optimized for detecting students sitting at desks with their backs
    to the camera. Focuses on shoulder visibility as primary indicator.
    """

    def __init__(
        self,
        min_detection_confidence: float = 0.5,
        min_shoulder_visibility: float = 0.5,
        simulate: bool = False
    ):
        """
        Initialize person detector.

        Args:
            min_detection_confidence: Minimum confidence for pose detection (0-1)
            min_shoulder_visibility: Minimum visibility for shoulder landmarks (0-1)
            simulate: If True, returns mock detection data
        """
        self.simulate = simulate
        self.min_shoulder_visibility = min_shoulder_visibility

        if not simulate:
            self.pose = mp_pose.Pose(
                static_image_mode=True,  # Process single frames independently
                model_complexity=0,      # Lightweight model
                enable_segmentation=False,
                min_detection_confidence=min_detection_confidence,
            )
            logger.info(f"PersonDetector initialized (confidence={min_detection_confidence})")
        else:
            self.pose = None
            logger.info("PersonDetector initialized in simulation mode")

    def detect(self, frame) -> bool:
        """
        Detect if a person is present in the frame.

        Args:
            frame: BGR image from camera (numpy array)

        Returns:
            True if person detected, False otherwise
        """
        if self.simulate:
            # In simulation, always return True for testing
            logger.debug("Simulation mode: Person detected (mock)")
            return True

        try:
            # Convert to RGB for MediaPipe
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.pose.process(rgb)

            # No pose detected
            if results.pose_landmarks is None:
                logger.debug("No pose landmarks detected")
                return False

            # Check shoulder visibility (most reliable from back view)
            lm = results.pose_landmarks.landmark

            # Shoulder landmarks: 11 (left shoulder), 12 (right shoulder)
            left_shoulder = lm[11]
            right_shoulder = lm[12]

            # Both shoulders should be visible
            left_vis = left_shoulder.visibility
            right_vis = right_shoulder.visibility

            shoulders_visible = (
                left_vis > self.min_shoulder_visibility and
                right_vis > self.min_shoulder_visibility
            )

            if shoulders_visible:
                logger.debug(
                    f"Person detected (L_shoulder: {left_vis:.2f}, "
                    f"R_shoulder: {right_vis:.2f})"
                )
            else:
                logger.debug(
                    f"Pose detected but shoulders not visible enough "
                    f"(L: {left_vis:.2f}, R: {right_vis:.2f})"
                )

            return shoulders_visible

        except Exception as e:
            logger.error(f"Error during person detection: {e}")
            return False

    def detect_with_details(self, frame) -> dict:
        """
        Detect person and return detailed information.

        Args:
            frame: BGR image from camera

        Returns:
            Dictionary with detection results:
            {
                'person_detected': bool,
                'pose_detected': bool,
                'left_shoulder_vis': float,
                'right_shoulder_vis': float,
                'confidence': float
            }
        """
        if self.simulate:
            return {
                'person_detected': True,
                'pose_detected': True,
                'left_shoulder_vis': 1.0,
                'right_shoulder_vis': 1.0,
                'confidence': 1.0
            }

        details = {
            'person_detected': False,
            'pose_detected': False,
            'left_shoulder_vis': 0.0,
            'right_shoulder_vis': 0.0,
            'confidence': 0.0
        }

        try:
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.pose.process(rgb)

            if results.pose_landmarks is None:
                return details

            details['pose_detected'] = True
            lm = results.pose_landmarks.landmark

            # Get shoulder visibility
            left_shoulder = lm[11]
            right_shoulder = lm[12]

            details['left_shoulder_vis'] = left_shoulder.visibility
            details['right_shoulder_vis'] = right_shoulder.visibility

            # Calculate confidence (average of both shoulders)
            details['confidence'] = (
                left_shoulder.visibility + right_shoulder.visibility
            ) / 2.0

            # Determine if person detected
            details['person_detected'] = (
                details['left_shoulder_vis'] > self.min_shoulder_visibility and
                details['right_shoulder_vis'] > self.min_shoulder_visibility
            )

            return details

        except Exception as e:
            logger.error(f"Error getting detection details: {e}")
            return details

    def close(self):
        """Release resources."""
        if self.pose:
            self.pose.close()
            logger.debug("PersonDetector closed")


# Convenience function for quick testing
def detect_person(frame, simulate: bool = False) -> bool:
    """
    Quick person detection without creating detector instance.

    Args:
        frame: BGR image from camera
        simulate: Simulation mode

    Returns:
        True if person detected
    """
    detector = PersonDetector(simulate=simulate)
    try:
        return detector.detect(frame)
    finally:
        detector.close()
