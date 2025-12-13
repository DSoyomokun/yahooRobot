"""
FULL PIPELINE + STATE MACHINE
"""
import sys
from pathlib import Path

# Add project root to Python path so we can import yahoo module
# This allows running the script from any directory
_script_dir = Path(__file__).parent.resolve()
# Go up 3 levels: scanner -> mission -> yahoo -> project_root
_project_root = _script_dir.parent.parent.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

import cv2
import time

from yahoo.config.cameras import CSI_CAMERA
from yahoo.sense.camera import open_camera
from yahoo.mission.scanner.detector import PaperDetector
from yahoo.mission.scanner.storage import init_db, insert_scan
from yahoo.mission.scanner.leds import (
    yellow_on, yellow_off,
    green_on, green_off
)

SCAN_DIR = _script_dir / "scans"
SCAN_DIR.mkdir(parents=True, exist_ok=True)

def main():
    init_db()
    cap = open_camera(CSI_CAMERA)
    if cap is None:
        return

    detector = PaperDetector()
    state = "IDLE"
    scan_id = 0

    print("[SYSTEM] Scanner ready")

    while True:
        # OpenCV VideoCapture
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

    # Release OpenCV VideoCapture
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
