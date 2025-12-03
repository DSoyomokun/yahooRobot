# 🎮 Yahoo Robot Commands Reference

Quick reference guide for running the Yahoo Robot and its test scripts.

---

## 📋 Table of Contents

- [Robot Commands](#robot-commands)
- [Test Commands](#test-commands)
- [Quick Examples](#quick-examples)

---

## 🤖 Robot Commands

### Run the Robot

```bash
# Run robot (default)
python3 main.py run

# Run in simulation mode (no hardware required)
python3 main.py run --simulate

# Run with debug logging
python3 main.py run --debug

# Start web interface
python3 main.py run --webui

# Combine options
python3 main.py run --simulate --debug
```

**Backward Compatibility:** The old-style commands still work:
```bash
python3 main.py --simulate
python3 main.py --debug
python3 main.py --webui
```

---

## 🧪 Test Commands

### List Available Tests

```bash
python3 main.py test --list
```

### Run Tests

```bash
# Run gesture detection test (Mac)
python3 main.py test mac

# Run camera test
python3 main.py test camera

# Run gesture test (alias for mac)
python3 main.py test gesture
```

---

## 🚀 Quick Examples

### Development on Mac

```bash
# Test camera
python3 main.py test camera

# Test gesture detection
python3 main.py test mac

# Run robot in simulation mode
python3 main.py run --simulate --debug
```

### On Raspberry Pi

```bash
# Test camera (when test_pi.py exists)
python3 main.py test pi

# Run robot with hardware
python3 main.py run

# Run with debug logging
python3 main.py run --debug
```

---

## 📝 Adding New Tests

To add a new test, update the `test_scripts` dictionary in `main.py`:

```python3
test_scripts = {
    'mac': 'tests/test_gesture_mac.py',
    'camera': 'scripts/camera_test.py',
    'gesture': 'tests/test_gesture_mac.py',
    'your_new_test': 'path/to/your_test.py',  # Add here
}
```

Then run it with:
```bash
python3 main.py test your_new_test
```

---

## 🔍 Help

Get help for any command:

```bash
# General help
python3 main.py --help

# Help for run command
python3 main.py run --help

# Help for test command
python3 main.py test --help
```

---

## 📚 Related Documentation

- [Robot Development Workflow](ROBOT_DEV_WORKFLOW.md) - How to sync code to robot
- [Quick Start Guide](QUICK_START.md) - Getting started with the project
- [Raspberry Pi Setup](RASPBERRY_PI_SETUP.md) - Pi-specific setup instructions

