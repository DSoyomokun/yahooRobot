"""
View and query the paper_scans database.
"""
import sys
import os
import sqlite3
from datetime import datetime
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../')))

from yahoo.mission.scanner.storage import DB_PATH

def view_all_scans():
    """Display all scans in the database."""
    if not os.path.exists(DB_PATH):
        print(f"❌ Database not found: {DB_PATH}")
        print("   Run a scan first to create the database.")
        return
    
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    # Get all scans
    cur.execute("""
        SELECT id, timestamp, image_path, student_name, ocr_raw, 
               ocr_confidence, processed, weight_grams
        FROM paper_scans
        ORDER BY timestamp DESC
    """)
    
    scans = cur.fetchall()
    
    if not scans:
        print("📭 No scans found in database.")
        return
    
    print("=" * 80)
    print(f"📊 PAPER SCANS DATABASE ({len(scans)} total)")
    print("=" * 80)
    print()
    
    for scan in scans:
        scan_id, ts, img_path, name, ocr_raw, conf, processed, weight = scan
        
        # Format timestamp
        try:
            dt = datetime.fromisoformat(ts)
            time_str = dt.strftime("%Y-%m-%d %H:%M:%S")
        except:
            time_str = ts
        
        print(f"📄 Scan ID: {scan_id}")
        print(f"   Time: {time_str}")
        print(f"   Image: {img_path}")
        print(f"   Student: {name if name else '(Not processed)'}")
        if ocr_raw:
            print(f"   OCR: \"{ocr_raw}\"")
        if conf:
            print(f"   Confidence: {conf:.1%}")
        print(f"   Status: {'✅ Processed' if processed else '⏳ Pending'}")
        if weight:
            print(f"   Weight: {weight}g")
        print()
    
    conn.close()


def view_unprocessed():
    """Show only unprocessed scans (no student name)."""
    if not os.path.exists(DB_PATH):
        print(f"❌ Database not found: {DB_PATH}")
        return
    
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    cur.execute("""
        SELECT id, timestamp, image_path
        FROM paper_scans
        WHERE processed = 0
        ORDER BY timestamp DESC
    """)
    
    scans = cur.fetchall()
    
    if not scans:
        print("✅ No unprocessed scans - all have student names!")
        return
    
    print(f"⏳ UNPROCESSED SCANS ({len(scans)} total)")
    print("=" * 60)
    print()
    
    for scan_id, ts, img_path in scans:
        try:
            dt = datetime.fromisoformat(ts)
            time_str = dt.strftime("%Y-%m-%d %H:%M:%S")
        except:
            time_str = ts
        
        print(f"  ID {scan_id}: {time_str} - {img_path}")
    
    conn.close()


def view_statistics():
    """Show database statistics."""
    if not os.path.exists(DB_PATH):
        print(f"❌ Database not found: {DB_PATH}")
        return
    
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    # Total scans
    cur.execute("SELECT COUNT(*) FROM paper_scans")
    total = cur.fetchone()[0]
    
    # Processed scans
    cur.execute("SELECT COUNT(*) FROM paper_scans WHERE processed = 1")
    processed = cur.fetchone()[0]
    
    # Unprocessed scans
    unprocessed = total - processed
    
    # Unique students
    cur.execute("SELECT COUNT(DISTINCT student_name) FROM paper_scans WHERE student_name IS NOT NULL")
    unique_students = cur.fetchone()[0]
    
    print("📊 DATABASE STATISTICS")
    print("=" * 60)
    print(f"Total scans: {total}")
    print(f"Processed: {processed} ({processed/total*100:.1f}%)" if total > 0 else "Processed: 0")
    print(f"Pending: {unprocessed} ({unprocessed/total*100:.1f}%)" if total > 0 else "Pending: 0")
    print(f"Unique students: {unique_students}")
    print()
    
    # Students with most scans
    cur.execute("""
        SELECT student_name, COUNT(*) as count
        FROM paper_scans
        WHERE student_name IS NOT NULL
        GROUP BY student_name
        ORDER BY count DESC
        LIMIT 10
    """)
    
    top_students = cur.fetchall()
    if top_students:
        print("👥 Top Students:")
        for name, count in top_students:
            print(f"   {name}: {count} scan(s)")
    
    conn.close()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="View paper scans database")
    parser.add_argument("--unprocessed", action="store_true", help="Show only unprocessed scans")
    parser.add_argument("--stats", action="store_true", help="Show database statistics")
    args = parser.parse_args()
    
    if args.stats:
        view_statistics()
    elif args.unprocessed:
        view_unprocessed()
    else:
        view_all_scans()


