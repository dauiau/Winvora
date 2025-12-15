"""
Winvora Linux Desktop Application

GUI application for Linux using PyQt6 (same as macOS but with Linux-specific adaptations).
"""

import sys
from pathlib import Path

try:
    from PyQt6.QtWidgets import QApplication
    PYQT_AVAILABLE = True
except ImportError:
    PYQT_AVAILABLE = False
    print("PyQt6 not available. Install with: pip install PyQt6")

from platforms.linux import LinuxPlatform

# Reuse the main window from macOS (it's cross-platform)
# but with Linux-specific platform integration
if PYQT_AVAILABLE:
    # Import the base window class
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent / 'macos'))
    from main import WinvoraMainWindow as BaseMainWindow
    
    class LinuxMainWindow(BaseMainWindow):
        """
        Linux-specific main window.
        
        Inherits from the base window but uses Linux platform integration.
        """
        
        def __init__(self):
            """Initialize the Linux main window."""
            # Override platform before calling super().__init__()
            super().__init__()
            self.platform = LinuxPlatform()
            
            # Update window title for Linux
            self.setWindowTitle("Winvora - Wine Manager (Linux)")
            
            # Refresh system info with Linux platform
            self._update_system_info()
        
        def _update_system_info(self):
            """Update system information display with Linux-specific info."""
            info = self.platform.get_system_info()
            text = f"""Platform: {info.get('platform', 'Unknown')}
Distribution: {info.get('distribution', 'Unknown')}
Architecture: {info.get('architecture', 'Unknown')}
Wine Path: {self.platform.get_wine_paths()[0] if self.platform.get_wine_paths() else 'Not found'}
Default Prefix Location: {self.platform.get_default_prefix_location()}

Wine Installation:
  Debian/Ubuntu: sudo apt install wine
  Fedora: sudo dnf install wine
  Arch: sudo pacman -S wine
"""
            self.system_info.setPlainText(text)


def main():
    """Main entry point for the Linux application."""
    if not PYQT_AVAILABLE:
        print("Error: PyQt6 is required to run the GUI application")
        print("Install with: pip install PyQt6")
        print("On Linux, you may also need: sudo apt install python3-pyqt6")
        return 1
    
    app = QApplication(sys.argv)
    app.setApplicationName("Winvora")
    app.setOrganizationName("Winvora")
    
    # Set Linux-specific style
    app.setStyle('Fusion')
    
    window = LinuxMainWindow()
    window.show()
    
    return app.exec()


if __name__ == '__main__':
    sys.exit(main())
