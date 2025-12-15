# Winvora Application Features Summary

## Overview

Winvora provides **three application interfaces** for managing Wine environments across macOS, Linux, and Android platforms.

---

## 1. CLI Application (Cross-Platform)

**File**: `src/cli/main.py`  
**Platforms**: macOS, Linux, Android (Termux)  
**Framework**: Pure Python (no GUI dependencies)

### Commands

#### Prefix Management
```bash
winvora prefix create <name> [--path PATH] [--windows-version VERSION]
winvora prefix list
winvora prefix delete <name>
winvora prefix info <name>
```

#### Application Management
```bash
winvora app install <installer> --prefix <name>
winvora app run <executable> --prefix <name> [--args ...]
winvora app list --prefix <name>
```

#### Configuration
```bash
winvora config show
winvora config set <key> <value>
winvora config wine --prefix <name>  # Opens winecfg
```

#### System Commands
```bash
winvora system check      # Check Wine installation
winvora system info       # Display system information
winvora system processes  # Show running Wine processes
```

### Features
- ✅ Full command-line control
- ✅ Scriptable and automatable
- ✅ No GUI dependencies
- ✅ Works in SSH/terminal environments
- ✅ Progress indicators and colored output
- ✅ Detailed help for all commands

---

## 2. Desktop GUI (macOS & Linux)

**Files**: 
- macOS: `src/apps/macos/main.py`
- Linux: `src/apps/linux/main.py`

**Framework**: PyQt6 (cross-platform GUI toolkit)  
**Platforms**: macOS, Linux

### User Interface

#### Tab 1: Wine Prefixes
- **List View**: Shows all managed Wine prefixes
- **Create Button**: Dialog to create new prefix with name and settings
- **Delete Button**: Remove selected prefix with confirmation
- **Info Button**: View detailed prefix information
- **Refresh Button**: Reload prefix list

#### Tab 2: Applications
- **App List**: Displays installed Windows applications per prefix
- **Install Button**: File picker for .exe/.msi installers
- **Run Button**: Launch selected application
- **Browse .exe Button**: Quick-run any Windows executable
- **Prefix Selector**: Choose which prefix to work with

#### Tab 3: Processes
- **Process List**: Shows running Wine processes with details
- **Refresh Button**: Update process list
- **Kill Selected**: Terminate selected process
- **Kill All Wine**: Emergency kill all Wine processes

#### Tab 4: Settings
- **System Information**: Display platform, Wine version, paths
- **Wine Check Button**: Verify Wine installation
- **Configuration Options**: Future settings panel
- **About Section**: Version and license info

### Features
- ✅ Native desktop look and feel
- ✅ File browser integration
- ✅ Drag-and-drop support (future)
- ✅ Visual feedback with dialogs
- ✅ Status bar with operation progress
- ✅ Keyboard shortcuts
- ✅ Multi-window support

### Platform-Specific Adaptations

**macOS**:
- Uses macOS platform integration
- Homebrew Wine paths
- Library/Application Support for data
- Native macOS styling

**Linux**:
- Uses Linux platform integration
- System package manager Wine paths
- XDG Base Directory compliance
- Fusion style for consistency

---

## 3. Mobile App (Android)

**File**: `src/apps/android/main.py`  
**Framework**: Kivy (Python mobile framework)  
**Platform**: Android  
**Packaging**: Buildozer (APK creation)

### User Interface

#### Tab 1: Prefixes
- **Scrollable List**: Touch-friendly prefix list
- **Large Buttons**: Create, Delete, Refresh
- **Tap to View**: Touch prefix for details
- **Full-Screen Dialogs**: Mobile-optimized input

#### Tab 2: Apps
- **App Grid**: Touch-optimized application grid
- **Install Button**: File picker for installers
- **Browse Files**: Navigate Android storage
- **Launch Apps**: One-tap application launch

#### Tab 3: System
- **System Info Panel**: Scrollable system details
- **Wine Check**: Verify Wine availability
- **Compatibility Info**: Android-specific warnings
- **Installation Help**: Guide for Wine on Android

### Features
- ✅ Touch-optimized interface
- ✅ Large, finger-friendly buttons
- ✅ Scrollable content for small screens
- ✅ Material Design principles
- ✅ Portrait/landscape support
- ✅ Android permissions handling
- ✅ Storage access for installers

### Android-Specific Considerations
- Requires Wine-Android or Termux with Wine
- Limited Wine functionality compared to desktop
- Storage access permissions needed
- May require rooted device for full functionality
- Architecture compatibility (ARM vs x86)

### Building APK
```bash
cd src/apps/android
buildozer android debug
# Output: bin/winvora-0.1.0-debug.apk
```

---

## Common Features Across All Apps

### 1. Wine Prefix Management
- **Create**: Set up isolated Wine environments
- **Configure**: Windows version, DPI, architecture
- **List**: View all managed prefixes
- **Delete**: Clean removal with confirmation
- **Info**: Detailed prefix statistics

