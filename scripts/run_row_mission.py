#!/usr/bin/env python3
"""
Run the complete row mission cycle:
- Pass-out: Move 60 inches 5 times (stops 0-4)
- Turn 180° at stop 4
- Collection: Reverse with scanner (stops 4-0)

Usage:
    python3 scripts/run_row_mission.py
    (Must be run from project root directory)
"""
import sys
import os
from pathlib import Path

# Add project root to path
# This script should be in scripts/ directory, so parent is project root
_script_dir = Path(__file__).parent.resolve()
_project_root = _script_dir.parent.resolve()

# Verify we found the project root (should contain yahoo/ directory)
if not (_project_root / "yahoo").exists():
    print(f"❌ ERROR: Cannot find project root!")
    print(f"   Script location: {_script_dir}")
    print(f"   Expected project root: {_project_root}")
    print(f"   yahoo/ directory not found at: {_project_root / 'yahoo'}")
    print("\n💡 Make sure you're running from the project root:")
    print("   cd ~/yahooRobot")
    print("   python3 scripts/run_row_mission.py")
    sys.exit(1)

# Add project root to Python path
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

# Change to project root directory for relative paths to work
os.chdir(_project_root)

import logging
from yahoo.robot import Robot
from yahoo.mission.row_mission import RowMission

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


def main():
    """Main entry point for row mission."""
    print("=" * 70)
    print("ROW MISSION - Full Cycle")
    print("=" * 70)
    print("\nThis will:")
    print("  1. Move forward 60 inches, 5 times (stops 0→1→2→3→4)")
    print("  2. Turn 180° at stop 4")
    print("  3. Move backward with scanner (stops 4→3→2→1→0)")
    print()
    
    # Initialize robot
    # Set simulate=True for testing without hardware
    simulate = False  # Change to True for testing
    robot = Robot(simulate=simulate)
    
    try:
        # Create row mission
        mission = RowMission(robot, scanner_timeout=30.0)
        
        # Execute full cycle
        print("\n🚀 Starting full cycle...\n")
        results = mission.execute_full_cycle()
        
        # Print final results
        print("\n" + "=" * 70)
        if results.get('overall_success'):
            print("✅ MISSION COMPLETED SUCCESSFULLY!")
        else:
            print("❌ MISSION FAILED")
            if results.get('error'):
                print(f"Error: {results['error']}")
        print("=" * 70)
        
        return 0 if results.get('overall_success') else 1
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Mission interrupted by user")
        return 1
    except Exception as e:
        print(f"\n\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    finally:
        # Cleanup
        if hasattr(robot, 'drive'):
            robot.drive.stop()


if __name__ == "__main__":
    sys.exit(main())

