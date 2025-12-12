# 🧪 GoPiGo Scanner Testing Guide

Complete testing documentation for the GoPiGo paper scanner.

---

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Initial Setup](#initial-setup)
3. [Basic Functionality Tests](#basic-functionality-tests)
4. [Paper Detection Tests](#paper-detection-tests)
5. [Database Tests](#database-tests)
6. [LED Feedback Tests](#led-feedback-tests)
7. [Error Handling Tests](#error-handling-tests)
8. [Performance Tests](#performance-tests)
9. [Troubleshooting](#troubleshooting)
10. [Test Checklist](#test-checklist)

---

## Prerequisites

Before testing, ensure you have:

- [ ] GoPiGo robot powered on
- [ ] Connected to GoPiGo WiFi network
- [ ] Camera module connected and enabled
- [ ] Code deployed to GoPiGo (`deploypi`)
- [ ] Dependencies installed (`pip3 install -r requirements.txt`)
- [ ] Database created (`python3 setup_db.py`)

---

## Initial Setup

### Step 1: Verify Platform Detection

```bash
# SSH to GoPiGo
robopi

# Navigate to scanner
cd ~/yahooRobot/yahoo/mission/scanner

# Run scanner (should auto-detect GoPiGo)
python3 scanner.py
```

**Expected Output:**
```
============================================================
📄 GoPiGo Paper Scanner
============================================================
Brightness threshold: 180
Scan folder: scans
============================================================

✅ GoPiGo camera (PiCamera2) initialized
📄 System Ready — Waiting for paper...
Press Ctrl+C to quit
```

**✅ Pass Criteria:**
- Shows "GoPiGo Paper Scanner" (not Mac/Windows)
- Camera initializes successfully
- No errors about missing picamera2

**❌ Fail Criteria:**
- Shows error about not being on GoPiGo
- Camera initialization fails
- Missing picamera2 error

---

## Basic Functionality Tests

### Test 1: Scanner Startup

**Test:** Verify scanner starts correctly

**Steps:**
1. Run `python3 scanner.py`
2. Observe startup messages
3. Check LEDs (should be off/idle)

**Expected:**
- Scanner starts without errors
- Camera initializes
- LEDs are off (idle state)
- Console shows "System Ready — Waiting for paper..."

**Result:** ☐ Pass ☐ Fail

---

### Test 2: Camera Feed

**Test:** Verify camera is capturing frames

**Steps:**
1. Start scanner
2. Place paper in front of camera
3. Watch console for "Paper detected" message

**Expected:**
- Paper detection triggers within 1-2 seconds
- No "Camera failure" errors
- Scanner responds to paper presence

**Result:** ☐ Pass ☐ Fail

---

## Paper Detection Tests

### Test 3: White Paper Detection

**Test:** Detect standard white paper

**Steps:**
1. Start scanner
2. Place white 8.5x11" paper in front of camera
3. Ensure good lighting
4. Wait for detection

**Expected:**
- Paper detected within 1-2 seconds
- Console shows: "📄 Paper detected → Processing..."
- LEDs turn yellow (processing)
- Image saved successfully

**Result:** ☐ Pass ☐ Fail

**Notes:**
- If not detected, try lowering brightness threshold
- Ensure paper is centered in camera view
- Check lighting conditions

---

### Test 4: Different Paper Sizes

**Test:** Detect various paper sizes

**Test Cases:**
- [ ] Letter size (8.5x11")
- [ ] A4 size
- [ ] Half sheet (5.5x8.5")
- [ ] Small note (3x5")

**Expected:**
- All sizes detected if bright enough
- Detection time < 2 seconds
- Images saved correctly

**Result:** ☐ Pass ☐ Fail

---

### Test 5: Brightness Threshold Tuning

**Test:** Adjust brightness threshold for different lighting

**Steps:**
1. Create `.env` file with different thresholds:
   ```bash
   echo "BRIGHTNESS_THRESHOLD=150" > .env  # Lower for dim lighting
   echo "BRIGHTNESS_THRESHOLD=200" > .env  # Higher for bright lighting
   ```
2. Test with paper in different lighting conditions
3. Find optimal threshold value

**Expected:**
- Lower threshold (150-170): Detects paper in dim lighting
- Default (180): Works in normal lighting
- Higher threshold (190-210): Reduces false positives in bright lighting

**Result:** ☐ Pass ☐ Fail

**Optimal Threshold Found:** `_____`

---

### Test 6: False Positive Prevention

**Test:** Ensure scanner doesn't trigger on empty surface

**Steps:**
1. Start scanner
2. Point camera at empty desk/surface
3. Wait 10 seconds
4. Verify no false detections

**Expected:**
- No false detections on empty surface
- Scanner remains in idle state
- LEDs stay off

**Result:** ☐ Pass ☐ Fail

---

## Database Tests

### Test 7: Database Creation

**Test:** Verify database is created correctly

**Steps:**
1. Run `python3 setup_db.py`
2. Check if `scans.db` file exists
3. Verify database structure

**Expected:**
- Database file created: `scans.db`
- Console shows: "✅ Database created successfully."
- File exists in scanner directory

**Result:** ☐ Pass ☐ Fail

---

### Test 8: Scan Record Storage

**Test:** Verify scans are saved to database

**Steps:**
1. Run scanner
2. Scan a paper (trigger detection)
3. Stop scanner (Ctrl+C)
4. Run `python3 verify_scanner.py`

**Expected:**
- Scan appears in database
- Image path is correct
- Timestamp is recorded
- Image file exists

**Result:** ☐ Pass ☐ Fail

**Database Record:**
```
Scan ID: _____
Image Path: _____
Timestamp: _____
```

---

### Test 9: Multiple Scans

**Test:** Store multiple scans correctly

**Steps:**
1. Start scanner
2. Scan 3-5 papers sequentially
3. Wait for each to complete
4. Verify all scans in database

**Expected:**
- All scans stored in database
- Each has unique ID
- Each has unique timestamp
- All image files exist

**Result:** ☐ Pass ☐ Fail

**Scans Recorded:** `_____`

---

## LED Feedback Tests

### Test 10: LED Idle State

**Test:** Verify LEDs are off when idle

**Steps:**
1. Start scanner
2. Don't place any paper
3. Observe LEDs

**Expected:**
- Left LED: OFF
- Right LED: OFF
- LEDs remain off until paper detected

**Result:** ☐ Pass ☐ Fail

---

### Test 11: LED Processing State

**Test:** Verify LEDs turn yellow during processing

**Steps:**
1. Start scanner
2. Place paper in front of camera
3. Observe LEDs immediately

**Expected:**
- Left LED: YELLOW
- Right LED: YELLOW
- LEDs turn yellow when "Paper detected" message appears
- Yellow state lasts ~0.3 seconds

**Result:** ☐ Pass ☐ Fail

---

### Test 12: LED Success State

**Test:** Verify LEDs turn green on success

**Steps:**
1. Start scanner
2. Place paper and wait for detection
3. Observe LEDs after image saved

**Expected:**
- Left LED: GREEN
- Right LED: GREEN
- Green state lasts ~1.3 seconds
- LEDs return to off (idle) after success

**Result:** ☐ Pass ☐ Fail

---

### Test 13: LED Error State

**Test:** Verify LEDs turn red on error

**Steps:**
1. Start scanner
2. Trigger an error (e.g., camera failure, save failure)
3. Observe LEDs

**Expected:**
- Left LED: RED
- Right LED: RED
- Red state lasts ~1.3 seconds
- LEDs return to off (idle) after error

**Result:** ☐ Pass ☐ Fail

**Note:** Errors are rare in normal operation. To test, you may need to simulate an error condition.

---

## Error Handling Tests

### Test 14: Camera Not Available

**Test:** Handle camera initialization failure gracefully

**Steps:**
1. Disable camera in `raspi-config` (or disconnect)
2. Run scanner
3. Observe error handling

**Expected:**
- Clear error message about camera
- Helpful tips to fix issue
- Scanner exits gracefully (doesn't crash)

**Result:** ☐ Pass ☐ Fail

---

### Test 15: Database Write Failure

**Test:** Handle database write errors

**Steps:**
1. Make database file read-only: `chmod 444 scans.db`
2. Run scanner and scan a paper
3. Observe error handling

**Expected:**
- Error message about database write failure
- Scanner continues running (doesn't crash)
- LED shows error state (red)

**Result:** ☐ Pass ☐ Fail

**Cleanup:** `chmod 644 scans.db` (restore write permissions)

---

### Test 16: Image Save Failure

**Test:** Handle image save errors

**Steps:**
1. Make scans folder read-only: `chmod 555 scans/`
2. Run scanner and scan a paper
3. Observe error handling

**Expected:**
- Error message about image save failure
- Scanner continues running
- LED shows error state (red)

**Result:** ☐ Pass ☐ Fail

**Cleanup:** `chmod 755 scans/` (restore permissions)

---

## Performance Tests

### Test 17: Detection Speed

**Test:** Measure paper detection time

**Steps:**
1. Start scanner
2. Place paper in front of camera
3. Measure time from placement to "Paper detected" message
4. Repeat 5 times and average

**Expected:**
- Detection time: < 2 seconds
- Consistent performance across multiple tests

**Result:** ☐ Pass ☐ Fail

**Average Detection Time:** `_____ seconds`

---

### Test 18: Image Capture Speed

**Test:** Measure time from detection to saved image

**Steps:**
1. Start scanner
2. Place paper and trigger detection
3. Measure time from "Paper detected" to "Saved image" message
4. Repeat 5 times and average

**Expected:**
- Capture time: < 1 second
- Image saved successfully each time

**Result:** ☐ Pass ☐ Fail

**Average Capture Time:** `_____ seconds`

---

### Test 19: Continuous Operation

**Test:** Run scanner for extended period

**Steps:**
1. Start scanner
2. Run for 10 minutes
3. Scan papers periodically
4. Monitor for memory leaks or crashes

**Expected:**
- No crashes or errors
- Consistent performance over time
- All scans saved correctly

**Result:** ☐ Pass ☐ Fail

---

## Troubleshooting

### Issue: Paper Not Detected

**Symptoms:**
- Paper placed but no detection
- Scanner stays in idle state

**Solutions:**
1. Lower brightness threshold: `echo "BRIGHTNESS_THRESHOLD=150" > .env`
2. Improve lighting conditions
3. Ensure paper is centered in camera view
4. Check camera view with: `libcamera-still -o test.jpg`

---

### Issue: False Positives

**Symptoms:**
- Scanner triggers without paper
- Detects empty surface

**Solutions:**
1. Raise brightness threshold: `echo "BRIGHTNESS_THRESHOLD=200" > .env`
2. Check for bright reflections
3. Ensure camera view is clear

---

### Issue: Camera Not Initializing

**Symptoms:**
- Error: "Failed to initialize PiCamera2"
- Scanner exits immediately

**Solutions:**
1. Enable camera: `sudo raspi-config` → Interface Options → Camera
2. Reboot: `sudo reboot`
3. Install picamera2: `pip3 install picamera2`
4. Test camera: `libcamera-still -o test.jpg`

---

### Issue: LEDs Not Working

**Symptoms:**
- LEDs don't change color
- LEDs stay off

**Solutions:**
1. Install easygopigo3: `pip3 install easygopigo3`
2. Verify GoPiGo connection: `python3 -c "from easygopigo3 import EasyGoPiGo3; gpg = EasyGoPiGo3(); print('OK')"`
3. Check hardware connections

---

### Issue: Database Errors

**Symptoms:**
- "Database not found" error
- Scans not saving

**Solutions:**
1. Create database: `python3 setup_db.py`
2. Check file permissions: `ls -la scans.db`
3. Verify database location matches code

---

## Test Checklist

Use this checklist for comprehensive testing:

### Setup
- [ ] Platform detection works
- [ ] Camera initializes
- [ ] Database created
- [ ] Dependencies installed

### Basic Functionality
- [ ] Scanner starts correctly
- [ ] Camera feed works
- [ ] Paper detection works

### Paper Detection
- [ ] White paper detected
- [ ] Various sizes work
- [ ] Brightness threshold tunable
- [ ] No false positives

### Database
- [ ] Database created
- [ ] Scans stored correctly
- [ ] Multiple scans work
- [ ] Records are accurate

### LEDs
- [ ] Idle state (off)
- [ ] Processing state (yellow)
- [ ] Success state (green)
- [ ] Error state (red)

### Error Handling
- [ ] Camera errors handled
- [ ] Database errors handled
- [ ] Image save errors handled
- [ ] Graceful failures

### Performance
- [ ] Detection speed acceptable
- [ ] Capture speed acceptable
- [ ] Continuous operation stable

---

## Test Results Summary

**Date:** `_____`

**Tester:** `_____`

**GoPiGo Serial Number:** `_____`

**Test Results:**
- Total Tests: `_____`
- Passed: `_____`
- Failed: `_____`
- Pass Rate: `_____%`

**Issues Found:**
1. `_____`
2. `_____`
3. `_____`

**Notes:**
`_____`

---

## Quick Test Commands

```bash
# Setup
cd ~/yahooRobot/yahoo/mission/scanner
python3 setup_db.py

# Run scanner
python3 scanner.py

# Verify scans
python3 verify_scanner.py

# View scans
python3 view_scans.py

# Check database
sqlite3 scans.db "SELECT * FROM scans;"
```

---

**Last Updated:** 2025-12-12

