"""
Row Path Planner for 5-stop point navigation system.
Defines fixed stop points at 60-inch intervals for pass-out and collection phases.
"""
import math
from typing import List, Tuple, Optional
import logging

logger = logging.getLogger(__name__)

# Conversion constants
INCHES_TO_CM = 2.54


class RowPathPlanner:
    """
    Path planner for fixed 5-stop point row navigation.
    
    Stop points are evenly spaced at 60 inches apart:
    - Stop 0-3: Correspond to desks 1-4
    - Stop 4: Buffer position for 180° turn
    
    Pass-out phase: 0 → 1 → 2 → 3 → 4 (forward)
    Collection phase: 4 → 3 → 2 → 1 → 0 (reverse)
    """
    
    def __init__(
        self,
        stop_spacing_inches: float = 60.0,
        origin_position: Tuple[float, float, float] = (0.0, 0.0, 0.0),
        num_stops: int = 5
    ):
        """
        Initialize row path planner.
        
        Args:
            stop_spacing_inches: Distance between stop points in inches (default: 60)
            origin_position: Starting position as (x_cm, y_cm, heading_deg)
            num_stops: Number of stop points (default: 5)
        """
        self.stop_spacing_inches = stop_spacing_inches
        self.stop_spacing_cm = stop_spacing_inches * INCHES_TO_CM
        self.origin_x_cm, self.origin_y_cm, self.origin_heading_deg = origin_position
        self.num_stops = num_stops
        
        # Calculate stop positions (all along Y-axis, forward from origin)
        self._stop_positions: List[Tuple[float, float, float]] = []
        self._calculate_stop_positions()
        
        # Desk mapping: stop_index -> desk_id (1-4), stop 4 has no desk
        self._desk_mapping = {
            0: 1,
            1: 2,
            2: 3,
            3: 4,
            4: None  # Buffer stop has no desk
        }
        
        logger.info(f"RowPathPlanner initialized: {num_stops} stops, {stop_spacing_inches} inches apart")
    
    def _calculate_stop_positions(self):
        """Calculate positions for all stop points."""
        self._stop_positions = []
        
        for i in range(self.num_stops):
            # All stops are along Y-axis (forward from origin)
            # Stop 0 is at origin, each subsequent stop is spacing_cm forward
            x_cm = self.origin_x_cm
            y_cm = self.origin_y_cm + (i * self.stop_spacing_cm)
            heading_deg = self.origin_heading_deg  # All stops face same direction initially
            
            self._stop_positions.append((x_cm, y_cm, heading_deg))
    
    def get_stop_position(self, stop_index: int) -> Tuple[float, float, float]:
        """
        Get position for a specific stop point.
        
        Args:
            stop_index: Stop index (0-4)
        
        Returns:
            Tuple of (x_cm, y_cm, heading_deg)
        
        Raises:
            ValueError: If stop_index is out of range
        """
        if stop_index < 0 or stop_index >= self.num_stops:
            raise ValueError(f"Stop index {stop_index} out of range (0-{self.num_stops-1})")
        
        return self._stop_positions[stop_index]
    
    def get_desk_stop(self, desk_id: int) -> int:
        """
        Map desk ID to stop index.
        
        Args:
            desk_id: Desk ID (1-4)
        
        Returns:
            Stop index (0-3)
        
        Raises:
            ValueError: If desk_id is not 1-4
        """
        if desk_id < 1 or desk_id > 4:
            raise ValueError(f"Desk ID {desk_id} out of range (1-4)")
        
        return desk_id - 1  # Desk 1 -> Stop 0, Desk 2 -> Stop 1, etc.
    
    def get_desk_for_stop(self, stop_index: int) -> Optional[int]:
        """
        Get desk ID for a stop index.
        
        Args:
            stop_index: Stop index (0-4)
        
        Returns:
            Desk ID (1-4) or None if stop 4 (buffer)
        """
        return self._desk_mapping.get(stop_index)
    
    def get_pass_out_route(self) -> List[int]:
        """
        Get route for pass-out phase (forward traversal).
        
        Returns:
            List of stop indices: [0, 1, 2, 3, 4]
        """
        return list(range(self.num_stops))
    
    def get_collection_route(self) -> List[int]:
        """
        Get route for collection phase (reverse traversal).
        
        Returns:
            List of stop indices: [4, 3, 2, 1, 0]
        """
        return list(range(self.num_stops - 1, -1, -1))
    
    def is_desk_stop(self, stop_index: int) -> bool:
        """
        Check if a stop index corresponds to a desk (not buffer).
        
        Args:
            stop_index: Stop index (0-4)
        
        Returns:
            True if stop has a desk (0-3), False if buffer (4)
        """
        return stop_index < 4
    
    def get_stop_spacing_cm(self) -> float:
        """Get stop spacing in centimeters."""
        return self.stop_spacing_cm
    
    def get_stop_spacing_inches(self) -> float:
        """Get stop spacing in inches."""
        return self.stop_spacing_inches
    
    def get_distance_to_stop(self, current_stop: int, target_stop: int) -> float:
        """
        Calculate distance between two stop points.
        
        Args:
            current_stop: Current stop index
            target_stop: Target stop index
        
        Returns:
            Distance in centimeters
        """
        stops_apart = abs(target_stop - current_stop)
        return stops_apart * self.stop_spacing_cm
    
    def print_summary(self):
        """Print a summary of the path planner configuration."""
        print("=" * 60)
        print("Row Path Planner Summary")
        print("=" * 60)
        print(f"\nStop spacing: {self.stop_spacing_inches} inches ({self.stop_spacing_cm:.1f} cm)")
        print(f"Number of stops: {self.num_stops}")
        print(f"Origin: ({self.origin_x_cm:.1f}, {self.origin_y_cm:.1f}) cm, heading: {self.origin_heading_deg:.1f}°")
        
        print(f"\nStop Points:")
        for i in range(self.num_stops):
            x, y, heading = self._stop_positions[i]
            desk_id = self.get_desk_for_stop(i)
            desk_info = f"Desk {desk_id}" if desk_id else "Buffer"
            print(f"  Stop {i}: ({x:6.1f}, {y:6.1f}) cm, heading: {heading:6.1f}° - {desk_info}")
        
        print(f"\nPass-out route: {self.get_pass_out_route()}")
        print(f"Collection route: {self.get_collection_route()}")
        print("=" * 60)

