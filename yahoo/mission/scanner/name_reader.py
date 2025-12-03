"""
Name reader module for extracting student names from test papers.
"""
import cv2
import numpy as np
import pytesseract
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class NameReader:
    """Extracts student names using OCR."""
    
    def __init__(self):
        """Initialize name reader."""
        self.confidence_threshold = 15
    
    def extract_name_region(self, image: np.ndarray) -> np.ndarray:
        """
        Extract the name field region from the paper using fixed coordinates.
        The form is static, so we can use fixed coordinates for the NAME box.
        
        Args:
            image: Full paper image
            
        Returns:
            Name region image (cropped from fixed coordinates)
        """
        h, w = image.shape[:2]
        
        # Fixed coordinates for name box (top of page, adjust based on your form)
        # These are percentages - adjust based on your actual form layout
        name_top = int(h * 0.05)      # 5% from top
        name_bottom = int(h * 0.15)   # 15% from top
        name_left = int(w * 0.10)     # 10% from left
        name_right = int(w * 0.50)    # 50% from left
        
        name_region = image[name_top:name_bottom, name_left:name_right]
        
        return name_region
    
    def preprocess(self, image: np.ndarray) -> np.ndarray:
        """
        Preprocess name region for better OCR accuracy.
        
        Args:
            image: Name region image
            
        Returns:
            Preprocessed image
        """
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image.copy()
        
        # Enhance contrast
        clahe = cv2.createCLAHE(clipLimit=4.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(gray)
        
        # Apply blur
        blurred = cv2.GaussianBlur(enhanced, (3, 3), 0)
        
        # Adaptive thresholding
        thresh = cv2.adaptiveThreshold(
            blurred,
            255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY,
            15,
            5
        )
        
        # Invert if needed
        if np.mean(thresh) < 127:
            thresh = cv2.bitwise_not(thresh)
        
        # Morphological operations
        kernel = np.ones((2, 2), np.uint8)
        thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel, iterations=1)
        
        # Denoise
        denoised = cv2.fastNlMeansDenoising(thresh, None, 5, 7, 15)
        
        # Resize if too small
        h, w = denoised.shape
        min_height, min_width = 200, 400
        if h < min_height or w < min_width:
            scale = max(min_height / h, min_width / w) * 2.0
            new_h, new_w = int(h * scale), int(w * scale)
            denoised = cv2.resize(denoised, (new_w, new_h), interpolation=cv2.INTER_CUBIC)
        
        return denoised
    
    def extract_name(self, image: np.ndarray) -> Optional[str]:
        """
        Extract student name from the image.
        
        Args:
            image: Full paper image
            
        Returns:
            Extracted name or None if failed
        """
        try:
            # Extract name region
            name_region = self.extract_name_region(image)
            
            if name_region.size == 0:
                logger.warning("Name region is empty")
                return None
            
            # Preprocess
            processed = self.preprocess(name_region)
            
            # Try multiple PSM modes for handwriting
            psm_modes = [7, 8, 6]  # Single line, single word, uniform block
            best_result = None
            best_confidence = 0.0
            
            for psm in psm_modes:
                try:
                    custom_config = f'--psm {psm} -l eng'
                    ocr_data = pytesseract.image_to_data(processed, config=custom_config, output_type=pytesseract.Output.DICT)
                    
                    texts = []
                    confidences = []
                    for i, text in enumerate(ocr_data['text']):
                        if text.strip():
                            texts.append(text.strip())
                            conf = float(ocr_data['conf'][i])
                            if conf > 0:
                                confidences.append(conf)
                    
                    if texts:
                        full_text = ' '.join(texts)
                        avg_conf = sum(confidences) / len(confidences) if confidences else 0.0
                        
                        if avg_conf > best_confidence:
                            best_confidence = avg_conf
                            best_result = full_text
                except Exception as e:
                    logger.debug(f"PSM mode {psm} failed: {e}")
                    continue
            
            if best_result and best_confidence >= self.confidence_threshold:
                # Clean up the name
                name = best_result.strip()
                # Remove extra whitespace
                name = ' '.join(name.split())
                logger.info(f"Name extracted: {name} (confidence: {best_confidence:.1f}%)")
                return name
            else:
                logger.warning(f"Low confidence for name extraction: {best_confidence:.1f}%")
                return best_result if best_result else None
                
        except Exception as e:
            logger.error(f"Error extracting name: {e}")
            return None

