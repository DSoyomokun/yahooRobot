#!/usr/bin/env python3
"""
Delivery Mission - Story 3.1

Delivers papers to occupied desks.

CURRENT IMPLEMENTATION (Manual Mode - Default):
- Prompts user to enter which desks are occupied
- Navigates only to those desks
- Skips empty desks (saves time)
- Waits for ENTER confirmation at each desk

FUTURE IMPLEMENTATION (Automated Mode):
- Use desk-centric polling to scan all desks
- Person detector identifies occupied desks automatically
- No manual input needed
- Same navigation and delivery workflow

Why Manual Mode First:
- Faster to implement for deadline
- Allows testing full mission workflow
- Detection code already exists in yahoo/sense/person_detector.py
- Easy to switch with --manual/--auto flag later

Future Integration Steps (see code comments marked FUTURE):
1. Remove --manual default, add --auto flag
2. Uncomment automated polling code
3. Test person detection accuracy
4. Switch default to automated mode
"""

import sys
import time
import logging
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from yahoo.robot import Robot
from yahoo.config.row_loader import load_row_config

# FUTURE: Uncomment when switching to automated mode
# from yahoo.sense.person_detector import PersonDetector
# from yahoo.mission.desk_poller import DeskPoller

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DeliveryMission:
    """Handles paper delivery to occupied desks."""

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
        Turn using encoder-based method with IMU verification (no auto-correction).
        
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
            
            # Verify with IMU (log only, no correction to avoid overcompensation)
            if initial_heading is not None:
                final_heading = self.get_heading()
                if final_heading is not None:
                    expected_heading = (initial_heading + degrees) % 360
                    error = (expected_heading - final_heading) % 360
                    if error > 180:
                        error -= 360
                    logger.info(f"  ✅ Turn verified: {final_heading:.1f}° (expected: {expected_heading:.1f}°, error: {error:.1f}°)")
        except Exception as e:
            logger.error(f"  ❌ Turn failed: {e}")
            # Fallback to timed turn if encoder fails
            logger.warning(f"  Falling back to timed turn...")
            if degrees < 0:
                self.robot.drive.turn_left_timed(abs(degrees) / 90.0 * 1.5)
            else:
                self.robot.drive.turn_right_timed(abs(degrees) / 90.0 * 1.5)

    def get_occupied_desks(self, manual=True):
        """
        Get list of occupied desk IDs.

        Args:
            manual: If True, prompt for manual input. If False, use automated detection.

        Returns:
            List of desk IDs (e.g., [1, 2, 4])
        """
        if manual:
            # MANUAL MODE: Terminal input
            logger.info("=" * 60)
            logger.info("📍 DESK OCCUPANCY CHECK")
            logger.info("=" * 60)
            logger.info("\nManual mode: Enter which desks have students")
            logger.info("Example: 1,2,4 (means Desks 1, 2, and 4 are occupied)")
            logger.info("This allows skipping empty desks to save time")

            while True:
                response = input("\nEnter occupied desks (comma-separated, e.g., 1,2,4): ").strip()

                if not response:
                    logger.warning("No desks entered. Try again or press Ctrl+C to exit.")
                    continue

                try:
                    occupied = [int(x.strip()) for x in response.split(',')]
                    # Validate desk IDs
                    valid_ids = [d.id for d in self.desks]
                    invalid = [d for d in occupied if d not in valid_ids]

                    if invalid:
                        logger.warning(f"Invalid desk IDs: {invalid}. Valid IDs are: {valid_ids}")
                        continue

                    logger.info(f"\n✅ Occupied desks: {occupied}")
                    logger.info(f"   Will deliver to {len(occupied)} desk(s)")
                    logger.info(f"   Skipping {len(self.desks) - len(occupied)} empty desk(s)")
                    return sorted(occupied)

                except ValueError:
                    logger.warning("Invalid format. Use comma-separated numbers (e.g., 1,2,4)")
                    continue

        else:
            # FUTURE: AUTOMATED MODE using person detection + polling
            logger.info("=" * 60)
            logger.info("📍 AUTOMATED DESK SCANNING")
            logger.info("=" * 60)
            logger.info("\nScanning all desks for students...")

            # FUTURE: Uncomment this code when ready for automated mode
            # poller = DeskPoller(
            #     robot=self.robot,
            #     config=self.config,
            #     camera=None,  # Add camera when ready
            #     simulate=False
            # )
            # occupied = poller.scan_for_persons()
            # logger.info(f"\n✅ Found students at desks: {occupied}")
            # return occupied

            # Placeholder for now
            raise NotImplementedError(
                "Automated mode not yet implemented. Use --manual flag."
            )

    def deliver_to_desk(self, desk):
        """
        Deliver paper to a single desk.

        Args:
            desk: Desk object
        """
        logger.info(f"\n📄 DELIVERING TO DESK {desk.id}")
        logger.info(f"   Waiting for student to take paper...")

        # Wait for confirmation (simulates button press)
        input(f"   Press ENTER when student at Desk {desk.id} takes paper...")

        logger.info(f"   ✅ Paper delivered to Desk {desk.id}")
        self.delivered_count += 1

    def run(self, limit_desks=None, manual=True):
        """
        Execute delivery mission.

        Args:
            limit_desks: If set, only visit first N desks (for testing)
            manual: If True, use manual input. If False, use automated detection.
        """
        logger.info("=" * 60)
        logger.info("📦 DELIVERY MISSION - Story 3.1")
        if self.simulate:
            logger.info("⚠️  SIMULATION MODE - No hardware required")
        logger.info("=" * 60)
        logger.info(f"\n📦 PHASE: PAPER DELIVERY (Passing Out)")
        logger.info(f"Goal: Deliver papers to occupied desks only")
        logger.info(f"\nMode: {'MANUAL' if manual else 'AUTOMATED'}")

        # Get occupied desks
        occupied_desk_ids = self.get_occupied_desks(manual=manual)

        if not occupied_desk_ids:
            logger.info("\n⚠️  No occupied desks. Mission complete.")
            return

        # Get desk objects for occupied desks
        desks_to_visit = [d for d in self.desks if d.id in occupied_desk_ids]

        # Limit desks if in debug mode
        if limit_desks:
            desks_to_visit = desks_to_visit[:limit_desks]
            logger.info(f"\n⚠️  DEBUG: Limited to first {limit_desks} desk(s)")

        logger.info(f"\n🤖 STARTING DELIVERY")
        logger.info(f"   Position: At Desk 1")
        logger.info(f"   Desks to visit: {[d.id for d in desks_to_visit]}")
        logger.info(f"   Papers to deliver: {len(desks_to_visit)}")

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

        # Turn 230° (using left turn since right turns don't work)
        logger.info(f"\n↻  Turning LEFT 230°...")
        self.turn_with_imu_verification(-230, "left 230°")

        # Drive forward 100cm
        logger.info(f"\n🚗 Driving forward 100 cm...")
        if self.simulate:
            logger.info(f"   [SIMULATED] robot.drive.drive_cm(100)")
        else:
            self.robot.drive.drive_cm(100)  # Positive = forward
        logger.info(f"✅ Drove forward 100 cm")
        
        # Turn 230° again
        logger.info(f"\n↻  Turning LEFT 230° again...")
        self.turn_with_imu_verification(-230, "left 230°")
        logger.info(f"✅ Final turn complete")

        # Mission complete
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
        description='Execute delivery mission (Story 3.1)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Manual mode - enter occupied desks at prompt
  python3 scripts/run_delivery_mission.py --manual

  # Debug: Only visit first 2 occupied desks
  python3 scripts/run_delivery_mission.py --manual --limit-desks 2

  # Future: Automated mode with person detection
  python3 scripts/run_delivery_mission.py --auto

