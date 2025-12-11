"""
Test script to process all images in the test_images directory.
"""
import os
import sys
import cv2
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../')))
from yahoo.mission.scanner.pipeline import process_test_image

def test_all_images_in_directory(directory="yahoo/mission/scanner/test_images", api_key=None):
    """
    Process all images in the test_images directory.
    """
    test_dir = Path(directory)
    
    if not test_dir.exists():
        print(f"❌ Directory not found: {directory}")
        print(f"💡 Create the directory and add test images there")
        return
    
    image_files = list(test_dir.glob("*.png")) + list(test_dir.glob("*.jpg")) + list(test_dir.glob("*.jpeg"))
    
    if not image_files:
        print(f"❌ No images found in {directory}")
        print(f"💡 Add test form images (.png, .jpg, .jpeg) to this directory")
        return
    
    print(f"📁 Found {len(image_files)} image(s) in {directory}\n")
    
    for img_path in sorted(image_files):
        print(f"\n{'='*60}")
        print(f"📄 Processing: {img_path.name}")
        print(f"{'='*60}\n")
        
        img = cv2.imread(str(img_path))
        if img is None:
            print(f"❌ Failed to read image: {img_path}")
            continue
        
        result = process_test_image(img, api_key=api_key)
        
        if result["success"]:
            print(f"✅ Success!")
            print(f"   Student: {result['student_name']}")
            print(f"   Confidence: {result.get('name_confidence', 'N/A')}")
            print(f"   OCR Mode: {result.get('ocr_mode', 'N/A')}")
            print(f"   Answers: {result['answers']}")
            print(f"   Score: {result['grading']['score']}/{result['grading']['total_questions']} ({result['grading']['percentage']}%)")
            print(f"   Correct: {sum(1 for v in result['grading']['correct_per_q'].values() if v is True)}")
            print(f"   Incorrect: {sum(1 for v in result['grading']['correct_per_q'].values() if v is False)}")
            print(f"   Unanswered: {sum(1 for v in result['grading']['correct_per_q'].values() if v is None)}")
        else:
            print(f"❌ Failed: {result['error'][:200]}...")
    
    print(f"\n{'='*60}")
    print("✅ All images processed!")
    print(f"{'='*60}\n")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Test scanner on all images in test_images directory")
    parser.add_argument("--api-key", help="OpenAI API key for online OCR", default=None)
    parser.add_argument("--dir", help="Directory with test images", default="yahoo/mission/scanner/test_images")
    args = parser.parse_args()
    
    test_all_images_in_directory(args.dir, api_key=args.api_key)

