import cv2
import time
import mediapipe as mp
from yahoo.sense.gesture import GestureDetector

mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose

def open_mac_camera(device_index=1, width=640, height=480):
    cap = cv2.VideoCapture(device_index, cv2.CAP_AVFOUNDATION)

    if not cap.isOpened():
        print("Error: Could not open camera.")
        return None

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

    time.sleep(0.5)
    return cap

def main():
    cap = open_mac_camera()
    if cap is None:
        return

    detector = GestureDetector()

    print("Camera + gesture detector running. Press 'q' to quit.")
    frame_fail_count = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            frame_fail_count += 1
            if frame_fail_count == 1:
                print("Failed to read frame from camera. Retrying...")
            if frame_fail_count > 10:
                print("Failed to read frames after multiple attempts.")
                break
            time.sleep(0.1)
            continue
        frame_fail_count = 0

        gesture, pose_landmarks = detector.detect(frame)

        # Draw pose for debugging
        if pose_landmarks:
            mp_drawing.draw_landmarks(
                frame,
                pose_landmarks,
                mp_pose.POSE_CONNECTIONS
            )

        cv2.putText(frame, f"gesture: {gesture}",
                    (10, 30), cv2.FONT_HERSHEY_SIMPLEX,
                    1, (0, 0, 255), 2, cv2.LINE_AA)

        if gesture == "RAISED":
            print("Hand raised detected!")

        cv2.imshow("Gesture detection (Mac)", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()