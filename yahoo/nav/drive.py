# nav/drive.py

class Drive:
    """
    Low-level motor controller.
    Handles speed, turns, and stopping.
    """

    def __init__(self, pins, gains):
        self.pins = pins
        self.gains = gains

    def set_speed(self, left_speed, right_speed):
        """
        Send PWM signals to motors.
        Replace this with your motor driver library.
        """
        print(f"[DRIVE] L={left_speed}, R={right_speed}")

    def stop(self):
        self.set_speed(0, 0)

    def forward(self, speed):
        self.set_speed(speed, speed)

    def backward(self, speed):
        self.set_speed(-speed, -speed)

    def turn_left(self, speed):
        self.set_speed(-speed, speed)

    def turn_right(self, speed):
        self.set_speed(speed, -speed)
