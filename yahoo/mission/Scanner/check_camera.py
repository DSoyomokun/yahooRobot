#!/usr/bin/env python3
"""
Camera diagnostic script - checks camera status and provides troubleshooting info
"""
import os
import sys
from pathlib import Path

# Add project root to path
script_dir = Path(__file__).parent.resolve()
project_root = script_dir.parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

print("=" * 70)
print("📷 CAMERA DIAGNOSTIC CHECK")
print("=" * 70)
print()

# Check 1: Is this a Raspberry Pi?
is_pi = False
try:
    with open('/proc/cpuinfo', 'r') as f:
        if 'Raspberry Pi' in f.read():
            is_pi = True
except:
    pass

if is_pi:
    print("✅ Running on Raspberry Pi")
else:
    print("⚠️  Not detected as Raspberry Pi")
print()

# Check 2: Check for video devices
print("📹 Checking video devices:")
video_devices = []
for i in range(4):
    device = f"/dev/video{i}"
    if os.path.exists(device):
        video_devices.append(device)
        # Get device info
        try:
            stat = os.stat(device)
            print(f"  ✅ {device} exists (mode: {oct(stat.st_mode)[-3:]})")
        except Exception as e:
            print(f"  ⚠️  {device} exists but can't stat: {e}")
    else:
        print(f"  ❌ {device} not found")

if not video_devices:
    print("\n⚠️  No video devices found!")
    print("   This usually means:")
    print("   1. Camera is not enabled in raspi-config")
    print("   2. Camera module is not connected")
    print("   3. System needs a reboot after enabling camera")
else:
    print(f"\n✅ Found {len(video_devices)} video device(s)")
print()

# Check 3: Try OpenCV
print("🔍 Testing OpenCV camera access:")
try:
    import cv2
    print(f"  ✅ OpenCV version: {cv2.__version__}")
    
    # Try to open camera
    for i in range(2):
        print(f"\n  Trying to open /dev/video{i}...")
        cap = cv2.VideoCapture(i)
        if cap.isOpened():
            width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
            height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
            print(f"  ✅ Successfully opened /dev/video{i}")
            print(f"     Resolution: {int(width)}x{int(height)}")
            cap.release()
        else:
            print(f"  ❌ Failed to open /dev/video{i}")
            cap.release()
except ImportError:
    print("  ❌ OpenCV not installed")
except Exception as e:
    print(f"  ❌ Error: {e}")

print()

# Check 4: Test with libcamera (if available)
print("🔍 Testing libcamera (if available):")
if os.system("which libcamera-still > /dev/null 2>&1") == 0:
    print("  ✅ libcamera-still is available")
    print("  💡 Try: libcamera-still -o test.jpg")
else:
    print("  ⚠️  libcamera-still not found")

print()

# Summary and recommendations
print("=" * 70)
print("📋 RECOMMENDATIONS:")
print("=" * 70)

if not video_devices:
    print("1. Enable camera:")
    print("   sudo raspi-config")
    print("   → Interface Options → Camera → Enable")
    print()
    print("2. Reboot:")
    print("   sudo reboot")
    print()
    print("3. After reboot, check again:")
    print("   ls -l /dev/video*")
    print()
    print("4. Test camera:")
    print("   libcamera-still -o test.jpg")
else:
    print("✅ Camera device(s) found!")
    print("   If scanner still fails, try:")
    print("   1. Check if another process is using camera:")
    print("      lsof /dev/video0")
    print("   2. Test with libcamera:")
    print("      libcamera-still -o test.jpg")
    print("   3. Try different video index in camera config")

print("=" * 70)

