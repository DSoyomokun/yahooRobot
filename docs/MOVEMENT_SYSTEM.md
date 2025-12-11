# 🚗 Yahoo Robot Movement System

Complete guide to understanding and modifying robot movement.

---

## Architecture Overview

```
main.py
  └─> Robot (yahoo/robot.py)
       └─> Drive (yahoo/nav/drive.py)
            └─> GoPiGo3 Hardware (easygopigo3 library)
                 └─> Physical Motors
```

---

## Quick Reference: Available Movement Commands

| Command | Speed (DPS) | Description |
|---------|-------------|-------------|
| `robot.drive.forward(speed)` | 200 | Move forward |
| `robot.drive.backward(speed)` | 200 | Move backward |
| `robot.drive.turn_left(speed)` | 150 | Turn left in place |
| `robot.drive.turn_right(speed)` | 150 | Turn right in place |
| `robot.drive.stop()` | 0 | Stop all motors |
| `robot.drive.drive_cm(distance, speed)` | 200 | Drive specific distance |
| `robot.drive.turn_degrees(angle, speed)` | 150 | Turn specific angle |
| `robot.drive.set_motor_dps(left, right)` | Custom | Direct motor control |

**DPS = Degrees Per Second** (motor shaft rotation speed)
- Typical range: -300 to 300 DPS
- Default forward/backward: 200 DPS
- Default turning: 150 DPS

---

## File-by-File Breakdown

### 1. `main.py` - Main Control Loop

**What it does:** Defines the robot's behavior sequence

**Current behavior (lines 147-176):**
1. Move forward for 3 seconds
2. Stop
3. Turn right for 2 seconds
4. Stop
5. Move backward for 2 seconds
6. Stop
7. Idle (wait for Ctrl+C)

**Example: Drive in a square**
```python
logger.info("Robot ready. Starting square pattern...")
import time

try:
    for i in range(4):
        logger.info(f"Side {i+1}...")
        robot.drive.forward(200)
        time.sleep(2)  # Drive 2 seconds per side
        robot.drive.stop()

        robot.drive.turn_right(150)
        time.sleep(1.5)  # Adjust timing for ~90 degree turn
        robot.drive.stop()
        time.sleep(0.5)  # Brief pause

    logger.info("Square complete!")
    while True:
        time.sleep(1)

except Exception as e:
    logger.error(f"Movement error: {e}")
    robot.drive.stop()
```

**Example: Follow a sensor**
```python
import time

try:
    while True:
        # Pseudocode - add your sensor logic
        distance = robot.distance_sensor.read()

        if distance > 30:  # Object far away
            robot.drive.forward(150)
        elif distance < 10:  # Too close
            robot.drive.backward(100)
        else:  # Just right
            robot.drive.stop()

        time.sleep(0.1)  # Check 10 times per second

except KeyboardInterrupt:
    robot.drive.stop()
```

---

### 2. `yahoo/robot.py` - Robot Initialization

**What it does:** Sets up all robot subsystems

**Key initialization (line 62):**
```python
self.drive = Drive(robot=self, simulate=self.simulate)
```

**Available subsystems:**
- `robot.drive` - Movement control
- `robot.leds` - LED control
- `robot.gpg` - Direct GoPiGo3 hardware access

**Battery monitoring:**
```python
voltage = robot.get_battery_voltage()  # Returns voltage (V)
```

⚠️ **You usually don't need to edit this file** - it's just setup.

---

### 3. `yahoo/nav/drive.py` - Drive Controller

**What it does:** Implements all movement commands

#### Core Method: `set_motor_dps(left_dps, right_dps)` (lines 44-62)

All other methods use this. It directly controls motor speeds:

```python
def set_motor_dps(self, left_dps: float, right_dps: float):
    """Set motor speeds in degrees per second."""
    if self.simulate:
        logger.info(f"[DRIVE] Motors: L={left_dps:.0f} DPS, R={right_dps:.0f} DPS")
        return

    if self.gpg:
        self.gpg.set_motor_dps(self.gpg.MOTOR_LEFT, left_dps)
        self.gpg.set_motor_dps(self.gpg.MOTOR_RIGHT, right_dps)
```

#### Movement Methods

