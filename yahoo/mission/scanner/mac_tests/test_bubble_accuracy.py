"""
Test script for bubble detection accuracy validation.
Tests on known image and compares detected vs expected answers.
"""
import os
import sys
import cv2
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../')))
from dotenv import load_dotenv
from yahoo.mission.scanner.pipeline import process_test_image

load_dotenv()

def test_bubble_accuracy(image_path, expected_answers, api_key=None):
    """
    Test bubble detection accuracy on a known image.
    
    Args:
        image_path: Path to test image
        expected_answers: Dict of {question_num: expected_letter}
        api_key: Optional OpenAI API key for name detection
    """
    print(f"📄 Testing: {image_path}\n")
    
    img = cv2.imread(image_path)
    if img is None:
        print("❌ Failed to read image")
        return
    
    result = process_test_image(img, api_key=api_key)
    
    if not result["success"]:
        print(f"❌ Pipeline failed: {result['error']}")
        return
    
    print("="*60)
    print("📊 BUBBLE DETECTION ACCURACY REPORT")
    print("="*60)
    print(f"👤 Student: {result['student_name']}")
    print()
    
    answers = result["answers"]
    correct = 0
    total = len(expected_answers)
    
    print("📝 Question-by-Question Results:")
    print("-" * 60)
    for q in sorted(expected_answers.keys()):
        detected = answers.get(q)
        expected = expected_answers[q]
        
        detected_str = detected if detected else "(blank)"
        expected_str = expected if expected else "(blank)"
        
        if detected == expected:
            correct += 1
            status = "✅"
        else:
            status = "❌"
        
        # Get density info if available
        densities = result.get("densities", {})
        q_densities = densities.get(q, {})
        density_str = ""
        if q_densities:
            density_str = f" [A:{q_densities.get('A',0):.2f} B:{q_densities.get('B',0):.2f} C:{q_densities.get('C',0):.2f} D:{q_densities.get('D',0):.2f}]"
        
        print(f"Q{q:2d}: Detected={detected_str:4s} Expected={expected_str:4s} {status}{density_str}")
    
    print("-" * 60)
    accuracy = (correct / total * 100) if total > 0 else 0
    print(f"\n📈 Accuracy: {correct}/{total} ({accuracy:.1f}%)")
    
    # Also show score vs answer key
    grading = result.get("grading", {})
    if grading:
        score = grading.get("score", 0)
        total_q = grading.get("total_questions", 10)
        percentage = grading.get("percentage", 0)
        print(f"📊 Score vs Answer Key: {score}/{total_q} ({percentage}%)")
    
    print("="*60)
    print()
    
    return accuracy

if __name__ == "__main__":
    # Expected answers for IMG_7096.JPG (from image description)
    expected = {
        1: "A",
        2: "B",
        3: "C",
        4: "D",
        5: "A",
        6: "B",
        7: "B",
        8: "B",
        9: "A",
        10: "B"
    }
    
    image_path = "yahoo/mission/scanner/test_images/IMG_7096.JPG"
    
    if len(sys.argv) > 1:
        image_path = sys.argv[1]
    
    api_key = os.getenv('OPENAI_API_KEY')
    test_bubble_accuracy(image_path, expected, api_key=api_key)


