---
name: Improve Scanner with Complete Pipeline and Database Integration
overview: ""
todos:
  - id: 5a36b54c-f1a1-45a5-89f6-e9e069a72367
    content: Create class_roster.py with all 32 students from provided list
    status: pending
  - id: 163d4738-2d15-4b29-adb2-332b73a5a1f4
    content: Create name_matcher.py with fuzzy matching logic
    status: pending
  - id: c95c0941-12f8-4a90-b2c9-1524d15977ac
    content: Fix name_reader.py to only extract name field (not entire page)
    status: pending
  - id: 39488588-db37-4c41-9cd7-e5e93cbf0b02
    content: Improve bubble_detector.py to detect all 10 questions accurately
    status: pending
  - id: f2578fff-010a-479f-9d3d-90eeba4467bc
    content: Update storage.py to support class table and name matching integration
    status: pending
  - id: db220cf2-9807-48ea-91e7-e5c63ce6c933
    content: Update scanner.py to implement 4-stage flow (Input → Process → Match → Output)
    status: pending
  - id: 2408674e-8d0f-472f-8433-9cf10f5dc65a
    content: Test complete pipeline end-to-end with real test paper
    status: pending
---

# Improve Scanner with Complete Pipeline and Database Integration

## Overview

Implement the complete 4-stage scanner pipeline with improved accuracy and create a student database for name matching. The flow: Capture → Process (OCR + Bubble Detection) → Match (Name to Database) → Output (Auto-grade + Save).

## Implementation Steps

### 1. Create Student Database Module

**File**: `yahoo/mission/scanner/class_roster.py` (new)

- Create `ClassRoster` class with the provided student list
- Parse names: "Abera, Nahom" → full_name="Nahom Abera", last_name="Abera", first_name="Nahom"
- Include role field (Student, Instructor, TA Designer)
- Function: `populate_database(storage)` to insert all 32 students into the class table

### 2. Create Name Matcher Module

**File**: `yahoo/mission/scanner/name_matcher.py` (new)

- Implement fuzzy string matching using `difflib` or `fuzzywuzzy`
- `normalize_name(name)`: Clean OCR text (remove special chars, normalize whitespace)
- `match_student_name(ocr_name, storage)`: Find best match in database
- Return student_id if match confidence > threshold (e.g., 70%)
- `get_suggestions(ocr_name, storage, limit=3)`: Return top matches for manual review

### 3. Improve Name Reader Accuracy

**File**: `yahoo/mission/scanner/name_reader.py`

- Fix name region extraction to ONLY capture the name field (not entire page)
- Current issue: Reading whole page instead of just name box
- Adjust coordinates: More precise cropping (e.g., 10-18% from top, 25-75% from left)
- Improve preprocessing: Better contrast, denoising, thresholding
- Add validation: Filter out OCR results that are too long (likely reading wrong region)

### 4. Improve Bubble Detection Accuracy

**File**: `yahoo/mission/scanner/bubble_detector.py`

- Current issue: Only detecting 1 answer out of 10
- Improve preprocessing: Better thresholding, noise reduction
- Adjust detection parameters:
  - `min_area`, `max_area`: Fine-tune for actual bubble sizes
  - `fill_threshold`: Lower if bubbles aren't fully filled
  - `circularity_threshold`: Adjust for imperfect circles
- Improve grouping logic: Better row/column detection
- Add validation: Ensure all 10 questions are detected

### 5. Update Storage Module

**File**: `yahoo/mission/scanner/storage.py`

- Ensure `class` table exists with columns: id, full_name, last_name, first_name, role
- Update `test_results` table to include `student_id` (foreign key)
- Add `needs_review` flag for unmatched names
- `save_result()`: Integrate name matching before saving
- If match found: Link to student_id
- If no match: Set needs_review=True, log suggestions

### 6. Update Scanner Pipeline

**File**: `yahoo/mission/scanner/scanner.py`

- Implement the 4-stage flow:

  1. **Input Stage**: `capture_image()` or accept image input
  2. **Processing Stage**: 

     - `extract_name()` → OCR
     - `extract_answers()` → Bubble detection

  1. **Matching Stage**: 

     - `match_name_to_database()` → Fuzzy match OCR name to student roster

  1. **Output Stage**: 

     - `grade()` → Auto-grade answers
     - `save_result()` → Save with student_id link
- Add logging at each stage for debugging
- Return structured result with all stage outputs

### 7. Create Database Initialization Script

**File**: `yahoo/mission/scanner/init_database.py` (new, optional)

- Script to initialize database and populate class roster
- Can be run once to set up the database
- Or auto-populate on first scanner initialization

## Technical Improvements

### Name Detection Improvements

- Precise ROI: Only extract the name field region (avoid header/instructions)
- OCR filtering: Remove results > 50 characters (likely reading wrong region)
- Multiple OCR attempts: Try different preprocessing settings
- Confidence threshold: Only accept results with reasonable confidence

### Bubble Detection Improvements

- Adaptive thresholding: Adjust based on image lighting
- Better contour filtering: More accurate circularity detection
- Improved grouping: Better row detection (handle slight misalignment)
- Fill calculation: More robust comparison to paper background
- Validation: Ensure exactly 10 questions detected

### Database Schema

```sql
CREATE TABLE class (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name TEXT NOT NULL,
    last_name TEXT,
    first_name TEXT,
    role TEXT,
    UNIQUE(full_name)
);

CREATE TABLE test_results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER,
    student_name TEXT,
    answers TEXT,
    score REAL,
    percentage REAL,
    scanned_at TIMESTAMP,
    needs_review BOOLEAN DEFAULT 0,
    FOREIGN KEY (student_id) REFERENCES class(id)
);
```

## Files to Create/Modify

1. `yahoo/mission/scanner/class_roster.py` (new)
2. `yahoo/mission/scanner/name_matcher.py` (new)
3. `yahoo/mission/scanner/name_reader.py` (improve)
4. `yahoo/mission/scanner/bubble_detector.py` (improve)
5. `yahoo/mission/scanner/storage.py` (update for class table)
6. `yahoo/mission/scanner/scanner.py` (implement 4-stage flow)
7. `yahoo/mission/scanner/init_database.py` (new, optional)

## Testing Strategy

1. Test name extraction with precise ROI
2. Test bubble detection with all 10 questions
3. Test name matching with various OCR outputs
4. Test end-to-end pipeline with real test paper
5. Verify database entries are correctly linked