# Quality of Life Improvements - Quick Reference

## New Features Added

### 1. **Favorites System** ⭐
- Mark applications as favorites in the library
- Quick filter to show only favorites
- CLI support: `winvora favorites toggle <app_id>` and `winvora favorites list`
- Displayed with star emoji in GUI lists

### 2. **Last Used Tracking** 🕐
- Automatically tracks when each app was last run
- Shows "Last used" timestamp in library view
- View recent apps with dedicated "Recent" button
- Includes run count statistics

### 3. **Search & Filter** 🔍
- Search bars in Prefixes and Library tabs
- Real-time filtering as you type
- Filter by name, description, or category
- Keyboard shortcut: Ctrl+F (when available)

### 4. **Keyboard Shortcuts** ⌨️
**Linux:**
- `F1` - Show keyboard shortcuts help
- `F5` - Refresh all lists
- `Ctrl+N` - Create new prefix
- `Ctrl+E` - Export logs
- `Ctrl+Q` - Quit application

**macOS:**
- `⌘+?` - Show keyboard shortcuts help
- `⌘+R` - Refresh all lists
- `⌘+N` - Create new prefix
- `⌘+E` - Export logs
- `⌘+Q` - Quit application

### 5. **Desktop Notifications** 🔔
- Success notifications for completed operations
- Error notifications for failed operations
- Progress completion notifications
- Cross-platform support (Linux & macOS)
- Can be enabled/disabled via settings

### 6. **Log Export** 📦
- Export all logs to a zip file
- GUI: Keyboard shortcut Ctrl/⌘+E or from menu
- CLI: `winvora logs export <output.zip>`
- Lists all log files: `winvora logs list`
- Clear old logs: `winvora logs clear --days 30`

### 7. **Enhanced Validation** ✅
- Disk space check before creating prefixes
- Prefix name validation (no special characters)
- Better error messages with suggested fixes
- Pre-operation checks to prevent failures

### 8. **Context Menus** 📋
- Right-click on library items for quick actions
- Toggle favorite
- Add/edit notes
- Remove application

### 9. **Application Notes** 📝
- Add custom notes to any application
- Accessed via context menu in library
- Stores installation tips, configuration notes, etc.
- Saved per application

### 10. **Most Used Apps** 📊
- Track run count for each application
- View most frequently used apps
- Helps identify your go-to applications

## CLI New Commands

### Logs Management
```bash
# Export logs to zip
winvora logs export ~/winvora-logs.zip

# List all log files
winvora logs list

# Clear logs older than 30 days
winvora logs clear --days 30
```

### Favorites Management
```bash
# Toggle favorite status
winvora favorites toggle "my-prefix:app.exe"

# List all favorites
winvora favorites list
```

## GUI Improvements

### Status Bar Messages
- Shows helpful keyboard shortcuts hint
- Real-time operation status
- Better progress feedback

### Better Visual Feedback
- Stars for favorite apps
- Last used timestamps
- Clearer status messages
- Improved button labels with emojis

### Enhanced Library Tab
- Search bar at the top
- Quick filters: "⭐ Favorites" and "🕐 Recent"
- Context menu with right-click
- Display last used times
- Star indicator for favorites

## Core Module Improvements

### AppLibrary (`src/core/app_library.py`)
- `toggle_favorite(app_id)` - Toggle favorite status
- `set_notes(app_id, notes)` - Add notes to app
- `get_favorites()` - Get all favorite apps
- `get_recent_apps(limit)` - Get recently used apps
- `get_most_used_apps(limit)` - Get most used apps

### WinvoraLogger (`src/core/logger.py`)
- `export_logs(output_path)` - Export logs to zip
- `get_log_files()` - List all log files
- `clear_old_logs(days)` - Remove old logs
- `get_log_directory()` - Get logs location

### WineManager (`src/core/wine_manager.py`)
- `check_disk_space(path, required_mb)` - Validate disk space
- `get_disk_space(path)` - Get available/total space
- Enhanced prefix name validation
- Better error messages

### NotificationManager (`src/core/notifications.py`) - NEW
- `send_notification(title, message)` - Send desktop notification
- `notify_success(title, message)` - Success notification
- `notify_error(title, message)` - Error notification
- `notify_info(title, message)` - Info notification
- Cross-platform (Linux, macOS)

## Usage Examples

### Mark App as Favorite (CLI)
```bash
# First, list apps to get the ID
winvora library list

# Toggle favorite
winvora favorites toggle "gaming:steam.exe"
```

### Export Logs (GUI)
1. Press `Ctrl+E` (Linux) or `⌘+E` (macOS)
2. Choose save location
3. Logs exported as zip file

### Search for Apps
1. Go to Library tab
2. Type in the search box
3. Results filter in real-time

### View Recent Apps
1. Go to Library tab
2. Click "🕐 Recent" button
3. See last 20 apps with timestamps

## Benefits

- **Faster workflow** - Keyboard shortcuts save time
- **Better organization** - Favorites and search help find apps quickly
- **Improved debugging** - Easy log export for support
- **Visual clarity** - Better indicators and timestamps
- **User-friendly** - Context menus and search make features discoverable
- **Cross-platform** - All features work on Linux and macOS

## What's Different?

### Before
- Manual list browsing only
- No favorites or bookmarks
- No search functionality
- No keyboard shortcuts
- No desktop notifications
- Manual log file collection
- Basic validation

### After
- Quick search and filter
- Star your favorite apps
- Track usage and recents
- Keyboard shortcuts for power users
- Desktop notifications
- One-click log export
- Enhanced validation with disk space checks
- Notes for each application
- Context menus for quick actions

---

All improvements are backward compatible - existing configurations and data will work without changes!
