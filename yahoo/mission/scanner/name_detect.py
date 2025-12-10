# mission/scanner/name_detect.py
"""
Name detection subsystem:
- Extract name ROI from warped sheet (1700x2550)
- OCR via OpenAI Vision (if internet)
- Offline fallback: save crop + mark for later refinement
- Match OCR text against roster using fuzzy similarity
"""

import cv2
import numpy as np
import os
import time
import difflib
import json
from datetime import datetime

from .config import (
    NAME_ROI_PCT,
    CLASS_ROSTER,
    roi_pct_to_px,
    WARPED_WIDTH, WARPED_HEIGHT
)

# ---------------------------------------------------------
# 1. Crop name box
# ---------------------------------------------------------
def crop_name_region(warped_color):
    """
    Crop the student's name box using % ROI → pixel ROI.
    Returns high-quality color image for Vision API (gpt-4o works best with color).
    """
    x, y, w, h = roi_pct_to_px(NAME_ROI_PCT)
    crop = warped_color[y:y+h, x:x+w]
    
    # Vision API works best with color images, but we can enhance quality
    # Ensure minimum size for better OCR (Vision API handles scaling, but larger is better)
    min_width = 400
    if crop.shape[1] < min_width:
        scale = min_width / crop.shape[1]
        new_w = int(crop.shape[1] * scale)
        new_h = int(crop.shape[0] * scale)
        crop = cv2.resize(crop, (new_w, new_h), interpolation=cv2.INTER_CUBIC)
    
    # Light enhancement - preserve color for Vision API
    # Convert to LAB color space for better enhancement
    lab = cv2.cvtColor(crop, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    
    # Enhance lightness channel only
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    l_enhanced = clahe.apply(l)
    
    # Merge back
    lab_enhanced = cv2.merge([l_enhanced, a, b])
    enhanced = cv2.cvtColor(lab_enhanced, cv2.COLOR_LAB2BGR)
    
    return enhanced


# ---------------------------------------------------------
# 2. Try OpenAI OCR (ONLINE ONLY)
# ---------------------------------------------------------
def online_ocr_openai(image_bgr, api_key):
    """
    Sends name crop to OpenAI Vision API (gpt-4o) for OCR.
    Uses the same process ChatGPT uses: direct vision model text extraction.
    Returns raw OCR text on success.
    """
    import base64
    import requests

    # Encode image as high-quality PNG
    success, buffer = cv2.imencode(".png", image_bgr, [cv2.IMWRITE_PNG_COMPRESSION, 1])
    if not success:
        raise Exception("Failed to encode image as PNG")
    
    img_b64 = base64.b64encode(buffer).decode("utf-8")

    # Use gpt-4o (better vision model) for OCR
    endpoint = "https://api.openai.com/v1/chat/completions"

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    payload = {
        "model": "gpt-4o",  # Same model ChatGPT uses for vision
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{img_b64}",
                            "detail": "high"  # High detail for text recognition
                        }
                    },
                    {
                        "type": "text",
                        "text": "What text is written in this image? Return only the text you see, nothing else."
                    }
                ]
            }
        ],
        "max_tokens": 50,
        "temperature": 0.1  # Lower temperature for more consistent OCR
    }

    try:
        r = requests.post(endpoint, headers=headers, json=payload, timeout=15)
        r.raise_for_status()
        response = r.json()
        extracted = response["choices"][0]["message"]["content"].strip()
        
        # Remove any quotes or extra formatting
        extracted = extracted.strip('"').strip("'").strip()
        
        # Filter out common error messages
        error_phrases = ["unable", "cannot", "not visible", "no text", "i cannot", "i'm unable"]
        if any(phrase in extracted.lower() for phrase in error_phrases):
            raise Exception("OCR could not read the image")
        
        return extracted

    except Exception as e:
        raise Exception(f"OCR API failed → {e}")


