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
cd ~/yahooRobot/yahoo/mission/scanner
python3 setup_db.py
echo "USE_GOPIGO=true" > .env
echo "BRIGHTNESS_THRESHOLD=180" >> .env
```

### 3. Run Scanner
```bash
python3 scanner.py
```

**✅ Check:** Should say **"Mode: GoPiGo"** (not Mac/Windows)

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

**Problem:** Says "Mode: Mac/Windows"
- **Fix:** `cat .env` - should show `USE_GOPIGO=true`
- **Fix:** `echo "USE_GOPIGO=true" > .env`

**Problem:** Camera not working
- **Fix:** `sudo raspi-config` → Interface Options → Camera → Enable
- **Fix:** Reboot: `sudo reboot`

**Problem:** Files missing
- **Fix:** On Mac: `deploypi` (while on GoPiGo WiFi)

---

For detailed instructions, see: **TEST_ON_GOPIGO.md**

