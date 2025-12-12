"""
Simplified scanner module for paper scanning with weight sensor.
"""

# Main entry point
from .scan_paper import main as scan_paper_main

# Simplified pipeline
from .simple_pipeline import process_paper_scan

# Components
from .camera_capture import CameraCapture, capture_image
from .weight_sensor_mock import MockWeightSensor, HX711WeightSensor

__all__ = [
    'scan_paper_main',
    'process_paper_scan',
    'CameraCapture',
    'capture_image',
    'MockWeightSensor',
    'HX711WeightSensor',
]
