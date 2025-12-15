"""
Android platform-specific implementation.

Handles Android-specific Wine integration and system interactions.
Note: Wine on Android typically requires special builds like Wine-Android or Termux.
"""

from pathlib import Path
from typing import Optional, Dict, Tuple
import subprocess
import platform
import os


class AndroidPlatform:
    """
    Android-specific platform implementation.
    """
    
    def __init__(self):
        """Initialize Android platform handler."""
        self.platform_name = "Android"
        self.is_termux = self._check_termux()
    
    def _check_termux(self) -> bool:
        """Check if running in Termux environment."""
        return Path('/data/data/com.termux/files').exists()
    
    def get_wine_paths(self) -> list[Path]:
        """
        Get potential Wine installation paths on Android.
        
        Returns:
            List of paths to check for Wine.
        """
        paths = []
        
        if self.is_termux:
            paths.extend([
                Path("/data/data/com.termux/files/usr/bin/wine"),
                Path("/data/data/com.termux/files/usr/bin/wine64"),
                Path.home() / ".local" / "bin" / "wine",
            ])
        else:
            paths.extend([
                Path("/system/bin/wine"),
                Path("/data/local/wine/bin/wine"),
            ])
        
        return paths
    
    def get_default_prefix_location(self) -> Path:
        """
        Get the default location for Wine prefixes on Android.
        
        Returns:
            Default prefix location.
        """
        if self.is_termux:
            return Path.home() / ".local" / "share" / "winvora" / "prefixes"
        else:
            return Path("/data/data/com.winvora/files/prefixes")
    
    def execute_wine_command(self, command: list[str], env: Optional[Dict] = None) -> Optional[subprocess.CompletedProcess]:
        """
        Execute a Wine command with Android-specific environment setup.
        
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
            
            # Android-specific: Set up display if needed
            if 'DISPLAY' not in exec_env:
                exec_env['DISPLAY'] = ':0'
            
            # Termux-specific adjustments
            if self.is_termux:
                exec_env['PREFIX'] = '/data/data/com.termux/files/usr'
            
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
        Get Android system information relevant to Wine compatibility.
        
        Returns:
            Dictionary containing system information.
        """
        try:
            info = {
                "platform": "Android",
                "is_termux": self.is_termux,
                "architecture": platform.machine(),
            }
            
            # Try to get Android API level
            if self.is_termux:
                try:
                    result = subprocess.run(
                        ['getprop', 'ro.build.version.sdk'],
                        capture_output=True,
                        text=True,
                        timeout=5
                    )
                    if result.returncode == 0:
                        info['api_level'] = result.stdout.strip()
                except Exception:
                    pass
            
            return info
        except Exception:
            return {
                "platform": "Android",
                "api_level": "unknown",
                "architecture": "unknown"
            }
    
    def check_compatibility(self) -> Tuple[bool, str]:
        """
        Check if the Android device is compatible with Wine.
        
        Returns:
            Tuple of (is_compatible, reason/message)
        """
        arch = platform.machine()
        
        # Check architecture
        if arch not in ['x86_64', 'aarch64', 'arm64']:
            return False, f"Incompatible architecture: {arch}. Wine requires x86_64 or arm64."
        
        # Check if Termux
        if not self.is_termux:
            return False, "Wine on Android typically requires Termux. Please install Termux and Wine."
        
        # Check if Wine is installed
        wine_paths = self.get_wine_paths()
        wine_found = any(p.exists() for p in wine_paths)
        
        if not wine_found:
            return False, "Wine not found. Install with: pkg install wine"
        
        return True, "System appears compatible with Wine"
    
    def get_storage_paths(self) -> Dict[str, Path]:
        """Get Android storage paths."""
        paths = {}
        
        if self.is_termux:
            paths['home'] = Path.home()
            paths['shared'] = Path('/sdcard')
            paths['downloads'] = Path('/sdcard/Download')
        
        return paths
