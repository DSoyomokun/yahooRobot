# yahooRobot

**Classroom Paper Assistant Robot** - An autonomous classroom robot built on GoPiGo3

## Overview

Yahoo Robot is a GoPiGo3-based autonomous robot designed for classroom paper distribution and collection. It features navigation, obstacle avoidance, computer vision-based person detection, and paper handling capabilities.

## Quick Start

### On Windows/Mac (Development - No Hardware)

```bash
# Create virtual environment
python -m venv venv --without-pip
.\venv\Scripts\Activate.ps1    # Windows
# source venv/bin/activate        # Mac/Linux

# Install dependencies
python -m ensurepip --upgrade
pip install --upgrade pip
pip install -r requirements-dev.txt

# Test simulation mode
python scripts/test_simulation.py
python main.py --simulate
```

### On Raspberry Pi (With GoPiGo3 Hardware)

```bash
# Install GoPiGo3 library first
curl -kL dexterindustries.com/update_gopigo3 | bash

# Install Python dependencies
pip3 install -r requirements-pi.txt

# Check hardware
python3 scripts/check_hardware.py

# Test movement
python3 scripts/test_movement.py
python3 scripts/manual_control.py

# Run robot
python3 main.py
python3 main.py --webui    # with web interface
```

**See [docs/QUICK_START.md](docs/QUICK_START.md) for detailed instructions**

**See [docs/WIRELESS_SETUP.md](docs/WIRELESS_SETUP.md) for wireless connection guide**

## Project Structure

- **yahoo/** - Main robot package
    - `config/` - Configuration files (room layout, PID gains, pin assignments)
    - `nav/` - Navigation (odometry, drive control, routing)
    - `io/` - I/O devices (feeder, collector, LEDs, buzzer)
    - `sense/` - Sensors (ultrasonic, ToF, cameras, load cells, gesture detection)
    - `mission/` - Mission behaviors (deliver, collect, wait)
    - `webui/` - Flask-based web interface

- **tests/** - Unit tests
- **utils/** - Utility functions
- **docs/** - Additional documentation
- **build-log/** - Runtime logs
- **screenshots/** - Debug images
- **notebooks/** - Jupyter notebooks for analysis
- **scripts/** - Helper scripts

## Features

- GoPiGo3 hardware abstraction
- Simulation mode for development without hardware
- Configurable JSON-based settings
- Modular sensor integration
- PID-based navigation control
- **Robust gesture detection with dual-hand tracking** (left, right, or both hands raised)
- **Temporal smoothing and cooldown** for reliable classroom interaction
- Test paper scanning and grading system
- Web-based control interface (coming soon)
- Autonomous navigation (coming soon)
- Package detection and handling (coming soon)

## Configuration

See `yahoo/config/` for:

- **room.json** - Map layout, waypoints, delivery zones
- **gains.json** - PID tuning, motor speeds, odometry parameters
- **pins.json** - GPIO pin assignments for sensors and actuators

## Documentation

See [docs/README.md](docs/README.md) for detailed documentation.

**Key Documentation:**
- [Gesture Detection Guide](docs/GESTURE_DETECTION.md) - Hand-raising detection system
- [Robot Development Workflow](docs/ROBOT_DEV_WORKFLOW.md) - How to sync code to robot
- [Commands Reference](docs/COMMANDS.md) - All available commands
- [Scanner Module](yahoo/mission/scanner/README.md) - Test paper scanning system

## Requirements

- GoPiGo3 robot (or simulation mode)
- Raspberry Pi (3/4/5)
- Python 3.7+
- See `requirements.txt` for Python dependencies

## License

[Add your license here]
