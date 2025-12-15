from pathlib import Path
from typing import Optional, Dict
import subprocess
import platform
import os


class MacOSPlatform:
    def __init__(self):
        self.platform_name = "macOS"
    
    def get_wine_paths(self) -> list[Path]:
        return [
            Path("/opt/homebrew/bin/wine"),
            Path("/usr/local/bin/wine"),
            Path("/opt/local/bin/wine"),
            Path.home() / ".local" / "bin" / "wine",
            Path("/Applications/Wine Stable.app/Contents/Resources/wine/bin/wine"),
        ]
    
    def get_default_prefix_location(self) -> Path:
        return Path.home() / "Library" / "Application Support" / "Winvora" / "prefixes"
    
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
            "version": platform.mac_ver()[0],
            "architecture": platform.machine(),
        }
        
        if platform.machine() == "arm64":
            info["is_apple_silicon"] = True
        else:
            info["is_apple_silicon"] = False
        
        return info
    
    def is_apple_silicon(self) -> bool:
        return platform.machine() == "arm64"
    
    def check_rosetta(self) -> bool:
        if not self.is_apple_silicon():
            return False
        
        try:
            result = subprocess.run(
                ["pgrep", "-q", "oahd"],
                capture_output=True,
                timeout=5
            )
            return result.returncode == 0
        except Exception:
            return False
    
    def get_homebrew_prefix(self) -> Optional[Path]:
        if self.is_apple_silicon():
            homebrew_path = Path("/opt/homebrew")
        else:
            homebrew_path = Path("/usr/local")
        
        if homebrew_path.exists():
            return homebrew_path
        
        return None
