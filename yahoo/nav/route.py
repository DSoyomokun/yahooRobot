# nav/route.py

import math
import time

class Route:
    """
    Handles waypoint navigation with:
    - Camera obstacle detection
    - Ultrasonic stop
    - LED feedback
    """

    def __init__(self, drive, odom, camera, ultrasonic, leds):
        self.drive = drive
        self.odom = odom
        self.camera = camera
        self.ultrasonic = ultrasonic
        self.leds = leds

    def goto(self, target):
        """
        Move toward a waypoint but obey safety sensors.
        """
        tx, ty = target["x"], target["y"]

        while True:
            # 1. Object detection
            frame = self.camera.get_frame()
            if self.camera.detect_blockage(frame):
                self.drive.stop()
                self.leds.set_color("red")
                print("[ROUTE] Camera sees obstacle → STOP")
                time.sleep(0.1)
                continue

            # 2. Ultrasonic safety
            if self.ultrasonic.distance() < 20:
                self.drive.stop()
                self.leds.set_color("red")
                print("[ROUTE] Ultrasonic too close → STOP")
                time.sleep(0.1)
                continue

            # 3. Path is clear → move
            self.leds.set_color("green")
            x, y, _ = self.odom.pose()
            dist = math.hypot(tx - x, ty - y)

            if dist < 0.15:  # reached waypoint
                print("[ROUTE] Reached waypoint")
                self.drive.stop()
                break

            # 4. Move forward
            self.drive.forward(0.3)
            time.sleep(0.1)