**Forward/Backward (lines 87-105)**
```python
def forward(self, speed: Optional[float] = None):
    speed = speed or self.DEFAULT_SPEED  # Default: 200
    self.set_motor_dps(speed, speed)     # Both motors same speed

def backward(self, speed: Optional[float] = None):
    speed = speed or self.DEFAULT_SPEED
    self.set_motor_dps(-speed, -speed)   # Negative = reverse
```

**Turning (lines 107-125)**
```python
def turn_left(self, speed: Optional[float] = None):
    speed = speed or self.TURN_SPEED
    self.set_motor_dps(-speed, speed)    # Left back, right forward

def turn_right(self, speed: Optional[float] = None):
    speed = speed or self.TURN_SPEED
    self.set_motor_dps(speed, -speed)    # Left forward, right back
```

**Precision Movements (lines 127-170)**
```python
def drive_cm(self, distance_cm: float, speed: Optional[float] = None):
    """Drive exact distance using encoders"""
    if self.gpg:
        self.gpg.drive_cm(distance_cm, blocking=True)

def turn_degrees(self, degrees: float, speed: Optional[float] = None):
    """Turn exact angle using encoders"""
    if self.gpg:
        self.gpg.turn_degrees(degrees, blocking=True)
```

#### Default Speeds (lines 21-24)

```python
DEFAULT_SPEED = 200  # Forward/backward speed
TURN_SPEED = 150     # Turning speed
SLOW_SPEED = 100     # Slow/careful speed
```

**To change defaults:** Edit these values and redeploy.

---

## Adding Custom Movement Methods

### Example 1: Drive in a Circle

Add to `yahoo/nav/drive.py`:

```python
def circle_right(self, radius_factor: float = 0.5):
    """
    Drive in a circle to the right.

    Args:
        radius_factor: 0.0-1.0, smaller = tighter circle
    """
    left_speed = self.DEFAULT_SPEED
    right_speed = self.DEFAULT_SPEED * radius_factor
    self.set_motor_dps(left_speed, right_speed)

def circle_left(self, radius_factor: float = 0.5):
    """Drive in a circle to the left."""
    left_speed = self.DEFAULT_SPEED * radius_factor
    right_speed = self.DEFAULT_SPEED
    self.set_motor_dps(left_speed, right_speed)
```

Usage in `main.py`:
```python
robot.drive.circle_right(0.5)  # Wide right circle
time.sleep(5)
robot.drive.stop()
```

### Example 2: Gentle Curve

```python
def curve_forward(self, left_speed: float = None, right_speed: float = None):
    """
    Drive forward with different wheel speeds for gentle curves.

    Args:
        left_speed: Left motor speed (default: DEFAULT_SPEED)
        right_speed: Right motor speed (default: DEFAULT_SPEED)
    """
    left = left_speed or self.DEFAULT_SPEED
    right = right_speed or self.DEFAULT_SPEED
    self.set_motor_dps(left, right)
```

Usage:
```python
# Gentle right curve
robot.drive.curve_forward(left_speed=200, right_speed=150)
time.sleep(3)
robot.drive.stop()
```

### Example 3: Speed Ramping

```python
def ramp_forward(self, target_speed: float, ramp_time: float = 2.0):
    """
    Gradually increase speed from 0 to target.

    Args:
        target_speed: Final speed in DPS
        ramp_time: Time to reach target speed (seconds)
    """
    import time
    steps = 20
    delay = ramp_time / steps

    for i in range(steps + 1):
        speed = (target_speed * i) / steps
        self.set_motor_dps(speed, speed)
        time.sleep(delay)
```

---

## Common Patterns

### Pattern 1: Timed Movements

```python
# Move for specific duration
robot.drive.forward(200)
time.sleep(3)  # Move for 3 seconds
robot.drive.stop()
```

### Pattern 2: Distance-Based Movements

```python
# Move exact distance (uses encoders)
robot.drive.drive_cm(50, speed=150)  # Drive 50cm forward
robot.drive.drive_cm(-30)            # Drive 30cm backward
```

### Pattern 3: Angle-Based Turns

```python
# Turn exact angles (uses encoders)
robot.drive.turn_degrees(90)   # Turn right 90°
robot.drive.turn_degrees(-45)  # Turn left 45°
```

### Pattern 4: Sensor-Based Movement

```python
while True:
    sensor_value = read_some_sensor()

    if sensor_value > threshold:
        robot.drive.forward(150)
    else:
        robot.drive.stop()

    time.sleep(0.1)
```

### Pattern 5: State Machine

