"""
Dynamic bubble location detection.
Finds all bubble positions in the form using circle detection instead of fixed coordinates.
"""
import cv2
import numpy as np
import logging
from typing import List, Tuple, Dict, Optional
from ..config.roi_config import NUM_QUESTIONS, NUM_CHOICES

logger = logging.getLogger(__name__)


def detect_all_bubbles(image: np.ndarray) -> List[Tuple[int, int, int]]:
    """
    Detect all bubbles in the form using multiple methods.
    
    Args:
        image: Aligned form image (BGR or grayscale)
        
    Returns:
        List of (center_x, center_y, radius) tuples for each detected bubble
    """
    # Convert to grayscale if needed
    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image.copy()
    
    h, w = gray.shape
    
    # Focus on question area (skip header)
    question_area = gray[int(h * 0.20):int(h * 0.95), int(w * 0.10):int(w * 0.90)]
    q_h, q_w = question_area.shape
    
    # Method 1: HoughCircles with multiple parameter sets
    detected_bubbles = []
    
    # Try different parameter combinations
    param_sets = [
        {"dp": 1, "minDist": int(q_w * 0.08), "param1": 50, "param2": 20, "minRadius": 15, "maxRadius": 50},
        {"dp": 1, "minDist": int(q_w * 0.06), "param1": 50, "param2": 15, "minRadius": 12, "maxRadius": 60},
    ]
    
    for params in param_sets:
        blurred = cv2.GaussianBlur(question_area, (5, 5), 0)
        circles = cv2.HoughCircles(blurred, cv2.HOUGH_GRADIENT, **params)
        
        if circles is not None:
            circles = np.round(circles[0, :]).astype("int")
            for (x, y, r) in circles:
                # Convert back to full image coordinates
                full_x = x + int(w * 0.10)
                full_y = y + int(h * 0.20)
                detected_bubbles.append((full_x, full_y, r))
    
    # Remove duplicates (bubbles detected by multiple methods)
    if detected_bubbles:
        # Group nearby bubbles
        unique_bubbles = []
        used = set()
        for i, (x1, y1, r1) in enumerate(detected_bubbles):
            if i in used:
                continue
            # Find all bubbles close to this one
            group = [(x1, y1, r1)]
            for j, (x2, y2, r2) in enumerate(detected_bubbles[i+1:], i+1):
                dist = np.sqrt((x1 - x2)**2 + (y1 - y2)**2)
                if dist < max(r1, r2) * 2:  # Overlapping or very close
                    group.append((x2, y2, r2))
                    used.add(j)
            
            # Use average of group
            avg_x = int(np.mean([b[0] for b in group]))
            avg_y = int(np.mean([b[1] for b in group]))
            avg_r = int(np.mean([b[2] for b in group]))
            unique_bubbles.append((avg_x, avg_y, avg_r))
        
        detected_bubbles = unique_bubbles
    
    # Method 2: Contour-based detection for non-perfect circles
    if len(detected_bubbles) < NUM_QUESTIONS * NUM_CHOICES * 0.5:  # Less than half detected
        # Use adaptive threshold to find dark circles
        adaptive = cv2.adaptiveThreshold(
            question_area, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY_INV, 11, 2
        )
        
        # Find contours
        contours, _ = cv2.findContours(adaptive, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        for contour in contours:
            area = cv2.contourArea(contour)
            if 200 < area < 5000:  # Reasonable bubble size
                # Check if roughly circular
                (cx, cy), radius = cv2.minEnclosingCircle(contour)
                circularity = 4 * np.pi * area / (cv2.arcLength(contour, True)**2) if cv2.arcLength(contour, True) > 0 else 0
                
                if circularity > 0.6:  # Roughly circular
                    # Convert to full image coordinates
                    full_x = int(cx) + int(w * 0.10)
                    full_y = int(cy) + int(h * 0.20)
                    full_r = int(radius)
                    
                    # Check if not already detected
                    is_duplicate = False
                    for bx, by, br in detected_bubbles:
                        dist = np.sqrt((full_x - bx)**2 + (full_y - by)**2)
                        if dist < max(full_r, br) * 1.5:
                            is_duplicate = True
                            break
                    
                    if not is_duplicate:
                        detected_bubbles.append((full_x, full_y, full_r))
    
    logger.info(f"Detected {len(detected_bubbles)} bubbles")
    return detected_bubbles


def group_bubbles_by_question(bubbles: List[Tuple[int, int, int]], 
                              image_width: int, 
                              image_height: int) -> Dict[int, List[Tuple[int, int, int, str]]]:
    """
    Group detected bubbles by question number.
    Assumes bubbles are arranged in rows (questions) and columns (choices A, B, C, D).
    
    Args:
        bubbles: List of (center_x, center_y, radius) tuples
        image_width: Width of the image
        image_height: Height of the image
        
    Returns:
        Dictionary mapping question number to list of (x, y, radius, choice_letter) tuples
    """
    if not bubbles:
        return {}
    
    # Sort bubbles by y-coordinate (top to bottom)
    sorted_bubbles = sorted(bubbles, key=lambda b: b[1])
    
    # Group bubbles that are roughly on the same horizontal line (same question)
    # Use a more sophisticated clustering approach
    question_groups = {}
    
    if not bubbles:
        return {}
    
    # Cluster bubbles by y-coordinate using a more adaptive approach
    # Calculate average spacing between bubbles to determine row tolerance
    y_coords = sorted([b[1] for b in bubbles])
    if len(y_coords) > 1:
        # Calculate median spacing between consecutive y-coordinates
        spacings = [y_coords[i+1] - y_coords[i] for i in range(len(y_coords)-1)]
        median_spacing = sorted(spacings)[len(spacings)//2] if spacings else image_height * 0.05
        y_tolerance = max(median_spacing * 0.4, image_height * 0.02)  # Adaptive tolerance
    else:
        y_tolerance = image_height * 0.03
    
    # Group bubbles into rows
    rows = []
    for bubble in sorted_bubbles:
        x, y, r = bubble
        assigned = False
        
        # Try to assign to existing row
        for row in rows:
            row_y = row[0][1]  # y-coordinate of first bubble in row
            if abs(y - row_y) <= y_tolerance:
                row.append(bubble)
                assigned = True
                break
        
        # Create new row if not assigned
        if not assigned:
            rows.append([bubble])
    
    # Sort rows by y-coordinate and assign question numbers
    rows.sort(key=lambda row: row[0][1])
    
    for q_num, row in enumerate(rows[:NUM_QUESTIONS], 1):
        # Sort bubbles in row by x-coordinate
        row.sort(key=lambda b: b[0])
        question_groups[q_num] = row
    
    # Sort each question's bubbles by x-coordinate and assign choice letters
    for q_num, q_bubbles in question_groups.items():
        # q_bubbles is already sorted by x from the grouping step
        # But ensure it's sorted
        q_bubbles.sort(key=lambda b: b[0])  # Sort by x
        
        # Assign choice letters (A, B, C, D)
        # Take up to NUM_CHOICES bubbles (should be exactly 4, but handle edge cases)
        labeled_bubbles = []
        for idx, bubble in enumerate(q_bubbles[:NUM_CHOICES]):
            x, y, r = bubble
            choice_letter = ['A', 'B', 'C', 'D'][idx]
            labeled_bubbles.append((x, y, r, choice_letter))
        
        question_groups[q_num] = labeled_bubbles
    
    logger.info(f"Grouped bubbles into {len(question_groups)} questions")
    return question_groups


def detect_bubble_positions(image: np.ndarray) -> Optional[Dict[int, Dict[str, Tuple[int, int, int]]]]:
    """
    Detect and organize all bubble positions in the form.
    
    Args:
        image: Aligned form image (BGR or grayscale)
        
    Returns:
        Dictionary mapping question number to choice letter to (x, y, radius)
        Format: {1: {'A': (x, y, r), 'B': (x, y, r), ...}, ...}
        Returns None if detection fails
    """
    # Detect all bubbles
    bubbles = detect_all_bubbles(image)
    
    if not bubbles:
        raise ValueError("No bubbles detected - dynamic detection required. Ensure bubbles are visible and clearly marked on the form.")
    
    # Group by question
    h, w = image.shape[:2]
    grouped = group_bubbles_by_question(bubbles, w, h)
    
    if len(grouped) < NUM_QUESTIONS * 0.5:  # Less than 50% of questions detected
        logger.error(f"Only detected {len(grouped)} questions, need at least {int(NUM_QUESTIONS * 0.5)}")
        raise ValueError(f"Insufficient bubble detection: only {len(grouped)}/{NUM_QUESTIONS} questions detected. Ensure all bubbles are clearly visible.")
    
    # Convert to expected format
    result = {}
    for q_num in range(1, NUM_QUESTIONS + 1):
        if q_num in grouped:
            result[q_num] = {}
            for x, y, r, choice_letter in grouped[q_num]:
                result[q_num][choice_letter] = (x, y, r)
        else:
            # Missing question - will need to use fixed coordinates or skip
            logger.warning(f"Question {q_num} not detected")
    
    return result

