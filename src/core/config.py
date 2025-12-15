from pathlib import Path
from typing import Optional, Dict, Any
import json
import platform
import os


class Config:
    DEFAULT_SETTINGS = {
        "wine_path": None,
        "default_windows_version": "win10",
        "default_architecture": "win64",
        "auto_create_shortcuts": True,
        "show_notifications": True,
        "dark_mode": False,
    }
    
    def __init__(self, config_path: Optional[Path] = None):
        self.config_path = config_path or self._get_default_config_path()
        self.settings: Dict[str, Any] = self.DEFAULT_SETTINGS.copy()
        self.load()
    
    def _get_default_config_path(self) -> Path:
        system = platform.system().lower()
        
        if system == 'darwin':
            config_dir = Path.home() / "Library" / "Application Support" / "Winvora"
        elif system == 'linux':
            if Path('/data/data/com.termux/files').exists():
                config_dir = Path('/data/data/com.termux/files/home') / ".config" / "winvora"
            else:
                xdg_config = os.environ.get('XDG_CONFIG_HOME', str(Path.home() / ".config"))
                config_dir = Path(xdg_config) / "winvora"
        else:
            config_dir = Path.home() / ".winvora"
        
        return config_dir / "config.json"
    
    def load(self) -> bool:
        try:
            if self.config_path.exists():
                with open(self.config_path, 'r') as f:
                    loaded_settings = json.load(f)
                    self.settings.update(loaded_settings)
                return True
            else:
                return self.save()
        except (json.JSONDecodeError, IOError) as e:
            print(f"Warning: Could not load config: {e}")
            return False
    
    def save(self) -> bool:
        try:
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_path, 'w') as f:
                json.dump(self.settings, f, indent=2)
            return True
        except IOError as e:
            print(f"Error: Could not save config: {e}")
            return False
    
    def get(self, key: str, default: Any = None) -> Any:
        return self.settings.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        self.settings[key] = value
        self.save()
    
    def get_config_dir(self) -> Path:
        """Get the configuration directory."""
        return self.config_path.parent
    
    def get_prefixes_dir(self) -> Path:
        custom_dir = self.get("prefixes_directory")
        if custom_dir:
            return Path(custom_dir)
        
        system = platform.system().lower()
        
        if system == 'darwin':
            return Path.home() / "Library" / "Application Support" / "Winvora" / "prefixes"
        elif system == 'linux':
            if Path('/data/data/com.termux/files').exists():
                return Path('/data/data/com.termux/files/home') / ".local" / "share" / "winvora" / "prefixes"
            else:
                xdg_data = os.environ.get('XDG_DATA_HOME', str(Path.home() / ".local" / "share"))
                return Path(xdg_data) / "winvora" / "prefixes"
        else:
            return Path.home() / ".winvora" / "prefixes"
    
    def reset_to_defaults(self) -> None:
        self.settings = self.DEFAULT_SETTINGS.copy()
        self.save()
