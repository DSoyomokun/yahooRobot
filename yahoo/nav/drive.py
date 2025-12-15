"""
Drive controller for GoPiGo3 robot.
Provides low-level motor control with simulation support.
"""

import logging
import time
from typing import Optional

logger = logging.getLogger(__name__)


class Drive:
    """
    Low-level motor controller for GoPiGo3.
    Handles speed, turns, and stopping with both hardware and simulation modes.

    Motor speeds are in DPS (degrees per second) for the GoPiGo3.
    Typical range: -300 to 300 DPS
    """

    # Default motor speeds (degrees per second)
    DEFAULT_SPEED = 200
    TURN_SPEED = 150
    SLOW_SPEED = 100

    def __init__(self, robot=None, simulate: bool = False):
        """
        Initialize drive controller.

        Args:
            robot: Robot instance with GoPiGo3 hardware (optional)
            simulate: If True, run in simulation mode (no hardware)
        """
        self.robot = robot
        self.simulate = simulate or (robot is None)
        self.gpg = None

        if not self.simulate and robot and hasattr(robot, 'gpg') and robot.gpg:
            self.gpg = robot.gpg
            logger.info("Drive controller: Hardware mode")
        else:
            logger.info("Drive controller: Simulation mode")

    def set_motor_dps(self, left_dps: float, right_dps: float):
        """
        Set motor speeds in degrees per second.

        Args:
            left_dps: Left motor speed (-300 to 300)
            right_dps: Right motor speed (-300 to 300)
        """
        if self.simulate:
            logger.info(f"[DRIVE] Motors: L={left_dps:.0f} DPS, R={right_dps:.0f} DPS")
            return

        if self.gpg:
            try:
                self.gpg.set_motor_dps(self.gpg.MOTOR_LEFT, left_dps)
                self.gpg.set_motor_dps(self.gpg.MOTOR_RIGHT, right_dps)
                logger.debug(f"Motors set: L={left_dps:.0f} DPS, R={right_dps:.0f} DPS")
            except Exception as e:
                logger.error(f"Failed to set motor speeds: {e}")

    def set_speed(self, left_speed: float, right_speed: float):
        """
        Legacy method for compatibility. Calls set_motor_dps.

        Args:
            left_speed: Left motor speed (DPS)
            right_speed: Right motor speed (DPS)
        """
        self.set_motor_dps(left_speed, right_speed)

    def stop(self):
        """Stop both motors immediately."""
        if self.simulate:
            logger.info("[DRIVE] STOP")
            return

        if self.gpg:
            try:
                self.gpg.stop()
                logger.debug("Motors stopped")
            except Exception as e:
                logger.error(f"Failed to stop motors: {e}")

    def forward(self, speed: Optional[float] = None):
        """
        Move forward at specified speed.

        Args:
            speed: Speed in DPS (default: 200)
        """
        speed = speed or self.DEFAULT_SPEED
        self.set_motor_dps(speed, speed)

    def backward(self, speed: Optional[float] = None):
        """
        Move backward at specified speed.

        Args:
            speed: Speed in DPS (default: 200)
        """
        speed = speed or self.DEFAULT_SPEED
        self.set_motor_dps(-speed, -speed)

    def turn_left(self, speed: Optional[float] = None):
        """
        Turn left (left motor backward, right motor forward).

        Args:
            speed: Turn speed in DPS (default: 150)
        """
        speed = speed or self.TURN_SPEED
        self.set_motor_dps(-speed, speed)

    def turn_right(self, speed: Optional[float] = None):
        """
        Turn right (left motor forward, right motor backward).

        Args:
            speed: Turn speed in DPS (default: 150)
        """
        speed = speed or self.TURN_SPEED
        self.set_motor_dps(speed, -speed)

    def drive_cm(self, distance_cm: float, speed: Optional[float] = None):
        """
        Drive forward/backward for a specific distance.

        Args:
            distance_cm: Distance in centimeters (negative = backward)
            speed: Speed in DPS (default: 200)
        """
        speed = speed or self.DEFAULT_SPEED

        if self.simulate:
            direction = "forward" if distance_cm > 0 else "backward"
            logger.info(f"[DRIVE] Drive {abs(distance_cm):.1f}cm {direction} at {speed} DPS")
            return

        if self.gpg:
            try:
                # Use blocking=False to avoid hanging, then wait with timeout
                logger.info(f"[DRIVE] Calling gpg.drive_cm({distance_cm:.1f}, blocking=True)...")
                self.gpg.drive_cm(distance_cm, blocking=True)

                logger.info(f"[DRIVE] ✅ drive_cm() completed - moved {abs(distance_cm):.1f}cm")
            except Exception as e:
                logger.error(f"[DRIVE] ❌ Failed to drive distance: {e}")
                import traceback
                traceback.print_exc()
                raise  # Re-raise so caller knows it failed

    def turn_degrees(self, degrees: float, speed: Optional[float] = None):
        """
        Turn by a specific angle.

        Args:
            degrees: Angle to turn (positive = right, negative = left)
            speed: Turn speed (not used by GoPiGo3 turn_degrees, kept for compatibility)
        """
        if self.simulate:
            direction = "right" if degrees > 0 else "left"
            logger.info(f"[DRIVE] Turn {abs(degrees):.1f}° {direction}")
            return

        if self.gpg:
            try:
                # Use blocking=True (blocking=False doesn't work with new chassis encoders)
                logger.info(f"[DRIVE] Turning {degrees:.1f}° {'right' if degrees > 0 else 'left'} at {self.TURN_SPEED} DPS...")
                self.gpg.turn_degrees(degrees, blocking=True)

                logger.info(f"[DRIVE] ✅ Turn complete - turned {degrees:.1f}° {'right' if degrees > 0 else 'left'}")
            except Exception as e:
                logger.error(f"[DRIVE] ❌ Failed to turn: {e}")
                import traceback
                traceback.print_exc()
                raise

    def turn_right_timed(self, duration_seconds: float, speed: Optional[float] = None):
        """
        Turn right for a specific duration (time-based, no encoders).
        Use this when encoder-based turning doesn't work.

        Args:
            duration_seconds: How long to turn (e.g., 1.5 for ~90 degrees)
            speed: Turn speed in DPS (default: 150)
        """
        speed = speed or self.TURN_SPEED

        if self.simulate:
            logger.info(f"[DRIVE] Turn RIGHT for {duration_seconds:.2f}s at {speed} DPS")
            return

        if self.gpg:
            try:
                logger.info(f"[DRIVE] Turning RIGHT for {duration_seconds:.2f}s at {speed} DPS...")

                # Set motors to turn right (left forward, right backward)
                self.gpg.set_motor_dps(self.gpg.MOTOR_LEFT, speed)
                self.gpg.set_motor_dps(self.gpg.MOTOR_RIGHT, -speed)

                # Wait for specified duration
                time.sleep(duration_seconds)

                # Stop motors
                self.gpg.stop()

                logger.info(f"[DRIVE] ✅ Turn RIGHT complete ({duration_seconds:.2f}s)")
            except Exception as e:
                logger.error(f"[DRIVE] ❌ Failed to turn right: {e}")
                self.gpg.stop()  # Ensure motors stop on error
                raise

    def turn_left_timed(self, duration_seconds: float, speed: Optional[float] = None):
        """
        Turn left for a specific duration (time-based, no encoders).
        Use this when encoder-based turning doesn't work.

        Args:
            duration_seconds: How long to turn (e.g., 1.5 for ~90 degrees)
            speed: Turn speed in DPS (default: 150)
        """
        speed = speed or self.TURN_SPEED

        if self.simulate:
            logger.info(f"[DRIVE] Turn LEFT for {duration_seconds:.2f}s at {speed} DPS")
            return

        if self.gpg:
            try:
                logger.info(f"[DRIVE] Turning LEFT for {duration_seconds:.2f}s at {speed} DPS...")

                # Set motors to turn left (left backward, right forward)
                self.gpg.set_motor_dps(self.gpg.MOTOR_LEFT, -speed)
                self.gpg.set_motor_dps(self.gpg.MOTOR_RIGHT, speed)

                # Wait for specified duration
                time.sleep(duration_seconds)

                # Stop motors
                self.gpg.stop()

                logger.info(f"[DRIVE] ✅ Turn LEFT complete ({duration_seconds:.2f}s)")
            except Exception as e:
                logger.error(f"[DRIVE] ❌ Failed to turn left: {e}")
                self.gpg.stop()  # Ensure motors stop on error
                raise

    def get_motor_status(self) -> dict:
        """
        Get current motor encoder positions and status.

        Returns:
            Dictionary with motor encoder values and flags
        """
        if self.simulate:
            return {
                'left_encoder': 0,
                'right_encoder': 0,
                'left_flags': 0,
                'right_flags': 0
            }

        if self.gpg:
            try:
                left_enc = self.gpg.get_motor_encoder(self.gpg.MOTOR_LEFT)
                right_enc = self.gpg.get_motor_encoder(self.gpg.MOTOR_RIGHT)
                return {
                    'left_encoder': left_enc,
                    'right_encoder': right_enc,
                }
            except Exception as e:
                logger.error(f"Failed to read motor status: {e}")
                return {'error': str(e)}

        return {}