Setup:
  Position robot in front of Desk 1, facing along the row

Manual Mode (Current):
  - Prompts for occupied desk IDs
  - Fast for testing and demos
  - No camera/detection needed

Automated Mode (Future):
  - Uses person detection + polling
  - Automatically identifies occupied desks
  - Requires camera and detection code
        """
    )
    parser.add_argument('--manual', action='store_true', default=True,
                       help='Manual input mode (default)')
    parser.add_argument('--auto', action='store_true',
                       help='Automated detection mode (future)')
    parser.add_argument('--simulate', action='store_true',
                       help='Run in simulation mode (no hardware required)')
    parser.add_argument('--limit-desks', type=int, metavar='N',
                       help='Only visit first N occupied desks (for testing)')
    parser.add_argument('--debug', action='store_true',
                       help='Enable debug logging')
    args = parser.parse_args()

    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)

    # Determine mode
    manual_mode = not args.auto

    logger.info("Initializing robot...")
    try:
        with Robot(simulate=args.simulate) as robot:
            logger.info(f"✅ Robot initialized (simulate={args.simulate})")
            logger.info(f"   Battery: {robot.get_battery_voltage():.2f}V")

            config = load_row_config()
            logger.info(f"✅ Config loaded: {len(config.desks)} desks")

            mission = DeliveryMission(robot, config, simulate=args.simulate)
            mission.run(limit_desks=args.limit_desks, manual=manual_mode)

    except KeyboardInterrupt:
        logger.warning("\n\nMission interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"\n\nMission error: {e}")
        logging.exception("Mission failed")
        sys.exit(1)


if __name__ == "__main__":
    main()
