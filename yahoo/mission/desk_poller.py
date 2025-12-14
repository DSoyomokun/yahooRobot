"""
Desk-Centric Polling System - Story 2.2

Generic polling module that scans each desk sequentially by turning to face them.
Used for both delivery (person detection) and collection (gesture detection) phases.

See docs/DESK_CENTRIC_POLLING.md for design details.
"""

import time
import logging
from typing import List, Callable, Optional
from dataclasses import dataclass

import cv2


logger = logging.getLogger(__name__)


@dataclass
class PollResult:
    """Result from polling a single desk."""
    desk_id: int
    detected: bool
    confidence: float = 0.0
    timestamp: float = 0.0


class DeskPoller:
    """
    Generic desk-centric polling system.

    Scans each desk in the configured row by:
    1. Turning to face the desk at its scan angle
    2. Capturing a camera frame
    3. Running a detector (person, gesture, etc.)
    4. Recording which desks had positive detections

    This eliminates spatial ambiguity - when the robot faces Desk 3,
    any detection must be from Desk 3.
    """

    def __init__(
        self,
        robot,
        config,
        camera,
        simulate: bool = False,
        stabilization_time: float = 0.5
    ):
        """
        Initialize desk poller.

        Args:
            robot: Robot instance with drive controller
            config: RowConfig instance with desk layout
            camera: Camera instance (or None for simulation)
            simulate: If True, uses mock detection
            stabilization_time: Seconds to wait after turning for camera to stabilize
        """
        self.robot = robot
        self.config = config
        self.camera = camera
        self.simulate = simulate
        self.stabilization_time = stabilization_time

        logger.info(f"DeskPoller initialized (simulate={simulate})")
        logger.info(f"  Desks to scan: {len(config.desks)}")
        logger.info(f"  Stabilization time: {stabilization_time}s")

    def reset_heading(self):
        """
        Reset robot to origin heading.

        This ensures consistent starting position for all scans.
        """
        origin_x, origin_y, origin_heading = self.config.get_origin()

        logger.info(f"Resetting to origin heading: {origin_heading}°")

        # For now, we assume robot is already at origin
        # In a real implementation, might need to turn to absolute heading
        # using IMU feedback

        # TODO: Implement absolute heading reset using IMU
        # For MVP, we assume robot starts at correct heading

    def turn_to_desk(self, desk_id: int) -> bool:
        """
        Turn robot to face a specific desk.

        Args:
            desk_id: ID of desk to face

        Returns:
            True if turn successful
        """
        try:
            desk = self.config.get_desk(desk_id)
            if desk is None:
                logger.error(f"Desk {desk_id} not found in configuration")
                return False

            # Get scan angle for this desk from config
            scan_angle = self.config.get_scan_angle(desk_id)

            logger.debug(f"Turning to face Desk {desk_id} (angle: {scan_angle:+.1f}°)")

            # Turn to scan angle
            # Note: This assumes we're starting from a known heading (origin)
            # and scan_angle is relative to that heading
            self.robot.drive.turn_degrees(scan_angle)

            # Wait for camera to stabilize
            time.sleep(self.stabilization_time)

            return True

        except Exception as e:
            logger.error(f"Error turning to desk {desk_id}: {e}")
            return False

    def capture_frame(self):
        """
        Capture a frame from the camera.

        Returns:
            Camera frame (numpy array), or None if unavailable
        """
        if self.simulate or self.camera is None:
            # In simulation, return None (detector will handle simulation)
            logger.debug("Simulation mode: No camera frame captured")
            return None

        try:
            # Capture frame from camera
            # Assuming camera has a read() method like cv2.VideoCapture
            ret, frame = self.camera.read()

            if not ret:
                logger.warning("Failed to capture camera frame")
                return None

            return frame

        except Exception as e:
            logger.error(f"Error capturing frame: {e}")
            return None

    def scan_all_desks(
        self,
        detector_func: Callable,
        descriptor: str = "detection"
    ) -> List[PollResult]:
        """
        Generic scan of all desks using provided detector function.

        Args:
            detector_func: Function that takes a frame and returns bool
                          (e.g., person_detector.detect or gesture_detector.detect)
            descriptor: Human-readable name for what's being detected

        Returns:
            List of PollResult objects for each desk
        """
        logger.info(f"Starting desk polling scan for {descriptor}...")
        results = []

        # Reset to origin heading (ensures consistent scan)
        self.reset_heading()

        # Scan each desk in sequence
        for desk in self.config.desks:
            logger.info(f"Scanning Desk {desk.id}...")

            # Turn to face this desk
            if not self.turn_to_desk(desk.id):
                logger.error(f"Failed to turn to Desk {desk.id}, skipping")
                results.append(PollResult(
                    desk_id=desk.id,
                    detected=False,
                    confidence=0.0,
                    timestamp=time.time()
                ))
                continue

            # Capture frame
            frame = self.capture_frame()

            # Run detector
            try:
                detected = detector_func(frame)

                result = PollResult(
                    desk_id=desk.id,
                    detected=detected,
                    confidence=1.0 if detected else 0.0,
                    timestamp=time.time()
                )

                if detected:
                    logger.info(f"  ✅ {descriptor.capitalize()} detected at Desk {desk.id}")
                    # Visual feedback (green blink)
                    if hasattr(self.robot, 'leds'):
                        self.robot.leds.success()
                        time.sleep(0.3)
                        self.robot.leds.off()
                else:
                    logger.info(f"  ❌ No {descriptor} at Desk {desk.id}")

                results.append(result)

            except Exception as e:
                logger.error(f"Error running detector on Desk {desk.id}: {e}")
                results.append(PollResult(
                    desk_id=desk.id,
                    detected=False,
                    confidence=0.0,
                    timestamp=time.time()
                ))

        # Return to origin heading
        logger.info("Polling scan complete, returning to origin heading")
        self.reset_heading()

        return results

    def scan_for_persons(self) -> List[int]:
        """
        Scan all desks for person presence (delivery phase).

        Returns:
            List of desk IDs where persons were detected
        """
        from yahoo.sense.person_detector import PersonDetector

        logger.info("=== PERSON DETECTION SCAN ===")

        # Create person detector
        detector = PersonDetector(simulate=self.simulate)

        try:
            # Run generic scan
            results = self.scan_all_desks(
                detector_func=detector.detect,
                descriptor="person"
            )

            # Extract desk IDs where persons detected
            occupied_desks = [r.desk_id for r in results if r.detected]

            logger.info(f"Scan complete: {len(occupied_desks)} occupied desks found")
            logger.info(f"Occupied desk IDs: {occupied_desks}")

            return occupied_desks

        finally:
            detector.close()

    def scan_for_raised_hands(self) -> List[int]:
        """
        Scan all desks for raised hand gestures (collection phase).

        Returns:
            List of desk IDs where raised hands were detected
        """
        from yahoo.sense.gesture import GestureDetector

        logger.info("=== RAISED HAND DETECTION SCAN ===")

        # Create gesture detector
        # Note: GestureDetector expects continuous frames for temporal smoothing
        # For polling, we might need to capture multiple frames per desk
        detector = GestureDetector()

        try:
            # Custom detector function for raised hands
            def detect_raised_hand(frame) -> bool:
                """Check if a raised hand gesture is detected."""
                if self.simulate:
                    # Simulation mode: randomly detect hands for testing
                    import random
                    return random.random() > 0.5

                if frame is None:
                    return False

                gesture, _ = detector.detect(frame)
                # Any raised hand gesture counts
                return gesture in ["RIGHT_RAISED", "LEFT_RAISED", "BOTH_RAISED"]

            # Run generic scan
            results = self.scan_all_desks(
                detector_func=detect_raised_hand,
                descriptor="raised hand"
            )

            # Extract desk IDs with raised hands
            collection_queue = [r.desk_id for r in results if r.detected]

            logger.info(f"Scan complete: {len(collection_queue)} raised hands found")
            logger.info(f"Collection queue: {collection_queue}")

            return collection_queue

        finally:
            pass  # GestureDetector doesn't have explicit close

    def get_scan_summary(self, results: List[PollResult]) -> dict:
        """
        Generate summary statistics from poll results.

        Args:
            results: List of PollResult objects

        Returns:
            Dictionary with summary stats
        """
        total_desks = len(results)
        detected_count = sum(1 for r in results if r.detected)
        detected_ids = [r.desk_id for r in results if r.detected]

        avg_confidence = (
            sum(r.confidence for r in results) / total_desks
            if total_desks > 0 else 0.0
        )

        return {
            'total_desks': total_desks,
            'detected_count': detected_count,
            'detected_ids': detected_ids,
            'detection_rate': detected_count / total_desks if total_desks > 0 else 0.0,
            'avg_confidence': avg_confidence
        }
