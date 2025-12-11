# mission/scanner/bubble_detect_vision.py
"""
Vision API-based bubble detection using gpt-4o (same as ChatGPT).
Sends bubble regions to Vision API to identify which bubble is filled.
"""

import cv2
import base64
import requests
import numpy as np
from .config import (
    WARPED_WIDTH, WARPED_HEIGHT,
    BUBBLE_ROIS_PCT,
    roi_pct_to_px
)


def detect_bubble_with_vision(warped_color, question_num, api_key):
    """
    Detect which bubble (A, B, C, or D) is filled using Vision API with full image.
    Similar to name detection - sends full warped image with region instructions.
    
    Args:
        warped_color: Full warped color image (1700x2550)
        question_num: Question number (1-10)
        api_key: OpenAI API key
    
    Returns:
        str: "A", "B", "C", "D", or None if no bubble is filled
    """
    # Calculate approximate position of question bubbles
    bubble_rois = BUBBLE_ROIS_PCT[question_num]
    
    # Get position info for instructions
    x_a, y_a, w_a, h_a = roi_pct_to_px(bubble_rois["A"])
    x_d, y_d, w_d, h_d = roi_pct_to_px(bubble_rois["D"])
    
    # Calculate percentages for instructions
    y_pct = int((y_a / WARPED_HEIGHT) * 100)
    x_a_pct = int((x_a / WARPED_WIDTH) * 100)
    x_d_pct = int(((x_d + w_d) / WARPED_WIDTH) * 100)
    
    # Encode full image
    success, buffer = cv2.imencode(".png", warped_color, [cv2.IMWRITE_PNG_COMPRESSION, 1])
    if not success:
        return None
    
    img_b64 = base64.b64encode(buffer).decode("utf-8")
    
    # Call Vision API with full image
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
                        "text": f"This is a multiple-choice test paper. Find question number {question_num}. It has 4 circular bubbles arranged horizontally: bubble A (leftmost), bubble B, bubble C, and bubble D (rightmost). Look carefully at all 4 bubbles for question {question_num}. Which bubble contains dark pencil marks, shading, or ink inside the circle? The filled bubble will appear darker than the empty ones. Respond with only the single letter: A, B, C, or D."
                    }
                ]
            }
        ],
        "max_tokens": 10,
        "temperature": 0.0
    }
    
    try:
        r = requests.post(endpoint, headers=headers, json=payload, timeout=15)
        r.raise_for_status()
        response = r.json()
        extracted = response["choices"][0]["message"]["content"].strip().upper()
        
        # Clean up response
        extracted = extracted.strip('"').strip("'").strip(".").strip()
        
        # Extract letter if present
        for letter in ["A", "B", "C", "D"]:
            if letter == extracted or letter in extracted.split():
                return letter
        
        if "NONE" in extracted:
            return None
        
        return None
        
    except Exception as e:
        return None


def detect_bubbles_vision(warped_color, api_key):
    """
    Detect all bubble answers using Vision API with full image.
    Calls Vision API once per question (like name detection approach).
    
    Args:
        warped_color: Full warped color image
        api_key: OpenAI API key
    
    Returns:
        answers: {1:"A", 2:"B", ..., 10:"C"}
        densities: {} (empty for vision method, kept for compatibility)
    """
    answers = {}
    densities = {}
    
    # Call Vision API for each question individually (more reliable)
    for q in range(1, 11):
        try:
            answer = detect_bubble_with_vision(warped_color, q, api_key)
            answers[q] = answer
            densities[q] = {}
        except Exception as e:
            answers[q] = None
            densities[q] = {}
    
    return answers, densities


def detect_bubbles_hybrid(warped_color, warped_thresh, api_key=None):
    """
    Hybrid approach: Try Vision API first, fallback to traditional method.
    
    Args:
        warped_color: Full warped color image
        warped_thresh: Thresholded image for traditional method
        api_key: OpenAI API key (optional)
    
    Returns:
        answers: {1:"A", 2:"B", ..., 10:"C"}
        densities: Debugging dictionary
    """
    # If API key provided, use Vision API
    if api_key:
        try:
            answers, densities = detect_bubbles_vision(warped_color, api_key)
            return answers, densities
        except Exception as e:
            # Fallback to traditional if Vision API fails
            pass
    
    # Fallback to traditional method
    from .bubble_detect import detect_bubbles
    return detect_bubbles(warped_thresh)

