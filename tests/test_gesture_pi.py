import time
import os
import csv
from datetime import datetime
import argparse

from yahoo.config.cameras import CSI_CAMERA, USB_CAMERA
from yahoo.sense.camera import open_camera
from yahoo.sense.gesture import GestureDetector  # your existing detector


LOG_DIR = "logs"
LOG_FILE = os.path.join(LOG_DIR, "gesture_events_pi.csv")


def init_logger():
    os.makedirs(LOG_DIR, exist_ok=True)
    new_file = not os.path.exists(LOG_FILE)
    f = open(LOG_FILE, "a", newline="")
    writer = csv.writer(f)
    if new_file:
        writer.writerow(["timestamp", "gesture", "frame_idx", "camera_name"])
    return f, writer


def main():
    parser = argparse.ArgumentParser(description="Headless gesture test on Pi.")
    parser.add_argument(
        "--cam",
        choices=["csi", "usb"],
        default="csi",
        help="Which camera to use: 'csi' (/dev/video0) or 'usb' (/dev/video1).",
    )
    args = parser.parse_args()

    cfg = CSI_CAMERA if args.cam == "csi" else USB_CAMERA
    print(f"[INFO] Starting gesture detection on {cfg.name} (index {cfg.index})")

    cap = open_camera(cfg)
    if cap is None:
        return

    detector = GestureDetector()
    log_file, log_writer = init_logger()

    frame_idx = 0
    last_gesture = "NONE"
    last_event_time = 0.0
    min_event_interval = 0.5

    print("[INFO] Press Ctrl+C to stop.")

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("[WARN] Failed to grab frame")
                time.sleep(0.05)
                continue

            frame_idx += 1
            gesture, _ = detector.detect(frame)
            now = time.time()

            if gesture != "NONE" and (
                gesture != last_gesture or (now - last_event_time) > min_event_interval
            ):
                ts = datetime.now().isoformat(timespec="seconds")
                print(f"[{ts}] Gesture: {gesture} (frame {frame_idx}, cam {cfg.name})")

                log_writer.writerow([ts, gesture, frame_idx, cfg.name])
                log_file.flush()

                last_gesture = gesture
                last_event_time = now

            time.sleep(0.02)

    except KeyboardInterrupt:
        print("\n[INFO] Stopped by user (Ctrl+C).")
    finally:
        cap.release()
        log_file.close()
        print("[INFO] Camera released, log file closed.")


if __name__ == "__main__":
    main()
