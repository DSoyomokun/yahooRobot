#!/usr/bin/env python3
"""
Row Traversal - Story 1.4

NEW APPROACH:
- Robot starts in front of Desk 1, facing along the row
- Drives straight along the aisle
- At each desk: turn left to face desk, then turn right to continue
- Pattern: Desk 1 → Desk 2 → Desk 3 → Desk 4
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


class RowTraversal:
    """Handles row traversal along the aisle in front of desks."""

    def __init__(self, robot, config):
        self.robot = robot
        self.config = config
        self.desks = sorted(config.desks, key=lambda d: d.x_cm)  # Sort by X position

    def run(self, limit_desks=None, pause_after_each=False):
        """
        Execute row traversal.

        Args:
            limit_desks: If set, only visit first N desks (for debugging)
            pause_after_each: If True, wait for user input after each desk
        """
        logger.info("=" * 60)
        logger.info("ROW TRAVERSAL - Story 1.4")
        if limit_desks:
            logger.info(f"DEBUG MODE: Limited to {limit_desks} desks")
        logger.info("=" * 60)

        # HARDCODED DISTANCES (measured from real setup)
        # DOUBLED - original measurements came up short
        # Original: Desk 1→2: 52cm, Desk 2→3: 119cm, Desk 3→4: 52cm
        # Doubled values:
        distances = {
            1: 0,    # Already at Desk 1
            2: 104,  # Desk 1 → Desk 2 (52 * 2)
            3: 238,  # Desk 2 → Desk 3 (119 * 2)
            4: 104   # Desk 3 → Desk 4 (52 * 2)
        }

        # Limit desks if in debug mode
        all_desks = sorted(self.config.desks, key=lambda d: d.id)
        desks_to_visit = all_desks[:limit_desks] if limit_desks else all_desks

        logger.info(f"\n🤖 STARTING POSITION:")
        logger.info(f"   - In front of Desk 1")
        logger.info(f"   - Facing straight along the row (parallel to desks)")
        logger.info(f"\n📍 DESKS TO VISIT: {len(desks_to_visit)}")
        for desk in desks_to_visit:
            dist = distances.get(desk.id, 0)
            logger.info(f"   Desk {desk.id}: drive {dist} cm from previous")

        logger.info(f"\n🔄 MOVEMENT PATTERN:")
        logger.info(f"   1. Turn LEFT 90° to face desk")
        logger.info(f"   2. Hand out paper (pause)")
        logger.info(f"   3. Turn RIGHT 90° back to straight")
        logger.info(f"   4. Drive to next desk position")

        input("\n⚠️  Press ENTER to start traversal...")

        # Visit each desk
        for i, desk in enumerate(desks_to_visit):
            logger.info(f"\n{'='*60}")
            logger.info(f"DESK {desk.id} (#{i+1}/{len(desks_to_visit)})")
            logger.info(f"{'='*60}")

            # Drive to desk position (if not first desk)
            distance_to_drive = distances.get(desk.id, 0)

            if distance_to_drive > 1.0:
                logger.info(f"\n📏 Distance to drive: {distance_to_drive} cm")
                logger.info(f"🚗 Driving {distance_to_drive} cm...")
                self.robot.drive.drive_cm(distance_to_drive)
                logger.info(f"✅ Arrived at Desk {desk.id} position")
            else:
                logger.info(f"\n✅ Already at Desk {desk.id} position")

            # Turn left to face desk
            logger.info(f"\n↰  Turning LEFT 90° to face Desk {desk.id}...")
            self.robot.drive.turn_degrees(-90)  # Negative = left
            time.sleep(0.5)

            logger.info(f"\n📍 AT DESK {desk.id}")
            logger.info(f"   Facing the desk - ready to hand out paper")

            # Pause (simulating paper handout)
            if pause_after_each:
                input(f"\n📄 Press ENTER after handing out paper at Desk {desk.id}...")
            else:
                logger.info(f"   📄 Handing out paper (pausing 2 seconds)...")
                time.sleep(2.0)

            # Turn right to face along row again (unless last desk)
            if i < len(desks_to_visit) - 1:
                logger.info(f"\n↱  Turning RIGHT 90° back to straight...")
                self.robot.drive.turn_degrees(90)  # Positive = right
                time.sleep(0.5)
                logger.info(f"   Ready to drive to next desk")

        logger.info("\n" + "=" * 60)
        logger.info("✅ ROW TRAVERSAL COMPLETE!")
        logger.info("=" * 60)
        logger.info(f"\nFinal position: At Desk {desks_to_visit[-1].id}")
        logger.info(f"Facing: Perpendicular to row (toward desk)")


def main():
    """Main entry point."""
    import argparse
    parser = argparse.ArgumentParser(
        description='Execute row traversal (Story 1.4)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Full traversal (all 4 desks)
  python3 scripts/run_row_traversal.py

  # Debug: Only visit first 2 desks
  python3 scripts/run_row_traversal.py --limit-desks 2

  # Debug with manual pause after each desk
  python3 scripts/run_row_traversal.py --limit-desks 2 --pause

  # Enable detailed debug logging
  python3 scripts/run_row_traversal.py --limit-desks 2 --debug

Setup:
  Position robot in front of Desk 1, facing along the row (parallel to desks)
        """
    )
    parser.add_argument('--limit-desks', type=int, metavar='N',
                       help='Only visit first N desks (for debugging)')
    parser.add_argument('--pause', action='store_true',
                       help='Pause and wait for ENTER after each desk')
    parser.add_argument('--debug', action='store_true',
                       help='Enable debug logging')
    args = parser.parse_args()

    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)

    logger.info("Initializing robot...")
    try:
        with Robot(simulate=False) as robot:
            logger.info(f"✅ Robot initialized")
            logger.info(f"   Battery: {robot.get_battery_voltage():.2f}V")

            config = load_row_config()
            logger.info(f"✅ Config loaded: {len(config.desks)} desks")

            traversal = RowTraversal(robot, config)
            traversal.run(limit_desks=args.limit_desks, pause_after_each=args.pause)

    except KeyboardInterrupt:
        logger.warning("\n\nTraversal interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"\n\nTraversal error: {e}")
        logging.exception("Traversal failed")
        sys.exit(1)


if __name__ == "__main__":
    main()
