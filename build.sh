#!/bin/bash
# Local build script for Winvora
# Builds packages for the current platform

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "🚀 Winvora Local Build Script"
echo "=============================="

# Detect platform
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    PLATFORM="linux"
elif [[ "$OSTYPE" == "darwin"* ]]; then
    PLATFORM="macos"
else
    echo "❌ Unsupported platform: $OSTYPE"
    exit 1
fi

echo "Platform: $PLATFORM"
echo ""

# Install dependencies
echo "📦 Installing dependencies..."
pip install --upgrade pip
pip install PyQt6 pyinstaller

# Build executable
echo "🔨 Building executable..."
if [ "$PLATFORM" == "linux" ]; then
    pyinstaller --onefile --windowed --name winvora-linux \
        --add-data "src:src" \
        --hidden-import PyQt6 \
        winvora.py
    
    echo "✅ Linux executable built: dist/winvora-linux"
    
    # Optional: Create AppImage
    read -p "Create AppImage? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "📦 Creating AppImage..."
        
        # Download appimagetool if not exists
        if [ ! -f "appimagetool-x86_64.AppImage" ]; then
            wget https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-x86_64.AppImage
            chmod +x appimagetool-x86_64.AppImage
        fi
        
        # Create AppDir
        rm -rf AppDir
        mkdir -p AppDir/usr/bin
        mkdir -p AppDir/usr/share/applications
        mkdir -p AppDir/usr/share/icons/hicolor/256x256/apps
        
        # Copy files
        cp dist/winvora-linux AppDir/usr/bin/winvora
        
        # Create desktop file
        cat > AppDir/winvora.desktop << EOF
[Desktop Entry]
Name=Winvora
Exec=winvora
Icon=winvora
Type=Application
Categories=Utility;
Comment=Wine compatibility layer manager
EOF
        
        cp AppDir/winvora.desktop AppDir/usr/share/applications/
        touch AppDir/usr/share/icons/hicolor/256x256/apps/winvora.png
        
        # Build AppImage
        ./appimagetool-x86_64.AppImage AppDir winvora-linux-x86_64.AppImage
        
        echo "✅ AppImage created: winvora-linux-x86_64.AppImage"
    fi
    
elif [ "$PLATFORM" == "macos" ]; then
    pyinstaller --onefile --windowed --name Winvora \
        --add-data "src:src" \
        --hidden-import PyQt6 \
        --osx-bundle-identifier com.winvora.app \
        winvora.py
    
    echo "✅ macOS app bundle built: dist/Winvora.app"
    
    # Optional: Create DMG
    read -p "Create DMG? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "📦 Creating DMG..."
        
        rm -rf dmg_temp
        mkdir -p dmg_temp
        cp -r "dist/Winvora.app" dmg_temp/
        ln -s /Applications dmg_temp/Applications
        
        hdiutil create -volname "Winvora" -srcfolder dmg_temp -ov -format UDZO Winvora.dmg
        
        rm -rf dmg_temp
        echo "✅ DMG created: Winvora.dmg"
    fi
fi

echo ""
echo "✨ Build complete!"
echo "Run your application:"
if [ "$PLATFORM" == "linux" ]; then
    echo "  ./dist/winvora-linux"
    [ -f "winvora-linux-x86_64.AppImage" ] && echo "  ./winvora-linux-x86_64.AppImage"
elif [ "$PLATFORM" == "macos" ]; then
    echo "  open dist/Winvora.app"
    [ -f "Winvora.dmg" ] && echo "  open Winvora.dmg"
fi
