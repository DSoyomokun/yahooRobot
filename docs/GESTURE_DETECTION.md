# Gesture Detection System

Robust hand-raising detection using MediaPipe Pose for classroom interaction.

---

## Overview

The GestureDetector (`yahoo/sense/gesture.py`) provides reliable raised-hand detection for the Yahoo Robot's classroom navigation mission. It tracks both left and right hands using pose estimation and includes temporal smoothing to prevent false positives.

### Key Features

- **Dual-hand tracking** - Detects left, right, or both hands raised
- **Robust heuristics** - Uses height, arm angle, and extension for reliable detection
- **Temporal smoothing** - Requires sustained gestures to prevent flickering
- **Cooldown mechanism** - Prevents event spam
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
6. **Cooldown** - Prevents re-triggering for a minimum number of frames
7. **Output Gesture** - Returns `RIGHT_RAISED`, `LEFT_RAISED`, `BOTH_RAISED`, or `NONE`

### Three-Criteria Heuristic

To get reliable raised-hand detection, the system uses:

1. **Correct plumbing**: Camera → OpenCV → MediaPipe Pose (with proper color conversion, object reuse)
2. **Clear definition**: "Hand raised" means wrist above shoulder/nose, arm angled upward, hand extended
3. **Temporal smoothing**: Debouncing prevents flicker and spam events

---

## Usage

### Basic Usage

```python
from yahoo.sense.gesture import GestureDetector
from yahoo.sense.camera import open_camera
from yahoo.config.cameras import CSI_CAMERA

# Initialize detector
detector = GestureDetector()

# Open camera
cap = open_camera(CSI_CAMERA)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Detect gesture
    gesture, pose_landmarks = detector.detect(frame)

    if gesture != "NONE":
        print(f"Detected: {gesture}")

cap.release()
```

### Configuration Parameters

```python
detector = GestureDetector(
    det_conf=0.7,              # Detection confidence (0.5-0.9)
    track_conf=0.7,            # Tracking confidence (0.5-0.9)
    raise_frames_required=8,   # Frames hand must be raised
    cooldown_frames=15         # Frames before next detection
)
```

**Parameter Tuning:**

- **`det_conf`** - Higher = fewer false positives, may miss quick gestures
- **`track_conf`** - Higher = more stable tracking, may lose person briefly
- **`raise_frames_required`** - Higher = needs hand up longer (more deliberate)
- **`cooldown_frames`** - Higher = less frequent triggers (prevents spam)

### Testing and Debug Mode

Run the test script with debug output:

```bash
# On Mac (development)
python3 -m tests.test_gesture_pi --cam usb

# On Raspberry Pi (with camera)
python3 -m tests.test_gesture_pi --cam csi

# With debug output for tuning thresholds
python3 -m tests.test_gesture_pi --cam csi --debug
```

**Debug output shows:**
- Wrist and shoulder Y-coordinates
- Landmark visibility scores
- Current gesture state

This helps you tune the detection thresholds in `_is_hand_raised()`.

---

## Detection Thresholds

The `_is_hand_raised()` method uses these thresholds (in `yahoo/sense/gesture.py`):

```python
# Arm angle threshold (radians)
arm_angle < -0.3  # Pointing upward

# Horizontal extension (normalized 0-1)
horizontal_dist > 0.08  # Hand away from body

# Height check
wrist_y < shoulder_y and wrist_y < nose_y  # Above both
```

### Tuning for Your Environment

**If detection is too sensitive (false positives):**
- Increase `raise_frames_required` (e.g., 10-12)
- Decrease `arm_angle` threshold (e.g., -0.4)
- Increase `horizontal_dist` (e.g., 0.10)

**If detection misses raised hands:**
- Decrease `raise_frames_required` (e.g., 5-6)
- Increase `arm_angle` threshold (e.g., -0.2)
- Decrease `horizontal_dist` (e.g., 0.05)

**For classroom use:**
- Test with students at typical distance from camera
- Adjust lighting for better pose detection
- Mount camera to see students' upper bodies clearly

---

## Output Format

### Gesture Labels

```python
gesture, pose_landmarks = detector.detect(frame)
```

**Possible values:**
- `"RIGHT_RAISED"` - Right hand raised
- `"LEFT_RAISED"` - Left hand raised
- `"BOTH_RAISED"` - Both hands raised
- `"NONE"` - No gesture detected

**pose_landmarks:**
- MediaPipe NormalizedLandmarkList if person detected
- `None` if no person in frame

---

## Classroom Context

### Practical Setup Tips

**Camera Placement:**
- Mount camera to see a single row/zone clearly
- Focus on detecting along robot's current row (not whole classroom)
- Ensure upper body (torso, head, arms) visible in frame

**Student Distance & Size:**
- Low resolution (320×240) makes distant students tiny
- Best results when frame contains torso + head + arms
- For full-body standing, pose detection may be less reliable

**Lighting:**
- NoIR cameras or dim rooms make pose jittery
- Keep classroom reasonably lit for best results
- Test under actual classroom lighting conditions

**Testing with Real Users:**
1. Have teammate sit where student would sit
2. Raise hand in different ways:
   - Straight up
   - Slightly forward
   - Slightly sideways
