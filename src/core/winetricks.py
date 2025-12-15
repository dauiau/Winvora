from typing import Optional, List, Dict, Tuple
from pathlib import Path
import subprocess
import shutil
import os


class WineTricksManager:
    def __init__(self, wine_manager=None):
        self.wine_manager = wine_manager
        self.winetricks_path = self._find_winetricks()
    
    def _find_winetricks(self) -> Optional[Path]:
        winetricks_cmd = shutil.which("winetricks")
        if winetricks_cmd:
            return Path(winetricks_cmd)
        
        common_paths = [
            Path("/usr/bin/winetricks"),
            Path("/usr/local/bin/winetricks"),
            Path("/opt/homebrew/bin/winetricks"),
            Path.home() / ".local" / "bin" / "winetricks",
        ]
        
        for path in common_paths:
            if path.exists():
                return path
        
        return None
    
    def is_installed(self) -> bool:
        return self.winetricks_path is not None and self.winetricks_path.exists()
    
    def install_dll(self, prefix_path: Path, dll_name: str) -> Tuple[bool, str]:
        if not self.is_installed():
            return False, "Winetricks is not installed"
        
        env = os.environ.copy()
        env["WINEPREFIX"] = str(prefix_path)
        
        try:
            result = subprocess.run(
                [str(self.winetricks_path), dll_name],
                env=env,
                capture_output=True,
                text=True,
                timeout=300
            )
            
            if result.returncode == 0:
                return True, f"Successfully installed {dll_name}"
            else:
                return False, f"Failed to install {dll_name}: {result.stderr}"
        except subprocess.TimeoutExpired:
            return False, f"Installation of {dll_name} timed out"
        except Exception as e:
            return False, f"Error installing {dll_name}: {e}"
    
    def install_font(self, prefix_path: Path, font_name: str) -> Tuple[bool, str]:
        return self.install_dll(prefix_path, font_name)
    
    def install_package(self, prefix_path: Path, package: str) -> Tuple[bool, str]:
        return self.install_dll(prefix_path, package)
    
    def get_common_dlls(self) -> List[str]:
        return [
            "vcrun2019",
            "vcrun2017",
            "vcrun2015",
            "vcrun2013",
            "vcrun2012",
            "vcrun2010",
            "vcrun2008",
            "vcrun2005",
            "dotnet48",
            "dotnet472",
            "dotnet462",
            "dotnet452",
            "d3dx9",
            "d3dcompiler_47",
            "dxvk",
        ]
    
    def get_common_fonts(self) -> List[str]:
        return [
            "corefonts",
            "tahoma",
            "consolas",
            "liberation",
        ]
    
    def run_winetricks_gui(self, prefix_path: Path) -> Tuple[bool, str]:
        if not self.is_installed():
            return False, "Winetricks is not installed"
        
        env = os.environ.copy()
        env["WINEPREFIX"] = str(prefix_path)
        
        try:
            subprocess.Popen(
                [str(self.winetricks_path)],
                env=env,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True
            )
            return True, "Winetricks GUI launched"
        except Exception as e:
            return False, f"Failed to launch winetricks: {e}"
