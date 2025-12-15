#!/usr/bin/env python3
import sys
import argparse
from pathlib import Path
from typing import Optional

from core.wine_manager import WineManager
from core.config import Config
from core.winetricks import WineTricksManager
from core.shortcuts import ShortcutManager
from core.app_library import AppLibrary
from core.cloud_sync import CloudSync
from core.advanced_config import AdvancedWineConfig
from core.performance import PerformanceMonitor
from core.dxvk import DXVKManager
from core.prefix_templates import PrefixTemplateManager
from core.wine_versions import WineVersionManager
from core.game_stores import GameStoreIntegration


class WinvoraCLI:
    def __init__(self):
        self.config = Config()
        self.wine_manager = WineManager()
        self.winetricks = WineTricksManager(self.wine_manager)
        self.shortcuts = ShortcutManager(self.wine_manager)
        self.app_library = AppLibrary(self.config)
        self.cloud_sync = CloudSync(self.config)
        self.advanced_config = AdvancedWineConfig()
        self.performance = PerformanceMonitor()
        self.dxvk = DXVKManager(self.wine_manager)
        self.templates = PrefixTemplateManager(self.config)
        self.wine_versions = WineVersionManager(self.config)
        self.game_stores = GameStoreIntegration(self.wine_manager, self.app_library)
        self.parser = self._create_parser()
    
    def _create_parser(self) -> argparse.ArgumentParser:
        parser = argparse.ArgumentParser(
            prog='winvora',
            description='Winvora - Wine compatibility layer manager'
        )
        
        subparsers = parser.add_subparsers(dest='command', help='Available commands')
        
        prefix_parser = subparsers.add_parser('prefix', help='Manage Wine prefixes')
        prefix_subparsers = prefix_parser.add_subparsers(dest='prefix_action')
        
        create_parser = prefix_subparsers.add_parser('create', help='Create a new Wine prefix')
        create_parser.add_argument('name', help='Name for the prefix')
        create_parser.add_argument('--path', help='Custom path for the prefix')
        create_parser.add_argument('--windows-version', default='win10',
                                  help='Windows version (default: win10)')
        
        prefix_subparsers.add_parser('list', help='List all Wine prefixes')
        
        delete_parser = prefix_subparsers.add_parser('delete', help='Delete a Wine prefix')
        delete_parser.add_argument('name', help='Name of the prefix to delete')
        
        info_parser = prefix_subparsers.add_parser('info', help='Show prefix information')
        info_parser.add_argument('name', help='Name of the prefix')
        
        app_parser = subparsers.add_parser('app', help='Manage applications')
        app_subparsers = app_parser.add_subparsers(dest='app_action')
        
        install_parser = app_subparsers.add_parser('install', help='Install an application')
        install_parser.add_argument('prefix', help='Prefix to install into')
        install_parser.add_argument('installer', help='Path to installer')
        
        run_parser = app_subparsers.add_parser('run', help='Run an application')
        run_parser.add_argument('prefix', help='Prefix to use')
        run_parser.add_argument('executable', help='Path to executable')
        run_parser.add_argument('--args', nargs='+', help='Additional arguments')
        run_parser.add_argument('--background', action='store_true', help='Run in background')
        
        list_parser = app_subparsers.add_parser('list', help='List installed applications')
        list_parser.add_argument('prefix', help='Prefix to list from')
        
        config_parser = subparsers.add_parser('config', help='Configuration management')
        config_subparsers = config_parser.add_subparsers(dest='config_action')
        
        config_subparsers.add_parser('show', help='Show current configuration')
        
        set_parser = config_subparsers.add_parser('set', help='Set configuration value')
        set_parser.add_argument('key', help='Configuration key')
        set_parser.add_argument('value', help='Configuration value')
        
        get_parser = config_subparsers.add_parser('get', help='Get configuration value')
        get_parser.add_argument('key', help='Configuration key')
        
        system_parser = subparsers.add_parser('system', help='System information')
        system_subparsers = system_parser.add_subparsers(dest='system_action')
        
        system_subparsers.add_parser('info', help='Show system information')
        system_subparsers.add_parser('check-wine', help='Check Wine installation')
        
        process_parser = subparsers.add_parser('process', help='Process management')
        process_subparsers = process_parser.add_subparsers(dest='process_action')
        
        process_subparsers.add_parser('list', help='List running Wine processes')
        
        kill_parser = process_subparsers.add_parser('kill', help='Kill a Wine process')
        kill_parser.add_argument('pid', help='Process ID to kill')
        
        process_subparsers.add_parser('kill-all', help='Kill all Wine processes')
        
        winetricks_parser = subparsers.add_parser('winetricks', help='Winetricks integration')
        winetricks_subparsers = winetricks_parser.add_subparsers(dest='winetricks_action')
        
        install_dll_parser = winetricks_subparsers.add_parser('install', help='Install DLL/component')
        install_dll_parser.add_argument('prefix', help='Prefix name')
        install_dll_parser.add_argument('component', help='Component to install')
        
        winetricks_subparsers.add_parser('list', help='List common components')
        
        library_parser = subparsers.add_parser('library', help='App library management')
        library_subparsers = library_parser.add_subparsers(dest='library_action')
        
        add_app_parser = library_subparsers.add_parser('add', help='Add app to library')
        add_app_parser.add_argument('name', help='App name')
        add_app_parser.add_argument('prefix', help='Prefix name')
        add_app_parser.add_argument('executable', help='Executable path')
        add_app_parser.add_argument('--category', default='Games', help='App category')
        
        library_subparsers.add_parser('list', help='List apps in library')
        
        remove_app_parser = library_subparsers.add_parser('remove', help='Remove app from library')
        remove_app_parser.add_argument('app_id', help='App ID')
        
        shortcut_parser = subparsers.add_parser('shortcut', help='Desktop shortcut management')
        shortcut_subparsers = shortcut_parser.add_subparsers(dest='shortcut_action')
        
        create_shortcut_parser = shortcut_subparsers.add_parser('create', help='Create desktop shortcut')
        create_shortcut_parser.add_argument('name', help='Shortcut name')
        create_shortcut_parser.add_argument('prefix', help='Prefix name')
        create_shortcut_parser.add_argument('executable', help='Executable path')
        
        shortcut_subparsers.add_parser('list', help='List shortcuts')
        
        cloud_parser = subparsers.add_parser('cloud', help='Cloud sync management')
        cloud_subparsers = cloud_parser.add_subparsers(dest='cloud_action')
        
        upload_parser = cloud_subparsers.add_parser('upload', help='Upload prefix to cloud')
        upload_parser.add_argument('prefix', help='Prefix name')
        
        download_parser = cloud_subparsers.add_parser('download', help='Download prefix from cloud')
        download_parser.add_argument('prefix', help='Prefix name')
        
        cloud_subparsers.add_parser('list', help='List cloud prefixes')
        
        template_parser = subparsers.add_parser('template', help='Prefix template management')
        template_subparsers = template_parser.add_subparsers(dest='template_action')
        
        template_subparsers.add_parser('list', help='List available templates')
        
        create_template_parser = template_subparsers.add_parser('create', help='Create template from prefix')
        create_template_parser.add_argument('name', help='Template name')
        create_template_parser.add_argument('prefix', help='Source prefix')
        create_template_parser.add_argument('--description', help='Template description')
        
        apply_template_parser = template_subparsers.add_parser('apply', help='Apply template to prefix')
        apply_template_parser.add_argument('name', help='Template name')
        apply_template_parser.add_argument('prefix', help='Target prefix')
        
        dxvk_parser = subparsers.add_parser('dxvk', help='DXVK management')
        dxvk_subparsers = dxvk_parser.add_subparsers(dest='dxvk_action')
        
        install_dxvk_parser = dxvk_subparsers.add_parser('install', help='Install DXVK')
        install_dxvk_parser.add_argument('prefix', help='Prefix name')
        install_dxvk_parser.add_argument('--version', help='DXVK version (default: latest)')
        
        uninstall_dxvk_parser = dxvk_subparsers.add_parser('uninstall', help='Uninstall DXVK')
        uninstall_dxvk_parser.add_argument('prefix', help='Prefix name')
        
        status_dxvk_parser = dxvk_subparsers.add_parser('status', help='Check DXVK status')
        status_dxvk_parser.add_argument('prefix', help='Prefix name')
        
        version_parser = subparsers.add_parser('wine-version', help='Wine version management')
        version_subparsers = version_parser.add_subparsers(dest='version_action')
        
        version_subparsers.add_parser('list', help='List installed Wine versions')
        
        download_version_parser = version_subparsers.add_parser('download', help='Download Wine version')
        download_version_parser.add_argument('version', help='Version identifier (e.g., stable-8.0)')
        
        delete_version_parser = version_subparsers.add_parser('delete', help='Delete Wine version')
        delete_version_parser.add_argument('version', help='Version name')
        
        switch_version_parser = version_subparsers.add_parser('switch', help='Switch prefix Wine version')
        switch_version_parser.add_argument('prefix', help='Prefix name')
        switch_version_parser.add_argument('version', help='Version name')
        
        store_parser = subparsers.add_parser('game-store', help='Game store integration')
        store_subparsers = store_parser.add_subparsers(dest='store_action')
        
        store_subparsers.add_parser('scan-steam', help='Scan Steam library')
        store_subparsers.add_parser('scan-epic', help='Scan Epic Games library')
        
        import_parser = store_subparsers.add_parser('import', help='Import games to library')
        import_parser.add_argument('store', choices=['steam', 'epic'], help='Store to import from')
        
        install_steam_parser = store_subparsers.add_parser('install-steam', help='Install Steam to prefix')
        install_steam_parser.add_argument('prefix', help='Prefix name')
        
        return parser
    
    def run(self, args=None):
        parsed_args = self.parser.parse_args(args)
        
        if not parsed_args.command:
            self.parser.print_help()
            return 0
        
        if parsed_args.command == 'prefix':
            return self._handle_prefix_command(parsed_args)
        elif parsed_args.command == 'app':
            return self._handle_app_command(parsed_args)
        elif parsed_args.command == 'config':
            return self._handle_config_command(parsed_args)
        elif parsed_args.command == 'system':
            return self._handle_system_command(parsed_args)
        elif parsed_args.command == 'process':
            return self._handle_process_command(parsed_args)
        elif parsed_args.command == 'winetricks':
            return self._handle_winetricks_command(parsed_args)
        elif parsed_args.command == 'library':
            return self._handle_library_command(parsed_args)
        elif parsed_args.command == 'shortcut':
            return self._handle_shortcut_command(parsed_args)
        elif parsed_args.command == 'cloud':
            return self._handle_cloud_command(parsed_args)
        elif parsed_args.command == 'template':
            return self._handle_template_command(parsed_args)
        elif parsed_args.command == 'dxvk':
            return self._handle_dxvk_command(parsed_args)
        elif parsed_args.command == 'wine-version':
            return self._handle_wine_version_command(parsed_args)
        elif parsed_args.command == 'game-store':
            return self._handle_game_store_command(parsed_args)
        
        return 0
    
    def _handle_prefix_command(self, args):
        if not args.prefix_action:
            print("Error: Specify prefix action (create, list, delete, info)")
            return 1
        
        if args.prefix_action == 'create':
            success, message = self.wine_manager.create_prefix(
                args.name,
                windows_version=args.windows_version
            )
            print(message)
            return 0 if success else 1
        
        elif args.prefix_action == 'list':
            prefixes = self.wine_manager.list_prefixes()
            if prefixes:
                print("Wine Prefixes:")
                for prefix in prefixes:
                    print(f"  - {prefix}")
            else:
                print("No Wine prefixes found")
            return 0
        
        elif args.prefix_action == 'delete':
            success, message = self.wine_manager.delete_prefix(args.name)
            print(message)
            return 0 if success else 1
        
        elif args.prefix_action == 'info':
            info = self.wine_manager.get_prefix_info(args.name)
            if info:
                print(f"Prefix: {info['name']}")
                print(f"Path: {info['path']}")
                print(f"Exists: {info['exists']}")
                if 'windows_version' in info:
                    print(f"Windows Version: {info['windows_version']}")
            else:
                print(f"Error: Prefix '{args.name}' not found")
                return 1
            return 0
        
        return 0
    
    def _handle_app_command(self, args):
        if not args.app_action:
            print("Error: Specify app action (install, run, list)")
            return 1
        
        if args.app_action == 'install':
            installer_path = Path(args.installer)
            success, message = self.wine_manager.install_application(
                args.prefix,
                installer_path
            )
            print(message)
            return 0 if success else 1
        
        elif args.app_action == 'run':
            exe_path = Path(args.executable)
            success, message = self.wine_manager.run_application(
                args.prefix,
                exe_path,
                args=args.args,
                background=args.background
            )
            print(message)
            return 0 if success else 1
        
        elif args.app_action == 'list':
            programs = self.wine_manager.get_prefix_programs(args.prefix)
            if programs:
                print(f"Installed applications in '{args.prefix}':")
                for program in programs:
                    print(f"  - {program.name}")
            else:
                print(f"No applications found in '{args.prefix}'")
            return 0
        
        return 0
    
    def _handle_config_command(self, args):
        if not args.config_action:
            print("Error: Specify config action (show, set, get)")
            return 1
        
        if args.config_action == 'show':
            print("Current configuration:")
            for key, value in self.config.config.items():
                print(f"  {key}: {value}")
            return 0
        
        elif args.config_action == 'set':
            self.config.set(args.key, args.value)
            self.config.save()
            print(f"Set {args.key} = {args.value}")
            return 0
        
        elif args.config_action == 'get':
            value = self.config.get(args.key)
            if value is not None:
                print(value)
            else:
                print(f"Error: Key '{args.key}' not found")
                return 1
            return 0
        
        return 0
    
    def _handle_system_command(self, args):
        if not args.system_action:
            print("Error: Specify system action (info, check-wine)")
            return 1
        
        if args.system_action == 'info':
            from platforms import get_platform
            platform = get_platform()
            info = platform.get_system_info()
            
            print("System Information:")
            for key, value in info.items():
                print(f"  {key}: {value}")
            return 0
        
        elif args.system_action == 'check-wine':
            if self.wine_manager.verify_wine_installation():
                version = self.wine_manager.get_wine_version()
                print(f"✓ Wine is installed")
                if version:
                    print(f"  Version: {version}")
                if self.wine_manager.wine_path:
                    print(f"  Path: {self.wine_manager.wine_path}")
            else:
                print("✗ Wine is not installed or not accessible")
                return 1
            return 0
        
        return 0
    
    def _handle_process_command(self, args):
        if not args.process_action:
            print("Error: Specify process action (list, kill, kill-all)")
            return 1
        
        if args.process_action == 'list':
            processes = self.wine_manager.get_running_processes()
            if processes:
                print("Running Wine processes:")
                for proc in processes:
                    print(f"  PID {proc['pid']}: {proc['command']}")
            else:
                print("No Wine processes running")
            return 0
        
        elif args.process_action == 'kill':
            success, message = self.wine_manager.kill_process(args.pid)
            print(message)
            return 0 if success else 1
        
        elif args.process_action == 'kill-all':
            success, message = self.wine_manager.kill_all_wine()
            print(message)
            return 0 if success else 1
        
        return 0
    
    def _handle_winetricks_command(self, args):
        if not args.winetricks_action:
            print("Error: Specify winetricks action")
            return 1
        
        if args.winetricks_action == 'install':
            if args.prefix not in self.wine_manager.prefixes:
                print(f"Error: Prefix '{args.prefix}' not found")
                return 1
            
            prefix_path = self.wine_manager.prefixes[args.prefix]
            success, message = self.winetricks.install_dll(prefix_path, args.component)
            print(message)
            return 0 if success else 1
        
        elif args.winetricks_action == 'list':
            print("Common DLLs:")
            for dll in self.winetricks.get_common_dlls():
                print(f"  - {dll}")
            print("\nCommon Fonts:")
            for font in self.winetricks.get_common_fonts():
                print(f"  - {font}")
            return 0
        
        return 0
    
    def _handle_library_command(self, args):
        if not args.library_action:
            print("Error: Specify library action")
            return 1
        
        if args.library_action == 'add':
            success = self.app_library.add_app(
                args.name, args.prefix, args.executable,
                category=args.category
            )
            if success:
                print(f"Added '{args.name}' to library")
            else:
                print("Failed to add app")
            return 0 if success else 1
        
        elif args.library_action == 'list':
            apps = self.app_library.list_apps()
            if apps:
                print("Apps in library:")
                for app in apps:
                    print(f"  - {app['name']} ({app['category']}) - ID: {app['id']}")
            else:
                print("No apps in library")
            return 0
        
        elif args.library_action == 'remove':
            success = self.app_library.remove_app(args.app_id)
            if success:
                print(f"Removed app from library")
            else:
                print("Failed to remove app")
            return 0 if success else 1
        
        return 0
    
    def _handle_shortcut_command(self, args):
        if not args.shortcut_action:
            print("Error: Specify shortcut action")
            return 1
        
        if args.shortcut_action == 'create':
            if args.prefix not in self.wine_manager.prefixes:
                print(f"Error: Prefix '{args.prefix}' not found")
                return 1
            
            prefix_path = self.wine_manager.prefixes[args.prefix]
            success = self.shortcuts.create_desktop_shortcut(
                args.name, prefix_path, Path(args.executable),
                wine_path=self.wine_manager.wine_path
            )
            if success:
                print(f"Created shortcut for '{args.name}'")
            else:
                print("Failed to create shortcut")
            return 0 if success else 1
        
        elif args.shortcut_action == 'list':
            shortcuts = self.shortcuts.get_shortcuts()
            if shortcuts:
                print("Desktop shortcuts:")
                for shortcut in shortcuts:
                    print(f"  - {shortcut.name}")
            else:
                print("No shortcuts found")
            return 0
        
        return 0
    
    def _handle_cloud_command(self, args):
        if not args.cloud_action:
            print("Error: Specify cloud action")
            return 1
        
        if args.cloud_action == 'upload':
            if args.prefix not in self.wine_manager.prefixes:
                print(f"Error: Prefix '{args.prefix}' not found")
                return 1
            
            prefix_path = self.wine_manager.prefixes[args.prefix]
            print(f"Uploading prefix '{args.prefix}' to cloud...")
            success, message = self.cloud_sync.upload_prefix(args.prefix, prefix_path)
            print(message)
            return 0 if success else 1
        
        elif args.cloud_action == 'download':
            from platforms import get_platform
            platform = get_platform()
            dest_path = platform.get_default_prefix_location() / args.prefix
            
            print(f"Downloading prefix '{args.prefix}' from cloud...")
            success, message = self.cloud_sync.download_prefix(args.prefix, dest_path)
            print(message)
            return 0 if success else 1
        
        elif args.cloud_action == 'list':
            prefixes = self.cloud_sync.list_cloud_prefixes()
            if prefixes:
                print("Cloud prefixes:")
                for prefix in prefixes:
                    print(f"  - {prefix}")
            else:
                print("No prefixes in cloud")
            return 0
        
        return 0
    
    def _handle_template_command(self, args):
        if not args.template_action:
            print("Error: Specify template action (list, create, apply)")
            return 1
        
        if args.template_action == 'list':
            templates = self.templates.list_templates()
            print("Available Templates:")
            for template in templates:
                print(f"  - {template['name']}: {template['description']}")
            return 0
        
        elif args.template_action == 'create':
            if not args.name:
                print("Error: Template name required")
                return 1
            if args.prefix not in self.wine_manager.prefixes:
                print(f"Error: Prefix '{args.prefix}' not found")
                return 1
            
            prefix_path = self.wine_manager.prefixes[args.prefix]
            print(f"Creating template from prefix '{args.prefix}'...")
            success, message = self.templates.create_template_from_prefix(
                args.name,
                prefix_path,
                description=args.description or f"Template created from {args.prefix}"
            )
            print(message)
            return 0 if success else 1
        
        elif args.template_action == 'apply':
            if not args.name:
                print("Error: Template name required")
                return 1
            if not args.prefix:
                print("Error: Target prefix name required")
                return 1
            
            print(f"Applying template '{args.name}' to prefix '{args.prefix}'...")
            success, message = self.templates.apply_template(args.name, args.prefix)
            print(message)
            return 0 if success else 1
        
        return 0
    
    def _handle_dxvk_command(self, args):
        if not args.dxvk_action:
            print("Error: Specify DXVK action (install, uninstall, status)")
            return 1
        
        if not args.prefix:
            print("Error: Prefix name required")
            return 1
        
        if args.prefix not in self.wine_manager.prefixes:
            print(f"Error: Prefix '{args.prefix}' not found")
            return 1
        
        prefix_path = self.wine_manager.prefixes[args.prefix]
        
        if args.dxvk_action == 'install':
            version = args.version or "latest"
            print(f"Installing DXVK {version} to prefix '{args.prefix}'...")
            
            def progress_callback(progress, message):
                print(f"[{progress:.0f}%] {message}")
            
            success, message = self.dxvk.install_dxvk(
                prefix_path,
                version=version,
                progress_callback=progress_callback
            )
            print(message)
            return 0 if success else 1
        
        elif args.dxvk_action == 'uninstall':
            print(f"Uninstalling DXVK from prefix '{args.prefix}'...")
            success, message = self.dxvk.uninstall_dxvk(prefix_path)
            print(message)
            return 0 if success else 1
        
        elif args.dxvk_action == 'status':
            installed = self.dxvk.is_dxvk_installed(prefix_path)
            if installed:
                print(f"DXVK is installed in prefix '{args.prefix}'")
            else:
                print(f"DXVK is not installed in prefix '{args.prefix}'")
            return 0
        
        return 0
    
    def _handle_wine_version_command(self, args):
        if not args.version_action:
            print("Error: Specify version action (list, download, delete, switch)")
            return 1
        
        if args.version_action == 'list':
            versions = self.wine_versions.list_installed_versions()
            if versions:
                print("Installed Wine versions:")
                for version in versions:
                    print(f"  - {version.name} ({version.version_type})")
                    print(f"    Path: {version.path}")
            else:
                print("No Wine versions installed")
            return 0
        
        elif args.version_action == 'download':
            if not args.version:
                print("Error: Version identifier required (e.g., 'stable-8.0', 'staging-9.0', 'proton-8.0')")
                return 1
            
            print(f"Downloading Wine version '{args.version}'...")
            
            def progress_callback(progress, message):
                print(f"[{progress:.0f}%] {message}")
            
            success, message = self.wine_versions.download_wine_version(
                args.version,
                progress_callback=progress_callback
            )
            print(message)
            return 0 if success else 1
        
        elif args.version_action == 'delete':
            if not args.version:
                print("Error: Version name required")
                return 1
            
            success, message = self.wine_versions.delete_wine_version(args.version)
            print(message)
            return 0 if success else 1
        
        elif args.version_action == 'switch':
            if not args.prefix:
                print("Error: Prefix name required")
                return 1
            if not args.version:
                print("Error: Version name required")
                return 1
            
            success, message = self.wine_versions.set_prefix_wine_version(args.prefix, args.version)
            print(message)
            return 0 if success else 1
        
        return 0
    
    def _handle_game_store_command(self, args):
        if not args.store_action:
            print("Error: Specify store action (scan-steam, scan-epic, import, install-steam)")
            return 1
        
        if args.store_action == 'scan-steam':
            print("Scanning Steam library...")
            games = self.game_stores.scan_steam_library()
            if games:
                print(f"Found {len(games)} Steam games:")
                for game in games[:20]:
                    print(f"  - {game.name} (ID: {game.app_id})")
                if len(games) > 20:
                    print(f"  ... and {len(games) - 20} more")
            else:
                print("No Steam games found")
            return 0
        
        elif args.store_action == 'scan-epic':
            print("Scanning Epic Games library...")
            games = self.game_stores.scan_epic_library()
            if games:
                print(f"Found {len(games)} Epic games:")
                for game in games[:20]:
                    print(f"  - {game.display_name}")
                if len(games) > 20:
                    print(f"  ... and {len(games) - 20} more")
            else:
                print("No Epic games found")
            return 0
        
        elif args.store_action == 'import':
            if not args.store:
                print("Error: Specify store (steam or epic)")
                return 1
            
            print(f"Importing {args.store} games to library...")
            count = self.game_stores.auto_import_games(args.store)
            print(f"Imported {count} games")
            return 0
        
        elif args.store_action == 'install-steam':
            if not args.prefix:
                print("Error: Prefix name required")
                return 1
            
            print(f"Installing Steam to prefix '{args.prefix}'...")
            
            def progress_callback(progress, message):
                print(f"[{progress:.0f}%] {message}")
            
            success, message = self.game_stores.install_steam(
                args.prefix,
                progress_callback=progress_callback
            )
            print(message)
            return 0 if success else 1
        
        return 0


def main():
    cli = WinvoraCLI()
    return cli.run()


if __name__ == '__main__':
    sys.exit(main())
