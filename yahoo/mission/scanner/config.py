# mission/scanner/config.py
"""
Global configuration for the scanner subsystem:
- warped sheet resolution
- roster
- answer key
- ROI definitions (percentage-based)
"""

import json
import os

# ------------------------------------------------------
# 1. WARPED RESOLUTION (after perspective correction)
# ------------------------------------------------------
WARPED_WIDTH  = 1700
WARPED_HEIGHT = 2550

# Helper to convert percentages into absolute pixels
def roi_pct_to_px(pct_roi, width=WARPED_WIDTH, height=WARPED_HEIGHT):
    """
    pct_roi: (x_pct, y_pct, w_pct, h_pct)
    returns (x_px, y_px, w_px, h_px)
    """
    x = int(pct_roi[0] * width)
    y = int(pct_roi[1] * height)
    w = int(pct_roi[2] * width)
    h = int(pct_roi[3] * height)
    return (x, y, w, h)

# ------------------------------------------------------
# 2. NAME BOX ROI (percentage-based)
# Based on uploaded test sheet layout
# Adjusted to capture the actual name box below "TEST PAPER" title
# ------------------------------------------------------
NAME_ROI_PCT = (0.075, 0.12, 0.85, 0.08)  # y: 12% from top (was 5.8%), height: 8% (was 7.5%)

# ------------------------------------------------------
# 3. WEIGHT SENSOR CONFIGURATION
# ------------------------------------------------------
# Weight threshold in grams to trigger camera
WEIGHT_THRESHOLD_GRAMS = float(os.getenv("WEIGHT_THRESHOLD_GRAMS", "1.0"))

# HX711 GPIO pins (for Raspberry Pi)
HX711_DT_PIN = int(os.getenv("HX711_DT_PIN", "5"))   # Data pin
HX711_SCK_PIN = int(os.getenv("HX711_SCK_PIN", "6")) # Clock pin

# Enable/disable weight sensor
WEIGHT_SENSOR_ENABLED = os.getenv("WEIGHT_SENSOR_ENABLED", "false").lower() == "true"

# Use mock sensor for testing (when hardware not available)
USE_MOCK_SENSOR = os.getenv("USE_MOCK_SENSOR", "true").lower() == "true"

# ------------------------------------------------------
# 4. CAMERA CONFIGURATION
# ------------------------------------------------------
CAMERA_INDEX = int(os.getenv("CAMERA_INDEX", "0"))
USE_PICAM = os.getenv("USE_PICAM", "false").lower() == "true"

# ------------------------------------------------------
# 5. ROSTER (You can move this to a JSON file if preferred)
# ------------------------------------------------------
CLASS_ROSTER = [
    ("Abera, Nahom", "Student"),
    ("Ashok, Rithika", "Student"),
    ("Bazil, Karian", "Student"),
    ("Berhan, Sami", "Student"),
    ("Bhuiyan, Irfan", "Student"),
    ("Binitie, Ej", "Student"),
    ("Boone, Joseph", "Student"),
    ("Emeka-Okoye, Chinaza", "Student"),
    ("Faizi, Fizzah", "Student"),
    ("Fikru, Gedeon", "Student"),
    ("Forrester, Edward", "Student"),
    ("Griffin, Carter", "Student"),
    ("Iyer, Anirudh", "Student"),
    ("Jeong, Jay", "Student"),
    ("Kalu, Ugo", "Student"),
    ("Kim, Ricky", "Student"),
    ("Le, Victoria", "Student"),
    ("Lee, Yoon Jae", "Instructor"),
    ("LeShore, Heavena", "Student"),
    ("Li, Atlas", "Student"),
    ("Lyu, Haolin", "Student"),
    ("Mandava, Aasrith", "TA Designer"),
    ("Mathieu, Michael", "Student"),
    ("Maxwell, Chisom", "Student"),
    ("Mekonnen, Jyonas", "Student"),
    ("Mohamad, Mohamad", "Student"),
    ("Nwokedi, Chioma", "Student"),
    ("Onafuye, Nick", "Student"),
    ("Patel, Jainish", "Student"),
    ("Patel, Vivek", "Student"),
    ("Soyomokun, Damilare", "Student"),
]


