# HR-SR04 Ultrasonic Sensor Setup Guide

This guide explains how to connect and configure the HR-SR04 (or HC-SR04) ultrasonic distance sensor to your GoPiGo3 robot.

---

## 📦 What You Need

- HR-SR04 or HC-SR04 Ultrasonic Sensor Module
- 4 jumper wires (female-to-female or female-to-male)
- Raspberry Pi with GPIO access

---

## 🔌 Pin Connections

### HR-SR04 Sensor Pins

The HR-SR04 has 4 pins:
- **VCC** - Power (5V)
- **GND** - Ground
- **Trig** - Trigger pin (output from Pi)
- **Echo** - Echo pin (input to Pi)

### Recommended GPIO Pin Configuration

**Default Configuration (in `yahoo/config/pins.json`):**
- **Trig** → GPIO 23 (Physical pin 16)
- **Echo** → GPIO 24 (Physical pin 18)
- **VCC** → 5V (Physical pin 2 or 4)
- **GND** → GND (Physical pin 6, 9, 14, 20, or 25)

### Wiring Diagram

```
HR-SR04          Raspberry Pi GPIO
─────────────────────────────────
VCC       →      5V (Pin 2)
GND       →      GND (Pin 6)
Trig      →      GPIO 23 (Pin 16)
Echo      →      GPIO 24 (Pin 18)
```

### Physical Pin Layout (Raspberry Pi)

```
    3.3V  [1]  [2]  5V
   GPIO2  [3]  [4]  5V
   GPIO3  [5]  [6]  GND  ← Connect GND here
   GPIO4  [7]  [8]  GPIO14
     GND  [9]  [10] GPIO15
  GPIO17 [11] [12] GPIO18
  GPIO27 [13] [14] GND
  GPIO22 [15] [16] GPIO23  ← Connect Trig here
    3.3V [17] [18] GPIO24  ← Connect Echo here
  GPIO10 [19] [20] GND
   GPIO9 [21] [22] GPIO25
  GPIO11 [23] [24] GPIO8
     GND [25] [26] GPIO7
```

---

## ⚙️ Configuration

### Option 1: Use Default Pins (Recommended)

The code will automatically use GPIO 23 (Trig) and GPIO 24 (Echo) if you don't modify the config file.

### Option 2: Custom Pin Configuration

Edit `yahoo/config/pins.json`:

```json
{
  "ultrasonic": {
    "hr_sr04": {
      "trig_pin": 23,
      "echo_pin": 24,
      "description": "HR-SR04 Ultrasonic Sensor - Trig=GPIO23, Echo=GPIO24"
    }
  }
}
```

**Important:** Use **BCM (Broadcom) GPIO numbering**, not physical pin numbers!

### Common GPIO Pin Alternatives

If GPIO 23/24 are already in use, you can use:
- GPIO 17 (Pin 11) and GPIO 27 (Pin 13)
- GPIO 22 (Pin 15) and GPIO 25 (Pin 18)
- GPIO 5 (Pin 29) and GPIO 6 (Pin 31)

Just update the `trig_pin` and `echo_pin` values in `pins.json`.

---

## 🔧 Software Setup

### 1. Install Required Library

The HR-SR04 uses `RPi.GPIO` which should already be installed:

```bash
pip3 install RPi.GPIO
```

Or install all Pi requirements:

```bash
pip3 install -r requirements-pi.txt
```

### 2. Verify GPIO Access

Make sure your user has GPIO permissions:

```bash
sudo usermod -a -G gpio pi
```

You may need to log out and back in for this to take effect.

### 3. Test the Sensor

The code will automatically detect and use the HR-SR04 if:
- The GoPiGo Distance Sensor is not available, OR
- You want to use HR-SR04 instead

Run your robot code:

```bash
python3 main.py run
```

You should see:
```
✅ HR-SR04 Ultrasonic Sensor initialized (GPIO23/GPIO24)
```

---

## 🧪 Testing the Sensor

### Quick Test Script

Create a test file `test_hr_sr04.py`:

```python
#!/usr/bin/env python3
import time
from yahoo.sense.ultrasonic import Ultrasonic

# Initialize sensor (using default pins: GPIO 23/24)
sensor = Ultrasonic(trig_pin=23, echo_pin=24, simulate=False)

print("HR-SR04 Distance Sensor Test")
print("Press Ctrl+C to stop\n")

try:
    while True:
        distance_cm = sensor.distance()
        if distance_cm < 999:
            print(f"Distance: {distance_cm:.1f} cm ({distance_cm/30.48:.2f} feet)")
        else:
            print("No object detected (out of range)")
        time.sleep(0.5)
except KeyboardInterrupt:
    print("\nStopping...")
    sensor.cleanup()
```

Run it:

```bash
python3 test_hr_sr04.py
```

---

## 🔄 How It Works in Your Code

The robot code automatically tries sensors in this order:

1. **GoPiGo Distance Sensor** (I2C) - if available
2. **HR-SR04** (GPIO) - fallback if GoPiGo sensor not available

You can see which sensor is being used in the startup logs:

```
✅ GoPiGo Distance Sensor initialized (I2C)
```

OR

```
✅ HR-SR04 Ultrasonic Sensor initialized (GPIO23/GPIO24)
```

---

## 🐛 Troubleshooting

### Problem: "RPi.GPIO not available"

**Solution:**
- Make sure you're running on a Raspberry Pi (not Mac/Windows)
- Install RPi.GPIO: `pip3 install RPi.GPIO`
- Check you're using Python 3: `python3 --version`

### Problem: "Permission denied" or sensor not reading

**Solutions:**
1. Add user to gpio group:
   ```bash
   sudo usermod -a -G gpio pi
   sudo usermod -a -G gpio $USER
   ```
   Then log out and back in.

2. Check wiring connections
3. Verify pins are correct in `pins.json`
4. Test with the test script above

### Problem: Sensor always returns 999 (out of range)

**Solutions:**
- Check wiring (especially VCC and GND)
- Make sure sensor is facing forward
- Test with an object 10-50cm away
- Verify GPIO pins are correct

### Problem: "GPIO pins already in use"

**Solutions:**
- Change pins in `pins.json` to unused GPIO pins
- Check what's using the pins: `gpio readall` (if installed)
- Make sure no other program is using those pins

---

## 📊 Sensor Specifications

- **Range:** 2cm - 400cm (0.8" - 13 feet)
- **Accuracy:** ±3mm
- **Operating Voltage:** 5V
- **Operating Current:** 15mA
- **Trigger Pulse:** 10µs
- **Echo Response Time:** Up to 30ms

---

## 💡 Tips

1. **Mount the sensor** facing forward on your robot
2. **Keep it clean** - dust/dirt can affect readings
3. **Avoid obstacles** at extreme angles (sensor works best straight ahead)
4. **Test range** - sensor works best between 10-200cm
5. **Use both sensors** - GoPiGo sensor for I2C, HR-SR04 as backup

---

## 📝 Quick Reference

**Default Pins:**
- Trig: GPIO 23 (Physical pin 16)
- Echo: GPIO 24 (Physical pin 18)

**Config File:**
- `yahoo/config/pins.json`

**Sensor Class:**
- `yahoo/sense/ultrasonic.py`

**Test Command:**
```bash
python3 test_hr_sr04.py
```

---

## 🔗 Related Documentation

- [Raspberry Pi GPIO Pinout](https://pinout.xyz/)
- [RPi.GPIO Documentation](https://sourceforge.net/projects/raspberry-gpio-python/)
- [HR-SR04 Datasheet](https://components101.com/sites/default/files/component_datasheet/HC-SR04%20Datasheet.pdf)

