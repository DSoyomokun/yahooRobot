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
from yahoo.mission.scanner import ScanControl
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
    
    # Initialize camera - try multiple indices to find Continuity Camera
    # Continuity Camera might be on index 1, 2, or 3
    camera = None
    for device_idx in [1, 2, 3, 0]:
        print(f"🔍 Trying camera device {device_idx}...")
        test_camera = PiCam(device_index=device_idx, width=1280, height=720, simulate=False)
        if test_camera.cap is not None:
            # Test if we can read a frame
            test_frame = test_camera.capture()
            if test_frame is not None:
                camera = test_camera
                print(f"✅ Found working camera at device {device_idx}")
                break
            else:
                test_camera.release()
    
    if camera is None:
        print("❌ No working camera found")
        return
    
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
    scanner = ScanControl()
    
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
                show_results = process_capture(frame, scanner, camera_index=1)
                if show_results:
                    # Close camera preview temporarily
                    cv2.destroyAllWindows()
                    # Don't display images automatically - just save them
                    print("\n" + "-"*60)
                    print("✅ Analysis complete! Images saved to detection_visualization folder")
                    print("📸 Camera preview will resume - Press 'c' to capture again, 'q' to quit")
                    print("💡 View images in: yahoo/mission/scanner/tests/captured_images/detection_visualization/")
                    time.sleep(2)
            
            # Handle keyboard input
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('c'):
                print("\n📸 Manual capture triggered...")
                show_results = process_capture(frame, scanner, camera_index=1)
                if show_results:
                    # Close camera preview temporarily
                    cv2.destroyAllWindows()
                    # Don't display images automatically - just save them
                    print("\n" + "-"*60)
                    print("✅ Analysis complete! Images saved to detection_visualization folder")
                    print("📸 Camera preview will resume - Press 'c' to capture again, 'q' to quit")
                    print("💡 View images in: yahoo/mission/scanner/tests/captured_images/detection_visualization/")
                    time.sleep(2)
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
    scanner = ScanControl()
    
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


def display_capture_results(results, timeout_ms=5000):
    """Display captured images and analysis results.
    
    Args:
        results: Dictionary with image results
        timeout_ms: Timeout in milliseconds for each window (default: 5 seconds)
    """
    if not results:
        return
    
    print("\n" + "="*60)
    print("🖼️  DISPLAYING CAPTURED IMAGES")
    print("="*60)
    print(f"\nPress any key in each window to continue (or wait {timeout_ms//1000}s to auto-advance)...")
    print("Press 'q' to skip remaining images.\n")
    
    def resize_for_display(img, max_width=1280):
        """Resize image for display if too large."""
        if img is None or img.size == 0:
            return None
        if img.shape[1] > max_width:
            scale = max_width / img.shape[1]
            new_w = int(img.shape[1] * scale)
            new_h = int(img.shape[0] * scale)
            return cv2.resize(img, (new_w, new_h))
        return img
    
    images_to_show = [
        ('raw_image', "1. Raw Captured Image", None),
        ('aligned_image', "2. Aligned Form", None),
        ('name_region', "3. Name Region (for OCR)", 800),
        ('detection_vis', "4. Detection Visualization", None),
        ('bubble_analysis', "5. Bubble Analysis (Green=Filled)", None),
    ]
    
    for key, title, max_width in images_to_show:
        if key in results and results[key] is not None:
            print(f"📸 Showing: {title}")
            display = resize_for_display(results[key], max_width=max_width or 1280)
            if display is not None:
                cv2.imshow(title, display)
                # Wait for key press or timeout
                key_pressed = cv2.waitKey(timeout_ms) & 0xFF
                if key_pressed == ord('q'):
                    print("⏭️  Skipping remaining images...")
                    break
                elif key_pressed == 255:  # Timeout
                    print(f"⏱️  Auto-advancing after {timeout_ms//1000}s...")
            else:
                print(f"⚠️  Could not display {title}")
    
    cv2.destroyAllWindows()
    print("\n✅ All images displayed!")


