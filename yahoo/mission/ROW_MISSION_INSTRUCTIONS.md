# Row Mission - Complete Running Instructions

Complete guide for running the 5-stop path planning system with obstacle detection and scanner integration.

## Overview

The row mission executes a complete cycle:
1. **Pass-out phase**: Move forward 60 inches, 5 times (stops 0→1→2→3→4)
2. **Turn**: 180° at stop 4
3. **Collection phase**: Move backward with scanner (stops 4→3→2→1→0)

## Prerequisites

- GoPiGo robot with Raspberry Pi
- CSI camera enabled
- Distance sensor connected (for obstacle detection)
- IMU sensor (optional, for path recovery)
- Code deployed to GoPiGo

## Quick Start

### Step 1: Deploy Code to GoPiGo

**On your Mac:**

```bash
# 1. Connect to GoPiGo WiFi (SSID: GoPiGo, Password: robots1234)

# 2. Deploy code
deploypi

# Or manually:
rsync -av --delete ~/yahooRobot/ pi@10.10.10.10:~/yahooRobot/
```

### Step 2: SSH into GoPiGo

```bash
# On Mac (after connecting to GoPiGo WiFi)
robopi

# Or manually:
ssh pi@10.10.10.10
# Password: robots1234
```

### Step 3: Switch to ej-nav Branch

**On GoPiGo:**

```bash
cd ~/yahooRobot
git fetch origin
git checkout ej-nav
git pull origin ej-nav
```

### Step 4: Verify Setup

```bash
# Check camera
python3 yahoo/mission/scanner/check_camera.py

# Verify imports work
python3 -c "from yahoo.mission import RowMission; print('✅ Imports OK')"
```

### Step 5: Run the Mission

```bash
# From project root (~/yahooRobot)
python3 scripts/run_row_mission.py
```

## What Happens During Execution

### Phase 1: Pass-Out (Forward)

```
Stop 0 (Desk 1) → Stop 1 (Desk 2) → Stop 2 (Desk 3) → Stop 3 (Desk 4) → Stop 4 (Buffer)
     ↓                ↓                ↓                ↓
Distribute        Distribute      Distribute      Distribute      (No action)
```

- Robot moves forward 60 inches between each stop
- Obstacle detection active - will stop and go around if obstacle detected
- Distributes papers at stops 0-3 (desks 1-4)
- Stop 4 is buffer position for turn

### Phase 2: 180° Turn

- Robot turns 180° at stop 4
- Positions for reverse traversal

### Phase 3: Collection (Reverse)

```
Stop 4 (Buffer) → Stop 3 (Desk 4) → Stop 2 (Desk 3) → Stop 1 (Desk 2) → Stop 0 (Desk 1)
  (No action)        ↓                  ↓                  ↓                  ↓
                 Scan (blocking)    Scan (blocking)    Scan (blocking)    Scan (blocking)
```

- Robot moves backward 60 inches between each stop
- Obstacle detection active - will stop and go around if obstacle detected
- At each desk stop (0-3), scanner waits for paper insertion
- Scanner timeout: 30 seconds per desk
- After scan completes or times out, continues to next stop

## Expected Output

```
======================================================================
ROW MISSION - Full Cycle
======================================================================

This will:
  1. Move forward 60 inches, 5 times (stops 0→1→2→3→4)
  2. Turn 180° at stop 4
  3. Move backward with scanner (stops 4→3→2→1→0)

🚀 Starting full cycle...

[ROW-MISSION] === PHASE 1: PASS-OUT ===
[PASS-OUT] Starting pass-out phase
[PASS-OUT] Navigating to Stop 0
[PASS-OUT] Moving 0.0cm from Stop 0 to Stop 0
[PASS-OUT] Arrived at Stop 0 (Desk 1)
[PASS-OUT] Distributing paper at Desk 1 (Stop 0)
[PASS-OUT] Navigating to Stop 1
[PASS-OUT] Moving 152.4cm from Stop 0 to Stop 1
...
[ROW-MISSION] === PHASE 2: 180° TURN ===
[ROW-MISSION] Executing 180° turn at Stop 4
...
[ROW-MISSION] === PHASE 3: COLLECTION ===
[COLLECTION] Starting collection phase
[COLLECTION] Navigating to Stop 3
[COLLECTION] Arrived at Stop 3 (Desk 4), waiting for paper...
[SCANNER] Ready - waiting for paper insertion...
[SCANNER] State: IDLE → PROCESSING (paper detected)
[SCANNER] Captured scan #1: scan_0001.jpg
[COLLECTION] Paper collected and scanned at Desk 4: /path/to/scan_0001.jpg
...

======================================================================
ROW MISSION SUMMARY
======================================================================

Pass-Out Phase:
  Desks visited: 4
  Papers distributed: 4
  Success: True

180° Turn:
  Success: True

Collection Phase:
  Desks visited: 4
  Papers collected: 3
  Timeouts: 1
  Success: True

Overall Success: True
======================================================================
```