### 2. Application Installation
- **Installer Support**: .exe and .msi files
- **Silent Install**: Background installation option
- **Progress Tracking**: Monitor installation progress
- **Error Handling**: Clear error messages
- **Post-Install**: Automatic shortcut creation

### 3. Application Launching
- **Browse Mode**: Quick-run any .exe
- **Installed Apps**: Launch from managed list
- **Arguments**: Pass command-line arguments
- **Environment**: Custom environment variables
- **Working Directory**: Set CWD for apps

### 4. Wine Configuration
- **winecfg**: Open Wine configuration tool
- **DLL Overrides**: Manage DLL loading
- **Registry**: Edit Wine registry
- **Desktop Integration**: Shortcuts and menus

### 5. Process Management
- **List Processes**: Real-time process monitoring
- **Process Details**: PID, memory, CPU usage
- **Kill Process**: Terminate stuck applications
- **Kill All**: Emergency cleanup
- **Auto-Cleanup**: Remove zombie processes

### 6. System Integration
- **Wine Detection**: Auto-find Wine installation
- **Version Check**: Verify Wine version compatibility
- **Platform Info**: Display OS and architecture
- **Path Configuration**: Custom Wine binary paths
- **Logs**: Application and Wine logs

---

## Technical Implementation

### Architecture Pattern
```
User Input → Application Layer → Core Logic → Platform Layer → Wine
```

### Separation of Concerns

1. **Core Layer** (`src/core/`)
   - Platform-agnostic Wine management
   - Configuration handling
   - Business logic

2. **Platform Layer** (`src/platforms/`)
   - OS-specific Wine integration
   - Path resolution
   - System calls

3. **Application Layer** (`src/apps/` & `src/cli/`)
   - User interface (GUI/CLI)
   - User input handling
   - Display logic

### Dependencies

**Core** (no dependencies):
- Pure Python 3.8+
- Standard library only

**Desktop GUI**:
- PyQt6 (install: `pip install PyQt6`)

**Android**:
- Kivy (install: `pip install kivy`)
- Buildozer (install: `pip install buildozer`)

**Wine** (external):
- Must be installed separately
- Not bundled or distributed
- Treated as system dependency

---

## Future Enhancements

### Planned Features
- [ ] Drag-and-drop .exe files
- [ ] Wine Tricks integration
- [ ] Automatic Wine updates
- [ ] Cloud prefix sync
- [ ] Application library/store
- [ ] Performance monitoring
- [ ] Graphics settings per-app
- [ ] Controller/gamepad support
- [ ] Multi-language support
- [ ] Dark mode toggle
- [ ] Backup/restore prefixes
- [ ] Wine staging integration

### Platform-Specific Plans

**macOS**:
- [ ] Native .app bundle
- [ ] Dock integration
- [ ] Spotlight integration
- [ ] Retina display optimization

**Linux**:
- [ ] .deb/.rpm packages
- [ ] Desktop file integration
- [ ] Wayland support
- [ ] Flatpak/Snap packages

**Android**:
- [ ] Play Store submission
- [ ] Google Drive integration
- [ ] Android TV support
- [ ] Stylus support for tablets

---

## Usage Examples

### CLI Examples
```bash
# Create a gaming prefix
winvora prefix create gaming --windows-version win10

# Install a game
winvora app install ~/Downloads/game-setup.exe --prefix gaming

# Run the game
winvora app run "C:/Program Files/Game/game.exe" --prefix gaming

# Monitor performance
winvora system processes
```

### GUI Workflow
1. Launch: `python winvora.py`
2. Go to "Wine Prefixes" tab
3. Click "Create Prefix", enter name
4. Switch to "Applications" tab
5. Click "Install Application", select .exe
6. Wait for installation
7. Click "Run Application" to launch

### Android Workflow
1. Install APK on device
2. Launch Winvora app
3. Tap "Prefixes" tab
4. Tap "Create" button
5. Enter prefix name
6. Tap "Apps" tab
7. Tap "Install App"
8. Select .exe from storage
9. Tap app to launch

---

## Summary

Winvora provides **three complete application interfaces** with **identical functionality** across all platforms:

| Feature | CLI | Desktop GUI | Android App |
|---------|-----|-------------|-------------|
| Prefix Management | ✅ | ✅ | ✅ |
| App Installation | ✅ | ✅ | ✅ |
| App Launching | ✅ | ✅ | ✅ |
| Process Monitoring | ✅ | ✅ | ✅ |
| Wine Configuration | ✅ | ✅ | ✅ |
| System Checks | ✅ | ✅ | ✅ |
| Scripting | ✅ | ❌ | ❌ |
| Visual Interface | ❌ | ✅ | ✅ |
| Touch Optimized | ❌ | ❌ | ✅ |
| No Dependencies | ✅ | ❌ | ❌ |

All applications use the same core logic and platform-specific integrations, ensuring consistent behavior across all platforms.
