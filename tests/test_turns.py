#!/usr/bin/env python3
"""
Test Precise Turns - Story 1.3

Tests the robot's ability to perform accurate in-place turns using IMU feedback.

Acceptance Criteria:
- Robot executes 90° right turn within ±3° tolerance
- Robot executes 90° left turn within ±3° tolerance
- Robot executes 180° turn within ±3° tolerance
- Test reports SUCCESS/FAILURE for each turn type
"""

import sys
import time
import logging
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from yahoo.robot import Robot


# Test configuration
TURN_TOLERANCE_DEG = 3.0  # ±3 degrees
STABILIZATION_TIME = 1.0  # Wait for IMU to stabilize after turn


class TurnTest:
    """Test for precise turning with IMU validation."""

    def __init__(self, robot, simulate=False):
        self.robot = robot
        self.simulate = simulate
        self.imu = None
        self.test_results = []

    def setup_imu(self):
        """Initialize IMU sensor."""
        if self.simulate:
            print("⚠️  Simulation mode - IMU data will be simulated")
            return True

        # Try to initialize IMU (from test_linear_movement.py pattern)
        print("Initializing IMU sensor...")

        # Method 1: Try di_sensors library
        try:
            from di_sensors.inertial_measurement_unit import InertialMeasurementUnit
            for bus_name in ["GPG3_AD1", "GPG3_AD2", "RPI_1"]:
                try:
                    self.imu = InertialMeasurementUnit(bus=bus_name)
                    test_read = self.imu.read_euler()
                    print(f"✅ IMU initialized on bus: {bus_name}")
                    return True
                except Exception:
                    continue
        except ImportError:
            pass

        # Method 2: Try easygopigo3 init_imu()
        if self.robot.gpg and hasattr(self.robot.gpg, 'init_imu'):
            try:
                self.imu = self.robot.gpg.init_imu()
                print("✅ IMU initialized via init_imu()")
                return True
            except Exception:
                pass

        # Method 3: Try direct access
        if self.robot.gpg and hasattr(self.robot.gpg, 'imu'):
            try:
                self.imu = self.robot.gpg.imu
                print("✅ IMU accessed via gpg.imu")
                return True
            except Exception:
                pass

        print("❌ IMU not available - test cannot run without heading feedback")
        return False

    def get_heading(self):
        """
        Get current heading from IMU.

        Returns:
            Heading in degrees (0-360), or None if not available
        """
        if self.simulate:
            # In simulation, return a simulated heading
            # This will be updated by turn commands
            if not hasattr(self, '_sim_heading'):
                self._sim_heading = 0.0
            return self._sim_heading

        if self.imu is None:
            return None

        try:
            euler = self.imu.read_euler()
            # Handle different return formats
            if isinstance(euler, (list, tuple)) and len(euler) >= 3:
                heading = float(euler[2])  # Yaw/heading is typically index 2
            elif isinstance(euler, dict):
                heading = float(euler.get('yaw', euler.get('heading', euler.get('z', 0))))
            else:
                return None

            # Normalize to 0-360
            heading = heading % 360
            return heading
        except Exception as e:
            logging.debug(f"IMU read error: {e}")
            return None

    def normalize_angle_difference(self, angle1, angle2):
        """
        Calculate the shortest angle difference between two headings.

        Args:
            angle1, angle2: Angles in degrees (0-360)

        Returns:
            Difference in degrees (-180 to 180)
        """
        diff = angle2 - angle1

        # Normalize to -180 to 180
        while diff > 180:
            diff -= 360
        while diff < -180:
            diff += 360

        return diff

    def test_turn(self, degrees, description):
        """
        Execute a turn and validate the result.

        Args:
            degrees: Angle to turn (positive = right, negative = left)
            description: Human-readable description for logging

        Returns:
            True if turn was within tolerance, False otherwise
        """
        print("\n" + "=" * 60)
        print(f"Test: {description}")
        print("=" * 60)

        # Get initial heading
        time.sleep(STABILIZATION_TIME)
        initial_heading = self.get_heading()

        if initial_heading is None:
            print("❌ ERROR: Could not read initial heading")
            return False

        print(f"\nInitial heading: {initial_heading:.2f}°")
        print(f"Commanded turn: {degrees:+.1f}°")

        # Calculate expected final heading
        expected_heading = (initial_heading + degrees) % 360
        print(f"Expected final heading: {expected_heading:.2f}°")

        # Confirm start
        if not self.simulate:
            input("\n⚠️  Press ENTER to execute turn (make sure robot has space)...")

        # Execute turn
        print(f"\nExecuting turn...")
        start_time = time.time()
        self.robot.drive.turn_degrees(degrees)
        end_time = time.time()

        # Update simulated heading if in simulation mode
        if self.simulate:
            self._sim_heading = expected_heading

        # Wait for stabilization
        time.sleep(STABILIZATION_TIME)

        # Get final heading
        final_heading = self.get_heading()

        if final_heading is None:
            print("❌ ERROR: Could not read final heading")
            return False

        print(f"Final heading: {final_heading:.2f}°")
        print(f"Turn duration: {end_time - start_time:.2f}s")

        # Calculate error
        # We want the shortest angle between expected and actual
        error = self.normalize_angle_difference(expected_heading, final_heading)
        abs_error = abs(error)

        print(f"\nHeading error: {error:+.2f}° (absolute: {abs_error:.2f}°)")
        print(f"Tolerance: ±{TURN_TOLERANCE_DEG}°")

        # Determine pass/fail
        passed = abs_error <= TURN_TOLERANCE_DEG

        if passed:
            print(f"\n✅ SUCCESS - Turn within tolerance")
        else:
            print(f"\n❌ FAILURE - Turn exceeded tolerance")
            print(f"   Overshoot by: {abs_error - TURN_TOLERANCE_DEG:.2f}°")

        # Record result
        self.test_results.append({
            'description': description,
            'commanded': degrees,
            'initial': initial_heading,
            'expected': expected_heading,
            'final': final_heading,
            'error': error,
            'abs_error': abs_error,
            'passed': passed
        })

        return passed

    def run_all_tests(self):
        """Execute all turn tests."""
        print("\n" + "=" * 60)
        print("PRECISE TURN TEST - Story 1.3")
        print("=" * 60)

        print(f"\nTest Configuration:")
        print(f"  Turn tolerance: ±{TURN_TOLERANCE_DEG}°")
        print(f"  Stabilization time: {STABILIZATION_TIME}s")

        # Initialize IMU
        print(f"\n" + "-" * 60)
        print("IMU Initialization")
        print("-" * 60)

        imu_available = self.setup_imu()

        if not imu_available:
            print("\n❌ ABORT: IMU required for turn testing")
            return False

        # Reset heading reference in simulation
        if self.simulate:
            self._sim_heading = 0.0

        # Run tests
        print(f"\n" + "-" * 60)
        print("Executing Turn Tests")
        print("-" * 60)

        # Test 1: 90° right turn
        test1 = self.test_turn(90.0, "90° Right Turn")

        # Test 2: 90° left turn
        test2 = self.test_turn(-90.0, "90° Left Turn")

        # Test 3: 180° turn
        test3 = self.test_turn(180.0, "180° Turn")

        # Print summary
        self.print_summary()

        # Return overall pass/fail
        return test1 and test2 and test3

    def print_summary(self):
        """Print test summary."""
        print("\n" + "=" * 60)
        print("TEST SUMMARY")
        print("=" * 60)

        passed_count = sum(1 for r in self.test_results if r['passed'])
        total_count = len(self.test_results)

        print(f"\nResults: {passed_count}/{total_count} tests passed\n")

        for i, result in enumerate(self.test_results, 1):
            status = "✅ PASS" if result['passed'] else "❌ FAIL"
            print(f"{i}. {result['description']}: {status}")
            print(f"   Commanded: {result['commanded']:+.1f}°")
            print(f"   Error: {result['error']:+.2f}° (tolerance: ±{TURN_TOLERANCE_DEG}°)")

        # Overall result
        print("\n" + "=" * 60)
        if passed_count == total_count:
            print("✅ ALL TESTS PASSED")
            print("=" * 60)
            print("\nThe robot successfully:")
            print("  - Executes 90° right turns within ±3° tolerance")
            print("  - Executes 90° left turns within ±3° tolerance")
            print("  - Executes 180° turns within ±3° tolerance")
            print("\n✅ Story 1.3 acceptance criteria met!")
        else:
            print("❌ SOME TESTS FAILED")
            print("=" * 60)
            print("\nIssues detected:")
            for result in self.test_results:
                if not result['passed']:
                    print(f"  - {result['description']}: error {result['error']:+.2f}°")
            print("\nConsider:")
            print("  - Calibrating IMU")
            print("  - Adjusting turn speed or motor calibration")
            print("  - Checking for mechanical issues (wheel slip, etc.)")


def main():
    """Main test entry point."""
    # Parse command line arguments
    import argparse
    parser = argparse.ArgumentParser(description='Test precise turns (Story 1.3)')
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

    # Initialize robot
    print("\n" + "=" * 60)
    print("Initializing Robot...")
    print("=" * 60)

    try:
        with Robot(simulate=args.simulate) as robot:
            print(f"✅ Robot initialized (simulate={args.simulate})")
            print(f"   Battery: {robot.get_battery_voltage():.2f}V")

            # Create and run test
            test = TurnTest(robot, simulate=args.simulate)
            result = test.run_all_tests()

            # Return appropriate exit code
            sys.exit(0 if result else 1)

    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Test error: {e}")
        logging.exception("Test failed with exception")
        sys.exit(1)


if __name__ == "__main__":
    main()
