# Storage Monitor - Final Project

A real-time storage monitoring application for Windows with dark mode, gaming mode, and treemap visualization.

## 📁 Project Structure (After Cleanup)

```
disk/
├── dist/
│   └── StorageMonitor_Stable.exe          # Your standalone executable
├── storage_monitor_stable_no_matplotlib.py # Main GUI application
├── storage_monitor_console.py             # Console version
├── build_exe_simple.bat                   # Build executable script
├── run_gui.bat                           # Run GUI version
├── run_console.bat                       # Run console version
├── cleanup.bat                           # Cleanup script
├── requirements.txt                      # Python dependencies
├── README.md                             # Original documentation
├── README_EXE.md                         # Executable build guide
└── README_FINAL.md                       # This file
```

## 🚀 Quick Start

### Option 1: Use the Executable (Recommended)
```bash
# Just double-click the executable
dist/StorageMonitor_Stable.exe
```

### Option 2: Run from Source
```bash
# GUI version
run_gui.bat

# Console version
run_console.bat
```

### Option 3: Build New Executable
```bash
# Build the executable
build_exe_simple.bat
```

## 🎯 Features

### ✅ Dark Mode
- Modern dark theme with blue accents
- Toggle between light and dark modes
- Professional styling

### ✅ Gaming Mode
- **Start Gaming Session**: Pauses intensive monitoring
- **End Gaming Session**: Shows detailed analysis
- **Performance Optimized**: Reduces CPU usage during gaming
- **Session History**: Tracks all gaming sessions

### ✅ Real-time Monitoring
- File system change detection
- Process identification
- Size change tracking
- Multiple view modes

### ✅ Treemap Visualization
- Visual representation of storage usage
- Three view modes:
  - Largest Files
  - Recent Changes
  - By Process
- Color-coded rectangles

### ✅ Storage Analysis
- Recent changes analysis
- Largest changes tracking
- Process-based grouping
- Directory monitoring

## 🎮 Gaming Mode Workflow

1. **Before Gaming**: Click "Start Gaming Session"
   - Takes snapshot of current storage state
   - Pauses intensive file monitoring
   - Reduces performance impact

2. **During Gaming**: Play your game normally
   - Minimal monitoring overhead
   - Still tracks basic changes

3. **After Gaming**: Click "End Gaming Session"
   - Shows comprehensive analysis
   - Lists all files that changed
   - Groups changes by process
   - Shows total storage impact

## 📊 Application Tabs

### 📊 Real-time Changes
- Live feed of file system changes
- Timestamps, paths, size changes, process names
- Auto-updates every 3 seconds

### 🗺️ Storage Treemap
- Visual representation of storage data
- Different view modes for different insights
- Color-coded by size

### 📈 Analysis
- Recent changes analysis (last 10 minutes)
- Largest changes tracking
- Process-based breakdowns

### 🎮 Gaming Sessions
- History of all gaming sessions
- Duration, changes, storage impact
- Detailed analysis for each session

### 💾 Storage Overview
- Current disk usage statistics
- Monitored directories
- File counts and sizes

## ⚡ Performance Notes

- **First Launch**: 10-30 seconds (loading dependencies)
- **File Size**: ~50MB executable (includes all libraries)
- **Memory Usage**: Similar to Python version
- **Startup Time**: Faster on subsequent launches

## 🔧 Troubleshooting

### Executable Won't Start
1. **Run as Administrator**: Right-click → "Run as administrator"
2. **Check Windows Defender**: May need to allow the executable
3. **Check file permissions**: Ensure .exe is not blocked

### Build Issues
1. **Update pip**: `python -m pip install --upgrade pip`
2. **Reinstall dependencies**: `pip install -r requirements.txt`
3. **Clear cache**: Delete `build/` and `dist/` folders

### Monitoring Issues
1. **Run as Administrator**: For better file access
2. **Check permissions**: Some directories may be restricted
3. **Try console version**: For debugging

## 🎯 Usage Tips

### For Gamers
- Use Gaming Mode before starting games
- Check session analysis after gaming
- Monitor specific game directories

### For Developers
- Monitor project directories
- Track build artifacts
- Analyze file creation patterns

### For System Administrators
- Monitor system directories
- Track application installations
- Analyze storage usage patterns

## 📞 Support

If you encounter issues:
1. **Try the console version** for debugging
2. **Run as administrator** if permission issues
3. **Check Windows event logs** for detailed errors
4. **Use Gaming Mode** to reduce performance impact

## 🔄 Updates

To update the application:
1. **Modify the Python code** as needed
2. **Run `build_exe_simple.bat`** to rebuild
3. **Replace the old .exe** with the new one

## 📋 System Requirements

- **OS**: Windows 10/11
- **RAM**: 4GB minimum
- **Storage**: 100MB free space
- **Python**: 3.8+ (for building from source)

---

**Note**: The executable is self-contained and includes all necessary dependencies. It will work on any Windows 10/11 system without requiring Python or any additional software installation. 