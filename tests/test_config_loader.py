#!/usr/bin/env python3
"""
Test script for row configuration loader.
Verifies that desk layout can be loaded and parsed correctly.
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from yahoo.config.row_loader import load_row_config


def test_config_loading():
    """Test that configuration loads without errors."""
    print("\n" + "=" * 60)
    print("Test 1: Loading Configuration")
    print("=" * 60)

    try:
        config = load_row_config()
        print("✅ Configuration loaded successfully")
        return config
    except Exception as e:
        print(f"❌ Failed to load configuration: {e}")
        sys.exit(1)


def test_desk_access():
    """Test accessing individual desks."""
    print("\n" + "=" * 60)
    print("Test 2: Accessing Individual Desks")
    print("=" * 60)

    config = load_row_config()

    for desk_id in [1, 2, 3, 4]:
        try:
            desk = config.get_desk(desk_id)
            print(f"✅ Desk {desk_id}: {desk.name}")
            print(f"   Position: ({desk.x_cm:.1f}, {desk.y_cm:.1f})cm")
            print(f"   Distance from origin: {desk.distance_from_origin():.1f}cm")
            print(f"   Angle from origin: {desk.angle_from_origin():+.1f}°")
        except Exception as e:
            print(f"❌ Failed to get Desk {desk_id}: {e}")
            sys.exit(1)


def test_scan_angles():
    """Test scan angle retrieval."""
    print("\n" + "=" * 60)
    print("Test 3: Scan Angles for Polling")
    print("=" * 60)

    config = load_row_config()

    for desk_id in [1, 2, 3, 4]:
        try:
            angle = config.get_scan_angle(desk_id)
            print(f"✅ Desk {desk_id} scan angle: {angle:+.1f}°")
        except Exception as e:
            print(f"❌ Failed to get scan angle for Desk {desk_id}: {e}")
            sys.exit(1)


def test_origin():
    """Test origin position retrieval."""
    print("\n" + "=" * 60)
    print("Test 4: Origin Position")
    print("=" * 60)

    config = load_row_config()

    try:
        x, y, heading = config.get_origin()
        print(f"✅ Origin position: ({x:.1f}, {y:.1f})cm")
        print(f"   Initial heading: {heading:.1f}°")
    except Exception as e:
        print(f"❌ Failed to get origin: {e}")
        sys.exit(1)


def test_navigation_settings():
    """Test navigation settings retrieval."""
    print("\n" + "=" * 60)
    print("Test 5: Navigation Settings")
    print("=" * 60)

    config = load_row_config()

    try:
        nav = config.get_navigation_settings()
        print(f"✅ Navigation settings loaded:")
        print(f"   Default speed: {nav.get('default_speed_dps', 'N/A')} DPS")
        print(f"   Turn speed: {nav.get('turn_speed_dps', 'N/A')} DPS")
        print(f"   Approach speed: {nav.get('approach_speed_dps', 'N/A')} DPS")
        print(f"   Stop distance: {nav.get('stop_distance_cm', 'N/A')}cm")
    except Exception as e:
        print(f"❌ Failed to get navigation settings: {e}")
        sys.exit(1)


def test_desk_order():
    """Test that desks are in correct order for traversal."""
    print("\n" + "=" * 60)
    print("Test 6: Desk Traversal Order")
    print("=" * 60)

    config = load_row_config()

    print("Expected order: Desk 1 → Desk 2 → Desk 3 → Desk 4")
    print("\nActual order from config:")

    for i, desk in enumerate(config.desks, 1):
        if desk.id != i:
            print(f"❌ Order mismatch: Expected Desk {i}, got Desk {desk.id}")
            sys.exit(1)

    print("✅ Desk order correct: ", end="")
    print(" → ".join([f"Desk {d.id}" for d in config.desks]))


def test_layout_visualization():
    """Visualize the desk layout."""
    print("\n" + "=" * 60)
    print("Test 7: Layout Visualization")
    print("=" * 60)

    config = load_row_config()

    print("\nTop-down view (not to scale):")
    print()
    print("      [D1]        [D2]   GAP   [D3]        [D4]")
    print("    (-227.5)    (-44.5)  |  (+44.5)    (+227.5)")
    print("        ↑           ↑     |     ↑           ↑")
    print("        └───────────┼─────┼─────┼───────────┘")
    print("                    └──→ 🤖 ←──┘")
    print("                      (0, 0)")
    print()

    print("Actual loaded positions:")
    for desk in config.desks:
        marker = "🤖" if desk.x_cm == 0 else "  "
        print(f"  {marker} Desk {desk.id}: ({desk.x_cm:+7.1f}, {desk.y_cm:6.1f})cm")


def print_full_summary():
    """Print full configuration summary."""
    print("\n" + "=" * 60)
    print("Full Configuration Summary")
    print("=" * 60)

    config = load_row_config()
    config.print_summary()


def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("Yahoo Robot - Row Configuration Loader Tests")
    print("=" * 60)

    # Run all tests
    test_config_loading()
    test_desk_access()
    test_scan_angles()
    test_origin()
    test_navigation_settings()
    test_desk_order()
    test_layout_visualization()
    print_full_summary()

    # Final result
    print("\n" + "=" * 60)
    print("✅ ALL TESTS PASSED!")
    print("=" * 60)
    print("\nConfiguration is ready to use.")
    print("\n⚠️  REMINDER: Measure actual desk distance and update config:")
    print("   1. Measure distance from origin to desks (Y-axis)")
    print("   2. Update in row_config.json: 'desk_distance_forward_cm'")
    print("   3. Scan angles will be recalculated automatically")
    print("=" * 60)


if __name__ == "__main__":
    main()
