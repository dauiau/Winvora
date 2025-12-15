from pathlib import Path
from typing import Optional, Dict
import subprocess
import platform
import os


class LinuxPlatform:
    def __init__(self):
        self.platform_name = "Linux"
    
    def get_wine_paths(self) -> list[Path]:
        return [
            Path("/usr/bin/wine"),
            Path("/usr/local/bin/wine"),
            Path("/opt/wine/bin/wine"),
            Path.home() / ".local" / "bin" / "wine",
        ]
    
    def get_default_prefix_location(self) -> Path:
        xdg_data_home = os.getenv("XDG_DATA_HOME")
        if xdg_data_home:
            return Path(xdg_data_home) / "winvora" / "prefixes"
        return Path.home() / ".local" / "share" / "winvora" / "prefixes"
    
    def execute_wine_command(self, command: list[str], env: Optional[Dict] = None) -> Optional[subprocess.CompletedProcess]:
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
        info = {
            "platform": self.platform_name,
            "architecture": platform.machine(),
        }
        
        try:
            with open("/etc/os-release", "r") as f:
                for line in f:
                    if line.startswith("PRETTY_NAME="):
                        info["distribution"] = line.split("=")[1].strip().strip('"')
                        break
        except Exception:
            pass
        
        try:
            info["version"] = platform.release()
        except Exception:
            pass
        
        return info
    
    def get_distribution(self) -> str:
        try:
            with open("/etc/os-release", "r") as f:
                for line in f:
                    if line.startswith("ID="):
                        return line.split("=")[1].strip().strip('"')
        except Exception:
            pass
        
        return "unknown"
    
    def check_wayland(self) -> bool:
        return os.getenv("WAYLAND_DISPLAY") is not None
    
    def check_x11(self) -> bool:
        return os.getenv("DISPLAY") is not None
