# Wireless Connection Guide for GoPiGo3

This guide will help you connect to your GoPiGo3 robot wirelessly and begin development.

## Prerequisites

- ✅ GoPiGo3 assembled with Raspberry Pi
- ✅ Raspberry Pi OS installed on SD card
- ✅ Batteries charged (> 7V)
- ✅ WiFi network available
- ✅ Your development computer (Windows/Mac/Linux)

---

## Step 1: Configure WiFi on Raspberry Pi

### Option A: With Monitor and Keyboard

1. **Connect peripherals:**

   - Monitor via HDMI
   - USB keyboard and mouse
   - Power on GoPiGo3

2. **Configure WiFi:**

   ```bash
   sudo raspi-config
   ```

   - Navigate to: `1 System Options` → `S1 Wireless LAN`
   - Enter WiFi SSID (network name)
   - Enter WiFi password
   - Exit and reboot: `sudo reboot`

3. **Find IP address:**
   ```bash
   hostname -I
   # Note the IP address shown
   ```

### Option B: Headless Setup (No Monitor)

1. **Remove SD card from Pi and insert into your computer**

2. **Navigate to the boot partition** (appears as a drive on Windows)

3. **Create WiFi configuration file:**

   Create a file named `wpa_supplicant.conf` with this content:

   ```conf
   country=US
   ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
   update_config=1

   network={
       ssid="YOUR_WIFI_NAME"
       psk="YOUR_WIFI_PASSWORD"
       key_mgmt=WPA-PSK
   }
   ```

   Replace:

   - `YOUR_WIFI_NAME` with your WiFi network name
   - `YOUR_WIFI_PASSWORD` with your WiFi password
   - `US` with your country code if different

4. **Enable SSH:**

   Create an empty file named `ssh` (no extension) on the boot partition

   **Windows PowerShell:**

   ```powershell
   # Assuming boot drive is D:
   New-Item -Path "D:\ssh" -ItemType File
   ```

5. **Eject SD card safely** and insert back into Raspberry Pi

6. **Power on the Pi** - Wait 1-2 minutes for boot

---

## Step 2: Find Your Raspberry Pi

### Method 1: Use Hostname (Easiest)

```bash
# From Windows PowerShell or Command Prompt
ping raspberrypi.local
```

If successful, you'll see the IP address.

### Method 2: Check Router

1. Log into your router's admin panel
2. Look for connected devices
3. Find "raspberrypi" or device with MAC address starting with `B8:27:EB` or `DC:A6:32`

### Method 3: Network Scan

**Windows - Use Advanced IP Scanner:**

- Download: https://www.advanced-ip-scanner.com/
- Scan your network
- Look for "Raspberry Pi Foundation" in manufacturer column

**Windows PowerShell (if you have nmap):**

```powershell
nmap -sn 192.168.1.0/24
# Replace 192.168.1.0/24 with your network range
```

---

## Step 3: Connect via SSH

### From Windows PowerShell:

```powershell
# Using hostname (preferred)
ssh pi@raspberrypi.local

# Or using IP address
ssh pi@192.168.1.xxx  # Replace with your Pi's IP
```

**Default password:** `raspberry`

⚠️ **Change the default password immediately:**

```bash
passwd
```

### First Login Checklist:

```bash
# Update system
sudo apt-get update
sudo apt-get upgrade -y

# Check battery
python3 -c "import gopigo3; print('Battery:', gopigo3.GoPiGo3().get_voltage_battery(), 'V')"

# If gopigo3 not installed yet, see Step 4
```

---

## Step 4: Transfer Your Project to Raspberry Pi

### Method 1: Using Git (Recommended)

**On Raspberry Pi:**

```bash
# Install git if not present
sudo apt-get install -y git

# Clone your repository
cd ~
git clone YOUR_REPO_URL csc4120
cd csc4120
```

### Method 2: Using SCP (Secure Copy)

**From Windows PowerShell (in your project directory):**

```powershell
# Copy entire project
scp -r . pi@raspberrypi.local:~/csc4120/

# Or using IP address
scp -r . pi@192.168.1.xxx:~/csc4120/
```

### Method 3: Using VS Code Remote SSH

1. **Install VS Code Extension:**

   - Open VS Code
   - Install "Remote - SSH" extension

2. **Connect to Pi:**

   - Press `Ctrl+Shift+P`
   - Type "Remote-SSH: Connect to Host"
   - Enter: `pi@raspberrypi.local`
   - Enter password
   - Open folder: `/home/pi/csc4120`

3. **Edit directly on Pi!**
   - Changes are made in real-time
   - Can run terminal commands directly
   - Much easier development workflow

---

## Step 5: Install GoPiGo3 Software on Raspberry Pi

```bash
# SSH into your Pi first
ssh pi@raspberrypi.local

# Run official GoPiGo3 installer
curl -kL dexterindustries.com/update_gopigo3 | bash

# This will:
# - Install GoPiGo3 Python library
# - Configure I2C
# - Set up permissions
# - Install dependencies

# Reboot after installation
sudo reboot
```

Wait 1 minute, then reconnect:

```bash
ssh pi@raspberrypi.local
```

---

## Step 6: Install Project Dependencies

```bash
# Navigate to project
cd ~/csc4120

# Install Python dependencies
pip3 install -r requirements-pi.txt

# Or install manually if needed:
pip3 install Flask Flask-SocketIO numpy PyYAML python-dotenv smbus2 RPi.GPIO
```

---

## Step 7: Verify Hardware Connection

```bash
# Run hardware check script
python3 scripts/check_hardware.py
```

