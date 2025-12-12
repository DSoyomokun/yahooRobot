"""
View stored scans from database.
Displays all scans with images.
"""
import sqlite3
import cv2
import os

DB_PATH = "scans.db"

def main():
    if not os.path.exists(DB_PATH):
        print("❌ Database not found. Run setup_db.py first.")
        return
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, image_path, timestamp FROM scans ORDER BY id DESC")
    rows = cursor.fetchall()
    
    if not rows:
        print("📭 No scans found in database.")
        conn.close()
        return
    
    print("\n" + "=" * 60)
    print(f"📋 STORED SCANS ({len(rows)} total)")
    print("=" * 60)
    
    for scan in rows:
        scan_id, image_path, timestamp = scan
        print(f"\nScan #{scan_id}")
        print(f"  Image: {image_path}")
        print(f"  Time: {timestamp}")
        
        # Check if image exists
        if os.path.exists(image_path):
            img = cv2.imread(image_path)
            if img is not None:
                # Resize if too large for display
                h, w = img.shape[:2]
                if w > 1200 or h > 800:
                    scale = min(1200/w, 800/h)
                    new_w = int(w * scale)
                    new_h = int(h * scale)
                    img = cv2.resize(img, (new_w, new_h))
                
                cv2.imshow(f"Scan #{scan_id} - {timestamp}", img)
                print(f"  ✅ Image displayed (press any key to continue)")
                cv2.waitKey(0)
                cv2.destroyAllWindows()
            else:
                print(f"  ⚠️  Could not load image")
        else:
            print(f"  ❌ Image file not found")
    
    conn.close()
    print("\n✅ Done viewing scans.")

if __name__ == "__main__":
    main()


