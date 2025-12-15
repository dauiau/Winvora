"""
Wine Manager - Core functionality for managing Wine environments.

This module provides the core logic for interacting with Wine as an external
dependency, managing Wine prefixes, and running Windows applications.
"""

from typing import Optional, Dict, List, Tuple
from pathlib import Path
import subprocess
import shutil
import os
import json
import shlex


class WineManager:
    """
    Manages Wine environments and application execution.
    
    Wine is treated as an external dependency and must be installed separately.
    """
    
    def __init__(self, wine_path: Optional[Path] = None, config=None):
        """
        Initialize the Wine Manager.
        
        Args:
            wine_path: Path to Wine executable. If None, will search system PATH.
            config: Config object for settings. If None, creates new one.
        """
        from core.config import Config
        self.config = config or Config()
        self.wine_path = wine_path or self._find_wine()
        self.prefixes: Dict[str, Path] = {}
        self._load_prefixes()
    
    def _find_wine(self) -> Optional[Path]:
        """
        Find Wine executable in system PATH or common locations.
        
        Returns:
            Path to Wine executable or None if not found.
        """
        # Check config first
        configured_path = self.config.get("wine_path")
        if configured_path and Path(configured_path).exists():
            return Path(configured_path)
        
        # Check system PATH
        wine_cmd = shutil.which("wine")
        if wine_cmd:
            return Path(wine_cmd)
        
        # Check common installation locations
        common_paths = [
            Path("/usr/bin/wine"),
            Path("/usr/local/bin/wine"),
            Path("/opt/homebrew/bin/wine"),
            Path.home() / ".local" / "bin" / "wine",
        ]
        
        for path in common_paths:
            if path.exists():
                return path
        
        return None
    
    def verify_wine_installation(self) -> bool:
        """
        Verify that Wine is installed and accessible.
        
        Returns:
            True if Wine is found, False otherwise.
        """
        if not self.wine_path or not self.wine_path.exists():
            self.wine_path = self._find_wine()
        
        if not self.wine_path:
            return False
        
        try:
            result = subprocess.run(
                [str(self.wine_path), "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False
    
    def get_wine_version(self) -> Optional[str]:
        """
        Get the installed Wine version.
        
        Returns:
            Wine version string or None if not available.
        """
        if not self.verify_wine_installation():
            return None
        
        try:
            result = subprocess.run(
                [str(self.wine_path), "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                return result.stdout.strip()
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass
        
        return None
    
    def _load_prefixes(self) -> None:
        """Load all existing Wine prefixes from disk."""
        prefixes_dir = self.config.get_prefixes_dir()
        
        if not prefixes_dir.exists():
            return
        
        for item in prefixes_dir.iterdir():
            if item.is_dir():
                # Check if it's a valid Wine prefix (has drive_c)
                if (item / "drive_c").exists():
                    self.prefixes[item.name] = item
    
    def create_prefix(self, name: str, path: Optional[Path] = None, 
                     windows_version: str = "win10") -> Tuple[bool, str]:
        """
        Create a new Wine prefix.
        
        Args:
            name: Name identifier for the prefix
            path: Path where the prefix should be created. If None, uses default location.
            windows_version: Windows version to emulate (win10, win7, winxp, etc.)
            
        Returns:
            Tuple of (success, message)
        """
        if not self.verify_wine_installation():
            return False, "Wine is not installed or not accessible"
        
        # Determine prefix path
        if path is None:
            path = self.config.get_prefixes_dir() / name
        
        # Check if prefix already exists
        if path.exists():
            return False, f"Prefix '{name}' already exists at {path}"
        
        try:
            # Create directory
            path.mkdir(parents=True, exist_ok=True)
            
            # Set up environment
            env = os.environ.copy()
            env["WINEPREFIX"] = str(path)
            env["WINEARCH"] = self.config.get("default_architecture", "win64")
            
            # Initialize prefix with wineboot
            result = subprocess.run(
                [str(self.wine_path), "wineboot", "-i"],
                env=env,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode != 0:
                return False, f"Failed to initialize prefix: {result.stderr}"
            
            # Set Windows version if specified
            if windows_version:
                self._set_windows_version(path, windows_version)
            
            # Save prefix metadata
            metadata = {
                "name": name,
                "path": str(path),
                "windows_version": windows_version,
                "created": str(Path.cwd()),  # Could use datetime here
            }
            
            metadata_file = path / "winvora.json"
            with open(metadata_file, 'w') as f:
                json.dump(metadata, f, indent=2)
            
            # Add to loaded prefixes
            self.prefixes[name] = path
            
            return True, f"Prefix '{name}' created successfully"
            
        except subprocess.TimeoutExpired:
            return False, "Timeout while creating prefix"
        except Exception as e:
            return False, f"Error creating prefix: {str(e)}"
    
    def _set_windows_version(self, prefix_path: Path, version: str) -> None:
        """Set Windows version for a prefix using winecfg."""
        try:
            env = os.environ.copy()
            env["WINEPREFIX"] = str(prefix_path)
            
            # Use reg add to set Windows version
            subprocess.run(
                [str(self.wine_path), "reg", "add",
                 "HKLM\\Software\\Microsoft\\Windows NT\\CurrentVersion",
                 "/v", "CurrentVersion", "/d", version, "/f"],
                env=env,
                capture_output=True,
                timeout=10
            )
        except Exception:
            pass  # Non-critical operation
    
    def delete_prefix(self, name: str) -> Tuple[bool, str]:
        """
        Delete a Wine prefix.
        
        Args:
            name: Name of the prefix to delete
            
        Returns:
            Tuple of (success, message)
        """
        if name not in self.prefixes:
            return False, f"Prefix '{name}' not found"
        
        try:
            prefix_path = self.prefixes[name]
            shutil.rmtree(prefix_path)
            del self.prefixes[name]
            return True, f"Prefix '{name}' deleted successfully"
        except Exception as e:
            return False, f"Error deleting prefix: {str(e)}"
    
    def list_prefixes(self) -> List[str]:
        """
        List all managed Wine prefixes.
        
        Returns:
            List of prefix names.
        """
        self._load_prefixes()  # Refresh list
        return list(self.prefixes.keys())
    
    def get_prefix_path(self, name: str) -> Optional[Path]:
        """
        Get the path to a prefix.
        
        Args:
            name: Name of the prefix
            
        Returns:
            Path to the prefix or None if not found.
        """
        return self.prefixes.get(name)
    
    def get_prefix_info(self, name: str) -> Optional[Dict]:
        """
        Get information about a prefix.
        
        Args:
            name: Name of the prefix
            
        Returns:
            Dictionary with prefix information or None if not found.
        """
        if name not in self.prefixes:
            return None
        
        prefix_path = self.prefixes[name]
        metadata_file = prefix_path / "winvora.json"
        
        info = {
            "name": name,
            "path": str(prefix_path),
            "exists": prefix_path.exists(),
            "has_drive_c": (prefix_path / "drive_c").exists(),
        }
        
        # Load metadata if available
        if metadata_file.exists():
            try:
                with open(metadata_file, 'r') as f:
                    metadata = json.load(f)
                    info.update(metadata)
            except Exception:
                pass
        
        return info
    
    def run_application(self, prefix: str, executable: Path, 
                       args: Optional[List[str]] = None,
                       background: bool = False) -> Tuple[bool, str]:
        """
        Run a Windows application in a specific Wine prefix.
        
        Args:
            prefix: Name of the Wine prefix to use
            executable: Path to the Windows executable
            args: Additional arguments to pass to the application
            background: Run in background without waiting
            
        Returns:
            Tuple of (success, message/output)
        """
        if not self.verify_wine_installation():
            return False, "Wine is not installed"
        
        if prefix not in self.prefixes:
            return False, f"Prefix '{prefix}' not found"
        
        if not executable.exists() and not str(executable).startswith('C:'):
            return False, f"Executable not found: {executable}"
        
        try:
            prefix_path = self.prefixes[prefix]
            env = os.environ.copy()
            env["WINEPREFIX"] = str(prefix_path)
            
            # Build command
            cmd = [str(self.wine_path), str(executable)]
            if args:
                cmd.extend(args)
            
            if background:
                # Start in background
                subprocess.Popen(
                    cmd,
                    env=env,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    start_new_session=True
                )
                return True, "Application started in background"
            else:
                # Run and wait
                result = subprocess.run(
                    cmd,
                    env=env,
                    capture_output=True,
                    text=True,
                    timeout=300  # 5 minute timeout
                )
                
                if result.returncode == 0:
                    return True, result.stdout
                else:
                    return False, result.stderr or "Application exited with error"
                    
        except subprocess.TimeoutExpired:
            return False, "Application timeout"
        except Exception as e:
            return False, f"Error running application: {str(e)}"
    
    def install_application(self, prefix: str, installer: Path) -> Tuple[bool, str]:
        """
        Install a Windows application from an installer.
        
        Args:
            prefix: Name of the Wine prefix
            installer: Path to installer (.exe or .msi)
            
        Returns:
            Tuple of (success, message)
        """
        return self.run_application(prefix, installer, background=False)
    
    def open_winecfg(self, prefix: str) -> Tuple[bool, str]:
        """
        Open winecfg for a specific prefix.
        
        Args:
            prefix: Name of the Wine prefix
            
        Returns:
            Tuple of (success, message)
        """
        if not self.verify_wine_installation():
            return False, "Wine is not installed"
        
        if prefix not in self.prefixes:
            return False, f"Prefix '{prefix}' not found"
        
        try:
            prefix_path = self.prefixes[prefix]
            env = os.environ.copy()
            env["WINEPREFIX"] = str(prefix_path)
            
            subprocess.Popen(
                [str(self.wine_path), "winecfg"],
                env=env,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True
            )
            return True, "winecfg opened"
        except Exception as e:
            return False, f"Error opening winecfg: {str(e)}"
    
    def get_running_processes(self) -> List[Dict]:
        """
        Get list of running Wine processes.
        
        Returns:
            List of dictionaries with process information.
        """
        processes = []
        
        try:
            result = subprocess.run(
                ["pgrep", "-a", "wine"],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                for line in result.stdout.strip().split('\n'):
                    if line:
                        parts = line.split(None, 1)
                        if len(parts) == 2:
                            processes.append({
                                "pid": parts[0],
                                "command": parts[1]
                            })
        except Exception:
            pass
        
        return processes
    
    def kill_process(self, pid: str) -> Tuple[bool, str]:
        """
        Kill a specific Wine process.
        
        Args:
            pid: Process ID to kill
            
        Returns:
            Tuple of (success, message)
        """
        try:
            subprocess.run(["kill", pid], check=True)
            return True, f"Process {pid} killed"
        except subprocess.CalledProcessError:
            return False, f"Failed to kill process {pid}"
    
    def kill_all_wine(self) -> Tuple[bool, str]:
        """
        Kill all Wine processes.
        
        Returns:
            Tuple of (success, message)
        """
        try:
            subprocess.run(["pkill", "wine"], check=False)
            subprocess.run(["pkill", "wineserver"], check=False)
            return True, "All Wine processes killed"
        except Exception as e:
            return False, f"Error killing processes: {str(e)}"
