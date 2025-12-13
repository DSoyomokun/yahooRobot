#!/usr/bin/env python3
"""
Yahoo Robot Main Entry Point
Campus Package Service Robot
"""

import argparse
import logging
import sys
import subprocess
import time
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
                # Movement sequence with obstacle avoidance
                try:
                    # Initialize sensors: GoPiGo Distance Sensor + IMU
                    distance_sensor = None
                    imu = None
                    
                    if not robot.simulate and robot.gpg:
                        # Initialize GoPiGo Distance Sensor (I2C)
                        logger.info("Attempting to initialize distance sensor...")
                        try:
                            distance_sensor = robot.gpg.init_distance_sensor()
                            logger.info("  Sensor object created, testing readings...")
                            
                            # Test the sensor with multiple readings
                            test_readings = []
                            successful_reads = 0
                            
                            for i in range(5):
                                try:
                                    test_dist = distance_sensor.read_mm()
                                    test_readings.append(test_dist)
                                    successful_reads += 1
                                    logger.info(f"  Test read {i+1}: {test_dist} mm")
                                    time.sleep(0.2)
                                except (IOError, OSError) as e:
                                    logger.error(f"  ❌ Test read {i+1} failed: {e}")
                                    test_readings.append(None)
                                except AttributeError as e:
                                    logger.error(f"  ❌ Sensor method error: {e}")
                                    logger.error(f"  Sensor object: {distance_sensor}")
                                    logger.error(f"  Available methods: {dir(distance_sensor)}")
                                    break
                                except Exception as e:
                                    logger.error(f"  ❌ Unexpected error on read {i+1}: {e}")
                                    test_readings.append(None)
                            
                            if successful_reads > 0:
                                valid_readings = [r for r in test_readings if r is not None]
                                logger.info("=" * 60)
                                logger.info("✅ GoPiGo Distance Sensor WORKING!")
                                logger.info(f"  Successful reads: {successful_reads}/5")
                                logger.info(f"  Valid readings: {valid_readings} mm")
                                logger.info("=" * 60)
                            else:
                                logger.error("=" * 60)
                                logger.error("❌ Distance sensor NOT WORKING!")
                                logger.error("  All test reads failed")
                                logger.error("=" * 60)
                                logger.error("TROUBLESHOOTING:")
                                logger.error("  1. Check sensor is connected to I2C port")
                                logger.error("  2. Verify I2C is enabled: sudo raspi-config")
                                logger.error("  3. Check I2C devices: sudo i2cdetect -y 1")
                                logger.error("  4. Try unplugging and reconnecting sensor")
                                logger.error("  5. Check sensor power (should be on)")
                                distance_sensor = None
                        except AttributeError as e:
                            logger.error(f"❌ init_distance_sensor() method not found: {e}")
                            logger.error("  Available methods: " + ", ".join([m for m in dir(robot.gpg) if 'distance' in m.lower() or 'sensor' in m.lower()]))
                            distance_sensor = None
                        except Exception as e:
                            logger.error(f"❌ Could not initialize distance sensor: {e}")
                            logger.error(f"  Error type: {type(e).__name__}")
                            logger.error("  Robot will run WITHOUT obstacle detection")
                            logger.error("  ⚠️  WARNING: Robot may collide with objects!")
                            distance_sensor = None
                        
                        # Initialize IMU (Inertial Measurement Unit)
                        # Try different methods to access IMU
                        imu = None
                        logger.info("Attempting to initialize IMU sensor...")
                        
                        # Method 1: Try di_sensors library (recommended method)
                        try:
                            from di_sensors.inertial_measurement_unit import InertialMeasurementUnit
                            logger.info("  Trying di_sensors library...")
                            # Try different I2C bus options
                            for bus_name in ["GPG3_AD1", "GPG3_AD2", "RPI_1"]:
                                try:
                                    imu = InertialMeasurementUnit(bus=bus_name)
                                    # Test if it works by reading once
                                    test_read = imu.read_euler()
                                    logger.info(f"✅ IMU initialized via di_sensors on bus: {bus_name}")
                                    break
                                except Exception as bus_error:
                                    logger.debug(f"    Bus {bus_name} failed: {bus_error}")
                                    continue
                        except ImportError:
                            logger.debug("  di_sensors library not available")
                        except Exception as e:
                            logger.debug(f"  di_sensors method failed: {e}")
                        
                        # Method 2: Try easygopigo3 init_imu()
                        if imu is None:
                            try:
                                logger.info("  Trying easygopigo3.init_imu()...")
                                if hasattr(robot.gpg, 'init_imu'):
                                    imu = robot.gpg.init_imu()
                                    logger.info("✅ IMU initialized via init_imu()")
                            except Exception as e:
                                logger.debug(f"  init_imu() failed: {e}")
                        
                        # Method 3: Try accessing IMU directly
                        if imu is None:
                            try:
                                logger.info("  Trying gpg.imu direct access...")
                                if hasattr(robot.gpg, 'imu'):
                                    imu = robot.gpg.imu
                                    logger.info("✅ IMU accessed via gpg.imu")
                            except Exception as e:
                                logger.debug(f"  gpg.imu failed: {e}")
                        
                        # Method 4: Try init_gyroscope() or similar
                        if imu is None:
                            try:
                                logger.info("  Trying init_gyroscope()...")
                                if hasattr(robot.gpg, 'init_gyroscope'):
                                    imu = robot.gpg.init_gyroscope()
                                    logger.info("✅ IMU initialized via init_gyroscope()")
                            except Exception as e:
                                logger.debug(f"  init_gyroscope() failed: {e}")
                        
                        # If still no IMU, provide detailed diagnostics
                        if imu is None:
                            logger.warning("=" * 60)
                            logger.warning("⚠️  IMU sensor NOT detected!")
                            logger.warning("=" * 60)
                            
                            # List available methods for debugging
                            available_methods = [m for m in dir(robot.gpg) if not m.startswith('_')]
                            sensor_methods = [m for m in available_methods if 'imu' in m.lower() or 'gyro' in m.lower() or 'accel' in m.lower()]
                            
                            logger.warning("TROUBLESHOOTING STEPS:")
                            logger.warning("  1. Check IMU sensor is connected to I2C port (AD1 or AD2)")
                            logger.warning("  2. Verify I2C is enabled: sudo raspi-config → Interface Options → I2C")
                            logger.warning("  3. Check I2C devices: sudo i2cdetect -y 1")
                            logger.warning("  4. Install di_sensors library:")
                            logger.warning("     curl -kL dexterindustries.com/update_sensors | bash")
                            logger.warning("  5. Update GoPiGo3 firmware:")
                            logger.warning("     curl -kL dexterindustries.com/update_gopigo3 | bash")
                            logger.warning("")
                            if sensor_methods:
                                logger.warning(f"  Available sensor methods: {sensor_methods}")
                            else:
                                logger.warning("  No IMU-related methods found in easygopigo3")
                            logger.warning("=" * 60)
                        else:
                            logger.info("✅ IMU sensor ready!")
                    else:
                        logger.info("Running in simulation mode - sensors disabled")
                    
                    # Warn if no obstacle detection
                    if distance_sensor is None and not robot.simulate:
                        logger.error("=" * 60)
                        logger.error("⚠️  WARNING: NO OBSTACLE DETECTION AVAILABLE!")
                        logger.error("  The robot will NOT stop for obstacles.")
                        logger.error("  Make sure you have clear space before running.")
                        logger.error("=" * 60)
                    
                    # Constants for movement and obstacle detection
                    FEET_TO_CM = 30.48  # 1 foot = 30.48 cm
                    DISTANCE_HALF_FT_CM = 0.5 * FEET_TO_CM  # 15.24 cm
                    OBSTACLE_THRESHOLD_CM = 1.0 * FEET_TO_CM  # 30.48 cm (1 foot)
                    TURN_90_DEGREES = 90
                    TURN_180_DEGREES = 180
                    CHECK_INTERVAL = 0.1  # Check distance every 100ms (reduced to prevent I/O errors)
                    DRIVE_SPEED_DPS = 200  # Speed for forward movement
                    # Approximate speed: 200 DPS ≈ 6.8 cm/s (based on GoPiGo3 wheel diameter)
                    CM_PER_SECOND = 6.8
                    
                    def check_obstacle():
                        """Check if obstacle is within threshold using distance sensor"""
                        if distance_sensor:
                            try:
                                # Read distance from GoPiGo Distance Sensor with retry logic
                                distance_mm = None
                                max_retries = 3
                                
                                for attempt in range(max_retries):
                                    try:
                                        distance_mm = distance_sensor.read_mm()
                                        break  # Success, exit retry loop
                                    except (IOError, OSError) as e:
                                        if attempt < max_retries - 1:
                                            time.sleep(0.01)  # Brief delay before retry
                                            continue
                                        else:
                                            # Last attempt failed, log and return safe value
                                            logger.debug(f"Distance sensor I/O error after {max_retries} attempts: {e}")
                                            return False, None
                                    except Exception as e:
                                        # Other errors - log once and return safe value
                                        logger.debug(f"Distance sensor error: {e}")
                                        return False, None
                                
                                if distance_mm is None:
                                    return False, None
                                
                                distance_cm = distance_mm / 10.0
                                
                                # Filter out invalid readings (sensor returns 0 or very large values when out of range)
                                if distance_cm < 2 or distance_cm > 400:
                                    return False, None
                                
                                return distance_cm < OBSTACLE_THRESHOLD_CM, distance_cm
                            except Exception as e:
                                # Catch any unexpected errors
                                logger.debug(f"Unexpected error reading distance sensor: {e}")
                                return False, None
                        return False, None
                    
                    def get_heading():
                        """Get current heading from IMU if available"""
                        if imu is not None:
                            try:
                                euler = imu.read_euler()
                                if isinstance(euler, (list, tuple)) and len(euler) >= 3:
                                    return float(euler[2])  # Yaw angle
                                elif isinstance(euler, dict):
                                    return float(euler.get('yaw', euler.get('heading', euler.get('z', 0))))
                            except Exception as e:
                                logger.debug(f"IMU read error: {e}")
                        return None
                    
                    def avoid_obstacle():
                        """
                        Perform tight, quick obstacle avoidance with path recovery using IMU.
                        Goes around obstacle and returns to original straight-line path.
                        
                        Strategy (tightened for speed): 
                        1. Record initial heading (IMU)
                        2. Turn right 90°
                        3. Move forward to clear obstacle (0.75 feet - tighter)
                        4. Turn left 90° to move parallel to original path
                        5. Move forward past obstacle (0.25 feet - tighter)
                        6. Turn left 90° to return to path
                        7. Move forward to path line (0.75 feet - tighter)
                        8. Turn right 90° to resume heading
                        9. Verify heading matches initial heading (IMU correction if needed)
                        """
                        logger.warning("🚨 Obstacle detected! Performing avoidance maneuver...")
                        
                        # Record initial heading for path recovery
                        initial_heading = get_heading()
                        if initial_heading is not None:
                            logger.info(f"  Initial heading: {initial_heading:.1f}°")
                        
                        # Step 1: Turn right 90 degrees to go around obstacle
                        logger.info("  → Step 1: Turning right 90 degrees...")
                        robot.drive.turn_degrees(TURN_90_DEGREES)
                        
                        # Step 2: Move forward to clear the obstacle (tighter: 0.75 feet)
                        AVOIDANCE_SIDE_DISTANCE = 0.75 * FEET_TO_CM  # 22.86 cm (tighter)
                        logger.info("  → Step 2: Moving forward 0.75 feet to clear obstacle...")
                        
                        # Check for obstacles while moving around (faster speed during avoidance)
                        AVOIDANCE_SPEED_DPS = 250  # Faster than normal (250 vs 200 DPS)
                        robot.drive.forward(AVOIDANCE_SPEED_DPS)
                        start_time = time.time()
                        AVOIDANCE_CM_PER_SECOND = 8.5  # Faster speed estimate
                        side_time = AVOIDANCE_SIDE_DISTANCE / AVOIDANCE_CM_PER_SECOND
        
                        while time.time() - start_time < side_time:
                            has_obstacle, dist = check_obstacle()
                            if has_obstacle:
                                robot.drive.stop()
                                logger.warning(f"  ⚠️  Obstacle still detected at {dist:.1f}cm - adjusting...")
                                # Move a bit more to clear
                                robot.drive.drive_cm(5)  # Extra 5cm (reduced from 10cm)
                                break
                            time.sleep(CHECK_INTERVAL)
                        robot.drive.stop()
                        
                        # Step 3: Turn left 90 degrees to move parallel to original path
                        logger.info("  → Step 3: Turning left 90 degrees...")
                        robot.drive.turn_degrees(-TURN_90_DEGREES)
                        
                        # Step 4: Move forward parallel to original path (0.50 feet)
                        AVOIDANCE_PARALLEL_DISTANCE = 0.50 * FEET_TO_CM  # 15.24 cm
                        logger.info("  → Step 4: Moving forward 0.50 feet parallel to path...")
                        robot.drive.forward(AVOIDANCE_SPEED_DPS)
                        time.sleep(AVOIDANCE_PARALLEL_DISTANCE / AVOIDANCE_CM_PER_SECOND)
                        robot.drive.stop()
                        
                        # Step 5: Turn left 90 degrees to face back toward original path
                        logger.info("  → Step 5: Turning left 90 degrees...")
                        robot.drive.turn_degrees(-TURN_90_DEGREES)
                        
                        # Step 6: Move forward to return to original path line (tighter: 0.75 feet)
                        logger.info("  → Step 6: Moving forward 0.75 feet to return to path...")
                        robot.drive.forward(AVOIDANCE_SPEED_DPS)
                        time.sleep(AVOIDANCE_SIDE_DISTANCE / AVOIDANCE_CM_PER_SECOND)
                        robot.drive.stop()
                        
                        # Step 7: Turn right 90 degrees to resume original heading
                        logger.info("  → Step 7: Turning right 90 degrees to resume heading...")
                        robot.drive.turn_degrees(TURN_90_DEGREES)
                        
                        # Step 8: Verify and correct heading using IMU
                        if initial_heading is not None:
                            time.sleep(0.2)  # Reduced stabilization time (0.2s vs 0.5s for speed)
                            final_heading = get_heading()
                            if final_heading is not None:
                                heading_error = abs(final_heading - initial_heading)
                                # Normalize to -180 to 180 range
                                if heading_error > 180:
                                    heading_error = 360 - heading_error
                                
                                if heading_error > 10:  # If error > 10 degrees, correct it
                                    logger.info(f"  → Step 8: Correcting heading error ({heading_error:.1f}°)...")
                                    correction = initial_heading - final_heading
                                    # Normalize correction
                                    if correction > 180:
                                        correction -= 360
                                    elif correction < -180:
                                        correction += 360
                                    robot.drive.turn_degrees(correction)
                                    logger.info(f"  ✅ Heading corrected to {initial_heading:.1f}°")
                                else:
                                    logger.info(f"  ✅ Heading verified: {final_heading:.1f}° (error: {heading_error:.1f}°)")
                        
                        logger.info("✅ Obstacle avoidance complete. Resumed on original path.")
                    
                    # ============================================================
                    # CONTINUOUS FORWARD MOVEMENT WITH OBSTACLE AVOIDANCE
                    # ============================================================
                    logger.info("=" * 60)
                    logger.info("CONTINUOUS FORWARD MOVEMENT WITH OBSTACLE DETECTION")
                    logger.info("=" * 60)
                    logger.info("Robot will move forward continuously")
                    logger.info("Obstacle detection:")
                    logger.info(f"  - Distance sensor: {OBSTACLE_THRESHOLD_CM:.1f}cm (1 foot)")
                    logger.info("  - IMU: For orientation tracking and path recovery")
                    logger.info("  - Robot will go around obstacles and continue straight path")
                    logger.info("")
                    logger.info("Press Ctrl+C to stop")
                    logger.info("=" * 60)
                    logger.info("")
                    
                    if distance_sensor is None:
                        logger.error("❌ Distance sensor not available!")
                        logger.error("  Cannot run without obstacle detection")
                        raise Exception("Distance sensor not initialized")
                    
                    if imu is None:
                        logger.warning("⚠️  IMU not available - path recovery may be less accurate")
                    
                    # Start continuous forward movement
                    logger.info("Starting continuous forward movement...")
                    robot.drive.forward(DRIVE_SPEED_DPS)
                    
                    start_time = time.time()
                    last_log_time = 0
                    obstacle_count = 0
                    
                    try:
                        while True:
                            # Check for obstacles continuously
                            has_obstacle, dist = check_obstacle()
                            
                            if has_obstacle:
                                # Stop immediately when obstacle detected
                                robot.drive.stop()
                                obstacle_count += 1
                                elapsed = time.time() - start_time
                                
                                logger.warning("")
                                logger.warning(f"🚨 OBSTACLE #{obstacle_count} DETECTED!")
                                logger.warning(f"  Distance: {dist:.1f} cm ({dist/30.48:.2f} feet)")
                                logger.warning(f"  Traveled for: {elapsed:.1f} seconds")
                                
                                # Perform robust avoidance maneuver with path recovery
                                avoid_obstacle()
                                
                                # Resume forward movement
                                logger.info("Resuming forward movement...")
                                robot.drive.forward(DRIVE_SPEED_DPS)
                                start_time = time.time()  # Reset timer
                            
                            # Log distance periodically (every second)
                            elapsed = time.time() - start_time
                            if int(elapsed) > last_log_time:
                                if dist is not None:
                                    logger.info(f"  Distance: {dist:5.1f} cm ({dist/30.48:4.2f} ft) | Elapsed: {elapsed:5.1f}s | Obstacles avoided: {obstacle_count}")
                                last_log_time = int(elapsed)
                            
                            time.sleep(CHECK_INTERVAL)
                            
                    except KeyboardInterrupt:
                        robot.drive.stop()
                        elapsed = time.time() - start_time
                        logger.info("")
                        logger.info("=" * 60)
                        logger.info("⚠️  Movement stopped by user")
                        logger.info(f"  Total time: {elapsed:.1f} seconds")
                        logger.info(f"  Obstacles avoided: {obstacle_count}")
                        logger.info("=" * 60)
                    
                    # Ensure robot is stopped
                    robot.drive.stop()
                    
                    logger.info("")
                    logger.info("=" * 60)
                    logger.info("✅ Movement complete!")
                    logger.info("=" * 60)
                    

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

