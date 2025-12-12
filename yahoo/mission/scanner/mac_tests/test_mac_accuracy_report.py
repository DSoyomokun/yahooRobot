import os
import cv2
import sys
# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../')))
from yahoo.mission.scanner.pipeline import process_test_image

def evaluate_folder(folder, api_key=None):
    print(f"\n📁 Evaluating folder: {folder}")

    files = [f for f in os.listdir(folder) if f.lower().endswith((".png",".jpg",".jpeg"))]

    if not files:
        print("❌ No images found.")
        return

    bubble_correct = 0
    bubble_total = 0
    name_matched = 0
    name_total = 0

    for f in files:
        path = os.path.join(folder, f)
        img = cv2.imread(path)
        if img is None:
            continue

        print(f"\nProcessing {f}...")
        result = process_test_image(img, api_key=api_key)

        if not result["success"]:
            print("❌ Pipeline failed:", result["error"])
            continue

        # Bubble accuracy
        grading = result["grading"]
        cpq = grading["correct_per_q"]

        for q,v in cpq.items():
            if v is not None:
                bubble_total += 1
                if v:
                    bubble_correct += 1

        # Name accuracy
        if result["student_name"] != "UNKNOWN":
            name_total += 1
            if result["ocr_mode"] == "online":  # only evaluate OCR online
                name_matched += 1

    print("\n========== ACCURACY REPORT ==========")
    if bubble_total > 0:
        print(f"Bubble accuracy: {bubble_correct}/{bubble_total} "
              f"({round(bubble_correct/bubble_total*100,2)}%)")
    else:
        print("No bubble answers detected.")

    if name_total > 0:
        print(f"Name accuracy (online OCR): {name_matched}/{name_total} "
              f"({round(name_matched/name_total*100,2)}%)")
    else:
        print("No name OCR results available.")
    print("=====================================\n")


if __name__ == "__main__":
    evaluate_folder("scans/raw", api_key=None)
