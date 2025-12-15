# Advanced Features Guide

## Winetricks Integration

Winvora integrates with Winetricks to simplify installation of Windows DLLs, fonts, and components.

### Installation
```bash
# Install winetricks on your system first
# Linux:
sudo apt install winetricks

# macOS:
brew install winetricks
```

### Using Winetricks

#### CLI
```bash
# Install a component
winvora winetricks install myprefix vcrun2019

# List available common components
winvora winetricks list
```

#### Programmatic
```python
from core.winetricks import WineTricksManager

winetricks = WineTricksManager()
success, message = winetricks.install_dll(prefix_path, "d3dx9")
```

### Common Components
- **Visual C++ Runtimes**: vcrun2005-2019
- **DirectX**: d3dx9, d3dcompiler_47, dxvk
- **.NET Framework**: dotnet48, dotnet472, dotnet462
- **Fonts**: corefonts, tahoma, consolas, liberation

---

## Desktop Shortcuts

Create native desktop shortcuts for your Windows applications.

### Linux (.desktop files)
Shortcuts are created in `~/.local/share/applications/`

### macOS (App Bundles)
Shortcuts are created in `~/Applications/` as .app bundles

### Using Shortcuts

#### CLI
```bash
# Create a shortcut
winvora shortcut create "MyApp" myprefix "/path/to/app.exe"

# List shortcuts
winvora shortcut list
```

#### Programmatic
```python
from core.shortcuts import ShortcutManager

shortcuts = ShortcutManager()
shortcuts.create_desktop_shortcut(
    name="MyGame",
    prefix_path=Path("/path/to/prefix"),
    executable_path=Path("/path/to/game.exe"),
    icon_path=Path("/path/to/icon.png")  # Optional
)
```

---

## Application Library

Organize and manage your Windows applications in a centralized library.

### Features
- Categorize applications (Games, Productivity, etc.)
- Track run statistics
- Search functionality
- JSON-based storage

### Using the Library

#### CLI
```bash
# Add an app
winvora library add "My Game" myprefix "/path/to/game.exe" --category Games

# List all apps
winvora library list

# Remove an app
winvora library remove "myprefix:game.exe"
```

#### Programmatic
```python
from core.app_library import AppLibrary

library = AppLibrary()

# Add application
library.add_app(
    name="Steam",
    prefix="gaming",
    executable_path="/prefix/drive_c/Program Files/Steam/Steam.exe",
    category="Games",
    description="Game distribution platform"
)

# List by category
games = library.list_apps(category="Games")

# Search
results = library.search_apps("steam")

# Update run stats
library.update_run_stats("gaming:Steam.exe")
```

### Storage Location
Library data is stored in: `~/.config/winvora/app_library.json`

---

## Cloud Prefix Sync

Synchronize your Wine prefixes across devices using cloud storage.

### Supported Services
- Dropbox
- Google Drive
- Microsoft OneDrive
- iCloud Drive
- Custom directory

### Configuration
```bash
# Set custom sync directory
winvora config set cloud_sync_dir "/path/to/cloud/folder"
```

### Using Cloud Sync

#### CLI
```bash
# Upload a prefix to cloud
winvora cloud upload myprefix

# Download a prefix from cloud
winvora cloud download myprefix

# List cloud prefixes
winvora cloud list
```

#### Programmatic
```python
from core.cloud_sync import CloudSync

cloud = CloudSync()

# Upload prefix
success, msg = cloud.upload_prefix("myprefix", prefix_path)

# Download prefix
success, msg = cloud.download_prefix("myprefix", dest_path)

# List cloud prefixes
cloud_prefixes = cloud.list_cloud_prefixes()

# Sync app library
cloud.sync_app_library(app_library)
cloud.restore_app_library(app_library)
```

### Auto-Sync
Set up automatic syncing by placing your prefixes directory in a cloud-synced folder:
```bash
# Example for Dropbox
winvora config set prefixes_dir "$HOME/Dropbox/Winvora/prefixes"
```

---

## Advanced Wine Configuration

Fine-tune Wine settings for optimal performance and compatibility.

### Available Options
- **Windows Version**: win10, win8, win7, winxp, win2k
- **DPI Scaling**: 96, 120, 144, 192
- **Virtual Desktop**: Enable/disable with custom resolution
- **CSMT**: Command Stream Multithreading
- **Renderer**: OpenGL, Vulkan, GDI

### Using Advanced Config

#### Programmatic
```python
from core.advanced_config import AdvancedWineConfig

config = AdvancedWineConfig()

# Set Windows version
config.set_windows_version(prefix_path, "win10", wine_path)

# Enable virtual desktop
config.set_virtual_desktop(prefix_path, enabled=True, resolution="1920x1080")

# Set DPI
config.set_dpi(prefix_path, 120)

# Enable CSMT for better performance
config.enable_csmt(prefix_path, True)

# Apply gaming optimizations
config.apply_gaming_optimizations(prefix_path)

# Apply app-specific fixes
config.apply_compatibility_fixes(prefix_path, "steam")
```

### Gaming Optimizations
Automatically applies:
- CSMT enabled
- OpenGL shader disk cache
- Threaded optimization
- Staging shared memory

---

## Performance Monitoring

Monitor Wine process performance and resource usage.

