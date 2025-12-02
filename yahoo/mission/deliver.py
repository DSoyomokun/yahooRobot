# mission/deliver.py

import time

class DeliverMission:
    """
    Robot passes out papers aisle-by-aisle,
    stopping at each row.
    """

    def __init__(self, route, config):
        self.route = route
        self.aisles = config["aisles"]

    def run(self):
        for aisle_name, aisle in self.aisles.items():
            print(f"[MISSION] Delivering in aisle {aisle_name}")

            # Down the aisle
            for wp in aisle["down"]:
                self.route.goto(wp)
                time.sleep(2)

            # Up the aisle
            for wp in aisle["up"]:
                self.route.goto(wp)
                time.sleep(2)

        print("[MISSION] Returning home")
        # Add home waypoint later
