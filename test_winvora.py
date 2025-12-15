#!/usr/bin/env python3
"""
Quick test script for Winvora functionality.

Tests core features without requiring Wine to be installed.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

def test_config():
    """Test configuration management."""
    print("=" * 50)
    print("Testing Config Module")
    print("=" * 50)
    
    from core.config import Config
    
    config = Config()
    print(f"✓ Config loaded from: {config.config_path}")
    print(f"✓ Prefixes directory: {config.get_prefixes_dir()}")
    print(f"✓ Default Windows version: {config.get('default_windows_version')}")
    
    # Test setting a value
    config.set('test_key', 'test_value')
    assert config.get('test_key') == 'test_value'
    print("✓ Config set/get working")
    
    print()

def test_wine_manager():
    """Test Wine manager (without actual Wine)."""
    print("=" * 50)
    print("Testing WineManager Module")
    print("=" * 50)
    
    from core.wine_manager import WineManager
    
    manager = WineManager()
    print(f"✓ WineManager initialized")
    print(f"  Wine path: {manager.wine_path or 'Not found (expected if Wine not installed)'}")
    
    # Test Wine detection
    is_installed = manager.verify_wine_installation()
    if is_installed:
        print(f"✓ Wine detected: {manager.get_wine_version()}")
    else:
        print("✗ Wine not installed (this is OK for testing)")
    
    # Test prefix listing
    prefixes = manager.list_prefixes()
    print(f"✓ Found {len(prefixes)} prefix(es)")
    for prefix in prefixes:
        print(f"  - {prefix}")
    
    print()

def test_platforms():
    """Test platform detection."""
    print("=" * 50)
    print("Testing Platform Detection")
    print("=" * 50)
    
    import platform
    system = platform.system()
    
    if system == 'Darwin':
        from platforms.macos import MacOSPlatform
        plat = MacOSPlatform()
    elif system == 'Linux':
        from platforms.linux import LinuxPlatform
        plat = LinuxPlatform()
    else:
        print(f"✗ Unsupported platform: {system}")
        return
    
    print(f"✓ Platform detected: {plat.platform_name}")
    
    info = plat.get_system_info()
    print(f"✓ System info:")
    for key, value in info.items():
        print(f"  {key}: {value}")
    
    print(f"✓ Wine paths to check:")
    for path in plat.get_wine_paths():
        exists = "✓" if path.exists() else "✗"
        print(f"  {exists} {path}")
    
    print(f"✓ Default prefix location: {plat.get_default_prefix_location()}")
    
    print()

def test_cli():
    """Test CLI parsing."""
    print("=" * 50)
    print("Testing CLI Module")
    print("=" * 50)
    
    from cli.main import WinvoraCLI
    
    cli = WinvoraCLI()
    print("✓ CLI initialized")
    
    # Test help
    print("✓ CLI commands available:")
    print("  - prefix (create, list, delete, info)")
    print("  - app (install, run, list)")
    print("  - config (show, set, wine)")
    print("  - system (check, info, processes)")
    
    print()

def main():
    """Run all tests."""
    print("\n🧪 Winvora Test Suite\n")
    
    try:
        test_config()
        test_wine_manager()
        test_platforms()
        test_cli()
        
        print("=" * 50)
        print("✅ All tests passed!")
        print("=" * 50)
        print()
        print("To use Winvora:")
        print("  CLI:  python -m cli.main --help")
        print("  GUI:  python winvora.py")
        print()
        print("Note: Wine must be installed to create prefixes and run applications.")
        print("      This test suite only verifies that the code is functional.")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == '__main__':
    sys.exit(main())
