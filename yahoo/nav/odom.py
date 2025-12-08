# nav/odom.py

import math

class Odom:
    """
    Tracks robot position (x,y,θ) using wheel encoders.
    """

    def __init__(self):
        self.x = 0
        self.y = 0
        self.theta = 0

    def update(self, left_ticks, right_ticks):
        """
        Use your encoder tick → distance conversion here.
        """
        # Placeholder: update nothing
        pass

    def pose(self):
        return (self.x, self.y, self.theta)
