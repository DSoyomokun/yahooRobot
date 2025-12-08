# Gesture Detection System

Robust hand-raising detection using MediaPipe Pose for classroom interaction.

---

## Overview

The GestureDetector (`yahoo/sense/gesture.py`) provides reliable raised-hand detection for the Yahoo Robot's classroom navigation mission. It tracks both left and right hands using pose estimation and includes temporal smoothing to prevent false positives.

### Key Features

- **Dual-hand tracking** - Detects left, right, or both hands raised
- **Robust heuristics** - Uses height, arm angle, and extension for reliable detection
- **Temporal smoothing** - Requires sustained gestures to trigger (prevents flickering)
- **Continuous output** - Returns current state each frame (no event-based cooldown)
- **Visibility filtering** - Ignores occluded or low-confidence landmarks

---

## How It Works

### Detection Pipeline

1. **Capture Image** - Camera frame (BGR from OpenCV)
2. **Pose Estimation** - MediaPipe Pose extracts 33 body landmarks
3. **Visibility Check** - Ensures wrist, elbow, shoulder, and nose are visible
4. **Multi-criteria Detection** - Applies three heuristics:
   - **Height**: Wrist above shoulder AND above nose
   - **Arm angle**: Arm pointing upward (< -0.3 radians)
   - **Extension**: Hand extended away from body (> 0.08 normalized distance)
5. **Temporal Smoothing** - Counts consecutive frames meeting criteria
6. **Output Gesture** - Returns `RIGHT_RAISED`, `LEFT_RAISED`, `BOTH_RAISED`, or `NONE`

### Continuous State Output

The detector outputs the **current state** each frame rather than discrete events:

- Once `raise_frames_required` consecutive frames detect a raised hand, the gesture activates
- The gesture **stays active** as long as the hand remains raised
- When the hand goes down, the counter resets and output returns to `NONE`
- Next raise requires another `raise_frames_required` frames to activate

This prevents flickering and gives stable, predictable output.

---

## Usage

### Basic Usage

```python
from yahoo.sense.gesture import GestureDetector
from yahoo.sense.camera import open_camera
from yahoo.config.cameras import CSI_CAMERA

detector = GestureDetector()
cap = open_camera(CSI_CAMERA)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    gesture, pose_landmarks = detector.detect(frame)

    if gesture != "NONE":
        print(f"Hand raised: {gesture}")

cap.release()
```

### Configuration Parameters

```python
detector = GestureDetector(
    det_conf=0.7,              # Detection confidence (0.5-0.9)
    track_conf=0.7,            # Tracking confidence (0.5-0.9)
    raise_frames_required=8,   # Frames hand must be raised to trigger
)
```

**Parameter Tuning:**

| Parameter | Effect | Increase | Decrease |
|-----------|--------|----------|----------|
| `det_conf` | How confident MediaPipe must be to detect a person | Fewer false positives, may miss quick movements | More sensitive, may detect noise |
| `track_conf` | How confident MediaPipe must be to maintain tracking | More stable tracking, may lose person briefly | More responsive, may jitter |
| `raise_frames_required` | Frames needed to trigger gesture | More deliberate raises only | Faster response, more false positives |

---

## Detection Thresholds

The `_is_hand_raised()` method uses these thresholds:

```python
# All three must be true:
wrist.y < shoulder.y and wrist.y < nose.y  # Height: above shoulder and nose
arm_angle < -0.3                            # Angle: pointing upward (radians)
horizontal_dist > 0.08                      # Extension: hand away from body
```

### Tuning for Your Environment

**Too many false positives (detects when hand isn't raised):**
- Increase `raise_frames_required` (e.g., 10-12)
- Tighten `arm_angle` threshold (e.g., -0.4)
- Increase `horizontal_dist` (e.g., 0.10)

**Misses raised hands:**
- Decrease `raise_frames_required` (e.g., 5-6)
- Loosen `arm_angle` threshold (e.g., -0.2)
- Decrease `horizontal_dist` (e.g., 0.05)

---

## Output Format

```python
gesture, pose_landmarks = detector.detect(frame)
```

**gesture values:**
- `"RIGHT_RAISED"` - Right hand raised
- `"LEFT_RAISED"` - Left hand raised
- `"BOTH_RAISED"` - Both hands raised
- `"NONE"` - No gesture detected

**pose_landmarks:**
- MediaPipe `NormalizedLandmarkList` if person detected
- `None` if no person in frame

---

## Testing

Run the test script with debug output:

```bash
# On Mac
python3 -m tests.test_gesture_pi --cam usb

# On Raspberry Pi
python3 -m tests.test_gesture_pi --cam csi

# With debug output
python3 -m tests.test_gesture_pi --cam csi --debug
```

**Debug output shows:**
```
[DEBUG] RW.y=0.234, RS.y=0.456, vis(RW)=0.89, gesture=NONE
[DEBUG] RW.y=0.145, RS.y=0.456, vis(RW)=0.95, gesture=RIGHT_RAISED
```

---

## Integration Example

For the classroom scanning mission:

```python
from yahoo.sense.gesture import GestureDetector

class ClassroomScanner:
    def __init__(self):
        self.gesture_detector = GestureDetector(raise_frames_required=8)
        self.currently_responding = False

    def scan_row(self):
        while scanning_row:
            ret, frame = self.camera.read()
            gesture, _ = self.gesture_detector.detect(frame)

            if gesture != "NONE" and not self.currently_responding:
                self.currently_responding = True
                self.handle_raised_hand(gesture)
            elif gesture == "NONE":
                self.currently_responding = False
```

Since the detector outputs continuous state, your application logic controls when to act on gestures (e.g., using a flag to avoid repeated handling).

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| No detection at all | Check camera works, lower `det_conf` to 0.5, check lighting |
| Too many false positives | Increase `raise_frames_required`, tighten thresholds |
| Detection too slow | Decrease `raise_frames_required` |
| Works on Mac but not Pi | Use `model_complexity=0` (default), lower resolution, check lighting |

---

## Architecture

### Class Structure

```python
class GestureDetector:
    def __init__(self, det_conf, track_conf, raise_frames_required)
    def _landmarks_visible(self, lm, indices, min_vis) -> bool
    def _is_hand_raised(self, lm, wrist_idx, elbow_idx, shoulder_idx, nose_idx) -> bool
    def detect(self, frame) -> Tuple[str, Optional[NormalizedLandmarkList]]
```

### Internal State

- `right_counter` - Consecutive frames right hand detected as raised
- `left_counter` - Consecutive frames left hand detected as raised

Counters increment while hand is raised (capped at `raise_frames_required`) and reset to 0 when hand goes down.

### MediaPipe Configuration

```python
self.pose = mp_pose.Pose(
    static_image_mode=False,      # Video stream mode
    model_complexity=0,           # Lighter model for Pi
    enable_segmentation=False,    # Save CPU
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7,
)
```

---

## Related Files

- `yahoo/sense/gesture.py` - GestureDetector implementation
- `tests/test_gesture_pi.py` - Test script with debug mode
- `yahoo/config/cameras.py` - Camera configuration
- `yahoo/sense/camera.py` - Camera utilities