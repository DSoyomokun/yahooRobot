# Robot Test Scripts Guide

Complete list of all test scripts for the Yahoo Robot.

## Test Script Locations

### 1. Main Test Directory: `tests/`

Located at: `tests/`

| Script | Purpose | Usage |
|--------|---------|-------|
| `test_config_loader.py` | Test configuration loading | `python3 tests/test_config_loader.py` |
| `test_distance_tof.py` | Test distance sensor (ToF) | `python3 tests/test_distance_tof.py` |
| `test_gesture_mac.py` | Test gesture detection (Mac) | `python3 tests/test_gesture_mac.py` |
| `test_gesture_pi.py` | Test gesture detection (Pi) | `python3 tests/test_gesture_pi.py` |
| `test_pi_camera.py` | Test Pi camera | `python3 tests/test_pi_camera.py` |

### 2. Yahoo Test Directory: `yahoo/test/`

Located at: `yahoo/test/`

| Script | Purpose | Usage |
|--------|---------|-------|
| `test_drive.py` | Test drive/movement system | `python3 yahoo/test/test_drive.py` |
| `test_detection.py` | Test detection systems | `python3 yahoo/test/test_detection.py` |
| `test_mission.py` | Test mission controllers | `python3 yahoo/test/test_mission.py` |

### 3. Scanner Test: `yahoo/mission/scanner/`

Located at: `yahoo/mission/scanner/`

| Script | Purpose | Usage |
|--------|---------|-------|
| `test_scanner.py` | Test scanner functionality | `python3 yahoo/mission/scanner/test_scanner.py` |

### 4. Mission Scripts: `scripts/`

Located at: `scripts/`

| Script | Purpose | Usage |
|--------|---------|-------|
| `run_row_mission.py` | **Main row mission execution** | `python3 scripts/run_row_mission.py` |

## Quick Test Commands

### On GoPiGo (Hardware Tests)

```bash
# Navigate to project root
cd ~/yahooRobot

# Test drive/movement
python3 yahoo/test/test_drive.py

# Test gesture detection
python3 tests/test_gesture_pi.py

# Test camera
python3 tests/test_pi_camera.py

# Test scanner
python3 yahoo/mission/scanner/test_scanner.py

# Test distance sensor
python3 tests/test_distance_tof.py

# Run full row mission
python3 scripts/run_row_mission.py
```

### On Mac (Development Tests)

```bash
# Navigate to project root
cd ~/yahooRobot

# Test gesture detection (simulation)
python3 tests/test_gesture_mac.py

# Test config loading
python3 tests/test_config_loader.py
```

## Test Script Details

### Movement/Drive Tests

**`yahoo/test/test_drive.py`**
- Tests basic drive commands
- Forward, backward, turns
- Distance-based movement

**Run:**
```bash
python3 yahoo/test/test_drive.py
```

### Gesture Detection Tests

**`tests/test_gesture_pi.py`** (On GoPiGo)
- Tests gesture detection with real camera
- Logs gesture events to CSV
- Headless operation

**Run:**
```bash
python3 tests/test_gesture_pi.py --cam csi
```

**`tests/test_gesture_mac.py`** (On Mac)
- Tests gesture detection simulation
- For development without hardware

**Run:**
```bash
python3 tests/test_gesture_mac.py
```

### Scanner Tests

**`yahoo/mission/scanner/test_scanner.py`**
- Tests scanner import safety
- Tests state machine
- Tests edge detection
- Tests completion signals

**Run:**
```bash
python3 yahoo/mission/scanner/test_scanner.py
```

### Camera Tests

**`tests/test_pi_camera.py`**
- Tests Pi camera initialization
- Tests frame capture
- Verifies camera access

**Run:**
```bash
python3 tests/test_pi_camera.py
```

### Distance Sensor Tests

**`tests/test_distance_tof.py`**
- Tests Time-of-Flight distance sensor
- Reads distance measurements
- Verifies sensor connectivity

**Run:**
```bash
python3 tests/test_distance_tof.py
```

### Configuration Tests

**`tests/test_config_loader.py`**
- Tests configuration file loading
- Verifies desk configuration
- Tests config access methods

**Run:**
```bash
python3 tests/test_config_loader.py
```

## Main Mission Script

### Row Mission

**`scripts/run_row_mission.py`**
- **Main execution script for row mission**
- Runs complete cycle: pass-out → turn → collection
- Includes obstacle detection
- Scanner integration

**Run:**
```bash
python3 scripts/run_row_mission.py
```

**What it does:**
1. Moves forward 60 inches, 5 times (stops 0→1→2→3→4)
2. Turns 180° at stop 4
3. Moves backward with scanner (stops 4→3→2→1→0)

## Running All Tests

### On GoPiGo

```bash
cd ~/yahooRobot

# Test drive system
python3 yahoo/test/test_drive.py

# Test scanner
python3 yahoo/mission/scanner/test_scanner.py

# Test camera
python3 tests/test_pi_camera.py

# Test distance sensor
python3 tests/test_distance_tof.py

# Run full mission
python3 scripts/run_row_mission.py
```

## Test Script Structure

```
yahooRobot/
├── tests/                    # Main test directory
│   ├── test_config_loader.py
│   ├── test_distance_tof.py
│   ├── test_gesture_mac.py
│   ├── test_gesture_pi.py
│   └── test_pi_camera.py
│
├── yahoo/
│   ├── test/                # Yahoo package tests
│   │   ├── test_drive.py
│   │   ├── test_detection.py
│   │   └── test_mission.py
│   │
│   └── mission/
│       └── scanner/
│           └── test_scanner.py
│
└── scripts/                 # Execution scripts
    └── run_row_mission.py   # Main mission script
```

## Notes

- All test scripts should be run from the project root: `~/yahooRobot`
- Most tests require GoPiGo hardware (except `test_gesture_mac.py`)
- Use `python3` (not `python`) on Raspberry Pi
- Make sure robot has clear space before running movement tests
- Press `Ctrl+C` to stop any test script

## Quick Reference

**Most Common Tests:**
- Movement: `python3 yahoo/test/test_drive.py`
- Scanner: `python3 yahoo/mission/scanner/test_scanner.py`
- Full Mission: `python3 scripts/run_row_mission.py`

