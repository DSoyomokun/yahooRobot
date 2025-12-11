# mission/scanner/bubble_detect.py
"""
Fixed ROI–based bubble detection for 10 questions (A–D options).
Uses percentage-based ROIs converted to pixel coordinates
AFTER perspective correction + normalization.

Improved with circular mask detection and relative comparison.
"""

import cv2
import numpy as np
from .config import (
    WARPED_WIDTH, WARPED_HEIGHT,
    BUBBLE_ROIS_PCT,
    roi_pct_to_px
)

# -------------------------------------------------------------
# Utility: compute fill density inside a bubble ROI (circular mask)
# -------------------------------------------------------------
def compute_fill_density_circular(thresh_img, roi):
    """
    Count how many 'ink/dark' pixels exist inside the bubble using circular mask.
    thresh_img: 1700x2550 thresholded warped sheet (binary INV)
    roi: (x,y,w,h)
    """
    x, y, w, h = roi
    
    if w <= 0 or h <= 0:
        return 0
    
    bubble_region = thresh_img[y:y+h, x:x+w]
    
    if bubble_region.size == 0:
        return 0
    
    # Create circular mask
    center_x, center_y = w // 2, h // 2
    radius = min(w, h) // 2 - 2  # Slightly smaller to avoid edge pixels
    
    mask = np.zeros((h, w), dtype=np.uint8)
    cv2.circle(mask, (center_x, center_y), radius, 255, -1)
    
    # Apply mask to bubble region
    masked = cv2.bitwise_and(bubble_region, bubble_region, mask=mask)
    
    # Count white pixels (filled) within circle
    filled_pixels = cv2.countNonZero(masked)
    total_circle_pixels = cv2.countNonZero(mask)
    
    if total_circle_pixels == 0:
        return 0
    
    return filled_pixels / total_circle_pixels  # ratio from 0 to 1


def compute_mean_brightness_circular(gray_img, roi):
    """
    Compute mean brightness of pixels inside circular bubble.
    Lower brightness = darker = more likely filled.
    gray_img: Grayscale image
    roi: (x,y,w,h)
    """
    x, y, w, h = roi
    
    if w <= 0 or h <= 0:
        return 255.0
    
    bubble_region = gray_img[y:y+h, x:x+w]
    
    if bubble_region.size == 0:
        return 255.0
    
    # Create circular mask
    center_x, center_y = w // 2, h // 2
    radius = min(w, h) // 2 - 2
    
    mask = np.zeros((h, w), dtype=np.uint8)
    cv2.circle(mask, (center_x, center_y), radius, 255, -1)
    
    # Get pixels within circle
    masked_region = cv2.bitwise_and(bubble_region, bubble_region, mask=mask)
    
    # Calculate mean brightness of non-zero pixels
    mean_brightness = cv2.mean(bubble_region, mask=mask)[0]
    
    return mean_brightness


# Legacy function for backward compatibility
def compute_fill_density(thresh_img, roi):
    """Legacy function - use compute_fill_density_circular instead."""
    return compute_fill_density_circular(thresh_img, roi)


# -------------------------------------------------------------
# Detect answers for all 10 questions, each with A–D (IMPROVED)
# -------------------------------------------------------------
def detect_bubbles_improved(warped_thresh, warped_gray):
    """
    Improved bubble detection with circular masks and relative comparison.
    Given thresholded and grayscale warped sheet, evaluate all bubble ROIs.
    Returns:
        answers = {1:"A", 2:"B", ..., 10:"C"}
        densities = debugging dictionary of raw fill ratios
    """
    answers = {}
    densities = {}

    for q in range(1, 11):
        q_densities = {}
        q_brightnesses = {}
        bubble_rois = BUBBLE_ROIS_PCT[q]

        # Evaluate A,B,C,D with both density and brightness
        for letter in ["A", "B", "C", "D"]:
            pct_roi = bubble_rois[letter]
            abs_roi = roi_pct_to_px(pct_roi)
            
            # Get fill density (from thresholded image)
            density = compute_fill_density_circular(warped_thresh, abs_roi)
            q_densities[letter] = density
            
            # Get mean brightness (from grayscale image)
            brightness = compute_mean_brightness_circular(warped_gray, abs_roi)
            q_brightnesses[letter] = brightness

        # Calculate combined scores
        # Higher density + lower brightness = more likely filled
        scores = {}
        for letter in ["A", "B", "C", "D"]:
            # Normalize brightness (0-1, where 0 = darkest, 1 = brightest)
            brightness_norm = 1.0 - (q_brightnesses[letter] / 255.0)
            
            # Combine density (80%) and brightness (20%) - density is primary
            combined_score = (q_densities[letter] * 0.8) + (brightness_norm * 0.2)
            scores[letter] = combined_score

        # Use a combination of density and brightness with strict relative comparison
        # Sort bubbles by combined score
        sorted_bubbles = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        best_letter, best_score = sorted_bubbles[0]
        second_letter, second_score = sorted_bubbles[1] if len(sorted_bubbles) > 1 else (None, 0)
        
        best_density = q_densities[best_letter]
        best_brightness = q_brightnesses[best_letter]
        
        # Calculate how much better the best is than the second best
        score_margin = best_score - second_score if second_score > 0 else best_score
        
        # Also check density and brightness margins
        other_densities = [q_densities[l] for l in ["A", "B", "C", "D"] if l != best_letter]
        max_other_density = max(other_densities) if other_densities else 0
        density_margin = best_density - max_other_density
        
        other_brightnesses = [q_brightnesses[l] for l in ["A", "B", "C", "D"] if l != best_letter]
        min_other_brightness = min(other_brightnesses) if other_brightnesses else 255
        brightness_margin = min_other_brightness - best_brightness  # Best should be darker (lower)
        
        # Simple approach: use the bubble with highest density
        # But validate it's reasonable compared to others
        best_letter = max(q_densities, key=q_densities.get)
        best_density = q_densities[best_letter]
        
        # Get other densities
        other_densities = [q_densities[l] for l in ["A", "B", "C", "D"] if l != best_letter]
        max_other_density = max(other_densities) if other_densities else 0
        second_best_density = sorted(q_densities.values(), reverse=True)[1] if len(q_densities) > 1 else 0
        
        # Use best if:
        # 1. Density is clearly highest (at least 0.01 more than second), OR
        # 2. Density is above 0.10 (clearly filled)
        density_margin = best_density - second_best_density
        
        if density_margin > 0.01 or best_density > 0.10:
            answers[q] = best_letter
        elif best_density > 0.05:  # Lower threshold for very light marks
            answers[q] = best_letter
        else:
            answers[q] = None  # Too low, probably blank

        densities[q] = q_densities

    return answers, densities


# Legacy function for backward compatibility
def detect_bubbles(warped_thresh):
    """
    Legacy function - converts to grayscale and calls improved version.
    """
    # Create grayscale from thresholded (approximation)
    warped_gray = cv2.cvtColor(
        cv2.cvtColor(warped_thresh, cv2.COLOR_GRAY2BGR),
        cv2.COLOR_BGR2GRAY
    )
    # Invert to get proper grayscale
    warped_gray = 255 - warped_gray
    return detect_bubbles_improved(warped_thresh, warped_gray)

