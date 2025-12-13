# 🚀 GoPiGo Scanner Setup & Testing

Quick guide to deploy and test the simplified scanner on your GoPiGo robot.

---

## 📡 Step 1: Connect to GoPiGo

### Connect to Robot WiFi

1. **Turn on the GoPiGo robot**
2. **On your laptop, connect to WiFi:**
   - SSID: `GoPiGo`
   - Password: `robots1234`
3. **Your laptop will disconnect from internet** (this is normal)

### SSH into the Robot

```bash
ssh pi@10.10.10.10
# Password: robots1234
```

---

## 📥 Step 2: Transfer Code to GoPiGo

### Option A: Git Pull (Recommended)

```bash
# On GoPiGo (via SSH)`
git checkout main
git pull origin main
```

### Option B: Manual Transfer (if git not synced)

```bash
# On your Mac (in project directory)
scp -r yahoo/mission/scanner/* pi@10.10.10.10:~/yahooRobot/yahoo/mission/scanner/
```

---

## 🔧 Step 3: Install Dependencies

```bash
# On GoPiGo (via SSH)
cd ~/yahooRobot

# Install Python packages
pip3 install opencv-python-headless  # For camera and image processing
pip3 install picamera2                # Preferred for CSI camera (auto-detected)
pip3 install easygopigo3              # For GoPiGo LEDs (Linux/Raspberry Pi only)
pip3 install python-dotenv            # For .env file support (optional)
```

**⚠️ Important:** 
- `picamera2` and `easygopigo3` are **Linux/Raspberry Pi only** and cannot be installed on Mac/Windows
- Scanner automatically uses `picamera2` for CSI camera if available, otherwise falls back to OpenCV VideoCapture
- Only install these packages on the GoPiGo robot!

---

## ⚙️ Step 4: Setup Database

```bash
# On GoPiGo
cd ~/yahooRobot/yahoo/mission/scanner
python3 setup_db.py
```

You should see: `✅ Database created successfully.`

---

## 📷 Step 5: Enable Camera

```bash
# On GoPiGo
sudo raspi-config
```

Navigate to:
- **Interface Options** → **Camera** → **Enable**
- Reboot: `sudo reboot`

After reboot, test camera:
```bash
raspistill -o test.jpg
# Or
libcamera-still -o test.jpg
```

---

## 🎯 Step 6: Verify Scanner Configuration

The scanner automatically uses `CSI_CAMERA` from `yahoo/config/cameras.py`:
- Camera: `/dev/video0` (CSI Pi Camera)
- Resolution: 1700x2550 (optimized for scanning)

**No configuration needed!** The scanner is ready to use.

Optional: Adjust camera resolution in `yahoo/config/cameras.py` if needed.

---

## 🚀 Step 7: Run Scanner

```bash
# On GoPiGo
cd ~/yahooRobot/yahoo/mission/scanner
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

## 🧪 Testing

1. **Place paper in front of camera**
2. **Watch LEDs:**
   - **Idle**: LEDs off
   - **Processing**: Yellow (when paper detected)
   - **Success**: Green (1.3 seconds)
   - **Error**: Red (if something fails)

3. **Check output:**
   ```
   📄 Paper detected → Processing...
   📸 Saved image: scans/scan_20251212_143000.jpg
   [DB] Logged scans/scan_20251212_143000.jpg @ 2025-12-12 14:30:00
   ✅ Scan stored successfully.
   ```

---

## 👀 View Scans

```bash
# On GoPiGo
cd ~/yahooRobot/yahoo/mission/scanner
python3 view_scans.py
```

Or transfer images to your Mac:
```bash
# On your Mac
scp pi@10.10.10.10:~/yahooRobot/yahoo/mission/scanner/scans/*.jpg ~/Desktop/scans/
```

---

## 🔧 Troubleshooting

### Camera Not Working

**Problem:** "Camera failure" or "Failed to open camera"

**Solutions:**
- Check camera is connected to CSI port
- Enable camera: `sudo raspi-config` → Interface Options → Camera
- Try: `raspistill -o test.jpg` to test camera
- Check permissions: `sudo usermod -a -G video pi` (then logout/login)

### Paper Not Detected

**Problem:** Paper placed but not detected

**Solutions:**
- Lower brightness threshold: `export BRIGHTNESS_THRESHOLD=150`
- Ensure good lighting
- Check camera view (paper should be in center)
- Try different paper (white paper works best)

### LEDs Not Working

**Problem:** LEDs don't change color

**Solutions:**
- Check `easygopigo3` is installed: `pip3 install easygopigo3`
- Verify GoPiGo is connected: `python3 -c "from easygopigo3 import EasyGoPiGo3; gpg = EasyGoPiGo3(); print('OK')"`
- Check `USE_GOPIGO=true` is set

### Import Errors

**Problem:** "ModuleNotFoundError: No module named 'cv2'"

**Solutions:**
```bash
pip3 install opencv-python-headless
```

**Problem:** Camera not opening

**Solutions:**
- Check camera is enabled: `sudo raspi-config` → Interface Options → Camera
- Test camera: `libcamera-still -o test.jpg`
- Verify `/dev/video0` exists: `ls -l /dev/video0`

---

## 📊 Quick Test Checklist

- [ ] Connected to GoPiGo WiFi
- [ ] SSH into robot successful
- [ ] Code transferred to robot
- [ ] Dependencies installed
- [ ] Database created (`setup_db.py` run)
- [ ] Camera enabled in `raspi-config`
- [ ] Camera test works (`raspistill -o test.jpg`)
- [ ] `.env` file created (or environment variables set)
- [ ] Scanner runs without errors
- [ ] Paper detection works
- [ ] Images saved to `scans/` folder
- [ ] Database records created
- [ ] LEDs respond correctly

---

## 🎯 Expected Behavior

1. **Start scanner:** LEDs off (idle)
2. **Place paper:** LEDs turn yellow (processing)
3. **Image captured:** LEDs turn green for 1.3 seconds
4. **Back to idle:** LEDs turn off
5. **Repeat:** Ready for next paper

---

## 📝 Notes

- **Offline operation:** No WiFi needed for scanning
- **Brightness threshold:** Adjust based on lighting conditions
- **Scan folder:** Images saved to `scans/` directory
- **Database:** All scans logged to `scans.db`
- **LED feedback:** Visual confirmation of scanner status

---

## 🆘 Need Help?

Check the console output for error messages. Common issues:
- Camera permissions
- Missing dependencies
- Brightness threshold too high/low
- Camera not enabled in raspi-config

