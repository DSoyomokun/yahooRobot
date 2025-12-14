"""
Row configuration loader for Yahoo Robot.
Loads desk layout from row_config.json.
"""

import json
import math
from pathlib import Path
from typing import Dict, List, Tuple
import logging

logger = logging.getLogger(__name__)


class Desk:
    """Represents a single desk in the classroom."""

    def __init__(self, desk_data: dict):
        self.id = desk_data['id']
        self.name = desk_data['name']
        self.x_cm = desk_data['x_cm']
        self.y_cm = desk_data['y_cm']
        self.description = desk_data.get('description', '')

    def position(self) -> Tuple[float, float]:
        """Get desk position as (x, y) tuple."""
        return (self.x_cm, self.y_cm)

    def distance_from_origin(self) -> float:
        """Calculate distance from origin to desk."""
        return math.sqrt(self.x_cm**2 + self.y_cm**2)

    def angle_from_origin(self) -> float:
        """
        Calculate angle from origin to desk.
        Returns angle in degrees (0° = forward, positive = right, negative = left).
        """
        angle_rad = math.atan2(self.x_cm, self.y_cm)
        return math.degrees(angle_rad)

    def __repr__(self):
        return f"Desk({self.id}: {self.name} at ({self.x_cm:.1f}, {self.y_cm:.1f})cm)"


class RowConfig:
    """Configuration for the row of desks."""

    def __init__(self, config_path: str = None):
        """
        Load row configuration.

        Args:
            config_path: Path to row_config.json. If None, uses default location.
        """
        if config_path is None:
            # Default to yahoo/config/row_config.json
            config_path = Path(__file__).parent / 'row_config.json'

        self.config_path = Path(config_path)
        self.config = self._load_config()
        self.desks = self._load_desks()

    def _load_config(self) -> dict:
        """Load configuration from JSON file."""
        if not self.config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {self.config_path}")

        with open(self.config_path, 'r') as f:
            config = json.load(f)

        logger.info(f"Loaded configuration from {self.config_path}")
        return config

    def _load_desks(self) -> List[Desk]:
        """Load desk objects from configuration."""
        desks = [Desk(desk_data) for desk_data in self.config['desks']]

        # Sort by ID to ensure consistent ordering
        desks.sort(key=lambda d: d.id)

        logger.info(f"Loaded {len(desks)} desks")
        return desks

    def get_desk(self, desk_id: int) -> Desk:
        """
        Get desk by ID.

        Args:
            desk_id: Desk ID (1-4)

        Returns:
            Desk object

        Raises:
            ValueError: If desk_id not found
        """
        for desk in self.desks:
            if desk.id == desk_id:
                return desk
        raise ValueError(f"Desk {desk_id} not found")

    def get_origin(self) -> Tuple[float, float, float]:
        """
        Get origin position and heading.

        Returns:
            Tuple of (x_cm, y_cm, heading_deg)
        """
        origin = self.config['origin']
        return (origin['x_cm'], origin['y_cm'], origin['heading_deg'])

    def get_scan_angle(self, desk_id: int) -> float:
        """
        Get scanning angle for desk-centric polling.

        Args:
            desk_id: Desk ID (1-4)

        Returns:
            Angle in degrees to turn to face the desk
        """
        return self.config['scan_angles'][str(desk_id)]

    def get_desk_distance_forward(self) -> float:
        """Get the Y-distance from origin to desk line."""
        return self.config['desk_distance_forward_cm']

    def update_desk_distance(self, distance_cm: float):
        """
        Update the desk distance and recalculate scan angles.

        Args:
            distance_cm: Measured distance from origin to desks
        """
        # Update config
        self.config['desk_distance_forward_cm'] = distance_cm

        # Recalculate scan angles
        for desk in self.desks:
            desk.y_cm = distance_cm
            angle = desk.angle_from_origin()
            self.config['scan_angles'][str(desk.id)] = round(angle, 1)

        # Save updated config
        self._save_config()
        logger.info(f"Updated desk distance to {distance_cm}cm and recalculated scan angles")

    def _save_config(self):
        """Save configuration back to JSON file."""
        with open(self.config_path, 'w') as f:
            json.dump(self.config, f, indent=2)

    def get_navigation_settings(self) -> dict:
        """Get navigation speed and distance settings."""
        return self.config.get('navigation', {})

    def print_summary(self):
        """Print a summary of the configuration."""
        print("=" * 60)
        print("Row Configuration Summary")
        print("=" * 60)

        origin = self.get_origin()
        print(f"\nOrigin: ({origin[0]:.1f}, {origin[1]:.1f})cm, heading: {origin[2]:.1f}°")
        print(f"Desk distance forward: {self.get_desk_distance_forward():.1f}cm")

        print(f"\nDesks ({len(self.desks)} total):")
        for desk in self.desks:
            scan_angle = self.get_scan_angle(desk.id)
            distance = desk.distance_from_origin()
            print(f"  {desk.id}. {desk.name}")
            print(f"     Position: ({desk.x_cm:6.1f}, {desk.y_cm:6.1f})cm")
            print(f"     Distance: {distance:6.1f}cm")
            print(f"     Scan angle: {scan_angle:+6.1f}°")

        nav = self.get_navigation_settings()
        if nav:
            print(f"\nNavigation Settings:")
            print(f"  Default speed: {nav.get('default_speed_dps', 'N/A')} DPS")
            print(f"  Turn speed: {nav.get('turn_speed_dps', 'N/A')} DPS")
            print(f"  Approach speed: {nav.get('approach_speed_dps', 'N/A')} DPS")

        print("=" * 60)


def load_row_config(config_path: str = None) -> RowConfig:
    """
    Convenience function to load row configuration.

    Args:
        config_path: Optional path to config file

    Returns:
        RowConfig object
    """
    return RowConfig(config_path)
