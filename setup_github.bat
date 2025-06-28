@echo off
echo Setting up Storage Monitor for GitHub...
echo.

REM Check if git is installed
git --version >nul 2>&1
if errorlevel 1 (
    echo Error: Git is not installed or not in PATH
    echo Please install Git from https://git-scm.com/
    pause
    exit /b 1
)

REM Initialize git repository
echo Initializing Git repository...
git init

REM Add all files
echo Adding files to repository...
git add .

REM Create initial commit
echo Creating initial commit...
git commit -m "Initial commit: Storage Monitor application

- Real-time Windows storage monitoring
- GUI and console interfaces
- Gaming mode functionality
- Dark mode support
- Standalone executables"

echo.
echo Git repository initialized successfully!
echo.
echo Next steps:
echo 1. Create a new repository on GitHub
echo 2. Run these commands to push to GitHub:
echo    git remote add origin https://github.com/YOUR_USERNAME/storage-monitor.git
echo    git branch -M main
echo    git push -u origin main
echo.
echo Remember to replace YOUR_USERNAME with your actual GitHub username!
echo.
pause 