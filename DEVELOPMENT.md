# Winvora Development Guide

## Installation

### Installing Winvora

```bash
# Clone the repository
git clone https://github.com/dauiau/Winvora.git
cd Winvora

# Install CLI only (no GUI dependencies)
pip install -e .

# Install with GUI support (macOS/Linux)
pip install -e ".[gui]"

# Install with all features
pip install -e ".[all]"
```

### Prerequisites

**Wine Installation** (required - external dependency):

- **macOS**: `brew install wine-stable`
- **Ubuntu/Debian**: `sudo apt install wine`
- **Fedora**: `sudo dnf install wine`
- **Arch**: `sudo pacman -S wine`
- **Android**: Install Wine in Termux: `pkg install wine`

## Running Winvora

### CLI Mode (All Platforms)

```bash
# Run CLI directly
winvora --help

# Or use the launcher
python winvora.py --cli
```

### GUI Mode

```bash
# Auto-detect platform and launch GUI
python winvora.py

# Or run platform-specific apps directly:
python -m apps.macos.main    # macOS
python -m apps.linux.main    # Linux
python -m apps.android.main  # Android
```

## Features

### 1. Prefix Management
- **Create prefix**: Set up isolated Wine environments
- **List prefixes**: View all managed prefixes
- **Delete prefix**: Remove prefixes and their data
- **Configure prefix**: Adjust Windows version, DPI, etc.

### 2. Application Management
- **Install apps**: Run Windows installers (.exe, .msi)
- **Launch apps**: Run installed Windows applications
- **Browse executables**: Quick-run any .exe file
- **Manage apps**: View and uninstall applications

### 3. Wine Configuration
- **Wine settings**: Access winecfg for each prefix
- **DLL overrides**: Configure DLL loading behavior
- **Environment**: Set Wine environment variables

### 4. Process Monitoring
- **View processes**: See running Wine applications
- **Kill processes**: Terminate stuck applications
- **Clean up**: Kill all Wine processes at once

### 5. System Information
- **Platform detection**: Automatically detect OS
- **Wine check**: Verify Wine installation
- **System info**: Display relevant system details

## CLI Examples

```bash
# Create a new Wine prefix
winvora prefix create my-prefix

# List all prefixes
winvora prefix list

# Install an application
winvora app install ~/Downloads/setup.exe --prefix my-prefix

# Run an application
winvora app run "C:/Program Files/App/app.exe" --prefix my-prefix

# Show system information
winvora system info

# Check Wine installation
winvora system check

# Configure Wine for a prefix
winvora config wine --prefix my-prefix
```

## GUI Applications

### macOS/Linux Desktop (PyQt6)
- **Multi-tab interface**: Prefixes, Apps, Processes, Settings
- **File browser**: Select installers and executables
- **Visual feedback**: Dialogs and status messages
- **Native feel**: Platform-appropriate styling

### Android (Kivy)
- **Touch-optimized**: Large buttons and touch gestures
- **Mobile layout**: Tabbed interface for small screens
- **Lightweight**: Minimal resource usage
- **Buildozer**: Package as APK with buildozer

## Building Android APK

```bash
cd src/apps/android
buildozer android debug
# APK will be in: bin/winvora-0.1.0-debug.apk
```

## Architecture

```
Winvora/
├── src/
│   ├── core/              # Cross-platform core logic
│   │   ├── wine_manager.py    # Wine environment management
│   │   └── config.py          # Configuration handling
│   ├── platforms/         # Platform-specific code
│   │   ├── macos/             # macOS integration
│   │   ├── linux/             # Linux integration
│   │   └── android/           # Android integration
│   ├── cli/              # Command-line interface
│   │   └── main.py
│   └── apps/             # GUI applications
│       ├── macos/             # macOS GUI (PyQt6)
│       ├── linux/             # Linux GUI (PyQt6)
│       └── android/           # Android app (Kivy)
├── winvora.py            # Universal launcher
├── setup.py              # Package configuration
└── README.md
```

## Contributing

See [README.md](README.md) for contribution guidelines. Remember:
- All code must be original (no GPL or copied code)
- Follow existing architecture patterns
- Test on multiple platforms when possible
- Document new features

## License

MIT License - see [LICENSE](LICENSE)
