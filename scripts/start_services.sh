#!/bin/bash
# Start GAP Protocol services

set -e

echo "🚀 Starting GAP Protocol Services"
echo "================================="

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "❌ Virtual environment not found. Running install script..."
    ./scripts/install.sh
fi

# Function to check if port is in use
check_port() {
    if lsof -Pi :$1 -sTCP:LISTEN -t >/dev/null 2>&1; then
        return 0
    else
        return 1
    fi
}

# Check if service is already running
if check_port 8000; then
    echo "⚠️  Service already running on port 8000"
    echo "   To stop it: kill $(lsof -ti:8000)"
    echo ""
    read -p "Stop existing service and restart? (y/N) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "Stopping existing service..."
        kill $(lsof -ti:8000) 2>/dev/null || true
        sleep 2
    else
        echo "Exiting..."
        exit 0
    fi
fi

# Start FastAPI service
echo "🌐 Starting FastAPI service on http://localhost:8000"
echo "   Documentation: http://localhost:8000/docs"
echo "   Health check: http://localhost:8000/health"
echo ""
echo "Press Ctrl+C to stop the service"
echo ""

# Run with UV
uv run uvicorn services.fastapi_service:app \
    --host 0.0.0.0 \
    --port 8000 \
    --reload \
    --log-level info
