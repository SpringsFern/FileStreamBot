@echo off
echo Building executable for Windows...
pip install -r requirements.txt
pyinstaller --onefile --name WebStreamer WebStreamer/__main__.py
echo Build complete! The executable is in the 'dist' folder.
pause
