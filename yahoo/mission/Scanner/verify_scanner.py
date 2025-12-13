"""
Quick verification script to check if scanner is working.
Checks database, files, and shows stats.
"""
import sqlite3
import os
import glob

DB_PATH = "scans.db"
SCAN_FOLDER = "scans"

def verify_scanner():
    print("=" * 60)
    print("🔍 SCANNER VERIFICATION")
    print("=" * 60)
    print()
    
    # Check 1: Database exists
    print("1️⃣  Checking database...")
    if os.path.exists(DB_PATH):
        print(f"   ✅ Database found: {DB_PATH}")
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Count records
        cursor.execute("SELECT COUNT(*) FROM scans")
        count = cursor.fetchone()[0]
        print(f"   📊 Total scans in DB: {count}")
        
        if count > 0:
            # Get latest scan
            cursor.execute("SELECT id, image_path, timestamp FROM scans ORDER BY id DESC LIMIT 1")
            latest = cursor.fetchone()
            if latest:
                scan_id, image_path, timestamp = latest
                print(f"   📸 Latest scan: #{scan_id}")
                print(f"      Image: {image_path}")
                print(f"      Time: {timestamp}")
                
                # Check if image file exists
                if os.path.exists(image_path):
                    size = os.path.getsize(image_path)
                    print(f"      ✅ Image file exists ({size:,} bytes)")
                else:
                    print(f"      ❌ Image file NOT found!")
            
            # Show all scans
            cursor.execute("SELECT id, image_path, timestamp FROM scans ORDER BY id DESC")
            all_scans = cursor.fetchall()
            print(f"\n   📋 All scans:")
            for scan_id, img_path, ts in all_scans:
                exists = "✅" if os.path.exists(img_path) else "❌"
                print(f"      {exists} Scan #{scan_id}: {img_path} @ {ts}")
        else:
            print("   ⚠️  No scans in database yet")
        
        conn.close()
    else:
        print(f"   ❌ Database not found: {DB_PATH}")
        print("   💡 Run: python3 setup_db.py")
    
    print()
    
    # Check 2: Scan folder
    print("2️⃣  Checking scan folder...")
    if os.path.exists(SCAN_FOLDER):
        print(f"   ✅ Folder exists: {SCAN_FOLDER}")
        
        # Count image files
        image_files = glob.glob(f"{SCAN_FOLDER}/*.jpg") + glob.glob(f"{SCAN_FOLDER}/*.png")
        print(f"   📸 Image files found: {len(image_files)}")
        
        if image_files:
            latest_file = max(image_files, key=os.path.getmtime)
            size = os.path.getsize(latest_file)
            print(f"   📄 Latest file: {os.path.basename(latest_file)} ({size:,} bytes)")
    else:
        print(f"   ⚠️  Folder not found: {SCAN_FOLDER}")
        print("   💡 Will be created automatically when scanner runs")
    
    print()
    
    # Summary
    print("=" * 60)
    if os.path.exists(DB_PATH):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM scans")
        count = cursor.fetchone()[0]
        conn.close()
        
        if count > 0:
            print("✅ SCANNER IS WORKING!")
            print(f"   Found {count} scan(s) in database")
        else:
            print("⚠️  Scanner ready but no scans yet")
            print("   Place paper in front of camera to test")
    else:
        print("❌ Database not set up")
        print("   Run: python3 setup_db.py")
    print("=" * 60)

if __name__ == "__main__":
    verify_scanner()

