"""
Production-Ready Paper Scanner
Edge-triggered detection with state machine and completion signals.
Safe to import - no side effects until start() is called.
"""
import sys
from pathlib import Path
from enum import Enum
from typing import Optional, Callable
import threading

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

SCAN_DIR = _script_dir / "scans"
SCAN_DIR.mkdir(parents=True, exist_ok=True)


class ScannerState(Enum):
    """Scanner state machine states."""
    IDLE = "IDLE"
    PROCESSING = "PROCESSING"  # Locked - prevents duplicate captures
    SUCCESS = "SUCCESS"
    COOLDOWN = "COOLDOWN"


class Scanner:
    """
    Production-ready paper scanner with state machine and edge-triggered detection.
    
    Usage:
        scanner = Scanner(completion_callback=lambda path: print(f"Scanned: {path}"))
        scanner.start()  # Starts scanning loop
        # ... later ...
        scanner.stop()   # Stops scanning loop
    
    State Flow:
        IDLE → PROCESSING (locked) → SUCCESS → COOLDOWN → IDLE
    """
    
    def __init__(
        self,
        camera_config=CSI_CAMERA,
        scan_dir: Optional[Path] = None,
        completion_callback: Optional[Callable[[str], None]] = None,
        cooldown_seconds: float = 2.0,
        detection_threshold: int = 30
    ):
        """
        Initialize scanner. Safe to instantiate - no side effects.
        
        Args:
            camera_config: Camera configuration (default: CSI_CAMERA)
            scan_dir: Directory to save scans (default: scanner/scans/)
            completion_callback: Called when scan is saved (path: str) -> None
            cooldown_seconds: Time to wait after SUCCESS before returning to IDLE
            detection_threshold: Brightness threshold for paper detection
        """
        self.camera_config = camera_config
        self.scan_dir = scan_dir or SCAN_DIR
        self.scan_dir.mkdir(parents=True, exist_ok=True)
        self.completion_callback = completion_callback
        self.cooldown_seconds = cooldown_seconds
        
        # State management
        self.state = ScannerState.IDLE
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._lock = threading.Lock()
        
        # Components (initialized on start)
        self.cap = None
        self.detector = PaperDetector(threshold=detection_threshold)
        self.scan_count = 0
        
        # Timing
        self._cooldown_start_time = None
    
    def start(self):
        """Start the scanner. Initializes camera and begins scanning loop."""
        if self._running:
            print("[SCANNER] Already running")
            return
        
        print("[SCANNER] Initializing...")
        
        # Open camera
        self.cap = open_camera(self.camera_config)
        if self.cap is None:
            print("[SCANNER] ERROR: Failed to open camera")
            return False
        
        # Small delay after opening camera
        time.sleep(0.5)
        
        # Reset state
        self.state = ScannerState.IDLE
        self._running = True
        self.scan_count = 0
        
        # Start scanning thread
        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()
        
        print("[SCANNER] Ready - waiting for paper insertion...")
        return True
    
    def stop(self):
        """Stop the scanner and release resources."""
        if not self._running:
            return
        
        print("[SCANNER] Stopping...")
        self._running = False
        
        # Wait for thread to finish
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=2.0)
        
        # Release camera
        if self.cap:
            self.cap.release()
            self.cap = None
        
        print(f"[SCANNER] Stopped. Total scans: {self.scan_count}")
    
    def _run_loop(self):
        """Main scanning loop - runs in separate thread."""
        try:
            while self._running:
                self._process_frame()
                time.sleep(0.05)  # Prevent excessive CPU usage
        except Exception as e:
            print(f"[SCANNER] ERROR in scan loop: {e}")
            self._running = False
        finally:
            if self.cap:
                self.cap.release()
    
    def _process_frame(self):
        """Process a single frame based on current state."""
        # Read frame
        ret, frame = self.cap.read()
        if not ret or frame is None:
            return
        
        if frame.size == 0:
            return
        
        # State machine
        with self._lock:
            if self.state == ScannerState.IDLE:
                self._handle_idle(frame)
            elif self.state == ScannerState.PROCESSING:
                self._handle_processing(frame)
            elif self.state == ScannerState.SUCCESS:
                self._handle_success()
            elif self.state == ScannerState.COOLDOWN:
                self._handle_cooldown()
    
    def _handle_idle(self, frame):
        """IDLE state: detect paper insertion (edge-triggered)."""
        if self.detector.paper_detected(frame):
            # Transition to PROCESSING (locked)
            self.state = ScannerState.PROCESSING
            print(f"[SCANNER] State: IDLE → PROCESSING (paper detected)")
    
    def _handle_processing(self, frame):
        """PROCESSING state: capture and save image (locked - no new detections)."""
        try:
            self.scan_count += 1
            filename = self.scan_dir / f"scan_{self.scan_count:04d}.jpg"
            
            # Save image
            cv2.imwrite(str(filename), frame)
            
            print(f"[SCANNER] State: PROCESSING → SUCCESS")
            print(f"[SCANNER] Captured scan #{self.scan_count}: {filename.name}")
            print(f"[SCANNER] Saved to: {filename}")
            
            # Emit completion signal
            if self.completion_callback:
                try:
                    self.completion_callback(str(filename))
                except Exception as e:
                    print(f"[SCANNER] WARNING: Completion callback error: {e}")
            
            # Transition to SUCCESS
            self.state = ScannerState.SUCCESS
            
        except Exception as e:
            print(f"[SCANNER] ERROR during capture: {e}")
            # Reset to IDLE on error
            self.detector.reset()
            self.state = ScannerState.IDLE
    
    def _handle_success(self):
        """SUCCESS state: reset detector and start cooldown."""
        # Reset detector for next insertion
        self.detector.reset()
        
        # Transition to COOLDOWN
        self.state = ScannerState.COOLDOWN
        self._cooldown_start_time = time.time()
        print(f"[SCANNER] State: SUCCESS → COOLDOWN ({self.cooldown_seconds}s)")
    
    def _handle_cooldown(self):
        """COOLDOWN state: wait before returning to IDLE."""
        if self._cooldown_start_time is None:
            self._cooldown_start_time = time.time()
        
        elapsed = time.time() - self._cooldown_start_time
        if elapsed >= self.cooldown_seconds:
            # Transition back to IDLE
            self.state = ScannerState.IDLE
            self._cooldown_start_time = None
            print(f"[SCANNER] State: COOLDOWN → IDLE (ready for next scan)")
    
    def is_running(self) -> bool:
        """Check if scanner is currently running."""
        return self._running
    
    def get_state(self) -> ScannerState:
        """Get current scanner state."""
        return self.state
    
    def get_scan_count(self) -> int:
        """Get total number of scans captured."""
        return self.scan_count


# Backward compatibility: main() function for direct script execution
def main():
    """Main entry point for direct script execution."""
    scanner = Scanner()
    try:
        if scanner.start():
            # Keep running until interrupted
            while scanner.is_running():
                time.sleep(1)
    except KeyboardInterrupt:
        print("\n[SCANNER] Interrupted by user")
    finally:
        scanner.stop()


if __name__ == "__main__":
    main()
