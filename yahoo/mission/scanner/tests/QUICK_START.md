# Quick Start Guide - Mac Testing

## Prerequisites

1. **Python 3** (use `python3` command on Mac)
2. **Dependencies installed:**
   ```bash
   pip3 install -r requirements-scanner.txt
   ```
3. **Tesseract OCR:**
   ```bash
   brew install tesseract
   ```

## Quick Test Commands

### Option 1: Test with Camera (Recommended)
```bash
python3 robot_scanner/tests/test_mac.py --camera
```
- Place your test paper in front of MacBook camera
- Automatically captures and processes

### Option 2: Quick Capture First
```bash
# Step 1: Capture image
python3 robot_scanner/tests/test_mac.py --capture

# Step 2: Test with captured image
python3 robot_scanner/tests/test_mac.py --image robot_scanner/tests/captured_paper.jpg
```

### Option 3: Test with Existing Image
```bash
python3 robot_scanner/tests/test_mac.py --image path/to/your/image.jpg
```

## Debug Visualization

To see what the scanner detects:
```bash
python3 robot_scanner/tests/debug_scanner.py --camera
```

This will show:
- Green rectangle = Name region
- Magenta rectangles = Detected bubbles

## Troubleshooting

**"command not found: python"**
- Use `python3` instead of `python` on Mac

**Camera not working**
- Check System Settings > Privacy & Security > Camera
- Make sure Terminal/Python has camera permissions

**No bubbles detected**
- Check lighting
- Ensure paper is flat and in focus
- Try adjusting thresholds in `bubble_detector.py`

**Name extraction poor**
- Adjust name region coordinates in `name_reader.py`
- Check `debug_output/name_region.jpg` to see what's being extracted

## Files Created

- `robot_scanner/test_results.db` - SQLite database with results
- `robot_scanner/tests/debug_output/` - Debug visualization images
- `robot_scanner/tests/captured_paper.jpg` - Captured test images

