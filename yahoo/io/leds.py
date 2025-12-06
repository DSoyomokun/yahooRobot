"""
LED controller for robot status feedback.
Integrates with GoPiGo3 LED pins.
"""
import logging
import time
from typing import Optional

logger = logging.getLogger(__name__)


class LEDController:
    """Controls LED status indicators for robot operations."""
    
    def __init__(self, robot=None, simulate: bool = False):
        """
        Initialize LED controller.
        
        Args:
            robot: Robot instance with GoPiGo3 (optional)
            simulate: If True, run in simulation mode (no hardware)
        """
        self.robot = robot
        self.simulate = simulate or (robot is None)
        self.current_state = None
        
        if not self.simulate and robot and hasattr(robot, 'gpg') and robot.gpg:
            self.gpg = robot.gpg
        else:
            self.gpg = None
            if not self.simulate:
                logger.warning("LED controller: No robot hardware, running in simulation mode")
    
    def scanning(self):
        """Set LED to yellow (scanning in progress)."""
        self.current_state = "scanning"
        if self.simulate:
            logger.info("LED: YELLOW (scanning)")
            return
        
        if self.gpg:
            try:
                # Yellow = Red + Green
                self.gpg.set_led(self.gpg.LED_EYE_LEFT, 255)  # Red
                self.gpg.set_led(self.gpg.LED_EYE_RIGHT, 255)  # Green
                logger.debug("LED: YELLOW (scanning)")
            except Exception as e:
                logger.warning(f"Failed to set LED (scanning): {e}")
    
    def success(self):
        """Set LED to green (scan successful)."""
        self.current_state = "success"
        if self.simulate:
            logger.info("LED: GREEN (success)")
            return
        
        if self.gpg:
            try:
                # Green only
                self.gpg.set_led(self.gpg.LED_EYE_LEFT, 0)
                self.gpg.set_led(self.gpg.LED_EYE_RIGHT, 255)  # Green
                logger.debug("LED: GREEN (success)")
            except Exception as e:
                logger.warning(f"Failed to set LED (success): {e}")
    
    def fail(self):
        """Set LED to red (scan failed)."""
        self.current_state = "fail"
        if self.simulate:
            logger.info("LED: RED (fail)")
            return
        
        if self.gpg:
            try:
                # Red only
                self.gpg.set_led(self.gpg.LED_EYE_LEFT, 255)  # Red
                self.gpg.set_led(self.gpg.LED_EYE_RIGHT, 0)
                logger.debug("LED: RED (fail)")
            except Exception as e:
                logger.warning(f"Failed to set LED (fail): {e}")
    
    def analyzing(self):
        """Set LED to blue (analyzing/processing)."""
        self.current_state = "analyzing"
        if self.simulate:
            logger.info("LED: BLUE (analyzing)")
            return
        
        if self.gpg:
            try:
                # Blue = Red + Green (approximation, or use blinker LED)
                # GoPiGo3 doesn't have true blue, so we'll use blinking pattern
                self.gpg.set_led(self.gpg.LED_BLINKER_LEFT, 128)  # Dim blue approximation
                logger.debug("LED: BLUE (analyzing)")
            except Exception as e:
                logger.warning(f"Failed to set LED (analyzing): {e}")
    
    def off(self):
        """Turn off all LEDs."""
        self.current_state = "off"
        if self.simulate:
            logger.info("LED: OFF")
            return
        
        if self.gpg:
            try:
                self.gpg.set_led(self.gpg.LED_EYE_LEFT, 0)
                self.gpg.set_led(self.gpg.LED_EYE_RIGHT, 0)
                self.gpg.set_led(self.gpg.LED_BLINKER_LEFT, 0)
                logger.debug("LED: OFF")
            except Exception as e:
                logger.warning(f"Failed to turn off LED: {e}")
    
    def blink(self, color: str = "green", times: int = 3, duration: float = 0.2):
        """
        Blink LED a specified number of times.
        
        Args:
            color: Color to blink ("green", "red", "yellow")
            times: Number of blinks
            duration: Duration of each blink in seconds
        """
        original_state = self.current_state
        
        for _ in range(times):
            if color == "green":
                self.success()
            elif color == "red":
                self.fail()
            elif color == "yellow":
                self.scanning()
            
            time.sleep(duration)
            self.off()
            time.sleep(duration)
        
        # Restore original state
        if original_state:
            if original_state == "success":
                self.success()
            elif original_state == "fail":
                self.fail()
            elif original_state == "scanning":
                self.scanning()
            elif original_state == "analyzing":
                self.analyzing()


