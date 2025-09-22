# GAP Protocol - Setup Guide

## Prerequisites

- Python 3.11 or higher
- Git (for version control)
- Terminal access

## Installation Methods

### Method 1: Automated Installation (Recommended)

```bash
# Clone the repository
git clone <repository-url> gap-protocol
cd gap-protocol

# Run the installation script
./scripts/install.sh
```

This script will:
1. Install UV package manager (if not present)
2. Set up Python 3.11 environment
3. Install all dependencies
4. Configure the development environment

### Method 2: Manual UV Installation

```bash
# Install UV
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone and enter directory
git clone <repository-url> gap-protocol
cd gap-protocol

# Install dependencies
uv sync

# For development
uv sync --dev
```

### Method 3: Development Setup

```bash
# Full development environment
./scripts/dev_setup.sh
```

This includes:
- Development dependencies
- Git hooks for code quality
- Environment variables
- Test configuration

## Configuration

### Environment Variables

Create a `.env` file:

```env
# API mode (false = direct, true = use service)
GAP_USE_API=false

# Service URL (if using API mode)
GAP_API_URL=http://localhost:8000

# Logging level
GAP_LOG_LEVEL=INFO
```

### ZED IDE Setup

If using ZED editor:

1. Open the project in ZED
2. Dependencies auto-install on folder open
3. Tasks are available in command palette
4. Key bindings are configured (Cmd+Shift+G prefix)

### Service Configuration

The FastAPI service runs on port 8000 by default. Ensure this port is available.

## Verification

### Test Installation

```bash
# Check CLI
uv run gap-cli --help

# Start service
./scripts/start_services.sh

# In another terminal, check health
curl http://localhost:8000/health
```

### Run Examples

```bash
# Run example code
uv run python examples/basic_usage.py

# Test CLI wrapping
echo "Test content" | uv run gap-cli wrap --stdin --platform test --chat-id test
```

## Troubleshooting

### Port 8000 in Use

```bash
# Check what's using port 8000
lsof -i:8000

# Kill process if needed
kill $(lsof -ti:8000)
```

### UV Not Found

```bash
# Add to PATH
export PATH="$HOME/.cargo/bin:$PATH"

# Add to shell profile
echo 'export PATH="$HOME/.cargo/bin:$PATH"' >> ~/.bashrc
```

### Python Version Issues

```bash
# Install Python 3.11 with UV
uv python install 3.11

# Set as project Python
echo "3.11" > .python-version
```

### Dependencies Not Installing

```bash
# Clear UV cache
rm -rf .venv uv.lock

# Reinstall
uv sync
```

## Next Steps

- Read [USAGE.md](./USAGE.md) to learn GAP operations
- Check [INTEGRATION.md](./INTEGRATION.md) for platform setup
- See [DEVELOPMENT.md](./DEVELOPMENT.md) to contribute