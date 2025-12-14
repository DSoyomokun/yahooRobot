# 🎮 Yahoo Robot Commands Reference

Quick reference guide for running the Yahoo Robot and its test scripts.

---

## 📋 Table of Contents

- [Development Aliases](#development-aliases) ⚡
- [Robot Commands](#robot-commands)
- [Test Commands](#test-commands)
- [Quick Examples](#quick-examples)

---

## ⚡ Development Aliases

**Quick setup:** Run `./scripts/setup_aliases.sh` to install these aliases automatically.

### Available Aliases

```bash
# Pull latest from GitHub (use on normal WiFi)
gitup

# Deploy code to robot (use on GoPiGo WiFi)
deploypi

# SSH into robot (normal, no GUI)
robopi

# SSH into robot with X11 forwarding (for GUI apps like cv2.imshow)
robopi_x

# Full sync - gitup + deploypi (ONLY when online)
fullsync
```

### Workflow Example

```bash
# Step 1: On normal WiFi - pull latest updates
gitup

# Step 2: Connect to GoPiGo WiFi, then deploy
deploypi

# Step 3: SSH into robot
robopi

# Step 4: Run your code
cd ~/yahooRobot
python3 main.py test mac
```

**💡 Why separate commands?**
- `gitup` needs internet (use on normal WiFi)
- `deploypi` works offline (use on GoPiGo WiFi)
- You might want to pull without deploying, or deploy without pulling

**📺 GUI Applications (X11 Forwarding)**

For apps that show windows (like `cv2.imshow`), use `robopi_x` instead of `robopi`:

1. **Install XQuartz on Mac** (if not already installed):
   ```bash
   brew install --cask xquartz
   ```

2. **Open XQuartz** (keep it running)

3. **Use `robopi_x` for GUI apps:**
   ```bash
   robopi_x                    # SSH with X11 forwarding
   echo $DISPLAY              # Verify (should show localhost:10.0)
   python3 main.py test pi_camera  # Run camera test with GUI
   ```

Windows will appear on your Mac via XQuartz.

See [Robot Development Workflow](ROBOT_DEV_WORKFLOW.md) for full details.

---

## 🤖 Robot Commands

### Run the Robot

```bash
# Run robot (default)
python3 main.py run

# Run in simulation mode (no hardware required)
python3 main.py run --simulate

# Run with debug logging
python3 main.py run --debug

# Start web interface
python3 main.py run --webui

# Combine options
python3 main.py run --simulate --debug
```

**Backward Compatibility:** The old-style commands still work:
```bash
python3 main.py --simulate
python3 main.py --debug
python3 main.py --webui
```

---

## 🧪 Test Commands

### List Available Tests

```bash
python3 main.py test --list
```

### Run Tests

```bash
# Run gesture detection test (Mac)
python3 main.py test mac

# Run camera test
python3 main.py test camera

# Run gesture test (alias for mac)
python3 main.py test gesture

# Run Pi camera test (on Raspberry Pi)
python3 main.py test pi_camera
```

### Story & Feature Tests

These are standalone scripts for testing major features and user stories.

**Workflow:**
1.  `(On Dev Machine)` Pull latest code: `gitup`
2.  `(On Dev Machine)` Deploy to robot: `deploypi`
3.  `(On Dev Machine)` SSH into robot: `robopi`
4.  `(On Robot)` Navigate to project directory: `cd ~/yahooRobot`
5.  `(On Robot)` Run the desired test script.

#### Story 1.2: Test Linear Movement

This test validates the robot's ability to drive in a straight line.

```bash
# Run on the robot (requires hardware)
python3 tests/test_linear_movement.py

# Run in simulation on any machine
python3 tests/test_linear_movement.py --simulate
```
> **Note:** When running on hardware, the test will pause and ask for confirmation before starting. It will also require you to manually measure the distance traveled at the end.

#### Story 1.3: Test Precise Turns

This test validates the robot's ability to perform accurate in-place turns using IMU feedback.

```bash
# Run on the robot (requires hardware and IMU)
python3 tests/test_turns.py

# Run in simulation on any machine
python3 tests/test_turns.py --simulate
```

**What it tests:**
- 90° right turn (within ±3° tolerance)
- 90° left turn (within ±3° tolerance)
- 180° turn (within ±3° tolerance)

> **Note:** When running on hardware, the test will pause before each turn and ask for confirmation. Make sure the robot has clear space to rotate in place without hitting obstacles.

#### Story 1.4: Execute Full Row Traversal

This script tests the robot's ability to navigate to all configured desks and return to origin.

```bash
# Run on the robot (requires hardware)
python3 scripts/run_row_traversal.py

# Run in simulation on any machine
python3 scripts/run_row_traversal.py --simulate
```

#### Stories 2.1 + 2.2: Desk-Centric Polling System

This test validates the person detection and desk polling systems working together.

```bash
# Run on the robot (requires hardware, camera, and IMU)
python3 tests/test_desk_polling.py

# Run in simulation on any machine
python3 tests/test_desk_polling.py --simulate
```

**What it tests:**
- Person detector (back-view optimized for detecting students from behind)
- Desk poller initialization and configuration
- Full polling scan (robot turns to face each desk sequentially)
- Detection queue creation (occupied desks found during scan)
- Summary statistics generation

**On hardware, this will:**
- Turn the robot to face each desk at configured scan angles
- Capture camera frame at each desk
- Run person detection using MediaPipe Pose (shoulder visibility)
- Build a list of occupied desk IDs
- Provide LED feedback (green blink when person detected)

> **Note:** When running on hardware, ensure the robot has clear space to rotate in place and that the camera has a clear view of each desk. The robot will turn approximately ±66° during the scan.

#### Camera Desk Monitor - Fixed Camera Person Detection (NEW)

**Updated Approach:** This is a simplified version of desk polling for demonstration purposes.

```bash
# Auto-detect camera
python3 scripts/camera_desk_monitor.py

# Use specific camera device
python3 scripts/camera_desk_monitor.py --camera 1

# Enable debug output
python3 scripts/camera_desk_monitor.py --debug
```

**What it does:**
- Uses a **single fixed camera** positioned to view all 4 desks at once
- Divides the camera frame into 4 regions (one per desk)
- Runs person detection on each region independently
- Shows real-time occupancy status: OCCUPIED or EMPTY for each desk
- Displays visual overlay with color-coded regions (green=occupied, red=empty)
- Press 's' for summary statistics, 'q' to quit

**Setup:**
1. Position camera to view all 4 desks in one frame
2. Desks should be arranged left to right: 1, 2, 3, 4
3. Camera should be roughly centered and high enough to see all desks

**Why this approach?**
- **Previous approach** (`test_desk_polling.py`): Robot turned to face each desk sequentially - more complex, required robot movement and hardware
- **New approach** (`camera_desk_monitor.py`): Single fixed camera view - simpler, faster implementation to save time for demonstration
- No robot movement needed, just camera and person detection
- Still demonstrates the core perception capability (person detection)

**Output example:**
```
==========================================================
DESK OCCUPANCY SUMMARY
==========================================================

Occupied desks: [1, 3, 4]
Empty desks: [2]

Occupancy rates (last 30 frames):
  Desk 1: 95.0% - OCCUPIED
  Desk 2: 10.0% - EMPTY
  Desk 3: 88.0% - OCCUPIED
  Desk 4: 92.0% - OCCUPIED
==========================================================
```

> **Note:** This simplified approach was adopted to save development time while still demonstrating the person detection capability. The original desk-centric polling system (robot turning to each desk) is still available in `tests/test_desk_polling.py` for reference.

#### Story 3.1: Delivery Mission

This executes the full paper delivery workflow.

```bash
# ON ROBOT: Manual mode (default) - enter occupied desks at prompt
python3 scripts/run_delivery_mission.py --manual

# ON ROBOT: Debug - Only visit first 2 occupied desks
python3 scripts/run_delivery_mission.py --manual --limit-desks 2

# ON MAC: Simulation mode - test workflow without hardware
python3 scripts/run_delivery_mission.py --simulate

# ON MAC: Simulation with limited desks
python3 scripts/run_delivery_mission.py --simulate --limit-desks 2

# Future: Automated mode with person detection
python3 scripts/run_delivery_mission.py --auto
```

**What it does:**
1. Prompts for occupied desk IDs (e.g., "1,2,4")
2. Navigates only to occupied desks (skips empty desks)
3. At each desk:
   - Turns left 90° to face the desk
   - Delivers paper
   - Waits for ENTER (student confirms receipt)
   - Turns back to continue
4. Shows delivery statistics at end

**Why manual mode?**
- Fast implementation for deadline
- Person detection code exists but not integrated yet
- Easy to switch to `--auto` mode later
- See code comments for future integration steps

**Setup (Hardware Mode):**
- Position robot in front of Desk 1, facing along the row

**Simulation Mode:**
- Run on your Mac to test workflow logic
- No robot hardware needed
- Logs show `[SIMULATED] robot.drive.drive_cm(104)` instead of actual movement
- All user prompts still work (enter occupied desks, press ENTER at desks)
- Perfect for testing logic before deploying to robot

**Phase Logging:**
- Shows "📦 PHASE: PAPER DELIVERY (Passing Out)"
- Clear indication of what the mission is doing

**Future automated mode:**
- Uses `DeskPoller.scan_for_persons()` to identify occupied desks
- No manual input needed
- Already implemented in `yahoo/sense/person_detector.py`

#### Story 3.2: Collection Mission

This executes the full paper collection workflow.

```bash
# ON ROBOT: Quick test - collect from 1 desk, no timer
python3 scripts/run_collection_mission.py --limit-desks 1

# ON ROBOT: Test with 2 desks
python3 scripts/run_collection_mission.py --limit-desks 2

# ON ROBOT: Full mission - all 4 desks, start immediately
python3 scripts/run_collection_mission.py

# ON ROBOT: Full mission with 10-minute countdown timer
python3 scripts/run_collection_mission.py --timer 10

# ON MAC: Simulation mode - test workflow without hardware
python3 scripts/run_collection_mission.py --simulate

# ON MAC: Simulation with timer
python3 scripts/run_collection_mission.py --simulate --timer 5
```

**What it does:**
1. Optional countdown timer (e.g., 10 minutes for students to complete work)
2. Navigates to each desk in sequence along the row
3. At each desk:
   - Turns left 90° to face the desk
   - Waits for student to insert paper (press ENTER)
   - Scans paper and saves with desk_id + timestamp
   - Turns back to continue to next desk
4. Shows collection statistics at end

**Setup (Hardware Mode):**
- Position robot in front of Desk 1, facing along the row (parallel to desks)
- Same positioning as row traversal test

**Simulation Mode:**
- Run on your Mac to test collection workflow
- No robot hardware needed
- Logs show `[SIMULATED] robot.drive.turn_degrees(-90)` instead of actual turns
- All prompts still work (timer confirmation, ENTER at each desk)
- Tests end-to-end workflow logic

**Phase Logging:**
- Shows "📥 PHASE: PAPER COLLECTION"
- Timer countdown visible
- Clear desk-by-desk progress

**Files saved to:** `collected_papers/desk_N_YYYYMMDD_HHMMSS.txt`

> **Note:** Robot uses hardcoded distances between desks (104cm, 238cm, 104cm). Does 180° turn after Desk 2 to reverse direction.

#### Hand Raise Helper (On-Demand Assistance)

Watches for hand raise gestures and navigates to specific desk for student help.

```bash
# ON ROBOT: One-time assistance - help one student and exit
python3 scripts/hand_raise_helper.py

# ON ROBOT: Continuous mode - keep helping multiple students
python3 scripts/hand_raise_helper.py --continuous

# ON MAC: Simulation mode - test workflow without hardware/webcam
python3 scripts/hand_raise_helper.py --simulate

# ON MAC: Simulation in continuous mode
python3 scripts/hand_raise_helper.py --simulate --continuous

# Future: Automated desk identification
python3 scripts/hand_raise_helper.py --auto
```

**What it does:**
1. Watches webcam for hand raise gesture (using MediaPipe Pose)
2. When detected, prompts: "Which desk raised hand? (1-4):"
3. Navigates to that specific desk
4. Provides assistance
5. (Optional) Returns to start and repeats

**Use case:**
- Student needs help during work time
- Raises hand in front of webcam
- Robot goes to help that specific student
- Not part of main delivery/collection workflow

**Simulation Mode:**
- Run on your Mac without webcam or hardware
- Fakes gesture detection (press ENTER to simulate hand raise)
- All navigation logged as `[SIMULATED]`
- Tests the assistance workflow end-to-end
- No OpenCV/webcam required

**Phase Logging:**
- Shows "✋ PHASE: ON-DEMAND STUDENT ASSISTANCE (Hand Raise)"
- Clear indication this is the help workflow

**Why manual desk confirmation?**
- Webcam detects gesture but not desk location
- Fast implementation for deadline
- Gesture detection code already exists
- Future: Use `DeskPoller.scan_for_raised_hands()` for automated desk ID

**Setup (Hardware Mode):**
- Position robot in front of Desk 1, facing along the row
- Webcam should have view of students

---

## 🚀 Quick Examples

### Development on Mac

```bash
# Test camera
python3 main.py test camera

# Test gesture detection
python3 main.py test mac

# Run robot in simulation mode
python3 main.py run --simulate --debug
```

### On Raspberry Pi

```bash
# Test gesture detection with camera
python3 -m tests.test_gesture_pi --cam csi

# Test with USB camera
python3 -m tests.test_gesture_pi --cam usb

# Test with debug output (for tuning thresholds)
python3 -m tests.test_gesture_pi --cam csi --debug

# Run robot with hardware
python3 main.py run

# Run with debug logging
python3 main.py run --debug
```

---

## 📝 Adding New Tests

To add a new test, update the `test_scripts` dictionary in `main.py`:

```python3
test_scripts = {
    'mac': 'tests/test_gesture_mac.py',
    'camera': 'scripts/camera_test.py',
    'gesture': 'tests/test_gesture_mac.py',
    'your_new_test': 'path/to/your_test.py',  # Add here
}
```

Then run it with:
```bash
python3 main.py test your_new_test
```

---

## 🔍 Help

Get help for any command:

```bash
# General help
python3 main.py --help

# Help for run command
python3 main.py run --help

# Help for test command
python3 main.py test --help
```

---

## 📚 Related Documentation

- [Robot Development Workflow](ROBOT_DEV_WORKFLOW.md) - How to sync code to robot
- [Quick Start Guide](QUICK_START.md) - Getting started with the project
- [Raspberry Pi Setup](RASPBERRY_PI_SETUP.md) - Pi-specific setup instructions

