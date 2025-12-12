# mission/scanner/pipeline.py
"""
Full test-processing pipeline:
1. Receive raw image (from PiCam or Mac)
2. Preprocess → detect printed form → warp to 1700x2550 → threshold
3. Detect bubbles (A–D, Q1–Q10)
4. Detect student name (OCR online/offline)
5. Grade test
6. Save all artifacts (raw, warped, crop)
7. Insert full result into SQLite
8. Return structured dictionary for the robot or UI
"""

import cv2
import traceback
from datetime import datetime

from .preprocess import preprocess_image
from .bubble_detect import detect_bubbles
from .name_detect import detect_name, crop_name_region
from .grader import grade_test
from .storage import (
    init_db,
    save_image,
    store_result
)


# -----------------------------------------------------------
# MAIN ENTRYPOINT
# -----------------------------------------------------------
def process_test_image(img_color, api_key=None):
    """
    img_color: raw BGR image from PiCam or Mac webcam
    api_key: optional OpenAI API key for online OCR

    Returns structured results:
    {
        "success": True/False,
        "error": None or str,
        "student_name": "...",
        "name_confidence": float or None,
        "answers": {...},
        "densities": {...},
        "grading": {...},
        "paths": {
            "raw": "...",
            "warped": "...",
            "name_crop": "..."
        }
    }
    """

    try:
        init_db()  # ensure DB & directories exist

        # -------------------------------------------
        # 1. Save raw image immediately
        # -------------------------------------------
        raw_path = save_image(img_color, "raw", "raw")

        # -------------------------------------------
        # 2. Preprocess
        # -------------------------------------------
        warped_color, warped_gray, warped_thresh = preprocess_image(img_color)

        warped_path = save_image(warped_color, "warped", "warped")

        # -------------------------------------------
        # 3. Bubble detection (Improved traditional method)
        # -------------------------------------------
        from .bubble_detect import detect_bubbles_improved
        answers, densities = detect_bubbles_improved(warped_thresh, warped_gray)

        # -------------------------------------------
        # 4. Name detection (OCR + fuzzy match)
        # -------------------------------------------
        name_info = detect_name(warped_color, api_key)
        name_crop_path = name_info["crop_path"]

        student_name   = name_info["matched_name"]
        ocr_raw        = name_info["raw_ocr"]
        ocr_conf       = name_info["confidence"]
        ocr_mode       = name_info["mode"]
        needs_review   = name_info["needs_review"]

        # -------------------------------------------
        # 5. Grade the test
        # -------------------------------------------
        grading = grade_test(answers)

        # -------------------------------------------
        # 6. Store results in SQLite
        # -------------------------------------------
        store_result(
            student_name,
            ocr_raw,
            ocr_conf,
            ocr_mode,
            needs_review,
            answers,
            grading["correct_per_q"],
            grading["score"],
            grading["percentage"],
            raw_path,
            warped_path,
            name_crop_path
        )

        # -------------------------------------------
        # 7. Return structured result to robot/UI
        # -------------------------------------------
        return {
            "success": True,
            "error": None,
            "student_name": student_name,
            "name_confidence": ocr_conf,
            "ocr_mode": ocr_mode,
            "answers": answers,
            "densities": densities,
            "grading": grading,
            "paths": {
                "raw": raw_path,
                "warped": warped_path,
                "name_crop": name_crop_path
            }
        }

    except Exception as e:
        return {
            "success": False,
            "error": f"{e}\n{traceback.format_exc()}",
            "student_name": None,
            "answers": None,
            "grading": None
        }

