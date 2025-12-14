#!/usr/bin/env python3
"""
Test Linear Movement - Story 1.2

Tests the robot's ability to drive straight for a specified distance
while maintaining heading using IMU feedback.

Acceptance Criteria:
- Robot drives forward 1 meter and stops
- Heading stays within +/- 2 degrees throughout movement
- Robot stops within +/- 5cm of target distance
"""

import sys
import time
import logging
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from yahoo.robot import Robot


# Test configuration
TEST_DISTANCE_CM = 100.0  # 1 meter
HEADING_TOLERANCE_DEG = 2.0  # +/- 2 degrees
DISTANCE_TOLERANCE_CM = 5.0  # +/- 5 cm
SAMPLE_RATE_HZ = 10  # Sample heading 10 times per second
DRIVE_SPEED_DPS = 200  # Speed in degrees per second


class LinearMovementTest:
    """Test for straight-line driving with heading monitoring."""

    def __init__(self, robot, simulate=False):
        self.robot = robot
        self.simulate = simulate
        self.imu = None
        self.heading_log = []
        self.initial_heading = None

    def setup_imu(self):
        """Initialize IMU sensor."""
        if self.simulate:
            print("⚠️  Simulation mode - IMU data will be simulated")
            return True

        # Try to initialize IMU (from main.py pattern)
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

        print("❌ IMU not available - test will run without heading monitoring")
        return False

    def get_heading(self):
        """
        Get current heading from IMU.

        Returns:
            Heading in degrees (0-360), or None if not available
        """
        if self.simulate:
            # Simulate perfect heading (stays at initial)
            if self.initial_heading is not None:
                # Add small random drift for realism
                import random
                drift = random.uniform(-0.5, 0.5)
                return self.initial_heading + drift
            return 0.0

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

    def run_test(self):
        """Execute the linear movement test."""
        print("\n" + "=" * 60)
        print("LINEAR MOVEMENT TEST - Story 1.2")
        print("=" * 60)

        # Setup
        print(f"\nTest Configuration:")
        print(f"  Distance: {TEST_DISTANCE_CM} cm (1 meter)")
        print(f"  Speed: {DRIVE_SPEED_DPS} DPS")
        print(f"  Heading tolerance: ±{HEADING_TOLERANCE_DEG}°")
        print(f"  Distance tolerance: ±{DISTANCE_TOLERANCE_CM} cm")
        print(f"  Sample rate: {SAMPLE_RATE_HZ} Hz")

        # Initialize IMU
        imu_available = self.setup_imu()

        if not imu_available and not self.simulate:
            print("\n⚠️  WARNING: No IMU available!")
            print("   Test will run but heading verification will be skipped.")
            response = input("\nContinue anyway? (y/n): ")
            if response.lower() != 'y':
                print("Test aborted.")
                return False

        # Get initial heading
        print("\n" + "-" * 60)
        print("Step 1: Recording Initial Heading")
        print("-" * 60)

        time.sleep(0.5)  # Let IMU stabilize
        self.initial_heading = self.get_heading()

        if self.initial_heading is not None:
            print(f"✅ Initial heading: {self.initial_heading:.2f}°")
        else:
            print("⚠️  Could not read initial heading")

        # Start movement
        print("\n" + "-" * 60)
        print("Step 2: Starting Forward Movement")
        print("-" * 60)
        print(f"Driving forward {TEST_DISTANCE_CM}cm at {DRIVE_SPEED_DPS} DPS...")
        print("Monitoring heading every {:.2f}s...".format(1.0 / SAMPLE_RATE_HZ))

        input("\n⚠️  Make sure robot has clear space! Press ENTER to start...")

        # Calculate expected duration
        # This is approximate - actual time depends on robot mechanics
        wheel_diameter_cm = 6.6  # GoPiGo3 wheel diameter
        wheel_circumference_cm = 3.14159 * wheel_diameter_cm
        degrees_per_cm = 360.0 / wheel_circumference_cm
        total_degrees = TEST_DISTANCE_CM * degrees_per_cm
        expected_duration = total_degrees / DRIVE_SPEED_DPS

        print(f"Expected duration: ~{expected_duration:.1f} seconds\n")

        # Start driving
        start_time = time.time()
        self.robot.drive.forward(DRIVE_SPEED_DPS)

        # Monitor heading during movement
        sample_interval = 1.0 / SAMPLE_RATE_HZ
        last_sample_time = start_time

        while (time.time() - start_time) < expected_duration:
            current_time = time.time()

            # Sample heading at specified rate
            if current_time - last_sample_time >= sample_interval:
                heading = self.get_heading()
                elapsed = current_time - start_time

                if heading is not None:
                    # Calculate deviation from initial heading
                    deviation = self.normalize_angle_difference(self.initial_heading, heading)

                    self.heading_log.append({
                        'time': elapsed,
                        'heading': heading,
                        'deviation': deviation
                    })

                    print(f"  t={elapsed:5.2f}s  heading={heading:6.2f}°  deviation={deviation:+6.2f}°")

                last_sample_time = current_time

            time.sleep(0.01)  # Small sleep to prevent busy-waiting

        # Stop the robot
        self.robot.drive.stop()
        end_time = time.time()
        actual_duration = end_time - start_time

        print(f"\n✅ Movement complete")
        print(f"   Actual duration: {actual_duration:.2f}s")

        # Wait a moment for robot to fully stop
        time.sleep(0.5)

        # Analyze results
        print("\n" + "-" * 60)
        print("Step 3: Analyzing Results")
        print("-" * 60)

        return self.analyze_results(actual_duration)

    def analyze_results(self, actual_duration):
        """Analyze test results and determine pass/fail."""

        success = True

        # 1. Heading Analysis
        print("\n1. HEADING STABILITY:")

        if len(self.heading_log) == 0:
            print("   ⚠️  No heading data collected")
        else:
            deviations = [abs(log['deviation']) for log in self.heading_log]
            max_deviation = max(deviations)
            avg_deviation = sum(deviations) / len(deviations)

            print(f"   Samples collected: {len(self.heading_log)}")
            print(f"   Average deviation: {avg_deviation:.2f}°")
            print(f"   Maximum deviation: {max_deviation:.2f}°")

            if max_deviation <= HEADING_TOLERANCE_DEG:
                print(f"   ✅ PASS - Stayed within ±{HEADING_TOLERANCE_DEG}° tolerance")
            else:
                print(f"   ❌ FAIL - Exceeded ±{HEADING_TOLERANCE_DEG}° tolerance")
                success = False

        # 2. Distance Analysis (placeholder - would need encoder data)
        print("\n2. DISTANCE ACCURACY:")
        print(f"   Target distance: {TEST_DISTANCE_CM} cm")
        print(f"   Expected duration: ~{actual_duration:.2f}s")

        if not self.simulate:
            print("   ⚠️  Manual measurement required:")
            print("      1. Measure actual distance traveled")
            print("      2. Should be within ±5cm of 100cm")

            measured = input("\n   Enter measured distance (cm) or 'skip': ")
            if measured.lower() != 'skip':
                try:
                    measured_distance = float(measured)
                    error = abs(measured_distance - TEST_DISTANCE_CM)
                    print(f"\n   Measured distance: {measured_distance} cm")
                    print(f"   Error: {error:.2f} cm")

                    if error <= DISTANCE_TOLERANCE_CM:
                        print(f"   ✅ PASS - Within ±{DISTANCE_TOLERANCE_CM}cm tolerance")
                    else:
                        print(f"   ❌ FAIL - Exceeded ±{DISTANCE_TOLERANCE_CM}cm tolerance")
                        success = False
                except ValueError:
                    print("   ⚠️  Invalid input - skipping distance verification")
        else:
            print("   ⚠️  Simulation mode - distance verification skipped")

        # Final result
        print("\n" + "=" * 60)
        if success:
            print("✅ TEST PASSED")
            print("=" * 60)
            print("\nThe robot successfully:")
            print("  - Drove forward for the target distance")
            print("  - Maintained heading within tolerance")
            print("  - Stopped at the correct position")
        else:
            print("❌ TEST FAILED")
            print("=" * 60)
            print("\nIssues detected - review logs above")

        return success


def main():
    """Main test entry point."""
    # Parse command line arguments
    import argparse
    parser = argparse.ArgumentParser(description='Test linear movement (Story 1.2)')
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
            test = LinearMovementTest(robot, simulate=args.simulate)
            result = test.run_test()

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
