from robot_control.config import *
import math

wheel_circ = math.pi * WHEEL_DIAMETER_IN

def inches_to_ticks(inches):
    rotations = inches / wheel_circ
    return rotations * TICKS_PER_ROT

def drive_inches(inches):
    ticks = inches_to_ticks(inches)
    motor.drive_ticks(ticks)   # you replace with real robot API

