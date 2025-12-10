"""Mission control - deliver, wait, collect behaviors"""

from .scanner.scan_control import ScanControl
# Backward compatibility
RobotScanner = ScanControl
capture_image = ScanControl.capture_image

try:
    from .mission_controller import MissionController
    __all__ = [
        'RobotScanner',
        'capture_image',
        'MissionController',
    ]
except ImportError:
    __all__ = [
        'RobotScanner',
        'capture_image',
    ]

