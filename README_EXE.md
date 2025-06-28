# Storage Monitor - Executable Build Guide

This guide will help you create standalone executable files (.exe) for the Storage Monitor applications.

## 🚀 Quick Start

### Option 1: Build Both Versions
```bash
build_exe.bat
```

### Option 2: Build Individual Versions
```bash
# Build only the stable version
build_stable_only.bat

# Build only the enhanced version  
build_enhanced_only.bat
```

## 📋 Prerequisites

1. **Python 3.8 or higher** installed on your system
2. **Windows 10/11** (the executables will be Windows-specific)
3. **Internet connection** for downloading dependencies

## 🔧 Build Process

### Step 1: Install Dependencies
The build scripts will automatically install all required packages:
- PyQt5 (GUI framework)
- psutil (system monitoring)
- watchdog (file system monitoring)
- pywin32 (Windows API)
- matplotlib & numpy (for enhanced version)
- PyInstaller (for creating executables)

### Step 2: Build Executables
Run one of the build scripts:
- `build_exe.bat` - Creates both versions
- `build_stable_only.bat` - Creates only stable version
- `build_enhanced_only.bat` - Creates only enhanced version

### Step 3: Find Your Executables
After successful build, you'll find the executables in the `dist` folder:
- `StorageMonitor_Stable.exe`
- `StorageMonitor_Enhanced.exe`

## 📁 File Structure After Build

```
disk/
├── dist/
│   ├── StorageMonitor_Stable.exe
│   └── StorageMonitor_Enhanced.exe
├── build/ (temporary build files)
├── *.spec (PyInstaller spec files)
└── ... (other project files)
```

## 🎯 Using the Executables

### StorageMonitor_Stable.exe
- **Recommended for most users**
- Stable treemap visualization
- Gaming mode functionality
- Dark mode support
- Real-time file monitoring

### StorageMonitor_Enhanced.exe
- **Advanced features**
- More complex treemap algorithm
- Enhanced visualizations
- All features from stable version
- May be slightly larger file size

## ⚡ Performance Notes

- **First Launch**: May take 10-30 seconds to start (loading all dependencies)
- **File Size**: Executables will be 50-100MB (includes all Python libraries)
- **Memory Usage**: Similar to running the Python versions
- **Startup Time**: Subsequent launches will be faster

## 🔍 Troubleshooting

### Build Fails
1. **Check Python installation**: `python --version`
2. **Update pip**: `python -m pip install --upgrade pip`
3. **Clear PyInstaller cache**: Delete `build/` and `dist/` folders
4. **Reinstall dependencies**: `pip install -r requirements.txt`

### Executable Won't Start
1. **Run as Administrator**: Right-click → "Run as administrator"
2. **Check Windows Defender**: May need to allow the executable
3. **Check file permissions**: Ensure the .exe file is not blocked
4. **Try stable version**: If enhanced version fails, use stable version

### Missing Dependencies
If you get "missing module" errors:
1. **Reinstall requirements**: `pip install -r requirements.txt`
2. **Use --hidden-import**: Add missing modules to PyInstaller command
3. **Check Python path**: Ensure Python is in your system PATH

## 🎮 Gaming Mode Usage

Both executables support gaming mode:

1. **Start Gaming Session**: Click the button before playing
2. **Play Your Game**: Monitoring is paused to reduce performance impact
3. **End Gaming Session**: Click when done to see storage analysis
4. **Review Results**: See exactly what files your game created/modified

## 📊 Features Comparison

| Feature | Stable | Enhanced |
|---------|--------|----------|
| Dark Mode | ✅ | ✅ |
| Gaming Mode | ✅ | ✅ |
| Treemap | ✅ (Simple) | ✅ (Advanced) |
| Real-time Monitoring | ✅ | ✅ |
| Process Tracking | ✅ | ✅ |
| File Size | ~50MB | ~80MB |
| Stability | High | Medium |

## 🚀 Distribution

Once built, you can:
- **Copy the .exe files** to any Windows computer
- **Share with friends** (no Python installation required)
- **Create shortcuts** on desktop or start menu
- **Run from USB drive** (portable)

## 🔄 Updates

To update the executables:
1. **Modify the Python code** as needed
2. **Run the build script** again
3. **Replace the old .exe** with the new one

## 📞 Support

If you encounter issues:
1. **Try the stable version** first
2. **Check the console version** for debugging
3. **Run as administrator** if permission issues occur
4. **Check Windows event logs** for detailed error messages

---

**Note**: The executables are self-contained and include all necessary dependencies. They will work on any Windows 10/11 system without requiring Python or any additional software installation. 