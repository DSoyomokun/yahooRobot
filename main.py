#!/usr/bin/env python3
"""
Yahoo Robot Main Entry Point
Campus Package Service Robot
"""

import argparse
import logging
import sys
import subprocess
from pathlib import Path
from yahoo.robot import Robot


def setup_logging(level=logging.INFO):
    """Configure logging for the application"""
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('build-log/robot.log'),
            logging.StreamHandler(sys.stdout)
        ]
    )


def run_test(test_name):
    """Run a test script"""
    project_root = Path(__file__).parent
    
    # Map of test names to their script paths
    test_scripts = {
        'mac': 'tests/test_gesture_mac.py',
        'camera': 'scripts/camera_test.py',
        'gesture': 'tests/test_gesture_mac.py',  # alias
        'pi_camera': 'tests/test_pi_camera.py',  # Pi camera test
    }
    
    if test_name not in test_scripts:
        print(f"❌ Unknown test: {test_name}")
        print(f"\nAvailable tests:")
        for name in test_scripts.keys():
            print(f"  - {name}")
        return 1
    
    script_path = project_root / test_scripts[test_name]
    
    if not script_path.exists():
        print(f"❌ Test script not found: {script_path}")
        return 1
    
    print(f"🚀 Running test: {test_name}")
    print(f"   Script: {script_path}\n")
    
    # Run the test script
    result = subprocess.run([sys.executable, str(script_path)])
    return result.returncode


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Yahoo Robot - Campus Package Service Robot',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    # Create subparsers for commands
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # 'run' command (default robot operation)
    run_parser = subparsers.add_parser('run', help='Run the robot (default)')
    run_parser.add_argument('--simulate', action='store_true', 
                           help='Run in simulation mode without hardware')
    run_parser.add_argument('--debug', action='store_true',
                           help='Enable debug logging')
    run_parser.add_argument('--webui', action='store_true',
                           help='Start web interface')
    
    # 'test' command
    test_parser = subparsers.add_parser('test', help='Run test scripts')
    test_parser.add_argument('test_name', nargs='?', 
                           help='Name of test to run (mac, camera, gesture)')
    test_parser.add_argument('--list', action='store_true',
                           help='List available tests')
    
    # Parse arguments
    args = parser.parse_args()
    
    # Handle 'test' command
    if args.command == 'test':
        if args.list:
            print("Available tests:")
            print("  mac      - Gesture detection test (Mac)")
            print("  camera   - Camera test")
            print("  gesture  - Gesture detection test (alias for mac)")
            return 0
        
        if not args.test_name:
            print("❌ Please specify a test name")
            print("   Use 'python main.py test --list' to see available tests")
            return 1
        
        return run_test(args.test_name)
    
    # Default to 'run' command if no command specified
    # Handle backward compatibility - if no command but old-style args, treat as run
    if args.command is None:
        # Re-parse with old-style arguments for backward compatibility
        old_parser = argparse.ArgumentParser(description='Yahoo Robot - Campus Package Service Robot')
        old_parser.add_argument('--simulate', action='store_true', 
                               help='Run in simulation mode without hardware')
        old_parser.add_argument('--debug', action='store_true',
                               help='Enable debug logging')
        old_parser.add_argument('--webui', action='store_true',
                               help='Start web interface')
        args = old_parser.parse_args()
        simulate = args.simulate
        webui = args.webui
        log_level = logging.DEBUG if args.debug else logging.INFO
    else:
        # New style with subcommands
        simulate = args.simulate if args.command == 'run' else False
        webui = args.webui if args.command == 'run' else False
        log_level = logging.DEBUG if (args.command == 'run' and args.debug) else logging.INFO
    
    # Setup logging
    setup_logging(log_level)
    
    logger = logging.getLogger(__name__)
    logger.info("Starting Yahoo Robot...")
    
    try:
        # Initialize robot
        with Robot(simulate=simulate) as robot:
            logger.info(f"Battery: {robot.get_battery_voltage():.2f}V")
            
            if webui:
                logger.info("Starting web interface...")
                # TODO: Import and start Flask app
                pass
            else:
                logger.info("Robot ready. Starting movement sequence...")
                import time

                # Movement sequence: forward 4s, stop 2s, turn 180°, stop 1s, forward 4s, turn 180°, stop
                try:
                    # Step 1: Move forward at 200 DPS for 4 seconds
                    logger.info("Step 1: Moving forward at 200 DPS for 4 seconds...")
                    robot.drive.forward(200)
                    time.sleep(4)

                    # Step 2: Stop for 2 seconds
                    logger.info("Step 2: Stopping for 2 seconds...")
                    robot.drive.stop()
                    time.sleep(2)

                    logger.info("Step 1: Moving forward at 200 DPS for 4 seconds...")
                    robot.drive.forward(200)
                    time.sleep(4)

                    # Step 2: Stop for 2 seconds
                    logger.info("Step 2: Stopping for 2 seconds...")
                    robot.drive.stop()
                    time.sleep(2)

                    logger.info("Step 1: Moving forward at 200 DPS for 4 seconds...")
                    robot.drive.forward(200)
                    time.sleep(4)

                    # Step 2: Stop for 2 seconds
                    logger.info("Step 2: Stopping for 2 seconds...")
                    robot.drive.stop()
                    time.sleep(2)

                    # Step 6: Rotate 180 degrees again
                    logger.info("Step 6: Rotating 180 degrees again...")
                    robot.drive.turn_degrees(180)

                    logger.info("Step 1: Moving forward at 200 DPS for 4 seconds...")
                    robot.drive.forward(600)
                    time.sleep(4)
                    

                    logger.info("Movement sequence complete. Press Ctrl+C to exit.")
                    while True:
                        time.sleep(1)

                except Exception as e:
                    logger.error(f"Movement error: {e}")
                    robot.drive.stop()
    
    except KeyboardInterrupt:
        logger.info("Shutting down...")
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())

