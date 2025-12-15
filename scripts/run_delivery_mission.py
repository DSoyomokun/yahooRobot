#!/usr/bin/env python3
"""
Delivery Mission - Story 3.1 (Combined)

Delivers papers to specified desks using the traversal pattern.

- Prompts user to enter which desks are occupied.
- Navigates to ONLY those desks.
- At each desk, it turns left, pauses, and turns right.
- Skips empty desks to save time.
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

    def get_occupied_desks(self):
        """
        Get list of occupied desk IDs from user input.
        """
        logger.info("=" * 60)
        logger.info("📍 DESK OCCUPANCY CHECK")
        logger.info("=" * 60)
        logger.info("\nEnter which desks the robot should visit.")
        logger.info("Example: 1,3,4 (visits Desks 1, 3, and 4)")

        while True:
            response = input("\nEnter desks to visit (comma-separated, e.g., 1,3,4): ").strip()

            if not response:
                logger.warning("No desks entered. Please provide a list of desks to visit.")
                continue

            try:
                occupied_ids = [int(x.strip()) for x in response.split(',')]
                valid_ids = [d.id for d in self.desks]
                invalid = [d_id for d_id in occupied_ids if d_id not in valid_ids]

                if invalid:
                    logger.warning(f"Invalid desk IDs: {invalid}. Valid IDs are: {valid_ids}")
                    continue

                logger.info(f"\n✅ Desks to visit: {occupied_ids}")
                return sorted(occupied_ids)

            except ValueError:
                logger.warning("Invalid format. Please use comma-separated numbers (e.g., 1,3,4).")
                continue

    def run(self, pause_after_each=False):
        """
        Execute the delivery mission.
        """
        logger.info("=" * 60)
        logger.info("📦 DELIVERY MISSION (TRAVERSAL-STYLE)")
        logger.info("=" * 60)

        # Get the list of desks to visit from the user
        occupied_desk_ids = self.get_occupied_desks()
        if not occupied_desk_ids:
            logger.info("\nNo desks selected. Mission aborted.")
            return

        desks_to_visit = [d for d in self.desks if d.id in occupied_desk_ids]

        # HARDCODED DISTANCES (from row traversal script)
        distances = {
            1: 0,
            2: 104,
            3: 238,
            4: 104
        }

        logger.info(f"\n🤖 STARTING DELIVERY")
        logger.info(f"   Position: In front of Desk 1")
        logger.info(f"   Desks to visit: {[d.id for d in desks_to_visit]}")
        logger.info(f"\n🔄 MOVEMENT PATTERN:")
        logger.info(f"   1. Turn LEFT 90° to face desk")
        logger.info(f"   2. Pause for delivery")
        logger.info(f"   3. Turn RIGHT 90° back to straight")
        logger.info(f"   4. Drive to next desk position")

        input("\n⚠️  Press ENTER to start delivery...")

        current_desk_pos = 1
        for i, desk in enumerate(desks_to_visit):
            logger.info(f"\n{'='*60}")
            logger.info(f"VISITING DESK {desk.id} (#{i+1}/{len(desks_to_visit)})")
            logger.info(f"{'='*60}")

            # Drive to the desk's position
            distance_to_drive = 0
            if desk.id > current_desk_pos:
                # This is a simplified drive model assuming sequential travel
                # A more robust solution would calculate path segments
                distance_to_drive = distances.get(desk.id, 0)

            if distance_to_drive > 1.0:
                logger.info(f"\n📏 Driving from {current_desk_pos} to {desk.id}")
                logger.info(f"🚗 Driving {distance_to_drive} cm...")
                self.robot.drive.drive_cm(distance_to_drive)
                logger.info(f"✅ Arrived at Desk {desk.id} position")
            else:
                logger.info(f"\n✅ Already at Desk {desk.id} position")

            # Update current position
            current_desk_pos = desk.id

            # Perform the traversal-style interaction
            logger.info(f"\n↰  Turning LEFT 90° to face Desk {desk.id}...")
            self.robot.drive.turn_degrees(-90)
            time.sleep(0.5)

            logger.info(f"\n📍 AT DESK {desk.id}")
            logger.info(f"   Facing the desk - ready for delivery.")

            if pause_after_each:
                input(f"\n📄 Press ENTER after delivery at Desk {desk.id}...")
            else:
                logger.info(f"   📄 Pausing for 2 seconds for delivery...")
                time.sleep(2.0)

            self.delivered_count += 1

            if i < len(desks_to_visit) - 1:
                logger.info(f"\n↱  Turning RIGHT 90° back to straight...")
                self.robot.drive.turn_degrees(90)
                time.sleep(0.5)
                logger.info(f"   Ready to drive to next desk")

            # Handle the 180-degree turn after Desk 2 if needed
            if desk.id == 2 and i < len(desks_to_visit) - 1:
                next_desk = desks_to_visit[i+1]
                if next_desk.id > 2: # Only turn if the next desk is on the other side
                    logger.info(f"\n{'='*60}")
                    logger.info(f"🔄 180° TURN AT DESK 2")
                    logger.info(f"{'='*60}")
                    logger.info(f"\n↻  Turning 180° to reverse direction...")
                    self.robot.drive.turn_degrees(180)
                    time.sleep(0.5)
                    logger.info(f"✅ 180° turn complete")
                    current_desk_pos = 0 # Reset position logic for return trip if needed

        logger.info("\n" + "=" * 60)
        logger.info("✅ DELIVERY MISSION COMPLETE!")
        logger.info("=" * 60)
        logger.info(f"\n📊 STATISTICS:")
        logger.info(f"   Desks visited: {self.delivered_count}")
        logger.info(f"   Final position: At Desk {desks_to_visit[-1].id if desks_to_visit else 'N/A'}")


def main():
    """Main entry point."""
    import argparse
    parser = argparse.ArgumentParser(
        description='Execute a delivery mission to specified desks.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
# Run the mission, will be prompted for desks
python3 scripts/run_delivery_mission.py

# Run with a manual pause after each delivery
python3 scripts/run_delivery_mission.py --pause

# Run in simulation mode
python3 scripts/run_delivery_mission.py --simulate
"""
    )
    parser.add_argument('--pause', action='store_true',
                        help='Pause and wait for ENTER after each desk delivery.')
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
            mission.run(pause_after_each=args.pause)

    except KeyboardInterrupt:
        logger.warning("\n\nMission interrupted by user.")
        sys.exit(1)
    except Exception as e:
        logger.error(f"\n\nAn error occurred: {e}")
        logging.exception("Mission failed")
        sys.exit(1)


if __name__ == "__main__":
    main()