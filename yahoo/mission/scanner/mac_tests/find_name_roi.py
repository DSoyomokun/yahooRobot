"""
Interactive script to find the correct name ROI by testing different positions.
"""
import cv2
import sys
import os
import numpy as np
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../')))
from dotenv import load_dotenv

from yahoo.mission.scanner.preprocess import preprocess_image
from yahoo.mission.scanner.name_detect import online_ocr_openai, fuzzy_match_roster
from yahoo.mission.scanner.config import roi_pct_to_px, WARPED_WIDTH, WARPED_HEIGHT

load_dotenv()

def test_roi(warped_color, x_pct, y_pct, w_pct, h_pct):
    """Test a specific ROI and return OCR result."""
    x, y, w, h = roi_pct_to_px((x_pct, y_pct, w_pct, h_pct), WARPED_WIDTH, WARPED_HEIGHT)
    crop = warped_color[y:y+h, x:x+w]
    
    if crop.size == 0:
        return None, "Empty crop"
    
    # Enhance crop
    gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(gray)
    denoised = cv2.fastNlMeansDenoising(enhanced, None, 10, 7, 21)
    upscaled = cv2.resize(denoised, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
    enhanced_bgr = cv2.cvtColor(upscaled, cv2.COLOR_GRAY2BGR)
    
    # Check edge density
    edges = cv2.Canny(upscaled, 50, 150)
    edge_ratio = cv2.countNonZero(edges) / edges.size
    
    # Try OCR
    api_key = os.getenv('OPENAI_API_KEY')
    if api_key:
        try:
            raw_ocr = online_ocr_openai(enhanced_bgr, api_key)
            matched, conf = fuzzy_match_roster(raw_ocr)
            return {
                "edge_ratio": edge_ratio,
                "raw_ocr": raw_ocr,
                "matched": matched,
                "confidence": conf
            }, None
        except Exception as e:
            return {"edge_ratio": edge_ratio, "error": str(e)}, None
    
    return {"edge_ratio": edge_ratio}, None

def find_name_roi(image_path):
    """Try different ROI positions to find the name box."""
    
    print(f"📄 Loading: {image_path}")
    img = cv2.imread(image_path)
    if img is None:
        print("❌ Failed to read image")
        return
    
    print("🔄 Preprocessing...")
    warped_color, _, _ = preprocess_image(img)
    cv2.imwrite("scans/name_crops/test_warped.png", warped_color)
    print(f"   Warped size: {warped_color.shape[1]}x{warped_color.shape[0]}")
    
    # Test different Y positions (vertical)
    print("\n🔍 Testing different Y positions (keeping X=7.5%, W=85%, H=8%):")
    best_result = None
    best_y = None
    
    for y_pct in [0.08, 0.10, 0.12, 0.14, 0.16, 0.18, 0.20]:
        result, error = test_roi(warped_color, 0.075, y_pct, 0.85, 0.08)
        if error:
            print(f"   Y={y_pct:.1%}: {error}")
            continue
        
        edge = result.get("edge_ratio", 0)
        matched = result.get("matched", "N/A")
        conf = result.get("confidence", 0)
        ocr = result.get("raw_ocr", "N/A")[:30]
        
        print(f"   Y={y_pct:.1%}: edges={edge:.2%}, OCR='{ocr}', match={matched}, conf={conf:.1%}" if conf else f"   Y={y_pct:.1%}: edges={edge:.2%}, OCR='{ocr}', match={matched}")
        
        # Save crop for best result
        if edge > 0.01 and matched and matched != "UNKNOWN":
            if best_result is None or (conf and conf > best_result.get("confidence", 0)):
                best_result = result
                best_y = y_pct
                x, y, w, h = roi_pct_to_px((0.075, y_pct, 0.85, 0.08))
                crop = warped_color[y:y+h, x:x+w]
                cv2.imwrite("scans/name_crops/best_crop.png", crop)
    
    if best_result:
        print(f"\n✅ Best result at Y={best_y:.1%}")
        print(f"   Matched: {best_result.get('matched')}")
        print(f"   Confidence: {best_result.get('confidence', 0):.1%}")
        print(f"   Saved crop: scans/name_crops/best_crop.png")
    else:
        print("\n⚠️  No good match found. Check the warped image alignment.")
        print("   Saved warped image: scans/name_crops/test_warped.png")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 find_name_roi.py <image_path>")
        sys.exit(1)
    
    find_name_roi(sys.argv[1])


