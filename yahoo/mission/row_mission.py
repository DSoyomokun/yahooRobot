"""
Unified Row Mission Controller.
Combines pass-out and collection phases with 180° turn at stop 4.
"""
import logging
from typing import Optional, Dict

from yahoo.config.row_loader import RowConfig
from yahoo.mission.row_path_planner import RowPathPlanner
from yahoo.mission.pass_out import PassOutMission
from yahoo.mission.collection import CollectionMission

logger = logging.getLogger(__name__)


class RowMission:
    """
    Unified mission controller for complete row traversal cycle.
    
    Flow:
    1. Pass-out phase: Stops 0→1→2→3→4 (forward)
    2. 180° turn at Stop 4
    3. Collection phase: Stops 4→3→2→1→0 (reverse, with scanning)
    """
    
    def __init__(self, robot, config_path: Optional[str] = None, scanner_timeout: float = 30.0):
        """
        Initialize row mission controller.
        
        Args:
            robot: Robot instance with drive subsystem
            config_path: Optional path to row_config.json (default: uses default location)
            scanner_timeout: Timeout in seconds for scanner during collection (default: 30.0)
        """
        self.robot = robot
        self.config = RowConfig(config_path)
        self.scanner_timeout = scanner_timeout
        
        # Get origin from config
        origin = self.config.get_origin()
        
        # Get stop spacing from config
        stop_spacing = self.config.get_stop_spacing()
        
        # Initialize path planner
        self.planner = RowPathPlanner(
            stop_spacing_inches=stop_spacing,
            origin_position=origin
        )
        
        # Initialize missions
        self.pass_out = PassOutMission(robot, self.planner)
        self.collection = CollectionMission(robot, self.planner, scanner_timeout)
        
        logger.info("[ROW-MISSION] Row mission controller initialized")
    
    def execute_pass_out(self) -> Dict:
        """
        Execute pass-out phase only.
        
        Returns:
            dict with pass-out mission results
        """
        logger.info("[ROW-MISSION] Executing pass-out phase")
        return self.pass_out.execute()
    
    def execute_collection(self) -> Dict:
        """
        Execute collection phase only.
        
        Returns:
            dict with collection mission results
        """
        logger.info("[ROW-MISSION] Executing collection phase")
        return self.collection.execute()
    
    def turn_180_degrees(self):
        """
        Execute 180° turn at stop 4 (buffer position).
        This positions the robot for reverse traversal.
        """
        logger.info("[ROW-MISSION] Executing 180° turn at Stop 4")
        
        if hasattr(self.robot, 'drive') and self.robot.drive:
            # Turn 180 degrees (can be left or right, using right as default)
            self.robot.drive.turn_degrees(180.0)
            logger.info("[ROW-MISSION] 180° turn complete")
        else:
            logger.warning("[ROW-MISSION] Robot drive not available, simulating 180° turn")
    
    def execute_full_cycle(self) -> Dict:
        """
        Execute complete cycle: pass-out → turn → collection.
        
        Returns:
            dict with combined mission results
        """
        logger.info("[ROW-MISSION] Starting full cycle: pass-out → turn → collection")
        
        results = {
            'pass_out': None,
            'turn': {'success': False},
            'collection': None,
            'overall_success': False
        }
        
        try:
            # Phase 1: Pass-out
            logger.info("[ROW-MISSION] === PHASE 1: PASS-OUT ===")
            results['pass_out'] = self.execute_pass_out()
            
            if not results['pass_out'].get('success', False):
                logger.error("[ROW-MISSION] Pass-out phase failed, aborting cycle")
                results['overall_success'] = False
                return results
            
            # Phase 2: 180° turn at Stop 4
            logger.info("[ROW-MISSION] === PHASE 2: 180° TURN ===")
            try:
                self.turn_180_degrees()
                results['turn'] = {'success': True}
            except Exception as e:
                logger.error(f"[ROW-MISSION] Turn failed: {e}")
                results['turn'] = {'success': False, 'error': str(e)}
                results['overall_success'] = False
                return results
            
            # Phase 3: Collection
            logger.info("[ROW-MISSION] === PHASE 3: COLLECTION ===")
            results['collection'] = self.execute_collection()
            
            if not results['collection'].get('success', False):
                logger.error("[ROW-MISSION] Collection phase failed")
                results['overall_success'] = False
                return results
            
            # All phases completed successfully
            results['overall_success'] = True
            logger.info("[ROW-MISSION] Full cycle completed successfully")
            
            # Print summary
            self._print_summary(results)
            
        except Exception as e:
            logger.error(f"[ROW-MISSION] Error during full cycle: {e}")
            results['overall_success'] = False
            results['error'] = str(e)
        
        return results
    
    def _print_summary(self, results: Dict):
        """Print mission summary."""
        print("=" * 70)
        print("ROW MISSION SUMMARY")
        print("=" * 70)
        
        # Pass-out summary
        if results.get('pass_out'):
            po = results['pass_out']
            print(f"\nPass-Out Phase:")
            print(f"  Desks visited: {po.get('desks_visited', 0)}")
            print(f"  Papers distributed: {po.get('papers_distributed', 0)}")
            print(f"  Success: {po.get('success', False)}")
        
        # Turn summary
        if results.get('turn'):
            turn = results['turn']
            print(f"\n180° Turn:")
            print(f"  Success: {turn.get('success', False)}")
        
        # Collection summary
        if results.get('collection'):
            col = results['collection']
            print(f"\nCollection Phase:")
            print(f"  Desks visited: {col.get('desks_visited', 0)}")
            print(f"  Papers collected: {col.get('papers_collected', 0)}")
            print(f"  Timeouts: {col.get('timeouts', 0)}")
            print(f"  Success: {col.get('success', False)}")
        
        # Overall
        print(f"\nOverall Success: {results.get('overall_success', False)}")
        print("=" * 70)
    
    def reset(self):
        """Reset all mission states."""
        self.pass_out.reset()
        self.collection.reset()
        logger.info("[ROW-MISSION] All missions reset")

