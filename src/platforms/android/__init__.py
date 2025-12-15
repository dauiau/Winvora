from pathlib import Path
from typing import Optional, Dict
import subprocess
import platform
import os


class AndroidPlatform:
    def __init__(self):
        self.platform_name = "Android"
    
    def get_wine_paths(self) -> list[Path]:
        prefix = os.getenv("PREFIX", "/data/data/com.termux/files/usr")
        return [
            Path(prefix) / "bin" / "wine",
            Path("/data/data/com.termux/files/usr/bin/wine"),
            Path.home() / "wine" / "bin" / "wine",
        ]
    
    def get_default_prefix_location(self) -> Path:
        storage = self.get_storage_path()
        return storage / "winvora" / "prefixes"
    
    def get_storage_path(self) -> Path:
        possible_paths = [
            Path("/storage/emulated/0"),
            Path("/sdcard"),
            Path.home() / "storage" / "shared",
        ]
        
        for path in possible_paths:
            if path.exists():
                return path
        
        return Path.home()
    
    def execute_wine_command(self, command: list[str], env: Optional[Dict] = None) -> Optional[subprocess.CompletedProcess]:
        try:
            exec_env = os.environ.copy()
            if env:
                exec_env.update(env)
            
            box64_path = os.getenv("PREFIX", "/data/data/com.termux/files/usr") + "/bin/box64"
            if Path(box64_path).exists():
                command = [box64_path] + command
            
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
            result = subprocess.run(
                ["getprop", "ro.build.version.release"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                info["android_version"] = result.stdout.strip()
        except Exception:
            pass
        
        return info
    
    def is_termux(self) -> bool:
        return os.path.exists("/data/data/com.termux/files")
    
    def get_termux_prefix(self) -> Optional[Path]:
        prefix = os.getenv("PREFIX")
        if prefix:
            return Path(prefix)
        
        default_prefix = Path("/data/data/com.termux/files/usr")
        if default_prefix.exists():
            return default_prefix
        
        return None
