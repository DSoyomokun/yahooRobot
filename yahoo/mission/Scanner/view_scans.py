#!/usr/bin/env python3
"""
View or transfer scanned images
Options: list scans, transfer to Mac, or view on Pi (if X11 available)
"""
import sys
from pathlib import Path
import os

# Add project root to path
_script_dir = Path(__file__).parent.resolve()
_project_root = _script_dir.parent.parent.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

scans_dir = _script_dir / "scans"

def list_scans():
    """List all scan files."""
    if not scans_dir.exists():
        print(f"❌ Scans directory not found: {scans_dir}")
        return []
    
    jpg_files = sorted(scans_dir.glob("*.jpg"))
    return jpg_files

def main():
    print("=" * 70)
    print("📸 SCANNED IMAGES")
    print("=" * 70)
    print()
    
    scans = list_scans()
    
    if not scans:
        print("⚠️  No scan images found")
        print(f"   Directory: {scans_dir}")
        return
    
    print(f"📁 Found {len(scans)} scan(s) in: {scans_dir}")
    print()
    
    # List all scans
    print("Scanned images:")
    print("-" * 70)
    for i, scan_file in enumerate(scans, 1):
        size = scan_file.stat().st_size
        size_kb = size / 1024
        print(f"  {i}. {scan_file.name} ({size_kb:.1f} KB)")
    print()
    
    # Instructions for viewing
    print("=" * 70)
    print("📥 HOW TO VIEW IMAGES")
    print("=" * 70)
    print()
    
    print("Option 1: Transfer to Mac (Recommended)")
    print("-" * 70)
    print("From your Mac terminal (while on GoPiGo WiFi):")
    print()
    print("  # Transfer all scans to your Mac")
    print(f"  scp pi@10.10.10.10:~/yahooRobot/yahoo/mission/scanner/scans/*.jpg ~/Desktop/scans/")
    print()
    print("  # Or transfer specific file")
    print(f"  scp pi@10.10.10.10:~/yahooRobot/yahoo/mission/scanner/scans/scan_0001.jpg ~/Desktop/")
    print()
    print("  # Create directory first if needed")
    print("  mkdir -p ~/Desktop/scans")
    print()
    
    print("Option 2: View on Pi (requires X11 forwarding)")
    print("-" * 70)
    print("From your Mac:")
    print("  1. Use: robopi_x  (SSH with X11 forwarding)")
    print("  2. Install image viewer: sudo apt-get install feh")
    print("  3. View: feh scans/scan_0001.jpg")
    print()
    
    print("Option 3: Quick file info")
    print("-" * 70)
    print("  # Check file sizes")
    print(f"  ls -lh {scans_dir}/")
    print()
    print("  # View latest scan info")
    if scans:
        latest = scans[-1]
        print(f"  file {latest}")
        print(f"  ls -lh {latest}")
    print()
    
    print("=" * 70)
    print(f"✅ Total scans: {len(scans)}")
    print("=" * 70)

if __name__ == "__main__":
    main()