```python
state = "FORWARD"

while True:
    if state == "FORWARD":
        robot.drive.forward(200)
        if some_condition():
            state = "TURN"

    elif state == "TURN":
        robot.drive.turn_right(150)
        if turned_enough():
            state = "STOP"

    elif state == "STOP":
        robot.drive.stop()
        break

    time.sleep(0.1)
```

---

## Testing Movement

### Test Script Template

Create `tests/test_my_movement.py`:

```python
#!/usr/bin/env python3
"""Test custom movement patterns"""

import time
import logging
from yahoo.robot import Robot

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_square():
    """Drive in a square pattern"""
    with Robot() as robot:
        logger.info("Testing square pattern...")

        for side in range(4):
            logger.info(f"Side {side + 1}")
            robot.drive.forward(200)
            time.sleep(2)
            robot.drive.stop()

            robot.drive.turn_right(150)
            time.sleep(1.5)
            robot.drive.stop()
            time.sleep(0.5)

        logger.info("Square complete!")

if __name__ == "__main__":
    test_square()
```

Run on robot:
```bash
python3 tests/test_my_movement.py
```

---

## Speed Guidelines

| Speed (DPS) | Use Case |
|-------------|----------|
| 50-100 | Slow/careful navigation, precise positioning |
| 150-200 | Normal driving, general navigation |
| 200-250 | Fast driving, open spaces |
| 250-300 | Maximum speed (use carefully!) |

⚠️ **Safety:**
- Start with lower speeds when testing
- Always test in open space first
- Keep `robot.drive.stop()` easily accessible (Ctrl+C)
- Monitor battery voltage - low battery affects performance

---

## Motor Physics

### Understanding DPS (Degrees Per Second)

- **360 DPS** = 1 full wheel rotation per second
- **200 DPS** ≈ 0.56 rotations/second
- Wheel diameter affects actual distance traveled

### Differential Drive

The robot uses **differential drive** - controlling two wheels independently:

| Left Motor | Right Motor | Result |
|------------|-------------|--------|
| +200 | +200 | Forward |
| -200 | -200 | Backward |
| +150 | -150 | Turn right in place |
| -150 | +150 | Turn left in place |
| +200 | +100 | Gentle right curve |
| +100 | +200 | Gentle left curve |

---

## Troubleshooting

### Robot doesn't move
1. Check battery: `robot.get_battery_voltage()` (should be > 7.0V)
2. Check motors are not blocked
3. Verify you're not in simulation mode (`simulate=False`)
4. Check logs for errors

### Robot moves erratically
1. Low battery - charge it
2. Floor surface may be too slippery
3. Speed too high - reduce DPS
4. Motor encoders may need calibration

### Turns are inconsistent
1. Floor surface affects turn radius
2. Battery voltage affects motor power
3. Use `turn_degrees()` for precise turns
4. Calibrate turn timing for your surface

### Motors make noise but don't move
1. Battery critically low
2. Motors mechanically blocked
3. Weight too heavy for robot
4. Check motor connections

---

## Advanced: Direct Motor Control

For maximum control, use `set_motor_dps()` directly:

```python
# Custom movement pattern
robot.drive.set_motor_dps(left_dps=180, right_dps=220)  # Curve left
time.sleep(2)

robot.drive.set_motor_dps(left_dps=220, right_dps=180)  # Curve right
time.sleep(2)

robot.drive.stop()
```

---

## Next Steps

1. **Integrate sensors:** Add distance sensors, cameras, or line followers
2. **Add navigation:** Implement odometry, path planning, or SLAM
3. **Mission control:** Connect to `MissionController` for autonomous behavior
4. **Web interface:** Control robot via web UI (`main.py --webui`)

---

## Summary

| Want to... | Edit this file | Method/Section |
|------------|----------------|----------------|
| Change robot behavior | `main.py` | Lines 147-176 |
| Add new movement types | `yahoo/nav/drive.py` | Add new methods |
| Change default speeds | `yahoo/nav/drive.py` | Lines 21-24 |
| Test movements | Create `tests/test_*.py` | Use `with Robot()` pattern |
| Understand hardware | `yahoo/robot.py` | Initialization code |

**Key concept:**
- `main.py` = WHAT the robot does (behavior)
- `yahoo/nav/drive.py` = HOW the robot moves (implementation)

Happy coding! 🚗💨
