# 🚀 Testing Scanner on GoPiGo - Step by Step

Complete guide to test the scanner using the GoPiGo camera (not Mac webcam).

---

## 📋 Prerequisites Checklist

Before starting, make sure you have:
- [ ] GoPiGo robot powered on
- [ ] GoPiGo WiFi network available
- [ ] Camera module connected to GoPiGo
- [ ] Code synced to GoPiGo

---

## 🔧 Step 1: Connect to GoPiGo WiFi

**On your Mac:**

1. Open WiFi settings
2. Connect to: **`GoPiGo`**
3. Password: **`robots1234`**
4. Wait for connection (you'll lose internet - this is normal)

---

## 📡 Step 2: SSH into GoPiGo

**On your Mac terminal:**

```bash
robopi
# Or manually:
ssh pi@10.10.10.10
# Password: robots1234
```

You should see:
```
pi@GoPiGo:~$
```

---

## 📁 Step 3: Navigate to Scanner Directory

**On GoPiGo (via SSH):**

```bash
cd ~/yahooRobot/yahoo/mission/scanner
pwd
# Should show: /home/pi/yahooRobot/yahoo/mission/scanner
```

---

## ✅ Step 4: Verify Files Are Present

**On GoPiGo:**

```bash
ls -la *.py
```

You should see:
- `scanner.py`
- `setup_db.py`
- `view_scans.py`
- `verify_scanner.py`

If files are missing, see **Troubleshooting** section below.

---

## 💾 Step 5: Setup Database

**On GoPiGo:**

```bash
python3 setup_db.py
```

**Expected output:**
```
✅ Database created successfully.
```

If you get an error, the file might not exist. See **Troubleshooting** below.

---

## ⚙️ Step 6: Configure for GoPiGo Camera

**On GoPiGo:**

```bash
# Create .env file with GoPiGo settings
echo "USE_GOPIGO=true" > .env
echo "BRIGHTNESS_THRESHOLD=180" >> .env

# Verify it was created correctly
cat .env
```

**Expected output:**
```
USE_GOPIGO=true
BRIGHTNESS_THRESHOLD=180
```

**⚠️ CRITICAL:** This tells the scanner to use the GoPiGo camera, not Mac webcam!

---

## 📷 Step 7: Verify Camera is Enabled

**On GoPiGo:**

```bash
# Check if camera is enabled
sudo raspi-config
```

Navigate:
- **Interface Options** → **Camera** → **Enable** → **Finish**

If camera was just enabled, reboot:
```bash
sudo reboot
```

After reboot, SSH back in and test camera:
```bash
robopi
cd ~/yahooRobot/yahoo/mission/scanner
libcamera-still -o test_camera.jpg
ls -lh test_camera.jpg
```

If `test_camera.jpg` exists, camera is working! ✅

---

## 📦 Step 8: Install Dependencies (if needed)

**On GoPiGo:**

```bash
# Install required packages
pip3 install opencv-python-headless picamera2 easygopigo3 python-dotenv
```

**Note:** These packages are Linux/Raspberry Pi only and won't work on Mac.

---

## 🚀 Step 9: Run the Scanner

**On GoPiGo:**

```bash
python3 scanner.py
```

**Expected output:**
```
============================================================
📄 Simplified Paper Scanner
============================================================
Mode: GoPiGo
Brightness threshold: 180
Scan folder: scans
============================================================

📄 System Ready — Waiting for paper...

Press 'q' to quit (Mac/Windows only)
```

**✅ Key indicator:** It should say **"Mode: GoPiGo"** (not "Mode: Mac/Windows")

If it says "Mode: Mac/Windows", check your `.env` file:
```bash
cat .env
# Should show: USE_GOPIGO=true
```

---

## 🧪 Step 10: Test Paper Detection

**Physical setup:**
1. Place a **white piece of paper** in front of the GoPiGo camera
2. Ensure good lighting
3. Paper should be in the center of the camera view

**What to watch for:**

1. **LEDs on GoPiGo:**
   - **Off** = Idle (waiting)
   - **Yellow** = Processing (paper detected!)
   - **Green** = Success (image saved!)
   - **Red** = Error

2. **Console output:**
   ```
   📄 Paper detected → Processing...
   📸 Saved image: scans/scan_20251212_150000.jpg
   [DB] Logged scans/scan_20251212_150000.jpg @ 2025-12-12 15:00:00
   ✅ Scan stored successfully.
   ```

---

## ✅ Step 11: Verify It Worked

**Keep scanner running, open a NEW terminal on your Mac:**

```bash
# Connect to GoPiGo WiFi (if not already)
robopi

# Navigate to scanner
cd ~/yahooRobot/yahoo/mission/scanner

# Run verification
python3 verify_scanner.py
```

**Expected output:**
```
============================================================
🔍 SCANNER VERIFICATION
============================================================

1️⃣  Checking database...
   ✅ Database found: scans.db
   📊 Total scans in DB: 1
   📸 Latest scan: #1
      Image: scans/scan_20251212_150000.jpg
      Time: 2025-12-12 15:00:00
      ✅ Image file exists (245,678 bytes)

2️⃣  Checking scan folder...
   ✅ Folder exists: scans
   📸 Image files found: 1

============================================================
✅ SCANNER IS WORKING!
   Found 1 scan(s) in database
============================================================
```

---

## 👀 Step 12: View the Scanned Images

**On GoPiGo (or transfer to Mac):**

**Option A: View on GoPiGo (if X11 forwarding):**
```bash
# SSH with X11 forwarding
robopi_x  # or: ssh -Y pi@10.10.10.10

cd ~/yahooRobot/yahoo/mission/scanner
python3 view_scans.py
```

**Option B: Transfer to Mac:**
```bash
# On your Mac (connected to GoPiGo WiFi)
scp pi@10.10.10.10:~/yahooRobot/yahoo/mission/scanner/scans/*.jpg ~/Desktop/gopigo_scans/

# Then view on Mac
open ~/Desktop/gopigo_scans/
```

**Option C: List files on GoPiGo:**
```bash
# On GoPiGo
cd ~/yahooRobot/yahoo/mission/scanner
ls -lh scans/
```

---

## 🔧 Troubleshooting

### Problem: Files not found on GoPiGo

**Solution:**
```bash
# On your Mac (connected to GoPiGo WiFi)
deploypi

# Then on GoPiGo, verify:
cd ~/yahooRobot/yahoo/mission/scanner
ls -la *.py
```

### Problem: Scanner says "Mode: Mac/Windows" instead of "Mode: GoPiGo"

**Solution:**
```bash
# On GoPiGo
cd ~/yahooRobot/yahoo/mission/scanner
cat .env
# Should show: USE_GOPIGO=true

# If not, recreate it:
echo "USE_GOPIGO=true" > .env
echo "BRIGHTNESS_THRESHOLD=180" >> .env

# Verify:
cat .env
```

### Problem: Camera not working

**Solution:**
```bash
# Enable camera
sudo raspi-config
# Interface Options → Camera → Enable

# Reboot
sudo reboot

# Test camera
libcamera-still -o test.jpg
ls -lh test.jpg
```

### Problem: Paper not detected

**Solutions:**
1. **Lower brightness threshold:**
   ```bash
   echo "BRIGHTNESS_THRESHOLD=150" > .env
   echo "USE_GOPIGO=true" >> .env
   ```

2. **Improve lighting** - ensure paper is well-lit

3. **Check camera view** - paper should be centered

4. **Try different paper** - white paper works best

### Problem: Import errors (picamera2, easygopigo3)

**Solution:**
```bash
# Install packages
pip3 install picamera2 easygopigo3

# Or if that fails:
sudo apt-get update
sudo apt-get install python3-picamera2
```

### Problem: LEDs not working

**Solution:**
```bash
# Verify easygopigo3 is installed
python3 -c "from easygopigo3 import EasyGoPiGo3; gpg = EasyGoPiGo3(); print('OK')"

# Check USE_GOPIGO is set
cat .env | grep USE_GOPIGO
```

---

## 📊 Success Checklist

After testing, verify:
- [ ] Scanner shows "Mode: GoPiGo" (not Mac/Windows)
- [ ] LEDs respond (yellow → green when paper detected)
- [ ] Console shows "✅ Scan stored successfully"
- [ ] `verify_scanner.py` shows scans in database
- [ ] Image files exist in `scans/` folder
- [ ] Images are from GoPiGo camera (not Mac webcam)

---

## 🎯 Quick Reference Commands

**On GoPiGo:**
```bash
cd ~/yahooRobot/yahoo/mission/scanner

# Setup
python3 setup_db.py
echo "USE_GOPIGO=true" > .env
echo "BRIGHTNESS_THRESHOLD=180" >> .env

# Run scanner
python3 scanner.py

# Verify (in another terminal)
python3 verify_scanner.py

# View scans
python3 view_scans.py
```

---

## 📝 Notes

- **GoPiGo mode:** Uses `picamera2` for camera, `easygopigo3` for LEDs
- **Mac mode:** Uses OpenCV webcam, no LEDs
- **Database:** All scans stored in `scans.db`
- **Images:** Saved to `scans/` folder
- **Offline:** Works without internet connection

---

## 🆘 Still Having Issues?

1. Check console output for error messages
2. Verify camera is enabled: `sudo raspi-config`
3. Test camera directly: `libcamera-still -o test.jpg`
4. Check `.env` file: `cat .env`
5. Verify files exist: `ls -la *.py`

---

**Last updated:** 2025-12-12

