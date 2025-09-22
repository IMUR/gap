#!/bin/bash
# Generate placeholder SVG icons for the GAP extension

cat > icon.svg << 'EOF'
<svg width="128" height="128" viewBox="0 0 128 128" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="grad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#667eea;stop-opacity:1" />
      <stop offset="100%" style="stop-color:#764ba2;stop-opacity:1" />
    </linearGradient>
  </defs>
  <rect width="128" height="128" rx="24" fill="url(#grad)"/>
  <text x="50%" y="50%" text-anchor="middle" dy=".3em" fill="white" font-family="Arial, sans-serif" font-size="48" font-weight="bold">GAP</text>
</svg>
EOF

# Convert SVG to PNG (requires ImageMagick or similar)
# For now, just create a placeholder message
echo "To generate PNG icons from the SVG:"
echo "1. Install ImageMagick: sudo apt-get install imagemagick"
echo "2. Run these commands:"
echo "   convert -background none icon.svg -resize 16x16 icon16.png"
echo "   convert -background none icon.svg -resize 32x32 icon32.png"
echo "   convert -background none icon.svg -resize 48x48 icon48.png"
echo "   convert -background none icon.svg -resize 128x128 icon128.png"
echo ""
echo "Or use an online SVG to PNG converter with icon.svg"
