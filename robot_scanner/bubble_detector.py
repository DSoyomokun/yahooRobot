"""
Bubble detection module for multiple-choice answer extraction.
"""
import cv2
import numpy as np
import logging
from typing import Dict, Optional, List

logger = logging.getLogger(__name__)


class BubbleDetector:
    """Detects and extracts answers from multiple-choice bubbles."""
    
    def __init__(self):
        """Initialize bubble detector."""
        self.min_area = 15  # Lowered to detect smaller bubbles
        self.max_area = 12000  # Increased to detect larger bubbles
        self.fill_threshold = 0.35  # Balanced threshold - bubble must be darker than paper
        self.aspect_tolerance = 0.6  # More lenient for slightly non-circular bubbles
        self.circularity_threshold = 0.3  # Lowered to detect slightly imperfect circles
    
    def preprocess(self, image: np.ndarray) -> np.ndarray:
        """
        Preprocess image for bubble detection.
        Pipeline: Convert to grayscale → Threshold
        
        Args:
            image: Input image
            
        Returns:
            Thresholded binary image
        """
        # Step 1: Convert to grayscale
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image.copy()
        
        # Step 2: Threshold the image
        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        
        return thresh
    
    def detect_bubbles(self, image: np.ndarray) -> List[Dict]:
        """
        Detect all bubbles in the image.
        Pipeline: Find contours → Filter for circular shapes (bubble size range)
        
        Args:
            image: Preprocessed binary image
            
        Returns:
            List of bubble dictionaries
        """
        # Step 3: Find contours
        contours, _ = cv2.findContours(image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if not contours:
            return []
        
        bubbles = []
        
        for contour in contours:
            area = cv2.contourArea(contour)
            
            # Step 4: Filter for circular shapes (bubble size range)
            if area < self.min_area or area > self.max_area:
                continue
            
            x, y, w, h = cv2.boundingRect(contour)
            if h == 0:
                continue
            
            # Check if circular (aspect ratio close to 1.0)
            aspect_ratio = float(w) / h
            if abs(aspect_ratio - 1.0) <= self.aspect_tolerance:
                perimeter = cv2.arcLength(contour, True)
                if perimeter > 0:
                    circularity = 4 * np.pi * area / (perimeter * perimeter)
                    
                    if circularity >= self.circularity_threshold:
                        M = cv2.moments(contour)
                        if M["m00"] != 0:
                            cx = int(M["m10"] / M["m00"])
                            cy = int(M["m01"] / M["m00"])
                            
                            bubbles.append({
                                'contour': contour,
                                'center': (cx, cy),
                                'area': area,
                                'bounding_rect': (x, y, w, h),
                                'circularity': circularity
                            })
        
        logger.info(f"Detected {len(bubbles)} bubbles")
        return bubbles
    
    def calculate_fill(self, image: np.ndarray, bubble: Dict) -> float:
        """
        Detect which bubble is filled by average pixel darkness.
        Uses the original grayscale image to check if bubble is filled (darker).
        
        Args:
            image: Grayscale image (original, not thresholded)
            bubble: Bubble dictionary
            
        Returns:
            Fill percentage (0.0 to 1.0) - higher = more filled/darker
        """
        x, y, w, h = bubble['bounding_rect']
        
        # Extract bubble region with padding
        padding = 2
        x_start = max(0, x - padding)
        y_start = max(0, y - padding)
        x_end = min(image.shape[1], x + w + padding)
        y_end = min(image.shape[0], y + h + padding)
        
        bubble_roi = image[y_start:y_end, x_start:x_end]
        
        if bubble_roi.size == 0:
            return 0.0
        
        # Ensure grayscale
        if len(bubble_roi.shape) == 3:
            gray_roi = cv2.cvtColor(bubble_roi, cv2.COLOR_BGR2GRAY)
        else:
            gray_roi = bubble_roi.copy()
        
        # Use the bubble contour to create a mask
        try:
            mask = np.zeros(gray_roi.shape, dtype=np.uint8)
            contour = bubble.get('contour')
            if contour is not None:
                # Adjust contour coordinates to ROI
                adjusted_contour = contour.copy()
                adjusted_contour[:, :, 0] -= x_start
                adjusted_contour[:, :, 1] -= y_start
                cv2.fillPoly(mask, [adjusted_contour], 255)
                
                # Get pixels inside the bubble
                masked_pixels = gray_roi[mask > 0]
                if len(masked_pixels) == 0:
                    return 0.0
                
                # Calculate average brightness inside bubble
                bubble_brightness = np.mean(masked_pixels)
                
                # Get surrounding paper brightness for comparison
                # Expand ROI to get paper area around bubble
                expand = 15
                x_expand = max(0, x_start - expand)
                y_expand = max(0, y_start - expand)
                x_end_expand = min(image.shape[1], x_end + expand)
                y_end_expand = min(image.shape[0], y_end + expand)
                
                paper_roi = image[y_expand:y_end_expand, x_expand:x_end_expand]
                if len(paper_roi.shape) == 3:
                    paper_gray = cv2.cvtColor(paper_roi, cv2.COLOR_BGR2GRAY)
                else:
                    paper_gray = paper_roi
                
                # Get paper pixels (outside the bubble mask area)
                # Create expanded mask
                expanded_mask = np.zeros(paper_gray.shape, dtype=np.uint8)
                if contour is not None:
                    expanded_contour = contour.copy()
                    expanded_contour[:, :, 0] -= x_expand
                    expanded_contour[:, :, 1] -= y_expand
                    cv2.fillPoly(expanded_mask, [expanded_contour], 255)
                
                paper_mask = cv2.bitwise_not(expanded_mask)
                paper_pixels = paper_gray[paper_mask > 0]
                
                if len(paper_pixels) > 10:
                    paper_brightness = np.median(paper_pixels)  # Use median to avoid outliers
                else:
                    paper_brightness = 220  # Default bright paper
                
                # Calculate fill: compare bubble darkness to paper brightness
                # Filled bubbles should be at least 80 points darker than paper
                brightness_diff = paper_brightness - bubble_brightness
                
                # Normalize: 0-1 scale where 60+ point difference = filled
                # More lenient calculation
                if brightness_diff >= 60:
                    fill_ratio = min(1.0, 0.5 + (brightness_diff - 60) / 80.0)  # 60-140 diff maps to 0.5-1.0
                elif brightness_diff >= 30:
                    fill_ratio = (brightness_diff - 30) / 60.0  # 30-60 diff maps to 0.0-0.5
                else:
                    fill_ratio = 0.0  # Too similar to paper = empty
                
                return fill_ratio
        except Exception:
            pass
        
        # Fallback: use entire ROI - compare to estimated paper brightness
        bubble_brightness = np.mean(gray_roi)
        paper_brightness = 200  # Estimated paper brightness
        
        brightness_diff = paper_brightness - bubble_brightness
        if brightness_diff > 50:
            fill_ratio = min(1.0, brightness_diff / 100.0)
        else:
            fill_ratio = max(0.0, brightness_diff / 50.0)
        return fill_ratio
    
    def group_by_question(self, bubbles: List[Dict], num_choices: int = 4) -> Dict[int, List[Dict]]:
        """
        Group bubbles by x/y coordinate into each question.
        
        Args:
            bubbles: List of detected bubbles
            num_choices: Number of answer choices per question (A, B, C, D)
            
        Returns:
            Dictionary mapping question number to bubbles
        """
        if not bubbles:
            return {}
        
        # Step 5: Group bubbles by x/y coordinates
        # Sort by y-coordinate (rows) first, then by x-coordinate (columns)
        sorted_bubbles = sorted(bubbles, key=lambda b: (b['center'][1], b['center'][0]))
        
        question_groups = {}
        current_question = 1
        current_row_y = sorted_bubbles[0]['center'][1]
        row_tolerance = 50  # Pixels tolerance for same row
        
        for bubble in sorted_bubbles:
            cy = bubble['center'][1]
            
            # Check if this bubble is in a new row (new question)
            if abs(cy - current_row_y) > row_tolerance:
                current_question += 1
                current_row_y = cy
            
            if current_question not in question_groups:
                question_groups[current_question] = []
            
            question_groups[current_question].append(bubble)
        
        # Sort bubbles within each question by x-coordinate (A, B, C, D order)
        for question_num in question_groups:
            question_groups[question_num] = sorted(
                question_groups[question_num],
                key=lambda b: b['center'][0]
            )[:num_choices]  # Limit to num_choices
        
        return question_groups
    
    def extract_answers(self, image: np.ndarray, num_questions: Optional[int] = None, num_choices: int = 4) -> Dict[str, Optional[str]]:
        """
        Extract answers from all bubbles in the image.
        Complete pipeline: grayscale → threshold → contours → filter circles → group by x/y → detect fill by darkness
        
        Args:
            image: Paper image
            num_questions: Expected number of questions
            num_choices: Number of answer choices per question (A, B, C, D)
            
        Returns:
            Dictionary mapping question number (as string) to answer letter
            Format: {"1": "B", "2": "D", ...} or None if unanswered
        """
        # Get grayscale version for fill detection
        if len(image.shape) == 3:
            gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray_image = image.copy()
        
        # Preprocess: grayscale → threshold
        processed = self.preprocess(image)
        
        # Detect bubbles: find contours → filter for circular shapes
        bubbles = self.detect_bubbles(processed)
        
        if not bubbles:
            logger.warning("No bubbles detected")
            return {}
        
        # Group bubbles by x/y coordinates into questions
        question_groups = self.group_by_question(bubbles, num_choices)
        
        answers = {}
        choice_letters = [chr(ord('A') + i) for i in range(num_choices)]
        
        for question_num, question_bubbles in question_groups.items():
            if num_questions and question_num > num_questions:
                break
            
            marked_bubbles = []
            
            # Detect which bubble is filled by average pixel darkness
            for i, bubble in enumerate(question_bubbles[:num_choices]):
                fill_percentage = self.calculate_fill(gray_image, bubble)
                
                if fill_percentage >= self.fill_threshold:
                    marked_bubbles.append((i, choice_letters[i], fill_percentage))
            
            # Determine answer
            if len(marked_bubbles) == 0:
                answers[str(question_num)] = None
            elif len(marked_bubbles) == 1:
                answers[str(question_num)] = marked_bubbles[0][1]
            else:
                # Multiple bubbles marked - use the one with highest fill (darkest)
                marked_bubbles.sort(key=lambda x: x[2], reverse=True)
                best_fill = marked_bubbles[0][2]
                second_fill = marked_bubbles[1][2] if len(marked_bubbles) > 1 else 0
                
                # If best fill is significantly higher (15% difference), use it
                # Otherwise, it's ambiguous
                if best_fill - second_fill > 0.15:
                    answers[str(question_num)] = marked_bubbles[0][1]
                else:
                    # Ambiguous - but still pick the best one if it's clearly filled
                    if best_fill > 0.50:  # If best is more than 50% filled, use it
                        answers[str(question_num)] = marked_bubbles[0][1]
                    else:
                        answers[str(question_num)] = None
        
        return answers

