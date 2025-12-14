#!/usr/bin/env python3
"""
Simple Drive Test - Drive straight to a desk

Position the robot directly in front of a desk, facing it.
This script will drive straight forward to the desk.
"""

import sys
import time
import logging
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from yahoo.robot import Robot

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    import argparse
    parser = argparse.ArgumentParser(description='Simple drive test - drive straight to desk')
    parser.add_argument('--distance', type=float, default=100.0,
                       help='Distance to drive in cm (default: 100cm)')
    args = parser.parse_args()

    logger.info("=" * 60)
    logger.info("SIMPLE DRIVE TEST")
    logger.info("=" * 60)
    logger.info(f"\nTest: Drive straight forward {args.distance} cm")
    logger.info("\n📍 SETUP:")
    logger.info("   1. Place robot directly in front of Desk 1")
    logger.info("   2. Robot should be facing the desk")
    logger.info("   3. Make sure path is clear")

    input("\n⚠️  Press ENTER when robot is positioned and ready...")

    try:
        with Robot(simulate=False) as robot:
            logger.info(f"\n✅ Robot initialized")
            logger.info(f"   Battery: {robot.get_battery_voltage():.2f}V")

            input(f"\n▶️  Press ENTER to drive {args.distance} cm forward...")

            logger.info(f"\n🚗 Driving forward {args.distance} cm...")
            start_time = time.time()

            robot.drive.drive_cm(args.distance)

            end_time = time.time()
            duration = end_time - start_time

            logger.info(f"\n✅ Drive complete!")
            logger.info(f"   Duration: {duration:.2f} seconds")
            logger.info(f"   Distance: {args.distance} cm")

            logger.info("\n📏 CHECK:")
            logger.info("   - Did the robot stop at the desk?")
            logger.info("   - Measure actual distance traveled")
            logger.info("   - Compare to expected distance")

            logger.info("\n" + "=" * 60)
            logger.info("Test Complete")
            logger.info("=" * 60)

    except KeyboardInterrupt:
        logger.warning("\n\nTest interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"\n\nTest error: {e}")
        logging.exception("Test failed")
        sys.exit(1)


if __name__ == "__main__":
    main()
