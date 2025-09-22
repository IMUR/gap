#!/bin/bash
# GAP Protocol Installation Script

set -e

echo "🚀 GAP Protocol Installation"
echo "============================"

# Check for UV
if ! command -v uv &> /dev/null; then
    echo "📦 Installing UV package manager..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.cargo/bin:$PATH"
fi

# Check Python version
echo "🐍 Checking Python version..."
if ! uv python list | grep -q "3.11"; then
    echo "📥 Installing Python 3.11..."
    uv python install 3.11
fi

# Create virtual environment
echo "🔧 Setting up virtual environment..."
uv venv

# Install dependencies
echo "📚 Installing dependencies..."
uv sync

# Install development dependencies
echo "🛠️ Installing development tools..."
uv sync --dev

echo ""
echo "✅ Installation complete!"
echo ""
echo "To start using GAP Protocol:"
echo "  1. Start the service: ./scripts/start_services.sh"
echo "  2. Use the CLI: uv run gap-cli --help"
echo "  3. Or in ZED: Press Cmd+Shift+G for GAP commands"
echo ""
