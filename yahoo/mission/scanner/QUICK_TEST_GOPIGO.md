# 🚀 Quick Test on GoPiGo

Fastest way to get the scanner running on your GoPiGo robot.

---

## Step 1: Connect to GoPiGo

```bash
# Connect to GoPiGo WiFi first (SSID: GoPiGo, Password: robots1234)
# Then SSH:
ssh pi@10.10.10.10
# Password: robots1234
```

---

## Step 2: Pull Latest Code

```bash
cd ~/yahooRobot
git checkout main
git pull origin main
```

---

## Step 3: Install Dependencies

```bash
cd ~/yahooRobot/yahoo/mission/scanner

# Install required packages
pip3 install opencv-python-headless picamera2 easygopigo3
```

**If you get errors:**
- `picamera2`: Try `sudo apt-get install python3-picamera2`
- `easygopigo3`: Should install with pip3

---

## Step 4: Setup Database

```bash
python3 setup_db.py
```

Should see: `✅ Database created successfully.`

---

## Step 5: Enable Camera (if not already done)

```bash
sudo raspi-config
```

Navigate: **Interface Options** → **Camera** → **Enable** → **Finish** → **Reboot**

After reboot, test camera:
```bash
raspistill -o test.jpg
# Or
libcamera-still -o test.jpg
```

---

## Step 6: Run Scanner

```bash
export USE_GOPIGO=true
python3 scanner.py
```

You should see:
```
============================================================
📄 Simplified Paper Scanner
============================================================
Mode: GoPiGo
Brightness threshold: 180
Scan folder: scans
============================================================

📄 System Ready — Waiting for paper...
```

---

## Testing

1. **Place paper in front of camera**
2. **Watch LEDs:**
   - **Yellow** = Processing (paper detected)
   - **Green** = Success (image saved)
   - **Red** = Error
   - **Off** = Idle (waiting)

3. **Check output:**
   ```
   📄 Paper detected → Processing...
   📸 Saved image: scans/scan_20251212_143000.jpg
   [DB] Logged scans/scan_20251212_143000.jpg @ 2025-12-12 14:30:00
   ✅ Scan stored successfully.
   ```

---

## View Scans

```bash
# View all scans
python3 view_scans.py

# Or check files directly
ls -la scans/
```

---

## Troubleshooting

### Camera Not Working
```bash
# Test camera
raspistill -o test.jpg

# If that fails, enable camera:
sudo raspi-config
# Interface Options → Camera → Enable
sudo reboot
```

### Paper Not Detected
```bash
# Lower the brightness threshold
export BRIGHTNESS_THRESHOLD=150
python3 scanner.py
```

### LEDs Not Working
```bash
# Test GoPiGo connection
python3 -c "from easygopigo3 import EasyGoPiGo3; gpg = EasyGoPiGo3(); print('OK')"

# If that fails, check GoPiGo is connected properly
```

---

## Quick Commands Reference

```bash
# Run scanner
export USE_GOPIGO=true && python3 scanner.py

# View scans
python3 view_scans.py

# Check database
sqlite3 scans.db "SELECT * FROM scans;"

# List images
ls -lh scans/*.jpg
```

---

## Expected Behavior

1. **Start:** LEDs off (idle)
2. **Place paper:** LEDs turn yellow (processing)
3. **Capture:** LEDs turn green for 1.3 seconds
4. **Back to idle:** LEDs off, ready for next paper

---

That's it! The scanner is now running on your GoPiGo! 🎉


