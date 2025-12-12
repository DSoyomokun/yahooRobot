# 📄 Simplified Paper Scanner

Ultra-simple paper scanning system that detects paper and saves images.

## Features

- ✅ **Simple brightness-based paper detection**
- ✅ **Works on GoPiGo and Mac/Windows**
- ✅ **LED feedback on GoPiGo** (idle, processing, success, error)
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

**On Mac/Windows:**
```bash
python3 scanner.py
```

**On GoPiGo:**
```bash
# Set environment variable
export USE_GOPIGO=true
python3 scanner.py
```

Or create `.env` file:
```env
USE_GOPIGO=true
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
- **Test with preview** (Mac/Windows shows camera feed)

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

## Mac/Windows Testing

1. **Install OpenCV:**
   ```bash
   pip3 install opencv-python
   ```

2. **Run scanner:**
   ```bash
   python3 scanner.py
   ```

3. **Preview window shows camera feed**
4. **Press 'q' to quit**

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