## Obstacle Detection

During movement, the robot continuously checks for obstacles:

- **Threshold**: 1 foot (30.48 cm)
- **Check Rate**: Every 100ms
- **Behavior**: 
  - Stops immediately when obstacle detected
  - Performs go-around maneuver
  - Returns to original path
  - Continues to next stop

### Go-Around Maneuver

When obstacle detected:
1. Stop immediately
2. Turn right 90°
3. Move forward 0.75 feet (clear obstacle)
4. Turn left 90° (parallel to path)
5. Move forward 0.50 feet (past obstacle)
6. Turn left 90° (back toward path)
7. Move forward 0.75 feet (return to path)
8. Turn right 90° (resume heading)
9. IMU correction (if heading error > 10°)

## Scanner Behavior

During collection phase at each desk stop:

- **State**: Scanner starts in IDLE
- **Detection**: Edge-triggered brightness detection
- **Timeout**: 30 seconds (configurable)
- **Behavior**:
  - Waits for paper insertion
  - Captures image when paper detected
  - Saves to `yahoo/mission/scanner/scans/scan_XXXX.jpg`
  - Continues to next stop after scan or timeout

## Troubleshooting

### Camera Not Opening

```bash
# Check camera status
python3 yahoo/mission/scanner/check_camera.py

# Enable camera
sudo raspi-config
# Interface Options → Camera → Enable
sudo reboot
```

### Distance Sensor Not Working

```bash
# Check I2C devices
sudo i2cdetect -y 1

# Should show device at 0x08 (GoPiGo3) and distance sensor address
```

### Import Errors

```bash
# Make sure you're in project root
cd ~/yahooRobot

# Verify Python path
python3 -c "import sys; print(sys.path)"

# Test imports
python3 -c "from yahoo.mission import RowMission; print('OK')"
```

### Script Not Found

```bash
# Make sure you're in project root
pwd  # Should show: /home/pi/yahooRobot

# Check script exists
ls -la scripts/run_row_mission.py

# Run from project root
python3 scripts/run_row_mission.py
```

## Configuration

### Adjust Scanner Timeout

Edit `scripts/run_row_mission.py`:

```python
mission = RowMission(robot, scanner_timeout=60.0)  # Change from 30.0 to 60.0
```

### Adjust Obstacle Threshold

Edit `yahoo/mission/obstacle_nav.py`:

```python
OBSTACLE_THRESHOLD_CM = 45.72  # Change from 30.48 to 45.72 (1.5 feet)
```

### Adjust Stop Spacing

Edit `yahoo/config/row_config.json`:

```json
"stop_points": {
  "spacing_inches": 72,  // Change from 60 to 72
  ...
}
```

## File Locations

- **Mission script**: `scripts/run_row_mission.py`
- **Mission classes**: `yahoo/mission/`
- **Scanned images**: `yahoo/mission/scanner/scans/`
- **Configuration**: `yahoo/config/row_config.json`
- **Logs**: Check console output

## Testing Without Hardware

For testing on Mac (simulation mode):

Edit `scripts/run_row_mission.py` line 38:

```python
simulate = True  # Change to True for testing
```

Then run:

```bash
python3 scripts/run_row_mission.py
```

## Complete Command Sequence

**Full sequence from Mac to GoPiGo:**

```bash
# On Mac - Step 1: Connect to GoPiGo WiFi
# (Connect to WiFi: GoPiGo, Password: robots1234)

# On Mac - Step 2: Deploy
deploypi

# On Mac - Step 3: SSH
robopi

# On GoPiGo - Step 4: Switch branch
cd ~/yahooRobot
git checkout ej-nav
git pull origin ej-nav

# On GoPiGo - Step 5: Run mission
python3 scripts/run_row_mission.py
```

## Success Indicators

✅ **Mission successful if you see:**
- All 5 stops visited in pass-out phase
- 180° turn completed
- All 4 desk stops visited in collection phase
- Scans saved to `scans/` folder
- Final summary shows `Overall Success: True`

## Emergency Stop

Press `Ctrl+C` to stop the mission at any time. The robot will:
- Stop all movement immediately
- Release camera resources
- Print summary of progress

---

**Ready to run!** Follow the steps above to execute the complete row mission cycle.

