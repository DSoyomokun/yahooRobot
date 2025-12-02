# Robot Scanner Module

Self-contained test paper scanning module for the Yahoo Robot.

## Structure

```
robot_scanner/
├── __init__.py           # Module exports
├── scanner.py            # Main scanner orchestrator
├── bubble_detector.py    # Multiple-choice bubble detection
├── name_reader.py        # Student name extraction (OCR)
├── grader.py            # Test grading system
├── storage.py           # Supabase database storage
├── answer_key.json      # Answer key (optional, can be in project root)
├── tests/               # Test scripts
│   ├── __init__.py
│   ├── test_scanner.py  # Main test script
│   └── debug_scanner.py # Debug visualization script
└── README.md            # This file
```

## Quick Start

### 1. Install Dependencies

```bash
pip3 install -r requirements-scanner.txt
```

### 2. Install Tesseract OCR

**macOS:**
```bash
brew install tesseract
```

**Linux/Raspberry Pi:**
```bash
sudo apt install tesseract-ocr
```

### 3. Create Answer Key

Create `answer_key.json` in project root or `robot_scanner/`:

```json
{
  "num_questions": 10,
  "answers": {
    "1": "A",
    "2": "B",
    "3": "C",
    ...
  }
}
```

### 4. Test the Scanner

**🚀 EASIEST WAY - Use the test runner:**

```bash
# Interactive menu
python3 robot_scanner/run_test.py

# Or use commands directly
python3 robot_scanner/run_test.py camera    # Test with camera
python3 robot_scanner/run_test.py capture   # Quick capture
python3 robot_scanner/run_test.py image     # Test with image
python3 robot_scanner/run_test.py debug     # Debug visualization
python3 robot_scanner/run_test.py db        # View database
python3 robot_scanner/run_test.py all       # Run all tests
```

**Or use shell script (Mac/Linux):**
```bash
./robot_scanner/run_test.sh
```

**Direct test scripts:**
```bash
# Test with camera
python3 robot_scanner/tests/test_mac.py --camera

# Test with saved image
python3 robot_scanner/tests/test_mac.py --image path/to/image.jpg

# Debug visualization
python3 robot_scanner/tests/debug_scanner.py --camera
```

## Usage

### Basic Usage

```python
from robot_scanner import RobotScanner

# Initialize scanner
scanner = RobotScanner(camera_index=0)

# Scan from camera
result = scanner.scan_paper()

# Or scan from image file
import cv2
image = cv2.imread("test_paper.jpg")
result = scanner.scan_paper(image=image)

# Results
print(f"Student: {result['student_name']}")
print(f"Score: {result['score']}/{result['total_questions']}")
print(f"Answers: {result['answers']}")

# Cleanup
scanner.release()
```

### Standalone Camera Capture

```python
from robot_scanner import capture_image

# Capture and save image
image_path = capture_image(camera_index=0, save_path="scan.jpg")
```

## Configuration

### Name Region Coordinates

Edit `name_reader.py` to adjust name box coordinates:
- `name_top`: Top of name box (default: 5% of height)
- `name_bottom`: Bottom of name box (default: 15% of height)
- `name_left`: Left edge (default: 10% of width)
- `name_right`: Right edge (default: 50% of width)

### Bubble Detection

Edit `bubble_detector.py` to adjust detection:
- `min_area`: Minimum bubble size (default: 30)
- `max_area`: Maximum bubble size (default: 8000)
- `fill_threshold`: Fill percentage to consider marked (default: 0.25)

### Database Configuration

Edit `config.py` to choose your database:

**SQLite (Default - No setup required):**
```python
DATABASE_TYPE = "sqlite"
SQLITE_DB_PATH = "robot_scanner/test_results.db"
```

**PostgreSQL:**
```python
DATABASE_TYPE = "postgresql"
POSTGRESQL_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "database": "test_scanner",
    "user": "postgres",
    "password": "your_password"
}
# Install: pip install psycopg2-binary
```

**MySQL:**
```python
DATABASE_TYPE = "mysql"
MYSQL_CONFIG = {
    "host": "localhost",
    "port": 3306,
    "database": "test_scanner",
    "user": "root",
    "password": "your_password"
}
# Install: pip install mysql-connector-python
```

**MongoDB:**
```python
DATABASE_TYPE = "mongodb"
MONGODB_CONFIG = {
    "connection_string": "mongodb://localhost:27017/",
    "database": "test_scanner",
    "collection": "test_results"
}
# Install: pip install pymongo
```

**JSON File (Simple testing):**
```python
DATABASE_TYPE = "json"
JSON_FILE_PATH = "robot_scanner/test_results.json"
```

## Pipeline

1. **Capture Image** - Camera or file
2. **Extract Name** - OCR from fixed coordinates
3. **Detect Bubbles** - Find and group bubbles by question
4. **Extract Answers** - Determine which bubbles are filled
5. **Grade Test** - Compare against answer key
6. **Store Results** - Save to Supabase database

## Output Format

```python
{
    'student_name': 'John Doe',
    'answers': {'1': 'A', '2': 'B', '3': None, ...},
    'score': 8.0,
    'total_questions': 10,
    'correct': 8,
    'incorrect': 1,
    'unanswered': 1,
    'percentage': 80.0,
    'scanned_at': '2025-12-01T20:00:00'
}
```

## Debug Output

Debug scripts save visualization images to:
- `robot_scanner/tests/debug_output/visualization.jpg` - Full detection overlay
- `robot_scanner/tests/debug_output/name_region.jpg` - Extracted name region

