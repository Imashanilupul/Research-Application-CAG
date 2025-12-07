#!/bin/bash

# Backend startup script for development

echo "PDF Research Assistant Backend - Development Setup"
echo "=================================================="

# Check Python version
python --version

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Initialize application
echo "Initializing application..."
python init_app.py

# Run application
echo "Starting application on http://0.0.0.0:8000"
echo "API Documentation: http://localhost:8000/docs"
echo "=================================================="

uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
