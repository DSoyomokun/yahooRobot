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
        logger.info(f"   Position: In front of Desk 1")
        logger.info(f"   Desks to visit: {[d.id for d in desks_to_visit]}")
        logger.info(f"   Papers to deliver: {len(desks_to_visit)}")

        input("\n⚠️  Press ENTER to start delivery traversal...")

        # HARDCODED DISTANCES (same as row traversal)
        distances = {
            1: 0,    # Already at Desk 1
            2: 104,  # Desk 1 → Desk 2
            3: 238,  # Desk 2 → Desk 3 (across gap)
            4: 104   # Desk 3 → Desk 4
        }

        # Track current position
        current_desk_id = 1

        # Visit each occupied desk
        for i, desk in enumerate(desks_to_visit):
            logger.info(f"\n{'='*60}")
            logger.info(f"DESK {desk.id} (#{i+1}/{len(desks_to_visit)})")
            logger.info(f"{'='*60}")

            # Calculate distance to drive from current position to target desk
            # Sum up distances between desks
            distance_to_drive = 0
            for desk_id in range(current_desk_id, desk.id):
                if desk_id + 1 in distances:
                    distance_to_drive += distances[desk_id + 1]

            if distance_to_drive > 1.0:
                logger.info(f"\n🚗 Driving {distance_to_drive} cm to Desk {desk.id}...")
                if self.simulate:
                    logger.info(f"   [SIMULATED] robot.drive.drive_cm({distance_to_drive})")
                else:
                    self.robot.drive.drive_cm(distance_to_drive)
                logger.info(f"✅ Arrived at Desk {desk.id}")
                current_desk_id = desk.id

            # Turn left to face desk
            logger.info(f"\n↰  Turning LEFT 90° to face Desk {desk.id}...")
            if self.simulate:
                logger.info(f"   [SIMULATED] robot.drive.turn_degrees(-90)")
            else:
                self.robot.drive.turn_degrees(-90)
                time.sleep(0.5)

            # Deliver paper
            self.deliver_to_desk(desk)

            # Turn back (unless last desk)
            if i < len(desks_to_visit) - 1:
                logger.info(f"\n↱  Turning RIGHT 90° back to straight...")
                if self.simulate:
                    logger.info(f"   [SIMULATED] robot.drive.turn_degrees(90)")
                else:
                    self.robot.drive.turn_degrees(90)
                    time.sleep(0.5)

            # 180° turn at Desk 2 if we visited it and need to continue
            if desk.id == 2 and i < len(desks_to_visit) - 1:
                logger.info(f"\n{'='*60}")
                logger.info(f"🔄 180° TURN AT DESK 2")
                logger.info(f"{'='*60}")
                logger.info(f"\n↻  Turning 180° to reverse direction...")
                if self.simulate:
                    logger.info(f"   [SIMULATED] robot.drive.turn_degrees(180)")
                else:
                    self.robot.drive.turn_degrees(180)
                    time.sleep(0.5)

        # Mission complete
        logger.info("\n" + "=" * 60)
        logger.info("✅ DELIVERY MISSION COMPLETE!")
        logger.info("=" * 60)
        logger.info(f"\n📊 STATISTICS:")
        logger.info(f"   Total desks: {len(self.desks)}")
        logger.info(f"   Occupied desks: {len(occupied_desk_ids)}")
        logger.info(f"   Papers delivered: {self.delivered_count}")
        logger.info(f"   Empty desks skipped: {len(self.desks) - len(occupied_desk_ids)}")
        logger.info(f"   Success rate: {self.delivered_count}/{len(desks_to_visit)}")


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
