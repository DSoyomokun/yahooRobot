# Raspberry Pi Setup Guide

This guide will help you set up your GoPiGo3 robot on a Raspberry Pi.

## Prerequisites

- GoPiGo3 robot kit assembled
- Raspberry Pi (3B+, 4, or 5) with Raspberry Pi OS installed
- MicroSD card (16GB+ recommended)
- Charged batteries (need at least 7V for safe operation)

## Step 1: Initial Raspberry Pi Setup

### 1.1 Flash Raspberry Pi OS

```bash
# Use Raspberry Pi Imager to flash Raspberry Pi OS (32-bit recommended)
# Enable SSH and configure WiFi during imaging if headless
```

### 1.2 Connect to Pi

```bash
# SSH into your Pi (replace with your Pi's IP)
ssh pi@raspberrypi.local
# Default password: raspberry (change it!)
```

### 1.3 Update System

```bash
sudo apt-get update
sudo apt-get upgrade -y
sudo apt-get install -y git python3-pip
```

## Step 2: Install GoPiGo3 Software

### 2.1 Install GoPiGo3 Library

```bash
# Official Dexter Industries installation
curl -kL dexterindustries.com/update_gopigo3 | bash

# Reboot after installation
sudo reboot
```

### 2.2 Enable I2C

```bash
# Run Raspberry Pi configuration tool
sudo raspi-config

# Navigate to: Interface Options → I2C → Enable
# Exit and reboot
```

### 2.3 Verify I2C Connection

```bash
# Install i2c tools if not present
sudo apt-get install -y i2c-tools

# Scan for I2C devices (GoPiGo3 should be at 0x08)
sudo i2cdetect -y 1
```

Expected output:

```
     0  1  2  3  4  5  6  7  8  9  a  b  c  d  e  f
00:          -- -- -- -- -- 08 -- -- -- -- -- -- --
...
```

### 2.4 Add User to I2C Group

```bash
sudo usermod -aG i2c $USER
# Log out and back in for this to take effect
```

## Step 3: Clone Your Project

```bash
# Navigate to home directory
cd ~

# Clone your repository
git clone <your-repo-url> csc4120
cd csc4120
```

## Step 4: Install Python Dependencies

```bash
# Install project dependencies for Raspberry Pi
pip3 install -r requirements-pi.txt

# Or install manually:
pip3 install Flask Flask-SocketIO numpy PyYAML python-dotenv smbus2 RPi.GPIO
```

## Step 5: Test Hardware

### 5.1 Check Hardware Status

```bash
python3 scripts/check_hardware.py
```

This should show:

- ✅ GoPiGo3 initialized
- ✅ Firmware and hardware versions
- ✅ Battery voltage (should be > 7V)
- ✅ Motor encoders working

### 5.2 Test Basic Movement

```bash
python3 scripts/test_movement.py
```

This will:

- Move forward for 2 seconds
- Move backward for 2 seconds
- Turn right for 1 second
- Turn left for 1 second

### 5.3 Manual Control Test

```bash
python3 scripts/manual_control.py
```

Use keyboard to control:

- `W` = Forward
- `S` = Backward
- `A` = Turn Left
- `D` = Turn Right
- `SPACE` = Stop
- `Q` = Quit

## Step 6: Run Your Robot Software

### 6.1 Test in Simulation Mode (optional)

```bash
# This works even without GoPiGo3 hardware
python3 main.py --simulate
```

### 6.2 Run with Hardware

```bash
# Run main robot software
python3 main.py

# Or with web interface
python3 main.py --webui
```

## Troubleshooting

### Problem: "gopigo3 library not found"

```bash
# Reinstall GoPiGo3
cd ~
git clone https://github.com/DexterInd/GoPiGo3.git
cd GoPiGo3/Install
sudo bash update_gopigo3.sh
```

### Problem: "IOError: GoPiGo3 not detected"

```bash
# Check I2C:
sudo i2cdetect -y 1

# If no device at 0x08:
# 1. Check power (batteries charged?)
# 2. Check GoPiGo3 red board connections
# 3. Try different I2C cable
# 4. Check that I2C is enabled in raspi-config
```

### Problem: "Permission denied" on I2C

```bash
# Add user to i2c group and reboot
sudo usermod -aG i2c $USER
sudo reboot
```

### Problem: Low battery voltage

```bash
# Charge batteries!
# GoPiGo3 needs at least 7V to operate safely
# Optimal range: 9-12V
```

### Problem: Motors don't move

```bash
# Check:
# 1. Battery voltage (should be > 7V)
# 2. Motor connections to GoPiGo3 board
# 3. Run: python3 scripts/check_hardware.py
```

## Next Steps

Once hardware is working:

1. **Configure your robot**

   - Edit `yahoo/config/room.json` for your environment
   - Tune `yahoo/config/gains.json` for PID parameters
   - Update `yahoo/config/pins.json` for your sensors

2. **Add sensors**

   - Implement sensor modules in `yahoo/sense/`
   - Test each sensor individually

3. **Develop navigation**

   - Create odometry tracking in `yahoo/nav/odom.py`
   - Implement drive control in `yahoo/nav/drive.py`
   - Build path planning in `yahoo/nav/route.py`

4. **Build missions**

   - Create delivery behaviors in `yahoo/mission/`
   - Test in controlled environment first

5. **Web Interface**
   - Develop Flask app in `yahoo/webui/`
   - Add camera streaming
   - Create control dashboard

## Remote Development

### VS Code Remote SSH

```bash
# Install "Remote - SSH" extension in VS Code
# Connect to: pi@raspberrypi.local
# Edit code directly on the Pi!
```

### File Transfer

```bash
# From your computer, copy files to Pi:
scp -r . pi@raspberrypi.local:~/csc4120/

# Or use git to sync:
git push  # from computer
git pull  # on Pi
```

## Auto-start on Boot (Optional)

Create a systemd service:

```bash
# Create service file
sudo nano /etc/systemd/system/gopigo-robot.service
```

Add:

```ini
[Unit]
Description=GoPiGo Robot Service
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/csc4120
ExecStart=/usr/bin/python3 /home/pi/csc4120/main.py
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

Enable:

```bash
sudo systemctl enable gopigo-robot.service
sudo systemctl start gopigo-robot.service
sudo systemctl status gopigo-robot.service
```

## Useful Commands

```bash
# Check battery
python3 -c "import gopigo3; print(gopigo3.GoPiGo3().get_voltage_battery())"

# View logs
tail -f build-log/robot.log

# Monitor system resources
htop

# Check disk space
df -h

# Check temperature
vcgencmd measure_temp
```

Good luck with your robot! 🤖
