#!/usr/bin/env python3
"""
CPSR Main Entry Point
Campus Package Service Robot
"""

import argparse
import logging
import sys
from cpsr.robot import Robot


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


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='CPSR - Campus Package Service Robot')
    parser.add_argument('--simulate', action='store_true', 
                       help='Run in simulation mode without hardware')
    parser.add_argument('--debug', action='store_true',
                       help='Enable debug logging')
    parser.add_argument('--webui', action='store_true',
                       help='Start web interface')
    
    args = parser.parse_args()
    
    # Setup logging
    log_level = logging.DEBUG if args.debug else logging.INFO
    setup_logging(log_level)
    
    logger = logging.getLogger(__name__)
    logger.info("Starting CPSR...")
    
    try:
        # Initialize robot
        with Robot(simulate=args.simulate) as robot:
            logger.info(f"Battery: {robot.get_battery_voltage():.2f}V")
            
            if args.webui:
                logger.info("Starting web interface...")
                # TODO: Import and start Flask app
                pass
            else:
                logger.info("Robot ready. Press Ctrl+C to exit.")
                # TODO: Start main control loop
                import time
                while True:
                    time.sleep(1)
    
    except KeyboardInterrupt:
        logger.info("Shutting down...")
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())

