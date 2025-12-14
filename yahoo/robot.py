"""
Yahoo Robot - Main robot class with GoPiGo3 integration.
Handles hardware initialization and provides unified interface for all subsystems.
"""

import logging
from typing import Optional

logger = logging.getLogger(__name__)


class Robot:
    """
    Main robot controller with GoPiGo3 hardware integration.

    Supports both hardware mode (Raspberry Pi with GoPiGo3) and simulation mode
    (development on Mac/Windows without hardware).

    Usage:
        # Hardware mode (on Raspberry Pi)
        with Robot() as robot:
            robot.drive.forward(200)

        # Simulation mode (on Mac/Windows)
        with Robot(simulate=True) as robot:
            robot.drive.forward(200)  # Prints debug messages
    """

    def __init__(self, simulate: bool = False):
        """
        Initialize robot with hardware or simulation mode.

        Args:
            simulate: If True, run in simulation mode without hardware.
                     If False, attempt to initialize GoPiGo3 hardware.
        """
        self.simulate = simulate
        self.gpg = None
        self._initialized = False

        # Try to import and initialize GoPiGo3
        if not simulate:
            try:
                import easygopigo3
                self.gpg = easygopigo3.EasyGoPiGo3()
                logger.info("GoPiGo3 hardware initialized successfully")
                self._initialized = True
            except ImportError:
                logger.warning("easygopigo3 not installed - running in simulation mode")
                self.simulate = True
            except Exception as e:
                logger.warning(f"Failed to initialize GoPiGo3: {e} - running in simulation mode")
                self.simulate = True
        else:
            logger.info("Running in simulation mode (no hardware)")

        # Import subsystems (lazy import to avoid circular dependencies)
        from yahoo.nav.drive import Drive
        from yahoo.io.leds import LEDController

        # Initialize subsystems
        self.drive = Drive(robot=self, simulate=self.simulate)
        self.leds = LEDController(robot=self, simulate=self.simulate)

        logger.info(f"Robot initialized (simulate={self.simulate})")

    def get_battery_voltage(self) -> float:
        """
        Get current battery voltage.

        Returns:
            Battery voltage in volts. Returns 10.0 in simulation mode.
        """
        if self.simulate or not self.gpg:
            return 10.0  # Simulated voltage

        try:
            voltage = self.gpg.get_voltage_battery()
            return voltage
        except Exception as e:
            logger.warning(f"Failed to read battery voltage: {e}")
            return 0.0

    def get_voltage_5v(self) -> float:
        """
        Get 5V rail voltage.

        Returns:
            5V rail voltage. Returns 5.0 in simulation mode.
        """
        if self.simulate or not self.gpg:
            return 5.0

        try:
            return self.gpg.get_voltage_5v()
        except Exception as e:
            logger.warning(f"Failed to read 5V voltage: {e}")
            return 0.0

    def reset_all(self):
        """Reset all robot systems to safe state."""
        logger.info("Resetting robot to safe state")

        if self.drive:
            self.drive.stop()

        if self.leds:
            self.leds.off()

        if self.gpg and not self.simulate:
            try:
                self.gpg.reset_all()
            except Exception as e:
                logger.warning(f"Failed to reset GoPiGo3: {e}")

    def __enter__(self):
        """Context manager entry - allows 'with Robot() as robot:' syntax."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - ensures cleanup on exit."""
        logger.info("Shutting down robot")
        self.reset_all()

        # Close GoPiGo3 connection if it exists
        if self.gpg and hasattr(self.gpg, 'reset_all'):
            try:
                self.gpg.reset_all()
            except Exception as e:
                logger.warning(f"Error during GoPiGo3 cleanup: {e}")

        return False  # Don't suppress exceptions

    def __del__(self):
        """Destructor - ensure cleanup even if context manager not used."""
        if hasattr(self, '_initialized') and self._initialized:
            self.reset_all()
