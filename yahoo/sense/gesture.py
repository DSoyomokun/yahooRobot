import math
from typing import Tuple, Optional, Any

import cv2
import mediapipe as mp


mp_pose = mp.solutions.pose


class GestureDetector:
    """
    Head/arm-based raised-hand detector using MediaPipe Pose.
    - Tracks both left and right hands.
    - Uses visibility, height, and arm angle.
    - Includes temporal smoothing (requires N consecutive frames to trigger).
    - Outputs continuous state: gesture persists while hand stays raised.
    """

    def __init__(
        self,
        det_conf: float = 0.7,
        track_conf: float = 0.7,
        raise_frames_required: int = 8,
    ):
        self.pose = mp_pose.Pose(
            static_image_mode=False,
            model_complexity=0,
            enable_segmentation=False,
            min_detection_confidence=det_conf,
            min_tracking_confidence=track_conf,
        )

        self.raise_frames_required = raise_frames_required
        self.right_counter = 0
        self.left_counter = 0

    def _landmarks_visible(self, lm, indices, min_vis=0.5) -> bool:
        """Check that all specified landmarks have at least min_vis visibility."""
        for idx in indices:
            if lm[idx].visibility < min_vis:
                return False
        return True

    def _is_hand_raised(
        self,
        lm,
        wrist_idx,
        elbow_idx,
        shoulder_idx,
        nose_idx,
    ) -> bool:
        """
        Returns True if hand is raised based on:
        - y-position (wrist above shoulder & nose)
        - arm angle (pointing upward)
        - extension (hand not too close to shoulder)
        """
        wrist = lm[wrist_idx]
        shoulder = lm[shoulder_idx]
        nose = lm[nose_idx]

        # Arm vector in normalized coords
        vx = wrist.x - shoulder.x
        vy = wrist.y - shoulder.y

        # Angle of arm (atan2). Raised arm → angle < -0.3
        arm_angle = math.atan2(vy, vx)

        # Horizontal distance from shoulder
        horizontal_dist = abs(wrist.x - shoulder.x)

        # Three conditions for "raised"
        cond_height = wrist.y < shoulder.y and wrist.y < nose.y
        cond_angle = arm_angle < -0.3
        cond_extension = horizontal_dist > 0.08

        return cond_height and cond_angle and cond_extension

    def detect(self, frame) -> Tuple[str, Optional[Any]]:
        """
        Process a frame and return current gesture state.
        
        :param frame: BGR frame from cv2.VideoCapture
        :return: (gesture_label, pose_landmarks)
                 gesture_label: "NONE", "RIGHT_RAISED", "LEFT_RAISED", or "BOTH_RAISED"
        """
        gesture = "NONE"

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.pose.process(rgb)
        pose_landmarks = results.pose_landmarks

        if pose_landmarks is None:
            self.right_counter = 0
            self.left_counter = 0
            return gesture, None

        lm = pose_landmarks.landmark

        # Landmark indices
        R_WRIST = mp_pose.PoseLandmark.RIGHT_WRIST.value
        R_ELBOW = mp_pose.PoseLandmark.RIGHT_ELBOW.value
        R_SHOULDER = mp_pose.PoseLandmark.RIGHT_SHOULDER.value

        L_WRIST = mp_pose.PoseLandmark.LEFT_WRIST.value
        L_ELBOW = mp_pose.PoseLandmark.LEFT_ELBOW.value
        L_SHOULDER = mp_pose.PoseLandmark.LEFT_SHOULDER.value

        NOSE = mp_pose.PoseLandmark.NOSE.value

        # Visibility checks
        right_ok = self._landmarks_visible(lm, [R_WRIST, R_ELBOW, R_SHOULDER, NOSE])
        left_ok = self._landmarks_visible(lm, [L_WRIST, L_ELBOW, L_SHOULDER, NOSE])

        # Check if hands are raised this frame
        right_raised = right_ok and self._is_hand_raised(
            lm, R_WRIST, R_ELBOW, R_SHOULDER, NOSE
        )
        left_raised = left_ok and self._is_hand_raised(
            lm, L_WRIST, L_ELBOW, L_SHOULDER, NOSE
        )

        # Update counters with clamping (prevents overflow, keeps state stable)
        if right_raised:
            self.right_counter = min(self.right_counter + 1, self.raise_frames_required)
        else:
            self.right_counter = 0

        if left_raised:
            self.left_counter = min(self.left_counter + 1, self.raise_frames_required)
        else:
            self.left_counter = 0

        # Determine gesture based on counters meeting threshold
        right_active = self.right_counter >= self.raise_frames_required
        left_active = self.left_counter >= self.raise_frames_required

        if right_active and left_active:
            gesture = "BOTH_RAISED"
        elif right_active:
            gesture = "RIGHT_RAISED"
        elif left_active:
            gesture = "LEFT_RAISED"

        return gesture, pose_landmarks