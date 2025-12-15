from typing import Optional, List
from pathlib import Path
import os
import stat


class ShortcutManager:
    def __init__(self, wine_manager=None):
        self.wine_manager = wine_manager
    
    def create_desktop_shortcut(self, name: str, prefix_path: Path, 
                               executable_path: Path, icon_path: Optional[Path] = None,
                               wine_path: Optional[Path] = None) -> bool:
        system = os.uname().sysname
        
        if system == "Linux":
            return self._create_linux_desktop_file(name, prefix_path, executable_path, 
                                                   icon_path, wine_path)
        elif system == "Darwin":
            return self._create_macos_app_bundle(name, prefix_path, executable_path, 
                                                 icon_path, wine_path)
        
        return False
    
    def _create_linux_desktop_file(self, name: str, prefix_path: Path,
                                   executable_path: Path, icon_path: Optional[Path],
                                   wine_path: Optional[Path]) -> bool:
        desktop_dir = Path.home() / ".local" / "share" / "applications"
        desktop_dir.mkdir(parents=True, exist_ok=True)
        
        desktop_file = desktop_dir / f"winvora-{name.lower().replace(' ', '-')}.desktop"
        
        wine_cmd = wine_path or Path("/usr/bin/wine")
        
        content = f"""[Desktop Entry]
Type=Application
Name={name}
Exec=env WINEPREFIX="{prefix_path}" {wine_cmd} "{executable_path}"
Icon={icon_path if icon_path else "wine"}
Categories=Wine;
Terminal=false
"""
        
        try:
            desktop_file.write_text(content)
            desktop_file.chmod(desktop_file.stat().st_mode | stat.S_IEXEC)
            return True
        except Exception:
            return False
    
    def _create_macos_app_bundle(self, name: str, prefix_path: Path,
                                 executable_path: Path, icon_path: Optional[Path],
                                 wine_path: Optional[Path]) -> bool:
        apps_dir = Path.home() / "Applications"
        apps_dir.mkdir(parents=True, exist_ok=True)
        
        app_bundle = apps_dir / f"{name}.app"
        contents_dir = app_bundle / "Contents"
        macos_dir = contents_dir / "MacOS"
        
        try:
            macos_dir.mkdir(parents=True, exist_ok=True)
            
            wine_cmd = wine_path or Path("/usr/local/bin/wine")
            
            script_path = macos_dir / name
            script_content = f"""#!/bin/bash
export WINEPREFIX="{prefix_path}"
"{wine_cmd}" "{executable_path}"
"""
            script_path.write_text(script_content)
            script_path.chmod(script_path.stat().st_mode | stat.S_IEXEC)
            
            info_plist = contents_dir / "Info.plist"
            plist_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleExecutable</key>
    <string>{name}</string>
    <key>CFBundleName</key>
    <string>{name}</string>
    <key>CFBundleIdentifier</key>
    <string>com.winvora.{name.lower().replace(' ', '-')}</string>
    <key>CFBundleVersion</key>
    <string>1.0</string>
</dict>
</plist>
"""
            info_plist.write_text(plist_content)
            
            return True
        except Exception:
            return False
    
    def get_shortcuts(self) -> List[Path]:
        shortcuts = []
        
        system = os.uname().sysname
        
        if system == "Linux":
            desktop_dir = Path.home() / ".local" / "share" / "applications"
            if desktop_dir.exists():
                shortcuts.extend(desktop_dir.glob("winvora-*.desktop"))
        elif system == "Darwin":
            apps_dir = Path.home() / "Applications"
            if apps_dir.exists():
                shortcuts.extend([d for d in apps_dir.glob("*.app") 
                                if (d / "Contents" / "MacOS").exists()])
        
        return shortcuts
    
    def remove_shortcut(self, shortcut_path: Path) -> bool:
        try:
            if shortcut_path.is_file():
                shortcut_path.unlink()
                return True
            elif shortcut_path.is_dir():
                import shutil
                shutil.rmtree(shortcut_path)
                return True
        except Exception:
            return False
        
        return False
