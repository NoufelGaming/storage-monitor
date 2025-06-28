@echo off
echo Building Storage Monitor Executables (Simplified)...
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python 3.8 or higher from https://python.org
    pause
    exit /b 1
)

echo Installing basic dependencies...
pip install psutil watchdog PyQt5 pywin32 pyinstaller

if errorlevel 1 (
    echo Error: Failed to install dependencies
    pause
    exit /b 1
)

echo.
echo Building Stable Version...
pyinstaller --onefile --windowed --name "StorageMonitor_Stable" --hidden-import=PyQt5.sip storage_monitor_stable.py

if errorlevel 1 (
    echo Error: Failed to build stable version
    pause
    exit /b 1
)

echo.
echo Build complete! Executable is in the dist folder:
echo - StorageMonitor_Stable.exe
echo.
echo You can now run this executable directly without Python!
pause 