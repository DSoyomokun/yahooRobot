#!/usr/bin/env python3
"""
Collection Mission - Story 3.2

After a timer countdown, robot navigates to each desk and collects papers.

Flow:
1. Countdown timer (e.g., 10 minutes for students to work)
2. Collection phase starts
3. Navigate to each desk in sequence
4. At each desk: wait for paper insertion, scan, save with desk_id
5. Continue to all desks
6. Mission complete
"""

import sys
import time
import logging
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from yahoo.robot import Robot
from yahoo.config.row_loader import load_row_config

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s'  # Clean format - just the message
)
logger = logging.getLogger(__name__)


class CollectionMission:
    """Handles paper collection from all desks."""

    def __init__(self, robot, config, simulate=False):
        self.robot = robot
        self.config = config
        self.desks = sorted(config.desks, key=lambda d: d.id)
        self.collected_count = 0
        self.simulate = simulate
        self.scan_dir = Path(__file__).parent.parent / "collected_papers"
        self.scan_dir.mkdir(parents=True, exist_ok=True)

    def countdown(self, minutes=10):
        """
        Countdown timer before collection starts.

        Args:
            minutes: Minutes to wait (default: 10)
        """
        logger.info("=" * 60)
        logger.info("⏰ COLLECTION TIMER")
        logger.info("=" * 60)
        logger.info(f"\n⏳ Students have {minutes} minutes to complete their work")
        logger.info(f"   Collection will begin automatically after timer")

        # For testing, allow skip
        response = input(f"\n⚠️  Press ENTER to skip timer and start collection now, or type minutes to wait: ")

        if response.strip():
            try:
                minutes = int(response)
            except ValueError:
                logger.info("Invalid input, skipping timer")
                return

        if minutes > 0:
            logger.info(f"\n⏳ Waiting {minutes} minutes...")
            logger.info(f"   Collection will start at: {datetime.now().strftime('%H:%M:%S')}")

            # Countdown in 1-minute intervals for last 5 minutes
            total_seconds = minutes * 60

            # Wait silently until last 5 minutes
            if minutes > 5:
                time.sleep((minutes - 5) * 60)
                total_seconds = 5 * 60

            # Countdown last 5 minutes
            while total_seconds > 0:
                mins_left = total_seconds // 60
                secs_left = total_seconds % 60

                if mins_left > 0:
                    logger.info(f"   ⏰ {mins_left} minute{'s' if mins_left != 1 else ''} remaining...")
                elif secs_left in [30, 10, 5, 4, 3, 2, 1]:
                    logger.info(f"   ⏰ {secs_left} second{'s' if secs_left != 1 else ''}...")

                time.sleep(1)
                total_seconds -= 1

        logger.info("\n🔔 TIME'S UP! Starting collection...")
        time.sleep(2)

    def collect_at_desk(self, desk):
        """
        Collect paper from a single desk.

        Args:
            desk: Desk object
        """
        logger.info(f"\n📄 WAITING FOR PAPER AT DESK {desk.id}")
        logger.info(f"   Student: Please insert your paper")

        # Simple version: just wait for ENTER key
        # TODO: Integrate with actual scanner when ready
        input(f"   Press ENTER when paper is inserted at Desk {desk.id}...")

        # Simulate scanning
        logger.info(f"   📸 Scanning paper from Desk {desk.id}...")
        time.sleep(1)  # Simulate scan time

        # Save "scan" (for now just create a placeholder file)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"desk_{desk.id}_{timestamp}.txt"
        filepath = self.scan_dir / filename

        with open(filepath, 'w') as f:
            f.write(f"Paper collected from Desk {desk.id}\n")
            f.write(f"Timestamp: {datetime.now()}\n")

        logger.info(f"   ✅ Paper collected and saved: {filename}")
        self.collected_count += 1

    def run(self, limit_desks=None, countdown_minutes=0):
        """
        Execute collection mission.

        Args:
            limit_desks: If set, only visit first N desks (for testing)
            countdown_minutes: Minutes to wait before collection (0 = start immediately)
        """
        logger.info("=" * 60)
        logger.info("📦 COLLECTION MISSION - Story 3.2")
        if self.simulate:
            logger.info("⚠️  SIMULATION MODE - No hardware required")
        logger.info("=" * 60)
        logger.info(f"\n📥 PHASE: PAPER COLLECTION")
        logger.info(f"Goal: Collect papers from all desks")

        # Countdown phase
        if countdown_minutes > 0:
            self.countdown(countdown_minutes)

        # Limit desks if in debug mode
        desks_to_visit = self.desks[:limit_desks] if limit_desks else self.desks

        logger.info(f"\n🤖 STARTING COLLECTION")
        logger.info(f"   Position: In front of Desk 1")
        logger.info(f"   Desks to visit: {len(desks_to_visit)}")
        logger.info(f"   Save directory: {self.scan_dir}")

        input("\n⚠️  Press ENTER to start collection traversal...")

        # HARDCODED DISTANCES (TESTING: 25cm between all desks for this room)
        distances = {
            1: 0,   # Already at Desk 1
            2: 25,  # Desk 1 → Desk 2 (25 cm for testing)
            3: 25,  # Desk 2 → Desk 3 (25 cm for testing)
            4: 25   # Desk 3 → Desk 4 (25 cm for testing)
        }

        # Visit each desk
        for i, desk in enumerate(desks_to_visit):
            logger.info(f"\n{'='*60}")
            logger.info(f"DESK {desk.id} (#{i+1}/{len(desks_to_visit)})")
            logger.info(f"{'='*60}")

            # Drive to desk position
            distance_to_drive = distances.get(desk.id, 0)

            if distance_to_drive > 1.0:
                logger.info(f"\n🚗 Driving {distance_to_drive} cm to Desk {desk.id}...")
                if self.simulate:
                    logger.info(f"   [SIMULATED] robot.drive.drive_cm({distance_to_drive})")
                else:
                    self.robot.drive.drive_cm(distance_to_drive)
                logger.info(f"✅ Arrived at Desk {desk.id}")

            # Turn left to face desk
            logger.info(f"\n↰  Turning LEFT 90° to face Desk {desk.id}...")
            if self.simulate:
                logger.info(f"   [SIMULATED] robot.drive.turn_degrees(-90)")
            else:
                self.robot.drive.turn_degrees(-90)
                time.sleep(0.5)

            # Collect paper
            self.collect_at_desk(desk)

            # Turn back (unless last desk)
            if i < len(desks_to_visit) - 1:
                logger.info(f"\n↱  Turning RIGHT 90° back to straight...")
                if self.simulate:
                    logger.info(f"   [SIMULATED] robot.drive.turn_degrees(90)")
                else:
                    self.robot.drive.turn_degrees(90)
                    time.sleep(0.5)

            # 180° turn at Desk 2 (same as row traversal)
            if desk.id == 2:
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
        logger.info("✅ COLLECTION MISSION COMPLETE!")
        logger.info("=" * 60)
        logger.info(f"\n📊 STATISTICS:")
        logger.info(f"   Desks visited: {len(desks_to_visit)}")
        logger.info(f"   Papers collected: {self.collected_count}")
        logger.info(f"   Success rate: {self.collected_count}/{len(desks_to_visit)}")
        logger.info(f"   Saved to: {self.scan_dir}")


