# Quick Start Guide

## For Windows/Mac Development (No Hardware)

### 1. Install Dependencies

```bash
# Windows PowerShell
python -m venv venv --without-pip
.\venv\Scripts\Activate.ps1
python -m ensurepip --upgrade
pip install --upgrade pip
pip install -r requirements-dev.txt

# Mac/Linux
python3 -m venv venv
source venv/bin/activate
pip install -r requirements-dev.txt
```

### 2. Test Simulation Mode

```bash
# Activate virtual environment first!
# Windows:
.\venv\Scripts\Activate.ps1

# Mac/Linux:
source venv/bin/activate

# Run simulation test
python scripts/test_simulation.py

# Or run main program in simulation
python main.py --simulate
```

### 3. Develop Your Code

Write code in the `yahoo/` modules. The robot will automatically use simulation mode when `gopigo3` library is not available.

---

## For Raspberry Pi (With Hardware)

### 1. Initial Setup

See [RASPBERRY_PI_SETUP.md](RASPBERRY_PI_SETUP.md) for detailed instructions.

Quick version:

```bash
# Update system
sudo apt-get update && sudo apt-get upgrade -y

# Install GoPiGo3
curl -kL dexterindustries.com/update_gopigo3 | bash
sudo reboot

# Enable I2C
sudo raspi-config
# Interface Options → I2C → Enable

# Clone project
cd ~
git clone <your-repo-url> csc4120
cd csc4120

# Install dependencies
pip3 install -r requirements-pi.txt
```

### 2. Check Hardware

```bash
# Verify GoPiGo3 is detected
python3 scripts/check_hardware.py
```

Expected output:

- ✅ GoPiGo3 initialized
- ✅ Battery voltage > 7V
- ✅ Encoders working

### 3. Test Movement

```bash
# Automated movement test
python3 scripts/test_movement.py

# Manual keyboard control
python3 scripts/manual_control.py
```

### 4. Run Your Robot

```bash
# Basic mode
python3 main.py

# With web interface
python3 main.py --webui

# Debug mode
python3 main.py --debug
```

---

## Project Structure Quick Reference

```
yahoo/
├── config/           # Configuration files
│   ├── room.json     # Map layout, waypoints, delivery zones
│   ├── gains.json    # PID tuning, motor speeds
│   └── pins.json     # GPIO pin assignments
├── nav/              # Navigation modules
│   ├── odom.py       # Odometry tracking (TODO)
│   ├── drive.py      # Motor control (TODO)
│   └── route.py      # Path planning (TODO)
├── io/               # Input/Output devices
│   ├── feeder.py     # Package feeder (TODO)
│   ├── collector.py  # Package collector (TODO)
│   ├── leds.py       # LED control (TODO)
│   └── buzzer.py     # Buzzer alerts (TODO)
├── sense/            # Sensors
│   ├── ultrasonic.py # Ultrasonic sensors (TODO)
│   ├── tof.py        # Time-of-Flight sensors (TODO)
│   ├── hx711.py      # Load cell/weight sensor (TODO)
│   └── cameras.py    # Camera modules (TODO)
├── mission/          # Mission behaviors
│   ├── deliver.py    # Delivery mission (TODO)
│   ├── collect.py    # Collection mission (TODO)
│   └── wait.py       # Waiting behavior (TODO)
└── webui/            # Web interface
    └── app.py        # Flask application (TODO)
```

---

## Common Tasks

### Add a New Sensor

1. Create module in `yahoo/sense/` (e.g., `ultrasonic.py`)
2. Define sensor class
3. Add pin configuration to `yahoo/config/pins.json`
4. Import in `yahoo/sense/__init__.py`
5. Test individually before integrating

### Tune PID Parameters

1. Edit `yahoo/config/gains.json`
2. Adjust `kp`, `ki`, `kd` values
3. Test with manual control
4. Document good values

### Add New Mission

1. Create module in `yahoo/mission/` (e.g., `patrol.py`)
2. Implement mission class with `start()`, `update()`, `stop()` methods
3. Add to mission controller
4. Test in controlled environment

---

## Testing

### Run All Tests

```bash
# Activate venv first
pytest tests/

# With coverage
pytest --cov=yahoo tests/
```

### Code Quality

```bash
# Format code
black yahoo/ scripts/ main.py

# Lint code
pylint yahoo/
```

---

## Troubleshooting

### Windows: "Cannot run scripts"

```powershell
# Run as Administrator:
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Virtual Environment Issues

```bash
# Delete and recreate
rm -rf venv  # or: Remove-Item -Recurse -Force venv
python -m venv venv
# Install dependencies again
```

### Raspberry Pi: GoPiGo3 Not Detected

```bash
# Check I2C
sudo i2cdetect -y 1

# Should show device at 0x08
# If not, check:
# 1. Power (battery charged?)
# 2. I2C enabled in raspi-config
# 3. Physical connections
```

### Import Errors

```bash
# Make sure you're in project root
cd ~/csc4120  # or wherever your project is

# And virtual environment is activated
source venv/bin/activate  # Linux/Mac
.\venv\Scripts\Activate.ps1  # Windows
```

---

## Next Steps

1. ✅ **Setup complete** - You can now develop!

2. **Implement core modules**

   - Start with `yahoo/nav/drive.py` for basic movement
   - Add sensors in `yahoo/sense/`
   - Build up to full autonomy

3. **Test incrementally**

   - Test each module individually
   - Use simulation mode for development
   - Test on hardware frequently

4. **Build missions**

   - Start simple (drive to point)
   - Add complexity gradually
   - Always have emergency stop ready!

5. **Add web interface**
   - Create dashboard in `yahoo/webui/`
   - Add camera streaming
   - Remote monitoring and control

Happy coding! 🤖
