"""
Robot Scanner Module
Handles test paper scanning, grading, and storage for the Yahoo Robot.
"""

from .scanner import RobotScanner, capture_image
from .bubble_detector import BubbleDetector
from .name_reader import NameReader
from .grader import Grader
from .storage import Storage

__all__ = [
    'RobotScanner',
    'capture_image',
    'BubbleDetector',
    'NameReader',
    'Grader',
    'Storage'
]

