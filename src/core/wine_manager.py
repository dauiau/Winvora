from typing import Optional, Dict, List, Tuple
from pathlib import Path
import subprocess
import shutil
import os
import json
import shlex


class WineManager:
    def __init__(self, wine_path: Optional[Path] = None, config=None):
        from core.config import Config
        self.config = config or Config()
        self.wine_path = wine_path or self._find_wine()
        self.prefixes: Dict[str, Path] = {}
        self._load_prefixes()
    
    def _find_wine(self) -> Optional[Path]:
        configured_path = self.config.get("wine_path")
        if configured_path and Path(configured_path).exists():
            return Path(configured_path)
        
        wine_cmd = shutil.which("wine")
        if wine_cmd:
            return Path(wine_cmd)
        
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
    
    def _load_prefixes(self):
        from platforms import get_platform
        platform = get_platform()
        prefix_dir = platform.get_default_prefix_location()
        
        if prefix_dir.exists():
            for item in prefix_dir.iterdir():
                if item.is_dir() and (item / "system.reg").exists():
                    self.prefixes[item.name] = item
        
        config_prefixes = self.config.get("prefixes", {})
        for name, path_str in config_prefixes.items():
            path = Path(path_str)
            if path.exists():
                self.prefixes[name] = path
    
    def list_prefixes(self) -> List[str]:
        self._load_prefixes()
        return sorted(self.prefixes.keys())
    
    def create_prefix(self, name: str, windows_version: str = "win10") -> Tuple[bool, str]:
        if not self.verify_wine_installation():
            return False, "Wine is not installed or not accessible"
        
        if name in self.prefixes:
            return False, f"Prefix '{name}' already exists"
        
        from platforms import get_platform
        platform = get_platform()
        prefix_dir = platform.get_default_prefix_location()
        prefix_path = prefix_dir / name
        
        if prefix_path.exists():
            return False, f"Directory already exists at {prefix_path}"
        
        try:
            prefix_path.mkdir(parents=True, exist_ok=False)
        except OSError as e:
            return False, f"Failed to create directory: {e}"
        
        env = os.environ.copy()
        env["WINEPREFIX"] = str(prefix_path)
        env["WINEARCH"] = "win64"
        
        try:
            result = subprocess.run(
                [str(self.wine_path), "wineboot", "--init"],
                env=env,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode != 0:
                shutil.rmtree(prefix_path, ignore_errors=True)
                return False, f"Wine initialization failed: {result.stderr}"
            
            self._set_windows_version(prefix_path, windows_version)
            self.prefixes[name] = prefix_path
            
            config_prefixes = self.config.get("prefixes", {})
            config_prefixes[name] = str(prefix_path)
            self.config.set("prefixes", config_prefixes)
            self.config.save()
            
            return True, f"Prefix '{name}' created successfully at {prefix_path}"
            
        except subprocess.TimeoutExpired:
            shutil.rmtree(prefix_path, ignore_errors=True)
            return False, "Wine initialization timed out"
        except Exception as e:
            shutil.rmtree(prefix_path, ignore_errors=True)
            return False, f"Failed to create prefix: {e}"
    
    def _set_windows_version(self, prefix_path: Path, version: str):
        version_map = {
            "win10": "win10",
            "win8": "win8",
            "win7": "win7",
            "winxp": "winxp",
        }
        
        wine_version = version_map.get(version, "win10")
        
        env = os.environ.copy()
        env["WINEPREFIX"] = str(prefix_path)
        
        try:
            subprocess.run(
                [str(self.wine_path), "winecfg", f"/v:{wine_version}"],
                env=env,
                capture_output=True,
                timeout=10
            )
        except (subprocess.TimeoutExpired, Exception):
            pass
    
    def delete_prefix(self, name: str) -> Tuple[bool, str]:
        if name not in self.prefixes:
            return False, f"Prefix '{name}' not found"
        
        prefix_path = self.prefixes[name]
        
        try:
            shutil.rmtree(prefix_path)
            del self.prefixes[name]
            
            config_prefixes = self.config.get("prefixes", {})
            if name in config_prefixes:
                del config_prefixes[name]
                self.config.set("prefixes", config_prefixes)
                self.config.save()
            
            return True, f"Prefix '{name}' deleted successfully"
            
        except Exception as e:
            return False, f"Failed to delete prefix: {e}"
    
    def get_prefix_info(self, name: str) -> Optional[Dict]:
        if name not in self.prefixes:
            return None
        
        prefix_path = self.prefixes[name]
        
        info = {
            "name": name,
            "path": str(prefix_path),
            "exists": prefix_path.exists(),
        }
        
        if prefix_path.exists():
            system_reg = prefix_path / "system.reg"
            if system_reg.exists():
                info["windows_version"] = self._get_windows_version(prefix_path)
        
        return info
    
    def _get_windows_version(self, prefix_path: Path) -> str:
        system_reg = prefix_path / "system.reg"
        if not system_reg.exists():
            return "Unknown"
        
        try:
            with open(system_reg, 'r', encoding='utf-16-le', errors='ignore') as f:
                content = f.read()
                if "Windows 10" in content or "win10" in content:
                    return "Windows 10"
                elif "Windows 8" in content or "win8" in content:
                    return "Windows 8"
                elif "Windows 7" in content or "win7" in content:
                    return "Windows 7"
                elif "Windows XP" in content or "winxp" in content:
                    return "Windows XP"
        except Exception:
            pass
        
        return "Unknown"
    
    def install_application(self, prefix_name: str, installer_path: Path, 
                          args: Optional[List[str]] = None) -> Tuple[bool, str]:
        if not self.verify_wine_installation():
            return False, "Wine is not installed"
        
        if prefix_name not in self.prefixes:
            return False, f"Prefix '{prefix_name}' not found"
        
        if not installer_path.exists():
            return False, f"Installer not found: {installer_path}"
        
        prefix_path = self.prefixes[prefix_name]
        env = os.environ.copy()
        env["WINEPREFIX"] = str(prefix_path)
        
        cmd = [str(self.wine_path), str(installer_path)]
        if args:
            cmd.extend(args)
        
        try:
            result = subprocess.run(
                cmd,
                env=env,
                capture_output=True,
                text=True,
                timeout=300
            )
            
            if result.returncode == 0:
                return True, "Installation completed"
            else:
                return False, f"Installation failed: {result.stderr}"
                
        except subprocess.TimeoutExpired:
            return False, "Installation timed out"
        except Exception as e:
            return False, f"Installation error: {e}"
    
    def run_application(self, prefix_name: str, executable_path: Path,
                       args: Optional[List[str]] = None,
                       background: bool = False) -> Tuple[bool, str]:
        if not self.verify_wine_installation():
            return False, "Wine is not installed"
        
        if prefix_name not in self.prefixes:
            return False, f"Prefix '{prefix_name}' not found"
        
        if not executable_path.exists():
            return False, f"Executable not found: {executable_path}"
        
        prefix_path = self.prefixes[prefix_name]
        env = os.environ.copy()
        env["WINEPREFIX"] = str(prefix_path)
        
        cmd = [str(self.wine_path), str(executable_path)]
        if args:
            cmd.extend(args)
        
        try:
            if background:
                subprocess.Popen(
                    cmd,
                    env=env,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    start_new_session=True
                )
                return True, f"Application started"
            else:
                result = subprocess.run(
                    cmd,
                    env=env,
                    capture_output=True,
                    text=True,
                    timeout=300
                )
                
                if result.returncode == 0:
                    return True, "Application exited normally"
                else:
                    return False, f"Application failed: {result.stderr}"
                    
        except subprocess.TimeoutExpired:
            return False, "Application timed out"
        except Exception as e:
            return False, f"Failed to run application: {e}"
    
    def configure_prefix(self, prefix_name: str) -> Tuple[bool, str]:
        if not self.verify_wine_installation():
            return False, "Wine is not installed"
        
        if prefix_name not in self.prefixes:
            return False, f"Prefix '{prefix_name}' not found"
        
        prefix_path = self.prefixes[prefix_name]
        env = os.environ.copy()
        env["WINEPREFIX"] = str(prefix_path)
        
        try:
            subprocess.Popen(
                [str(self.wine_path), "winecfg"],
                env=env,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True
            )
            return True, "Wine configuration opened"
        except Exception as e:
            return False, f"Failed to open configuration: {e}"
    
    def get_running_processes(self) -> List[Dict]:
        processes = []
        
        try:
            result = subprocess.run(
                ["ps", "aux"],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                for line in result.stdout.splitlines():
                    if "wine" in line.lower() or "wineserver" in line:
                        parts = line.split(None, 10)
                        if len(parts) >= 11:
                            processes.append({
                                "pid": parts[1],
                                "command": parts[10]
                            })
                        
        except (subprocess.TimeoutExpired, Exception):
            pass
        
        return processes
    
    def kill_process(self, pid: str) -> Tuple[bool, str]:
        try:
            subprocess.run(
                ["kill", pid],
                capture_output=True,
                timeout=5
            )
            return True, f"Process {pid} killed"
        except Exception as e:
            return False, f"Failed to kill process: {e}"
    
    def kill_all_wine(self) -> Tuple[bool, str]:
        try:
            subprocess.run(
                ["killall", "-9", "wine", "wineserver"],
                capture_output=True,
                timeout=5
            )
            return True, "All Wine processes killed"
        except Exception as e:
            return False, f"Failed to kill processes: {e}"
    
    def get_prefix_programs(self, prefix_name: str) -> List[Path]:
        if prefix_name not in self.prefixes:
            return []
        
        prefix_path = self.prefixes[prefix_name]
        programs_dir = prefix_path / "drive_c" / "Program Files"
        
        executables = []
        if programs_dir.exists():
            for exe in programs_dir.rglob("*.exe"):
                executables.append(exe)
        
        return executables
