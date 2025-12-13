# Production-Ready Paper Scanner

Edge-triggered paper scanner for GoPiGo robot with state machine and completion signals.

## Overview

The scanner detects paper insertions using brightness-based edge detection, captures exactly one image per insertion, and saves it to the `scans/` folder. Designed for integration with robot path planning systems.

**Key Features:**
- ✅ **Edge-triggered detection** - Only triggers on paper insertion (not continuous)
- ✅ **State machine** - IDLE → PROCESSING (locked) → SUCCESS → COOLDOWN → IDLE
- ✅ **One insertion = one capture** - Locking prevents duplicate captures
- ✅ **Completion signals** - Callback mechanism for robot integration
- ✅ **Safe to import** - No side effects until `start()` is called
- ✅ **GoPiGo only** - Requires Raspberry Pi hardware (prevents Mac execution)

## Requirements

- **Hardware:** GoPiGo robot with Raspberry Pi
- **Camera:** CSI camera module enabled on Raspberry Pi
- **Software:** Python 3, OpenCV (`opencv-python-headless`)

## Installation

### 1. Enable Camera on Raspberry Pi

```bash
sudo raspi-config
# Navigate to: Interface Options → Camera → Enable
sudo reboot
```

### 2. Verify Camera

```bash
# Check camera device exists
ls -l /dev/video*

# Test camera
libcamera-still -o test.jpg
```

### 3. Install Dependencies

```bash
pip3 install opencv-python-headless
```

## Usage

### Basic Usage (Direct Execution)

```bash
cd ~/yahooRobot/yahoo/mission/scanner
python3 scanner.py
```

The scanner will:
1. Initialize and wait in IDLE state
2. Detect paper insertion (edge-triggered)
3. Lock in PROCESSING state and capture image
4. Save to `scans/scan_0001.jpg`, `scans/scan_0002.jpg`, etc.
5. Enter COOLDOWN period (2 seconds)
6. Return to IDLE, ready for next scan

### Programmatic Usage (Robot Integration)

```python
from yahoo.mission.scanner.scanner import Scanner

# Define completion callback
def on_scan_complete(file_path):
    print(f"Scan saved: {file_path}")
    # Signal robot to move to next desk
    robot.move_to_next_desk()

# Create and start scanner
scanner = Scanner(
    completion_callback=on_scan_complete,
    cooldown_seconds=2.0,
    detection_threshold=30
)

scanner.start()

# Scanner runs in background thread
# Keep main thread alive or integrate with robot loop
try:
    while scanner.is_running():
        # Do other robot tasks
        time.sleep(0.1)
except KeyboardInterrupt:
    scanner.stop()
```

### Scanner Class API

```python
scanner = Scanner(
    camera_config=CSI_CAMERA,          # Camera configuration
    scan_dir=None,                      # Scan directory (default: scanner/scans/)
    completion_callback=None,           # Callback(file_path: str) -> None
    cooldown_seconds=2.0,               # Cooldown after capture
    detection_threshold=30              # Brightness threshold
)

# Methods
scanner.start()                         # Start scanning (returns bool)
scanner.stop()                          # Stop scanning and release resources
scanner.is_running() -> bool            # Check if scanner is running
scanner.get_state() -> ScannerState     # Get current state (IDLE, PROCESSING, etc.)
scanner.get_scan_count() -> int         # Get total scans captured
```

## State Machine

The scanner uses a strict state machine to ensure one insertion = one capture:

```
IDLE
  ↓ (paper detected - edge trigger)
PROCESSING (locked - no new detections)
  ↓ (image saved)
SUCCESS
  ↓ (detector reset)
COOLDOWN (2 seconds)
  ↓ (timeout)
IDLE (ready for next scan)
```

**State Descriptions:**
- **IDLE:** Waiting for paper insertion. Detector actively monitoring.
- **PROCESSING:** Paper detected, capturing image. Scanner is locked - no new detections.
- **SUCCESS:** Image saved, detector reset. Transitioning to cooldown.
- **COOLDOWN:** Waiting period before ready for next scan. Prevents immediate re-triggering.

## Edge-Triggered Detection

The scanner uses brightness-based edge detection:

- **Baseline:** Establishes brightness baseline when no paper is present
- **Trigger:** Only triggers on brightness **increase** (paper insertion)
- **Lock:** Once triggered, locks until image is captured and cooldown completes
- **Reset:** After capture, baseline updates to current brightness for next detection

This ensures:
- ✅ One insertion → exactly one capture
- ✅ No duplicate captures from same paper
- ✅ Only detects transitions (insertion), not continuous presence

## Completion Callback

The completion callback is called when a scan is saved:

