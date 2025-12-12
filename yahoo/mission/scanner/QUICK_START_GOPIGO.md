# 🚀 Quick Start: Testing Scanner on GoPiGo

## Step 1: Connect to Robot

```bash
# 1. Connect to WiFi: "GoPiGo" (password: robots1234)
# 2. SSH into robot
ssh pi@10.10.10.10
# Password: robots1234
```

## Step 2: Pull Latest Code

```bash
cd ~/yahooRobot
git pull origin main
```

## Step 3: Configure

```bash
# Edit .env file
nano .env
```

Add:
```env
OPENAI_API_KEY=sk-proj-YOUR_KEY_HERE
USE_MOCK_SENSOR=true
USE_PICAM=true
CAMERA_INDEX=0
```

## Step 4: Test

```bash
# Test camera
python3 yahoo/mission/scanner/mac_tests/test_camera_only.py

# Test full pipeline
python3 yahoo/mission/scanner/mac_tests/test_full_pipeline_mock.py
```

## Step 5: Run Scanner

```bash
# Start continuous scanning
python3 yahoo/mission/scanner/scan_paper.py
```

## View Results

```bash
# View database
python3 yahoo/mission/scanner/mac_tests/view_database.py

# View with images
python3 yahoo/mission/scanner/mac_tests/view_scans_with_images.py
```

---

**Full guide:** `yahoo/mission/scanner/DEPLOY_GOPIGO.md`

