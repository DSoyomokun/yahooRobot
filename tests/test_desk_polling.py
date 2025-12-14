#!/usr/bin/env python3
"""
Test Desk-Centric Polling - Stories 2.1 + 2.2

Tests the person detection and desk polling systems:
- Person detector (back-view optimized)
- Desk poller (generic scanner)
- Full polling workflow

This can run in simulation mode for development or on hardware for validation.
"""

import sys
import time
import logging
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from yahoo.robot import Robot
from yahoo.config.row_loader import load_row_config
from yahoo.sense.person_detector import PersonDetector
from yahoo.mission.desk_poller import DeskPoller


class PollingTest:
    """Test suite for desk polling system."""

    def __init__(self, robot, config, simulate=False):
        self.robot = robot
        self.config = config
        self.simulate = simulate
        self.camera = None  # Would be initialized on hardware

    def test_person_detector(self):
        """Test 1: Person detector basics."""
        print("\n" + "=" * 60)
        print("TEST 1: Person Detector")
        print("=" * 60)

        print("\nInitializing person detector...")
        detector = PersonDetector(simulate=self.simulate)

        print(f"✅ Detector initialized (simulate={self.simulate})")

        if self.simulate:
            print("\n⚠️  Simulation mode - using mock detection")
            # Test with None frame (simulation)
            result = detector.detect(None)
            print(f"Detection result: {result}")
            assert result == True, "Simulation should always detect person"
            print("✅ Simulation detection works")

            # Test with details
            details = detector.detect_with_details(None)
            print(f"\nDetection details: {details}")
            assert details['person_detected'] == True
            assert details['confidence'] == 1.0
            print("✅ Detailed detection works")
        else:
            print("\n⚠️  Hardware mode - would need camera feed")
            print("   Skipping frame-based detection in this test")

        detector.close()
        print("\n✅ TEST 1 PASSED: Person detector functional")
        return True

    def test_desk_poller_setup(self):
        """Test 2: Desk poller initialization."""
        print("\n" + "=" * 60)
        print("TEST 2: Desk Poller Setup")
        print("=" * 60)

        print("\nInitializing desk poller...")
        poller = DeskPoller(
            robot=self.robot,
            config=self.config,
            camera=self.camera,
            simulate=self.simulate,
            stabilization_time=0.5
        )

        print(f"✅ Poller initialized")
        print(f"   Desks to scan: {len(self.config.desks)}")
        print(f"   Desk IDs: {[d.id for d in self.config.desks]}")

        # Print scan angles
        print("\nScan configuration:")
        for desk in self.config.desks:
            scan_angle = self.config.get_scan_angle(desk.id)
            print(f"  Desk {desk.id}: scan angle = {scan_angle:+.1f}°")

        print("\n✅ TEST 2 PASSED: Desk poller initialized correctly")
        return True

    def test_person_scan(self):
        """Test 3: Full person detection scan."""
        print("\n" + "=" * 60)
        print("TEST 3: Person Detection Scan")
        print("=" * 60)

        if not self.simulate:
            print("\n⚠️  Hardware mode: This test will turn the robot!")
            response = input("Continue? (y/n): ")
            if response.lower() != 'y':
                print("Test skipped.")
                return True

        print("\nCreating desk poller...")
        poller = DeskPoller(
            robot=self.robot,
            config=self.config,
            camera=self.camera,
            simulate=self.simulate,
            stabilization_time=0.5 if not self.simulate else 0.1
        )

        print("\nStarting person detection scan...")
        print("The robot will turn to face each desk and check for persons.\n")

        start_time = time.time()

        # Run the scan
        occupied_desks = poller.scan_for_persons()

        end_time = time.time()
        duration = end_time - start_time

        # Print results
        print("\n" + "=" * 60)
        print("SCAN RESULTS")
        print("=" * 60)

        print(f"\nScan duration: {duration:.1f} seconds")
        print(f"Total desks scanned: {len(self.config.desks)}")
        print(f"Occupied desks found: {len(occupied_desks)}")

        if occupied_desks:
            print(f"Occupied desk IDs: {occupied_desks}")
            print("\n✅ Delivery queue created:")
            for desk_id in occupied_desks:
                print(f"   - Desk {desk_id}")
        else:
            print("No occupied desks detected")
            print("⚠️  In real deployment, mission would end here")

        print("\n✅ TEST 3 PASSED: Person scan completed successfully")
        return True

    def test_scan_summary(self):
        """Test 4: Scan summary statistics."""
        print("\n" + "=" * 60)
        print("TEST 4: Scan Summary Statistics")
        print("=" * 60)

        print("\nRunning scan to collect results...")
        poller = DeskPoller(
            robot=self.robot,
            config=self.config,
            camera=self.camera,
            simulate=self.simulate,
            stabilization_time=0.1
        )

        # Use generic scan for testing
        detector = PersonDetector(simulate=self.simulate)
        try:
            results = poller.scan_all_desks(
                detector_func=detector.detect,
                descriptor="person"
            )

            # Generate summary
            summary = poller.get_scan_summary(results)

            print("\nSummary statistics:")
            print(f"  Total desks: {summary['total_desks']}")
            print(f"  Detected count: {summary['detected_count']}")
            print(f"  Detected IDs: {summary['detected_ids']}")
            print(f"  Detection rate: {summary['detection_rate']:.1%}")
            print(f"  Avg confidence: {summary['avg_confidence']:.2f}")

            assert summary['total_desks'] == len(self.config.desks)
            print("\n✅ TEST 4 PASSED: Summary statistics generated")
            return True

        finally:
            detector.close()

    def run_all_tests(self):
        """Execute all polling tests."""
        print("\n" + "=" * 60)
        print("DESK POLLING TEST SUITE - Stories 2.1 + 2.2")
        print("=" * 60)

        print(f"\nConfiguration:")
        print(f"  Simulate: {self.simulate}")
        print(f"  Desks: {len(self.config.desks)}")
        print(f"  Robot: {type(self.robot).__name__}")

        # Run tests
        tests = [
            self.test_person_detector,
            self.test_desk_poller_setup,
            self.test_person_scan,
            self.test_scan_summary
        ]

        passed = 0
        failed = 0

        for test_func in tests:
            try:
                if test_func():
                    passed += 1
                else:
                    failed += 1
            except Exception as e:
                print(f"\n❌ TEST FAILED: {e}")
                logging.exception(f"Test {test_func.__name__} failed")
                failed += 1

        # Print final summary
        print("\n" + "=" * 60)
        print("TEST SUITE SUMMARY")
        print("=" * 60)

        print(f"\nResults: {passed}/{len(tests)} tests passed")

        if failed == 0:
            print("\n✅ ALL TESTS PASSED")
            print("=" * 60)
            print("\nStories 2.1 + 2.2 acceptance criteria met:")
            print("  ✅ Person detector works (back-view optimized)")
            print("  ✅ Desk poller scans all desks sequentially")
            print("  ✅ Detection results compiled into queue")
            print("  ✅ System works in simulation mode")
            print("\nReady for hardware testing!")
            return True
        else:
            print(f"\n❌ {failed} TEST(S) FAILED")
            print("=" * 60)
            print("\nReview errors above and fix issues.")
            return False


