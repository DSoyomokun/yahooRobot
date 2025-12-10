import cv2
import sys
import os
# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../')))
from dotenv import load_dotenv
from yahoo.mission.scanner.pipeline import process_test_image

load_dotenv()

def run_pipeline_on_image(path, api_key=None):
    print(f"\n📄 Loading image: {path}")
    img = cv2.imread(path)

    if img is None:
        print("❌ Failed to read image.")
        return

    result = process_test_image(img, api_key=api_key)

    print("\n=========== SCAN RESULT ===========")
    print(result)
    print("=================================\n")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python test_mac_run.py /path/to/image.png")
        sys.exit()

    image_path = sys.argv[1]
    api_key = os.getenv('OPENAI_API_KEY')  # Load from .env
    run_pipeline_on_image(image_path, api_key=api_key)
