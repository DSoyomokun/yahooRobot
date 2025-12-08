#!/bin/bash

# Robot Scanner - Quick Test Script
# Makes testing easy on Mac

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"

cd "$PROJECT_ROOT"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}🤖 Robot Scanner - Test Runner${NC}"
echo "=================================="
echo ""

# Check if python3 is available
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ python3 not found. Please install Python 3.${NC}"
    exit 1
fi

# Function to show menu
show_menu() {
    echo -e "${YELLOW}Choose a test option:${NC}"
    echo ""
    echo "  1) Test with camera (live capture)"
    echo "  2) Quick capture (save image only)"
    echo "  3) Test with saved image"
    echo "  4) Debug visualization (see what's detected)"
    echo "  5) View database results"
    echo "  6) Run all tests"
    echo "  0) Exit"
    echo ""
    read -p "Enter choice [0-6]: " choice
}

# Test with camera
test_camera() {
    echo -e "\n${GREEN}📸 Testing with camera...${NC}"
    python3 yahoo/mission/scanner/tests/test_mac.py --camera
}

# Quick capture
quick_capture() {
    echo -e "\n${GREEN}📸 Quick capture...${NC}"
    python3 yahoo/mission/scanner/tests/test_mac.py --capture
    echo -e "\n${BLUE}💡 Image saved! Test it with option 3.${NC}"
}

# Test with image
test_image() {
    echo -e "\n${GREEN}🖼️  Testing with image...${NC}"
    
    # Check for captured images
    if [ -f "yahoo/mission/scanner/tests/captured_paper.jpg" ]; then
        echo "Found: yahoo/mission/scanner/tests/captured_paper.jpg"
        read -p "Use this image? [y/n]: " use_captured
        if [ "$use_captured" = "y" ]; then
            python3 yahoo/mission/scanner/tests/test_mac.py --image yahoo/mission/scanner/tests/captured_paper.jpg
            return
        fi
    fi
    
    read -p "Enter image path: " image_path
    if [ -f "$image_path" ]; then
        python3 yahoo/mission/scanner/tests/test_mac.py --image "$image_path"
    else
        echo -e "${RED}❌ Image not found: $image_path${NC}"
    fi
}

# Debug visualization
debug_scan() {
    echo -e "\n${GREEN}🔍 Debug visualization...${NC}"
    python3 yahoo/mission/scanner/tests/debug_scanner.py --camera
    echo -e "\n${BLUE}💡 Check yahoo/mission/scanner/tests/debug_output/ for visualization images${NC}"
}

# View database
view_database() {
    echo -e "\n${GREEN}📊 Viewing database results...${NC}"
    
    if [ -f "yahoo/mission/scanner/test_results.db" ]; then
        python3 -c "
import sqlite3
import json
from datetime import datetime

conn = sqlite3.connect('yahoo/mission/scanner/test_results.db')
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

cursor.execute('SELECT * FROM test_results ORDER BY scanned_at DESC LIMIT 10')
rows = cursor.fetchall()

if rows:
    print(f'\n📋 Last {len(rows)} Results:\n')
    for row in rows:
        print(f\"Student: {row['student_name']}\")
        print(f\"Score: {row['score']:.0f}/{row['total_questions']} ({row['percentage']:.1f}%)\")
        print(f\"Scanned: {row['scanned_at']}\")
        print('-' * 50)
else:
    print('No results found in database.')
"
    else
        echo -e "${YELLOW}⚠️  Database not found. Run a test first.${NC}"
    fi
}

# Run all tests
run_all() {
    echo -e "\n${GREEN}🚀 Running all tests...${NC}\n"
    
    echo "1. Quick capture..."
    quick_capture
    
    echo -e "\n2. Testing with captured image..."
    if [ -f "yahoo/mission/scanner/tests/captured_paper.jpg" ]; then
        python3 yahoo/mission/scanner/tests/test_mac.py --image yahoo/mission/scanner/tests/captured_paper.jpg
    fi
    
    echo -e "\n3. Viewing results..."
    view_database
}

# Main loop
if [ $# -eq 0 ]; then
    # Interactive mode
    while true; do
        show_menu
        case $choice in
            1) test_camera ;;
            2) quick_capture ;;
            3) test_image ;;
            4) debug_scan ;;
            5) view_database ;;
            6) run_all ;;
            0) echo -e "${BLUE}👋 Goodbye!${NC}"; exit 0 ;;
            *) echo -e "${RED}Invalid option${NC}" ;;
        esac
        echo ""
        read -p "Press Enter to continue..."
        echo ""
    done
else
    # Command line mode
    case $1 in
        camera) test_camera ;;
        capture) quick_capture ;;
        image) test_image ;;
        debug) debug_scan ;;
        db|database) view_database ;;
        all) run_all ;;
        *) 
            echo "Usage: $0 [camera|capture|image|debug|db|all]"
            echo ""
            echo "Examples:"
            echo "  $0 camera    # Test with camera"
            echo "  $0 capture   # Quick capture"
            echo "  $0 image     # Test with image"
            echo "  $0 debug     # Debug visualization"
            echo "  $0 db        # View database"
            echo "  $0 all       # Run all tests"
            echo ""
            echo "Or run without arguments for interactive menu"
            exit 1
            ;;
    esac
fi

