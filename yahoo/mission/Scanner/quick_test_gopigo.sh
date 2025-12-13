#!/bin/bash
# Quick setup and test script for GoPiGo scanner

echo "🚀 GoPiGo Scanner Quick Setup"
echo "=============================="
echo ""

# Check if we're in the right directory
if [ ! -f "scanner.py" ]; then
    echo "❌ Error: scanner.py not found!"
    echo "Please run this from: ~/yahooRobot/yahoo/mission/scanner"
    exit 1
fi

# Step 1: Install dependencies
echo "📦 Installing dependencies..."
pip3 install -q opencv-python-headless easygopigo3 python-dotenv 2>/dev/null || {
    echo "⚠️  Some packages may already be installed or need sudo"
}
echo "✅ Note: Scanner uses OpenCV VideoCapture - no picamera2 needed"

# Step 2: Setup database
echo ""
echo "💾 Setting up database..."
python3 setup_db.py

# Step 3: Create .env file
echo ""
echo "⚙️  Creating .env file..."
cat > .env << EOF
USE_GOPIGO=true
BRIGHTNESS_THRESHOLD=180
EOF
echo "✅ .env created"

# Step 4: Check camera
echo ""
echo "📷 Checking camera..."
if command -v libcamera-still &> /dev/null; then
    echo "✅ Camera tools available"
else
    echo "⚠️  Camera tools not found. Run: sudo raspi-config → Interface Options → Camera"
fi

# Step 5: Ready to run
echo ""
echo "✅ Setup complete!"
echo ""
echo "🎯 To run the scanner:"
echo "   python3 scanner.py"
echo ""
echo "📋 To view scans:"
echo "   python3 view_scans.py"
echo ""

