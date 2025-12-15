import cv2
import time
import sys
import argparse
from pathlib import Path
import mediapipe as mp

# Add project root to path to import yahoo module
sys.path.insert(0, str(Path(__file__).parent.parent))

from yahoo.sense.gesture import GestureDetector

mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose

def open_mac_camera(device_index=0, width=640, height=480):
    """Open Mac camera using AVFoundation backend."""
    # Try with AVFoundation first
    cap = cv2.VideoCapture(device_index, cv2.CAP_AVFOUNDATION)

    if not cap.isOpened():
        print(f"AVFoundation failed, trying default backend...")
        cap = cv2.VideoCapture(device_index)

    if not cap.isOpened():
        print(f"Error: Could not open camera at index {device_index}.")
        return None

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # Reduce buffer to get fresher frames

    # macOS needs longer initialization time
    print("Initializing camera...")
    time.sleep(2.0)

    # Warm-up: read and discard first few frames
    print("Warming up camera...")
    for i in range(10):
        ret, _ = cap.read()
        if ret:
            print(f"✓ Camera ready after {i+1} warm-up frames")
            time.sleep(0.5)  # Extra delay after successful warm-up
            return cap
        time.sleep(0.1)

    print("Warning: Camera opened but couldn't read frames during warm-up")
    return cap

def main():
    parser = argparse.ArgumentParser(description="Test gesture detection on Mac camera.")
    parser.add_argument(
        "--camera",
        type=int,
        default=1,
        help="Camera device index (default: 1 for external/continuity, try 0 for built-in)",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Print raw debug info for thresholds & tuning.",
    )
    args = parser.parse_args()

    # Initialize gesture detector FIRST (before camera) to avoid conflicts
    print("Initializing MediaPipe gesture detector...")
    detector = GestureDetector(
        det_conf=0.7,
        track_conf=0.7,
        raise_frames_required=8,
    )
    print("✓ Gesture detector ready")

    # Try specified camera index first, then try alternatives
    cap = None
    camera_indices = [args.camera] + [i for i in [0, 1, 2] if i != args.camera]

    for device_index in camera_indices:
        print(f"Trying camera device {device_index}...")
        cap = open_mac_camera(device_index=device_index)
        if cap is not None:
            print(f"✓ Successfully opened camera at device {device_index}")
            break

    if cap is None:
        print("✗ Error: Could not open any camera. Make sure a camera is connected.")
        return

    print("\n[INFO] Gesture Detection Running")
    print("  - Press 'q' to quit")
    print("  - Raise your hand to test detection")
    if args.debug:
        print("  - Debug mode: showing landmark values\n")

    frame_fail_count = 0
    last_gesture = "NONE"
    success_count = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            frame_fail_count += 1
            if frame_fail_count == 1:
                print("[WARN] Failed to read frame from camera. Retrying...")
            if frame_fail_count > 30:  # Increased from 10 to 30
                print("[ERROR] Failed to read frames after multiple attempts.")
                print(f"       Successfully read {success_count} frames before failure.")
                break
            time.sleep(0.05)  # Reduced from 0.1 to 0.05 for faster recovery
            continue

        frame_fail_count = 0
        success_count += 1

        # Detect gesture
        gesture, pose_landmarks = detector.detect(frame)

        # Draw pose landmarks for debugging
        if pose_landmarks:
            mp_drawing.draw_landmarks(
                frame,
                pose_landmarks,
                mp_pose.POSE_CONNECTIONS,
                mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=2),
                mp_drawing.DrawingSpec(color=(0, 0, 255), thickness=2, circle_radius=1),
            )

        # Display gesture text
        gesture_color = (0, 255, 0) if gesture != "NONE" else (0, 0, 255)
        cv2.putText(
            frame,
            f"Gesture: {gesture}",
            (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            gesture_color,
            2,
            cv2.LINE_AA
        )

        # Print detected gestures
        if gesture != "NONE" and gesture != last_gesture:
            print(f"[DETECTED] {gesture}")
            last_gesture = gesture
        elif gesture == "NONE":
            last_gesture = "NONE"

        # Debug output
        if args.debug and pose_landmarks is not None:
            lm = pose_landmarks.landmark

            # Right hand landmarks
            RW = lm[mp_pose.PoseLandmark.RIGHT_WRIST.value]
            RS = lm[mp_pose.PoseLandmark.RIGHT_SHOULDER.value]
            RE = lm[mp_pose.PoseLandmark.RIGHT_ELBOW.value]

            # Left hand landmarks
            LW = lm[mp_pose.PoseLandmark.LEFT_WRIST.value]
            LS = lm[mp_pose.PoseLandmark.LEFT_SHOULDER.value]

            print(
                f"[DEBUG] Right: wrist.y={RW.y:.3f}, shoulder.y={RS.y:.3f}, "
                f"vis={RW.visibility:.2f} | "
                f"Left: wrist.y={LW.y:.3f}, shoulder.y={LS.y:.3f}, "
                f"vis={LW.visibility:.2f} | gesture={gesture}"
            )

        cv2.imshow("Gesture Detection (Mac)", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    print("\n[INFO] Gesture detection stopped.")

if __name__ == "__main__":
    main()

