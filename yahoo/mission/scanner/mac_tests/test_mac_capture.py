import cv2
from datetime import datetime
import os

def capture_from_webcam():
    os.makedirs("scans/raw", exist_ok=True)

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("❌ Could not open webcam.")
        return

    print("Press SPACE to capture, ESC to exit.")

    while True:
        ret, frame = cap.read()
        if not ret:
            print("❌ Failed to read frame.")
            break

        cv2.imshow("Webcam Preview", frame)
        key = cv2.waitKey(1)

        if key == 27:  # ESC
            break

        if key == 32:  # SPACE
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            path = f"scans/raw/mac_capture_{ts}.png"
            cv2.imwrite(path, frame)
            print(f"✅ Saved image → {path}")

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    capture_from_webcam()

