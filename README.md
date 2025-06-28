# Storage Monitor

A real-time Windows storage monitoring application that tracks disk usage, file changes, and program activity. Built with Python and PyQt5, featuring both GUI and console interfaces.

![Storage Monitor](https://img.shields.io/badge/Python-3.8+-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![Platform](https://img.shields.io/badge/Platform-Windows-lightgrey.svg)

## Features

- **Real-time Monitoring**: Track file system changes and disk usage in real-time
- **Dual Interface**: Both GUI and console versions available
- **Storage Analysis**: Identify which programs and directories consume the most space
- **File Change Tracking**: Monitor file creation, modification, and deletion
- **Gaming Mode**: Pause monitoring during gameplay and analyze changes afterward
- **Dark Mode**: Modern dark theme for better user experience
- **Standalone Executables**: No Python installation required

## Screenshots

*Add screenshots here once you have them*

## Installation

### Option 1: Standalone Executable (Recommended)

1. Download the latest release from the [Releases](https://github.com/yourusername/storage-monitor/releases) page
2. Extract the ZIP file
3. Run `storage_monitor_console.exe` for console version or `storage_monitor_gui.exe` for GUI version

### Option 2: From Source

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/storage-monitor.git
   cd storage-monitor
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the application:
   ```bash
   # Console version
   python storage_monitor_console.py
   
   # GUI version
   python storage_monitor_stable.py
   ```

## Usage

### Console Version
- Run `storage_monitor_console.exe` or `python storage_monitor_console.py`
- Press `Ctrl+C` to stop monitoring
- View real-time file system changes and disk usage statistics

### GUI Version
- Run `storage_monitor_stable.exe` or `python storage_monitor_stable.py`
- Use the interface to:
  - Start/stop monitoring
  - View storage usage by directory
  - Analyze file changes
  - Enable gaming mode
  - Switch between light and dark themes

### Gaming Mode
- Click "Gaming Mode" to pause monitoring
- Play your games
- Click "Analyze Changes" to see what files were modified during gameplay

## Building Executables

To create standalone executables:

```bash
# Build all versions
build_exe_simple.bat

# Or build individually
pyinstaller --onefile --windowed storage_monitor_console.py
pyinstaller --onefile --windowed storage_monitor_stable.py
```

## Project Structure

```
storage-monitor/
├── storage_monitor_console.py      # Console version
├── storage_monitor_stable.py       # GUI version (stable)
├── storage_monitor_stable_no_matplotlib.py  # GUI version (no matplotlib)
├── requirements.txt                # Python dependencies
├── build_exe_simple.bat           # Build script for executables
├── run_console.bat                # Run console version
├── run_gui.bat                    # Run GUI version
├── cleanup.bat                    # Cleanup script
├── README.md                      # This file
├── README_FINAL.md                # Detailed documentation
├── LICENSE                        # MIT License
└── .gitignore                     # Git ignore rules
```

## Dependencies

- Python 3.8+
- PyQt5
- psutil
- watchdog

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Inspired by tools like SpaceSniffer and WinDirStat
- Built with PyQt5 for cross-platform compatibility
- Uses watchdog for efficient file system monitoring

## Issues and Support

If you encounter any issues or have questions:

1. Check the [Issues](https://github.com/yourusername/storage-monitor/issues) page
2. Create a new issue with detailed information about your problem
3. Include your Windows version and Python version if applicable

## Roadmap

- [ ] Add network drive monitoring
- [ ] Implement file type filtering
- [ ] Add export functionality (CSV, JSON)
- [ ] Create system tray integration
- [ ] Add email notifications for large file changes
- [ ] Implement cloud storage monitoring

---

**Note**: This application requires Windows and may need administrator privileges for full functionality. 