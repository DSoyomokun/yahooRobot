"""
Simple Paper Scanner - Detects new paper and saves to database
"""
import sys
from pathlib import Path

# Add project root to Python path
_script_dir = Path(__file__).parent.resolve()
_project_root = _script_dir.parent.parent.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

import cv2
import time

from yahoo.config.cameras import CSI_CAMERA
from yahoo.sense.camera import open_camera
from yahoo.mission.scanner.detector import PaperDetector
from yahoo.mission.scanner.storage import init_db, insert_scan

SCAN_DIR = _script_dir / "scans"
SCAN_DIR.mkdir(parents=True, exist_ok=True)

def main():
    print("[SYSTEM] Initializing scanner...")
    
    # Setup database
    init_db()
    
    # Open camera
    cap = open_camera(CSI_CAMERA)
    if cap is None:
        print("[ERROR] Failed to open camera")
        return
    
    # Warm up camera - let it stabilize
    print("[SYSTEM] Warming up camera...")
    for _ in range(10):
        ret, frame = cap.read()
        if ret and frame is not None:
            break
        time.sleep(0.1)
    
    # Initialize paper detector
    detector = PaperDetector()
    scan_count = 0
    
    print("[SYSTEM] Scanner ready - waiting for paper...")
    
    try:
        while True:
            # Read frame from camera
            ret, frame = cap.read()
            if not ret or frame is None:
                print("[WARN] Failed to read frame")
                time.sleep(0.1)
                continue
            
            # Validate frame dimensions
            if frame.size == 0:
                print("[WARN] Empty frame received")
                time.sleep(0.1)
                continue
            
            # Check if new paper detected
            try:
                if detector.paper_detected(frame):
                    scan_count += 1
                    filename = SCAN_DIR / f"scan_{scan_count:04d}.jpg"
                    
                    # Save image
                    cv2.imwrite(str(filename), frame)
                    
                    # Save to database
                    insert_scan(str(filename))
                    
                    print(f"[SCAN] Captured scan #{scan_count}: {filename.name}")
                    
                    # Reset detector to wait for next paper
                    detector.reset()
                    time.sleep(1)  # Brief pause after detection
            except Exception as e:
                print(f"[ERROR] Detection error: {e}")
                time.sleep(0.1)
                continue
            
            # Small delay to prevent excessive CPU usage
            time.sleep(0.05)
            
    except KeyboardInterrupt:
        print("\n[SYSTEM] Scanner stopped by user")
    finally:
        cap.release()
        print(f"[SYSTEM] Scanner stopped. Total scans: {scan_count}")

if __name__ == "__main__":
    main()
