# Complete Wiring Guide for HR-SR04 Sensor

Step-by-step instructions to wire your HR-SR04 ultrasonic sensor to the GoPiGo3 robot.

---

## 📋 What You Need

- HR-SR04 or HC-SR04 Ultrasonic Sensor Module
- 4 jumper wires (female-to-female recommended)
- Small screwdriver (if using terminal blocks)
- GoPiGo3 robot with Raspberry Pi

---

## 🔌 Step-by-Step Wiring Instructions

### Step 1: Identify the HR-SR04 Pins

Your HR-SR04 sensor has 4 pins. Looking at the sensor with the two round transducers facing you:

```
    ┌─────────────┐
    │   HR-SR04   │
    │             │
    │  VCC  [1]   │  ← Power (5V)
    │  Trig [2]   │  ← Trigger (output from Pi)
    │  Echo [3]   │  ← Echo (input to Pi)
    │  GND  [4]   │  ← Ground
    └─────────────┘
```

**Pin Order (left to right):**
1. VCC (Power)
2. Trig (Trigger)
3. Echo (Echo)
4. GND (Ground)

---

### Step 2: Identify Raspberry Pi GPIO Pins

**Important:** We use **BCM (Broadcom) GPIO numbering**, not physical pin numbers!

**Physical Pin Layout (40-pin header):**

```
    3.3V  [1]  [2]  5V  ←─── Connect VCC here
   GPIO2  [3]  [4]  5V
   GPIO3  [5]  [6]  GND ←─── Connect GND here
   GPIO4  [7]  [8]  GPIO14
     GND  [9]  [10] GPIO15
  GPIO17 [11] [12] GPIO18
  GPIO27 [13] [14] GND
  GPIO22 [15] [16] GPIO23 ←─── Connect Trig here
    3.3V [17] [18] GPIO24 ←─── Connect Echo here
  GPIO10 [19] [20] GND
   GPIO9 [21] [22] GPIO25
  GPIO11 [23] [24] GPIO8
     GND [25] [26] GPIO7
```

---

### Step 3: Make the Connections

**Connection Table:**

| HR-SR04 Pin | Wire Color (suggestion) | Raspberry Pi Connection | Physical Pin |
|-------------|------------------------|-------------------------|--------------|
| **VCC**     | Red                    | 5V                      | Pin 2        |
| **GND**     | Black                   | GND                     | Pin 6         |
| **Trig**    | Yellow/Orange           | GPIO 23                 | Pin 16       |
| **Echo**    | Green                  | GPIO 24                 | Pin 18       |

**Wiring Steps:**

1. **Connect VCC (Power)**
   - Take a red wire (or any color)
   - Connect one end to HR-SR04 **VCC** pin
   - Connect other end to Raspberry Pi **Pin 2** (5V)
   - ✅ **This powers the sensor**

2. **Connect GND (Ground)**
   - Take a black wire (or any color)
   - Connect one end to HR-SR04 **GND** pin
   - Connect other end to Raspberry Pi **Pin 6** (GND)
   - ✅ **This completes the power circuit**

3. **Connect Trig (Trigger)**
   - Take a yellow/orange wire
   - Connect one end to HR-SR04 **Trig** pin
   - Connect other end to Raspberry Pi **Pin 16** (GPIO 23)
   - ✅ **This sends trigger pulses from Pi to sensor**

4. **Connect Echo**
   - Take a green wire
   - Connect one end to HR-SR04 **Echo** pin
   - Connect other end to Raspberry Pi **Pin 18** (GPIO 24)
   - ✅ **This receives echo signal from sensor to Pi**

---

### Step 4: Verify Connections

**Visual Check:**
- [ ] All 4 wires are securely connected
- [ ] No loose connections
- [ ] Wires are not touching each other
- [ ] Sensor is facing forward on your robot

**Double-check:**
- VCC → 5V (Pin 2) ✅
- GND → GND (Pin 6) ✅
- Trig → GPIO 23 (Pin 16) ✅
- Echo → GPIO 24 (Pin 18) ✅

