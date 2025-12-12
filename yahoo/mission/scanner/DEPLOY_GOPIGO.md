# 🚀 Deploying Scanner Feature to GoPiGo

This guide explains how to deploy and test the paper scanning feature on your GoPiGo robot.

---

## 📡 Step 1: Connect to GoPiGo

### Connect to Robot WiFi

1. **Turn on the GoPiGo robot**
2. **On your laptop, connect to WiFi:**
   - SSID: `GoPiGo`
   - Password: `robots1234`
3. **Your laptop will disconnect from internet** (this is normal - GoPiGo creates its own network)

### SSH into the Robot

**Quick method (if you have aliases set up):**
```bash
robopi        # Normal SSH
robopi_x      # SSH with X11 forwarding (for GUI apps)
```

**Manual method:**
```bash
ssh pi@10.10.10.10
# Password: robots1234
```

**With X11 forwarding (for camera preview):**
```bash
ssh -Y pi@10.10.10.10
```

---

## 📥 Step 2: Pull Latest Code

Once connected via SSH:

```bash
# Navigate to project directory
cd ~/yahooRobot

# Pull latest changes from main branch
git checkout main
git pull origin main

# Verify scanner files are present
ls -la yahoo/mission/scanner/
```

You should see:
- `simple_pipeline.py`
- `scan_paper.py`
- `camera_capture.py`
- `weight_sensor_mock.py`
- `image_warp.py`
- `name_detect.py`
- `storage.py`
- `config.py`

---

## 🔧 Step 3: Install Dependencies

```bash
# Install Python packages
pip3 install opencv-python-headless  # Use headless version on Pi
pip3 install python-dotenv
pip3 install requests

# If using real HX711 weight sensor (when hardware arrives):
# pip3 install hx711
```

---

## ⚙️ Step 4: Configure Environment

```bash
# Create .env file if it doesn't exist
cd ~/yahooRobot
nano .env
```

Add these settings:

```env
# OpenAI API Key (for name detection when WiFi connected)
OPENAI_API_KEY=sk-proj-YOUR_KEY_HERE

# Weight Sensor Configuration
WEIGHT_SENSOR_ENABLED=false
USE_MOCK_SENSOR=true
WEIGHT_THRESHOLD_GRAMS=1.0
HX711_DT_PIN=5
HX711_SCK_PIN=6

# Camera Configuration
CAMERA_INDEX=0
USE_PICAM=true
```

**Note:** 
- Set `USE_PICAM=true` to use Raspberry Pi Camera Module
- Set `USE_MOCK_SENSOR=true` until HX711 hardware is connected
- Set `WEIGHT_SENSOR_ENABLED=true` when HX711 is ready

---

## 🧪 Step 5: Test Components

### Test 1: Camera Only

```bash
cd ~/yahooRobot
python3 yahoo/mission/scanner/mac_tests/test_camera_only.py
```

**Expected:** Camera should capture an image and save it to `scans/test/camera_test.png`

### Test 2: Mock Weight Sensor

```bash
python3 yahoo/mission/scanner/mac_tests/test_mock_weight_sensor.py
```

**Expected:** Press 'P' + Enter to simulate paper detection

### Test 3: Full Pipeline (Mock)

```bash
python3 yahoo/mission/scanner/mac_tests/test_full_pipeline_mock.py
```

**Expected:** 
- Press 'P' + Enter to trigger
- Camera captures image
- Image is processed and stored in database
- Student name detected (if WiFi connected)

---

## 🚀 Step 6: Run Full Scanner System

### Start the Continuous Scanner Loop

```bash
cd ~/yahooRobot
python3 yahoo/mission/scanner/scan_paper.py
```

**What happens:**
1. System initializes weight sensor (mock or real)
2. System initializes camera (PiCam or USB)
3. Waits for paper detection (weight threshold or manual trigger)
4. Captures image when paper detected
5. Processes image (warping, name detection)
6. Stores result in database
7. Repeats

**To stop:** Press `Ctrl+C`

---

