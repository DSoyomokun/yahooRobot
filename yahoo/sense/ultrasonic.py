# sense/ultrasonic.py
"""
HR-SR04 / HC-SR04 Ultrasonic Distance Sensor
Uses GPIO pins on Raspberry Pi to measure distance.
"""

import time
import logging

logger = logging.getLogger(__name__)

try:
    import RPi.GPIO as GPIO
    GPIO_AVAILABLE = True
except ImportError:
    GPIO_AVAILABLE = False
    logger.warning("RPi.GPIO not available - running in simulation mode")


class Ultrasonic:
    """
    HR-SR04 / HC-SR04 ultrasonic distance sensor.
    
    Pin connections:
    - VCC → 5V
    - GND → GND
    - Trig → GPIO pin (specified in trig_pin)
    - Echo → GPIO pin (specified in echo_pin)
    
    Typical GPIO pins (BCM numbering):
    - Trig: GPIO 23 (Physical pin 16)
    - Echo: GPIO 24 (Physical pin 18)
    """

    def __init__(self, trig_pin, echo_pin, simulate=False):
        """
        Initialize HR-SR04 ultrasonic sensor.
        
        Args:
            trig_pin: GPIO pin number for trigger (BCM numbering)
            echo_pin: GPIO pin number for echo (BCM numbering)
            simulate: If True, return mock values (for testing without hardware)
        """
        self.trig_pin = trig_pin
        self.echo_pin = echo_pin
        self.simulate = simulate or not GPIO_AVAILABLE
        
        if not self.simulate:
            try:
                GPIO.setmode(GPIO.BCM)
                GPIO.setwarnings(False)
                GPIO.setup(self.trig_pin, GPIO.OUT)
                GPIO.setup(self.echo_pin, GPIO.IN)
                GPIO.output(self.trig_pin, False)
                logger.info(f"HR-SR04 initialized: Trig=GPIO{trig_pin}, Echo=GPIO{echo_pin}")
            except Exception as e:
                logger.error(f"Failed to initialize HR-SR04: {e}")
                self.simulate = True
        else:
            logger.info("HR-SR04 running in simulation mode")

    def distance(self):
        """
        Return distance to nearest object in cm.
        
        Returns:
            Distance in centimeters. Returns 999 if error or in simulation mode.
        """
        if self.simulate:
            return 999.0  # Always clear in simulation
        
        try:
            # Send trigger pulse
            GPIO.output(self.trig_pin, True)
            time.sleep(0.00001)  # 10 microseconds
            GPIO.output(self.trig_pin, False)
            
            # Wait for echo to start
            timeout_start = time.time()
            while GPIO.input(self.echo_pin) == 0:
                if time.time() - timeout_start > 0.1:  # 100ms timeout
                    return 999.0
                pulse_start = time.time()
            
            # Wait for echo to end
            timeout_start = time.time()
            while GPIO.input(self.echo_pin) == 1:
                if time.time() - timeout_start > 0.1:  # 100ms timeout
                    return 999.0
                pulse_end = time.time()
            
            # Calculate distance
            pulse_duration = pulse_end - pulse_start
            # Speed of sound = 34300 cm/s
            # Distance = (time * speed) / 2 (divided by 2 because sound travels there and back)
            distance_cm = (pulse_duration * 34300) / 2
            
            # Sanity check: HR-SR04 range is 2-400cm
            if distance_cm < 2 or distance_cm > 400:
                return 999.0
            
            return distance_cm
            
        except Exception as e:
            logger.error(f"Error reading HR-SR04: {e}")
            return 999.0
    
    def read_mm(self):
        """
        Return distance in millimeters (for compatibility with GoPiGo sensor).
        
        Returns:
            Distance in millimeters.
        """
        return self.distance() * 10.0
    
    def cleanup(self):
        """Clean up GPIO pins."""
        if not self.simulate and GPIO_AVAILABLE:
            try:
                GPIO.cleanup([self.trig_pin, self.echo_pin])
            except Exception as e:
                logger.warning(f"Error cleaning up GPIO: {e}")