def main():
    """Main entry point."""
    import argparse
    parser = argparse.ArgumentParser(
        description='Execute collection mission (Story 3.2)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Full mission with 10-minute timer
  python3 scripts/run_collection_mission.py --timer 10

  # Start collection immediately (skip timer)
  python3 scripts/run_collection_mission.py

  # Debug: Only collect from first 2 desks
  python3 scripts/run_collection_mission.py --limit-desks 2

  # Quick test with no timer
  python3 scripts/run_collection_mission.py --limit-desks 1

Setup:
  Position robot in front of Desk 1, facing along the row
        """
    )
    parser.add_argument('--timer', type=int, default=0, metavar='MINUTES',
                       help='Minutes to wait before collection (0 = start now)')
    parser.add_argument('--simulate', action='store_true',
                       help='Run in simulation mode (no hardware required)')
    parser.add_argument('--limit-desks', type=int, metavar='N',
                       help='Only visit first N desks (for testing)')
    parser.add_argument('--debug', action='store_true',
                       help='Enable debug logging')
    args = parser.parse_args()

    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)

    logger.info("Initializing robot...")
    try:
        with Robot(simulate=args.simulate) as robot:
            logger.info(f"✅ Robot initialized (simulate={args.simulate})")
            logger.info(f"   Battery: {robot.get_battery_voltage():.2f}V")

            config = load_row_config()
            logger.info(f"✅ Config loaded: {len(config.desks)} desks")

            mission = CollectionMission(robot, config, simulate=args.simulate)
            mission.run(
                limit_desks=args.limit_desks,
                countdown_minutes=args.timer
            )

    except KeyboardInterrupt:
        logger.warning("\n\nMission interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"\n\nMission error: {e}")
        logging.exception("Mission failed")
        sys.exit(1)


if __name__ == "__main__":
    main()
