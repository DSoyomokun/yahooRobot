#!/usr/bin/env python3
"""
Delivery Mission

Delivers papers to specified desks.

- Prompts user to enter which desks are OCCUPIED.
- Navigates to ONLY those desks.
- At each occupied desk, it turns left, waits for user confirmation, and turns right.
- Skips empty desks.
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

    def get_desks_to_visit(self):
        """
        Asks user for OCCUPIED desks and returns a list of desk IDs to visit.
        """
        logger.info("=" * 60)
        logger.info("📍 DESK OCCUPANCY CHECK")
        logger.info("=" * 60)
        logger.info("\nEnter which desks have students and should be visited.")
        logger.info("Example: 1,2,4 (visits Desks 1, 2, and 4)")
        logger.info("Press ENTER if all desks are occupied.")

        while True:
            response = input("\nEnter occupied desks (comma-separated, e.g., 1,2,4): ").strip()
            
            # Default to all desks if input is empty
            if not response:
                occupied_ids = [d.id for d in self.desks]
            else:
                try:
                    occupied_ids = [int(x.strip()) for x in response.split(',')]
                except ValueError:
                    logger.warning("Invalid format. Please use comma-separated numbers (e.g., 1,2,4).")
                    continue

            all_desk_ids = [d.id for d in self.desks]
            invalid_ids = [d_id for d_id in occupied_ids if d_id not in all_desk_ids]

            if invalid_ids:
                logger.warning(f"Invalid desk IDs: {invalid_ids}. Valid IDs are: {all_desk_ids}")
                continue

            total_desks = len(all_desk_ids)
            skipped_desks = total_desks - len(occupied_ids)
            
            logger.info(f"\n✅ Occupied desks to visit: {occupied_ids}")
            logger.info(f"   Will deliver to {len(occupied_ids)} desk(s)")
            logger.info(f"   Skipping {skipped_desks} empty desk(s)")
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

        # Distances between adjacent desks
        distances = {
            2: 104,  # From 1 to 2
            3: 238,  # From 2 to 3
            4: 104   # From 3 to 4
        }

        logger.info(f"\n🤖 STARTING DELIVERY")
        logger.info(f"   Position: In front of Desk 1")
        logger.info(f"   Desks to visit: {[d.id for d in desks_to_visit]}")
        
        input("\n⚠️  Press ENTER to start delivery...")

        current_desk_pos = 1
        for i, desk in enumerate(desks_to_visit):
            logger.info(f"\n{'='*60}")
            logger.info(f"VISITING DESK {desk.id} (#{i+1}/{len(desks_to_visit)})")
            logger.info(f"{'='*60}")

            # Calculate distance to drive from current position
            distance_to_drive = 0
            if desk.id > current_desk_pos:
                # Sum the segments between the current desk and the target desk
                distance_to_drive = sum(distances.get(j, 0) for j in range(current_desk_pos + 1, desk.id + 1))

            if distance_to_drive > 0:
                logger.info(f"\n📏 Driving from Desk {current_desk_pos} to {desk.id}")
                logger.info(f"🚗 Driving {distance_to_drive} cm...")
                self.robot.drive.drive_cm(distance_to_drive)
                logger.info(f"✅ Arrived at Desk {desk.id} position")
            else:
                logger.info(f"\n✅ Already at Desk {desk.id} position")

            current_desk_pos = desk.id

            # Turn to face desk and wait for user confirmation
            logger.info(f"\n↰  Turning LEFT 90° to face Desk {desk.id}...")
            self.robot.drive.turn_degrees(-90)
            time.sleep(0.5)

            logger.info(f"\n📍 AT DESK {desk.id}")
            input(f"   📄 Press ENTER when paper is collected from Desk {desk.id}...")
            
            self.delivered_count += 1
            logger.info(f"   ✅ Paper collected.")

            # Turn back to the aisle if it's not the last desk
            if i < len(desks_to_visit) - 1:
                logger.info(f"\n↱  Turning RIGHT 90° back to straight...")
                self.robot.drive.turn_degrees(90)
                time.sleep(0.5)
                logger.info(f"   Ready to drive to next desk.")

        logger.info("\n" + "=" * 60)
        logger.info("✅ DELIVERY MISSION COMPLETE!")
        logger.info("=" * 60)
        logger.info(f"\n📊 STATISTICS:")
        logger.info(f"   Papers delivered: {self.delivered_count}")
        logger.info(f"   Final position: At Desk {desks_to_visit[-1].id if desks_to_visit else 'N/A'}")


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