def online_ocr_openai_full_image(warped_color, api_key):
    """
    Alternative approach: Send full warped image with region instructions.
    Similar to how ChatGPT can focus on specific regions in an image.
    """
    import base64
    import requests
    from .config import NAME_ROI_PCT, WARPED_WIDTH, WARPED_HEIGHT

    # Encode full image
    success, buffer = cv2.imencode(".png", warped_color, [cv2.IMWRITE_PNG_COMPRESSION, 1])
    if not success:
        raise Exception("Failed to encode image")
    
    img_b64 = base64.b64encode(buffer).decode("utf-8")

    # Calculate region coordinates for instructions
    x, y, w, h = roi_pct_to_px(NAME_ROI_PCT, WARPED_WIDTH, WARPED_HEIGHT)
    x_pct = int((x / WARPED_WIDTH) * 100)
    y_pct = int((y / WARPED_HEIGHT) * 100)
    w_pct = int((w / WARPED_WIDTH) * 100)
    h_pct = int((h / WARPED_HEIGHT) * 100)

    endpoint = "https://api.openai.com/v1/chat/completions"

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    payload = {
        "model": "gpt-4o",
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{img_b64}",
                            "detail": "high"
                        }
                    },
                    {
                        "type": "text",
                        "text": f"Look at the top portion of this test paper image, approximately {y_pct}% from the top, in a rectangular box that spans about {w_pct}% of the width. Extract the handwritten student name from that region. Return only the name text."
                    }
                ]
            }
        ],
        "max_tokens": 50,
        "temperature": 0.1
    }

    try:
        r = requests.post(endpoint, headers=headers, json=payload, timeout=15)
        r.raise_for_status()
        response = r.json()
        extracted = response["choices"][0]["message"]["content"].strip()
        extracted = extracted.strip('"').strip("'").strip()
        return extracted
    except Exception as e:
        raise Exception(f"Full image OCR failed → {e}")


# ---------------------------------------------------------
# 3. Roster matching (fuzzy + exact normalization)
# ---------------------------------------------------------
def fuzzy_match_roster(ocr_text):
    """
    Compare the OCR extracted name to class roster entries.
    Returns best match + similarity score.
    """
    if not ocr_text or len(ocr_text.strip()) == 0:
        return None, 0.0

    candidates = [name for (name, role) in CLASS_ROSTER]

    best_match = difflib.get_close_matches(ocr_text, candidates, n=1, cutoff=0.0)
    if not best_match:
        return None, 0.0

    best = best_match[0]
    score = difflib.SequenceMatcher(None, ocr_text, best).ratio()

    return best, float(score)


# ---------------------------------------------------------
# 4. Save name crop image for offline processing
# ---------------------------------------------------------
def save_offline_name_crop(image_bgr):
    """
    Save name crop so it can be OCR'd later.
    Returns stored_path.
    """
    save_dir = "scans/name_crops"
    os.makedirs(save_dir, exist_ok=True)

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = os.path.join(save_dir, f"name_{ts}.png")

    cv2.imwrite(path, image_bgr)

    return path


# ---------------------------------------------------------
# 5. MAIN — Detect name with hybrid online/offline logic
# ---------------------------------------------------------
def detect_name(warped_color, api_key=None):
    """
    Returns:
    {
        "matched_name": str or "UNKNOWN",
        "confidence": float or None,
        "raw_ocr": raw text or None,
        "mode": "online" or "offline",
        "needs_review": True/False,
        "crop_path": path to name crop image
    }
    """
    crop = crop_name_region(warped_color)

    # Save crop regardless (for storage + refinement)
    crop_path = save_offline_name_crop(crop)

    # Try ONLINE OCR if API key provided
    if api_key:
        try:
            # First try with the crop
            raw_ocr = online_ocr_openai(crop, api_key)
            
            # If crop fails, try with full image + region instructions (like ChatGPT)
            if "can't read" in raw_ocr.lower() or "cannot" in raw_ocr.lower() or "unreadable" in raw_ocr.lower():
                raw_ocr = online_ocr_openai_full_image(warped_color, api_key)
            
            matched_name, confidence = fuzzy_match_roster(raw_ocr)

            return {
                "matched_name": matched_name if matched_name else "UNKNOWN",
                "confidence": confidence if matched_name else None,
                "raw_ocr": raw_ocr,
                "mode": "online",
                "needs_review": False if matched_name else True,
                "crop_path": crop_path
            }
        except:
            pass  # fall through to offline mode

    # OFFLINE MODE
    return {
        "matched_name": "UNKNOWN",
        "confidence": None,
        "raw_ocr": None,
        "mode": "offline",
        "needs_review": True,
        "crop_path": crop_path
    }

