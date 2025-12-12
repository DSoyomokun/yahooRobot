"""
View database scans with image previews.
Opens images in default image viewer or displays in OpenCV window.
"""
import sys
import os
import sqlite3
import cv2
import subprocess
from datetime import datetime
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../')))

from yahoo.mission.scanner.storage import DB_PATH

def view_scan_image(scan_id=None, image_path=None):
    """
    View a specific scan image.
    
    Args:
        scan_id: Database ID of scan
        image_path: Direct path to image file
    """
    if image_path:
        path = image_path
    elif scan_id:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("SELECT image_path FROM paper_scans WHERE id = ?", (scan_id,))
        result = cur.fetchone()
        conn.close()
        
        if not result:
            print(f"❌ Scan ID {scan_id} not found")
            return
        path = result[0]
    else:
        print("❌ Provide either scan_id or image_path")
        return
    
    if not os.path.exists(path):
        print(f"❌ Image not found: {path}")
        return
    
    # Load and display image
    img = cv2.imread(path)
    if img is None:
        print(f"❌ Failed to load image: {path}")
        return
    
    # Resize if too large for display
    h, w = img.shape[:2]
    max_display_size = 1200
    if w > max_display_size or h > max_display_size:
        scale = max_display_size / max(w, h)
        new_w = int(w * scale)
        new_h = int(h * scale)
        img = cv2.resize(img, (new_w, new_h))
    
    # Display with info
    cv2.imshow(f"Scan Image - {os.path.basename(path)}", img)
    print(f"✅ Displaying: {path}")
    print("   Press any key to close...")
    cv2.waitKey(0)
    cv2.destroyAllWindows()


def list_scans_with_preview():
    """List all scans and allow selecting one to view."""
    if not os.path.exists(DB_PATH):
        print(f"❌ Database not found: {DB_PATH}")
        return
    
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    cur.execute("""
        SELECT id, timestamp, image_path, student_name, processed
        FROM paper_scans
        ORDER BY timestamp DESC
    """)
    
    scans = cur.fetchall()
    conn.close()
    
    if not scans:
        print("📭 No scans found.")
        return
    
    print("=" * 80)
    print(f"📊 SCANS IN DATABASE ({len(scans)} total)")
    print("=" * 80)
    print()
    
    for i, (scan_id, ts, img_path, name, processed) in enumerate(scans, 1):
        try:
            dt = datetime.fromisoformat(ts)
            time_str = dt.strftime("%Y-%m-%d %H:%M:%S")
        except:
            time_str = ts
        
        status = "✅" if processed else "⏳"
        name_str = name if name else "(Not processed)"
        
        print(f"{i}. {status} ID {scan_id} | {time_str}")
        print(f"   Student: {name_str}")
        print(f"   Image: {img_path}")
        print()
    
    # Interactive selection
    try:
        choice = input("Enter scan number to view image (or 'q' to quit): ").strip()
        if choice.lower() == 'q':
            return
        
        scan_num = int(choice)
        if 1 <= scan_num <= len(scans):
            scan_id = scans[scan_num - 1][0]
            image_path = scans[scan_num - 1][2]
            view_scan_image(image_path=image_path)
        else:
            print("❌ Invalid selection")
    except (ValueError, KeyboardInterrupt):
        print("\n👋 Exiting...")


def open_image_in_system_viewer(image_path):
    """Open image in system's default image viewer."""
    if not os.path.exists(image_path):
        print(f"❌ Image not found: {image_path}")
        return False
    
    try:
        if sys.platform == 'darwin':  # macOS
            subprocess.run(['open', image_path])
        elif sys.platform == 'linux':
            subprocess.run(['xdg-open', image_path])
        elif sys.platform == 'win32':
            os.startfile(image_path)
        return True
    except Exception as e:
        print(f"❌ Failed to open image: {e}")
        return False


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="View scans with images")
    parser.add_argument("--id", type=int, help="View specific scan by ID")
    parser.add_argument("--path", help="View image by path")
    parser.add_argument("--open", action="store_true", help="Open in system viewer instead of OpenCV")
    args = parser.parse_args()
    
    if args.id:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("SELECT image_path FROM paper_scans WHERE id = ?", (args.id,))
        result = cur.fetchone()
        conn.close()
        if result:
            if args.open:
                open_image_in_system_viewer(result[0])
            else:
                view_scan_image(image_path=result[0])
        else:
            print(f"❌ Scan ID {args.id} not found")
    elif args.path:
        if args.open:
            open_image_in_system_viewer(args.path)
        else:
            view_scan_image(image_path=args.path)
    else:
        list_scans_with_preview()


