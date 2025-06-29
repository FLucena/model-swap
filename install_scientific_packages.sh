#!/bin/bash
# Script to install scientific packages after basic deployment

echo "Installing scientific packages..."
pip install -r requirements-scientific.txt

echo "Scientific packages installation completed!"
echo "You can now use the 3D conversion features." 