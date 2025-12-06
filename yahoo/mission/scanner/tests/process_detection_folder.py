#!/usr/bin/env python3
"""
Process all images in detection_visualization folder for auto-grading and storage.
This script processes the processed images that are ready for grading.
"""
import sys
import cv2
from pathlib import Path
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from yahoo.mission.scanner.scanner import RobotScanner


def process_detection_folder():
    """Process all processed images in detection_visualization folder."""
    base_dir = Path(__file__).parent / "captured_images"
    vis_dir = base_dir / "detection_visualization"
    
    if not vis_dir.exists():
        print(f"❌ Detection visualization folder not found: {vis_dir}")
        return
    
    # Find all processed images (processed_*.jpg)
    processed_images = sorted(vis_dir.glob("processed_*.jpg"))
    
    if not processed_images:
        print(f"⚠️  No processed images found in {vis_dir}")
        print("   Looking for files matching: processed_*.jpg")
        return
    
    print(f"\n{'='*60}")
    print(f"📝 PROCESSING DETECTION VISUALIZATION FOLDER")
    print(f"{'='*60}")
    print(f"\n📁 Folder: {vis_dir}")
    print(f"📊 Found {len(processed_images)} processed image(s)\n")
    
    scanner = RobotScanner()
    
    for i, image_path in enumerate(processed_images, 1):
        print(f"\n{'='*60}")
        print(f"Processing {i}/{len(processed_images)}: {image_path.name}")
        print(f"{'='*60}")
        
        # Load image
        image = cv2.imread(str(image_path))
        if image is None:
            print(f"❌ Failed to load image: {image_path}")
            continue
        
        # Process with scanner (this will auto-grade and store)
        print("\n🔍 Running full scan pipeline (name + bubbles + grading + storage)...")
        result = scanner.scan_image(image, store=True)
        
        if result:
            print(f"\n✅ SCAN SUCCESSFUL!")
            print(f"   👤 Student: {result.get('student_name', 'Unknown')}")
            print(f"   📊 Score: {result.get('score', 0)}/{result.get('total_questions', 0)} ({result.get('percentage', 0):.1f}%)")
            print(f"   ✅ Correct: {result.get('correct', 0)}")
            print(f"   ❌ Incorrect: {result.get('incorrect', 0)}")
            print(f"   ⚪ Unanswered: {result.get('unanswered', 0)}")
            print(f"   💾 Results stored to database")
        else:
            print(f"❌ Scan failed for {image_path.name}")
    
    print(f"\n{'='*60}")
    print(f"✅ PROCESSING COMPLETE")
    print(f"{'='*60}")
    print(f"\n📊 Processed {len(processed_images)} image(s)")
    print(f"💾 All results saved to database")


if __name__ == "__main__":
    process_detection_folder()


