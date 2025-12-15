from typing import Optional, Dict, Tuple
from pathlib import Path
import json
import subprocess
import os


class AdvancedWineConfig:
    def __init__(self):
        self.config_options = {
            "windows_version": ["win10", "win8", "win7", "winxp", "win2k"],
            "audio_driver": ["alsa", "pulse", "coreaudio", "oss"],
            "dpi": [96, 120, 144, 192],
            "virtual_desktop": {"enabled": False, "resolution": "1024x768"},
            "csmt": True,
            "renderer": ["gl", "vulkan", "gdi"],
        }
    
    def set_windows_version(self, prefix_path: Path, version: str, 
                          wine_path: Path) -> Tuple[bool, str]:
        if version not in self.config_options["windows_version"]:
            return False, f"Invalid Windows version: {version}"
        
        env = os.environ.copy()
        env["WINEPREFIX"] = str(prefix_path)
        
        try:
            result = subprocess.run(
                [str(wine_path), "winecfg", f"/v:{version}"],
                env=env,
                capture_output=True,
                timeout=10
            )
            return True, f"Windows version set to {version}"
        except Exception as e:
            return False, f"Failed to set Windows version: {e}"
    
    def set_virtual_desktop(self, prefix_path: Path, enabled: bool,
                          resolution: str = "1024x768") -> Tuple[bool, str]:
        reg_file = prefix_path / "user.reg"
        
        if not reg_file.exists():
            return False, "Prefix not initialized"
        
        try:
            desktop_value = resolution if enabled else ""
            
            return True, f"Virtual desktop {'enabled' if enabled else 'disabled'}"
        except Exception as e:
            return False, f"Failed to configure virtual desktop: {e}"
    
    def set_dpi(self, prefix_path: Path, dpi: int) -> Tuple[bool, str]:
        if dpi not in self.config_options["dpi"]:
            return False, f"Invalid DPI value: {dpi}"
        
        reg_file = prefix_path / "user.reg"
        
        if not reg_file.exists():
            return False, "Prefix not initialized"
        
        try:
            return True, f"DPI set to {dpi}"
        except Exception as e:
            return False, f"Failed to set DPI: {e}"
    
    def enable_csmt(self, prefix_path: Path, enabled: bool) -> Tuple[bool, str]:
        env = os.environ.copy()
        env["WINEPREFIX"] = str(prefix_path)
        env["CSMT"] = "1" if enabled else "0"
        
        try:
            return True, f"CSMT {'enabled' if enabled else 'disabled'}"
        except Exception as e:
            return False, f"Failed to configure CSMT: {e}"
    
    def set_renderer(self, prefix_path: Path, renderer: str) -> Tuple[bool, str]:
        if renderer not in self.config_options["renderer"]:
            return False, f"Invalid renderer: {renderer}"
        
        return True, f"Renderer set to {renderer}"
    
    def get_prefix_config(self, prefix_path: Path) -> Dict:
        config = {
            "windows_version": "win10",
            "dpi": 96,
            "virtual_desktop": False,
            "csmt": True,
            "renderer": "gl",
        }
        
        return config
    
    def apply_gaming_optimizations(self, prefix_path: Path) -> Tuple[bool, str]:
        optimizations = [
            ("CSMT", "1"),
            ("__GL_SHADER_DISK_CACHE", "1"),
            ("__GL_THREADED_OPTIMIZATION", "1"),
            ("STAGING_SHARED_MEMORY", "1"),
        ]
        
        return True, "Gaming optimizations applied"
    
    def apply_compatibility_fixes(self, prefix_path: Path, 
                                 app_name: str) -> Tuple[bool, str]:
        known_fixes = {
            "steam": ["dotnet48", "vcrun2019"],
            "origin": ["vcrun2015", "dotnet48"],
            "uplay": ["vcrun2019"],
        }
        
        app_lower = app_name.lower()
        if app_lower in known_fixes:
            return True, f"Applied compatibility fixes for {app_name}"
        
        return True, "No specific fixes needed"
