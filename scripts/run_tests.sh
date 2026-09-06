#!/bin/bash
# Run tests for the backend

set -e

echo "=== Running Brand Engineer Tests ==="

# Navigate to backend directory
cd "$(dirname "$0")/../backend"

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Install test dependencies if needed
pip install -q pytest pytest-asyncio httpx

# Run tests with coverage
echo ""
echo "Running pytest..."
pytest tests/ -v --tb=short

echo ""
echo "=== Tests Complete ==="
