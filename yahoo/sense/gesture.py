# sense/gesture.py
import cv2
import mediapipe as mp

mp_pose = mp.solutions.pose

class GestureDetector:
    def __init__(self,
                 det_conf=0.5,
                 track_conf=0.5,
                 raise_frames_required=10):
        self.pose = mp_pose.Pose(
            min_detection_confidence=det_conf,
            min_tracking_confidence=track_conf
        )
        self.raise_frames_required = raise_frames_required
        self.raise_counter = 0

    def detect(self, frame):
        """
        Input: BGR frame (numpy array)
        Returns:
            gesture: 'RAISED' or 'NONE'
            pose_landmarks: MediaPipe landmarks or None
        """
        h, w, _ = frame.shape

        image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image_rgb.flags.writeable = False
        results = self.pose.process(image_rgb)
        image_rgb.flags.writeable = True

        gesture = "NONE"
        pose_landmarks = results.pose_landmarks

        if pose_landmarks:
            lm = pose_landmarks.landmark
            wrist = lm[mp_pose.PoseLandmark.RIGHT_WRIST]
            shoulder = lm[mp_pose.PoseLandmark.RIGHT_SHOULDER]
            nose = lm[mp_pose.PoseLandmark.NOSE]

            wrist_y = wrist.y * h
            shoulder_y = shoulder.y * h
            nose_y = nose.y * h

            if wrist_y < shoulder_y and wrist_y < nose_y:
                self.raise_counter += 1
            else:
                self.raise_counter = 0

            if self.raise_counter >= self.raise_frames_required:
                gesture = "RAISED"

        return gesture, pose_landmarks
