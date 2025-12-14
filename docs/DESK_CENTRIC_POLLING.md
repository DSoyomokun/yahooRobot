# Desk-Centric Polling Strategy

## Overview

**Desk-Centric Polling** is the core scanning strategy used by the Yahoo Robot in **both delivery and collection phases**. The robot systematically turns to face each desk individually and runs detection algorithms to identify:
- **Phase 1 (Delivery):** Which desks are occupied (person detection)
- **Phase 2 (Collection):** Which desks have raised hands (gesture detection)

This unified approach eliminates spatial ambiguity, saves navigation time, and provides consistent behavior across both mission types.

## The Challenge

The robot needs to answer key questions during both phases:

**Delivery Phase:**
1. **Is there a person at this desk?** (Detection)
2. **Which desks should I visit?** (Efficiency)

**Collection Phase:**
1. **Is there a raised hand?** (Detection)
2. **Which desk is it?** (Identification)

Traditional approaches might use:
- Wide-angle camera to see all desks simultaneously
- Complex spatial reasoning to map detections to desk positions
- Multiple cameras or sensors

This introduces:
- Ambiguity in mapping detections to desks
- Complex computer vision (spatial localization)
- Distortion from wide-angle lenses
- Wasted time navigating to empty desks

## Our Solution: Sequential Desk Polling

The robot performs a **systematic scan** from origin before each mission phase:

### High-Level Algorithm (Generic)

```
1. Robot at origin/polling position
2. Reset to known heading (0°)
3. FOR each desk in the row:
   a. Turn body/camera to face that specific desk
   b. Wait for camera stabilization (0.5s)
   c. Capture camera frame
   d. Run detector (person OR gesture, depending on phase)
   e. IF detection positive:
      - Add desk to queue
      - Log detection
      - LED feedback (green blink)
   f. Turn to next desk position
4. Return to original heading
5. Return queue (list of desk IDs)
6. Navigate only to desks in queue
7. Perform mission action (deliver OR collect)
```

### Phase-Specific Usage

**Delivery Mission:**
```python
# Scan for occupied desks
occupied_desks = poller.scan_for_persons()
# Returns: [1, 2, 4] (Desk 3 is empty)

# Navigate only to occupied desks
for desk_id in occupied_desks:
    deliver_to(desk_id)
```

**Collection Mission:**
```python
# Scan for raised hands
collection_queue = poller.scan_for_raised_hands()
# Returns: [2, 4] (Only Desks 2 and 4 raised hands)

# Navigate only to requesting desks
for desk_id in collection_queue:
    collect_from(desk_id)
```

### Why This Works

**Eliminates Ambiguity:**
- When camera points at Desk #3 and detects → It's from Desk #3
- No spatial reasoning required
- No guessing or probability calculations
- Works for both person detection and gesture detection

**Simpler Computer Vision:**
- Task becomes: "Is there [a person / raised hand] in center of frame?"
- Not: "Where is [the person / hand] in 3D space relative to the room?"
- Can use existing detection code
- High accuracy (detector only needs binary yes/no)

**Maximum Efficiency:**
- **Saves navigation time** - Robot only visits desks that need attention
- Example: 1 absent student = skip 1 desk = ~30 seconds saved
- Consistent behavior across both mission phases

**Reliable and Deterministic:**
- Clear turn-by-turn behavior
- Easy to debug and verify
- Predictable outcomes
- Students understand the robot's scanning pattern

**Builds on Existing Capabilities:**
- Uses robot's existing `turn_degrees()` function
- Reuses person detector and gesture detector
- Leverages IMU for precise heading control
- Minimal new code required

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

- [x] Story 1.1: Configuration includes scan angles for each desk
- [ ] Story 2.1: Person detector implementation
- [ ] Story 2.2: Implement generic desk-centric polling module
- [ ] Story 2.2: Determine optimal scan angles experimentally
- [ ] Story 2.2: Test with both person detection and gesture detection
- [ ] Story 3.1: Integrate polling into delivery mission (scan for persons)
- [ ] Story 3.2: Integrate polling into collection mission (scan for raised hands)

---

**Last Updated:** 2025-12-13
**Status:** Design Document (Implementation Pending)
**Optimization:** Now used for BOTH delivery and collection phases
