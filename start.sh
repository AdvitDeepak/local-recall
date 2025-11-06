#!/bin/bash
# Startup script for Local Recall on Linux/Mac

echo "Starting Local Recall..."
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo ""
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies if needed
if [ ! -d "venv/lib/python*/site-packages/fastapi" ]; then
    echo "Installing dependencies..."
    pip install -r requirements.txt
    echo ""
fi

# Create .env if it doesn't exist
if [ ! -f ".env" ]; then
    echo "Creating .env file..."
    cp .env.example .env
    echo ""
fi

# Start all components
echo "Starting all components..."
echo "Backend will run on port 8000"
echo "Frontend will run on port 8501"
echo ""
echo "Press Ctrl+C to stop all components"
echo ""

python main.py all
