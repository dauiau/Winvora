from typing import Optional, Dict, Tuple, List
from pathlib import Path
import json
import shutil
import time
import os


class CloudSync:
    def __init__(self, config=None):
        from core.config import Config
        self.config = config or Config()
        self.sync_dir = self._get_sync_directory()
        self.metadata_file = self.sync_dir / "sync_metadata.json"
        self.metadata: Dict = {}
        self.load_metadata()
    
    def _get_sync_directory(self) -> Path:
        sync_path = self.config.get("cloud_sync_dir")
        if sync_path:
            return Path(sync_path)
        
        possible_dirs = [
            Path.home() / "Dropbox" / "Winvora",
            Path.home() / "Google Drive" / "Winvora",
            Path.home() / "OneDrive" / "Winvora",
            Path.home() / "iCloud Drive" / "Winvora",
            Path.home() / ".winvora-sync",
        ]
        
        for dir_path in possible_dirs:
            if dir_path.parent.exists():
                dir_path.mkdir(parents=True, exist_ok=True)
                return dir_path
        
        default_sync = Path.home() / ".winvora-sync"
        default_sync.mkdir(parents=True, exist_ok=True)
        return default_sync
    
    def load_metadata(self):
        if self.metadata_file.exists():
            try:
                with open(self.metadata_file, 'r') as f:
                    self.metadata = json.load(f)
            except Exception:
                self.metadata = {}
        else:
            self.metadata = {}
    
    def save_metadata(self):
        try:
            with open(self.metadata_file, 'w') as f:
                json.dump(self.metadata, f, indent=2)
            return True
        except Exception:
            return False
    
    def upload_prefix(self, prefix_name: str, prefix_path: Path) -> Tuple[bool, str]:
        if not prefix_path.exists():
            return False, f"Prefix not found: {prefix_path}"
        
        dest_dir = self.sync_dir / "prefixes" / prefix_name
        dest_dir.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            if dest_dir.exists():
                shutil.rmtree(dest_dir)
            
            shutil.copytree(prefix_path, dest_dir)
            
            self.metadata[prefix_name] = {
                "last_sync": int(time.time()),
                "sync_type": "upload",
                "size_bytes": self._get_dir_size(dest_dir),
            }
            self.save_metadata()
            
            return True, f"Prefix '{prefix_name}' uploaded to cloud"
        except Exception as e:
            return False, f"Upload failed: {e}"
    
    def download_prefix(self, prefix_name: str, dest_path: Path) -> Tuple[bool, str]:
        source_dir = self.sync_dir / "prefixes" / prefix_name
        
        if not source_dir.exists():
            return False, f"Prefix not found in cloud: {prefix_name}"
        
        try:
            if dest_path.exists():
                return False, f"Destination already exists: {dest_path}"
            
            shutil.copytree(source_dir, dest_path)
            
            self.metadata[prefix_name] = {
                "last_sync": int(time.time()),
                "sync_type": "download",
            }
            self.save_metadata()
            
            return True, f"Prefix '{prefix_name}' downloaded from cloud"
        except Exception as e:
            return False, f"Download failed: {e}"
    
    def list_cloud_prefixes(self) -> List[str]:
        prefixes_dir = self.sync_dir / "prefixes"
        if not prefixes_dir.exists():
            return []
        
        return [d.name for d in prefixes_dir.iterdir() if d.is_dir()]
    
    def delete_cloud_prefix(self, prefix_name: str) -> Tuple[bool, str]:
        source_dir = self.sync_dir / "prefixes" / prefix_name
        
        if not source_dir.exists():
            return False, f"Prefix not found in cloud: {prefix_name}"
        
        try:
            shutil.rmtree(source_dir)
            
            if prefix_name in self.metadata:
                del self.metadata[prefix_name]
                self.save_metadata()
            
            return True, f"Cloud prefix '{prefix_name}' deleted"
        except Exception as e:
            return False, f"Delete failed: {e}"
    
    def get_sync_info(self, prefix_name: str) -> Optional[Dict]:
        return self.metadata.get(prefix_name)
    
    def _get_dir_size(self, path: Path) -> int:
        total = 0
        try:
            for entry in path.rglob('*'):
                if entry.is_file():
                    total += entry.stat().st_size
        except Exception:
            pass
        return total
    
    def sync_app_library(self, app_library) -> Tuple[bool, str]:
        library_file = self.sync_dir / "app_library.json"
        
        try:
            with open(library_file, 'w') as f:
                json.dump(app_library.apps, f, indent=2)
            return True, "App library synced to cloud"
        except Exception as e:
            return False, f"Sync failed: {e}"
    
    def restore_app_library(self, app_library) -> Tuple[bool, str]:
        library_file = self.sync_dir / "app_library.json"
        
        if not library_file.exists():
            return False, "No cloud backup found"
        
        try:
            with open(library_file, 'r') as f:
                app_library.apps = json.load(f)
            app_library.save()
            return True, "App library restored from cloud"
        except Exception as e:
            return False, f"Restore failed: {e}"
