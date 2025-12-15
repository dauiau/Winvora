"""
macOS platform-specific implementation.

Handles macOS-specific Wine integration and system interactions.
"""

from pathlib import Path
from typing import Optional, Dict
import subprocess
import platform
import os


class MacOSPlatform:
    """
    macOS-specific platform implementation.
    """
    
    def __init__(self):
        """Initialize macOS platform handler."""
        self.platform_name = "macOS"
    
    def get_wine_paths(self) -> list[Path]:
        """
        Get potential Wine installation paths on macOS.
        
        Returns:
            List of paths to check for Wine.
        """
        return [
            Path("/opt/homebrew/bin/wine"),  # Apple Silicon Homebrew
            Path("/usr/local/bin/wine"),    # Intel Homebrew
            Path("/opt/local/bin/wine"),    # MacPorts
            Path.home() / ".local" / "bin" / "wine",
            Path("/Applications/Wine Stable.app/Contents/Resources/wine/bin/wine"),
        ]
    
    def get_default_prefix_location(self) -> Path:
        """
        Get the default location for Wine prefixes on macOS.
        
        Returns:
            Default prefix location.
        """
        return Path.home() / "Library" / "Application Support" / "Winvora" / "prefixes"
    
    def execute_wine_command(self, command: list[str], env: Optional[Dict] = None) -> Optional[subprocess.CompletedProcess]:
        """
        Execute a Wine command with macOS-specific environment setup.
        
        Args:
            command: Command and arguments to execute
            env: Environment variables
            
        Returns:
            CompletedProcess object or None if failed.
        """
        try:
            exec_env = os.environ.copy()
            if env:
                exec_env.update(env)
            
            result = subprocess.run(
                command,
                env=exec_env,
                capture_output=True,
                text=True,
                timeout=300
            )
            return result
        except Exception as e:
            print(f"Error executing Wine command: {e}")
            return None
    
    def get_system_info(self) -> dict:
        """
        Get macOS system information relevant to Wine compatibility.
        
        Returns:
            Dictionary containing system information.
        """
        try:
            mac_ver = platform.mac_ver()[0]
            machine = platform.machine()
            
            return {
                "platform": "macOS",
                "version": mac_ver,
                "architecture": machine,
                "is_apple_silicon": machine == "arm64"
            }
        except Exception:
            return {
                "platform": "macOS",
                "architecture": "unknown"
            }
    
    def open_finder(self, path: Path) -> bool:
        """Open a path in Finder."""
        try:
            subprocess.run(["open", str(path)], check=True)
            return True
        except Exception:
            return False
