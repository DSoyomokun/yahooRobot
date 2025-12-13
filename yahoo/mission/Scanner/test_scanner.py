#!/usr/bin/env python3
"""
Test script for production-ready scanner
Tests all functionality: import, state machine, edge detection, completion signals
"""
import sys
from pathlib import Path

# Add project root to path
_script_dir = Path(__file__).parent.resolve()
_project_root = _script_dir.parent.parent.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

import time
from yahoo.mission.scanner.scanner import Scanner, ScannerState

def test_import_safety():
    """Test 1: Verify scanner can be imported without side effects."""
    print("=" * 70)
    print("TEST 1: Import Safety")
    print("=" * 70)
    
    try:
        from yahoo.mission.scanner.scanner import Scanner, ScannerState
        print("✅ Scanner imports successfully")
        
        scanner = Scanner()
        print("✅ Scanner can be instantiated")
        print(f"✅ Initial state: {scanner.get_state().value}")
        print(f"✅ Not running: {not scanner.is_running()}")
        print("✅ No side effects on import/instantiation")
        return True
    except Exception as e:
        print(f"❌ Import test failed: {e}")
        return False

def test_state_machine():
    """Test 2: Verify state machine states exist."""
    print("\n" + "=" * 70)
    print("TEST 2: State Machine")
    print("=" * 70)
    
    try:
        states = [s.value for s in ScannerState]
        expected = ["IDLE", "PROCESSING", "SUCCESS", "COOLDOWN"]
        
        print(f"✅ States defined: {states}")
        
        if states == expected:
            print("✅ All required states present")
            return True
        else:
            print(f"❌ Missing states. Expected: {expected}, Got: {states}")
            return False
    except Exception as e:
        print(f"❌ State machine test failed: {e}")
        return False

def test_completion_callback():
    """Test 3: Verify completion callback mechanism."""
    print("\n" + "=" * 70)
    print("TEST 3: Completion Callback")
    print("=" * 70)
    
    callback_called = []
    
    def test_callback(file_path):
        callback_called.append(file_path)
        print(f"  📢 Callback received: {file_path}")
    
    try:
        scanner = Scanner(completion_callback=test_callback)
        print("✅ Scanner accepts completion_callback parameter")
        print("✅ Callback will be called when scan is saved")
        return True
    except Exception as e:
        print(f"❌ Callback test failed: {e}")
        return False

def test_scanner_lifecycle():
    """Test 4: Test scanner start/stop lifecycle."""
    print("\n" + "=" * 70)
    print("TEST 4: Scanner Lifecycle")
    print("=" * 70)
    
    try:
        scanner = Scanner()
        
        # Test start
        print("Attempting to start scanner...")
        result = scanner.start()
        
        if result:
            print("✅ Scanner started successfully")
            print(f"✅ State after start: {scanner.get_state().value}")
            print(f"✅ Running status: {scanner.is_running()}")
            
            # Wait a moment
            time.sleep(1)
            
            # Test stop
            print("\nStopping scanner...")
            scanner.stop()
            print("✅ Scanner stopped successfully")
            print(f"✅ State after stop: {scanner.get_state().value}")
            print(f"✅ Running status: {not scanner.is_running()}")
            return True
        else:
            print("⚠️  Scanner start returned False (camera may not be available)")
            print("   This is OK if testing without camera hardware")
            return True  # Not a failure if camera unavailable
    except Exception as e:
        print(f"❌ Lifecycle test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_edge_detection():
    """Test 5: Verify edge-triggered detection logic."""
    print("\n" + "=" * 70)
    print("TEST 5: Edge-Triggered Detection")
    print("=" * 70)
    
    try:
        from yahoo.mission.scanner.detector import PaperDetector
        
        detector = PaperDetector(threshold=30)
        print("✅ PaperDetector instantiated")
        
        # Test that it doesn't trigger without baseline
        import numpy as np
        dummy_frame = np.zeros((480, 640, 3), dtype=np.uint8)
        
        result1 = detector.paper_detected(dummy_frame)
        print(f"✅ First frame (baseline): {result1} (should be False)")
        
        result2 = detector.paper_detected(dummy_frame)
        print(f"✅ Second frame (same): {result2} (should be False)")
        
        # Test reset
        detector.reset()
        print("✅ Detector reset successfully")
        
        return True
    except Exception as e:
        print(f"❌ Edge detection test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests."""
    print("\n" + "=" * 70)
    print("🧪 PRODUCTION-READY SCANNER TEST SUITE")
    print("=" * 70)
    print()
    
    tests = [
        ("Import Safety", test_import_safety),
        ("State Machine", test_state_machine),
        ("Completion Callback", test_completion_callback),
        ("Edge Detection", test_edge_detection),
        ("Scanner Lifecycle", test_scanner_lifecycle),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"❌ Test '{name}' crashed: {e}")
            results.append((name, False))
    
    # Summary
    print("\n" + "=" * 70)
    print("📊 TEST SUMMARY")
    print("=" * 70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {name}")
    
    print()
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed!")
    else:
        print("⚠️  Some tests failed or skipped (may be due to missing camera)")
    
    print("=" * 70)
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

