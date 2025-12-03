#!/usr/bin/env python3
"""
Detailed image analysis - see exactly what the scanner detects.
"""
import cv2
import sys
from pathlib import Path
import numpy as np

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent))

from yahoo.mission.scanner.bubble_detector import BubbleDetector
from yahoo.mission.scanner.name_reader import NameReader

def analyze_image(image_path: str):
    """Analyze image in detail."""
    print(f"\n🔍 ANALYZING: {image_path}")
    print("="*60)
    
    # Load image
    image = cv2.imread(image_path)
    if image is None:
        print(f"❌ Failed to load: {image_path}")
        return
    
    h, w = image.shape[:2]
    print(f"📐 Image size: {w}x{h} pixels")
    
    # 1. Analyze name region
    print(f"\n📝 NAME REGION ANALYSIS")
    print("-"*60)
    reader = NameReader()
    
    # Show name region coordinates
    name_top = int(h * 0.05)
    name_bottom = int(h * 0.15)
    name_left = int(w * 0.10)
    name_right = int(w * 0.50)
    
    print(f"Name region coordinates:")
    print(f"  Top: {name_top} ({name_top/h*100:.1f}% of height)")
    print(f"  Bottom: {name_bottom} ({name_bottom/h*100:.1f}% of height)")
    print(f"  Left: {name_left} ({name_left/w*100:.1f}% of width)")
    print(f"  Right: {name_right} ({name_right/w*100:.1f}% of width)")
    print(f"  Size: {name_right-name_left}x{name_bottom-name_top}")
    
    # Extract and show name region
    name_region = reader.extract_name_region(image)
    name = reader.extract_name(image)
    
    print(f"\nExtracted name: {name}")
    
    # Save name region
    output_dir = Path(__file__).parent / "analysis_output"
    output_dir.mkdir(exist_ok=True)
    cv2.imwrite(str(output_dir / "name_region.jpg"), name_region)
    print(f"✅ Name region saved to: {output_dir}/name_region.jpg")
    
    # 2. Analyze bubbles
    print(f"\n⭕ BUBBLE DETECTION ANALYSIS")
    print("-"*60)
    detector = BubbleDetector()
    
    # Preprocess
    processed = detector.preprocess(image)
    bubbles = detector.detect_bubbles(processed)
    
    print(f"Total bubbles detected: {len(bubbles)}")
    print(f"\nBubble detection settings:")
    print(f"  Min area: {detector.min_area}")
    print(f"  Max area: {detector.max_area}")
    print(f"  Fill threshold: {detector.fill_threshold}")
    print(f"  Circularity threshold: {detector.circularity_threshold}")
    
    # Analyze each bubble
    if bubbles:
        print(f"\nDetected bubbles:")
        gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
        
        for i, bubble in enumerate(bubbles[:20], 1):  # Show first 20
            x, y, w, h = bubble['bounding_rect']
            cx, cy = bubble['center']
            area = bubble['area']
            fill = detector.calculate_fill(gray_image, bubble)
            is_marked = fill >= detector.fill_threshold
            
            print(f"  Bubble {i}:")
            print(f"    Center: ({cx}, {cy})")
            print(f"    Size: {w}x{h}, Area: {area:.0f}")
            print(f"    Fill: {fill:.2%} {'✅ MARKED' if is_marked else '❌ empty'}")
    
    # Group by question
    question_groups = detector.group_by_question(bubbles, num_choices=4)
    print(f"\n📋 GROUPED BY QUESTIONS:")
    print(f"  Questions found: {len(question_groups)}")
    
    for q_num, q_bubbles in sorted(question_groups.items())[:10]:  # Show first 10
        print(f"  Question {q_num}: {len(q_bubbles)} bubbles")
        for j, bubble in enumerate(q_bubbles[:4]):
            fill = detector.calculate_fill(gray_image, bubble)
            letter = chr(ord('A') + j)
            marked = "✅" if fill >= detector.fill_threshold else "⭕"
            print(f"    {letter}: {fill:.2%} {marked}")
    
    # Extract answers
    answers = detector.extract_answers(image)
    print(f"\n📝 EXTRACTED ANSWERS:")
    print(f"  {answers}")
    
    # 3. Create visualization
    print(f"\n🎨 CREATING VISUALIZATION...")
    vis_image = image.copy()
    
    # Draw name region
    cv2.rectangle(vis_image, (name_left, name_top), (name_right, name_bottom), (0, 255, 0), 3)
    cv2.putText(vis_image, "NAME REGION", (name_left, name_top - 10), 
                cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 0), 2)
    
    # Draw bubbles
    for i, bubble in enumerate(bubbles[:50]):  # Limit to 50
        x, y, w, h = bubble['bounding_rect']
        cx, cy = bubble['center']
        fill = detector.calculate_fill(gray_image, bubble)
        
        # Color based on fill
        color = (0, 255, 0) if fill >= detector.fill_threshold else (0, 0, 255)
        cv2.rectangle(vis_image, (x, y), (x+w, y+h), color, 2)
        cv2.circle(vis_image, (cx, cy), 5, color, -1)
        cv2.putText(vis_image, f"{fill:.0%}", (x, y-5), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.4, color, 1)
    
    # Save visualization
    vis_path = output_dir / "analysis_visualization.jpg"
    cv2.imwrite(str(vis_path), vis_image)
    print(f"✅ Visualization saved to: {vis_path}")
    
    # 4. Summary
    print(f"\n📊 SUMMARY")
    print("-"*60)
    print(f"Name extracted: {name[:50]}..." if name and len(name) > 50 else f"Name extracted: {name}")
    print(f"Bubbles detected: {len(bubbles)}")
    print(f"Questions found: {len(question_groups)}")
    print(f"Answers extracted: {len(answers)}")
    print(f"\n💡 Check {output_dir}/ for detailed images")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('image', nargs='?', default='robot_scanner/tests/test_capture.jpg',
                       help='Image to analyze')
    
    args = parser.parse_args()
    analyze_image(args.image)

