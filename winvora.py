#!/usr/bin/env python3
"""
Winvora Launcher Script

Universal launcher that detects the platform and runs the appropriate application.
"""

import sys
import platform
from pathlib import Path


def detect_platform():
    """
    Detect the current platform.
    
    Returns:
        String: 'macos', 'linux', 'android', or 'unknown'
    """
    system = platform.system().lower()
    
    if system == 'darwin':
        return 'macos'
    elif system == 'linux':
        # Check if running on Android (Termux)
        if Path('/data/data/com.termux/files').exists():
            return 'android'
        return 'linux'
    else:
        return 'unknown'


def main():
    """Main launcher entry point."""
    detected_platform = detect_platform()
    
    print(f"Winvora Launcher")
    print(f"Detected platform: {detected_platform}")
    print()
    
    # Check for CLI mode flag
    if '--cli' in sys.argv:
        print("Starting CLI mode...")
        from cli.main import main as cli_main
        sys.exit(cli_main())
    
    # Launch appropriate GUI
    if detected_platform == 'macos':
        print("Starting macOS GUI...")
        try:
            from apps.macos.main import main as macos_main
            sys.exit(macos_main())
        except ImportError as e:
            print(f"Error: Could not start macOS GUI: {e}")
            print("\nFalling back to CLI mode...")
            from cli.main import main as cli_main
            sys.exit(cli_main())
    
    elif detected_platform == 'linux':
        print("Starting Linux GUI...")
        try:
            from apps.linux.main import main as linux_main
            sys.exit(linux_main())
        except ImportError as e:
            print(f"Error: Could not start Linux GUI: {e}")
            print("\nFalling back to CLI mode...")
            from cli.main import main as cli_main
            sys.exit(cli_main())
    
    elif detected_platform == 'android':
        print("Starting Android app...")
        try:
            from apps.android.main import main as android_main
            sys.exit(android_main())
        except ImportError as e:
            print(f"Error: Could not start Android app: {e}")
            print("\nFalling back to CLI mode...")
            from cli.main import main as cli_main
            sys.exit(cli_main())
    
    else:
        print(f"Unsupported platform: {detected_platform}")
        print("\nTrying CLI mode...")
        try:
            from cli.main import main as cli_main
            sys.exit(cli_main())
        except Exception as e:
            print(f"Error: {e}")
            sys.exit(1)


if __name__ == '__main__':
    main()
