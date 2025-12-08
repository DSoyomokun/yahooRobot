# Yahoo Robot Documentation

## Project Structure

```
yahoo/
├── config/          # Configuration files
│   ├── room.json    # Map and waypoints
│   ├── gains.json   # PID tuning parameters
│   └── pins.json    # GPIO pin assignments
├── nav/             # Navigation modules
│   ├── odom.py      # Odometry tracking
│   ├── drive.py     # Motor control
│   └── route.py     # Path planning
├── io/              # Input/Output devices
│   ├── feeder.py    # Package feeder
│   ├── collector.py # Package collector
│   ├── leds.py      # LED control
│   └── buzzer.py    # Buzzer alerts
├── sense/           # Sensors
│   ├── laser.py     # Laser range finder
│   ├── ultrasonic.py # Ultrasonic sensors
│   ├── tof.py       # Time-of-Flight sensors
│   ├── hx711.py     # Load cell (weight)
│   ├── camera.py    # Camera utilities
│   └── gesture.py   # Gesture detection (hand raising)
├── mission/         # High-level behaviors
│   ├── deliver.py   # Delivery mission
│   ├── wait.py      # Waiting behavior
│   └── collect.py   # Collection mission
└── webui/           # Web interface
    └── app.py       # Flask application

```

## Getting Started

1. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

2. Run in simulation mode:

   ```bash
   python main.py --simulate
   ```

3. Run with hardware:

   ```bash
   python main.py
   ```

4. Start web interface:
   ```bash
   python main.py --webui
   ```

## Configuration

Edit the JSON files in `yahoo/config/` to customize:

- Map layout and waypoints (`room.json`)
- PID gains for navigation (`gains.json`)
- Pin assignments (`pins.json`)

## Development

- Add tests in `tests/`
- Keep logs in `build-log/`
- Save screenshots in `screenshots/`
- Use Jupyter notebooks in `notebooks/` for analysis
