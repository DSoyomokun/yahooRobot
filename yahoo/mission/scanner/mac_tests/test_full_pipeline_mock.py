"""
Test full simplified pipeline with mocked weight sensor.
"""
import sys
import os
import cv2
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../')))
from dotenv import load_dotenv

from yahoo.mission.scanner.weight_sensor_mock import MockWeightSensor
from yahoo.mission.scanner.camera_capture import CameraCapture
from yahoo.mission.scanner.simple_pipeline import process_paper_scan

load_dotenv()

def test_full_pipeline_mock():
    """Test full pipeline with mocked components."""
    print("🔄 Testing Full Simplified Pipeline (Mocked)")
    print("=" * 60)
    
    # Initialize components
    weight_sensor = MockWeightSensor(threshold_grams=1.0, mock_mode='keyboard')
    camera = CameraCapture(camera_index=0)
    
    try:
        camera.initialize()
        
        print("\n📄 Waiting for paper...")
        print("   Press 'P' + Enter to simulate paper detection")
        
        # Wait for paper
        if weight_sensor.wait_for_paper(timeout=60):
            print("\n📷 Capturing image...")
            image = camera.capture_image()
            
            print(f"   Image captured: {image.shape[1]}x{image.shape[0]}")
            
            # Process through simplified pipeline
            api_key = os.getenv('OPENAI_API_KEY')
            result = process_paper_scan(image, api_key=api_key, weight_grams=1.5)
            
            print(f"\n✅ Scan complete:")
            print(f"   Success: {result['success']}")
            if result['success']:
                print(f"   Image saved: {result['image_path']}")
                print(f"   Student: {result.get('student_name', 'UNKNOWN')}")
                if result.get('ocr_confidence'):
                    print(f"   Confidence: {result['ocr_confidence']:.1%}")
                print(f"   Processed: {result.get('processed', False)}")
                print(f"   WiFi: {result.get('has_wifi', False)}")
            else:
                print(f"   Error: {result.get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        camera.release()

if __name__ == "__main__":
    test_full_pipeline_mock()
