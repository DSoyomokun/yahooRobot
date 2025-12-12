"""
Mock weight sensor for testing without HX711 hardware.
Simulates paper detection via keyboard input or timer.
"""
import time
import sys
import select
import os

class MockWeightSensor:
    """Mock HX711 weight sensor for development/testing."""
    
    def __init__(self, threshold_grams=1.0, mock_mode='keyboard'):
        """
        Args:
            threshold_grams: Weight threshold to trigger (default: 1.0g)
            mock_mode: 'keyboard' (press key) or 'timer' (auto every N seconds)
        """
        self.threshold = threshold_grams
        self.mock_mode = mock_mode
        self.current_weight = 0.0
        
    def read_weight(self):
        """Simulate reading weight from sensor."""
        if self.mock_mode == 'keyboard':
            # Return 0 (no paper) unless key pressed
            return 0.0
        elif self.mock_mode == 'timer':
            # Simulate weight detection every 5 seconds
            if int(time.time()) % 5 == 0:
                return 2.0  # Simulate paper weight
            return 0.0
        return 0.0
    
    def detect_paper(self):
        """Check if paper weight is detected (above threshold)."""
        weight = self.read_weight()
        return weight >= self.threshold
    
    def wait_for_paper(self, timeout=None):
        """
        Block until paper is detected.
        
        Args:
            timeout: Maximum time to wait (None = wait forever)
        
        Returns:
            True if paper detected, False if timeout
        """
        start_time = time.time()
        
        print("📄 Waiting for paper... (Press 'P' + Enter to simulate paper detection)")
        
        while True:
            if timeout and (time.time() - start_time) > timeout:
                return False
            
            if self.mock_mode == 'keyboard':
                # Check for keyboard input (non-blocking on Unix)
                if sys.platform != 'win32':
                    if sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
                        line = sys.stdin.readline().strip()
                        if line.lower() == 'p':
                            print("✅ Paper detected (simulated)")
                            return True
                else:
                    # Windows - use msvcrt
                    import msvcrt
                    if msvcrt.kbhit():
                        key = msvcrt.getch().decode('utf-8').lower()
                        if key == 'p':
                            print("✅ Paper detected (simulated)")
                            return True
            elif self.mock_mode == 'timer':
                if self.detect_paper():
                    print("✅ Paper detected (timer)")
                    return True
            
            time.sleep(0.1)  # Small delay to avoid CPU spinning


# Real HX711 sensor class (placeholder for when hardware is available)
class HX711WeightSensor:
    """Real HX711 weight sensor implementation."""
    
    def __init__(self, dt_pin, sck_pin, threshold_grams=1.0):
        """
        Args:
            dt_pin: GPIO pin for data (HX711 DT)
            sck_pin: GPIO pin for clock (HX711 SCK)
            threshold_grams: Weight threshold
        """
        self.dt_pin = dt_pin
        self.sck_pin = sck_pin
        self.threshold = threshold_grams
        self.sensor = None
        # TODO: Initialize HX711 library when hardware is available
        # try:
        #     from hx711 import HX711
        #     self.sensor = HX711(dt_pin, sck_pin)
        #     self.sensor.set_scale(...)
        #     self.sensor.tare()
        # except ImportError:
        #     print("⚠️  HX711 library not installed. Using mock sensor.")
    
    def read_weight(self):
        """Read actual weight from HX711 sensor."""
        if self.sensor is None:
            raise NotImplementedError("HX711 hardware not yet implemented. Use MockWeightSensor for testing.")
        # TODO: Implement actual sensor reading
        # return self.sensor.get_weight(5)  # Read 5 times and average
        return 0.0
    
    def detect_paper(self):
        """Check if paper weight is detected."""
        weight = self.read_weight()
        return weight >= self.threshold
    
    def wait_for_paper(self, timeout=None):
        """Block until paper is detected."""
        start_time = time.time()
        print("📄 Waiting for paper on weight sensor...")
        
        while True:
            if timeout and (time.time() - start_time) > timeout:
                return False
            
            if self.detect_paper():
                print("✅ Paper detected!")
                return True
            
            time.sleep(0.1)
