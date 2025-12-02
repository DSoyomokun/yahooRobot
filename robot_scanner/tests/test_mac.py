"""
Quick test script for Mac - no robot needed!
Tests the scanner using MacBook camera or saved images.
"""
import cv2
import logging
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from robot_scanner import RobotScanner, capture_image

# Configure logging (less verbose for testing)
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s: %(message)s'
)

def test_with_camera():
    """Test scanner with MacBook camera."""
    print("\n" + "="*60)
    print("📸 TESTING WITH MACBOOK CAMERA")
    print("="*60)
    print("Place your test paper in front of the camera...")
    print("Press any key after placing the paper, then wait for capture...")
    
    scanner = RobotScanner(camera_index=0)
    
    try:
        # Capture and scan
        print("\n⏳ Capturing and processing...")
        result = scanner.scan_paper()
        
        if result:
            print("\n" + "="*60)
            print("✅ SCAN SUCCESSFUL!")
            print("="*60)
            print(f"📝 Student Name: {result['student_name']}")
            print(f"📊 Score: {result['score']:.0f}/{result['total_questions']}")
            print(f"📈 Percentage: {result['percentage']:.1f}%")
            print(f"✅ Correct: {result['correct']}")
            print(f"❌ Incorrect: {result['incorrect']}")
            print(f"⭕ Unanswered: {result['unanswered']}")
            print(f"\n📋 Answers: {result['answers']}")
            print("\n💾 Results saved to database!")
            return True
        else:
            print("\n❌ SCAN FAILED - Check camera and paper placement")
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
    print(f"🖼️  TESTING WITH IMAGE: {image_path}")
    print("="*60)
    
    if not Path(image_path).exists():
        print(f"❌ Image file not found: {image_path}")
        return False
    
    # Load image
    image = cv2.imread(image_path)
    if image is None:
        print(f"❌ Failed to load image: {image_path}")
        return False
    
    scanner = RobotScanner()
    
    try:
        print("\n⏳ Processing image...")
        result = scanner.scan_paper(image=image)
        
        if result:
            print("\n" + "="*60)
            print("✅ SCAN SUCCESSFUL!")
            print("="*60)
            print(f"📝 Student Name: {result['student_name']}")
            print(f"📊 Score: {result['score']:.0f}/{result['total_questions']}")
            print(f"📈 Percentage: {result['percentage']:.1f}%")
            print(f"✅ Correct: {result['correct']}")
            print(f"❌ Incorrect: {result['incorrect']}")
            print(f"⭕ Unanswered: {result['unanswered']}")
            print(f"\n📋 Answers: {result['answers']}")
            print("\n💾 Results saved to database!")
            return True
        else:
            print("\n❌ SCAN FAILED")
            return False
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


def quick_capture():
    """Quickly capture an image for later testing."""
    print("\n" + "="*60)
    print("📸 QUICK CAPTURE")
    print("="*60)
    print("Capturing image in 2 seconds...")
    print("Make sure your test paper is in front of the camera!")
    
    import time
    time.sleep(2)
    
    try:
        output_path = "robot_scanner/tests/captured_paper.jpg"
        image_path = capture_image(camera_index=0, save_path=output_path)
        print(f"\n✅ Image captured and saved to: {image_path}")
        print(f"\nYou can now test it with:")
        print(f"  python robot_scanner/tests/test_mac.py --image {image_path}")
        return True
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        return False


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Test Robot Scanner on Mac (No robot needed!)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Test with camera (place paper in front of MacBook)
  python robot_scanner/tests/test_mac.py --camera
  
  # Test with saved image
  python robot_scanner/tests/test_mac.py --image path/to/image.jpg
  
  # Quick capture (save image for later)
  python robot_scanner/tests/test_mac.py --capture
        """
    )
    parser.add_argument('--image', type=str, help='Test with saved image file')
    parser.add_argument('--camera', action='store_true', help='Test with MacBook camera')
    parser.add_argument('--capture', action='store_true', help='Quick capture (save image only)')
    
    args = parser.parse_args()
    
    if args.image:
        test_with_image(args.image)
    elif args.capture:
        quick_capture()
    elif args.camera:
        test_with_camera()
    else:
        print("🤖 Robot Scanner - Mac Testing Mode")
        print("="*60)
        print("\nChoose a test option:")
        print("  1. Test with camera:     python robot_scanner/tests/test_mac.py --camera")
        print("  2. Test with image:      python robot_scanner/tests/test_mac.py --image path.jpg")
        print("  3. Quick capture:        python robot_scanner/tests/test_mac.py --capture")
        print("\n💡 Tip: Use --capture first to save an image, then test with --image")