```python
def my_callback(file_path: str):
    # file_path is the full path to saved image
    # e.g., "/path/to/scans/scan_0001.jpg"
    print(f"Scan complete: {file_path}")
    # Signal robot, update UI, etc.

scanner = Scanner(completion_callback=my_callback)
```

**Callback Signature:**
- **Parameter:** `file_path: str` - Full path to saved scan image
- **Called:** Immediately after image is saved (in PROCESSING → SUCCESS transition)
- **Thread:** Called from scanner thread (ensure thread-safe operations)

## Testing

### Run Test Suite

```bash
cd ~/yahooRobot/yahoo/mission/scanner
python3 test_scanner.py
```

Tests verify:
- ✅ Import safety (no side effects)
- ✅ State machine (all states present)
- ✅ Completion callback mechanism
- ✅ Edge-triggered detection logic
- ✅ Scanner lifecycle (start/stop)

### Manual Testing

1. **Start scanner:**
   ```bash
   python3 scanner.py
   ```

2. **Watch for state transitions:**
   ```
   [SCANNER] State: IDLE → PROCESSING (paper detected)
   [SCANNER] State: PROCESSING → SUCCESS
   [SCANNER] Captured scan #1: scan_0001.jpg
   [SCANNER] State: SUCCESS → COOLDOWN (2.0s)
   [SCANNER] State: COOLDOWN → IDLE (ready for next scan)
   ```

3. **Verify scans:**
   ```bash
   ls -lh scans/
   # Should see scan_0001.jpg, scan_0002.jpg, etc.
   ```

### Test Requirements

✅ **One insertion = one capture**
- Insert paper once → exactly one scan saved
- Scanner locks during PROCESSING
- No duplicate captures

✅ **Cooldown period**
- After capture, wait ~2 seconds before ready
- Should see COOLDOWN → IDLE transition

✅ **Edge-triggered**
- Only triggers on brightness increase (insertion)
- Doesn't trigger continuously while paper present

## Troubleshooting

### Camera Not Opening

```bash
# Run diagnostic script
python3 check_camera.py

# Check camera device
ls -l /dev/video*

# Verify camera enabled
vcgencmd get_camera
# Should show: supported=1 detected=1

# Enable camera
sudo raspi-config
# Interface Options → Camera → Enable
sudo reboot
```

### No Detections

- **Check lighting:** Ensure good contrast between paper and background
- **Adjust threshold:** Increase `detection_threshold` (default: 30)
  ```python
  scanner = Scanner(detection_threshold=50)  # Higher = less sensitive
  ```
- **Verify paper position:** Paper should be in center of camera view
- **Check state:** Scanner should be in IDLE state

### Multiple Captures

Should not happen - scanner locks in PROCESSING state. If it does:
- Check state transitions in logs
- Verify cooldown period is completing
- Ensure detector is resetting properly

### Scanner Won't Start on Mac

This is intentional - scanner requires Raspberry Pi hardware. You'll see:
```
[SCANNER] ERROR: Scanner requires Raspberry Pi hardware
[SCANNER] This scanner is designed for GoPiGo robot only
```

## Integration with Robot

The scanner is designed as a pure intake primitive for robot path planning:

```python
# Example: Robot mission flow
robot = Robot()
scanner = Scanner(completion_callback=on_scan_complete)

# Move to desk
robot.move_to_desk(desk_id=1)

# Start scanner
scanner.start()

# Wait for scan (completion callback handles next step)
# Or poll:
while scanner.get_state() != ScannerState.IDLE:
    time.sleep(0.1)

# Move to next desk
robot.move_to_desk(desk_id=2)
```

## File Structure

```
scanner/
├── scanner.py          # Main Scanner class
├── detector.py         # Edge-triggered PaperDetector
├── test_scanner.py     # Test suite
├── check_camera.py     # Camera diagnostic tool
├── scans/              # Saved scan images (scan_0001.jpg, etc.)
└── README.md           # This file
```

## Configuration

### Detection Threshold

Controls sensitivity of paper detection:
- **Lower (10-20):** More sensitive, triggers on smaller brightness changes
- **Default (30):** Balanced for typical paper/background contrast
- **Higher (50+):** Less sensitive, requires larger brightness increase

```python
scanner = Scanner(detection_threshold=40)
```

### Cooldown Period

Time to wait after capture before ready for next scan:
- **Default:** 2.0 seconds
- **Shorter (1.0s):** Faster scanning, may be too quick
- **Longer (3.0s):** More conservative, ensures paper is removed

```python
scanner = Scanner(cooldown_seconds=3.0)
```

## Success Criteria

✅ One insertion → exactly one image captured  
✅ Scanner locks after detection, prevents duplicates  
✅ Cooldown period before ready for next scan  
✅ Importable without auto-starting  
✅ Completion signal emitted  
✅ Runs indefinitely without crashes  

## License

Part of the Yahoo Robot project.

