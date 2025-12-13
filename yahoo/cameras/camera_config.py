from dataclasses import dataclass

@dataclass
class CameraConfig:
    name: str
    index: int = 0
    width: int = 1700
    height: int = 2550

