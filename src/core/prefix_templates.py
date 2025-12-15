from typing import Dict, List, Tuple, Optional
from pathlib import Path
import json


class PrefixTemplate:
    def __init__(self, name: str, description: str, windows_version: str = "win10"):
        self.name = name
        self.description = description
        self.windows_version = windows_version
        self.winetricks_packages: List[str] = []
        self.dll_overrides: Dict[str, str] = {}
        self.registry_settings: Dict[str, str] = {}
        self.install_dxvk = False
        self.env_vars: Dict[str, str] = {}
    
    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "description": self.description,
            "windows_version": self.windows_version,
            "winetricks_packages": self.winetricks_packages,
            "dll_overrides": self.dll_overrides,
            "registry_settings": self.registry_settings,
            "install_dxvk": self.install_dxvk,
            "env_vars": self.env_vars,
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'PrefixTemplate':
        template = cls(
            data["name"],
            data["description"],
            data.get("windows_version", "win10")
        )
        template.winetricks_packages = data.get("winetricks_packages", [])
        template.dll_overrides = data.get("dll_overrides", {})
        template.registry_settings = data.get("registry_settings", {})
        template.install_dxvk = data.get("install_dxvk", False)
        template.env_vars = data.get("env_vars", {})
        return template


class PrefixTemplateManager:
    def __init__(self, config=None):
        from core.config import Config
        self.config = config or Config()
        self.templates = self._load_builtin_templates()
        self.custom_templates: Dict[str, PrefixTemplate] = {}
        self._load_custom_templates()
    
    def _load_builtin_templates(self) -> Dict[str, PrefixTemplate]:
        templates = {}
        
        gaming = PrefixTemplate(
            "gaming",
            "Optimized for gaming with DXVK and common runtimes",
            "win10"
        )
        gaming.winetricks_packages = ["vcrun2019", "d3dx9", "dotnet48"]
        gaming.install_dxvk = True
        gaming.env_vars = {"DXVK_HUD": "fps", "STAGING_SHARED_MEMORY": "1"}
        templates["gaming"] = gaming
        
        steam = PrefixTemplate(
            "steam",
            "Pre-configured for Steam client",
            "win10"
        )
        steam.winetricks_packages = ["vcrun2019", "dotnet48", "corefonts"]
        steam.install_dxvk = True
        templates["steam"] = steam
        
        office = PrefixTemplate(
            "office",
            "Optimized for Microsoft Office applications",
            "win10"
        )
        office.winetricks_packages = ["dotnet48", "vcrun2019", "corefonts", "msxml6"]
        templates["office"] = office
        
        development = PrefixTemplate(
            "development",
            "For development tools and IDEs",
            "win10"
        )
        development.winetricks_packages = ["vcrun2019", "dotnet48"]
        templates["development"] = development
        
        compatibility = PrefixTemplate(
            "compatibility",
            "Maximum compatibility for older applications",
            "win7"
        )
        compatibility.winetricks_packages = ["vcrun2008", "vcrun2010", "dotnet35"]
        templates["compatibility"] = compatibility
        
        minimal = PrefixTemplate(
            "minimal",
            "Minimal prefix with no extra packages",
            "win10"
        )
        templates["minimal"] = minimal
        
        return templates
    
    def _load_custom_templates(self):
        template_file = self.config.get_config_dir() / "prefix_templates.json"
        if template_file.exists():
            try:
                with open(template_file, 'r') as f:
                    data = json.load(f)
                    for name, template_data in data.items():
                        self.custom_templates[name] = PrefixTemplate.from_dict(template_data)
            except Exception:
                pass
    
    def save_custom_templates(self):
        template_file = self.config.get_config_dir() / "prefix_templates.json"
        try:
            data = {name: t.to_dict() for name, t in self.custom_templates.items()}
            with open(template_file, 'w') as f:
                json.dump(data, f, indent=2)
            return True
        except Exception:
            return False
    
    def get_template(self, name: str) -> Optional[PrefixTemplate]:
        if name in self.templates:
            return self.templates[name]
        return self.custom_templates.get(name)
    
    def list_templates(self) -> List[Dict]:
        result = []
        for name, template in self.templates.items():
            result.append({
                "name": name,
                "description": template.description,
                "type": "builtin"
            })
        for name, template in self.custom_templates.items():
            result.append({
                "name": name,
                "description": template.description,
                "type": "custom"
            })
        return result
    
    def create_custom_template(self, template: PrefixTemplate) -> Tuple[bool, str]:
        if template.name in self.templates:
            return False, "Cannot override builtin template"
        
        self.custom_templates[template.name] = template
        if self.save_custom_templates():
            return True, f"Template '{template.name}' created"
        return False, "Failed to save template"
    
    def delete_custom_template(self, name: str) -> Tuple[bool, str]:
        if name in self.templates:
            return False, "Cannot delete builtin template"
        
        if name in self.custom_templates:
            del self.custom_templates[name]
            if self.save_custom_templates():
                return True, f"Template '{name}' deleted"
            return False, "Failed to save changes"
        
        return False, "Template not found"
    
    def apply_template(self, wine_manager, prefix_name: str, 
                      template_name: str, progress_callback=None) -> Tuple[bool, str]:
        template = self.get_template(template_name)
        if not template:
            return False, f"Template '{template_name}' not found"
        
        if progress_callback:
            progress_callback(10, f"Creating prefix with {template_name} template...")
        
        success, msg = wine_manager.create_prefix(prefix_name, template.windows_version)
        if not success:
            return False, msg
        
        prefix_path = wine_manager.prefixes[prefix_name]
        
        if template.winetricks_packages and progress_callback:
            progress_callback(30, "Installing packages...")
            
            from core.winetricks import WineTricksManager
            winetricks = WineTricksManager(wine_manager)
            
            if winetricks.is_installed():
                for i, package in enumerate(template.winetricks_packages):
                    if progress_callback:
                        pct = 30 + (40 * (i + 1) / len(template.winetricks_packages))
                        progress_callback(int(pct), f"Installing {package}...")
                    
                    winetricks.install_package(prefix_path, package)
        
        if template.install_dxvk:
            if progress_callback:
                progress_callback(70, "Installing DXVK...")
            
            from core.dxvk import DXVKManager
            dxvk = DXVKManager(wine_manager)
            dxvk.install_dxvk(prefix_path)
        
        if progress_callback:
            progress_callback(100, "Template applied successfully!")
        
        return True, f"Prefix '{prefix_name}' created from template '{template_name}'"
