"""
Robot Scanner Module - New Modular Architecture
Handles test paper scanning, grading, and storage for the Yahoo Robot.
"""

# Main orchestrator
from .scan_control import ScanControl

# Module components (for advanced usage)
from .alignment.aligner import align_form, align_form_simple
from .alignment.roi_extractor import extract_rois, extract_name_roi, extract_bubble_roi
from .name.name_pipeline import NamePipeline
from .name.ocr_engine import OCREngine
from .bubbles.bubble_detector import BubbleDetector
from .grading.score import ScoreCalculator
from .grading.saver import ResultSaver
from .storage import Storage

# Backward compatibility (deprecated - use ScanControl instead)
# These will be removed in future versions
try:
    from .scan_control import ScanControl as RobotScanner
    capture_image = ScanControl.capture_image
except ImportError:
    RobotScanner = None
    capture_image = None

__all__ = [
    # Main API
    'ScanControl',
    
    # Backward compatibility (deprecated)
    'RobotScanner',
    'capture_image',
    
    # Module components
    'align_form',
    'align_form_simple',
    'extract_rois',
    'extract_name_roi',
    'extract_bubble_roi',
    'NamePipeline',
    'OCREngine',
    'BubbleDetector',
    'ScoreCalculator',
    'ResultSaver',
    'Storage'
]
