#!/usr/bin/env python3
"""
Hand Raise Helper - On-Demand Assistance

Watches webcam for hand raise gesture detection.
When detected, prompts which desk needs help.
Robot navigates to that specific desk.

Use Case:
- Student raises hand during work time
- Webcam detects raised hand gesture
- Operator confirms which desk
- Robot goes to help that student

CURRENT IMPLEMENTATION (Manual Confirmation):
- Gesture detector runs on webcam
- When hand raise detected → beep/alert
- Prompt: "Which desk raised hand? (1-4): "
- Navigate to that desk only

FUTURE IMPLEMENTATION (Automated Desk ID):
- Use desk-centric polling with gesture detection
- Automatically identify which desk has raised hand
- No manual confirmation needed
- See yahoo/mission/desk_poller.py scan_for_raised_hands()

Why Manual Confirmation First:
- Faster to implement for deadline
- Webcam can detect gesture but not desk location
- Allows testing navigation to specific desk
- Detection code already exists in yahoo/sense/gesture.py
- Easy to integrate automated polling later
"""

import sys
import time
import logging
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from yahoo.robot import Robot
from yahoo.config.row_loader import load_row_config
from yahoo.sense.gesture import GestureDetector

# FUTURE: For automated desk identification
# from yahoo.mission.desk_poller import DeskPoller

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class HandRaiseHelper:
    """Monitors for hand raises and navigates to help students."""

    def __init__(self, robot, config, simulate=False):
        self.robot = robot
        self.config = config
        self.desks = sorted(config.desks, key=lambda d: d.id)
        self.gesture_detector = None
        self.simulate = simulate

    def watch_for_hand_raise(self):
        """
        Watch webcam for hand raise gesture.

        Returns:
            True if hand raise detected, False otherwise
        """
        # SIMULATION MODE: Fake gesture detection
        if self.simulate:
            logger.info("\n👀 [SIMULATED] Watching for hand raise...")
            logger.info("   (In real mode, this would use webcam)")
            response = input("\n   Press ENTER to simulate hand raise detected: ")
            logger.info(f"\n🙋 [SIMULATED] HAND RAISE DETECTED!")
            return True

        logger.info("\n👀 Watching for hand raise...")
        logger.info("   Raise your hand in front of webcam to test")
        logger.info("   Press Ctrl+C to stop watching\n")

        try:
            import cv2

            # Initialize gesture detector
            self.gesture_detector = GestureDetector()

            # Open webcam
            cap = cv2.VideoCapture(0)
            if not cap.isOpened():
                logger.error("Could not open webcam")
                return False

            logger.info("✅ Webcam opened - watching for hand raise gesture...")

            while True:
                ret, frame = cap.read()
                if not ret:
                    logger.warning("Failed to read frame")
                    time.sleep(0.1)
                    continue

                # Run gesture detection
                gesture, landmarks = self.gesture_detector.detect(frame)

                # Check for hand raise
                if gesture in ["RIGHT_RAISED", "LEFT_RAISED", "BOTH_RAISED"]:
                    logger.info(f"\n🙋 HAND RAISE DETECTED! ({gesture})")

                    # Visual/audio feedback
                    logger.info("   ✅ Gesture confirmed")
                    cap.release()
                    cv2.destroyAllWindows()
                    return True

                # Show feedback (optional - can comment out)
                # cv2.imshow("Hand Raise Detection", frame)
                # if cv2.waitKey(1) & 0xFF == ord('q'):
                #     break

                time.sleep(0.1)  # Don't overwhelm CPU

        except KeyboardInterrupt:
            logger.info("\n\nStopped watching")
            return False
        except ImportError:
            logger.warning("OpenCV not available - using manual trigger instead")
            response = input("\n👋 Simulate hand raise? Press ENTER when ready...")
            return True
        finally:
            try:
                cap.release()
                cv2.destroyAllWindows()
            except:
                pass

    def get_desk_with_raised_hand(self, manual=True):
        """
        Determine which desk has raised hand.

        Args:
            manual: If True, prompt for desk ID. If False, use automated detection.

        Returns:
            Desk ID (1-4)
        """
        if manual:
            # MANUAL MODE: Prompt operator
            logger.info("\n" + "=" * 60)
            logger.info("📍 DESK IDENTIFICATION")
            logger.info("=" * 60)

            valid_ids = [d.id for d in self.desks]

            while True:
                try:
                    response = input(f"\nWhich desk raised hand? ({', '.join(map(str, valid_ids))}): ").strip()
                    desk_id = int(response)

                    if desk_id not in valid_ids:
                        logger.warning(f"Invalid desk ID. Choose from: {valid_ids}")
                        continue

                    logger.info(f"✅ Desk {desk_id} confirmed")
                    return desk_id

                except ValueError:
                    logger.warning("Invalid input. Enter a number.")
                    continue
                except KeyboardInterrupt:
                    logger.info("\n\nCancelled")
                    return None

        else:
            # FUTURE: AUTOMATED MODE using desk-centric polling
            logger.info("=" * 60)
            logger.info("📍 AUTOMATED DESK SCANNING")
            logger.info("=" * 60)
            logger.info("\nScanning all desks for raised hands...")

            # FUTURE: Uncomment when ready for automated mode
            # poller = DeskPoller(
            #     robot=self.robot,
            #     config=self.config,
            #     camera=None,  # Add camera
            #     simulate=False
            # )
            # raised_hands = poller.scan_for_raised_hands()
            # if raised_hands:
            #     return raised_hands[0]  # Return first detected
            # return None

            raise NotImplementedError(
                "Automated mode not yet implemented. Use manual mode."
            )

    def navigate_to_desk(self, target_desk_id):
        """
        Navigate from current position to target desk.

        Args:
            target_desk_id: Desk ID to navigate to (1-4)
        """
        logger.info(f"\n{'='*60}")
        logger.info(f"NAVIGATING TO DESK {target_desk_id}")
        logger.info(f"{'='*60}")

        # HARDCODED DISTANCES (same as other missions)
        distances = {
            1: 0,    # From start position
            2: 104,  # Desk 1 → Desk 2
            3: 238,  # Desk 2 → Desk 3 (across gap)
            4: 104   # Desk 3 → Desk 4
        }

        # Simple approach: assume starting at Desk 1, navigate to target
        # FUTURE: Track actual position and calculate optimal path

        current_pos = 1  # Assume starting at Desk 1
        distance_to_drive = sum(distances[i] for i in range(current_pos + 1, target_desk_id + 1))

        if distance_to_drive > 1.0:
            logger.info(f"\n🚗 Driving {distance_to_drive} cm to Desk {target_desk_id}...")
            if self.simulate:
                logger.info(f"   [SIMULATED] robot.drive.drive_cm({distance_to_drive})")
            else:
                self.robot.drive.drive_cm(distance_to_drive)
            logger.info(f"✅ Arrived at Desk {target_desk_id}")

        # Turn left to face desk
        logger.info(f"\n↰  Turning LEFT 90° to face Desk {target_desk_id}...")
        if self.simulate:
            logger.info(f"   [SIMULATED] robot.drive.turn_degrees(-90)")
        else:
            self.robot.drive.turn_degrees(-90)
            time.sleep(0.5)

        logger.info(f"\n🎯 AT DESK {target_desk_id} - Ready to assist student")

    def run(self, manual=True, continuous=False):
        """
        Execute hand raise helper.

        Args:
            manual: If True, manually confirm desk. If False, use automated detection.
            continuous: If True, keep watching. If False, handle one request and exit.
        """
        logger.info("=" * 60)
        logger.info("🙋 HAND RAISE HELPER")
        if self.simulate:
            logger.info("⚠️  SIMULATION MODE - No hardware required")
        logger.info("=" * 60)
        logger.info(f"\n✋ PHASE: ON-DEMAND STUDENT ASSISTANCE (Hand Raise)")
        logger.info(f"Goal: Help student who raises hand during work time")
        logger.info(f"\nMode: {'MANUAL' if manual else 'AUTOMATED'}")
        logger.info(f"Continuous: {'Yes' if continuous else 'No (one-time)'}")

        logger.info(f"\n🤖 READY FOR ASSISTANCE")
        logger.info(f"   Position: In front of Desk 1")
        logger.info(f"   Waiting for hand raise gesture...")

        while True:
            # Watch for hand raise
            hand_detected = self.watch_for_hand_raise()

            if not hand_detected:
                if not continuous:
                    logger.info("\nNo hand raise detected. Exiting.")
                    break
                continue

            # Get desk ID
            desk_id = self.get_desk_with_raised_hand(manual=manual)

            if desk_id is None:
                logger.info("\nCancelled. Exiting.")
                break

            # Confirm navigation
            response = input(f"\n⚠️  Navigate to Desk {desk_id}? (y/n): ").strip().lower()

            if response == 'y':
                self.navigate_to_desk(desk_id)

                logger.info("\n✅ Assistance complete")

                if continuous:
                    # Return to start position
                    response = input("\nReturn to start position? (y/n): ").strip().lower()
                    if response == 'y':
                        logger.info("Returning to Desk 1...")
                        # TODO: Navigate back to Desk 1
                        logger.info("(Manual return for now - drive robot back to start)")
                else:
                    break
            else:
                logger.info("Navigation cancelled")
                if not continuous:
                    break

            if continuous:
                logger.info("\n" + "-" * 60)
                logger.info("Ready for next hand raise...")
            else:
                break