3. Adjust thresholds based on what works reliably

---

## How to Ensure Correctness

"Correct" gesture detection means:

1. **Consistent behavior** - Same gesture → same output most of the time
2. **Low false positives** - Scratching head doesn't trigger "RAISED"
3. **Stable in environment** - Works under classroom lighting/camera angle/distance

### Tuning Process

1. Use the robust detector as your base (already implemented)
2. Run `tests/test_gesture_pi.py --cam csi --debug`
3. Film someone raising hand in different positions
4. Adjust parameters until behavior feels right:
   - `raise_frames_required`
   - `cooldown_frames`
   - `horizontal_dist` threshold
   - `arm_angle` threshold

**Example debug session:**

```bash
python3 -m tests.test_gesture_pi --cam csi --debug
```

Watch the debug output while waving your hand:
```
[DEBUG] RW.y=0.234, RS.y=0.456, vis(RW)=0.89, gesture=NONE
[DEBUG] RW.y=0.189, RS.y=0.456, vis(RW)=0.92, gesture=NONE
[DEBUG] RW.y=0.145, RS.y=0.456, vis(RW)=0.95, gesture=RIGHT_RAISED
```

This shows exact numbers to help you set thresholds.

---

## Architecture Details

### Class Structure

```python
class GestureDetector:
    def __init__(self, det_conf, track_conf, raise_frames_required, cooldown_frames)
    def _landmarks_visible(self, lm, indices, min_vis) -> bool
    def _is_hand_raised(self, lm, wrist_idx, elbow_idx, shoulder_idx, nose_idx, img_h, img_w) -> bool
    def detect(self, frame) -> Tuple[str, Optional[NormalizedLandmarkList]]
```

**Key Methods:**

- `detect()` - Main entry point, processes frame and returns gesture
- `_is_hand_raised()` - Applies three heuristics (height, angle, extension)
- `_landmarks_visible()` - Checks if required landmarks are visible

**Internal State:**

- `frame_count` - Total frames processed
- `right_counter` - Consecutive frames right hand raised
- `left_counter` - Consecutive frames left hand raised
- `last_detected_frame` - Frame number of last detection (for cooldown)
- `last_gesture` - Previous gesture detected

### MediaPipe Configuration

```python
self.pose = mp_pose.Pose(
    static_image_mode=False,      # Video stream mode
    model_complexity=0,           # Lighter model for Pi
    enable_segmentation=False,    # Don't need segmentation
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7,
)
```

**Why these settings:**
- `model_complexity=0` - Faster on Raspberry Pi (less accurate but sufficient)
- `static_image_mode=False` - Optimized for video, not single images
- `enable_segmentation=False` - Saves CPU, we only need landmarks

---

## Event Logging

The test script logs events to `logs/gesture_events.csv`:

```csv
timestamp,gesture
2025-12-05 22:30:15.234,RIGHT_RAISED
2025-12-05 22:30:18.567,LEFT_RAISED
2025-12-05 22:30:22.890,BOTH_RAISED
```

This helps track when students raise hands for later analysis.

---

## Integration with Mission

For the classroom scanning mission, the gesture detector integrates like this:

```python
from yahoo.sense.gesture import GestureDetector

class ClassroomScanner:
    def __init__(self):
        self.gesture_detector = GestureDetector(
            raise_frames_required=8,
            cooldown_frames=20  # Longer cooldown for classroom
        )

    def scan_row(self):
        """Scan current row for raised hands."""
        while scanning_row:
            ret, frame = self.camera.read()
            gesture, _ = self.gesture_detector.detect(frame)

            if gesture != "NONE":
                self.log_student_response(gesture)
                self.robot.stop()
                # Handle raised hand...
```

---

## Troubleshooting

**No detection at all:**
- Check camera is working (`cv2.imshow` to verify)
- Verify person is visible in frame
- Lower `det_conf` and `track_conf` (try 0.5)
- Check lighting conditions

**Too many false positives:**
- Increase `raise_frames_required`
- Increase `cooldown_frames`
- Tighten thresholds in `_is_hand_raised()`

**Detection too slow:**
- Decrease `raise_frames_required`
- Use `model_complexity=0` (already default)

**Gesture flickers on/off:**
- Increase `raise_frames_required`
- Increase `cooldown_frames`
- Check camera framerate is stable

**Works on Mac but not Pi:**
- Pi has less CPU - use `model_complexity=0`
- Check camera resolution (lower = faster)
- Verify lighting is adequate

---

## Related Files

- **`yahoo/sense/gesture.py`** - GestureDetector implementation
- **`tests/test_gesture_pi.py`** - Test script with debug mode
- **`yahoo/config/cameras.py`** - Camera configuration
- **`yahoo/sense/camera.py`** - Camera utilities
- **`logs/gesture_events.csv`** - Event log output

---

## References

- [MediaPipe Pose](https://google.github.io/mediapipe/solutions/pose.html)
- [OpenCV VideoCapture](https://docs.opencv.org/4.x/d8/dfe/classcv_1_1VideoCapture.html)
- [Yahoo Robot Documentation](README.md)
