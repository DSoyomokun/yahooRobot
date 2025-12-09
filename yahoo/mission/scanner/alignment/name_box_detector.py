"""
Dynamic name box detection using contour analysis.
Finds the rectangular name field on the form instead of using fixed coordinates.
"""
import cv2
import numpy as np
import logging
from typing import Optional, Tuple

logger = logging.getLogger(__name__)


def detect_name_box(image: np.ndarray) -> Optional[Tuple[int, int, int, int]]:
    """
    Detect the name box rectangle on the form using multiple detection methods.
    
    Args:
        image: Aligned form image (BGR or grayscale)
        
    Returns:
        Tuple of (top, bottom, left, right) coordinates, or None if not found
    """
    # Convert to grayscale if needed
    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image.copy()
    
    h, w = gray.shape
    
    # Focus on upper portion of form (name box is typically in top 35%)
    upper_region = gray[:int(h * 0.35), :]
    upper_h, upper_w = upper_region.shape
    
    # Method 1: Detect horizontal lines (top and bottom of name box)
    # Name boxes typically have horizontal lines above and below
    horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (int(upper_w * 0.3), 1))
    horizontal_lines = cv2.morphologyEx(upper_region, cv2.MORPH_OPEN, horizontal_kernel)
    
    # Find horizontal line positions using HoughLines
    edges = cv2.Canny(upper_region, 50, 150)
    lines = cv2.HoughLinesP(edges, 1, np.pi/180, threshold=int(upper_w * 0.2), 
                           minLineLength=int(upper_w * 0.2), maxLineGap=20)
    
    horizontal_line_y = []
    if lines is not None:
        for line in lines:
            x1, y1, x2, y2 = line[0]
            # Check if line is roughly horizontal
            if abs(y2 - y1) < 5 and abs(x2 - x1) > upper_w * 0.2:
                horizontal_line_y.append((y1 + y2) // 2)
    
    # If we found horizontal lines, use them to find the box
    if len(horizontal_line_y) >= 2:
        horizontal_line_y.sort()
        # Look for two lines close together (box height should be 20-100 pixels)
        for i in range(len(horizontal_line_y) - 1):
            y1 = horizontal_line_y[i]
            y2 = horizontal_line_y[i + 1]
            box_height = y2 - y1
            if 20 <= box_height <= 150:  # Reasonable box height
                # Now find the left and right edges
                box_region = upper_region[y1:y2, :]
                
                # Find vertical edges
                vertical_edges = cv2.Canny(box_region, 50, 150)
                vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, box_height // 2))
                vertical_lines = cv2.morphologyEx(vertical_edges, cv2.MORPH_OPEN, vertical_kernel)
                
                # Find left and right edges
                left_col = None
                right_col = None
                for col in range(upper_w):
                    if np.sum(vertical_lines[:, col]) > box_height * 0.3:  # Strong vertical line
                        if left_col is None:
                            left_col = col
                        right_col = col
                
                if left_col is not None and right_col is not None and (right_col - left_col) > upper_w * 0.15:
                    # Found a valid box
                    return (y1, y2, left_col, right_col)
    
    # Method 2: Use contour detection as fallback
    # Apply edge detection
    edges = cv2.Canny(upper_region, 50, 150)
    
    # Method 2: Adaptive threshold (better for varying lighting)
    adaptive = cv2.adaptiveThreshold(
        upper_region, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
        cv2.THRESH_BINARY_INV, 11, 2
    )
    
    # Combine both methods
    combined = cv2.bitwise_or(edges, adaptive)
    
    # Dilate to connect broken lines
    kernel = np.ones((3, 3), np.uint8)
    dilated = cv2.dilate(combined, kernel, iterations=2)
    
    # Find contours
    contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    if not contours:
        logger.warning("No contours found for name box detection")
        return None
    
    # Look for rectangular contours that could be the name box
    # Name box characteristics:
    # - Rectangular shape (4 corners or close to it)
    # - Reasonable size (not too small, not too large)
    # - Aspect ratio around 3:1 to 5:1 (wide rectangle)
    # - Located in upper-middle portion
    
    best_box = None
    best_score = 0.0
    
    for contour in contours:
        area = cv2.contourArea(contour)
        if area < 500:  # Too small (lowered threshold)
            continue
        
        # Get bounding box (more reliable than polygon approximation)
        x, y, box_w, box_h = cv2.boundingRect(contour)
        
        # Check aspect ratio (should be wide rectangle)
        aspect_ratio = box_w / box_h if box_h > 0 else 0
        if not (2.0 <= aspect_ratio <= 8.0):  # More lenient
            continue
        
        # Check size (should be reasonable for name box)
        # Name box is typically 15-40% of form width, 2-8% of form height
        width_ratio = box_w / w
        height_ratio = box_h / h
        
        if not (0.10 <= width_ratio <= 0.50) or not (0.015 <= height_ratio <= 0.10):  # More lenient
            continue
        
        # Check position (should be in upper-middle area)
        y_ratio = y / h
        x_ratio = x / w
        
        # Should be below header but not too low
        if not (0.12 <= y_ratio <= 0.35):  # More lenient
            continue
        
        # Should be roughly in left-middle to center area (where name boxes typically are)
        if not (0.10 <= x_ratio <= 0.60):  # More lenient
            continue
        
        # Score based on how well it matches expected characteristics
        # Higher score = better match
        area_score = min(area / (w * h * 0.005), 1.0)  # Normalize area
        aspect_score = 1.0 - abs(aspect_ratio - 4.0) / 4.0  # Prefer ~4:1 ratio
        position_score = 1.0 - abs(y_ratio - 0.20) / 0.20  # Prefer around 20% from top
        
        score = area_score * 0.3 + aspect_score * 0.4 + position_score * 0.3
        
        if score > best_score:
            best_score = score
            # Convert coordinates back to full image
            best_box = (y, y + box_h, x, x + box_w)
    
    if best_box:
        logger.info(f"Name box detected: top={best_box[0]}, bottom={best_box[1]}, left={best_box[2]}, right={best_box[3]}")
        return best_box
    
    # Method 3: Fallback - look for any rectangular region in the expected area
    # This is more lenient and will find the name box even if edges aren't perfect
    logger.info("Trying fallback method: searching for rectangular regions in expected area")
    
    # Use a wider search area
    search_top = int(h * 0.12)
    search_bottom = int(h * 0.30)
    search_region = gray[search_top:search_bottom, int(w * 0.10):int(w * 0.90)]
    
    # Apply adaptive threshold
    adaptive = cv2.adaptiveThreshold(
        search_region, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY_INV, 15, 5
    )
    
    # Find contours
    contours, _ = cv2.findContours(adaptive, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # Look for the largest rectangular region
    best_area = 0
    best_rect = None
    
    for contour in contours:
        area = cv2.contourArea(contour)
        if area < 2000:  # Minimum area
            continue
        
        x, y, box_w, box_h = cv2.boundingRect(contour)
        aspect_ratio = box_w / box_h if box_h > 0 else 0
        
        # Check if it's a wide rectangle (name box characteristic)
        if 2.0 <= aspect_ratio <= 8.0 and area > best_area:
            best_area = area
            # Convert back to full image coordinates
            best_rect = (
                y + search_top,
                y + search_top + box_h,
                x + int(w * 0.10),
                x + int(w * 0.10) + box_w
            )
    
    if best_rect:
        logger.info(f"Name box detected (fallback): top={best_rect[0]}, bottom={best_rect[1]}, left={best_rect[2]}, right={best_rect[3]}")
        return best_rect
    
    logger.warning("No suitable name box found with any method")
    return None


def detect_name_box_alternative(image: np.ndarray) -> Optional[Tuple[int, int, int, int]]:
    """
    Alternative method: Use template matching or text detection to find name box.
    Looks for "STUDENT NAME:" text and finds rectangle below it.
    
    Args:
        image: Aligned form image (BGR or grayscale)
        
    Returns:
        Tuple of (top, bottom, left, right) coordinates, or None if not found
    """
    # Convert to grayscale if needed
    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image.copy()
    
    h, w = gray.shape
    
    # Focus on upper portion
    upper_region = gray[:int(h * 0.35), :]
    
    # Use horizontal line detection to find the name box
    # Name box typically has horizontal lines (top and bottom edges)
    horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (40, 1))
    detected_lines = cv2.morphologyEx(upper_region, cv2.MORPH_OPEN, horizontal_kernel)
    
    # Find horizontal lines
    edges = cv2.Canny(detected_lines, 50, 150)
    lines = cv2.HoughLinesP(edges, 1, np.pi/180, threshold=100, minLineLength=w//4, maxLineGap=10)
    
    if lines is None or len(lines) == 0:
        return None
    
    # Find pairs of horizontal lines that could be top/bottom of name box
    horizontal_lines = []
    for line in lines:
        x1, y1, x2, y2 = line[0]
        # Check if line is roughly horizontal
        if abs(y2 - y1) < 5 and abs(x2 - x1) > w // 4:
            horizontal_lines.append((y1, x1, x2))
    
    if len(horizontal_lines) < 2:
        return None
    
    # Sort by y-coordinate
    horizontal_lines.sort(key=lambda x: x[0])
    
    # Look for two horizontal lines close together (top and bottom of box)
    for i in range(len(horizontal_lines) - 1):
        y1, x1_1, x2_1 = horizontal_lines[i]
        y2, x1_2, x2_2 = horizontal_lines[i + 1]
        
        # Check if lines are close vertically (box height)
        box_height = y2 - y1
        if 20 <= box_height <= 100:  # Reasonable box height
            # Check if lines overlap horizontally
            left = max(x1_1, x1_2)
            right = min(x2_1, x2_2)
            
            if right - left > w // 3:  # Box is wide enough
                # Found potential name box
                return (y1, y2, left, right)
    
    return None

