#!/usr/bin/env python3
"""
Run Full Row Traversal - Story 1.4

This script commands the robot to traverse a full row of desks,
as defined in the room configuration file.

Path: Origin -> Desk 1 -> ... -> Last Desk -> Origin
"""

import sys
import time
import logging
import math
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from yahoo.robot import Robot
from yahoo.config.row_loader import load_row_config
from yahoo.config.row_loader import RowConfig

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class RowTraversal:
    """Handles the logic for the row traversal mission."""

    def __init__(self, robot: Robot, config: RowConfig):
        self.robot = robot
        self.config = config

        # Get origin from config
        origin_x, origin_y, origin_heading = config.get_origin()

        # State tracking
        self.current_x = origin_x
        self.current_y = origin_y
        self.current_heading = origin_heading

    def _turn_to_heading(self, target_heading: float):
        """Turn the robot to a specific absolute heading."""
        turn_angle = (target_heading - self.current_heading + 180) % 360 - 180
        if abs(turn_angle) > 1.0:  # Tolerance for small errors
            logger.info(f"Turning {turn_angle:.1f}° to face {target_heading}°")
            self.robot.drive.turn_degrees(turn_angle)
            self.current_heading = target_heading
        time.sleep(0.5)

    def _navigate_to_waypoint(self, name: str, target_x: float, target_y: float):
        """Navigate from current position to a target waypoint."""
        logger.info(f"--- Navigating to: {name} ({target_x:.1f}, {target_y:.1f}) ---")

        # 1. Drive along Y-axis to align with the target's Y-coordinate
        delta_y = target_y - self.current_y
        if abs(delta_y) > 1.0:
            heading = 0 if delta_y > 0 else 180
            self._turn_to_heading(heading)
            logger.info(f"Driving {abs(delta_y):.1f} cm along Y-axis")
            self.robot.drive.drive_cm(abs(delta_y))
            self.current_y = target_y
            time.sleep(0.5)

        # 2. Drive along X-axis to align with the target's X-coordinate
        delta_x = target_x - self.current_x
        if abs(delta_x) > 1.0:
            heading = 90 if delta_x > 0 else 270
            self._turn_to_heading(heading)
            logger.info(f"Driving {abs(delta_x):.1f} cm along X-axis")
            self.robot.drive.drive_cm(abs(delta_x))
            self.current_x = target_x
            time.sleep(0.5)

        logger.info(f"Arrived at {name}. Current position: ({self.current_x:.1f}, {self.current_y:.1f})")

    def run(self):
        """Execute the full row traversal."""
        logger.info("=" * 50)
        logger.info("Starting Full Row Traversal Mission")
        logger.info("=" * 50)

        # Get origin coordinates
        origin_x, origin_y, _ = self.config.get_origin()

        # Create list of waypoints
        waypoints = [
            ("Origin", origin_x, origin_y)
        ] + [
            (f"Desk {i+1}", desk.x_cm, desk.y_cm) for i, desk in enumerate(self.config.desks)
        ] + [
            ("Origin", origin_x, origin_y)
        ]

        logger.info("Initial position: "
                    f"({self.current_x:.1f}, {self.current_y:.1f}) "
                    f"at {self.current_heading}°")

        # Sequentially navigate to each waypoint
        for i, (name, x, y) in enumerate(waypoints):
            # The first move is from the current position to the first waypoint
            if i == 0:
                continue

            self._navigate_to_waypoint(name, x, y)
            
            logger.info(f"Pausing at {name}...")
            time.sleep(2.0) # Pause at each waypoint

        logger.info("=" * 50)
        logger.info("✅ Full Row Traversal Mission Complete!")
        logger.info("=" * 50)


def main():
    """Main entry point."""
    import argparse
    parser = argparse.ArgumentParser(description='Execute full row traversal (Story 1.4)')
    parser.add_argument('--simulate', action='store_true',
                        help='Run in simulation mode (no hardware)')
    parser.add_argument('--debug', action='store_true',
                        help='Enable debug logging')
    args = parser.parse_args()

    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)

    logger.info("Initializing robot...")
    try:
        with Robot(simulate=args.simulate) as robot:
            logger.info(f"Robot initialized (simulate={args.simulate})")
            logger.info(f"Battery: {robot.get_battery_voltage():.2f}V")

            config = load_row_config()
            logger.info(f"Loaded config for '{config.config.get('name', 'Unnamed Row')}' with {len(config.desks)} desks.")

            traversal = RowTraversal(robot, config)
            traversal.run()

    except KeyboardInterrupt:
        logger.warning("\nTraversal interrupted by user.")
        sys.exit(1)
    except Exception:
        logger.exception("An error occurred during the traversal.")
        sys.exit(1)


if __name__ == "__main__":
    main()