#!/usr/bin/env python3
"""
Winvora CLI - Cross-platform command-line interface for Winvora.

This CLI tool provides terminal-based access to all Winvora functionality
and works on macOS, Linux, and Android (via Termux).
"""

import sys
import argparse
from pathlib import Path
from typing import Optional

from core.wine_manager import WineManager
from core.config import Config


class WinvoraCLI:
    """
    Command-line interface for Winvora.
    """
    
    def __init__(self):
        """Initialize the CLI."""
        self.config = Config()
        self.wine_manager = WineManager()
        self.parser = self._create_parser()
    
    def _create_parser(self) -> argparse.ArgumentParser:
        """
        Create the argument parser with all subcommands.
        
        Returns:
            Configured ArgumentParser.
        """
        parser = argparse.ArgumentParser(
            prog='winvora',
            description='Winvora - Wine compatibility layer manager'
        )
        
        subparsers = parser.add_subparsers(dest='command', help='Available commands')
        
        # Prefix management commands
        prefix_parser = subparsers.add_parser('prefix', help='Manage Wine prefixes')
        prefix_subparsers = prefix_parser.add_subparsers(dest='prefix_action')
        
        # prefix create
        create_parser = prefix_subparsers.add_parser('create', help='Create a new Wine prefix')
        create_parser.add_argument('name', help='Name for the prefix')
        create_parser.add_argument('--path', help='Custom path for the prefix')
        create_parser.add_argument('--windows-version', default='win10',
                                  help='Windows version to emulate (default: win10)')
        
        # prefix list
        prefix_subparsers.add_parser('list', help='List all Wine prefixes')
        
        # prefix delete
        delete_parser = prefix_subparsers.add_parser('delete', help='Delete a Wine prefix')
        delete_parser.add_argument('name', help='Name of the prefix to delete')
        
        # prefix info
        info_parser = prefix_subparsers.add_parser('info', help='Show prefix information')
        info_parser.add_argument('name', help='Name of the prefix')
        
        # Application management commands
        app_parser = subparsers.add_parser('app', help='Manage applications')
        app_subparsers = app_parser.add_subparsers(dest='app_action')
        
        # app install
        install_parser = app_subparsers.add_parser('install', help='Install a Windows application')
        install_parser.add_argument('installer', help='Path to installer (.exe or .msi)')
        install_parser.add_argument('--prefix', required=True, help='Prefix to install into')
        
        # app run
        run_parser = app_subparsers.add_parser('run', help='Run a Windows application')
        run_parser.add_argument('executable', help='Path to executable')
        run_parser.add_argument('--prefix', required=True, help='Prefix to use')
        run_parser.add_argument('--args', nargs='*', help='Arguments to pass to the application')
        
        # app list
        list_parser = app_subparsers.add_parser('list', help='List installed applications')
        list_parser.add_argument('--prefix', required=True, help='Prefix to list apps from')
        
        # Configuration commands
        config_parser = subparsers.add_parser('config', help='Manage configuration')
        config_subparsers = config_parser.add_subparsers(dest='config_action')
        
        # config show
        config_subparsers.add_parser('show', help='Show current configuration')
        
        # config set
        set_parser = config_subparsers.add_parser('set', help='Set a configuration value')
        set_parser.add_argument('key', help='Configuration key')
        set_parser.add_argument('value', help='Configuration value')
        
        # config wine
        wine_parser = config_subparsers.add_parser('wine', help='Configure Wine settings')
        wine_parser.add_argument('--prefix', required=True, help='Prefix to configure')
        
        # System commands
        sys_parser = subparsers.add_parser('system', help='System information and checks')
        sys_subparsers = sys_parser.add_subparsers(dest='system_action')
        
        # system check
        sys_subparsers.add_parser('check', help='Check Wine installation')
        
        # system info
        sys_subparsers.add_parser('info', help='Show system information')
        
        # system processes
        sys_subparsers.add_parser('processes', help='Show running Wine processes')
        
        # Version
        parser.add_argument('--version', action='version', version='Winvora 0.1.0')
        
        return parser
    
    def run(self, args: Optional[list] = None) -> int:
        """
        Run the CLI with the given arguments.
        
        Args:
            args: Command-line arguments (None to use sys.argv)
            
        Returns:
            Exit code (0 for success, non-zero for error)
        """
        parsed_args = self.parser.parse_args(args)
        
        if not parsed_args.command:
            self.parser.print_help()
            return 0
        
        # Route to appropriate handler
        try:
            if parsed_args.command == 'prefix':
                return self._handle_prefix(parsed_args)
            elif parsed_args.command == 'app':
                return self._handle_app(parsed_args)
            elif parsed_args.command == 'config':
                return self._handle_config(parsed_args)
            elif parsed_args.command == 'system':
                return self._handle_system(parsed_args)
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            return 1
        
        return 0
    
    def _handle_prefix(self, args) -> int:
        """Handle prefix management commands."""
        if args.prefix_action == 'create':
            print(f"Creating prefix '{args.name}'...")
            path = Path(args.path) if args.path else None
            success, message = self.wine_manager.create_prefix(
                args.name, 
                path, 
                args.windows_version
            )
            if success:
                print(f"✓ {message}")
                return 0
            else:
                print(f"✗ {message}", file=sys.stderr)
                return 1
        
        elif args.prefix_action == 'list':
            print("Wine Prefixes:")
            prefixes = self.wine_manager.list_prefixes()
            if not prefixes:
                print("  No prefixes found")
                print(f"\n  Create a prefix with: winvora prefix create <name>")
            else:
                for prefix in prefixes:
                    info = self.wine_manager.get_prefix_info(prefix)
                    if info:
                        print(f"  • {prefix}")
                        print(f"    Path: {info.get('path', 'unknown')}")
                    else:
                        print(f"  • {prefix}")
            return 0
        
        elif args.prefix_action == 'delete':
            print(f"Deleting prefix '{args.name}'...")
            success, message = self.wine_manager.delete_prefix(args.name)
            if success:
                print(f"✓ {message}")
                return 0
            else:
                print(f"✗ {message}", file=sys.stderr)
                return 1
        
        elif args.prefix_action == 'info':
            info = self.wine_manager.get_prefix_info(args.name)
            if not info:
                print(f"✗ Prefix '{args.name}' not found", file=sys.stderr)
                return 1
            
            print(f"Prefix: {info['name']}")
            print(f"  Path: {info['path']}")
            print(f"  Exists: {'Yes' if info['exists'] else 'No'}")
            print(f"  Has drive_c: {'Yes' if info['has_drive_c'] else 'No'}")
            if 'windows_version' in info:
                print(f"  Windows Version: {info['windows_version']}")
            return 0
        
        self.parser.print_help()
        return 1
    
    def _handle_app(self, args) -> int:
        """Handle application management commands."""
        if args.app_action == 'install':
            installer_path = Path(args.installer)
            if not installer_path.exists():
                print(f"✗ Installer not found: {installer_path}", file=sys.stderr)
                return 1
            
            print(f"Installing {installer_path.name} into prefix '{args.prefix}'...")
            success, message = self.wine_manager.install_application(args.prefix, installer_path)
            
            if success:
                print(f"✓ Installation completed")
                if message:
                    print(f"\nOutput:\n{message}")
                return 0
            else:
                print(f"✗ Installation failed: {message}", file=sys.stderr)
                return 1
        
        elif args.app_action == 'run':
            executable_path = Path(args.executable)
            run_args = args.args if args.args else []
            
            print(f"Running {executable_path} in prefix '{args.prefix}'...")
            success, message = self.wine_manager.run_application(
                args.prefix, 
                executable_path,
                run_args,
                background=False
            )
            
            if success:
                print(f"✓ Application completed")
                if message:
                    print(f"\nOutput:\n{message}")
                return 0
            else:
                print(f"✗ Application failed: {message}", file=sys.stderr)
                return 1
        
        elif args.app_action == 'list':
            print(f"Applications in prefix '{args.prefix}':")
            
            # List Program Files directories
            prefix_path = self.wine_manager.get_prefix_path(args.prefix)
            if not prefix_path:
                print(f"✗ Prefix '{args.prefix}' not found", file=sys.stderr)
                return 1
            
            program_files = prefix_path / "drive_c" / "Program Files"
            program_files_x86 = prefix_path / "drive_c" / "Program Files (x86)"
            
            found_apps = []
            for pf_dir in [program_files, program_files_x86]:
                if pf_dir.exists():
                    for app_dir in pf_dir.iterdir():
                        if app_dir.is_dir():
                            found_apps.append(app_dir.name)
            
            if found_apps:
                for app in sorted(found_apps):
                    print(f"  • {app}")
            else:
                print("  No applications found in Program Files")
            
            return 0
        
        self.parser.print_help()
        return 1
    
    def _handle_config(self, args) -> int:
        """Handle configuration commands."""
        if args.config_action == 'show':
            print("Winvora Configuration:")
            print(f"  Config File: {self.config.config_path}")
            print(f"  Wine Path: {self.wine_manager.wine_path or 'Auto-detect'}")
            print(f"  Default Prefix Location: {self.config.get_prefixes_dir()}")
            print(f"  Windows Version: {self.config.get('default_windows_version')}")
            print(f"  Architecture: {self.config.get('default_architecture')}")
            
            wine_version = self.wine_manager.get_wine_version()
            if wine_version:
                print(f"  Wine Version: {wine_version}")
            
            return 0
        
        elif args.config_action == 'set':
            print(f"Setting {args.key} = {args.value}")
            self.config.set(args.key, args.value)
            print("✓ Configuration updated and saved")
            return 0
        
        elif args.config_action == 'wine':
            print(f"Opening winecfg for prefix '{args.prefix}'...")
            success, message = self.wine_manager.open_winecfg(args.prefix)
            if success:
                print(f"✓ {message}")
                return 0
            else:
                print(f"✗ {message}", file=sys.stderr)
                return 1
        
        self.parser.print_help()
        return 1
    
    def _handle_system(self, args) -> int:
        """Handle system commands."""
        if args.system_action == 'check':
            print("Checking Wine installation...")
            is_installed = self.wine_manager.verify_wine_installation()
            
            if is_installed:
                wine_version = self.wine_manager.get_wine_version()
                print(f"✓ Wine is installed and accessible")
                if wine_version:
                    print(f"  Version: {wine_version}")
                if self.wine_manager.wine_path:
                    print(f"  Path: {self.wine_manager.wine_path}")
                return 0
            else:
                print("✗ Wine not found")
                print("\nPlease install Wine:")
                print("  macOS:  brew install wine-stable")
                print("  Ubuntu/Debian:  sudo apt install wine")
                print("  Fedora:  sudo dnf install wine")
                print("  Arch:  sudo pacman -S wine")
                print("  Android (Termux):  pkg install wine")
                return 1
        
        elif args.system_action == 'info':
            import platform as plat
            system = plat.system()
            
            print("System Information:")
            print(f"  Platform: {system}")
            print(f"  Architecture: {plat.machine()}")
            print(f"  Python: {plat.python_version()}")
            
            # Get platform-specific info
            if system == 'Darwin':
                from platforms.macos import MacOSPlatform
                platform_obj = MacOSPlatform()
            elif system == 'Linux':
                from platforms.linux import LinuxPlatform
                platform_obj = LinuxPlatform()
            else:
                platform_obj = None
            
            if platform_obj:
                sys_info = platform_obj.get_system_info()
                for key, value in sys_info.items():
                    if key not in ['platform']:
                        print(f"  {key.replace('_', ' ').title()}: {value}")
            
            # Wine info
            wine_version = self.wine_manager.get_wine_version()
            if wine_version:
                print(f"  Wine Version: {wine_version}")
            else:
                print(f"  Wine: Not installed")
            
            print(f"\nWinvora:")
            print(f"  Config Dir: {self.config.config_path.parent}")
            print(f"  Prefixes Dir: {self.config.get_prefixes_dir()}")
            
            return 0
        
        elif args.system_action == 'processes':
            print("Running Wine processes:")
            processes = self.wine_manager.get_running_processes()
            
            if processes:
                for proc in processes:
                    print(f"  PID {proc['pid']}: {proc['command']}")
                print(f"\nTotal: {len(processes)} process(es)")
                print("\nTo kill a process: kill <PID>")
                print("To kill all Wine: winvora system kill-all (future feature)")
            else:
                print("  No Wine processes found")
            
            return 0
        
        self.parser.print_help()
        return 1


def main():
    """Main entry point for the CLI."""
    cli = WinvoraCLI()
    sys.exit(cli.run())


if __name__ == '__main__':
    main()
