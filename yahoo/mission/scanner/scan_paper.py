# mission/scanner/scan_paper.py
"""
Main entry point for simplified paper scanner.
Waits for paper (weight sensor or manual trigger), captures image, processes, and saves.
"""

import sys
import signal
import os
from dotenv import load_dotenv

from .config import (
    WEIGHT_SENSOR_ENABLED,
    WEIGHT_THRESHOLD_GRAMS,
    USE_MOCK_SENSOR,
    HX711_DT_PIN,
    HX711_SCK_PIN,
    CAMERA_INDEX,
    USE_PICAM
)
from .weight_sensor_mock import MockWeightSensor, HX711WeightSensor
from .camera_capture import CameraCapture
from .simple_pipeline import process_paper_scan

load_dotenv()

# Global flag for graceful shutdown
running = True


def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully."""
    global running
    print("\n\n🛑 Shutting down...")
    running = False


def main():
    """Main scanning loop."""
    global running
    
    # Set up signal handler for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    
    print("=" * 60)
    print("📄 Simplified Paper Scanner")
    print("=" * 60)
    print(f"Weight sensor: {'Enabled' if WEIGHT_SENSOR_ENABLED else 'Disabled'}")
    print(f"Using mock sensor: {USE_MOCK_SENSOR}")
    print(f"Camera index: {CAMERA_INDEX}")
    print("=" * 60)
    print()
    
    # Initialize weight sensor
    if WEIGHT_SENSOR_ENABLED:
        if USE_MOCK_SENSOR:
            weight_sensor = MockWeightSensor(
                threshold_grams=WEIGHT_THRESHOLD_GRAMS,
                mock_mode='keyboard'
            )
            print("📦 Using MOCK weight sensor (press 'P' + Enter to simulate paper)")
        else:
            weight_sensor = HX711WeightSensor(
                dt_pin=HX711_DT_PIN,
                sck_pin=HX711_SCK_PIN,
                threshold_grams=WEIGHT_THRESHOLD_GRAMS
            )
            print("⚖️  Using HX711 weight sensor")
    else:
        weight_sensor = None
        print("📷 Manual mode - camera will capture on command")
    
    # Initialize camera
    camera = CameraCapture(camera_index=CAMERA_INDEX, use_picam=USE_PICAM)
    
    try:
        camera.initialize()
        
        scan_count = 0
        
        # Main loop
        while running:
            try:
                # Wait for paper (or manual trigger)
                if weight_sensor:
                    print("\n📄 Waiting for paper...")
                    if not weight_sensor.wait_for_paper(timeout=None):
                        continue
                else:
                    # Manual mode - wait for user input
                    input("\n📄 Press Enter to capture image (Ctrl+C to exit)...")
                
                # Capture image
                print("📷 Capturing image...")
                image = camera.capture_image()
                
                # Get weight if sensor available
                weight = None
                if weight_sensor:
                    weight = weight_sensor.read_weight()
                
                # Process scan
                print("🔄 Processing scan...")
                result = process_paper_scan(image, weight_grams=weight)
                
                if result["success"]:
                    scan_count += 1
                    print(f"\n✅ Scan #{scan_count} complete!")
                    print(f"   Image: {result['image_path']}")
                    if result["processed"]:
                        print(f"   Student: {result['student_name']}")
                        if result.get('ocr_confidence'):
                            print(f"   Confidence: {result['ocr_confidence']:.1%}")
                    else:
                        print("   Status: Saved (name detection pending - no WiFi or API key)")
                    print()
                else:
                    print(f"\n❌ Scan failed: {result['error']}")
                    print()
                
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"\n❌ Error during scan: {e}")
                import traceback
                traceback.print_exc()
                print()
        
    finally:
        camera.release()
        print("\n👋 Scanner stopped. Goodbye!")


if __name__ == "__main__":
    main()
