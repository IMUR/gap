#!/bin/bash
# Development environment setup for GAP Protocol

set -e

echo "🔧 GAP Protocol Development Setup"
echo "=================================="

# Install UV if not present
if ! command -v uv &> /dev/null; then
    echo "📦 Installing UV..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.cargo/bin:$PATH"
fi

# Setup Python environment
echo "🐍 Setting up Python environment..."
uv python install 3.11
uv venv
uv sync --dev

# Install pre-commit hooks (if using git)
if [ -d ".git" ]; then
    echo "🎣 Setting up git hooks..."
    cat > .git/hooks/pre-commit << 'EOF'
#!/bin/bash
# Pre-commit hook for GAP Protocol

# Format code
uv run black . --check
uv run ruff check .

# Run tests
uv run pytest tests/ -q
EOF
    chmod +x .git/hooks/pre-commit
fi

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "📝 Creating .env file..."
    cat > .env << EOF
# GAP Protocol Environment Variables
GAP_USE_API=false
GAP_API_URL=http://localhost:8000
GAP_LOG_LEVEL=INFO
EOF
fi

# Make scripts executable
chmod +x scripts/*.sh

echo ""
echo "✅ Development environment ready!"
echo ""
echo "Available commands:"
echo "  ./scripts/start_services.sh - Start GAP service"
echo "  uv run gap-cli --help      - CLI tool"
echo "  uv run pytest              - Run tests"
echo "  uv run black .             - Format code"
echo "  uv run ruff check .        - Lint code"
echo ""
