"""
ROI (Region of Interest) extraction module.
Extracts name and bubble regions from aligned form using dynamic detection.
"""
import cv2
import numpy as np
import logging
from typing import Tuple, Optional
from ..config.roi_config import NUM_QUESTIONS, NUM_CHOICES
from .name_box_detector import detect_name_box, detect_name_box_alternative

logger = logging.getLogger(__name__)


def extract_name_roi(aligned_image: np.ndarray) -> np.ndarray:
    """
    Extract name region from aligned form using dynamic detection only.
    
    Args:
        aligned_image: Aligned form image
        
    Returns:
        Cropped name region image
        
    Raises:
        ValueError: If name box cannot be detected
    """
    h, w = aligned_image.shape[:2]
    
    # Try dynamic detection
    name_box = detect_name_box(aligned_image)
    if name_box is None:
        # Try alternative method
        name_box = detect_name_box_alternative(aligned_image)
    
    if name_box:
        top, bottom, left, right = name_box
        logger.info(f"✅ Dynamically detected name box: top={top}, bottom={bottom}, left={left}, right={right}")
    else:
        raise ValueError("Failed to detect name box - dynamic detection required")
    
    # Add small padding to ensure we capture the full name
    padding = 5
    top = max(0, top - padding)
    bottom = min(h, bottom + padding)
    left = max(0, left - padding)
    right = min(w, right + padding)
    
    name_roi = aligned_image[top:bottom, left:right]
    return name_roi


def extract_bubble_roi(aligned_image: np.ndarray, 
                       question_num: int, 
                       choice_index: int,
                       bubble_positions: dict) -> np.ndarray:
    """
    Extract a specific bubble ROI from aligned form using dynamic detection only.
    
    Args:
        aligned_image: Aligned form image
        question_num: Question number (1-indexed)
        choice_index: Choice index (0=A, 1=B, 2=C, 3=D)
        bubble_positions: Dict from detect_bubble_positions() for dynamic detection (required)
        
    Returns:
        Cropped bubble region image
        
    Raises:
        ValueError: If bubble position not found in bubble_positions
    """
    h, w = aligned_image.shape[:2]
    
    # Use dynamic detection (required)
    choice_letter = ['A', 'B', 'C', 'D'][choice_index]
    
    if question_num not in bubble_positions:
        raise ValueError(f"Question {question_num} not found in detected bubble positions. Dynamic detection failed.")
    
    if choice_letter not in bubble_positions[question_num]:
        # Missing bubble - return empty ROI (will be handled gracefully)
        logger.warning(f"Choice {choice_letter} for question {question_num} not found, using placeholder")
        # Return a small empty ROI
        h, w = aligned_image.shape[:2]
        empty_roi = np.zeros((10, 10, 3) if len(aligned_image.shape) == 3 else (10, 10), dtype=aligned_image.dtype)
        return empty_roi
    
    center_x, center_y, radius = bubble_positions[question_num][choice_letter]
    
    # Extract square region around bubble
    top = max(0, center_y - radius - 2)
    bottom = min(h, center_y + radius + 2)
    left = max(0, center_x - radius - 2)
    right = min(w, center_x + radius + 2)
    
    bubble_roi = aligned_image[top:bottom, left:right]
    return bubble_roi


def extract_all_bubbles(aligned_image: np.ndarray, bubble_positions: dict) -> dict:
    """
    Extract all bubble ROIs from aligned form using dynamic detection only.
    
    Args:
        aligned_image: Aligned form image
        bubble_positions: Dict from detect_bubble_positions() for dynamic detection (required)
        
    Returns:
        Dictionary mapping (question_num, choice_letter) to bubble ROI
        Format: {(1, 'A'): roi_array, (1, 'B'): roi_array, ...}
        
    Raises:
        ValueError: If bubble_positions is missing required questions/choices
    """
    bubbles = {}
    
    for q_num in range(1, NUM_QUESTIONS + 1):
        for choice_idx, choice_letter in enumerate(['A', 'B', 'C', 'D']):
            bubble_roi = extract_bubble_roi(aligned_image, q_num, choice_idx, bubble_positions)
            bubbles[(q_num, choice_letter)] = bubble_roi
    
    return bubbles


def extract_rois(aligned_image: np.ndarray) -> Tuple[np.ndarray, dict, dict]:
    """
    Extract both name ROI and all bubble ROIs using dynamic detection only.
    
    Args:
        aligned_image: Aligned form image
        
    Returns:
        Tuple of (name_roi, bubbles_dict, bubble_positions)
        bubbles_dict maps (question_num, choice_letter) to bubble ROI
        bubble_positions is the detected bubble positions dict (for use in bubble detection)
        
    Raises:
        ValueError: If name box or bubble positions cannot be detected
    """
    # Extract name ROI (dynamic detection only)
    name_roi = extract_name_roi(aligned_image)
    
    # Detect bubble positions (dynamic detection only)
    from ..bubbles.bubble_locator import detect_bubble_positions
    bubble_positions = detect_bubble_positions(aligned_image)
    
    if not bubble_positions:
        raise ValueError("Failed to detect bubble positions - dynamic detection required")
    
    logger.info(f"✅ Using dynamically detected bubble positions ({len(bubble_positions)} questions)")
    
    # Extract all bubble ROIs using detected positions
    bubbles = extract_all_bubbles(aligned_image, bubble_positions)
    
    return name_roi, bubbles, bubble_positions

