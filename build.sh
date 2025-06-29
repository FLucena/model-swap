#!/bin/bash
set -e

echo "=== Build Script Starting ==="
echo "Python version:"
python --version

echo "=== Upgrading pip and build tools ==="
pip install --upgrade pip
pip install --upgrade setuptools wheel

echo "=== Installing basic packages ==="
pip install -r requirements.txt

echo "=== Installing scientific packages ==="
# Install numpy first (dependency for others)
echo "Installing numpy..."
pip install "numpy>=1.26.0"

# Install scipy (should have wheels for Python 3.13)
echo "Installing scipy..."
pip install "scipy>=1.11.0"

# Install other scientific packages
echo "Installing other scientific packages..."
pip install "networkx>=3.0.0"
pip install pycollada==0.9.1
pip install trimesh==3.23.5

echo "=== Build completed successfully ===" 