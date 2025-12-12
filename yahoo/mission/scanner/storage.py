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
        CREATE TABLE IF NOT EXISTS paper_scans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            image_path TEXT,
            student_name TEXT,
            ocr_raw TEXT,
            ocr_confidence REAL,
            processed INTEGER,
            weight_grams REAL
        )
    """)
    
    # Keep old table for backward compatibility (can be removed later)
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
def save_paper_scan(image_path, student_name=None, ocr_raw=None, ocr_confidence=None, weight_grams=None):
    """
    Save a paper scan to the database.
    
    Args:
        image_path: Path to saved image
        student_name: Detected student name (None if not processed)
        ocr_raw: Raw OCR text
        ocr_confidence: OCR confidence score
        weight_grams: Weight detected by sensor
    
    Returns:
        row_id: ID of inserted record
    """
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    processed = 1 if student_name and student_name != "UNKNOWN" else 0

    cur.execute("""
        INSERT INTO paper_scans (
            timestamp, image_path, student_name, ocr_raw, 
            ocr_confidence, processed, weight_grams
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        datetime.now().isoformat(),
        image_path,
        student_name,
        ocr_raw,
        ocr_confidence,
        processed,
        weight_grams
    ))

    row_id = cur.lastrowid
    conn.commit()
    conn.close()
    
    return row_id


def get_unprocessed_scans():
    """
    Get all scans that haven't been processed (no student name).
    Useful for batch processing when WiFi reconnects.
    
    Returns:
        List of scan records
    """
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
        SELECT id, timestamp, image_path 
        FROM paper_scans 
        WHERE processed = 0
        ORDER BY timestamp
    """)

    results = cur.fetchall()
    conn.close()
    
    return results


# Legacy function for backward compatibility
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
        Legacy function - kept for backward compatibility.
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
            json.dumps(answers),
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

