"""
Test script for mock weight sensor functionality.
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../')))

from yahoo.mission.scanner.weight_sensor_mock import MockWeightSensor

def test_mock_sensor():
    """Test mock weight sensor with keyboard input."""
    print("🧪 Testing Mock Weight Sensor")
    print("=" * 50)
    
    sensor = MockWeightSensor(threshold_grams=1.0, mock_mode='keyboard')
    
    print("\nTest 1: Wait for paper (keyboard trigger)")
    print("Press 'P' + Enter to simulate paper detection...")
    
    detected = sensor.wait_for_paper(timeout=30)
    
    if detected:
        print("✅ Test passed: Paper detection triggered")
    else:
        print("❌ Test failed: Timeout waiting for paper")
    
    print("\nTest 2: Weight detection check")
    weight = sensor.read_weight()
    print(f"Current weight: {weight}g")
    print(f"Threshold: {sensor.threshold}g")
    print(f"Paper detected: {sensor.detect_paper()}")

if __name__ == "__main__":
    test_mock_sensor()
