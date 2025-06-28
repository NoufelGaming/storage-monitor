@echo off
echo Cleaning up project directory...
echo.

REM Remove PyInstaller build artifacts
echo Removing PyInstaller build files...
if exist build rmdir /s /q build
if exist *.spec del *.spec

REM Remove Python cache files
echo Removing Python cache files...
if exist __pycache__ rmdir /s /q __pycache__
if exist *.pyc del *.pyc
if exist *.pyo del *.pyo

REM Remove temporary files
echo Removing temporary files...
if exist *.tmp del *.tmp
if exist *.log del *.log

REM Remove old Python files (keep only the final versions)
echo Cleaning up Python source files...
if exist storage_monitor.py del storage_monitor.py
if exist storage_monitor_light.py del storage_monitor_light.py
if exist storage_monitor_simple.py del storage_monitor_simple.py
if exist storage_monitor_enhanced.py del storage_monitor_enhanced.py

REM Remove old batch files (keep only the final ones)
echo Cleaning up batch files...
if exist install.bat del install.bat
if exist install_fixed.bat del install_fixed.bat
if exist run.bat del run.bat
if exist run_light.bat del run_light.bat
if exist run_simple.bat del run_simple.bat
if exist run_enhanced.bat del run_enhanced.bat
if exist run_stable.bat del run_stable.bat
if exist build_exe.bat del build_exe.bat
if exist build_stable_only.bat del build_stable_only.bat
if exist build_enhanced_only.bat del build_enhanced_only.bat

echo.
echo Cleanup complete! Keeping only essential files:
echo - storage_monitor_stable_no_matplotlib.py (main source)
echo - storage_monitor_console.py (console version)
echo - build_exe_simple.bat (build script)
echo - requirements.txt (dependencies)
echo - README.md (documentation)
echo - README_EXE.md (executable guide)
echo - dist/ (contains your executables)
echo.
pause 