"""
Linux platform-specific implementation.

Handles Linux-specific Wine integration and system interactions.
"""

from pathlib import Path
from typing import Optional, Dict
import subprocess
import platform
import os


class LinuxPlatform:
    """
    Linux-specific platform implementation.
    """
    
    def __init__(self):
        """Initialize Linux platform handler."""
        self.platform_name = "Linux"
    
    def get_wine_paths(self) -> list[Path]:
        """
        Get potential Wine installation paths on Linux.
        
        Returns:
            List of paths to check for Wine.
        """
        return [
            Path("/usr/bin/wine"),
            Path("/usr/local/bin/wine"),
            Path("/opt/wine/bin/wine"),
            Path.home() / ".local" / "bin" / "wine",
            Path("/usr/lib/wine/wine"),
        ]
    
    def get_default_prefix_location(self) -> Path:
        """
        Get the default location for Wine prefixes on Linux.
        
        Returns:
            Default prefix location.
        """
        xdg_data_home = os.environ.get('XDG_DATA_HOME', str(Path.home() / ".local" / "share"))
        return Path(xdg_data_home) / "winvora" / "prefixes"
    
    def execute_wine_command(self, command: list[str], env: Optional[Dict] = None) -> Optional[subprocess.CompletedProcess]:
        """
        Execute a Wine command with Linux-specific environment setup.
        
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
            
            # Linux-specific: Ensure DISPLAY is set
            if 'DISPLAY' not in exec_env:
                exec_env['DISPLAY'] = ':0'
            
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
        Get Linux system information relevant to Wine compatibility.
        
        Returns:
            Dictionary containing system information.
        """
        try:
            distro = self._get_distribution()
            machine = platform.machine()
            kernel = platform.release()
            
            return {
                "platform": "Linux",
                "distribution": distro,
                "kernel": kernel,
                "architecture": machine,
                "desktop_environment": os.environ.get('DESKTOP_SESSION', 'unknown')
            }
        except Exception:
            return {
                "platform": "Linux",
                "distribution": "unknown",
                "architecture": "unknown"
            }
    
    def _get_distribution(self) -> str:
        """Get Linux distribution name."""
        try:
            # Try reading /etc/os-release
            if Path('/etc/os-release').exists():
                with open('/etc/os-release', 'r') as f:
                    for line in f:
                        if line.startswith('PRETTY_NAME='):
                            return line.split('=')[1].strip().strip('"')
            return 'Linux'
        except Exception:
            return 'Linux'
    
    def open_file_manager(self, path: Path) -> bool:
        """Open a path in the file manager."""
        try:
            subprocess.run(["xdg-open", str(path)], check=True)
            return True
        except Exception:
            return False
