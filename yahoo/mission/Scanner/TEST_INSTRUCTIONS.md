# Scanner Testing Instructions

## Quick Test on GoPiGo

### 1. Pull Latest Code
```bash
cd ~/yahooRobot
git pull
```

### 2. Run Test Suite
```bash
cd yahoo/mission/scanner
python3 test_scanner.py
```

This will verify:
- ✅ Import safety
- ✅ State machine
- ✅ Completion callbacks
- ✅ Edge detection
- ✅ Scanner lifecycle

### 3. Test Actual Scanning

**Option A: Direct execution (backward compatible)**
```bash
python3 scanner.py
```

**Option B: Programmatic usage**
```python
from yahoo.mission.scanner.scanner import Scanner

# With completion callback
def on_scan(file_path):
    print(f"✅ Scan complete: {file_path}")

scanner = Scanner(completion_callback=on_scan)
scanner.start()

# Keep running until Ctrl+C
try:
    while scanner.is_running():
        time.sleep(1)
except KeyboardInterrupt:
    scanner.stop()
```

### 4. Verify State Transitions

Watch for these state transitions when paper is inserted:
```
[SCANNER] State: IDLE → PROCESSING (paper detected)
[SCANNER] State: PROCESSING → SUCCESS
[SCANNER] Captured scan #1: scan_0001.jpg
[SCANNER] State: SUCCESS → COOLDOWN (2.0s)
[SCANNER] State: COOLDOWN → IDLE (ready for next scan)
```

### 5. Test Requirements

✅ **One insertion = one capture**
- Insert paper once → should see exactly one scan saved
- Scanner should lock during PROCESSING
- No duplicate captures

✅ **Cooldown period**
- After capture, wait ~2 seconds before ready for next scan
- Should see COOLDOWN → IDLE transition

✅ **Edge-triggered**
- Only triggers on brightness increase (paper insertion)
- Doesn't trigger continuously while paper is present

✅ **Completion signal**
- If callback provided, should be called with file path
- Check console for callback messages

### 6. Check Scans

```bash
ls -lh scans/
# Should see scan_0001.jpg, scan_0002.jpg, etc.
```

## Troubleshooting

**Camera not opening:**
- Run: `python3 check_camera.py`
- Check: `ls -l /dev/video*`
- Enable camera: `sudo raspi-config` → Interface Options → Camera

**No detections:**
- Check lighting conditions
- Adjust threshold: `Scanner(detection_threshold=50)` (higher = less sensitive)
- Verify paper is in center of camera view

**Multiple captures:**
- Should not happen - scanner locks in PROCESSING state
- If it does, check state transitions in logs

