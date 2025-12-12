"""
OFFLINE PAPER SCANNING SYSTEM (SIMPLIFIED)
GoPiGo robot only
LEDs: idle, processing, success, error
"""
import cv2
import sqlite3
import time
import datetime
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

#############################################
# AUTO-DETECT PLATFORM
#############################################
def is_raspberry_pi():
    """Detect if running on Raspberry Pi by checking /proc/cpuinfo."""
    try:
        with open('/proc/cpuinfo', 'r') as f:
            if 'Raspberry Pi' in f.read():
                return True
    except:
        pass
    return False

def check_gopigo_platform():
    """Verify we're running on GoPiGo/Raspberry Pi."""
    # Check if we're on Raspberry Pi
    if not is_raspberry_pi():
        return False
    
    # Verify picamera2 is available
    try:
        import picamera2
        return True
    except ImportError:
        return False

#############################################
# SETTINGS
#############################################
# This scanner is GoPiGo-only - exit if not on GoPiGo
if not check_gopigo_platform():
    print("❌ ERROR: This scanner requires GoPiGo robot with Raspberry Pi")
    print("💡 Make sure you're running on GoPiGo with:")
    print("   - Raspberry Pi OS")
    print("   - Camera enabled (sudo raspi-config)")
    print("   - picamera2 installed (pip3 install picamera2)")
    exit(1)

USE_GOPIGO = True  # Always true - we've verified we're on GoPiGo
SCAN_FOLDER = "scans"
DB_PATH = "scans.db"
BRIGHTNESS_THRESHOLD = int(os.getenv("BRIGHTNESS_THRESHOLD", "180"))  # Tune if paper is too dark/light

#############################################
# CREATE STORAGE FOLDER
#############################################
os.makedirs(SCAN_FOLDER, exist_ok=True)

#############################################
# INITIALIZE CAMERA
#############################################
# GoPiGo Camera (PiCamera2)
try:
    from picamera2 import Picamera2
    picam = Picamera2()
    picam.configure(picam.create_still_configuration())
    picam.start()
    
    def get_frame():
        return picam.capture_array()
    print("✅ GoPiGo camera (PiCamera2) initialized")
except Exception as e:
    print(f"❌ Failed to initialize PiCamera2: {e}")
    print("💡 Check camera is enabled: sudo raspi-config → Interface Options → Camera")
    print("💡 Install picamera2: pip3 install picamera2")
    exit(1)

#############################################
# INITIALIZE LEDs
#############################################
try:
    from easygopigo3 import EasyGoPiGo3
    gpg = EasyGoPiGo3()
    
    def led_idle():
        gpg.led_off("left")
        gpg.led_off("right")
    
    def led_processing():
        gpg.set_led(gpg.LED_LEFT, 255, 255, 0)   # Yellow
        gpg.set_led(gpg.LED_RIGHT, 255, 255, 0)
    
    def led_success():
        gpg.set_led(gpg.LED_LEFT, 0, 255, 0)     # Green
        gpg.set_led(gpg.LED_RIGHT, 0, 255, 0)
        time.sleep(1.3)
        led_idle()
    
    def led_error():
        gpg.set_led(gpg.LED_LEFT, 255, 0, 0)     # Red
        gpg.set_led(gpg.LED_RIGHT, 255, 0, 0)
        time.sleep(1.3)
        led_idle()
except ImportError:
    print("⚠️  easygopigo3 not available, LEDs disabled")
    def led_idle(): pass
    def led_processing(): pass
    def led_success(): pass
    def led_error(): pass
except Exception as e:
    print(f"⚠️  Failed to initialize LEDs: {e}")
    def led_idle(): pass
    def led_processing(): pass
    def led_success(): pass
    def led_error(): pass

#############################################
# PAPER DETECTION FUNCTION
#############################################
def paper_present(frame):
    """Detect if paper is present by checking brightness in center region."""
    if frame is None:
        return False
    
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    h, w = gray.shape
    
    # Middle area = best place to detect presence of a sheet
    roi = gray[h//4:3*h//4, w//4:3*w//4]
    brightness = roi.mean()
    
    return brightness > BRIGHTNESS_THRESHOLD

#############################################
# DATABASE INSERT FUNCTION
#############################################
def insert_scan(image_path):
    """Insert scan record into database."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute(
            "INSERT INTO scans (image_path, timestamp) VALUES (?, ?)",
            (image_path, ts)
        )
        conn.commit()
        conn.close()
        print(f"[DB] Logged {image_path} @ {ts}")
        return True
    except Exception as e:
        print(f"[DB ERROR] {e}")
        return False

#############################################
# MAIN LOOP
#############################################
def main():
    print("=" * 60)
    print("📄 GoPiGo Paper Scanner")
    print("=" * 60)
    print(f"Brightness threshold: {BRIGHTNESS_THRESHOLD}")
    print(f"Scan folder: {SCAN_FOLDER}")
    print("=" * 60)
    print("\n📄 System Ready — Waiting for paper...")
    print("Press Ctrl+C to quit\n")
    
    led_idle()
    
    try:
        while True:
            frame = get_frame()
            if frame is None:
                print("❌ Camera failure.")
                led_error()
                time.sleep(1)
                continue
            
            # Detect presence of paper sheet
            if paper_present(frame):
                print("\n📄 Paper detected → Processing...")
                led_processing()
                time.sleep(0.3)  # let the paper settle
                
                final = get_frame()
                if final is None:
                    print("❌ Could not capture final frame.")
                    led_error()
                    continue
                
                # Generate filename
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                img_path = f"{SCAN_FOLDER}/scan_{timestamp}.jpg"
                
                # Save image
                success = cv2.imwrite(img_path, final)
                if not success:
                    print("❌ Error saving image.")
                    led_error()
                    continue
                
                print(f"📸 Saved image: {img_path}")
                
                # Log to DB
                if insert_scan(img_path):
                    print("✅ Scan stored successfully.")
                    led_success()
                else:
                    print("❌ Failed to store scan in DB.")
                    led_error()
                
                # Prevent double-scanning
                time.sleep(1)
                led_idle()
            
            time.sleep(0.1)  # Small delay to avoid CPU spinning
    
    except KeyboardInterrupt:
        print("\n\n👋 Shutting down...")
    finally:
        led_idle()
        print("✅ Scanner stopped.")

if __name__ == "__main__":
    main()


