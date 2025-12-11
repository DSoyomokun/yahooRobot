# mission/scanner/preprocess.py
"""
Preprocessing pipeline for test-sheet images:
1. Detect printed form edges (ignores physical page edges)
2. Perspective-transform sheet to normalized 1700x2550 frame
3. Normalize illumination
4. Adaptive thresholding for bubble detection
"""

import cv2
import numpy as np
from .config import WARPED_WIDTH, WARPED_HEIGHT

# ------------------------------------------------------------
# Utility: Order 4 points (top-left, top-right, bottom-right, bottom-left)
# ------------------------------------------------------------
def order_points(pts):
    """Return coordinates as TL, TR, BR, BL."""
    rect = np.zeros((4, 2), dtype="float32")

    s = pts.sum(axis=1)
    rect[0] = pts[np.argmin(s)]   # top-left
    rect[2] = pts[np.argmax(s)]   # bottom-right

    diff = np.diff(pts, axis=1)
    rect[1] = pts[np.argmin(diff)]  # top-right
    rect[3] = pts[np.argmax(diff)]  # bottom-left

    return rect


# ------------------------------------------------------------
# Step 1 — Detect the bounding box of the PRINTED FORM
# ------------------------------------------------------------
def detect_form_contour(img_gray):
    """
    Detects the contour of the printed test region, NOT the paper border.

    Strategy:
    - Edge detection
    - Morphological closing to fill gaps
    - Find largest rectangular-ish contour
    """
    blurred = cv2.GaussianBlur(img_gray, (5,5), 0)
    edges = cv2.Canny(blurred, 50, 150)

    # Close gaps in edges
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (9, 9))
    closed = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel)

    contours, _ = cv2.findContours(closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if not contours:
        raise Exception("No contours found — cannot detect form boundary.")

    # Choose contour with largest area (printed region)
    contours = sorted(contours, key=cv2.contourArea, reverse=True)
    form_contour = None

    for cnt in contours:
        peri = cv2.arcLength(cnt, True)
        approx = cv2.approxPolyDP(cnt, 0.02 * peri, True)

        # Look for 4-point contours (rectangle-like)
        if len(approx) == 4:
            form_contour = approx
            break

    if form_contour is None:
        raise Exception("Failed to detect rectangular printed form area.")

    return form_contour.reshape(4,2)


# ------------------------------------------------------------
# Step 2 — Warp sheet to normalized frame (1700 x 2550)
# ------------------------------------------------------------
def warp_form(img_color, form_pts):
    """
    Apply perspective transform to create a normalized sheet image.
    """
    rect = order_points(form_pts)
    dst = np.array([
        [0, 0],
        [WARPED_WIDTH - 1, 0],
        [WARPED_WIDTH - 1, WARPED_HEIGHT - 1],
        [0, WARPED_HEIGHT - 1]
    ], dtype="float32")

    M = cv2.getPerspectiveTransform(rect, dst)
    warped = cv2.warpPerspective(img_color, M, (WARPED_WIDTH, WARPED_HEIGHT))

    return warped


# ------------------------------------------------------------
# Step 3 — Illumination normalization + thresholding (IMPROVED)
# ------------------------------------------------------------
def normalize_and_threshold(warped_color):
    """
    Normalize lighting across the warped sheet and threshold for bubble detection.
    Enhanced with CLAHE for better contrast.
    """
    gray = cv2.cvtColor(warped_color, cv2.COLOR_BGR2GRAY)

    # Apply CLAHE (Contrast Limited Adaptive Histogram Equalization) for better contrast
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(gray)

    # Normalize uneven illumination
    blur = cv2.GaussianBlur(enhanced, (41, 41), 0)
    normalized = cv2.divide(enhanced, blur, scale=255)

    # Adaptive threshold with optimized parameters
    thresh = cv2.adaptiveThreshold(
        normalized, 255,
        cv2.ADAPTIVE_THRESH_MEAN_C,
        cv2.THRESH_BINARY_INV,
        25,  # Smaller block size for better detail
        12   # Adjusted constant
    )

    return enhanced, thresh


# ------------------------------------------------------------
# MAIN ENTRYPOINT for pipeline
# ------------------------------------------------------------
def preprocess_image(img_color):
    """
    Full preprocessing pipeline.
    Input: BGR color image from PiCam or Mac webcam
    Returns:
        warped_color  — normalized sheet in color
        warped_gray   — grayscale warped version
        warped_thresh — thresholded for bubble detection
    """
    if img_color is None:
        raise Exception("Input image is None in preprocess_image()")

    gray = cv2.cvtColor(img_color, cv2.COLOR_BGR2GRAY)

    # 1. Detect printed form edges
    form_pts = detect_form_contour(gray)

    # 2. Warp to normalized resolution
    warped_color = warp_form(img_color, form_pts)

    # 3. Normalize illumination + threshold
    warped_gray, warped_thresh = normalize_and_threshold(warped_color)

    return warped_color, warped_gray, warped_thresh

