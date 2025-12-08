# sense/ultrasonic.py

class Ultrasonic:
    """
    HC-SR04 style ultrasonic distance sensor.
    """

    def __init__(self, trig_pin, echo_pin):
        self.trig = trig_pin
        self.echo = echo_pin

    def distance(self):
        """
        Return distance to nearest object in cm.
        Replace with your GPIO code.
        """
        return 999  # placeholder, always clear
