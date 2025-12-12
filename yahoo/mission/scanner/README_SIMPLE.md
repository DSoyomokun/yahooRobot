# 📄 GoPiGo Paper Scanner

Ultra-simple paper scanning system for GoPiGo robot that detects paper and saves images.

## 🚀 Testing on GoPiGo

**For step-by-step GoPiGo testing instructions, see:**
- **[TEST_ON_GOPIGO.md](TEST_ON_GOPIGO.md)** - Complete detailed guide (recommended)
- **[QUICK_TEST_STEPS.md](QUICK_TEST_STEPS.md)** - Quick 5-minute reference

**⚠️ Important:** This scanner is **GoPiGo robot only** - requires Raspberry Pi with camera enabled.

## Features

- ✅ **Simple brightness-based paper detection**
- ✅ **GoPiGo robot only** (Raspberry Pi required)
- ✅ **LED feedback** (idle, processing, success, error)
- ✅ **SQLite database** for scan records
- ✅ **No external dependencies** (no WiFi, no API keys)
- ✅ **Offline operation**

## Quick Start

### 1. Setup Database

```bash
cd yahoo/mission/scanner
python3 setup_db.py
```

### 2. Run Scanner

**On GoPiGo:**
```bash
python3 scanner.py
```

The scanner will automatically detect it's running on GoPiGo and use the robot camera.

Optional: Create `.env` file to adjust brightness threshold:
```env
BRIGHTNESS_THRESHOLD=180
```

### 3. View Scans

```bash
python3 view_scans.py
```

## How It Works

1. **Camera captures frames continuously**
2. **Brightness detection** checks center region of frame
3. **If brightness > threshold** → paper detected
4. **Capture final image** and save to `scans/` folder
5. **Log to database** with timestamp
6. **LED feedback** (on GoPiGo):
   - **Idle**: LEDs off
   - **Processing**: Yellow
   - **Success**: Green (1.3s)
   - **Error**: Red (1.3s)

## Configuration

### Environment Variables

```env
USE_GOPIGO=false              # Set true on GoPiGo robot
BRIGHTNESS_THRESHOLD=180      # Adjust if paper not detected (higher = brighter paper needed)
```

### Brightness Threshold Tuning

- **Paper not detected?** → Lower threshold (try 150-170)
- **False positives?** → Raise threshold (try 190-210)

## File Structure

```
scanner/
├── setup_db.py          # Create database
├── scanner.py           # Main scanner loop
├── view_scans.py        # View stored scans
├── requirements.txt     # Dependencies
├── scans/               # Images stored here
└── scans.db             # Database (created automatically)
```

## Database Schema

```sql
CREATE TABLE scans (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    image_path TEXT NOT NULL,
    timestamp TEXT NOT NULL
);
```

## Troubleshooting

### Camera Not Working
- Check camera permissions
- Try different camera index: `cv2.VideoCapture(1)`
- On GoPiGo: Enable camera in `raspi-config`

### Paper Not Detected
- Adjust `BRIGHTNESS_THRESHOLD` in `.env`
- Ensure good lighting
- Check camera view (paper should be in center)

### Database Errors
- Run `setup_db.py` to create database
- Check file permissions on `scans/` folder

## GoPiGo Setup

1. **Install dependencies:**
   ```bash
   pip3 install picamera2 easygopigo3
   ```

2. **Enable camera:**
   ```bash
   sudo raspi-config
   # Interface Options → Camera → Enable
   ```

3. **Run scanner:**
   ```bash
   export USE_GOPIGO=true
   python3 scanner.py
   ```

## Platform Requirements

**This scanner is GoPiGo robot only** and requires:
- Raspberry Pi (3B+, 4, or 5)
- Raspberry Pi OS
- Camera module enabled
- GoPiGo3 robot hardware

The scanner will exit with an error if not running on GoPiGo.

## Example Output

```
============================================================
📄 Simplified Paper Scanner
============================================================
Mode: Mac/Windows
Brightness threshold: 180
Scan folder: scans
============================================================

📄 System Ready — Waiting for paper...

📄 Paper detected → Processing...
📸 Saved image: scans/scan_20251210_180920.jpg
[DB] Logged scans/scan_20251210_180920.jpg @ 2025-12-10 18:09:20
✅ Scan stored successfully.
```

## Next Steps

This is a minimal working scanner. You can extend it with:
- Image warping/perspective correction
- Name detection (OCR)
- Batch processing
- Web UI for viewing scans

But for now, **keep it simple** and get it working! 🚀

