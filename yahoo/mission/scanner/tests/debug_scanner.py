"""
Debug script to visualize what the scanner detects.
Shows name region and detected bubbles.
"""
import cv2
import sys
from pathlib import Path
import numpy as np

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent))

from yahoo.mission.scanner import RobotScanner, capture_image
from yahoo.mission.scanner.bubble_detector import BubbleDetector
from yahoo.mission.scanner.name_reader import NameReader

def debug_scan(image_path: str):
    """Debug scan with visualization."""
    print(f"\n🔍 DEBUGGING SCAN: {image_path}")
    print("="*60)
    
    # Load image
    image = cv2.imread(image_path)
    if image is None:
        print(f"❌ Failed to load: {image_path}")
        return
    
    h, w = image.shape[:2]
    print(f"Image size: {w}x{h}")
    
    # Create debug visualization
    debug_image = image.copy()
    
    # 1. Show name region (fixed coordinates)
    name_top = int(h * 0.05)
    name_bottom = int(h * 0.15)
    name_left = int(w * 0.10)
    name_right = int(w * 0.50)
    
    cv2.rectangle(debug_image, (name_left, name_top), (name_right, name_bottom), (0, 255, 0), 3)
    cv2.putText(debug_image, "NAME REGION", (name_left, name_top - 10), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
    
    # 2. Test bubble detection
    detector = BubbleDetector()
    
    processed = detector.preprocess(image)
    bubbles = detector.detect_bubbles(processed)
    
    print(f"\n📊 DETECTION RESULTS:")
    print(f"   Bubbles detected: {len(bubbles)}")
    
    # Draw detected bubbles
    for i, bubble in enumerate(bubbles[:50]):  # Limit to first 50
        x, y, w, h = bubble['bounding_rect']
        cx, cy = bubble['center']
        
        # Draw bubble
        cv2.rectangle(debug_image, (x, y), (x+w, y+h), (255, 0, 255), 2)
        cv2.circle(debug_image, (cx, cy), 5, (255, 0, 255), -1)
        
        # Calculate fill
        gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
        fill = detector.calculate_fill(gray_image, bubble)
        cv2.putText(debug_image, f"{fill:.2f}", (x, y-5), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 0, 255), 1)
    
    # Save debug image
    debug_dir = Path(__file__).parent / "debug_output"
    debug_dir.mkdir(exist_ok=True)
    debug_path = debug_dir / "visualization.jpg"
    cv2.imwrite(str(debug_path), debug_image)
    print(f"\n✅ Debug visualization saved to: {debug_path}")
    print(f"   - Green rectangle = Name region")
    print(f"   - Magenta rectangles = Detected bubbles (with fill %)")
    
    # 3. Test name extraction
    reader = NameReader()
    
    name_region = reader.extract_name_region(image)
    name = reader.extract_name(image)
    
    print(f"\n📝 NAME EXTRACTION:")
    print(f"   Extracted: {name}")
    
    # Save name region
    name_region_path = debug_dir / "name_region.jpg"
    cv2.imwrite(str(name_region_path), name_region)
    print(f"   Name region saved to: {name_region_path}")
    
    # 4. Test full pipeline
    print(f"\n🔄 RUNNING FULL PIPELINE...")
    scanner = RobotScanner()
    result = scanner.scan_paper(image=image)
    
    if result:
        print(f"\n✅ FULL SCAN RESULTS:")
        print(f"   Name: {result['student_name']}")
        print(f"   Answers: {result['answers']}")
        print(f"   Score: {result['score']}/{result['total_questions']}")
    else:
        print(f"\n❌ Full scan failed")
    
    return str(debug_path)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--image', type=str, help='Image file to debug')
    parser.add_argument('--camera', action='store_true', help='Capture from camera first')
    
    args = parser.parse_args()
    
    if args.camera:
        debug_dir = Path(__file__).parent / "debug_output"
        debug_dir.mkdir(exist_ok=True)
        image_path = capture_image(save_path=str(debug_dir / "capture.jpg"))
        print(f"📸 Captured image: {image_path}")
        debug_scan(image_path)
    elif args.image:
        debug_scan(args.image)
    else:
        print("Usage:")
        print("  python robot_scanner/tests/debug_scanner.py --camera    # Capture and debug")
        print("  python robot_scanner/tests/debug_scanner.py --image path.jpg  # Debug saved image")

