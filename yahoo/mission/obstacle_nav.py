"""
Obstacle-aware navigation for row missions.
Provides safe movement with obstacle detection and go-around maneuver.
"""
import logging
import time
from typing import Optional, Tuple

logger = logging.getLogger(__name__)

# Constants
FEET_TO_CM = 30.48
OBSTACLE_THRESHOLD_CM = 30.48  # 1 foot
TURN_90_DEGREES = 90
CHECK_INTERVAL = 0.1  # Check distance every 100ms
AVOIDANCE_SPEED_DPS = 250  # Faster speed during avoidance
AVOIDANCE_CM_PER_SECOND = 8.5  # Approximate speed during avoidance


class ObstacleNavigator:
    """
    Obstacle-aware navigation helper.
    Provides safe movement with continuous obstacle detection and avoidance.
    """
    
    def __init__(self, robot):
        """
        Initialize obstacle navigator.
        
        Args:
            robot: Robot instance with drive subsystem and gpg (GoPiGo3)
        """
        self.robot = robot
        self.distance_sensor = None
        self.imu = None
        self._init_sensors()
    
    def _init_sensors(self):
        """Initialize distance sensor and IMU if available."""
        if self.robot.simulate or not self.robot.gpg:
            logger.info("[OBSTACLE-NAV] Running in simulation mode - sensors disabled")
            return
        
        # Initialize distance sensor
        try:
            self.distance_sensor = self.robot.gpg.init_distance_sensor()
            logger.info("[OBSTACLE-NAV] Distance sensor initialized")
        except Exception as e:
            logger.warning(f"[OBSTACLE-NAV] Distance sensor not available: {e}")
            self.distance_sensor = None
        
        # Initialize IMU (try multiple methods)
        try:
            from di_sensors.inertial_measurement_unit import InertialMeasurementUnit
            for bus_name in ["GPG3_AD1", "GPG3_AD2", "RPI_1"]:
                try:
                    self.imu = InertialMeasurementUnit(bus=bus_name)
                    test_read = self.imu.read_euler()
                    logger.info(f"[OBSTACLE-NAV] IMU initialized on bus: {bus_name}")
                    break
                except:
                    continue
        except ImportError:
            pass
        
        if self.imu is None and self.robot.gpg:
            # Try easygopigo3 methods
            if hasattr(self.robot.gpg, 'init_imu'):
                try:
                    self.imu = self.robot.gpg.init_imu()
                    logger.info("[OBSTACLE-NAV] IMU initialized via init_imu()")
                except:
                    pass
        
        if self.distance_sensor is None and not self.robot.simulate:
            logger.warning("[OBSTACLE-NAV] ⚠️  No obstacle detection available!")
    
    def check_obstacle(self) -> Tuple[bool, Optional[float]]:
        """
        Check if obstacle is within threshold.
        
        Returns:
            Tuple of (has_obstacle: bool, distance_cm: float or None)
        """
        if not self.distance_sensor:
            return False, None
        
        try:
            distance_mm = self.distance_sensor.read_mm()
            distance_cm = distance_mm / 10.0
            
            # Filter invalid readings
            if distance_cm < 2 or distance_cm > 400:
                return False, None
            
            return distance_cm < OBSTACLE_THRESHOLD_CM, distance_cm
        except Exception as e:
            logger.debug(f"[OBSTACLE-NAV] Distance sensor error: {e}")
            return False, None
    
    def get_heading(self) -> Optional[float]:
        """Get current heading from IMU if available."""
        if not self.imu:
            return None
        
        try:
            euler = self.imu.read_euler()
            if isinstance(euler, (list, tuple)) and len(euler) >= 3:
                return float(euler[2])  # Yaw angle
            elif isinstance(euler, dict):
                return float(euler.get('yaw', euler.get('heading', euler.get('z', 0))))
        except Exception as e:
            logger.debug(f"[OBSTACLE-NAV] IMU read error: {e}")
        
        return None
    
    def avoid_obstacle(self):
        """
        Perform go-around obstacle avoidance maneuver.
        Goes around obstacle and returns to original path.
        """
        logger.warning("[OBSTACLE-NAV] 🚨 Obstacle detected! Performing avoidance maneuver...")
        
        # Record initial heading for path recovery
        initial_heading = self.get_heading()
        if initial_heading is not None:
            logger.info(f"[OBSTACLE-NAV] Initial heading: {initial_heading:.1f}°")
        
        # Step 1: Turn right 90 degrees
        logger.info("[OBSTACLE-NAV] → Step 1: Turning right 90 degrees...")
        self.robot.drive.turn_degrees(TURN_90_DEGREES)
        
        # Step 2: Move forward to clear obstacle (0.75 feet)
        AVOIDANCE_SIDE_DISTANCE = 0.75 * FEET_TO_CM  # 22.86 cm
        logger.info("[OBSTACLE-NAV] → Step 2: Moving forward 0.75 feet to clear obstacle...")
        self.robot.drive.forward(AVOIDANCE_SPEED_DPS)
        
        # Check for obstacles while moving around
        start_time = time.time()
        side_time = AVOIDANCE_SIDE_DISTANCE / AVOIDANCE_CM_PER_SECOND
        
        while time.time() - start_time < side_time:
            has_obstacle, dist = self.check_obstacle()
            if has_obstacle:
                self.robot.drive.stop()
                logger.warning(f"[OBSTACLE-NAV] ⚠️  Obstacle still detected at {dist:.1f}cm - adjusting...")
                self.robot.drive.drive_cm(5)  # Extra 5cm to clear
                break
            time.sleep(CHECK_INTERVAL)
        self.robot.drive.stop()
        
        # Step 3: Turn left 90 degrees to move parallel to original path
        logger.info("[OBSTACLE-NAV] → Step 3: Turning left 90 degrees...")
        self.robot.drive.turn_degrees(-TURN_90_DEGREES)
        
        # Step 4: Move forward parallel to original path (0.50 feet)
        AVOIDANCE_PARALLEL_DISTANCE = 0.50 * FEET_TO_CM  # 15.24 cm
        logger.info("[OBSTACLE-NAV] → Step 4: Moving forward 0.50 feet parallel to path...")
        self.robot.drive.forward(AVOIDANCE_SPEED_DPS)
        time.sleep(AVOIDANCE_PARALLEL_DISTANCE / AVOIDANCE_CM_PER_SECOND)
        self.robot.drive.stop()
        
        # Step 5: Turn left 90 degrees to face back toward original path
        logger.info("[OBSTACLE-NAV] → Step 5: Turning left 90 degrees...")
        self.robot.drive.turn_degrees(-TURN_90_DEGREES)
        
        # Step 6: Move forward to return to original path line (0.75 feet)
        logger.info("[OBSTACLE-NAV] → Step 6: Moving forward 0.75 feet to return to path...")
        self.robot.drive.forward(AVOIDANCE_SPEED_DPS)
        time.sleep(AVOIDANCE_SIDE_DISTANCE / AVOIDANCE_CM_PER_SECOND)
        self.robot.drive.stop()
        
        # Step 7: Turn right 90 degrees to resume original heading
        logger.info("[OBSTACLE-NAV] → Step 7: Turning right 90 degrees to resume heading...")
        self.robot.drive.turn_degrees(TURN_90_DEGREES)
        
        # Step 8: Verify and correct heading using IMU
        if initial_heading is not None:
            time.sleep(0.2)  # Stabilization time
            final_heading = self.get_heading()
            if final_heading is not None:
                heading_error = abs(final_heading - initial_heading)
                # Normalize to -180 to 180 range
                if heading_error > 180:
                    heading_error = 360 - heading_error
                
                if heading_error > 10:  # If error > 10 degrees, correct it
                    logger.info(f"[OBSTACLE-NAV] → Step 8: Correcting heading error ({heading_error:.1f}°)...")
                    correction = initial_heading - final_heading
                    # Normalize correction
                    if correction > 180:
                        correction -= 360
                    elif correction < -180:
                        correction += 360
                    self.robot.drive.turn_degrees(correction)
                    logger.info(f"[OBSTACLE-NAV] ✅ Heading corrected to {initial_heading:.1f}°")
                else:
                    logger.info(f"[OBSTACLE-NAV] ✅ Heading verified: {final_heading:.1f}° (error: {heading_error:.1f}°)")
        
        logger.info("[OBSTACLE-NAV] ✅ Obstacle avoidance complete. Resumed on original path.")
    
    def drive_cm_safe(self, distance_cm: float, check_obstacles: bool = True) -> bool:
        """
        Drive a specific distance with obstacle detection and avoidance.
        
        Args:
            distance_cm: Distance to travel (positive = forward, negative = backward)
            check_obstacles: If True, check for obstacles during movement
        
        Returns:
            True if completed successfully, False if interrupted
        """
        if abs(distance_cm) < 0.1:
            return True
        
        if not check_obstacles or not self.distance_sensor:
            # No obstacle detection - use simple drive
            logger.info(f"[OBSTACLE-NAV] Driving {distance_cm:.1f}cm (no obstacle detection)")
            if self.robot.simulate:
                logger.info(f"[OBSTACLE-NAV] ⚠️  SIMULATION MODE - Robot will not actually move")
            self.robot.drive.drive_cm(distance_cm)
            logger.info(f"[OBSTACLE-NAV] Drive command completed")
            return True
        
        # Calculate movement parameters
        direction = "forward" if distance_cm > 0 else "backward"
        abs_distance = abs(distance_cm)
        
        # Start movement
        if distance_cm > 0:
            self.robot.drive.forward(200)  # Default speed
        else:
            self.robot.drive.backward(200)
        
        # Monitor movement with obstacle detection
        start_time = time.time()
        estimated_time = abs_distance / 6.8  # Approximate: 200 DPS ≈ 6.8 cm/s
        distance_traveled = 0.0
        obstacle_count = 0
        
        try:
            while distance_traveled < abs_distance:
                # Check for obstacles
                has_obstacle, dist = self.check_obstacle()
                
                if has_obstacle:
                    # Stop immediately
                    self.robot.drive.stop()
                    obstacle_count += 1
                    logger.warning(f"[OBSTACLE-NAV] 🚨 Obstacle #{obstacle_count} detected at {dist:.1f}cm during movement!")
                    
                    # Perform avoidance maneuver
                    self.avoid_obstacle()
                    
                    # Resume movement
                    remaining_distance = abs_distance - distance_traveled
                    if remaining_distance > 0.1:
                        logger.info(f"[OBSTACLE-NAV] Resuming movement ({remaining_distance:.1f}cm remaining)...")
                        if distance_cm > 0:
                            self.robot.drive.forward(200)
                        else:
                            self.robot.drive.backward(200)
                
                # Update distance traveled (approximate)
                elapsed = time.time() - start_time
                distance_traveled = elapsed * 6.8  # Approximate speed
                
                # Check timeout (safety)
                if elapsed > estimated_time * 2:  # Allow 2x estimated time
                    logger.warning(f"[OBSTACLE-NAV] Movement timeout - stopping")
                    self.robot.drive.stop()
                    return False
                
                time.sleep(CHECK_INTERVAL)
            
            # Stop when distance reached
            self.robot.drive.stop()
            
            if obstacle_count > 0:
                logger.info(f"[OBSTACLE-NAV] ✅ Movement complete (avoided {obstacle_count} obstacle(s))")
            
            return True
            
        except Exception as e:
            logger.error(f"[OBSTACLE-NAV] Error during safe movement: {e}")
            self.robot.drive.stop()
            return False

