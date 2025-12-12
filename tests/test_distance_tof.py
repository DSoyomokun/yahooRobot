import time
from easygopigo3 import EasyGoPiGo3

gpg = EasyGoPiGo3()

# Dexter/GoPiGo distance sensor over I2C
ds = gpg.init_distance_sensor()

print("ToF distance sensor initialized. Ctrl+C to stop.")

try:
    while True:
        dist_cm = ds.read()   # typically cm
        print(f"Distance: {dist_cm} cm")
        time.sleep(0.2)
except KeyboardInterrupt:
    print("Stopped.")
