#!/usr/bin/env python3
"""
Quick script to check database for scanned images
"""
import sqlite3
import os
from pathlib import Path

# Find database (could be in scanner directory or current directory)
db_paths = [
    "yahoo/mission/scanner/scans.db",
    "scans.db",
    Path(__file__).parent / "scans.db"
]

db_path = None
for path in db_paths:
    if os.path.exists(path):
        db_path = path
        break

if not db_path:
    print("❌ Database not found. Tried:")
    for p in db_paths:
        print(f"   - {p}")
    exit(1)

print(f"📊 Checking database: {db_path}\n")

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Get all scans
cursor.execute("SELECT id, image_path, timestamp FROM scans ORDER BY id DESC")
scans = cursor.fetchall()

if not scans:
    print("⚠️  No scans found in database yet")
    print("   Run the scanner and place paper in front of camera")
else:
    print(f"✅ Found {len(scans)} scan(s) in database:\n")
    for scan_id, img_path, timestamp in scans:
        exists = "✅" if os.path.exists(img_path) else "❌"
        size = ""
        if os.path.exists(img_path):
            size = f" ({os.path.getsize(img_path):,} bytes)"
        print(f"  {exists} Scan #{scan_id}: {img_path}{size}")
        print(f"     Time: {timestamp}")

conn.close()
