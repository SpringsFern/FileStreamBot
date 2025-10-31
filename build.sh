#!/bin/bash
echo "Building executable for Linux/macOS..."
pip install -r requirements.txt
pyinstaller --onefile --name WebStreamer WebStreamer/__main__.py
echo "Build complete! The executable is in the 'dist' folder."
