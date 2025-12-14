"""
Pass-Out Mission for row navigation.
Traverses stops 0→1→2→3→4 forward, distributing papers at desk stops (0-3).
Includes obstacle detection and avoidance.
"""
import logging
from typing import Optional

from yahoo.mission.obstacle_nav import ObstacleNavigator

logger = logging.getLogger(__name__)


class PassOutMission:
    """
    Pass-out mission that traverses row forward, distributing papers at desk stops.
    
    Route: Stop 0 (Desk 1) → Stop 1 (Desk 2) → Stop 2 (Desk 3) → Stop 3 (Desk 4) → Stop 4 (Buffer)
    """
    
    def __init__(self, robot, row_planner):
        """
        Initialize pass-out mission.
        
        Args:
            robot: Robot instance with drive subsystem
            row_planner: RowPathPlanner instance
        """
        self.robot = robot
        self.planner = row_planner
        self.current_stop = 0  # Track current position
        self.obstacle_nav = ObstacleNavigator(robot)  # Obstacle-aware navigation
        
        logger.info("[PASS-OUT] Mission initialized")
    
    def execute(self):
        """
        Execute the complete pass-out phase.
        
        Returns:
            dict with mission summary (desks_visited, papers_distributed, etc.)
        """
        logger.info("[PASS-OUT] Starting pass-out phase")
        
        route = self.planner.get_pass_out_route()
        papers_distributed = 0
        desks_visited = 0
        
        try:
            for stop_idx in route:
                logger.info(f"[PASS-OUT] Navigating to Stop {stop_idx}")
                self.navigate_to_stop(stop_idx)
                
                if self.planner.is_desk_stop(stop_idx):
                    # Desk stop - distribute paper
                    desk_id = self.planner.get_desk_for_stop(stop_idx)
                    desks_visited += 1
                    
                    logger.info(f"[PASS-OUT] Arrived at Stop {stop_idx} (Desk {desk_id})")
                    
                    if self.distribute_at_desk(stop_idx, desk_id):
                        papers_distributed += 1
                        logger.info(f"[PASS-OUT] Paper distributed at Desk {desk_id}")
                    else:
                        logger.info(f"[PASS-OUT] Skipped Desk {desk_id} (no person detected or other reason)")
                else:
                    # Stop 4 - buffer position, prepare for turn
                    logger.info(f"[PASS-OUT] Arrived at Stop {stop_idx} (Buffer - prepare for turn)")
                    self.prepare_for_turn()
            
            logger.info("[PASS-OUT] Pass-out phase complete")
            
            return {
                'success': True,
                'desks_visited': desks_visited,
                'papers_distributed': papers_distributed,
                'route_completed': True
            }
            
        except Exception as e:
            logger.error(f"[PASS-OUT] Error during pass-out: {e}")
            return {
                'success': False,
                'error': str(e),
                'desks_visited': desks_visited,
                'papers_distributed': papers_distributed
            }
    
    def navigate_to_stop(self, stop_index: int):
        """
        Navigate to a specific stop point.
        
        Args:
            stop_index: Target stop index (0-4)
        """
        if stop_index == self.current_stop:
            logger.debug(f"[PASS-OUT] Already at Stop {stop_index}")
            return
        
        # Calculate distance to travel
        distance_cm = self.planner.get_distance_to_stop(self.current_stop, stop_index)
        
        if distance_cm > 0:
            logger.info(f"[PASS-OUT] Moving {distance_cm:.1f}cm from Stop {self.current_stop} to Stop {stop_index}")
            
            # Use obstacle-aware navigation
            if hasattr(self.robot, 'drive') and self.robot.drive:
                success = self.obstacle_nav.drive_cm_safe(distance_cm, check_obstacles=True)
                if not success:
                    logger.warning("[PASS-OUT] Movement interrupted or failed")
            else:
                logger.warning("[PASS-OUT] Robot drive not available, simulating movement")
        
        # Update current position
        self.current_stop = stop_index
        logger.info(f"[PASS-OUT] Arrived at Stop {stop_index}")
    
    def distribute_at_desk(self, stop_index: int, desk_id: int) -> bool:
        """
        Distribute paper at a desk stop.
        
        Args:
            stop_index: Stop index (0-3)
            desk_id: Desk ID (1-4)
        
        Returns:
            True if paper was distributed, False if skipped
        """
        # TODO: Integrate with person detection if needed
        # For now, always distribute (can be extended later)
        
        logger.info(f"[PASS-OUT] Distributing paper at Desk {desk_id} (Stop {stop_index})")
        
        # Placeholder for actual distribution logic
        # This could involve:
        # - Person detection
        # - Mechanical paper drop
        # - Button confirmation
        # - LED feedback
        
        return True  # Assume success for now
    
    def prepare_for_turn(self):
        """
        Prepare for 180° turn at stop 4.
        This is a placeholder - actual turn happens in row_mission.py
        """
        logger.info("[PASS-OUT] Positioned at buffer stop, ready for 180° turn")
        # Turn logic will be handled by row_mission.py
    
    def reset(self):
        """Reset mission state."""
        self.current_stop = 0
        logger.info("[PASS-OUT] Mission reset")

