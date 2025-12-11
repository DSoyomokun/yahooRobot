# mission/scanner/storage.py
"""
SQLite storage subsystem for scanned test results.

Stores:
- student name (or UNKNOWN)
- OCR details
- detected answers
- correctness
- score + percentage
- timestamps
- file paths (raw image, warped sheet, name crop)
"""

import sqlite3
import os
import json
from datetime import datetime

DB_PATH = "scans/results.db"


# ----------------------------------------------------------
# Ensure directories exist
# ----------------------------------------------------------
def ensure_dirs():
    os.makedirs("scans/raw", exist_ok=True)
    os.makedirs("scans/warped", exist_ok=True)
    os.makedirs("scans/name_crops", exist_ok=True)


# ----------------------------------------------------------
# Initialize SQLite DB with needed tables
# ----------------------------------------------------------
def init_db():
    ensure_dirs()
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS test_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            student_name TEXT,
            ocr_raw TEXT,
            ocr_confidence REAL,
            ocr_mode TEXT,
            needs_review INTEGER,
            answers_json TEXT,
            correctness_json TEXT,
            score INTEGER,
            percentage REAL,
            raw_image_path TEXT,
            warped_image_path TEXT,
            name_crop_path TEXT
        )
    """)

    conn.commit()
    conn.close()


# ----------------------------------------------------------
# Save raw, warped images to disk
# ----------------------------------------------------------
def save_image(img, folder, prefix):
    """
    Saves an image to disk and returns the file path.
    """
    ensure_dirs()
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = f"scans/{folder}/{prefix}_{ts}.png"
    import cv2
    cv2.imwrite(path, img)
    return path


# ----------------------------------------------------------
# Insert a full test result into DB
# ----------------------------------------------------------
def store_result(
    student_name,
    ocr_raw,
    ocr_confidence,
    ocr_mode,
    needs_review,
    answers,
    correctness,
    score,
    percentage,
    raw_image_path,
    warped_image_path,
    name_crop_path
):
    """
    Insert one completed scan result into DB.
    """

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO test_results (
            timestamp, student_name, ocr_raw, ocr_confidence, ocr_mode,
            needs_review, answers_json, correctness_json, score, percentage,
            raw_image_path, warped_image_path, name_crop_path
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        datetime.now().isoformat(),
        student_name,
        ocr_raw,
        ocr_confidence,
        ocr_mode,
        1 if needs_review else 0,
        json.dumps(answers),          # store dict as JSON
        json.dumps(correctness),
        score,
        percentage,
        raw_image_path,
        warped_image_path,
        name_crop_path
    ))

    conn.commit()
    conn.close()


# ----------------------------------------------------------
# Update a row later after OCR refinement
# ----------------------------------------------------------
def update_name_result(row_id, student_name, confidence, raw_ocr):
    """
    Called by a later script when internet becomes available
    to re-OCR name_crops and update the DB.
    """
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
        UPDATE test_results
        SET student_name = ?, ocr_confidence = ?, ocr_raw = ?, needs_review = 0
        WHERE id = ?
    """, (
        student_name,
        confidence,
        raw_ocr,
        row_id
    ))

    conn.commit()
    conn.close()

