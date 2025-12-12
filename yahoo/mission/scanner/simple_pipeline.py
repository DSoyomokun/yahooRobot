# mission/scanner/simple_pipeline.py
"""
Simplified paper scanning pipeline:
1. Capture image from camera
2. Warp to standard size
3. Save image to disk
4. If WiFi: Detect student name using OpenAI Vision API
5. Save to database with student association
"""

import cv2
import os
import traceback
from datetime import datetime

try:
    from .image_warp import warp_form_to_standard
except ImportError:
    # Fallback to preprocess if image_warp doesn't exist
    from .preprocess import preprocess_image
    def warp_form_to_standard(img):
        warped, _, _ = preprocess_image(img)
        return warped
from .name_detect import detect_name
from .storage import (
    init_db,
    save_image,
    save_paper_scan
)


def check_wifi_connection():
    """
    Check if WiFi/internet connection is available.
    
    Returns:
        bool: True if connected, False otherwise
    """
    import socket
    try:
        # Try to connect to a reliable server
        socket.create_connection(("8.8.8.8", 53), timeout=3)
        return True
    except OSError:
        return False


def process_paper_scan(img_color, api_key=None, weight_grams=None):
    """
    Process a single paper scan: capture, warp, detect name (if WiFi), save to DB.
    
    Args:
        img_color: Raw BGR image from camera
        api_key: OpenAI API key (optional, will use from .env if not provided)
        weight_grams: Weight detected by sensor (optional)
    
    Returns:
        dict: {
            "success": True/False,
            "error": None or str,
            "image_path": path to saved image,
            "student_name": detected name or None,
            "ocr_raw": raw OCR text or None,
            "ocr_confidence": confidence score or None,
            "processed": True if name detected, False if offline
        }
    """
    try:
        init_db()  # Ensure DB & directories exist
        
        # -------------------------------------------
        # 1. Save raw image immediately
        # -------------------------------------------
        raw_path = save_image(img_color, "raw", "paper_scan")
        
        # -------------------------------------------
        # 2. Warp to standard size
        # -------------------------------------------
        try:
            warped_color = warp_form_to_standard(img_color)
            warped_path = save_image(warped_color, "warped", "warped")
        except Exception as e:
            # If warping fails, use original image
            print(f"⚠️  Warping failed: {e}. Using original image.")
            warped_color = img_color
            warped_path = raw_path
        
        # -------------------------------------------
        # 3. Check WiFi and detect name if available
        # -------------------------------------------
        student_name = None
        ocr_raw = None
        ocr_confidence = None
        processed = False
        
        has_wifi = check_wifi_connection()
        
        if has_wifi:
            # Load API key from environment if not provided
            if api_key is None:
                from dotenv import load_dotenv
                load_dotenv()
                import os
                api_key = os.getenv('OPENAI_API_KEY')
            
            if api_key:
                try:
                    print("🔍 Detecting student name...")
                    name_info = detect_name(warped_color, api_key)
                    student_name = name_info["matched_name"]
                    ocr_raw = name_info.get("raw_ocr")
                    ocr_confidence = name_info.get("confidence")
                    
                    if student_name and student_name != "UNKNOWN":
                        processed = True
                        print(f"✅ Student detected: {student_name} (confidence: {ocr_confidence:.1%})" if ocr_confidence else f"✅ Student detected: {student_name}")
                    else:
                        print("⚠️  Student name not detected")
                except Exception as e:
                    print(f"⚠️  Name detection failed: {e}")
            else:
                print("⚠️  No API key available")
        else:
            print("📴 No WiFi connection - saving image without name detection")
        
        # -------------------------------------------
        # 4. Save to database
        # -------------------------------------------
        row_id = save_paper_scan(
            image_path=raw_path,
            student_name=student_name,
            ocr_raw=ocr_raw,
            ocr_confidence=ocr_confidence,
            weight_grams=weight_grams
        )
        
        # -------------------------------------------
        # 5. Return result
        # -------------------------------------------
        return {
            "success": True,
            "error": None,
            "row_id": row_id,
            "image_path": raw_path,
            "warped_path": warped_path,
            "student_name": student_name,
            "ocr_raw": ocr_raw,
            "ocr_confidence": ocr_confidence,
            "processed": processed,
            "has_wifi": has_wifi
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"{e}\n{traceback.format_exc()}",
            "image_path": None,
            "student_name": None,
            "processed": False
        }
