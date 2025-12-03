# 🎮 Yahoo Robot Commands Reference

Quick reference guide for running the Yahoo Robot and its test scripts.

---

## 📋 Table of Contents

- [Development Aliases](#development-aliases) ⚡
- [Robot Commands](#robot-commands)
- [Test Commands](#test-commands)
- [Quick Examples](#quick-examples)

---

## ⚡ Development Aliases

**Quick setup:** Run `./scripts/setup_aliases.sh` to install these aliases automatically.

### Available Aliases

```bash
# Pull latest from GitHub (use on normal WiFi)
gitup

# Deploy code to robot (use on GoPiGo WiFi)
deploypi

# SSH into robot (normal, no GUI)
robopi

# SSH into robot with X11 forwarding (for GUI apps like cv2.imshow)
robopi_x

# Full sync - gitup + deploypi (ONLY when online)
fullsync
```

### Workflow Example

```bash
# Step 1: On normal WiFi - pull latest updates
gitup

# Step 2: Connect to GoPiGo WiFi, then deploy
deploypi

# Step 3: SSH into robot
robopi

# Step 4: Run your code
cd ~/yahooRobot
python3 main.py test mac
```

**💡 Why separate commands?**
- `gitup` needs internet (use on normal WiFi)
- `deploypi` works offline (use on GoPiGo WiFi)
- You might want to pull without deploying, or deploy without pulling

**📺 GUI Applications (X11 Forwarding)**

For apps that show windows (like `cv2.imshow`), use `robopi_x` instead of `robopi`:

1. **Install XQuartz on Mac** (if not already installed):
   ```bash
   brew install --cask xquartz
   ```

2. **Open XQuartz** (keep it running)

3. **Use `robopi_x` for GUI apps:**
   ```bash
   robopi_x                    # SSH with X11 forwarding
   echo $DISPLAY              # Verify (should show localhost:10.0)
   python3 main.py test pi_camera  # Run camera test with GUI
   ```

Windows will appear on your Mac via XQuartz.

See [Robot Development Workflow](ROBOT_DEV_WORKFLOW.md) for full details.

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

# Run Pi camera test (on Raspberry Pi)
python3 main.py test pi_camera
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

