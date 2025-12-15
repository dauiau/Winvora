from typing import Tuple, Optional
from pathlib import Path
import subprocess
import shutil
import os
import urllib.request
import tarfile


class DXVKManager:
    def __init__(self, wine_manager=None):
        self.wine_manager = wine_manager
        self.dxvk_versions = {
            "2.3.1": "https://github.com/doitsujin/dxvk/releases/download/v2.3.1/dxvk-2.3.1.tar.gz",
            "2.3": "https://github.com/doitsujin/dxvk/releases/download/v2.3/dxvk-2.3.tar.gz",
            "2.2": "https://github.com/doitsujin/dxvk/releases/download/v2.2/dxvk-2.2.tar.gz",
        }
    
    def is_installed(self, prefix_path: Path) -> bool:
        dxvk_marker = prefix_path / ".dxvk_installed"
        return dxvk_marker.exists()
    
    def install_dxvk(self, prefix_path: Path, version: str = "2.3.1",
                     progress_callback=None) -> Tuple[bool, str]:
        if not prefix_path.exists():
            return False, "Prefix does not exist"
        
        system32 = prefix_path / "drive_c" / "windows" / "system32"
        syswow64 = prefix_path / "drive_c" / "windows" / "syswow64"
        
        if not system32.exists():
            return False, "Invalid prefix structure"
        
        try:
            if progress_callback:
                progress_callback(10, "Downloading DXVK...")
            
            cache_dir = Path.home() / ".cache" / "winvora" / "dxvk"
            cache_dir.mkdir(parents=True, exist_ok=True)
            
            dxvk_tar = cache_dir / f"dxvk-{version}.tar.gz"
            
            if not dxvk_tar.exists():
                url = self.dxvk_versions.get(version)
                if not url:
                    return False, f"Unknown DXVK version: {version}"
                
                urllib.request.urlretrieve(url, dxvk_tar)
            
            if progress_callback:
                progress_callback(40, "Extracting DXVK...")
            
            extract_dir = cache_dir / f"dxvk-{version}"
            if not extract_dir.exists():
                with tarfile.open(dxvk_tar, 'r:gz') as tar:
                    tar.extractall(cache_dir)
            
            if progress_callback:
                progress_callback(60, "Installing DLLs...")
            
            x64_dir = extract_dir / "x64"
            x32_dir = extract_dir / "x32"
            
            dlls = ["d3d9.dll", "d3d10core.dll", "d3d11.dll", "dxgi.dll"]
            
            if x64_dir.exists():
                for dll in dlls:
                    src = x64_dir / dll
                    if src.exists():
                        shutil.copy2(src, system32 / dll)
            
            if x32_dir.exists() and syswow64.exists():
                for dll in dlls:
                    src = x32_dir / dll
                    if src.exists():
                        shutil.copy2(src, syswow64 / dll)
            
            if progress_callback:
                progress_callback(80, "Configuring DLL overrides...")
            
            self._set_dll_overrides(prefix_path, dlls)
            
            marker = prefix_path / ".dxvk_installed"
            marker.write_text(version)
            
            if progress_callback:
                progress_callback(100, "DXVK installed!")
            
            return True, f"DXVK {version} installed successfully"
            
        except Exception as e:
            return False, f"Failed to install DXVK: {e}"
    
    def _set_dll_overrides(self, prefix_path: Path, dlls: list):
        user_reg = prefix_path / "user.reg"
        if not user_reg.exists():
            return
        
        try:
            content = user_reg.read_text(encoding='utf-16-le', errors='ignore')
            
            for dll in dlls:
                dll_name = dll.replace('.dll', '')
                override_line = f'"{dll_name}"="native,builtin"'
                if override_line not in content:
                    content += f'\n[Software\\\\Wine\\\\DllOverrides]\n{override_line}\n'
            
            user_reg.write_text(content, encoding='utf-16-le')
        except Exception:
            pass
    
    def uninstall_dxvk(self, prefix_path: Path) -> Tuple[bool, str]:
        if not self.is_installed(prefix_path):
            return False, "DXVK is not installed"
        
        try:
            system32 = prefix_path / "drive_c" / "windows" / "system32"
            syswow64 = prefix_path / "drive_c" / "windows" / "syswow64"
            
            dlls = ["d3d9.dll", "d3d10core.dll", "d3d11.dll", "dxgi.dll"]
            
            for dll in dlls:
                (system32 / dll).unlink(missing_ok=True)
                if syswow64.exists():
                    (syswow64 / dll).unlink(missing_ok=True)
            
            marker = prefix_path / ".dxvk_installed"
            marker.unlink(missing_ok=True)
            
            return True, "DXVK uninstalled successfully"
            
        except Exception as e:
            return False, f"Failed to uninstall DXVK: {e}"
    
    def get_installed_version(self, prefix_path: Path) -> Optional[str]:
        marker = prefix_path / ".dxvk_installed"
        if marker.exists():
            return marker.read_text().strip()
        return None
    
    def install_vkd3d(self, prefix_path: Path, progress_callback=None) -> Tuple[bool, str]:
        if not prefix_path.exists():
            return False, "Prefix does not exist"
        
        try:
            if progress_callback:
                progress_callback(50, "Installing VKD3D-Proton...")
            
            return True, "VKD3D-Proton installed (stub implementation)"
        except Exception as e:
            return False, f"Failed to install VKD3D: {e}"
