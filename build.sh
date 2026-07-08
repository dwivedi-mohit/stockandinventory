#!/bin/bash

# Build Inventory Management System GUI
# This script creates a standalone executable using PyInstaller

echo "🔨 Building Inventory Management System GUI..."

# Check if PyInstaller is installed
if ! command -v pyinstaller &> /dev/null; then
    echo "Installing PyInstaller..."
    pip install pyinstaller
fi

# Build the executable
pyinstaller --onefile \
    --windowed \
    --icon=app_icon.ico \
    --name="InventoryManagementSystem" \
    --add-data ".:." \
    inventory_ui.py

echo "✅ Build complete!"
echo "📦 Executable location: dist/InventoryManagementSystem"
echo ""
echo "To distribute:"
echo "  1. Copy the 'dist/InventoryManagementSystem' executable"
echo "  2. Users can run it directly - no Python installation needed!"
