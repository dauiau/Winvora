from typing import Dict, List, Optional
from pathlib import Path
import json
import time


class AppLibrary:
    def __init__(self, config=None):
        from core.config import Config
        self.config = config or Config()
        self.library_path = self._get_library_path()
        self.library_path.parent.mkdir(parents=True, exist_ok=True)
        self.apps: Dict[str, Dict] = {}
        self.load()
    
    def _get_library_path(self) -> Path:
        config_dir = self.config.get_config_dir()
        return config_dir / "app_library.json"
    
    def load(self):
        if self.library_path.exists():
            try:
                with open(self.library_path, 'r') as f:
                    self.apps = json.load(f)
            except Exception:
                self.apps = {}
        else:
            self.apps = {}
    
    def save(self):
        try:
            with open(self.library_path, 'w') as f:
                json.dump(self.apps, f, indent=2)
            return True
        except Exception:
            return False
    
    def add_app(self, name: str, prefix: str, executable_path: str,
                icon_path: Optional[str] = None, description: Optional[str] = None,
                category: str = "Games") -> bool:
        app_id = f"{prefix}:{Path(executable_path).name}"
        
        self.apps[app_id] = {
            "name": name,
            "prefix": prefix,
            "executable_path": executable_path,
            "icon_path": icon_path,
            "description": description,
            "category": category,
            "added_timestamp": int(time.time()),
            "last_run": None,
            "run_count": 0,
        }
        
        return self.save()
    
    def remove_app(self, app_id: str) -> bool:
        if app_id in self.apps:
            del self.apps[app_id]
            return self.save()
        return False
    
    def get_app(self, app_id: str) -> Optional[Dict]:
        return self.apps.get(app_id)
    
    def list_apps(self, category: Optional[str] = None) -> List[Dict]:
        apps_list = []
        for app_id, app_data in self.apps.items():
            if category is None or app_data.get("category") == category:
                app_data["id"] = app_id
                apps_list.append(app_data)
        
        return sorted(apps_list, key=lambda x: x.get("name", "").lower())
    
    def update_run_stats(self, app_id: str):
        if app_id in self.apps:
            self.apps[app_id]["last_run"] = int(time.time())
            self.apps[app_id]["run_count"] = self.apps[app_id].get("run_count", 0) + 1
            self.save()
    
    def get_categories(self) -> List[str]:
        categories = set()
        for app_data in self.apps.values():
            categories.add(app_data.get("category", "Uncategorized"))
        return sorted(list(categories))
    
    def search_apps(self, query: str) -> List[Dict]:
        query_lower = query.lower()
        results = []
        
        for app_id, app_data in self.apps.items():
            name = app_data.get("name", "").lower()
            description = app_data.get("description", "").lower()
            
            if query_lower in name or query_lower in description:
                app_data["id"] = app_id
                results.append(app_data)
        
        return results