**Expected output:**

```
  GoPiGo3 Hardware Check
============================================================

1. Initializing GoPiGo3...
   ✅ GoPiGo3 initialized successfully

2. Checking firmware...
   ✅ Firmware version: 1.0.0

3. Checking hardware...
   ✅ Hardware version: 3.2.0

4. Checking battery...
   Battery Voltage: 10.5V
   ✅ Battery level: GOOD

...
```

---

## Step 8: Test Basic Movement

### Automated Movement Test:

```bash
python3 scripts/test_movement.py
```

This will:

- ✅ Move forward for 2 seconds
- ✅ Move backward for 2 seconds
- ✅ Turn right for 1 second
- ✅ Turn left for 1 second

⚠️ **Make sure robot has clear space!**

### Manual Control Test:

```bash
python3 scripts/manual_control.py
```

**Controls:**

- `W` - Forward
- `S` - Backward
- `A` - Turn Left
- `D` - Turn Right
- `SPACE` - Stop
- `+/-` - Speed control
- `Q` - Quit

---

## Step 9: Run Your Robot Software

```bash
# Basic mode
python3 main.py

# Debug mode (shows more info)
python3 main.py --debug

# With web interface (coming soon)
python3 main.py --webui
```

---

## Development Workflow

### Option 1: Edit on Windows, Deploy to Pi

**On Windows:**

```bash
# Make changes to code
# Test in simulation
python main.py --simulate

# Commit changes
git add .
git commit -m "Your changes"
git push
```

**On Raspberry Pi:**

```bash
# Pull updates
cd ~/csc4120
git pull

# Test on hardware
python3 scripts/test_movement.py
```

### Option 2: Edit Directly on Pi (VS Code Remote)

1. Use VS Code with Remote-SSH extension
2. Connect to `pi@raspberrypi.local`
3. Edit files directly
4. Run tests in integrated terminal
5. Commit from VS Code

---

## Troubleshooting

### Cannot Connect via SSH

**Check Pi is on network:**

```bash
ping raspberrypi.local
```

**Try IP address directly:**

```bash
ssh pi@192.168.1.xxx
```

**Check SSH is enabled:**

- If using headless setup, make sure `ssh` file was created on boot partition

### GoPiGo3 Not Detected

**Check I2C:**

```bash
sudo i2cdetect -y 1
# Should show device at address 0x08
```

**Enable I2C if not working:**

```bash
sudo raspi-config
# Interface Options → I2C → Enable
sudo reboot
```

**Check battery:**

```bash
# Low battery can prevent GoPiGo3 from working
# Needs > 7V for operation
```

### Permission Denied Errors

```bash
# Add user to i2c and gpio groups
sudo usermod -aG i2c,gpio,spi $USER

# Reboot for changes to take effect
sudo reboot
```

### WiFi Keeps Disconnecting

**Disable power management:**

```bash
sudo nano /etc/rc.local

# Add before 'exit 0':
/sbin/iwconfig wlan0 power off

# Save and reboot
sudo reboot
```

### Slow Performance

**Check CPU temperature:**

```bash
vcgencmd measure_temp

# If > 80°C, add cooling or reduce load
```

**Check memory:**

```bash
free -h
```

---

## Tips for Wireless Development

### 1. Use Static IP (Optional but Recommended)

Edit `/etc/dhcpcd.conf`:

```bash
sudo nano /etc/dhcpcd.conf
```

Add at the end:

```conf
interface wlan0
static ip_address=192.168.1.100/24
static routers=192.168.1.1
static domain_name_servers=192.168.1.1 8.8.8.8
```

Replace IPs with your network settings.

### 2. Create SSH Key for Passwordless Login

**On Windows:**

```powershell
# Generate SSH key (if you don't have one)
ssh-keygen -t rsa

# Copy to Pi
type $env:USERPROFILE\.ssh\id_rsa.pub | ssh pi@raspberrypi.local "cat >> .ssh/authorized_keys"

# Now you can connect without password!
ssh pi@raspberrypi.local
```

### 3. Use Screen/Tmux for Persistent Sessions

```bash
# Install screen
sudo apt-get install screen

# Start a session
screen -S robot

# Run your program
python3 main.py

# Detach: Ctrl+A, then D
# Reconnect later: screen -r robot
```

### 4. Monitor Remotely

```bash
# Check robot status from anywhere
ssh pi@raspberrypi.local "python3 ~/csc4120/scripts/check_hardware.py"

# View logs
ssh pi@raspberrypi.local "tail -f ~/csc4120/build-log/robot.log"
```

---

## Next Steps

1. ✅ **Connected wirelessly** - You can now SSH into your Pi
2. ✅ **Hardware verified** - GoPiGo3 is working
3. ✅ **Basic movement tested** - Motors are functional

**Now you can:**

- Develop code on Windows in simulation mode
- Deploy and test on actual hardware wirelessly
- Monitor robot operation remotely
- Build your delivery robot features!

See [QUICK_START.md](QUICK_START.md) for development workflow.

---

## Quick Reference

```bash
# Connect to Pi
ssh pi@raspberrypi.local

# Check battery
python3 -c "import gopigo3; print(gopigo3.GoPiGo3().get_voltage_battery())"

# Test movement
python3 scripts/test_movement.py

# Manual control
python3 scripts/manual_control.py

# Run robot
python3 main.py

# Update code (if using git)
cd ~/csc4120 && git pull

# View logs
tail -f build-log/robot.log
```

Happy wireless robot development! 🤖📡
