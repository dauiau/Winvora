#!/usr/bin/env python3
import sys
import argparse
from pathlib import Path
from typing import Optional

from core.wine_manager import WineManager
from core.config import Config


class WinvoraCLI:
    def __init__(self):
        self.config = Config()
        self.wine_manager = WineManager()
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


def main():
    cli = WinvoraCLI()
    return cli.run()


if __name__ == '__main__':
    sys.exit(main())