### Features
- CPU usage tracking
- Memory usage tracking
- Session statistics
- Process count monitoring

### Using Performance Monitor

```python
from core.performance import PerformanceMonitor

monitor = PerformanceMonitor()

# Start monitoring an app
monitor.start_monitoring("game_session_1")

# Record metrics (call periodically)
monitor.record_metrics("game_session_1", cpu_percent=15.5, memory_mb=512.0)

# Stop monitoring
monitor.stop_monitoring("game_session_1")

# Get session summary
summary = monitor.get_session_summary("game_session_1")
print(f"Total runtime: {summary['total_runtime_seconds']}s")
print(f"Average CPU: {summary['avg_cpu_percent']}%")
print(f"Peak memory: {summary['max_memory_mb']} MB")

# Get current Wine process stats
stats = monitor.get_wine_process_stats()
print(f"Running processes: {stats['process_count']}")
print(f"Total CPU: {stats['total_cpu']}%")
```

---

## Logging System

Comprehensive logging for debugging and monitoring.

### Features
- Daily log files
- Multiple log levels (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- Separate console and file output
- Automatic log rotation

### Log Location
Logs are stored in: `~/.config/winvora/logs/winvora_YYYYMMDD.log`

### Using the Logger

```python
from core.logger import get_logger

logger = get_logger()

# Log messages
logger.info("Application started")
logger.debug("Debug information")
logger.warning("Warning message")
logger.error("Error occurred")

# Log Wine operations
logger.log_wine_operation(
    operation="create_prefix",
    prefix="gaming",
    success=True,
    details="Prefix created successfully"
)

# Log app launches
logger.log_app_launch(
    app_name="Steam",
    prefix="gaming",
    executable="Steam.exe"
)

# Log prefix operations
logger.log_prefix_operation(
    operation="delete",
    prefix_name="old_prefix",
    success=True
)
```

### Log Levels
- **DEBUG**: Detailed diagnostic information
- **INFO**: General informational messages
- **WARNING**: Warning messages
- **ERROR**: Error messages
- **CRITICAL**: Critical failures

### Viewing Logs
```bash
# View today's log
cat ~/.config/winvora/logs/winvora_$(date +%Y%m%d).log

# Follow log in real-time
tail -f ~/.config/winvora/logs/winvora_$(date +%Y%m%d).log

# Search logs
grep "ERROR" ~/.config/winvora/logs/*.log
```

---

## Integration Example

Here's a complete example integrating multiple features:

```python
from core.wine_manager import WineManager
from core.winetricks import WineTricksManager
from core.app_library import AppLibrary
from core.shortcuts import ShortcutManager
from core.cloud_sync import CloudSync
from core.performance import PerformanceMonitor
from core.advanced_config import AdvancedWineConfig
from core.logger import get_logger
from pathlib import Path

# Initialize components
wine = WineManager()
winetricks = WineTricksManager(wine)
library = AppLibrary()
shortcuts = ShortcutManager()
cloud = CloudSync()
performance = PerformanceMonitor()
config = AdvancedWineConfig()
logger = get_logger()

# Create and configure a prefix
prefix_name = "gaming"
logger.info(f"Creating prefix: {prefix_name}")
success, msg = wine.create_prefix(prefix_name)

if success:
    prefix_path = wine.prefixes[prefix_name]
    
    # Apply gaming optimizations
    config.apply_gaming_optimizations(prefix_path)
    
    # Install required DLLs
    winetricks.install_dll(prefix_path, "vcrun2019")
    winetricks.install_dll(prefix_path, "d3dx9")
    
    # Install game
    installer = Path("/path/to/game_installer.exe")
    wine.install_application(prefix_name, installer)
    
    # Add to library
    library.add_app(
        name="My Game",
        prefix=prefix_name,
        executable_path="/prefix/drive_c/Program Files/Game/game.exe",
        category="Games"
    )
    
    # Create desktop shortcut
    shortcuts.create_desktop_shortcut(
        name="My Game",
        prefix_path=prefix_path,
        executable_path=Path("/prefix/drive_c/Program Files/Game/game.exe")
    )
    
    # Upload to cloud for backup
    cloud.upload_prefix(prefix_name, prefix_path)
    
    logger.info(f"Setup complete for {prefix_name}")
```

---

## CLI Command Reference

### Winetricks Commands
```bash
winvora winetricks install <prefix> <component>
winvora winetricks list
```

### Library Commands
```bash
winvora library add <name> <prefix> <executable> [--category <category>]
winvora library list
winvora library remove <app_id>
```

### Shortcut Commands
```bash
winvora shortcut create <name> <prefix> <executable>
winvora shortcut list
```

### Cloud Commands
```bash
winvora cloud upload <prefix>
winvora cloud download <prefix>
winvora cloud list
```

---

## Best Practices

1. **Regular Backups**: Use cloud sync to backup important prefixes
2. **Monitor Performance**: Track resource usage for optimization
3. **Check Logs**: Review logs when troubleshooting issues
4. **Organize Library**: Categorize apps for easy management
5. **Use Shortcuts**: Create shortcuts for frequently used apps
6. **Install Dependencies**: Use winetricks for common DLLs
7. **Apply Optimizations**: Use gaming optimizations for better performance
