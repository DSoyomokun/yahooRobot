"""
Main Robot class for GoPiGo3 initialization and control
"""

import time
import logging
from typing import Optional

try:
    import gopigo3
except ImportError:
    print("Warning: gopigo3 library not found. Running in simulation mode.")
    gopigo3 = None


class Robot:
    """Main robot controller for GoPiGo3"""
    
    def __init__(self, simulate: bool = False):
        """
        Initialize the GoPiGo3 robot
        
        Args:
            simulate: If True, run without actual hardware
        """
        self.logger = logging.getLogger(__name__)
        self.simulate = simulate or (gopigo3 is None)
        
        if self.simulate:
            self.logger.warning("Running in simulation mode")
            self.gpg = None
        else:
            try:
                self.gpg = gopigo3.GoPiGo3()
                self.logger.info("GoPiGo3 initialized successfully")
                self._reset()
            except Exception as e:
                self.logger.error(f"Failed to initialize GoPiGo3: {e}")
                self.simulate = True
                self.gpg = None
    
    def _reset(self):
        """Reset the robot to initial state"""
        if self.gpg:
            self.gpg.reset_all()
            time.sleep(0.1)
    
    def get_battery_voltage(self) -> float:
        """Get current battery voltage"""
        if self.gpg:
            try:
                return self.gpg.get_voltage_battery()
            except Exception as e:
                self.logger.error(f"Error reading battery: {e}")
                return 0.0
        return 12.0  # Simulated voltage
    
    def stop(self):
        """Stop all motors"""
        if self.gpg:
            self.gpg.stop()
        self.logger.info("Robot stopped")
    
    def cleanup(self):
        """Cleanup and reset robot"""
        self.stop()
        if self.gpg:
            self._reset()
        self.logger.info("Robot cleanup complete")
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.cleanup()


if __name__ == "__main__":
    # Quick test
    logging.basicConfig(level=logging.INFO)
    
    with Robot() as robot:
        print(f"Battery Voltage: {robot.get_battery_voltage():.2f}V")
        time.sleep(1)

