"""
OFFLINE PAPER SCANNING SYSTEM (SIMPLIFIED)
GoPiGo + Mac compatible
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

def auto_detect_gopigo():
    """Auto-detect if we should use GoPiGo mode."""
    # First check environment variable (manual override)
    env_value = os.getenv("USE_GOPIGO", "").lower()
    if env_value == "true":
        return True
    if env_value == "false":
        return False
    
    # Auto-detect: Try to import picamera2 (only available on Pi)
    try:
        import picamera2
        # If we can import it, we're likely on a Pi
        return True
    except ImportError:
        pass
    
    # Fallback: Check if we're on Raspberry Pi
    return is_raspberry_pi()

#############################################
# SETTINGS
#############################################
USE_GOPIGO = auto_detect_gopigo()  # Auto-detect or use .env override
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
if USE_GOPIGO:
    # ----------------------
    # GoPiGo Camera (PiCamera2)
    # ----------------------
    try:
        from picamera2 import Picamera2
        picam = Picamera2()
        picam.configure(picam.create_still_configuration())
        picam.start()
        
        def get_frame():
            return picam.capture_array()
        print("✅ GoPiGo camera (PiCamera2) initialized")
    except ImportError:
        print("⚠️  picamera2 not available, falling back to OpenCV")
        print("💡 Install with: pip3 install picamera2")
        USE_GOPIGO = False
        cam = cv2.VideoCapture(0)
        def get_frame():
            ret, frame = cam.read()
            return frame if ret else None
    except Exception as e:
        print(f"❌ Failed to initialize PiCamera2: {e}")
        print("💡 Check camera is enabled: sudo raspi-config → Interface Options → Camera")
        print("💡 Falling back to OpenCV...")
        USE_GOPIGO = False
        cam = cv2.VideoCapture(0)
        def get_frame():
            ret, frame = cam.read()
            return frame if ret else None
else:
    # ----------------------
    # Mac / Windows Webcam Testing
    # ----------------------
    cam = cv2.VideoCapture(0)
    if not cam.isOpened():
        print("❌ Failed to open camera")
        exit(1)
    
    def get_frame():
        ret, frame = cam.read()
        return frame if ret else None

#############################################
# INITIALIZE LEDs (GoPiGo ONLY)
#############################################
if USE_GOPIGO:
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
else:
    # On Mac: LEDs do nothing
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
    print("📄 Simplified Paper Scanner")
    print("=" * 60)
    print(f"Mode: {'GoPiGo' if USE_GOPIGO else 'Mac/Windows'}")
    print(f"Brightness threshold: {BRIGHTNESS_THRESHOLD}")
    print(f"Scan folder: {SCAN_FOLDER}")
    
    # Show detection status
    if USE_GOPIGO:
        print("✅ Auto-detected: GoPiGo mode")
    else:
        print("✅ Auto-detected: Mac/Windows mode")
        env_override = os.getenv("USE_GOPIGO", "")
        if env_override:
            print(f"   (USE_GOPIGO={env_override} from .env)")
    
    print("=" * 60)
    print("\n📄 System Ready — Waiting for paper...")
    print("Press 'q' to quit (Mac/Windows only)\n")
    
    led_idle()
    
    try:
        while True:
            frame = get_frame()
            if frame is None:
                print("❌ Camera failure.")
                led_error()
                time.sleep(1)
                continue
            
            # Preview window only for Mac testing
            if not USE_GOPIGO:
                cv2.imshow("Scanner Preview", frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    print("\n👋 Shutting down...")
                    break
            
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
        if not USE_GOPIGO:
            cam.release()
            cv2.destroyAllWindows()
        led_idle()
        print("✅ Scanner stopped.")

if __name__ == "__main__":
    main()


