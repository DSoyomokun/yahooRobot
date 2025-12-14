#!/usr/bin/env python3
"""
Quick script to check scanner database and view scans
Run this on GoPiGo: python3 check_db.py
"""
import sqlite3
import os
from pathlib import Path

# Find database and scans directory (relative to script location)
script_dir = Path(__file__).parent.resolve()
db_path = script_dir / "scans.db"
scans_dir = script_dir / "scans"

print("=" * 70)
print("📊 SCANNER DATABASE CHECK")
print("=" * 70)
print()

if not db_path.exists():
    print(f"❌ Database not found: {db_path}")
    print(f"   Run the scanner first to create the database")
    exit(1)

conn = sqlite3.connect(str(db_path))
cursor = conn.cursor()

# Get all scans
cursor.execute("SELECT id, image_path, timestamp FROM scans ORDER BY id DESC")
scans = cursor.fetchall()

print(f"📁 Database: {db_path}")
print(f"📸 Total scans in database: {len(scans)}\n")

if scans:
    print("Recent scans:")
    print("-" * 70)
    for scan_id, img_path, timestamp in scans:
        # Try to find the file
        file_paths = [
            script_dir / img_path,  # Relative to scanner dir
            scans_dir / Path(img_path).name,  # Just filename in scans dir
            Path(img_path),  # Absolute path
        ]
        
        found_path = None
        for path in file_paths:
            if path.exists():
                found_path = path
                size = path.stat().st_size
                break
        
        if found_path:
            print(f"✅ Scan #{scan_id}: {found_path.name}")
            print(f"   Path: {img_path}")
            print(f"   File: {found_path} ({size:,} bytes)")
            print(f"   Time: {timestamp}")
        else:
            print(f"❌ Scan #{scan_id}: {img_path}")
            print(f"   ⚠️  File not found")
            print(f"   Time: {timestamp}")
        print()
else:
    print("⚠️  No scans in database yet")

# Check scan files directory
print("-" * 70)
if scans_dir.exists():
    jpg_files = sorted(scans_dir.glob("*.jpg"))
    print(f"📂 Scan files directory: {scans_dir}")
    print(f"   JPG files found: {len(jpg_files)}")
    if jpg_files:
        print(f"\n   Files:")
        for jpg in jpg_files:
            size = jpg.stat().st_size
            print(f"     ✅ {jpg.name} ({size:,} bytes)")
else:
    print(f"❌ Scans directory not found: {scans_dir}")

conn.close()
print("=" * 70)

