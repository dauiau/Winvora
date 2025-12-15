from typing import List, Dict, Optional, Tuple
from pathlib import Path
import subprocess
import shutil
import os
import urllib.request
import tarfile


class WineVersion:
    def __init__(self, version: str, variant: str, path: Path, is_active: bool = False):
        self.version = version
        self.variant = variant  # stable, staging, proton, custom
        self.path = path
        self.is_active = is_active
    
    def __str__(self):
        return f"{self.variant.capitalize()} {self.version}"


class WineVersionManager:
    def __init__(self, config=None):
        from core.config import Config
        self.config = config or Config()
        self.wine_dir = Path.home() / ".local" / "share" / "winvora" / "wine-versions"
        self.wine_dir.mkdir(parents=True, exist_ok=True)
        self.versions: List[WineVersion] = []
        self._scan_versions()
    
    def _scan_versions(self):
        self.versions = []
        
        system_wine = shutil.which("wine")
        if system_wine:
            version = self._get_wine_version(Path(system_wine))
            self.versions.append(WineVersion(
                version or "unknown",
                "system",
                Path(system_wine).parent,
                is_active=True
            ))
        
        if self.wine_dir.exists():
            for version_dir in self.wine_dir.iterdir():
                if version_dir.is_dir():
                    wine_bin = version_dir / "bin" / "wine"
                    if wine_bin.exists():
                        parts = version_dir.name.split('-')
                        variant = parts[0] if len(parts) > 1 else "custom"
                        version = '-'.join(parts[1:]) if len(parts) > 1 else parts[0]
                        
                        self.versions.append(WineVersion(
                            version,
                            variant,
                            version_dir
                        ))
    
    def _get_wine_version(self, wine_path: Path) -> Optional[str]:
        try:
            result = subprocess.run(
                [str(wine_path), "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                return result.stdout.strip().replace("wine-", "")
        except Exception:
            pass
        return None
    
    def list_versions(self) -> List[WineVersion]:
        return self.versions
    
    def get_active_version(self) -> Optional[WineVersion]:
        for version in self.versions:
            if version.is_active:
                return version
        return None
    
    def set_active_version(self, version: WineVersion) -> Tuple[bool, str]:
        for v in self.versions:
            v.is_active = False
        
        version.is_active = True
        
        wine_path = version.path / "bin" / "wine"
        if version.variant == "system":
            wine_path = version.path / "wine"
        
        self.config.set("wine_path", str(wine_path))
        self.config.save()
        
        return True, f"Switched to {version}"
    
    def download_wine_version(self, variant: str, version: str,
                             progress_callback=None) -> Tuple[bool, str]:
        if progress_callback:
            progress_callback(10, f"Downloading Wine {variant} {version}...")
        
        download_urls = {
            "staging": f"https://github.com/wine-staging/wine-staging/archive/v{version}.tar.gz",
            "proton": f"https://github.com/ValveSoftware/Proton/archive/refs/tags/proton-{version}.tar.gz",
        }
        
        url = download_urls.get(variant)
        if not url:
            return False, f"Unknown variant: {variant}"
        
        try:
            cache_dir = Path.home() / ".cache" / "winvora" / "wine"
            cache_dir.mkdir(parents=True, exist_ok=True)
            
            tar_file = cache_dir / f"{variant}-{version}.tar.gz"
            
            if not tar_file.exists():
                if progress_callback:
                    progress_callback(30, "Downloading...")
                urllib.request.urlretrieve(url, tar_file)
            
            if progress_callback:
                progress_callback(60, "Extracting...")
            
            install_dir = self.wine_dir / f"{variant}-{version}"
            install_dir.mkdir(parents=True, exist_ok=True)
            
            with tarfile.open(tar_file, 'r:gz') as tar:
                tar.extractall(install_dir)
            
            if progress_callback:
                progress_callback(100, "Downloaded!")
            
            self._scan_versions()
            return True, f"Downloaded Wine {variant} {version}"
            
        except Exception as e:
            return False, f"Download failed: {e}"
    
    def delete_version(self, version: WineVersion) -> Tuple[bool, str]:
        if version.variant == "system":
            return False, "Cannot delete system Wine"
        
        if version.is_active:
            return False, "Cannot delete active Wine version"
        
        try:
            shutil.rmtree(version.path)
            self._scan_versions()
            return True, f"Deleted {version}"
        except Exception as e:
            return False, f"Failed to delete: {e}"
    
    def set_prefix_wine_version(self, prefix_name: str, wine_version: WineVersion) -> Tuple[bool, str]:
        prefix_config_file = self.config.get_config_dir() / "prefix_wine_versions.json"
        
        import json
        data = {}
        if prefix_config_file.exists():
            try:
                with open(prefix_config_file, 'r') as f:
                    data = json.load(f)
            except Exception:
                pass
        
        wine_path = wine_version.path / "bin" / "wine"
        if wine_version.variant == "system":
            wine_path = wine_version.path / "wine"
        
        data[prefix_name] = str(wine_path)
        
        try:
            with open(prefix_config_file, 'w') as f:
                json.dump(data, f, indent=2)
            return True, f"Set {prefix_name} to use {wine_version}"
        except Exception as e:
            return False, f"Failed to save: {e}"
    
    def get_prefix_wine_version(self, prefix_name: str) -> Optional[Path]:
        prefix_config_file = self.config.get_config_dir() / "prefix_wine_versions.json"
        
        if not prefix_config_file.exists():
            return None
        
        import json
        try:
            with open(prefix_config_file, 'r') as f:
                data = json.load(f)
                wine_path = data.get(prefix_name)
                if wine_path:
                    return Path(wine_path)
        except Exception:
            pass
        
        return None
