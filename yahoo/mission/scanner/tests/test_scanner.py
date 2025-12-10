"""
Standalone test script for robot_scanner module.
Tests the scanner without using the rest of the yahooRobot codebase.
"""
import cv2
import logging
import sys
from pathlib import Path

# Add project root to path to import yahoo.mission.scanner
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent))

from yahoo.mission.scanner import ScanControl

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def test_with_camera():
    """Test scanner with live camera capture."""
    print("\n" + "="*60)
    print("TESTING ROBOT SCANNER - CAMERA MODE")
    print("="*60)
    
    scanner = ScanControl(camera_index=0)
    
    try:
        # Capture and scan
        result = scanner.scan_paper()
        
        if result:
            print("\n✅ SCAN SUCCESSFUL!")
            print(f"Student Name: {result['student_name']}")
            print(f"Score: {result['score']}/{result['total_questions']}")
            print(f"Percentage: {result['percentage']:.1f}%")
            print(f"Correct: {result['correct']}, Incorrect: {result['incorrect']}, Unanswered: {result['unanswered']}")
            print(f"\nAnswers: {result['answers']}")
            return True
        else:
            print("\n❌ SCAN FAILED")
            return False
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        scanner.release()


def test_with_image(image_path: str):
    """Test scanner with a saved image file."""
    print("\n" + "="*60)
    print(f"TESTING ROBOT SCANNER - IMAGE FILE: {image_path}")
    print("="*60)
    
    if not Path(image_path).exists():
        print(f"❌ Image file not found: {image_path}")
        return False
    
    # Load image
    image = cv2.imread(image_path)
    if image is None:
        print(f"❌ Failed to load image: {image_path}")
        return False
    
    scanner = ScanControl()
    
    try:
        # Scan the loaded image
        result = scanner.process_test(image=image, store=True)
        
        if result:
            print("\n✅ SCAN SUCCESSFUL!")
            print(f"Student Name: {result['student_name']}")
            print(f"Score: {result['score']}/{result['total_questions']}")
            print(f"Percentage: {result['percentage']:.1f}%")
            print(f"Correct: {result['correct']}, Incorrect: {result['incorrect']}, Unanswered: {result['unanswered']}")
            print(f"\nAnswers: {result['answers']}")
            return True
        else:
            print("\n❌ SCAN FAILED")
            return False
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_capture_only():
    """Test just the camera capture function."""
    print("\n" + "="*60)
    print("TESTING CAMERA CAPTURE ONLY")
    print("="*60)
    
    try:
        image_path = capture_image(camera_index=0, save_path="robot_scanner/tests/test_capture.jpg")
        print(f"✅ Image captured and saved to: {image_path}")
        return True
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Test Robot Scanner Module')
    parser.add_argument('--image', type=str, help='Test with saved image file')
    parser.add_argument('--camera', action='store_true', help='Test with live camera')
    parser.add_argument('--capture-only', action='store_true', help='Test camera capture only')
    
    args = parser.parse_args()
    
    if args.image:
        test_with_image(args.image)
    elif args.capture_only:
        test_capture_only()
    elif args.camera:
        test_with_camera()
    else:
        print("Usage:")
        print("  python robot_scanner/tests/test_scanner.py --camera          # Test with live camera")
        print("  python robot_scanner/tests/test_scanner.py --image path.jpg  # Test with saved image")
        print("  python robot_scanner/tests/test_scanner.py --capture-only    # Test camera capture only")