def main():
    """Main entry point."""
    import argparse
    parser = argparse.ArgumentParser(
        description='Hand raise helper - on-demand student assistance',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Watch for hand raise, navigate to one desk, exit
  python3 scripts/hand_raise_helper.py

  # Continuous mode - keep helping students
  python3 scripts/hand_raise_helper.py --continuous

  # Future: Automated desk identification
  python3 scripts/hand_raise_helper.py --auto

Setup:
  Position robot in front of Desk 1, facing along the row

How it works:
  1. Webcam watches for hand raise gesture
  2. When detected, prompts: "Which desk raised hand?"
  3. Robot navigates to that desk
  4. Assist student
  5. (Optional) Return to start and repeat
        """
    )
    parser.add_argument('--manual', action='store_true', default=True,
                       help='Manual desk confirmation (default)')
    parser.add_argument('--auto', action='store_true',
                       help='Automated desk detection (future)')
    parser.add_argument('--simulate', action='store_true',
                       help='Run in simulation mode (no hardware required)')
    parser.add_argument('--continuous', action='store_true',
                       help='Keep watching for multiple requests')
    parser.add_argument('--debug', action='store_true',
                       help='Enable debug logging')
    args = parser.parse_args()

    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)

    manual_mode = not args.auto

    logger.info("Initializing robot...")
    try:
        with Robot(simulate=args.simulate) as robot:
            logger.info(f"✅ Robot initialized (simulate={args.simulate})")
            logger.info(f"   Battery: {robot.get_battery_voltage():.2f}V")

            config = load_row_config()
            logger.info(f"✅ Config loaded: {len(config.desks)} desks")

            helper = HandRaiseHelper(robot, config, simulate=args.simulate)
            helper.run(manual=manual_mode, continuous=args.continuous)

    except KeyboardInterrupt:
        logger.warning("\n\nHelper interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"\n\nHelper error: {e}")
        logging.exception("Helper failed")
        sys.exit(1)


if __name__ == "__main__":
    main()
