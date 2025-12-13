# ⚡ Quick Test Steps - GoPiGo Camera

**TL;DR version** - Get testing in 5 minutes!

---

## 🚀 Quick Start

### 1. Connect & SSH
```bash
# On Mac: Connect to GoPiGo WiFi, then:
robopi
# Password: robots1234
```

### 2. Navigate & Setup
```bash
cd ~/yahooRobot
python3 yahoo/mission/scanner/storage.py  # Initialize DB (if needed)
```

### 3. Run Scanner
```bash
# From repo root:
PYTHONPATH=. python3 yahoo/mission/scanner/scanner.py
```

**✅ Check:** Should see `[SYSTEM] Scanner ready` and camera opens successfully

### 4. Test It!
- Place white paper in front of camera
- Watch LEDs: Yellow → Green = Success!

### 5. Verify
```bash
# In new terminal: robopi
cd ~/yahooRobot/yahoo/mission/scanner
python3 verify_scanner.py
```

---

## ⚠️ Common Issues

**Problem:** Camera not opening
- **Fix:** Check camera is enabled: `sudo raspi-config` → Interface Options → Camera → Enable
- **Fix:** Test camera: `libcamera-still -o test.jpg`
- **Fix:** Reboot if needed: `sudo reboot`

**Problem:** OpenCV not installed
- **Fix:** `pip3 install opencv-python-headless`

**Problem:** Files missing
- **Fix:** On Mac: `deploypi` (while on GoPiGo WiFi)

---

For detailed instructions, see: **TEST_ON_GOPIGO.md**

