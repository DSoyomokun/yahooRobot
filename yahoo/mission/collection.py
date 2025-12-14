"""
Collection Mission for row navigation with scanner integration.
Traverses stops 4→3→2→1→0 reverse, scanning papers at desk stops (0-3).
Includes obstacle detection and avoidance.
"""
import logging
from typing import Optional

from yahoo.mission.obstacle_nav import ObstacleNavigator

logger = logging.getLogger(__name__)


class CollectionMission:
    """
    Collection mission that traverses row in reverse, scanning papers at desk stops.
    
    Route: Stop 4 (Buffer) → Stop 3 (Desk 4) → Stop 2 (Desk 3) → Stop 1 (Desk 2) → Stop 0 (Desk 1)
    Scanner runs as blocking process at each desk stop with timeout.
    """
    
    def __init__(self, robot, row_planner, scanner_timeout: float = 30.0):
        """
        Initialize collection mission.
        
        Args:
            robot: Robot instance with drive subsystem
            row_planner: RowPathPlanner instance
            scanner_timeout: Timeout in seconds for scanner wait (default: 30.0)
        """
        self.robot = robot
        self.planner = row_planner
        self.scanner_timeout = scanner_timeout
        self.current_stop = 4  # Start at buffer stop (after 180° turn)
        self.obstacle_nav = ObstacleNavigator(robot)  # Obstacle-aware navigation
        
        logger.info(f"[COLLECTION] Mission initialized (scanner timeout: {scanner_timeout}s)")
    
    def execute(self):
        """
        Execute the complete collection phase.
        
        Returns:
            dict with mission summary (desks_visited, papers_collected, timeouts, etc.)
        """
        logger.info("[COLLECTION] Starting collection phase")
        
        route = self.planner.get_collection_route()
        papers_collected = 0
        desks_visited = 0
        timeouts = 0
        
        try:
            for stop_idx in route:
                logger.info(f"[COLLECTION] Navigating to Stop {stop_idx}")
                self.navigate_to_stop(stop_idx)
                
                if self.planner.is_desk_stop(stop_idx):
                    # Desk stop - collect and scan paper
                    desk_id = self.planner.get_desk_for_stop(stop_idx)
                    desks_visited += 1
                    
                    logger.info(f"[COLLECTION] Arrived at Stop {stop_idx} (Desk {desk_id}), waiting for paper...")
                    
                    scan_result = self.collect_and_scan(desk_id)
                    
                    if scan_result:
                        papers_collected += 1
                        logger.info(f"[COLLECTION] Paper collected and scanned at Desk {desk_id}: {scan_result}")
                    else:
                        timeouts += 1
                        logger.warning(f"[COLLECTION] Timeout waiting for paper at Desk {desk_id}")
                else:
                    # Stop 4 - buffer position, no action needed
                    logger.info(f"[COLLECTION] At Stop {stop_idx} (Buffer), continuing...")
            
            logger.info("[COLLECTION] Collection phase complete")
            
            return {
                'success': True,
                'desks_visited': desks_visited,
                'papers_collected': papers_collected,
                'timeouts': timeouts,
                'route_completed': True
            }
            
        except Exception as e:
            logger.error(f"[COLLECTION] Error during collection: {e}")
            return {
                'success': False,
                'error': str(e),
                'desks_visited': desks_visited,
                'papers_collected': papers_collected,
                'timeouts': timeouts
            }
    
    def navigate_to_stop(self, stop_index: int):
        """
        Navigate to a specific stop point.
        
        Args:
            stop_index: Target stop index (0-4)
        """
        if stop_index == self.current_stop:
            logger.debug(f"[COLLECTION] Already at Stop {stop_index}")
            return
        
        # Calculate distance to travel (negative for reverse movement)
        distance_cm = self.planner.get_distance_to_stop(self.current_stop, stop_index)
        
        # For reverse movement, distance should be negative
        if self.current_stop > stop_index:
            # Moving backward (reverse)
            distance_cm = -distance_cm
        
        if abs(distance_cm) > 0.1:  # Only move if distance is significant
            direction = "backward" if distance_cm < 0 else "forward"
            logger.info(f"[COLLECTION] Moving {abs(distance_cm):.1f}cm {direction} from Stop {self.current_stop} to Stop {stop_index}")
            
            # Use obstacle-aware navigation
            if hasattr(self.robot, 'drive') and self.robot.drive:
                success = self.obstacle_nav.drive_cm_safe(distance_cm, check_obstacles=True)
                if not success:
                    logger.warning("[COLLECTION] Movement interrupted or failed")
            else:
                logger.warning("[COLLECTION] Robot drive not available, simulating movement")
        
        # Update current position
        self.current_stop = stop_index
        logger.info(f"[COLLECTION] Arrived at Stop {stop_index}")
    
    def collect_and_scan(self, desk_id: int) -> Optional[str]:
        """
        Blocking scan process with timeout.
        
        Args:
            desk_id: Desk ID (1-4)
        
        Returns:
            file_path (str) if scan completed, None if timeout
        """
        from yahoo.mission.scanner.scanner import Scanner
        
        logger.info(f"[COLLECTION] Starting scanner for Desk {desk_id} (timeout: {self.scanner_timeout}s)")
        
        # Create scanner instance
        scanner = Scanner()
        
        # Start scanner and wait for scan
        scan_path = scanner.wait_for_scan(timeout=self.scanner_timeout)
        
        if scan_path:
            logger.info(f"[COLLECTION] Scan completed at Desk {desk_id}: {scan_path}")
            return scan_path
        else:
            logger.warning(f"[COLLECTION] Scan timeout at Desk {desk_id} after {self.scanner_timeout}s")
            return None
    
    def reset(self):
        """Reset mission state."""
        self.current_stop = 4  # Reset to buffer stop
        logger.info("[COLLECTION] Mission reset")

