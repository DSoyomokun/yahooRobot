"""
FULL PIPELINE + STATE MACHINE
"""
import cv2
import time
from pathlib import Path

from yahoo.cameras.camera_config import CameraConfig
from yahoo.cameras.camera_utils import open_camera
from yahoo.mission.scanner.detector import PaperDetector
from yahoo.mission.scanner.storage import init_db, insert_scan
from yahoo.mission.scanner.leds import (
    yellow_on, yellow_off,
    green_on, green_off
)

SCAN_DIR = Path("yahoo/mission/scanner/scans")
SCAN_DIR.mkdir(parents=True, exist_ok=True)

def main():
    init_db()
    cfg = CameraConfig(name="scanner_cam")
    cap = open_camera(cfg)
    if cap is None:
        return

    detector = PaperDetector()
    state = "IDLE"
    scan_id = 0

    print("[SYSTEM] Scanner ready")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        if state == "IDLE":
            if detector.paper_detected(frame):
                yellow_on()
                state = "PROCESSING"

        elif state == "PROCESSING":
            scan_id += 1
            filename = SCAN_DIR / f"scan_{scan_id:04d}.jpg"
            cv2.imwrite(str(filename), frame)
            insert_scan(str(filename))
            yellow_off()
            green_on()
            state = "SUCCESS"

        elif state == "SUCCESS":
            time.sleep(2)
            green_off()
            detector.reset()
            state = "IDLE"

        cv2.imshow("Scanner Preview", frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
