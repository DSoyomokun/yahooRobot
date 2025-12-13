# Desk-Centric Polling Strategy

## Overview

**Desk-Centric Polling** is the strategy used by the Yahoo Robot to reliably identify which desk has a student requesting paper collection during Phase 2 (Collection).

Instead of trying to detect raised hands across the entire classroom simultaneously and determining spatial positions, the robot performs a systematic scan by turning to face each desk individually.

## The Challenge

When a student raises their hand to request paper collection, the robot needs to answer two questions:
1. **Is there a raised hand?** (Detection)
2. **Which desk is it?** (Identification)

Traditional approaches might use wide-angle camera views and complex spatial reasoning to map hand positions to desks. This introduces:
- Ambiguity in hand-to-desk mapping
- Complex computer vision (spatial localization)
- Distortion from wide-angle lenses
- Difficulty handling multiple simultaneous requests

## Our Solution: Sequential Desk Polling

The robot performs a **systematic scan** from a designated waiting position:

### High-Level Algorithm

```
1. Robot returns to origin/waiting position
2. FOR each desk in the row:
   a. Turn body/camera to face that specific desk
   b. Capture camera frame
   c. Run hand-raise detection on frame
   d. IF hand detected:
      - Add desk to collection queue
      - Log the request
   e. Turn to next desk position
3. Navigate to desks in collection queue
4. Collect papers
```

### Why This Works

**Eliminates Ambiguity:**
- When camera points at Desk #3 and detects a hand → Request is from Desk #3
- No spatial reasoning required
- No guessing or probability calculations

**Simpler Computer Vision:**
- Task becomes: "Is there a raised hand in center of frame?"
- Not: "Where is the hand in 3D space relative to the room?"
- Can use existing gesture detection code

**Reliable and Deterministic:**
- One student raises hand at a time (simple protocol)
- Clear turn-by-turn behavior
- Easy to debug and verify

**Builds on Existing Capabilities:**
- Uses robot's existing `turn_degrees()` function
- Reuses gesture detection module
- Leverages IMU for precise heading control

## Implementation Details

### Configuration

Each desk has two key properties in the configuration:

```json
{
  "desks": [
    {
      "id": 1,
      "position_cm": 30,        // Linear position for navigation
      "scan_angle": 90          // Angle to turn for polling
    },
    {
      "id": 2,
      "position_cm": 60,
      "scan_angle": 85
    }
  ]
}
```

### Scanning Process

**Step 1: Position Robot**
- Robot drives to designated polling position (likely origin)
- Resets to known heading (e.g., 0° facing forward along row)

**Step 2: Sequential Scan**
```python
for desk in desks:
    # Turn to face desk
    robot.turn_to_angle(desk.scan_angle)

    # Stabilize and capture
    time.sleep(0.5)  # Allow camera to stabilize
    frame = camera.capture()

    # Detect raised hand
    gesture = gesture_detector.detect(frame)

    if gesture == "HAND_RAISED":
        collection_queue.append(desk.id)
        logger.info(f"Desk {desk.id} requested collection")
```

**Step 3: Process Queue**
- Robot navigates to each desk in the collection queue
- At each desk: scan paper, confirm collection
- Remove from queue when complete

### Single Row Simplification

For the MVP's single row layout, polling becomes very straightforward:

```
        Scan Direction
           ↓
    [Student] [Student] [Student] [Student]
    Desk 1    Desk 2    Desk 3    Desk 4
       ↑         ↑         ↑         ↑
       90°       85°       80°       75°

    Origin → 🤖 (Robot turns in place)
```

The robot:
1. Stays at origin (or drives to optimal scanning position)
2. Turns to face perpendicular to the row
3. Scans across desks with small angular adjustments
4. Each angle corresponds to a specific desk

### Angle Calculation

For a straight row of desks, angles can be calculated geometrically:

```python
import math

def calculate_scan_angle(robot_pos, desk_pos, perpendicular_offset):
    """
    Calculate angle to turn to face a desk.

    Args:
        robot_pos: Robot's (x, y) position
        desk_pos: Desk's (x, y) position
        perpendicular_offset: Distance from row to robot

    Returns:
        Angle in degrees
    """
    dx = desk_pos[0] - robot_pos[0]
    dy = desk_pos[1] - robot_pos[1]
    angle_rad = math.atan2(dy, dx)
    return math.degrees(angle_rad)
```

Or for simple cases with desks perpendicular to robot:
```python
# Desks at: 30cm, 60cm, 90cm, 120cm along row
# Robot at origin, 30cm perpendicular to row
# All angles relative to 90° (perpendicular)

angles = {
    1: 90 + math.degrees(math.atan(0/30)),    # 90°
    2: 90 + math.degrees(math.atan(30/30)),   # ~135°
    3: 90 + math.degrees(math.atan(60/30)),   # ~153°
    4: 90 + math.degrees(math.atan(90/30)),   # ~162°
}
```

**Note:** Actual angles will be determined experimentally during Story 2.2 implementation.

## Student Protocol

For the system to work reliably, students follow a simple protocol:

1. **One at a time:** Only one student raises hand during each scan cycle
2. **Hold steady:** Keep hand raised until robot acknowledges (LED feedback)
3. **Wait for robot:** Don't lower hand until robot confirms detection

This protocol ensures deterministic behavior and avoids confusion.

## Advantages Over Alternatives

### vs. Wide-Angle Detection
- **Simpler CV:** Binary detection vs. spatial localization
- **No lens distortion:** Each desk gets centered, undistorted view
- **Higher accuracy:** Each desk examined individually with full attention

### vs. Fixed Cameras at Desks
- **Lower cost:** Single robot camera vs. multiple fixed cameras
- **Easier setup:** No classroom infrastructure required
- **More flexible:** Works with different room layouts

### vs. Manual Input (Students Press Buttons)
- **More engaging:** Visual hand-raise preserves classroom interaction
- **No extra hardware:** No buttons at each desk required
- **Natural behavior:** Raising hand is familiar classroom action

## Future Enhancements

This documentation will be updated as implementation progresses. Potential improvements:

- **Adaptive scanning:** Skip desks known to be empty (from delivery phase)
- **Multi-hand detection:** Allow multiple requests in single scan cycle
- **Confidence scoring:** Re-scan desks with uncertain detections
- **Position optimization:** Determine best robot position for scanning based on room geometry

## Related Documentation

- [Gesture Detection System](GESTURE_DETECTION.md) - Hand-raise detection implementation
- [Robot Development Workflow](ROBOT_DEV_WORKFLOW.md) - Development and testing process
- [MVP v2](../MVP_v2.md) - Overall project goals and phases

## Implementation Status

- [ ] Story 2.2: Implement desk-centric polling scan routine
- [ ] Story 2.2: Determine optimal scan angles experimentally
- [ ] Story 2.2: Integrate with gesture detection module
- [ ] Story 3.2: Integrate polling into collection mission workflow

---

**Last Updated:** 2025-12-13
**Status:** Design Document (Implementation Pending)
