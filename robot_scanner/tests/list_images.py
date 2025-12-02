#!/usr/bin/env python3
"""
List all captured images and their locations.
"""
from pathlib import Path
import os

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent

print("📸 Captured Images\n")
print("="*60)

# Check test images
test_dir = script_dir
test_images = list(test_dir.glob("*.jpg")) + list(test_dir.glob("*.png"))

if test_images:
    print(f"\n📁 Test Images ({test_dir.relative_to(project_root)}/):")
    for img in sorted(test_images):
        size = img.stat().st_size / 1024  # KB
        print(f"  ✅ {img.name} ({size:.1f} KB)")
        print(f"     Full path: {img.absolute()}")
else:
    print(f"\n📁 No images in {test_dir.relative_to(project_root)}/")

# Check debug output
debug_dir = test_dir / "debug_output"
if debug_dir.exists():
    debug_images = list(debug_dir.glob("*.jpg")) + list(debug_dir.glob("*.png"))
    if debug_images:
        print(f"\n📁 Debug Images ({debug_dir.relative_to(project_root)}/):")
        for img in sorted(debug_images):
            size = img.stat().st_size / 1024  # KB
            print(f"  🔍 {img.name} ({size:.1f} KB)")
            print(f"     Full path: {img.absolute()}")

# Check project root
root_images = list(project_root.glob("*.jpg")) + list(project_root.glob("*.png"))
if root_images:
    print(f"\n📁 Root Directory Images:")
    for img in sorted(root_images):
        size = img.stat().st_size / 1024  # KB
        print(f"  📄 {img.name} ({size:.1f} KB)")

print("\n" + "="*60)
print("\n💡 To view an image:")
print("   open robot_scanner/tests/captured_paper.jpg")
print("\n💡 To test with an image:")
print("   python3 robot_scanner/run_test.py image")

