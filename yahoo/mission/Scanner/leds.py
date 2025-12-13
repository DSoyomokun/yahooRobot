"""
LED abstraction (safe for demo)
"""
try:
    from easygopigo3 import EasyGoPiGo3
    gpg = EasyGoPiGo3()
    YELLOW = gpg.led(0)
    GREEN = gpg.led(1)
except Exception:
    YELLOW = GREEN = None

def yellow_on():
    if YELLOW: YELLOW.on()
    print("[LED] YELLOW ON")

def yellow_off():
    if YELLOW: YELLOW.off()
    print("[LED] YELLOW OFF")

def green_on():
    if GREEN: GREEN.on()
    print("[LED] GREEN ON")

def green_off():
    if GREEN: GREEN.off()
    print("[LED] GREEN OFF")

# If LEDs aren't wired → no crash, only logs.


