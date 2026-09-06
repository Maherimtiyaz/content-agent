#!/bin/bash
# Setup development environment

set -e

echo "=== Brand Engineer Development Setup ==="

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed. Please install Python 3.10+ first."
    exit 1
fi

echo "Python version: $(python3 --version)"

# Navigate to backend directory
cd "$(dirname "$0")/../backend"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Copy .env.example to .env if it doesn't exist
if [ ! -f ".env" ]; then
    echo "Creating .env from .env.example..."
    cp .env.example .env
    echo "WARNING: Please update .env with your actual configuration!"
fi

# Generate a secret key if using default
if grep -q "dev_secret_key_change_in_production" .env; then
    echo "Generating secure secret key..."
    SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")
    sed -i.bak "s/dev_secret_key_change_in_production/$SECRET_KEY/" .env
    rm .env.bak
fi

echo ""
echo "=== Setup Complete ==="
echo ""
echo "Next steps:"
echo "1. Update backend/.env with your database credentials"
echo "2. Start PostgreSQL (or use docker-compose)"
echo "3. Run migrations: cd backend && alembic upgrade head"
echo "4. Start the server: cd backend && uvicorn app.main:app --reload"
echo ""
echo "Or use Docker Compose:"
echo "  cd /workspace && docker-compose up -d"
echo ""