## 📊 Step 7: View Results

### View Database

```bash
# List all scans
python3 yahoo/mission/scanner/mac_tests/view_database.py

# View statistics
python3 yahoo/mission/scanner/mac_tests/view_database.py --stats

# View unprocessed scans
python3 yahoo/mission/scanner/mac_tests/view_database.py --unprocessed
```

### View Images

```bash
# List scans and view images
python3 yahoo/mission/scanner/mac_tests/view_scans_with_images.py

# View specific scan
python3 yahoo/mission/scanner/mac_tests/view_scans_with_images.py --id 1
```

### Web UI (if Flask installed)

```bash
# Start web server
python3 yahoo/mission/scanner/web_ui/app.py

# On your laptop, open browser:
# http://10.10.10.10:5000
```

---

## 🔌 Step 8: Connect Real Hardware (When Ready)

### HX711 Weight Sensor

1. **Connect HX711 to Raspberry Pi GPIO:**
   - DT pin → GPIO 5
   - SCK pin → GPIO 6
   - VCC → 5V
   - GND → GND

2. **Update .env:**
   ```env
   WEIGHT_SENSOR_ENABLED=true
   USE_MOCK_SENSOR=false
   ```

3. **Install HX711 library:**
   ```bash
   pip3 install hx711
   ```

4. **Test:**
   ```bash
   python3 yahoo/mission/scanner/mac_tests/test_mock_weight_sensor.py
   # Should now read actual weight values
   ```

### Raspberry Pi Camera Module

1. **Connect PiCam to CSI port**
2. **Enable camera in raspi-config:**
   ```bash
   sudo raspi-config
   # Navigate to: Interface Options → Camera → Enable
   # Reboot: sudo reboot
   ```

3. **Test:**
   ```bash
   # Test camera
   raspistill -o test.jpg
   
   # Or use our test script
   python3 yahoo/mission/scanner/mac_tests/test_camera_only.py
   ```

---

## 🐛 Troubleshooting

### Camera Issues

**Problem:** Black screen or "Failed to initialize camera"

**Solutions:**
- Check camera is connected properly
- Enable camera: `sudo raspi-config` → Interface Options → Camera
- Try different camera index: `CAMERA_INDEX=1` in `.env`
- Check permissions: `sudo usermod -a -G video pi`

### Weight Sensor Issues

**Problem:** Sensor not detecting paper

**Solutions:**
- Check GPIO connections
- Calibrate sensor (may need to adjust threshold)
- Use mock sensor for testing: `USE_MOCK_SENSOR=true`

### Name Detection Not Working

**Problem:** Student name always "UNKNOWN"

**Solutions:**
- Check WiFi connection: `ping google.com`
- Verify OpenAI API key in `.env`
- Check image quality (may need better lighting)
- View name crop: `scans/name_crops/name_*.png`

### Database Issues

**Problem:** "Database not found" or permission errors

**Solutions:**
- Ensure `scans/` directory exists: `mkdir -p scans/raw scans/warped scans/name_crops`
- Check write permissions: `chmod 755 scans/`

---

## 📝 Quick Reference Commands

```bash
# Connect to robot
ssh pi@10.10.10.10

# Navigate to project
cd ~/yahooRobot

# Pull latest code
git pull origin main

# Run scanner
python3 yahoo/mission/scanner/scan_paper.py

# View database
python3 yahoo/mission/scanner/mac_tests/view_database.py

# View images
python3 yahoo/mission/scanner/mac_tests/view_scans_with_images.py --id 1

# Check camera
python3 yahoo/mission/scanner/mac_tests/test_camera_only.py
```

---

## 🎯 Next Steps

1. ✅ **Test with mock sensor** - Verify pipeline works
2. ✅ **Connect PiCam** - Test camera capture
3. ✅ **Connect HX711** - Test weight detection
4. ✅ **Test full system** - Paper → Weight → Camera → Process → Store
5. ✅ **Batch process** - Process unprocessed scans when WiFi reconnects

---

**Happy Scanning! 📄🤖**

