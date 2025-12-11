"""
Debug script to visualize the name crop region and test OCR.
"""
import cv2
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../')))
from dotenv import load_dotenv

from yahoo.mission.scanner.preprocess import preprocess_image
from yahoo.mission.scanner.name_detect import crop_name_region, online_ocr_openai, fuzzy_match_roster
from yahoo.mission.scanner.config import NAME_ROI_PCT, roi_pct_to_px, WARPED_WIDTH, WARPED_HEIGHT

load_dotenv()

def debug_name_crop(image_path):
    """Load image, preprocess, crop name region, and test OCR."""
    
    print(f"📄 Loading: {image_path}")
    img = cv2.imread(image_path)
    if img is None:
        print("❌ Failed to read image")
        return
    
    print(f"   Original size: {img.shape[1]}x{img.shape[0]}")
    
    # Preprocess
    print("\n🔄 Preprocessing...")
    warped_color, warped_gray, warped_thresh = preprocess_image(img)
    print(f"   Warped size: {warped_color.shape[1]}x{warped_color.shape[0]}")
    
    # Show ROI configuration
    print(f"\n📐 Name ROI Configuration:")
    print(f"   Percentage: {NAME_ROI_PCT}")
    x, y, w, h = roi_pct_to_px(NAME_ROI_PCT)
    print(f"   Pixel coords: x={x}, y={y}, w={w}, h={h}")
    print(f"   Expected warped size: {WARPED_WIDTH}x{WARPED_HEIGHT}")
    
    # Crop name region
    print(f"\n✂️  Cropping name region...")
    name_crop = crop_name_region(warped_color)
    print(f"   Crop size: {name_crop.shape[1]}x{name_crop.shape[0]}")
    
    # Save crop for inspection
    crop_path = "scans/name_crops/debug_crop.png"
    os.makedirs("scans/name_crops", exist_ok=True)
    cv2.imwrite(crop_path, name_crop)
    print(f"   Saved to: {crop_path}")
    
    # Draw ROI on warped image for visualization
    vis = warped_color.copy()
    cv2.rectangle(vis, (x, y), (x+w, y+h), (0, 255, 0), 3)
    vis_path = "scans/name_crops/debug_roi_visualization.png"
    cv2.imwrite(vis_path, vis)
    print(f"   ROI visualization: {vis_path}")
    
    # Test OCR if API key available
    api_key = os.getenv('OPENAI_API_KEY')
    if api_key:
        print(f"\n🔍 Testing OCR...")
        try:
            raw_ocr = online_ocr_openai(name_crop, api_key)
            print(f"   Raw OCR: '{raw_ocr}'")
            
            matched_name, confidence = fuzzy_match_roster(raw_ocr)
            print(f"   Matched: {matched_name}")
            print(f"   Confidence: {confidence:.1%}" if confidence else "   Confidence: None")
        except Exception as e:
            print(f"   ❌ OCR failed: {e}")
    else:
        print(f"\n⚠️  No API key - skipping OCR test")
    
    print(f"\n✅ Debug complete! Check the saved images.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 debug_name_crop.py <image_path>")
        sys.exit(1)
    
    debug_name_crop(sys.argv[1])

