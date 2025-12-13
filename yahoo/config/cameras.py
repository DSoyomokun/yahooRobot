# yahoo/config/cameras.py

from dataclasses import dataclass


@dataclass
class CameraConfig:
    name: str
    index: int
    width: int = 320
    height: int = 240


# Logical cameras for the robot
# /dev/video0 → CSI Pi Camera (IMX219)
# Using 640x480 for maximum stability (prevents segfaults with OpenCV VideoCapture)
CSI_CAMERA = CameraConfig(
    name="pi_csi",
    index=0,
    width=640,
    height=480,
)

# /dev/video1 → USB webcam (primary node)
USB_CAMERA = CameraConfig(
    name="usb_cam",
    index=1,
    width=640,
    height=480,
)