def process_capture(frame, scanner, camera_index: int = 0):
    """Process a captured frame with detailed visualization.
    Returns dict with images and paths for display."""
    def _align_for_visualization(image):
        """Match the main pipeline alignment (rotate landscape + perspective)."""
        from yahoo.mission.scanner.alignment.aligner import align_form, align_form_simple

        img = image.copy()
        h, w = img.shape[:2]

        # Scan pipeline rotates to portrait first; mirror that so ROIs line up.
        if w > h:
            img = cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE)

        aligned = align_form(img)
        if aligned is None:
            aligned = align_form_simple(img)
        return aligned

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
    
    # Prepare results dict for display
    results = {
        'raw_image': frame.copy(),
        'timestamp': timestamp,
        'paths': {}
    }
    
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
    
    # Test full scanning pipeline (includes name and bubble detection)
    print("\n" + "="*60)
    print("📝 FULL SCAN RESULTS")
    print("="*60)
    try:
        print("⏳ Processing image (this may take a moment)...")
        print("   Step 1: Aligning form...")
        import sys
        sys.stdout.flush()
        
        result = scanner.process_test(image=frame, store=False)
        print("✅ Processing complete!")
        
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
        
        # Generate analysis images for display
        print("\n⏳ Generating analysis images...")
        try:
            from yahoo.mission.scanner.alignment.aligner import align_form_simple
            from yahoo.mission.scanner.alignment.roi_extractor import extract_name_roi, extract_bubble_roi
            from yahoo.mission.scanner.config.roi_config import get_bubble_coords, get_name_roi_coords, NUM_QUESTIONS
            from yahoo.mission.scanner.bubbles.bubble_detector import BubbleDetector
            
            # Align image
            print("   - Aligning image...")
            aligned = _align_for_visualization(frame)
            results['aligned_image'] = aligned.copy()
            
            # Extract name region
            print("   - Extracting name region...")
            name_roi = extract_name_roi(aligned)
            results['name_region'] = name_roi.copy() if name_roi.size > 0 else None
            
            # Create detection visualization
            print("   - Creating bubble detection visualization...")
            h, w = aligned.shape[:2]
            vis = aligned.copy()
            
            # Draw name region
            name_top, name_bottom, name_left, name_right = get_name_roi_coords(w, h)
            cv2.rectangle(vis, (name_left, name_top), (name_right, name_bottom), (0, 255, 0), 3)
            cv2.putText(vis, "NAME REGION", (name_left, name_top - 10), 
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            
            # Draw bubbles
            detector = BubbleDetector()
            for q_num in range(1, NUM_QUESTIONS + 1):
                for choice_idx, letter in enumerate(['A', 'B', 'C', 'D']):
                    center_x, center_y, radius = get_bubble_coords(q_num, choice_idx, w, h)
                    bubble_roi = extract_bubble_roi(aligned, q_num, choice_idx)
                    fill_ratio = detector.detect_fill(bubble_roi)
                    is_filled = fill_ratio >= detector.fill_threshold
                    
                    color = (0, 255, 0) if is_filled else (100, 100, 100)
                    thickness = 4 if is_filled else 2
                    cv2.circle(vis, (center_x, center_y), radius + 3, color, thickness)
                    
                    label = f"{letter}:{fill_ratio:.0%}"
                    cv2.putText(vis, label, (center_x - 15, center_y - radius - 5),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.3, color, 1)
            
            results['detection_vis'] = vis.copy()
            results['bubble_analysis'] = vis.copy()  # Same for now
            
            # Save all analysis images to detection_visualization folder
            print("   - Saving analysis images...")
            
            # Save aligned form
            aligned_path = vis_dir / f"02_aligned_form_{timestamp}.jpg"
            cv2.imwrite(str(aligned_path), aligned)
            results['paths']['aligned'] = aligned_path
            print(f"      ✅ Aligned form: {aligned_path.name}")
            
            # Save name region
            if results['name_region'] is not None and results['name_region'].size > 0:
                name_path = vis_dir / f"03_name_region_{timestamp}.jpg"
                cv2.imwrite(str(name_path), results['name_region'])
                results['paths']['name_region'] = name_path
                print(f"      ✅ Name region: {name_path.name}")
            
            # Save detection visualization
            vis_path = vis_dir / f"04_detection_visualization_{timestamp}.jpg"
            cv2.imwrite(str(vis_path), vis)
            results['paths']['detection_vis'] = vis_path
            print(f"      ✅ Detection visualization: {vis_path.name}")
            
            # Save bubble analysis
            bubble_path = vis_dir / f"05_bubble_analysis_{timestamp}.jpg"
            cv2.imwrite(str(bubble_path), vis)
            results['paths']['bubble_analysis'] = bubble_path
            print(f"      ✅ Bubble analysis: {bubble_path.name}")
            
            print("✅ Analysis images generated and saved!")
        except Exception as e:
            print(f"⚠️  Could not generate analysis images: {e}")
            import traceback
            traceback.print_exc()
        
        if not result:
            print("❌ Scan failed - no results returned")
    except Exception as e:
        print(f"❌ Scan error: {e}")
        import traceback
        traceback.print_exc()
        result = None
    
    # Display results if we have them
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
            
            # Also save raw captured image to visualization folder for reference
            raw_vis_path = vis_dir / f"01_raw_captured_{timestamp}.jpg"
            cv2.imwrite(str(raw_vis_path), frame)
            results['paths']['raw'] = raw_vis_path
            print(f"📄 Raw captured image saved to: {raw_vis_path.name}")
    
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
    
    return results


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
