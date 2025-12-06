import math
from typing import Tuple, Optional

import cv2
import mediapipe as mp


mp_pose = mp.solutions.pose


class GestureDetector:
    """
    Head/arm-based raised-hand detector using MediaPipe Pose.
    - Tracks both left and right hands.
    - Uses visibility, height, and arm angle.
    - Includes temporal smoothing and cooldown.
    """

    def __init__(
        self,
        det_conf: float = 0.7,
        track_conf: float = 0.7,
        raise_frames_required: int = 8,
        cooldown_frames: int = 15,
    ):
        self.pose = mp_pose.Pose(
            static_image_mode=False,
            model_complexity=0,  # lighter model for Pi
            enable_segmentation=False,
            min_detection_confidence=det_conf,
            min_tracking_confidence=track_conf,
        )

        # Temporal state
        self.frame_count = 0
        self.raise_frames_required = raise_frames_required
        self.cooldown_frames = cooldown_frames

        self.right_counter = 0
        self.left_counter = 0

        self.last_gesture = "NONE"
        self.last_detected_frame = -1000  # far in the past

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
        img_h,
        img_w,
    ) -> bool:
        """
        Use a combination of:
        - y-position (above shoulder & nose)
        - arm angle (roughly pointing up)
        - extension (hand not too close to shoulder horizontally)
        """

        wrist = lm[wrist_idx]
        elbow = lm[elbow_idx]
        shoulder = lm[shoulder_idx]
        nose = lm[nose_idx]

        # Normalized coordinates: y increases downward
        wrist_y = wrist.y
        shoulder_y = shoulder.y
        nose_y = nose.y

        # Convert to "arm vector" in normalized coords
        vx = wrist.x - shoulder.x
        vy = wrist.y - shoulder.y

        # Angle of arm relative to horizontal
        # atan2(dy, dx). For a raised arm, we want angle < -0.3 (roughly upwards).
        arm_angle = math.atan2(vy, vx)

        # Horizontal distance (normalized, 0..1 range)
        horizontal_dist = abs(wrist.x - shoulder.x)

        # Heuristics:
        # 1) Wrist above shoulder + nose
        # 2) Arm angled upward
        # 3) Hand at least some distance away from shoulder (not just hovering)
        cond_height = wrist_y < shoulder_y and wrist_y < nose_y
        cond_angle = arm_angle < -0.3
        cond_extension = horizontal_dist > 0.08  # tweak as needed

        return cond_height and cond_angle and cond_extension

    def detect(self, frame) -> Tuple[str, Optional[mp.framework.formats.landmark_pb2.NormalizedLandmarkList]]:
        """
        Main entrypoint.
        :param frame: BGR frame from cv2.VideoCapture
        :return: (gesture_label, pose_landmarks)
                 gesture_label in {"NONE", "RIGHT_RAISED", "LEFT_RAISED", "BOTH_RAISED"}
        """
        self.frame_count += 1
        gesture = "NONE"

        # Convert BGR -> RGB for MediaPipe
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Run pose
        results = self.pose.process(rgb)
        pose_landmarks = results.pose_landmarks

        if pose_landmarks is None:
            # Lost tracking → reset counters
            self.right_counter = 0
            self.left_counter = 0
            return gesture, None

        lm = pose_landmarks.landmark
        h, w, _ = frame.shape

        # Indices
        R_WRIST = mp_pose.PoseLandmark.RIGHT_WRIST.value
        R_ELBOW = mp_pose.PoseLandmark.RIGHT_ELBOW.value
        R_SHOULDER = mp_pose.PoseLandmark.RIGHT_SHOULDER.value

        L_WRIST = mp_pose.PoseLandmark.LEFT_WRIST.value
        L_ELBOW = mp_pose.PoseLandmark.LEFT_ELBOW.value
        L_SHOULDER = mp_pose.PoseLandmark.LEFT_SHOULDER.value

        NOSE = mp_pose.PoseLandmark.NOSE.value

        # Visibility checks – skip if critical points are occluded
        right_ok = self._landmarks_visible(
            lm, [R_WRIST, R_ELBOW, R_SHOULDER, NOSE]
        )
        left_ok = self._landmarks_visible(
            lm, [L_WRIST, L_ELBOW, L_SHOULDER, NOSE]
        )

        # Check both hands
        right_raised = False
        left_raised = False

        if right_ok:
            right_raised = self._is_hand_raised(
                lm,
                R_WRIST,
                R_ELBOW,
                R_SHOULDER,
                NOSE,
                h,
                w,
            )

        if left_ok:
            left_raised = self._is_hand_raised(
                lm,
                L_WRIST,
                L_ELBOW,
                L_SHOULDER,
                NOSE,
                h,
                w,
            )

        # Temporal smoothing via frame counters
        # Right hand
        if right_raised:
            self.right_counter += 1
        else:
            self.right_counter = 0

        # Left hand
        if left_raised:
            self.left_counter += 1
        else:
            self.left_counter = 0

        # Apply cooldown to prevent spam
        in_cooldown = (
            self.frame_count - self.last_detected_frame
        ) < self.cooldown_frames

        if not in_cooldown:
            right_active = self.right_counter >= self.raise_frames_required
            left_active = self.left_counter >= self.raise_frames_required

            if right_active and left_active:
                gesture = "BOTH_RAISED"
            elif right_active:
                gesture = "RIGHT_RAISED"
            elif left_active:
                gesture = "LEFT_RAISED"

            if gesture != "NONE":
                # Reset counters and set cooldown
                self.right_counter = 0
                self.left_counter = 0
                self.last_detected_frame = self.frame_count
                self.last_gesture = gesture
        else:
            gesture = "NONE"

        return gesture, pose_landmarks