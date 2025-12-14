"""
Drive controller for GoPiGo3 robot.
Provides low-level motor control with simulation support.
"""

import logging
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
            robot: Robot instance with GoPiGo3 hardware (required)
            simulate: Ignored - always uses hardware
        """
        self.robot = robot
        self.gpg = None

        if robot and hasattr(robot, 'gpg') and robot.gpg:
            self.gpg = robot.gpg
            logger.info("Drive controller: Hardware mode")
        else:
            logger.error("Drive controller: ❌ GoPiGo3 hardware (gpg) not available!")
            logger.error("  Check robot initialization and hardware connection")

    def set_motor_dps(self, left_dps: float, right_dps: float):
        """
        Set motor speeds in degrees per second.

        Args:
            left_dps: Left motor speed (-300 to 300)
            right_dps: Right motor speed (-300 to 300)
        """
        if not self.gpg:
            logger.error(f"[DRIVE] ❌ Cannot set motor speeds - GoPiGo3 hardware not available")
            raise RuntimeError("GoPiGo3 hardware (gpg) not available - cannot control motors")

        try:
            self.gpg.set_motor_dps(self.gpg.MOTOR_LEFT, left_dps)
            self.gpg.set_motor_dps(self.gpg.MOTOR_RIGHT, right_dps)
            logger.debug(f"Motors set: L={left_dps:.0f} DPS, R={right_dps:.0f} DPS")
        except Exception as e:
            logger.error(f"[DRIVE] ❌ Failed to set motor speeds: {e}")
            raise

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
        if not self.gpg:
            logger.warning("[DRIVE] ⚠️  Cannot stop - GoPiGo3 hardware not available")
            return

        try:
            self.gpg.stop()
            logger.debug("Motors stopped")
        except Exception as e:
            logger.error(f"[DRIVE] ❌ Failed to stop motors: {e}")

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
        if not self.gpg:
            logger.error(f"[DRIVE] ❌ Cannot drive - GoPiGo3 hardware (gpg) not available")
            raise RuntimeError("GoPiGo3 hardware not available - cannot drive")

        speed = speed or self.DEFAULT_SPEED
        direction = "forward" if distance_cm > 0 else "backward"

        try:
            logger.info(f"[DRIVE] Driving {abs(distance_cm):.1f}cm {direction} at {speed} DPS...")
            if distance_cm > 0:
                self.gpg.drive_cm(distance_cm, blocking=True)
            else:
                self.gpg.drive_cm(distance_cm, blocking=True)
            logger.info(f"[DRIVE] ✅ Completed driving {abs(distance_cm):.1f}cm {direction}")
        except Exception as e:
            logger.error(f"[DRIVE] ❌ Failed to drive distance: {e}")
            import traceback
            traceback.print_exc()
            raise

    def turn_degrees(self, degrees: float, speed: Optional[float] = None):
        """
        Turn by a specific angle.

        Args:
            degrees: Angle to turn (positive = right, negative = left)
            speed: Turn speed (not used by GoPiGo3 turn_degrees, kept for compatibility)
        """
        if not self.gpg:
            logger.error(f"[DRIVE] ❌ Cannot turn - GoPiGo3 hardware (gpg) not available")
            raise RuntimeError("GoPiGo3 hardware not available - cannot turn")

        direction = "right" if degrees > 0 else "left"

        try:
            logger.info(f"[DRIVE] Turning {abs(degrees):.1f}° {direction}...")
            self.gpg.turn_degrees(degrees, blocking=True)
            logger.info(f"[DRIVE] ✅ Completed turning {abs(degrees):.1f}° {direction}")
        except Exception as e:
            logger.error(f"[DRIVE] ❌ Failed to turn: {e}")
            import traceback
            traceback.print_exc()
            raise

    def get_motor_status(self) -> dict:
        """
        Get current motor encoder positions and status.

        Returns:
            Dictionary with motor encoder values and flags
        """
        if not self.gpg:
            logger.error("[DRIVE] ❌ Cannot read motor status - GoPiGo3 hardware not available")
            return {'error': 'Hardware not available'}

        try:
            left_enc = self.gpg.get_motor_encoder(self.gpg.MOTOR_LEFT)
            right_enc = self.gpg.get_motor_encoder(self.gpg.MOTOR_RIGHT)
            return {
                'left_encoder': left_enc,
                'right_encoder': right_enc,
            }
        except Exception as e:
            logger.error(f"[DRIVE] ❌ Failed to read motor status: {e}")
            return {'error': str(e)}
