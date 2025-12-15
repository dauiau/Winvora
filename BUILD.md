# Winvora Build and Release System

This document describes the automated build and release system for Winvora.

## Overview

Winvora uses GitHub Actions to automatically build installation packages for all supported platforms:
- **Linux**: Standalone executable, AppImage, and .deb package
- **macOS**: .app bundle and .dmg installer
- **Android**: .apk package

## Automatic Builds

### Triggers

Builds are automatically triggered on:
- **Push to main branch**: Creates development builds
- **Pull requests**: Runs tests and builds for validation
- **Version tags** (v*): Creates official releases
- **Manual trigger**: Via GitHub Actions UI

### Workflow Files

- `.github/workflows/build-releases.yml` - Main build pipeline
- `.github/workflows/test.yml` - Testing and linting

## Build Outputs

### Linux Builds

1. **Standalone Executable** (`winvora-linux`)
   - Single file executable
   - No installation required
   - Portable

2. **AppImage** (`winvora-linux-x86_64.AppImage`)
   - Universal Linux package
   - Works on most distributions
   - Self-contained with dependencies
   - Just download and run

3. **DEB Package** (`winvora_1.0.0_amd64.deb`)
   - For Debian/Ubuntu systems
   - Installs to `/usr/bin/winvora`
   - Creates desktop entry
   - Install with: `sudo dpkg -i winvora_1.0.0_amd64.deb`

### macOS Builds

1. **DMG Installer** (`Winvora.dmg`)
   - Standard macOS installer
   - Drag & drop to Applications
   - Signed and notarized (when certificates configured)

### Android Builds

1. **APK Package** (`winvora-android.apk`)
   - Android installation package
   - Built with Buildozer
   - Supports ARM and ARM64 architectures

## Using the Builds

### Downloading Builds

**From GitHub Actions:**
1. Go to the [Actions tab](../../actions)
2. Click on the latest successful workflow run
3. Download artifacts from the bottom of the page

**From Releases** (for tagged versions):
1. Go to the [Releases page](../../releases)
2. Download the package for your platform
3. Install using platform-specific instructions

### Installation Instructions

#### Linux - AppImage
```bash
# Download
wget https://github.com/dauiau/Winvora/releases/latest/download/winvora-linux-x86_64.AppImage

# Make executable
chmod +x winvora-linux-x86_64.AppImage

# Run
./winvora-linux-x86_64.AppImage
```

#### Linux - DEB Package
```bash
# Download
wget https://github.com/dauiau/Winvora/releases/latest/download/winvora_1.0.0_amd64.deb

# Install
sudo dpkg -i winvora_1.0.0_amd64.deb

# Install dependencies if needed
sudo apt-get install -f

# Run
winvora
```

#### macOS
```bash
# Download
curl -LO https://github.com/dauiau/Winvora/releases/latest/download/Winvora.dmg

# Open DMG
open Winvora.dmg

# Drag Winvora.app to Applications folder
# Then launch from Applications
```

#### Android
```bash
# Download APK to your device
# Open the APK file
# Allow installation from unknown sources if prompted
# Install and run
```

## Creating a Release

To create an official release:

1. **Update version numbers** in relevant files
2. **Commit changes** to main branch
3. **Create and push a tag:**
   ```bash
   git tag v1.0.0
   git push origin v1.0.0
   ```
4. **GitHub Actions will automatically:**
   - Build for all platforms
   - Run tests
   - Create a GitHub Release
   - Upload all packages

## Local Building

### Linux

**Using PyInstaller:**
```bash
pip install PyQt6 pyinstaller
pyinstaller --onefile --windowed --name winvora-linux \
  --add-data "src:src" \
  --hidden-import PyQt6 \
  winvora.py
```

**Creating AppImage:**
```bash
# Requires appimagetool
# See .github/workflows/build-releases.yml for complete script
```

**Creating DEB:**
```bash
# Requires dpkg
# See .github/workflows/build-releases.yml for complete script
```

### macOS

**Using PyInstaller:**
```bash
pip install PyQt6 pyinstaller
pyinstaller --onefile --windowed --name Winvora \
  --add-data "src:src" \
  --hidden-import PyQt6 \
  --osx-bundle-identifier com.winvora.app \
  winvora.py
```

**Creating DMG:**
```bash
hdiutil create -volname "Winvora" -srcfolder dist/Winvora.app \
  -ov -format UDZO Winvora.dmg
```

### Android

**Using Buildozer:**
```bash
cd src/apps/android
pip install buildozer cython kivy
buildozer android debug
# APK will be in .buildozer/android/platform/build-*/outputs/apk/debug/
```

## Configuration

### Build Settings

Edit `.github/workflows/build-releases.yml` to customize:
- Python version
- Build flags
- Package metadata
- Upload destinations

### Adding Code Signing

**For macOS:**
Add these secrets to your repository:
- `APPLE_CERTIFICATE`: Base64-encoded .p12 certificate
- `APPLE_CERTIFICATE_PASSWORD`: Certificate password
- `APPLE_ID`: Your Apple ID
- `APPLE_APP_SPECIFIC_PASSWORD`: App-specific password

**For Android:**
Add these secrets:
- `ANDROID_KEYSTORE`: Base64-encoded keystore
- `ANDROID_KEYSTORE_PASSWORD`: Keystore password
- `ANDROID_KEY_ALIAS`: Key alias
- `ANDROID_KEY_PASSWORD`: Key password

## Troubleshooting

### Build Fails on Linux
- Check PyQt6 installation
- Verify Python version compatibility
- Check hidden imports in PyInstaller spec

### Build Fails on macOS
- Ensure proper bundle identifier
- Check for macOS-specific dependencies
- Verify icon file exists (.icns format)

### Build Fails on Android
- Check Java version (requires JDK 17)
- Verify Android SDK installation
- Check buildozer.spec configuration
- Ensure sufficient disk space

### Missing Dependencies
Add dependencies to the workflow file:
```yaml
pip install your-dependency
```

## CI/CD Status

Check the current build status:
- ![Build Status](../../actions/workflows/build-releases.yml/badge.svg)
- ![Tests](../../actions/workflows/test.yml/badge.svg)

## Support

For build issues:
1. Check [GitHub Actions logs](../../actions)
2. Review [Issues](../../issues)
3. See [Discussions](../../discussions)
