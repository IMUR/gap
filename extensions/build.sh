#!/bin/bash
# Build script for GAP browser extensions

set -e

echo "🔧 GAP Extension Builder"
echo "========================"

# Check if we're in the right directory
if [ ! -f "../pyproject.toml" ]; then
    echo "❌ Please run this script from the extensions/ directory"
    exit 1
fi

# Function to build Chrome extension
build_chrome() {
    echo "📦 Building Chrome extension..."

    cd chrome

    # Check for required files
    if [ ! -f "manifest.json" ]; then
        echo "❌ manifest.json not found"
        exit 1
    fi

    # Check for icons
    if [ ! -f "icons/icon128.png" ]; then
        echo "⚠️  Warning: Icons not found. Generate them using icons/icon.html"
    fi

    # Create build directory
    mkdir -p ../../build

    # Create zip file
    zip -r ../../build/gap-chrome-extension.zip . \
        -x "*.md" \
        -x "*.sh" \
        -x "icons/*.html" \
        -x "icons/*.svg" \
        -x ".DS_Store" \
        -x "*.git*"

    cd ..

    echo "✅ Chrome extension built: build/gap-chrome-extension.zip"
}

# Function to build Firefox extension (future)
build_firefox() {
    echo "🦊 Firefox extension not yet implemented"
}

# Parse arguments
if [ $# -eq 0 ]; then
    # Build all by default
    build_chrome
else
    case $1 in
        chrome)
            build_chrome
            ;;
        firefox)
            build_firefox
            ;;
        all)
            build_chrome
            build_firefox
            ;;
        clean)
            echo "🧹 Cleaning build directory..."
            rm -rf build/
            echo "✅ Build directory cleaned"
            ;;
        *)
            echo "Usage: ./build.sh [chrome|firefox|all|clean]"
            exit 1
            ;;
    esac
fi

echo ""
echo "📋 Next Steps:"
echo "1. To install in Chrome:"
echo "   - Open chrome://extensions/"
echo "   - Enable Developer mode"
echo "   - Drag and drop build/gap-chrome-extension.zip"
echo ""
echo "2. To test locally:"
echo "   - Click 'Load unpacked' in Chrome extensions"
echo "   - Select the extensions/chrome/ directory"
echo ""
