"""
Test camera capture independently.
"""
import sys
import os
import cv2
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../')))

from yahoo.mission.scanner.camera_capture import CameraCapture

def test_camera():
    """Test camera capture."""
    print("📷 Testing Camera Capture")
    print("=" * 50)
    
    camera = CameraCapture(camera_index=0)
    
    try:
        print("\n1. Initializing camera...")
        camera.initialize()
        
        print("2. Capturing image...")
        image = camera.capture_image()
        
        print(f"   Image size: {image.shape[1]}x{image.shape[0]}")
        
        # Save test image
        os.makedirs("scans/test", exist_ok=True)
        test_path = "scans/test/camera_test.png"
        cv2.imwrite(test_path, image)
        print(f"3. ✅ Image saved to: {test_path}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        camera.release()

if __name__ == "__main__":
    test_camera()
