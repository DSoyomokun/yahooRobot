#!/usr/bin/env python3
"""
Robot Scanner - Quick Test Runner (Python version)
Cross-platform test script for easy testing
"""
import sys
import os
from pathlib import Path

# Add project root to path
script_dir = Path(__file__).parent
project_root = script_dir.parent
sys.path.insert(0, str(project_root))

def print_header(text):
    """Print colored header."""
    print(f"\n{'='*60}")
    print(f"🤖 {text}")
    print('='*60)

def test_camera():
    """Test with camera."""
    print_header("Testing with Camera")
    print("Place your test paper in front of the camera...")
    
    from robot_scanner.tests.test_mac import test_with_camera
    return test_with_camera()

def quick_capture():
    """Quick capture."""
    print_header("Quick Capture")
    print("Capturing image in 2 seconds...")
    
    from robot_scanner.tests.test_mac import quick_capture
    return quick_capture()

def test_image(image_path=None):
    """Test with image."""
    if image_path is None:
        # Check for captured images
        captured = script_dir / "tests" / "captured_paper.jpg"
        if captured.exists():
            print(f"Found captured image: {captured}")
            use = input("Use this image? [y/n]: ").lower()
            if use == 'y':
                image_path = str(captured)
        
        if image_path is None:
            image_path = input("Enter image path: ").strip()
    
    print_header(f"Testing with Image: {image_path}")
    
    from robot_scanner.tests.test_mac import test_with_image
    return test_with_image(image_path)

def debug_scan():
    """Debug visualization."""
    print_header("Debug Visualization")
    print("This will show what the scanner detects...")
    
    from robot_scanner.tests.debug_scanner import debug_scan
    from robot_scanner import capture_image
    from pathlib import Path
    
    debug_dir = script_dir / "tests" / "debug_output"
    debug_dir.mkdir(exist_ok=True)
    
    image_path = capture_image(save_path=str(debug_dir / "capture.jpg"))
    print(f"📸 Captured: {image_path}")
    return debug_scan(image_path)

def view_database():
    """View database results."""
    print_header("Database Results")
    
    db_path = script_dir / "test_results.db"
    if not db_path.exists():
        print("⚠️  Database not found. Run a test first.")
        return
    
    try:
        import sqlite3
        
        conn = sqlite3.connect(str(db_path))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM test_results ORDER BY scanned_at DESC LIMIT 10")
        rows = cursor.fetchall()
        
        if rows:
            print(f"\n📋 Last {len(rows)} Results:\n")
            for i, row in enumerate(rows, 1):
                print(f"{i}. Student: {row['student_name']}")
                print(f"   Score: {row['score']:.0f}/{row['total_questions']} ({row['percentage']:.1f}%)")
                print(f"   Correct: {row['correct']}, Incorrect: {row['incorrect']}, Unanswered: {row['unanswered']}")
                print(f"   Scanned: {row['scanned_at']}")
                print("-" * 50)
        else:
            print("No results found in database.")
        
        conn.close()
    except Exception as e:
        print(f"❌ Error reading database: {e}")

def run_all():
    """Run all tests."""
    print_header("Running All Tests")
    
    print("\n1️⃣ Quick capture...")
    quick_capture()
    
    print("\n2️⃣ Testing with captured image...")
    captured = script_dir / "tests" / "captured_paper.jpg"
    if captured.exists():
        test_with_image(str(captured))
    
    print("\n3️⃣ Viewing results...")
    view_database()

def show_menu():
    """Show interactive menu."""
    print("\n" + "="*60)
    print("🤖 Robot Scanner - Test Runner")
    print("="*60)
    print("\nChoose a test option:")
    print("  1) Test with camera (live capture)")
    print("  2) Quick capture (save image only)")
    print("  3) Test with saved image")
    print("  4) Debug visualization (see what's detected)")
    print("  5) View database results")
    print("  6) Run all tests")
    print("  0) Exit")
    print()

def main():
    """Main function."""
    if len(sys.argv) > 1:
        # Command line mode
        command = sys.argv[1].lower()
        
        if command == "camera":
            test_camera()
        elif command == "capture":
            quick_capture()
        elif command == "image":
            image_path = sys.argv[2] if len(sys.argv) > 2 else None
            test_image(image_path)
        elif command == "debug":
            debug_scan()
        elif command == "db" or command == "database":
            view_database()
        elif command == "all":
            run_all()
        else:
            print("Usage: python3 robot_scanner/run_test.py [command]")
            print("\nCommands:")
            print("  camera    - Test with camera")
            print("  capture   - Quick capture")
            print("  image     - Test with image (optional: path)")
            print("  debug     - Debug visualization")
            print("  db        - View database")
            print("  all       - Run all tests")
            print("\nOr run without arguments for interactive menu")
            sys.exit(1)
    else:
        # Interactive mode
        while True:
            show_menu()
            try:
                choice = input("Enter choice [0-6]: ").strip()
                
                if choice == "1":
                    test_camera()
                elif choice == "2":
                    quick_capture()
                elif choice == "3":
                    test_image()
                elif choice == "4":
                    debug_scan()
                elif choice == "5":
                    view_database()
                elif choice == "6":
                    run_all()
                elif choice == "0":
                    print("\n👋 Goodbye!")
                    break
                else:
                    print("❌ Invalid option")
                
                if choice != "0":
                    input("\nPress Enter to continue...")
            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}")
                import traceback
                traceback.print_exc()
                input("\nPress Enter to continue...")

if __name__ == "__main__":
    main()