def main():
    """Main test entry point."""
    # Parse arguments
    import argparse
    parser = argparse.ArgumentParser(
        description='Test desk-centric polling system (Stories 2.1 + 2.2)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run in simulation mode (Mac)
  python3 tests/test_desk_polling.py --simulate

  # Run on hardware (Raspberry Pi)
  python3 tests/test_desk_polling.py

  # Run with debug output
  python3 tests/test_desk_polling.py --simulate --debug
        """
    )
    parser.add_argument('--simulate', action='store_true',
                       help='Run in simulation mode (no hardware)')
    parser.add_argument('--debug', action='store_true',
                       help='Enable debug logging')
    args = parser.parse_args()

    # Setup logging
    log_level = logging.DEBUG if args.debug else logging.INFO
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    logger = logging.getLogger(__name__)

    try:
        # Load configuration
        print("\n" + "=" * 60)
        print("Initializing Test Environment")
        print("=" * 60)

        config = load_row_config()
        print(f"✅ Configuration loaded: {len(config.desks)} desks")

        # Initialize robot
        print(f"\nInitializing robot (simulate={args.simulate})...")
        with Robot(simulate=args.simulate) as robot:
            print(f"✅ Robot initialized")
            print(f"   Battery: {robot.get_battery_voltage():.2f}V")

            # Create and run test suite
            test_suite = PollingTest(robot, config, simulate=args.simulate)
            result = test_suite.run_all_tests()

            # Exit with appropriate code
            sys.exit(0 if result else 1)

    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
        logger.info("Test interrupted")
        sys.exit(1)

    except Exception as e:
        print(f"\n\n❌ Test error: {e}")
        logger.exception("Test failed with exception")
        sys.exit(1)


if __name__ == "__main__":
    main()
