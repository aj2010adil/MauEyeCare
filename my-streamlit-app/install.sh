#!/bin/bash

echo "Installing MauEyeCare with UV..."

# Check if UV is installed
if ! command -v uv &> /dev/null; then
    echo "UV not found. Installing UV..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    
    # Add UV to PATH for current session
    export PATH="$HOME/.cargo/bin:$PATH"
    
    if ! command -v uv &> /dev/null; then
        echo "Failed to install UV. Please install manually from https://github.com/astral-sh/uv"
        exit 1
    fi
fi

echo "UV found. Installing dependencies..."
uv sync

if [ $? -ne 0 ]; then
    echo "Failed to install dependencies with UV"
    exit 1
fi

echo "Installation complete!"
echo "Starting MauEyeCare system..."
python start_system.py