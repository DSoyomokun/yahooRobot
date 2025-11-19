import cv2
import time

def open_mac_camera(device_index=1, width=640, height=480):
    cap = cv2.VideoCapture(device_index, cv2.CAP_AVFOUNDATION)

    if not cap.isOpened():
        print("Error: Could not open camera.")
        return None

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

    time.sleep(0.5)  # let camera warm up
    return cap

def main():
    cap = open_mac_camera()
    if cap is None:
        return

    print("Camera opened successfully. Press 'q' to quit.")
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

        cv2.imshow("Webcam test", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()