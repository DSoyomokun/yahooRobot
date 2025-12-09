"""
ROI-based bubble fill detection using pixel density.
Fast and accurate for printed forms.
"""
import cv2
import numpy as np
import logging
from typing import Dict, Optional
from ..alignment.preprocessing import preprocess_for_bubble_detection
from ..config.roi_config import NUM_QUESTIONS, NUM_CHOICES, FILL_THRESHOLDS

logger = logging.getLogger(__name__)


class BubbleDetector:
    """Detects filled bubbles using ROI-based pixel density."""
    
    def __init__(self, fill_threshold: Optional[float] = None, mark_type: str = "default"):
        """
        Initialize bubble detector.
        
        Args:
            fill_threshold: Custom fill threshold (0.0-1.0). If None, uses default from config.
            mark_type: Type of mark - "pencil", "pen", or "default"
        """
        self.fill_threshold = fill_threshold or FILL_THRESHOLDS.get(mark_type, FILL_THRESHOLDS["default"])
        logger.info(f"Bubble detector initialized with threshold: {self.fill_threshold:.1%}")
    
    def detect_fill(self, bubble_roi: np.ndarray) -> float:
        """
        Detect fill ratio of a bubble ROI using circular mask and Otsu's thresholding.
        Only analyzes pixels inside the bubble circle.
        
        Args:
            bubble_roi: Bubble region image (grayscale or BGR)
            
        Returns:
            Fill ratio (0.0-1.0), where 1.0 = completely filled
        """
        if bubble_roi.size == 0:
            return 0.0
        
        # Convert to grayscale if needed, but also check for colored marks (red/brown)
        if len(bubble_roi.shape) == 3:
            # Check for red/brown marks (common for pencil/pen marks)
            hsv = cv2.cvtColor(bubble_roi, cv2.COLOR_BGR2HSV)
            # Red/brown range in HSV (covers pencil marks, red pen, etc.)
            lower_red = np.array([0, 30, 30])
            upper_red = np.array([25, 255, 255])
            mask_colored = cv2.inRange(hsv, lower_red, upper_red)
            colored_pixels = np.sum(mask_colored > 0)
            
            gray = cv2.cvtColor(bubble_roi, cv2.COLOR_BGR2GRAY)
        else:
            gray = bubble_roi.copy()
            colored_pixels = 0
        
        h, w = gray.shape
        if h < 5 or w < 5:
            return 0.0
        
        # Apply slight Gaussian blur to reduce noise
        blurred = cv2.GaussianBlur(gray, (3, 3), 0)
        
        center_x, center_y = w // 2, h // 2
        # Use smaller radius to focus on center of bubble (avoid edge artifacts)
        radius = min(w, h) // 2 - 2  # Leave small margin to avoid edges
        
        if radius < 2:
            return 0.0
        
        # Create circular mask
        y, x = np.ogrid[:h, :w]
        mask = (x - center_x)**2 + (y - center_y)**2 <= radius**2
        
        # Extract only pixels inside the circle
        circle_pixels = blurred[mask]
        
        if len(circle_pixels) == 0:
            return 0.0
        
        # Improved fill detection: Use multiple methods and take the most conservative
        # Method 1: Otsu's thresholding
        try:
            threshold_value, _ = cv2.threshold(circle_pixels, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            dark_pixels_otsu = np.sum(circle_pixels < threshold_value)
        except cv2.error:
            dark_pixels_otsu = 0
        
        # Method 2: Mean-based threshold (more conservative)
        mean_brightness = np.mean(circle_pixels)
        std_brightness = np.std(circle_pixels)
        
        # For filled bubbles, mean should be significantly lower than empty bubbles
        # Use mean - 1.5*std as threshold (more conservative)
        mean_threshold = mean_brightness - 1.5 * std_brightness
        dark_pixels_mean = np.sum(circle_pixels < mean_threshold)
        
        # Method 3: Fixed threshold based on typical paper brightness
        # Empty bubbles on white paper should be > 200, filled should be < 150
        fixed_threshold = 150
        dark_pixels_fixed = np.sum(circle_pixels < fixed_threshold)
        
        # Use the most conservative (lowest) count to avoid false positives
        total_pixels = len(circle_pixels)
        fill_ratio_otsu = dark_pixels_otsu / total_pixels if total_pixels > 0 else 0.0
        fill_ratio_mean = dark_pixels_mean / total_pixels if total_pixels > 0 else 0.0
        fill_ratio_fixed = dark_pixels_fixed / total_pixels if total_pixels > 0 else 0.0
        
        # Check for colored marks (red/brown pencil/pen marks) within the circle
        if colored_pixels > 0 and len(bubble_roi.shape) == 3:
            # Create mask for circle area
            y_coords, x_coords = np.ogrid[:h, :w]
            circle_mask = (x_coords - w//2)**2 + (y_coords - h//2)**2 <= (min(w, h)//2 - 2)**2
            # Count colored pixels within circle
            colored_in_circle = np.sum(mask_colored[circle_mask] > 0)
            circle_mask_area = np.sum(circle_mask)
            colored_ratio = colored_in_circle / circle_mask_area if circle_mask_area > 0 else 0.0
            # Colored marks are a strong indicator of filling
            fill_ratio_colored = colored_ratio * 1.2  # Boost colored mark detection
        else:
            fill_ratio_colored = 0.0
        
        # Use maximum of grayscale methods, but also consider colored marks
        fill_ratio_gray = max(fill_ratio_otsu, fill_ratio_mean, fill_ratio_fixed)
        fill_ratio = max(fill_ratio_gray, fill_ratio_colored)
        
        # Additional check: if mean brightness is very high (>220), bubble is definitely empty
        if mean_brightness > 220:
            fill_ratio = 0.0
        
        # Additional check: if mean brightness is very low (<80), bubble is likely filled
        if mean_brightness < 80:
            fill_ratio = max(fill_ratio, 0.5)  # Boost confidence for very dark bubbles
        
        # Ultimate fallback if something went wrong
        if np.isnan(fill_ratio) or fill_ratio < 0:
            mean_brightness = np.mean(circle_pixels)
            if mean_brightness < 100:
                fill_ratio = 0.3  # Conservative estimate for dark bubbles
            elif mean_brightness > 200:
                fill_ratio = 0.0
            else:
                fill_ratio = 0.1  # Conservative estimate for medium brightness
        
        return min(fill_ratio, 1.0)  # Cap at 1.0
    
    def is_filled(self, bubble_roi: np.ndarray) -> bool:
        """
        Check if bubble is filled based on threshold.
        
        Args:
            bubble_roi: Bubble region image
            
        Returns:
            True if bubble is filled, False otherwise
        """
        fill_ratio = self.detect_fill(bubble_roi)
        return fill_ratio >= self.fill_threshold
    
    def extract_answers(self, aligned_image: np.ndarray, bubble_positions: dict) -> Dict[str, Optional[str]]:
        """
        Extract answers from all bubbles in aligned form using dynamic detection only.
        
        Args:
            aligned_image: Aligned form image (BGR or grayscale)
            bubble_positions: Dict from detect_bubble_positions() for dynamic detection (required)
            
        Returns:
            Dictionary mapping question number (as string) to answer letter
            Format: {"1": "A", "2": "B", ...} or None if unanswered
            
        Raises:
            ValueError: If bubble_positions is missing required questions/choices
        """
        answers = {}
        
        # Use original image for fill detection (not preprocessed)
        # detect_fill handles its own preprocessing
        h, w = aligned_image.shape[:2]
        
        for q_num in range(1, NUM_QUESTIONS + 1):
            q_str = str(q_num)
            
            # Check if question exists in dynamic detection
            if q_num not in bubble_positions:
                logger.warning(f"Question {q_num} not found in dynamic detection, marking as unanswered")
                answers[q_str] = None
                continue
            
            # Get fill ratios for all choices
            fill_ratios = {}
            
            for choice_idx, choice_letter in enumerate(['A', 'B', 'C', 'D']):
                # Get bubble coordinates (dynamic detection only)
                if choice_letter not in bubble_positions[q_num]:
                    # Missing bubble - skip but don't fail
                    fill_ratios[choice_letter] = 0.0
                    continue
                
                center_x, center_y, radius = bubble_positions[q_num][choice_letter]
                
                # Extract bubble ROI from original image
                top = max(0, center_y - radius - 2)
                bottom = min(h, center_y + radius + 2)
                left = max(0, center_x - radius - 2)
                right = min(w, center_x + radius + 2)
                
                bubble_roi = aligned_image[top:bottom, left:right]
                
                # Calculate fill ratio (detect_fill handles preprocessing)
                fill_ratio = self.detect_fill(bubble_roi)
                fill_ratios[choice_letter] = fill_ratio
            
            # Find the bubble with highest fill ratio
            if fill_ratios:
                # Sort by fill ratio (highest first)
                sorted_choices = sorted(fill_ratios.items(), key=lambda x: x[1], reverse=True)
                best_choice = sorted_choices[0]
                choice_letter, fill_ratio = best_choice
                
                # Calculate mean brightness for each bubble to find the darkest one
                # This is more reliable than fill ratio for distinguishing filled vs empty
                mean_brightnesses = {}
                for choice_idx, choice_letter_check in enumerate(['A', 'B', 'C', 'D']):
                    if choice_letter_check in bubble_positions[q_num]:
                        center_x, center_y, radius = bubble_positions[q_num][choice_letter_check]
                        top = max(0, center_y - radius - 2)
                        bottom = min(h, center_y + radius + 2)
                        left = max(0, center_x - radius - 2)
                        right = min(w, center_x + radius + 2)
                        bubble_roi = aligned_image[top:bottom, left:right]
                        
                        if len(bubble_roi.shape) == 3:
                            gray_roi = cv2.cvtColor(bubble_roi, cv2.COLOR_BGR2GRAY)
                        else:
                            gray_roi = bubble_roi.copy()
                        
                        # Get mean brightness of circle area
                        h_roi, w_roi = gray_roi.shape
                        center_x_roi, center_y_roi = w_roi // 2, h_roi // 2
                        radius_roi = min(w_roi, h_roi) // 2 - 2
                        y_coords, x_coords = np.ogrid[:h_roi, :w_roi]
                        circle_mask = (x_coords - center_x_roi)**2 + (y_coords - center_y_roi)**2 <= radius_roi**2
                        mean_brightness = np.mean(gray_roi[circle_mask])
                        mean_brightnesses[choice_letter_check] = mean_brightness
                
                # Find the bubble that's most different from the average (filled bubble should stand out)
                if mean_brightnesses:
                    # Calculate average brightness of all bubbles
                    avg_brightness = np.mean(list(mean_brightnesses.values()))
                    
                    # Find which bubble deviates most from average (should be darker for filled)
                    deviations = {}
                    for choice, brightness in mean_brightnesses.items():
                        # Negative deviation means darker than average (good for filled bubbles)
                        deviation = avg_brightness - brightness
                        deviations[choice] = deviation
                    
                    # Sort by deviation (most negative = darkest relative to average)
                    sorted_deviations = sorted(deviations.items(), key=lambda x: x[1])
                    most_deviant_choice, most_deviant_value = sorted_deviations[0]
                    
                    # Simple approach: Use the bubble that's both darkest AND has highest fill ratio
                    # Score each bubble: (brightness_deviation / 50) + fill_ratio
                    # Higher score = more likely to be filled
                    scores = {}
                    for choice in ['A', 'B', 'C', 'D']:
                        if choice in mean_brightnesses and choice in fill_ratios:
                            brightness_dev = deviations.get(choice, 0)
                            fill = fill_ratios.get(choice, 0.0)
                            # Normalize brightness deviation (divide by 50 to scale it)
                            # Higher deviation (darker) = higher score
                            brightness_score = max(0, brightness_dev) / 50.0
                            # Combined score
                            score = brightness_score + fill
                            scores[choice] = score
                    
                    if scores:
                        # Get the choice with highest combined score
                        best_scored_choice = max(scores.items(), key=lambda x: x[1])[0]
                        best_score = scores[best_scored_choice]
                        
                        # Check if the best score is significantly higher than others
                        other_scores = [s for c, s in scores.items() if c != best_scored_choice]
                        if other_scores:
                            second_best_score = max(other_scores)
                            # Best must be at least 0.2 higher (significant difference)
                            if best_score >= second_best_score + 0.2:
                                answers[q_str] = best_scored_choice
                            else:
                                answers[q_str] = None
                        else:
                            answers[q_str] = best_scored_choice
                    else:
                        # Fallback to fill ratio only
                        if len(sorted_choices) > 1:
                            second_best_ratio = sorted_choices[1][1]
                            if fill_ratio >= second_best_ratio * 1.5 and fill_ratio >= self.fill_threshold:
                                answers[q_str] = choice_letter
                            else:
                                answers[q_str] = None
                        else:
                            answers[q_str] = None if fill_ratio < self.fill_threshold else choice_letter
                else:
                    # Fallback to fill ratio only
                    if len(sorted_choices) > 1:
                        second_best_ratio = sorted_choices[1][1]
                        is_significantly_higher = fill_ratio >= second_best_ratio * 1.5 and fill_ratio >= self.fill_threshold
                    else:
                        is_significantly_higher = fill_ratio >= self.fill_threshold
                    
                    if is_significantly_higher:
                        answers[q_str] = choice_letter
                    else:
                        answers[q_str] = None
            else:
                answers[q_str] = None
        
        return answers

