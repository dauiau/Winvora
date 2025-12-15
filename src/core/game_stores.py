from typing import List, Dict, Optional, Tuple
from pathlib import Path
import json
import os
import configparser


class SteamGame:
    def __init__(self, app_id: str, name: str, install_dir: Path):
        self.app_id = app_id
        self.name = name
        self.install_dir = install_dir
        self.executable = self._find_executable()
    
    def _find_executable(self) -> Optional[Path]:
        if not self.install_dir.exists():
            return None
        
        for exe in self.install_dir.rglob("*.exe"):
            if "unins" not in exe.name.lower() and "crash" not in exe.name.lower():
                return exe
        return None


class EpicGame:
    def __init__(self, app_name: str, display_name: str, install_location: Path):
        self.app_name = app_name
        self.display_name = display_name
        self.install_location = install_location
        self.executable = self._find_executable()
    
    def _find_executable(self) -> Optional[Path]:
        if not self.install_location.exists():
            return None
        
        for exe in self.install_location.rglob("*.exe"):
            if "unins" not in exe.name.lower():
                return exe
        return None


class GameStoreIntegration:
    def __init__(self, wine_manager=None, app_library=None):
        self.wine_manager = wine_manager
        self.app_library = app_library
    
    def find_steam_library(self) -> Optional[Path]:
        possible_paths = [
            Path.home() / ".steam" / "steam",
            Path.home() / ".local" / "share" / "Steam",
            Path("/usr/share/steam"),
        ]
        
        for path in possible_paths:
            if path.exists():
                return path
        return None
    
    def scan_steam_games(self, prefix_name: Optional[str] = None) -> List[SteamGame]:
        games = []
        
        if prefix_name and self.wine_manager:
            if prefix_name in self.wine_manager.prefixes:
                prefix_path = self.wine_manager.prefixes[prefix_name]
                steam_dir = prefix_path / "drive_c" / "Program Files (x86)" / "Steam"
                
                if steam_dir.exists():
                    games.extend(self._scan_steam_directory(steam_dir))
        
        steam_path = self.find_steam_library()
        if steam_path:
            games.extend(self._scan_steam_directory(steam_path))
        
        return games
    
    def _scan_steam_directory(self, steam_dir: Path) -> List[SteamGame]:
        games = []
        
        steamapps = steam_dir / "steamapps"
        if not steamapps.exists():
            return games
        
        for manifest in steamapps.glob("appmanifest_*.acf"):
            try:
                with open(manifest, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                app_id = manifest.stem.replace("appmanifest_", "")
                
                name_start = content.find('"name"')
                if name_start != -1:
                    name_start = content.find('"', name_start + 6)
                    name_end = content.find('"', name_start + 1)
                    name = content[name_start + 1:name_end]
                else:
                    name = f"Game {app_id}"
                
                install_start = content.find('"installdir"')
                if install_start != -1:
                    install_start = content.find('"', install_start + 12)
                    install_end = content.find('"', install_start + 1)
                    install_dir = content[install_start + 1:install_end]
                    
                    full_path = steamapps / "common" / install_dir
                    if full_path.exists():
                        games.append(SteamGame(app_id, name, full_path))
            
            except Exception:
                continue
        
        return games
    
    def import_steam_game(self, game: SteamGame, prefix_name: str) -> Tuple[bool, str]:
        if not self.app_library:
            return False, "App library not available"
        
        if not game.executable:
            return False, f"Could not find executable for {game.name}"
        
        success = self.app_library.add_app(
            name=game.name,
            prefix=prefix_name,
            executable_path=str(game.executable),
            category="Steam Games",
            description=f"Steam App ID: {game.app_id}"
        )
        
        if success:
            return True, f"Imported {game.name}"
        return False, "Failed to add to library"
    
    def find_epic_games(self) -> List[EpicGame]:
        games = []
        
        manifests_dir = Path.home() / ".config" / "Epic" / "EpicGamesStore" / "Manifests"
        if not manifests_dir.exists():
            return games
        
        for manifest in manifests_dir.glob("*.item"):
            try:
                with open(manifest, 'r') as f:
                    data = json.load(f)
                
                app_name = data.get("AppName", "")
                display_name = data.get("DisplayName", app_name)
                install_location = data.get("InstallLocation", "")
                
                if install_location:
                    location_path = Path(install_location)
                    if location_path.exists():
                        games.append(EpicGame(app_name, display_name, location_path))
            
            except Exception:
                continue
        
        return games
    
    def import_epic_game(self, game: EpicGame, prefix_name: str) -> Tuple[bool, str]:
        if not self.app_library:
            return False, "App library not available"
        
        if not game.executable:
            return False, f"Could not find executable for {game.display_name}"
        
        success = self.app_library.add_app(
            name=game.display_name,
            prefix=prefix_name,
            executable_path=str(game.executable),
            category="Epic Games",
            description=f"Epic App: {game.app_name}"
        )
        
        if success:
            return True, f"Imported {game.display_name}"
        return False, "Failed to add to library"
    
    def auto_import_all_games(self, prefix_name: str, progress_callback=None) -> Tuple[int, int]:
        imported = 0
        failed = 0
        
        if progress_callback:
            progress_callback(10, "Scanning Steam library...")
        
        steam_games = self.scan_steam_games(prefix_name)
        for i, game in enumerate(steam_games):
            if progress_callback:
                pct = 10 + (40 * (i + 1) / max(len(steam_games), 1))
                progress_callback(int(pct), f"Importing {game.name}...")
            
            success, _ = self.import_steam_game(game, prefix_name)
            if success:
                imported += 1
            else:
                failed += 1
        
        if progress_callback:
            progress_callback(50, "Scanning Epic Games...")
        
        epic_games = self.find_epic_games()
        for i, game in enumerate(epic_games):
            if progress_callback:
                pct = 50 + (50 * (i + 1) / max(len(epic_games), 1))
                progress_callback(int(pct), f"Importing {game.display_name}...")
            
            success, _ = self.import_epic_game(game, prefix_name)
            if success:
                imported += 1
            else:
                failed += 1
        
        if progress_callback:
            progress_callback(100, f"Imported {imported} games!")
        
        return imported, failed
    
    def install_steam(self, prefix_name: str, progress_callback=None) -> Tuple[bool, str]:
        if not self.wine_manager:
            return False, "Wine manager not available"
        
        if progress_callback:
            progress_callback(20, "Downloading Steam installer...")
        
        import urllib.request
        cache_dir = Path.home() / ".cache" / "winvora"
        cache_dir.mkdir(parents=True, exist_ok=True)
        
        steam_installer = cache_dir / "SteamSetup.exe"
        
        try:
            if not steam_installer.exists():
                url = "https://cdn.cloudflare.steamstatic.com/client/installer/SteamSetup.exe"
                urllib.request.urlretrieve(url, steam_installer)
            
            if progress_callback:
                progress_callback(50, "Installing Steam...")
            
            success, msg = self.wine_manager.install_application(
                prefix_name,
                steam_installer
            )
            
            if progress_callback:
                progress_callback(100, "Steam installed!")
            
            return success, msg
            
        except Exception as e:
            return False, f"Failed to install Steam: {e}"
