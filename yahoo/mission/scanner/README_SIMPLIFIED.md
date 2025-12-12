# Simplified Paper Scanner

Simple paper scanning system that detects paper weight, captures image, and identifies student name.

## How It Works

1. **Weight Detection**: HX711 sensor detects when paper is placed (or mock sensor for testing)
2. **Camera Capture**: Automatically captures image when weight detected
3. **Image Storage**: Saves image to database
4. **Name Detection** (if WiFi): Uses OpenAI Vision API to identify student name
5. **Association**: Links image with student in database

## Quick Start

### Testing Without Hardware (Mock Sensor)

```bash
# Test the full pipeline with mock weight sensor
python3 yahoo/mission/scanner/mac_tests/test_full_pipeline_mock.py

# Press 'P' + Enter to simulate paper detection
```

### Run Main Scanner

```bash
# Start the scanner (uses mock sensor by default)
python3 -m yahoo.mission.scanner.scan_paper
```

### Test Individual Components

```bash
# Test camera only
python3 yahoo/mission/scanner/mac_tests/test_camera_only.py

# Test mock weight sensor
python3 yahoo/mission/scanner/mac_tests/test_mock_weight_sensor.py
```

## Configuration

Set in `.env` file:

```bash
# Weight Sensor
WEIGHT_SENSOR_ENABLED=false  # Set to true when HX711 is connected
USE_MOCK_SENSOR=true         # Use mock for testing
WEIGHT_THRESHOLD_GRAMS=1.0   # Minimum weight to trigger

# Camera
CAMERA_INDEX=0               # USB webcam index
USE_PICAM=false              # Set true for Raspberry Pi camera

# OpenAI (for name detection)
OPENAI_API_KEY=sk-proj-...
```

## Database

Images are stored in `scans/results.db` in the `paper_scans` table:

- `image_path`: Path to saved image
- `student_name`: Detected name (NULL if offline)
- `ocr_raw`: Raw OCR text
- `ocr_confidence`: Confidence score
- `processed`: 1 if name detected, 0 if pending
- `weight_grams`: Weight detected by sensor
- `timestamp`: When scan was taken

## Offline Mode

When WiFi is not available:
- Image is still saved to disk
- Image is stored in database with `student_name = NULL`
- `processed = 0` marks it for later processing
- When WiFi reconnects, can batch process unprocessed scans

## Files

**Core Modules:**
- `scan_paper.py` - Main entry point
- `simple_pipeline.py` - Processing pipeline
- `weight_sensor_mock.py` - Weight sensor (mock & HX711)
- `camera_capture.py` - Camera wrapper
- `image_warp.py` - Image warping/preprocessing
- `name_detect.py` - Student name detection (OpenAI Vision API)
- `storage.py` - Database operations

**Test Files:**
- `mac_tests/test_full_pipeline_mock.py` - Full pipeline test
- `mac_tests/test_camera_only.py` - Camera test
- `mac_tests/test_mock_weight_sensor.py` - Weight sensor test