---

### Step 5: Mount the Sensor

**Recommended mounting:**
- Mount sensor facing forward on the front of your robot
- Keep it level (not tilted up or down)
- Ensure nothing blocks the sensor's view
- Keep sensor clean (dust can affect readings)

---

### Step 6: Test the Wiring

**Option 1: Use Verification Script**

```bash
cd ~/yahooRobot
python3 scripts/verify_wiring.py
```

This script will:
- Check GPIO pin configuration
- Test Trig and Echo pins
- Take sensor readings
- Verify everything is working

**Option 2: Quick Manual Test**

```bash
python3 -c "
from yahoo.sense.ultrasonic import Ultrasonic
import time

sensor = Ultrasonic(23, 24, simulate=False)
print('Testing HR-SR04 sensor...')
for i in range(5):
    dist = sensor.distance()
    print(f'Reading {i+1}: {dist:.1f} cm')
    time.sleep(0.5)
sensor.cleanup()
"
```

**Expected Output:**
- If working: Distance readings in cm (e.g., "Reading 1: 25.3 cm")
- If not working: "Out of range" or errors

---

## 🐛 Troubleshooting

### Problem: Sensor not reading / Always returns 999

**Check:**
1. ✅ VCC connected to 5V? (Pin 2)
2. ✅ GND connected to GND? (Pin 6)
3. ✅ Trig connected to GPIO 23? (Pin 16)
4. ✅ Echo connected to GPIO 24? (Pin 18)
5. ✅ Wires are secure (not loose)?
6. ✅ Sensor is powered (LED might be on)?

**Test power:**
- Use a multimeter to check 5V on VCC pin
- Check continuity on GND connection

### Problem: "Permission denied" error

**Solution:**
```bash
sudo usermod -a -G gpio pi
# Log out and back in, or:
newgrp gpio
```

### Problem: "GPIO pins already in use"

**Solution:**
- Check what's using the pins: `gpio readall` (if installed)
- Change pins in `yahoo/config/pins.json` to unused GPIO pins
- Make sure no other program is running

### Problem: Inconsistent readings

**Solutions:**
- Keep sensor clean
- Avoid obstacles at extreme angles
- Ensure sensor is mounted securely
- Check for loose connections
- Test with object 10-50cm away

---

## 📊 Pin Reference Quick Card

**Print this and keep it handy:**

```
HR-SR04 Wiring Quick Reference
═══════════════════════════════

HR-SR04 → Raspberry Pi
───────────────────────
VCC     → Pin 2  (5V)
GND     → Pin 6  (GND)
Trig    → Pin 16 (GPIO 23)
Echo    → Pin 18 (GPIO 24)

Physical Pin Numbers:
[2]  = 5V
[6]  = GND
[16] = GPIO 23
[18] = GPIO 24
```

---

## ✅ Final Checklist

Before running your robot:

- [ ] All 4 wires connected correctly
- [ ] Sensor mounted facing forward
- [ ] Wiring verified with test script
- [ ] Sensor reads distances correctly
- [ ] No loose connections
- [ ] User has GPIO permissions

---

## 🚀 Next Steps

Once wiring is complete:

1. **Test the sensor:**
   ```bash
   python3 scripts/verify_wiring.py
   ```

2. **Run your robot:**
   ```bash
   python3 main.py run
   ```

3. **Check logs** - you should see:
   ```
   ✅ HR-SR04 Ultrasonic Sensor initialized (GPIO23/GPIO24)
   ```

---

## 📚 Additional Resources

- [HR-SR04 Setup Guide](HR_SR04_SETUP.md) - Detailed sensor setup
- [Raspberry Pi GPIO Pinout](https://pinout.xyz/) - Interactive pin reference
- [GoPiGo3 Documentation](https://gopigo3.readthedocs.io/) - Robot documentation

---

**Need Help?** Check the troubleshooting section or run the verification script!

