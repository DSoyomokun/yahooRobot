#!/usr/bin/env python3
"""
Delivery Mission - Story 3.1 (Combined)

Delivers papers to specified desks using the traversal pattern.

- Prompts user to enter which desks are EMPTY.
- Navigates to all OTHER desks (the occupied ones).
- At each occupied desk, it turns left, waits for user confirmation, and turns right.
- Skips the specified empty desks to save time.
"""

import sys
import time
import logging
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from yahoo.robot import Robot
from yahoo.config.row_loader import load_row_config

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DeliveryMission:
    """Handles paper delivery to specified desks."""

    def __init__(self, robot, config, simulate=False):
        self.robot = robot
        self.config = config
        self.desks = sorted(config.desks, key=lambda d: d.id)
        self.delivered_count = 0
        self.simulate = simulate
        self.imu = None
        
        # Initialize IMU if available
        if not simulate and robot.gpg:
            self._init_imu()
    
    def _init_imu(self):
        """Initialize IMU sensor for turn verification."""
        logger.info("Attempting to initialize IMU sensor...")
        
        # Method 1: Try di_sensors library
        try:
            from di_sensors.inertial_measurement_unit import InertialMeasurementUnit
            logger.info("  Trying di_sensors library...")
            for bus_name in ["GPG3_AD1", "GPG3_AD2", "RPI_1"]:
                try:
                    self.imu = InertialMeasurementUnit(bus=bus_name)
                    test_read = self.imu.read_euler()
                    logger.info(f"✅ IMU initialized via di_sensors on bus: {bus_name}")
                    return
                except Exception:
                    continue
        except ImportError:
            logger.debug("  di_sensors library not available")
        except Exception as e:
            logger.debug(f"  di_sensors method failed: {e}")
        
        # Method 2: Try easygopigo3 init_imu()
        if self.imu is None:
            try:
                if hasattr(self.robot.gpg, 'init_imu'):
                    self.imu = self.robot.gpg.init_imu()
                    logger.info("✅ IMU initialized via init_imu()")
                    return
            except Exception:
                pass
        
        # Method 3: Try direct access
        if self.imu is None:
            try:
                if hasattr(self.robot.gpg, 'imu'):
                    self.imu = self.robot.gpg.imu
                    logger.info("✅ IMU accessed via gpg.imu")
                    return
            except Exception:
                pass
        
        if self.imu is None:
            logger.warning("⚠️  IMU not available - turns will use encoder-based method only")
    
    def get_heading(self):
        """Get current heading from IMU if available."""
        if self.imu is not None:
            try:
                euler = self.imu.read_euler()
                if isinstance(euler, (list, tuple)) and len(euler) >= 3:
                    return float(euler[2])  # Yaw angle
                elif isinstance(euler, dict):
                    return float(euler.get('yaw', euler.get('heading', euler.get('z', 0))))
            except Exception as e:
                logger.debug(f"IMU read error: {e}")
        return None
    
    def turn_with_imu_verification(self, degrees, direction_name="turn"):
        """
        Turn using encoder-based method with IMU verification and auto-correction.
        
        Args:
            degrees: Degrees to turn (positive = right, negative = left)
            direction_name: Description for logging
        """
        if self.simulate:
            logger.info(f"   [SIMULATED] robot.drive.turn_degrees({degrees})")
            return
        
        # Get initial heading if IMU available
        initial_heading = self.get_heading()
        if initial_heading is not None:
            logger.debug(f"  Initial heading: {initial_heading:.1f}°")
        
        # Perform encoder-based turn
        try:
            self.robot.drive.turn_degrees(degrees)
            time.sleep(0.3)  # Brief pause for IMU to stabilize
            
            # Verify with IMU and correct if needed
            if initial_heading is not None:
                final_heading = self.get_heading()
                if final_heading is not None:
                    expected_heading = (initial_heading + degrees) % 360
                    error = (expected_heading - final_heading) % 360
                    if error > 180:
                        error -= 360
                    
                    logger.info(f"  📊 Turn verified: {final_heading:.1f}° (expected: {expected_heading:.1f}°, error: {error:.1f}°)")
                    
                    # Auto-correct if error is significant (more than 2 degrees)
                    if abs(error) > 2.0:
                        correction_degrees = -error  # Negative error means we need to turn more
                        logger.info(f"  🔧 Correcting turn by {correction_degrees:.1f}° to reach target...")
                        self.robot.drive.turn_degrees(correction_degrees)
                        time.sleep(0.3)  # Brief pause for IMU to stabilize
                        
                        # Verify correction
                        corrected_heading = self.get_heading()
                        if corrected_heading is not None:
                            corrected_error = (expected_heading - corrected_heading) % 360
                            if corrected_error > 180:
                                corrected_error -= 360
                            logger.info(f"  ✅ Turn corrected: {corrected_heading:.1f}° (expected: {expected_heading:.1f}°, error: {corrected_error:.1f}°)")
                    else:
                        logger.info(f"  ✅ Turn accurate (error < 2°)")
            else:
                # No IMU available, just do the turn
                logger.debug(f"  Turn completed (no IMU verification available)")
        except Exception as e:
            logger.error(f"  ❌ Turn failed: {e}")
            # Fallback to timed turn if encoder fails
            logger.warning(f"  Falling back to timed turn...")
            if degrees < 0:
                self.robot.drive.turn_left_timed(abs(degrees) / 90.0 * 1.5)
            else:
                self.robot.drive.turn_right_timed(abs(degrees) / 90.0 * 1.5)

    def get_desks_to_visit(self):
        """
        Asks user for OCCUPIED desks and returns a list of desks to visit.
        """
        logger.info("=" * 60)
        logger.info("📍 DESK OCCUPANCY CHECK")
        logger.info("=" * 60)
        logger.info("\nEnter which desks are OCCUPIED (where students are present).")
        logger.info("Example: 1,3,4 (visits Desks 1, 3, and 4)")
        logger.info("Press ENTER if no desks are occupied (mission will be aborted).")

        while True:
            response = input("\nEnter OCCUPIED desks to visit (comma-separated, e.g., 1,3,4): ").strip()

            occupied_ids = []
            if response:
                try:
                    occupied_ids = [int(x.strip()) for x in response.split(',')]
                except ValueError:
                    logger.warning("Invalid format. Please use comma-separated numbers (e.g., 1,3,4).")
                    continue

            all_desk_ids = [d.id for d in self.desks]
            invalid_ids = [d_id for d_id in occupied_ids if d_id not in all_desk_ids]

            if invalid_ids:
                logger.warning(f"Invalid desk IDs: {invalid_ids}. Valid IDs are: {all_desk_ids}")
                continue

            logger.info(f"\n✅ Desks to visit (occupied): {sorted(occupied_ids)}")
            return sorted(occupied_ids)

    def run(self):
        """
        Execute the delivery mission.
        """
        logger.info("=" * 60)
        logger.info("📦 DELIVERY MISSION")
        logger.info("=" * 60)

        occupied_desk_ids = self.get_desks_to_visit()
        if not occupied_desk_ids:
            logger.info("\nNo desks to visit. Mission aborted.")
            return

        desks_to_visit = [d for d in self.desks if d.id in occupied_desk_ids]

        logger.info(f"\n🤖 STARTING DELIVERY")
        logger.info(f"   Position: At Desk 1")
        logger.info(f"   Desks to visit: {[d.id for d in desks_to_visit]}")

        # HARDCODED DISTANCES (TESTING: 25cm between all desks for this room)
        distances = {
            1: 0,    # Already at Desk 1
            2: 25,   # Desk 1 → Desk 2 (25 cm for testing)
            3: 25,   # Desk 2 → Desk 3 (25 cm for testing)
            4: 25    # Desk 3 → Desk 4 (25 cm for testing)
        }

        # Calculate total forward distance for return trip
        total_forward_distance = 0
        for i in range(len(desks_to_visit) - 1):
            current_desk = desks_to_visit[i].id
            next_desk = desks_to_visit[i + 1].id
            # Sum distances between consecutive desks
            for desk_id in range(current_desk, next_desk):
                if desk_id + 1 in distances:
                    total_forward_distance += distances[desk_id + 1]

        # Visit each desk
        for i, desk in enumerate(desks_to_visit):
            logger.info(f"\n{'='*60}")
            logger.info(f"AT DESK {desk.id} (#{i+1}/{len(desks_to_visit)})")
            logger.info(f"{'='*60}")

            # Prompt to press ENTER
            input(f"\n⚠️  Press ENTER at Desk {desk.id}...")

            # Turn LEFT 90° to face desk (using encoder with IMU verification)
            logger.info(f"\n↰  Turning LEFT 90° to face Desk {desk.id}...")
            self.turn_with_imu_verification(-90, "left")

            # Wait 3 seconds
            logger.info(f"\n⏱️  Waiting 3 seconds at Desk {desk.id}...")
            time.sleep(3.0)

            # Turn LEFT 345° back to straight
            logger.info(f"\n↰  Turning LEFT 345° back to straight...")
            self.turn_with_imu_verification(-345, "left")

            # If not last desk, drive forward to next desk
            if i < len(desks_to_visit) - 1:
                next_desk = desks_to_visit[i + 1]
                # Calculate distance to next desk
                distance_to_next = 0
                for desk_id in range(desk.id, next_desk.id):
                    if desk_id + 1 in distances:
                        distance_to_next += distances[desk_id + 1]
                
                logger.info(f"\n🚗 Driving {distance_to_next} cm to Desk {next_desk.id}...")
                if self.simulate:
                    logger.info(f"   [SIMULATED] robot.drive.drive_cm({distance_to_next})")
                else:
                    self.robot.drive.drive_cm(distance_to_next)
                logger.info(f"✅ Arrived at Desk {next_desk.id} position")

        # At last desk - final action
        logger.info("\n" + "=" * 60)
        logger.info("FINAL ACTION AT LAST DESK")
        logger.info("=" * 60)
        input(f"\n⚠️  Press ENTER for final action at Desk {desks_to_visit[-1].id}...")

        # Turn 215° (using left turn since right turns don't work)
        logger.info(f"\n↻  Turning LEFT 215°...")
        self.turn_with_imu_verification(-215, "left 215°")

        # Drive forward 100cm
        logger.info(f"\n🚗 Driving forward 100 cm...")
        if self.simulate:
            logger.info(f"   [SIMULATED] robot.drive.drive_cm(100)")
        else:
            self.robot.drive.drive_cm(100)  # Positive = forward
        logger.info(f"✅ Drove forward 100 cm")
        
        # Turn 215° again
        logger.info(f"\n↻  Turning LEFT 215° again...")
        self.turn_with_imu_verification(-215, "left 215°")
        logger.info(f"✅ Final turn complete")

        logger.info("\n" + "=" * 60)
        logger.info("✅ DELIVERY MISSION COMPLETE!")
        logger.info("=" * 60)
        logger.info(f"\n📊 STATISTICS:")
        logger.info(f"   Total desks: {len(self.desks)}")
        logger.info(f"   Occupied desks: {len(occupied_desk_ids)}")
        logger.info(f"   Desks visited: {len(desks_to_visit)}")
        logger.info(f"   Total forward distance: {total_forward_distance} cm")
        logger.info(f"   Final forward movement: 100 cm")


def main():
    """Main entry point."""
    import argparse
    parser = argparse.ArgumentParser(
        description='Execute a delivery mission to specified desks.',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument('--simulate', action='store_true',
                        help='Run in simulation mode (no hardware required).')
    parser.add_argument('--debug', action='store_true',
                        help='Enable debug logging.')
    args = parser.parse_args()

    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)

    logger.info("Initializing robot...")
    try:
        with Robot(simulate=args.simulate) as robot:
            logger.info(f"✅ Robot initialized (simulate={args.simulate})")
            if not args.simulate:
                logger.info(f"   Battery: {robot.get_battery_voltage():.2f}V")

            config = load_row_config()
            logger.info(f"✅ Config loaded: {len(config.desks)} desks")

            mission = DeliveryMission(robot, config, simulate=args.simulate)
            mission.run()

    except KeyboardInterrupt:
        logger.warning("\n\nMission interrupted by user.")
        sys.exit(1)
    except Exception as e:
        logger.error(f"\n\nAn error occurred: {e}")
        logging.exception("Mission failed")
        sys.exit(1)


if __name__ == "__main__":
    main()