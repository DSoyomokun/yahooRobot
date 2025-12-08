#!/usr/bin/env python3
"""
Test camera capture with preview and countdown.
Shows live camera feed, countdown, then captures and tests detection.
"""
import cv2
import sys
import time
import argparse
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from yahoo.io.camera import PiCam
from yahoo.mission.scanner.scanner import RobotScanner
from yahoo.mission.mission_controller import MissionController


def countdown(seconds: int = 3):
    """Display countdown."""
    for i in range(seconds, 0, -1):
        print(f"\r⏱️  Capturing in {i}...", end='', flush=True)
        time.sleep(1)
    print("\r✅ CAPTURING NOW!                    ")


def test_mac():
    """Test on Mac with preview."""
    print("\n" + "="*60)
    print("📷 MAC CAMERA TEST")
    print("="*60)
    print("\nInstructions:")
    print("  1. Align your test paper in the camera view")
    print("  2. Wait for the countdown")
    print("  3. Image will be captured and analyzed")
    print("  4. Press 'q' to quit, 'c' to capture manually")
    print("\n" + "-"*60)
    
    # Initialize camera (Mac typically uses device_index=1)
    camera = PiCam(device_index=1, width=1280, height=720, simulate=False)
    
    if camera.cap is None and not camera.simulate:
        print("❌ Failed to open camera. Trying device 0...")
        camera.release()
        camera = PiCam(device_index=0, width=1280, height=720, simulate=False)
        if camera.cap is None:
            print("❌ Camera not available")
            return
    
    print("✅ Camera opened successfully")
    print("📹 Starting preview...\n")
    
    # Initialize scanner
    scanner = RobotScanner()
    
    frame_count = 0
    auto_capture_countdown = None
    auto_capture_triggered = False
    
    try:
        while True:
            frame = camera.capture()
            if frame is None:
                print("⚠️  Failed to read frame")
                time.sleep(0.1)
                continue
            
            frame_count += 1
            
            # Create display frame
            display_frame = frame.copy()
            h, w = display_frame.shape[:2]
            
            # Add instructions overlay
            cv2.putText(display_frame, "Press 'c' to capture, 'q' to quit", 
                       (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            
            # Add countdown overlay if active
            if auto_capture_countdown is not None:
                remaining = int(auto_capture_countdown - time.time())
                if remaining > 0:
                    cv2.putText(display_frame, f"Capturing in {remaining}...", 
                               (w//2 - 150, h//2), cv2.FONT_HERSHEY_SIMPLEX, 
                               1.5, (0, 0, 255), 3)
                    cv2.circle(display_frame, (w//2, h//2), 100, (0, 0, 255), 3)
                else:
                    # Time to capture!
                    auto_capture_countdown = None
                    auto_capture_triggered = True
            
            # Show frame
            cv2.imshow("Camera Preview - Press 'c' to capture, 'q' to quit", display_frame)
            
            # Handle auto-capture
            if auto_capture_triggered:
                auto_capture_triggered = False
                print("\n📸 Auto-capturing...")
                process_capture(frame, scanner, camera_index=1)
            
            # Handle keyboard input
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('c'):
                print("\n📸 Manual capture triggered...")
                process_capture(frame, scanner, camera_index=1)
            elif key == ord('a'):
                # Auto-capture with countdown
                if auto_capture_countdown is None:
                    print("\n⏱️  Starting 3-second countdown...")
                    auto_capture_countdown = time.time() + 3
            
            # Small delay to prevent high CPU usage
            time.sleep(0.03)
            
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
    finally:
        camera.release()
        cv2.destroyAllWindows()
        print("\n✅ Camera released")


def test_pi():
    """Test on Raspberry Pi (simplified, no preview window)."""
    print("\n" + "="*60)
    print("📷 RASPBERRY PI CAMERA TEST")
    print("="*60)
    print("\nNote: On Pi, we'll capture without preview window")
    print("      (X11 forwarding may be slow)")
    print("\n" + "-"*60)
    
    # Initialize camera (Pi typically uses device_index=0)
    camera = PiCam(device_index=0, width=1280, height=720, simulate=False)
    
    if camera.cap is None and not camera.simulate:
        print("❌ Failed to open camera")
        return
    
    print("✅ Camera opened successfully")
    
    # Initialize scanner
    scanner = RobotScanner()
    
    # Countdown
    print("\n⏱️  Starting countdown...")
    countdown(3)
    
    # Capture
    print("📸 Capturing image...")
    frame = camera.capture()
    
    if frame is None:
        print("❌ Failed to capture frame")
        camera.release()
        return
    
    # Process
    process_capture(frame, scanner, camera_index=0)
    
    camera.release()
    print("\n✅ Test complete")


def process_capture(frame, scanner, camera_index: int = 0):
    """Process a captured frame with detailed visualization."""
    # Create organized folder structure
    base_dir = Path(__file__).parent / "captured_images"
    raw_dir = base_dir / "raw_captured"
    vis_dir = base_dir / "detection_visualization"
    
    raw_dir.mkdir(parents=True, exist_ok=True)
    vis_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    
    # Save raw captured image
    raw_image_path = raw_dir / f"capture_{timestamp}.jpg"
    cv2.imwrite(str(raw_image_path), frame)
    print(f"💾 Raw capture saved to: {raw_image_path}")
    
    # Test paper detection
    print("\n" + "="*60)
    print("🔍 PAPER DETECTION")
    print("="*60)
    try:
        from yahoo.mission.mission_controller import MissionController
        controller = MissionController(camera_index=camera_index, simulate=True)
        paper_detected = controller.paper_detected(frame)
        
        if paper_detected:
            print("✅ Paper detected in frame!")
        else:
            print("⚠️  Paper not detected (may still work for scanning)")
    except Exception as e:
        print(f"⚠️  Paper detection test failed: {e}")
    
    # Test name extraction (handwriting detection)
    print("\n" + "="*60)
    print("✍️  HANDWRITING / NAME DETECTION")
    print("="*60)
    try:
        from yahoo.mission.scanner.name_reader import NameReader
        name_reader = NameReader()
        
        # Extract name region
        name_region = name_reader.extract_name_region(frame)
        if name_region.size > 0:
            # Save name region to detection_visualization folder
            name_region_path = vis_dir / f"name_region_{timestamp}.jpg"
            cv2.imwrite(str(name_region_path), name_region)
            print(f"📝 Name region extracted and saved to: {name_region_path}")
            
            # Extract name
            student_name = name_reader.extract_name(frame)
            if student_name:
                print(f"✅ Name extracted: '{student_name}'")
            else:
                print("⚠️  No name extracted (may be empty or unclear)")
        else:
            print("❌ Failed to extract name region")
    except Exception as e:
        print(f"❌ Name extraction error: {e}")
        import traceback
        traceback.print_exc()
    
    # Test bubble detection
    print("\n" + "="*60)
    print("⭕ BUBBLE DETECTION")
    print("="*60)
    try:
        from yahoo.mission.scanner.bubble_detector import BubbleDetector
        bubble_detector = BubbleDetector()
        
        # Preprocess
        processed = bubble_detector.preprocess(frame)
        bubbles = bubble_detector.detect_bubbles(processed)
        
        print(f"📊 Total bubbles detected: {len(bubbles)}")
        
        if bubbles:
            # Get grayscale for fill calculation
            if len(frame.shape) == 3:
                gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            else:
                gray_frame = frame
            
            # Group by question
            question_groups = bubble_detector.group_by_question(bubbles, num_choices=4)
            print(f"📋 Questions found: {len(question_groups)}")
            
            # Show first few questions
            print("\n📝 Bubble details (first 5 questions):")
            for q_num in sorted(question_groups.keys())[:5]:
                q_bubbles = question_groups[q_num]
                print(f"\n  Question {q_num}:")
                for i, bubble in enumerate(q_bubbles[:4]):
                    fill = bubble_detector.calculate_fill(gray_frame, bubble)
                    letter = chr(ord('A') + i)
                    marked = "✅ MARKED" if fill >= bubble_detector.fill_threshold else "⭕ empty"
                    print(f"    {letter}: {fill:.1%} fill - {marked}")
            
            # Create visualization
            vis_frame = frame.copy()
            for bubble in bubbles[:50]:  # Limit to 50 for display
                x, y, w, h = bubble['bounding_rect']
                fill = bubble_detector.calculate_fill(gray_frame, bubble)
                color = (0, 255, 0) if fill >= bubble_detector.fill_threshold else (0, 0, 255)
                cv2.rectangle(vis_frame, (x, y), (x+w, y+h), color, 2)
                cv2.putText(vis_frame, f"{fill:.0%}", (x, y-5), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.4, color, 1)
            
            # Draw name region
            h, w = frame.shape[:2]
            name_top = int(h * 0.05)
            name_bottom = int(h * 0.15)
            name_left = int(w * 0.10)
            name_right = int(w * 0.50)
            cv2.rectangle(vis_frame, (name_left, name_top), (name_right, name_bottom), (255, 255, 0), 3)
            cv2.putText(vis_frame, "NAME REGION", (name_left, name_top - 10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
            
            # Save visualization to detection_visualization folder
            vis_path = vis_dir / f"bubble_detection_{timestamp}.jpg"
            cv2.imwrite(str(vis_path), vis_frame)
            print(f"\n🎨 Bubble detection visualization saved to: {vis_path}")
            print("   - Green boxes = Marked bubbles")
            print("   - Red boxes = Empty bubbles")
            print("   - Yellow box = Name region")
        else:
            print("❌ No bubbles detected")
    except Exception as e:
        print(f"❌ Bubble detection error: {e}")
        import traceback
        traceback.print_exc()
    
    # Test full scanning pipeline
    print("\n" + "="*60)
    print("📝 FULL SCAN RESULTS")
    print("="*60)
    try:
        result = scanner.scan_image(frame, store=False)
        
        if result:
            print("\n✅ SCAN SUCCESSFUL!")
            print(f"\n👤 Student Name: {result.get('student_name', 'Unknown')}")
            print(f"\n📊 Score: {result.get('score', 0)}/{result.get('total_questions', 0)}")
            print(f"   Percentage: {result.get('percentage', 0):.1f}%")
            print(f"   ✅ Correct: {result.get('correct', 0)}")
            print(f"   ❌ Incorrect: {result.get('incorrect', 0)}")
            print(f"   ⚪ Unanswered: {result.get('unanswered', 0)}")
            
            # Show answers
            answers = result.get('answers', {})
            if answers:
                print(f"\n📝 Detected Answers:")
                # Group answers for better display
                answer_list = []
                for q_num in sorted(answers.keys(), key=int):
                    answer = answers[q_num]
                    if answer:
                        answer_list.append(f"Q{q_num}: {answer}")
                    else:
                        answer_list.append(f"Q{q_num}: (unanswered)")
                
                # Print in columns
                for i in range(0, len(answer_list), 5):
                    print("   " + "  ".join(answer_list[i:i+5]))
            
            # Save results summary to detection_visualization folder (processed results)
            summary_path = vis_dir / f"scan_results_{timestamp}.txt"
            with open(summary_path, 'w') as f:
                f.write("SCAN RESULTS\n")
                f.write("="*60 + "\n\n")
                f.write(f"Student Name: {result.get('student_name', 'Unknown')}\n")
                f.write(f"Score: {result.get('score', 0)}/{result.get('total_questions', 0)}\n")
                f.write(f"Percentage: {result.get('percentage', 0):.1f}%\n")
                f.write(f"Correct: {result.get('correct', 0)}\n")
                f.write(f"Incorrect: {result.get('incorrect', 0)}\n")
                f.write(f"Unanswered: {result.get('unanswered', 0)}\n\n")
                f.write("Answers:\n")
                for q_num in sorted(answers.keys(), key=int):
                    f.write(f"  Q{q_num}: {answers.get(q_num, 'unanswered')}\n")
            print(f"\n💾 Results summary saved to: {summary_path}")
            
            # Also save a processed image ready for grading/storage
            processed_image_path = vis_dir / f"processed_{timestamp}.jpg"
            cv2.imwrite(str(processed_image_path), frame)
            print(f"📄 Processed image saved to: {processed_image_path} (ready for auto-grade/storage)")
        else:
            print("❌ Scan failed - no results returned")
    except Exception as e:
        print(f"❌ Scan error: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "="*60)
    print("✅ PROCESSING COMPLETE")
    print("="*60)
    print(f"\n📁 Folder Structure:")
    print(f"   📂 {base_dir}/")
    print(f"      📁 raw_captured/")
    print(f"         └─ capture_{timestamp}.jpg (original capture)")
    print(f"      📁 detection_visualization/ (processed for auto-grade/storage)")
    print(f"         ├─ name_region_{timestamp}.jpg")
    print(f"         ├─ bubble_detection_{timestamp}.jpg")
    print(f"         ├─ processed_{timestamp}.jpg (ready for grading)")
    print(f"         └─ scan_results_{timestamp}.txt")
    print(f"\n💡 The detection_visualization folder contains processed images")
    print(f"   ready for auto-grading and storage.")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Test camera capture with preview and countdown',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Test on Mac (interactive)
  python test_capture_with_preview.py --mac
  
  # Test on Pi (countdown only)
  python test_capture_with_preview.py --pi
  
  # Auto-detect platform
  python test_capture_with_preview.py
        """
    )
    
    parser.add_argument('--mac', action='store_true', 
                       help='Test on Mac (with preview window)')
    parser.add_argument('--pi', action='store_true',
                       help='Test on Raspberry Pi (no preview)')
    parser.add_argument('--device', type=int, default=None,
                       help='Camera device index (0 or 1, auto-detect if not specified)')
    
    args = parser.parse_args()
    
    # If no platform specified, ask user
    if not args.mac and not args.pi:
        print("\n" + "="*60)
        print("📷 CAMERA CAPTURE TEST")
        print("="*60)
        print("\nSelect platform:")
        print("  1. Mac (with preview window)")
        print("  2. Raspberry Pi (no preview)")
        
        try:
            choice = input("\nEnter choice (1 or 2): ").strip()
            if choice == '1':
                args.mac = True
            elif choice == '2':
                args.pi = True
            else:
                print("❌ Invalid choice, defaulting to Mac")
                args.mac = True
        except (EOFError, KeyboardInterrupt):
            print("\n❌ Cancelled")
            return 1
    
    # Run appropriate test
    if args.mac:
        test_mac()
    elif args.pi:
        test_pi()
    
    return 0


if __name__ == "__main__":
    sys.exit(main())

