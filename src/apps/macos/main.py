import sys
from pathlib import Path
from typing import Optional

try:
    from PyQt6.QtWidgets import (
        QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
        QPushButton, QListWidget, QLabel, QTabWidget, QMessageBox,
        QFileDialog, QInputDialog, QTextEdit, QGroupBox, QStatusBar,
        QListWidgetItem, QSplitter, QLineEdit
    )
    from PyQt6.QtCore import Qt, QTimer
    from PyQt6.QtGui import QFont, QColor, QPalette, QKeySequence, QShortcut
    PYQT_AVAILABLE = True
except ImportError:
    PYQT_AVAILABLE = False

from core.wine_manager import WineManager
from core.config import Config
from core.winetricks import WineTricksManager
from core.app_library import AppLibrary
from core.dxvk import DXVKManager
from core.prefix_templates import PrefixTemplateManager
from core.wine_versions import WineVersionManager
from core.game_stores import GameStoreIntegration
from core.notifications import get_notification_manager
from core.logger import get_logger
from platforms.macos import MacOSPlatform


class StyledButton(QPushButton):
    def __init__(self, text, primary=False):
        super().__init__(text)
        if primary:
            self.setStyleSheet("""
                QPushButton {
                    background-color: #007AFF;
                    color: white;
                    border: none;
                    padding: 8px 16px;
                    border-radius: 6px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #0051D5;
                }
                QPushButton:pressed {
                    background-color: #003D99;
                }
            """)
        else:
            self.setStyleSheet("""
                QPushButton {
                    background-color: #F5F5F7;
                    color: #1D1D1F;
                    border: 1px solid #D2D2D7;
                    padding: 8px 16px;
                    border-radius: 6px;
                }
                QPushButton:hover {
                    background-color: #E8E8ED;
                }
                QPushButton:pressed {
                    background-color: #D2D2D7;
                }
            """)


class WinvoraMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.wine_manager = WineManager()
        self.config = Config()
        self.platform = MacOSPlatform()
        self.winetricks = WineTricksManager(self.wine_manager)
        self.app_library = AppLibrary(self.config)
        self.dxvk = DXVKManager(self.wine_manager)
        self.templates = PrefixTemplateManager(self.config)
        self.wine_versions = WineVersionManager(self.config)
        self.game_stores = GameStoreIntegration(self.wine_manager, self.app_library)
        self.notifications = get_notification_manager()
        self.logger = get_logger()
        
        self.setWindowTitle("Winvora")
        self.setMinimumSize(1000, 700)
        
        self._apply_modern_style()
        self._init_ui()
        self._setup_keyboard_shortcuts()
        self._start_auto_refresh()
    
    def _apply_modern_style(self):
        self.setStyleSheet("""
            QMainWindow {
                background-color: #FFFFFF;
            }
            QTabWidget::pane {
                border: 1px solid #D2D2D7;
                border-radius: 8px;
                background-color: white;
            }
            QTabBar::tab {
                background-color: #F5F5F7;
                color: #1D1D1F;
                padding: 10px 20px;
                margin-right: 2px;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
            }
            QTabBar::tab:selected {
                background-color: white;
                color: #007AFF;
                font-weight: bold;
            }
            QListWidget {
                border: 1px solid #D2D2D7;
                border-radius: 6px;
                background-color: white;
                padding: 4px;
            }
            QListWidget::item {
                padding: 8px;
                border-radius: 4px;
            }
            QListWidget::item:selected {
                background-color: #007AFF;
                color: white;
            }
            QListWidget::item:hover {
                background-color: #F5F5F7;
            }
            QTextEdit {
                border: 1px solid #D2D2D7;
                border-radius: 6px;
                padding: 8px;
                background-color: #F9F9F9;
                font-family: 'Monaco', 'Menlo', monospace;
                font-size: 11px;
            }
            QGroupBox {
                font-weight: bold;
                border: 1px solid #D2D2D7;
                border-radius: 8px;
                margin-top: 12px;
                padding-top: 12px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 12px;
                padding: 0 8px;
            }
            QLabel {
                color: #1D1D1F;
            }
        """)
    
    def _init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        header = QLabel("Winvora Wine Manager")
        header_font = QFont()
        header_font.setPointSize(24)
        header_font.setBold(True)
        header.setFont(header_font)
        header.setStyleSheet("color: #1D1D1F; margin-bottom: 10px;")
        main_layout.addWidget(header)
        
        tabs = QTabWidget()
        tabs.setDocumentMode(True)
        main_layout.addWidget(tabs)
        
        tabs.addTab(self._create_prefixes_tab(), "🍷 Wine Prefixes")
        tabs.addTab(self._create_applications_tab(), "📦 Applications")
        tabs.addTab(self._create_library_tab(), "📚 Library")
        tabs.addTab(self._create_templates_tab(), "📋 Templates")
        tabs.addTab(self._create_winetricks_tab(), "🧰 Winetricks")
        tabs.addTab(self._create_wine_versions_tab(), "🍾 Wine Versions")
        tabs.addTab(self._create_game_stores_tab(), "🎮 Game Stores")
        tabs.addTab(self._create_processes_tab(), "⚙️ Processes")
        tabs.addTab(self._create_settings_tab(), "🔧 Settings")
        
        self.statusBar().setStyleSheet("""
            QStatusBar {
                background-color: #F5F5F7;
                color: #86868B;
                border-top: 1px solid #D2D2D7;
                padding: 4px;
            }
        """)
        self.statusBar().showMessage("Ready")
    
    def _create_prefixes_tab(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(16)
        
        desc = QLabel("Manage Wine prefixes for different applications")
        desc.setStyleSheet("color: #86868B; font-size: 13px; margin-bottom: 8px;")
        layout.addWidget(desc)
        
        list_group = QGroupBox("Available Prefixes")
        list_layout = QVBoxLayout(list_group)
        
        self.prefix_list = QListWidget()
        self.prefix_list.setAlternatingRowColors(True)
        list_layout.addWidget(self.prefix_list)
        
        button_layout = QHBoxLayout()
        button_layout.setSpacing(8)
        
        create_btn = StyledButton("Create Prefix", primary=True)
        create_btn.clicked.connect(self._on_create_prefix)
        button_layout.addWidget(create_btn)
        
        info_btn = StyledButton("Info")
        info_btn.clicked.connect(self._on_prefix_info)
        button_layout.addWidget(info_btn)
        
        delete_btn = StyledButton("Delete")
        delete_btn.clicked.connect(self._on_delete_prefix)
        button_layout.addWidget(delete_btn)
        
        button_layout.addStretch()
        
        refresh_btn = StyledButton("↻ Refresh")
        refresh_btn.clicked.connect(self._refresh_prefixes)
        button_layout.addWidget(refresh_btn)
        
        list_layout.addLayout(button_layout)
        layout.addWidget(list_group)
        
        return widget
    
    def _create_applications_tab(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(16)
        
        desc = QLabel("Install and run Windows applications")
        desc.setStyleSheet("color: #86868B; font-size: 13px; margin-bottom: 8px;")
        layout.addWidget(desc)
        
        list_group = QGroupBox("Installed Applications")
        list_layout = QVBoxLayout(list_group)
        
        self.app_list = QListWidget()
        self.app_list.setAlternatingRowColors(True)
        list_layout.addWidget(self.app_list)
        
        button_layout = QHBoxLayout()
        button_layout.setSpacing(8)
        
        install_btn = StyledButton("Install Application", primary=True)
        install_btn.clicked.connect(self._on_install_app)
        button_layout.addWidget(install_btn)
        
        run_btn = StyledButton("Run .exe")
        run_btn.clicked.connect(self._on_browse_exe)
        button_layout.addWidget(run_btn)
        
        button_layout.addStretch()
        list_layout.addLayout(button_layout)
        
        layout.addWidget(list_group)
        return widget
    
    def _create_processes_tab(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(16)
        
        desc = QLabel("Monitor and manage running Wine processes")
        desc.setStyleSheet("color: #86868B; font-size: 13px; margin-bottom: 8px;")
        layout.addWidget(desc)
        
        self.process_list = QListWidget()
        self.process_list.setAlternatingRowColors(True)
        layout.addWidget(self.process_list)
        
        button_layout = QHBoxLayout()
        button_layout.setSpacing(8)
        
        refresh_btn = StyledButton("↻ Refresh", primary=True)
        refresh_btn.clicked.connect(self._refresh_processes)
        button_layout.addWidget(refresh_btn)
        
        kill_btn = StyledButton("Kill Selected")
        kill_btn.clicked.connect(self._on_kill_process)
        button_layout.addWidget(kill_btn)
        
        kill_all_btn = StyledButton("Kill All Wine")
        kill_all_btn.clicked.connect(self._on_kill_all)
        button_layout.addWidget(kill_all_btn)
        
        button_layout.addStretch()
        layout.addLayout(button_layout)
        
        return widget
    
    def _create_settings_tab(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(16)
        
        desc = QLabel("System information and configuration")
        desc.setStyleSheet("color: #86868B; font-size: 13px; margin-bottom: 8px;")
        layout.addWidget(desc)
        
        info_group = QGroupBox("System Information")
        info_layout = QVBoxLayout(info_group)
        
        self.system_info = QTextEdit()
        self.system_info.setReadOnly(True)
        self._update_system_info()
        info_layout.addWidget(self.system_info)
        
        layout.addWidget(info_group)
        
        check_btn = StyledButton("Check Wine Installation", primary=True)
        check_btn.clicked.connect(self._on_check_wine)
        layout.addWidget(check_btn)
        
        return widget
    
    def _on_create_prefix(self):
        name, ok = QInputDialog.getText(self, "Create Prefix", "Enter prefix name:")
        if ok and name:
            self.statusBar().showMessage(f"Creating prefix '{name}'...")
            QApplication.processEvents()
            
            success, message = self.wine_manager.create_prefix(name)
            if success:
                QMessageBox.information(self, "Success", message)
                self._refresh_prefixes()
            else:
                QMessageBox.warning(self, "Error", message)
            self.statusBar().showMessage("Ready")
    
    def _on_delete_prefix(self):
        current = self.prefix_list.currentItem()
        if current:
            reply = QMessageBox.question(
                self, "Confirm Delete",
                f"Delete prefix '{current.text()}'?\n\nThis action cannot be undone.",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.Yes:
                self.statusBar().showMessage(f"Deleting prefix...")
                QApplication.processEvents()
                
                success, message = self.wine_manager.delete_prefix(current.text())
                if success:
                    QMessageBox.information(self, "Success", message)
                    self._refresh_prefixes()
                else:
                    QMessageBox.warning(self, "Error", message)
                self.statusBar().showMessage("Ready")
    
    def _on_prefix_info(self):
        current = self.prefix_list.currentItem()
        if current:
            info_dict = self.wine_manager.get_prefix_info(current.text())
            if info_dict:
                info_text = f"Prefix: {info_dict['name']}\n"
                info_text += f"Path: {info_dict['path']}\n"
                info_text += f"Status: {'Active' if info_dict['exists'] else 'Missing'}\n"
                if 'windows_version' in info_dict:
                    info_text += f"Windows Version: {info_dict['windows_version']}"
                QMessageBox.information(self, "Prefix Information", info_text)
            else:
                QMessageBox.warning(self, "Error", f"Could not get info for prefix '{current.text()}'")
    
    def _on_install_app(self):
        prefixes = self.wine_manager.list_prefixes()
        if not prefixes:
            QMessageBox.warning(self, "No Prefixes", 
                "Create a Wine prefix first before installing applications.\n\n"
                "Click 'Create Prefix' in the Wine Prefixes tab.")
            return
        
        prefix, ok = QInputDialog.getItem(
            self, "Select Prefix", "Install into prefix:", prefixes, 0, False
        )
        if not ok:
            return
        
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Installer",
            str(Path.home()),
            "Windows Executables (*.exe *.msi);;All Files (*)"
        )
        if file_path:
            self.statusBar().showMessage(f"Installing {Path(file_path).name}...")
            QApplication.processEvents()
            
            success, message = self.wine_manager.install_application(prefix, Path(file_path))
            if success:
                QMessageBox.information(self, "Success", "Installation completed successfully")
            else:
                QMessageBox.warning(self, "Installation Failed", message)
            self.statusBar().showMessage("Ready")
    
    def _on_browse_exe(self):
        prefixes = self.wine_manager.list_prefixes()
        if not prefixes:
            QMessageBox.warning(self, "No Prefixes", "Create a Wine prefix first.")
            return
        
        prefix, ok = QInputDialog.getItem(
            self, "Select Prefix", "Run in prefix:", prefixes, 0, False
        )
        if not ok:
            return
        
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Windows Executable",
            str(Path.home()),
            "Windows Executables (*.exe);;All Files (*)"
        )
        if file_path:
            self.statusBar().showMessage(f"Launching {Path(file_path).name}...")
            QApplication.processEvents()
            
            success, message = self.wine_manager.run_application(prefix, Path(file_path), background=True)
            if success:
                QMessageBox.information(self, "Success", "Application launched")
            else:
                QMessageBox.warning(self, "Error", message)
            self.statusBar().showMessage("Ready")
    
    def _on_kill_process(self):
        current = self.process_list.currentItem()
        if current:
            text = current.text()
            pid = text.split()[1]
            
            reply = QMessageBox.question(
                self, "Confirm Kill",
                f"Kill process {pid}?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.Yes:
                success, message = self.wine_manager.kill_process(pid)
                if success:
                    self._refresh_processes()
                    self.statusBar().showMessage(message)
                else:
                    QMessageBox.warning(self, "Error", message)
    
    def _on_kill_all(self):
        reply = QMessageBox.question(
            self, "Confirm Kill All",
            "Kill all Wine processes?\n\nThis will close all running Windows applications.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            success, message = self.wine_manager.kill_all_wine()
            if success:
                self._refresh_processes()
                self.statusBar().showMessage(message)
            else:
                QMessageBox.warning(self, "Error", message)
    
    def _on_check_wine(self):
        is_installed = self.wine_manager.verify_wine_installation()
        if is_installed:
            wine_version = self.wine_manager.get_wine_version()
            msg = "✓ Wine is installed and accessible"
            if wine_version:
                msg += f"\n\nVersion: {wine_version}"
            if self.wine_manager.wine_path:
                msg += f"\nPath: {self.wine_manager.wine_path}"
            QMessageBox.information(self, "Wine Check", msg)
        else:
            QMessageBox.warning(
                self, "Wine Not Found",
                "Wine is not installed or not accessible.\n\n"
                "Install Wine with:\n"
                "  brew install wine-stable"
            )
    
    def _refresh_prefixes(self):
        self.prefix_list.clear()
        prefixes = self.wine_manager.list_prefixes()
        for prefix in prefixes:
            item = QListWidgetItem(f"🍷 {prefix}")
            self.prefix_list.addItem(item)
        
        count = len(prefixes)
        self.statusBar().showMessage(f"Found {count} prefix{'es' if count != 1 else ''}")
    
    def _refresh_processes(self):
        self.process_list.clear()
        processes = self.wine_manager.get_running_processes()
        for proc in processes:
            item = QListWidgetItem(f"PID {proc['pid']}: {proc['command']}")
            self.process_list.addItem(item)
        
        count = len(processes)
        self.statusBar().showMessage(f"Found {count} Wine process{'es' if count != 1 else ''}")
    
    def _create_library_tab(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(16)
        
        desc = QLabel("Browse and manage your application library")
        desc.setStyleSheet("color: #86868B; font-size: 13px; margin-bottom: 8px;")
        layout.addWidget(desc)
        
        list_group = QGroupBox("Application Library")
        list_layout = QVBoxLayout(list_group)
        
        self.library_list = QListWidget()
        list_layout.addWidget(self.library_list)
        
        button_layout = QHBoxLayout()
        add_button = StyledButton("➕ Add Application", primary=True)
        add_button.clicked.connect(self._add_to_library)
        button_layout.addWidget(add_button)
        
        remove_button = StyledButton("🗑️ Remove")
        remove_button.clicked.connect(self._remove_from_library)
        button_layout.addWidget(remove_button)
        
        refresh_button = StyledButton("🔄 Refresh")
        refresh_button.clicked.connect(self._refresh_library)
        button_layout.addWidget(refresh_button)
        
        button_layout.addStretch()
        list_layout.addLayout(button_layout)
        
        layout.addWidget(list_group)
        self._refresh_library()
        
        return widget
    
    def _create_templates_tab(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(16)
        
        desc = QLabel("Use prefix templates for quick setup of common configurations")
        desc.setStyleSheet("color: #86868B; font-size: 13px; margin-bottom: 8px;")
        layout.addWidget(desc)
        
        list_group = QGroupBox("Available Templates")
        list_layout = QVBoxLayout(list_group)
        
        self.template_list = QListWidget()
        list_layout.addWidget(self.template_list)
        
        button_layout = QHBoxLayout()
        apply_button = StyledButton("✅ Apply to Prefix", primary=True)
        apply_button.clicked.connect(self._apply_template)
        button_layout.addWidget(apply_button)
        
        create_button = StyledButton("➕ Create from Prefix")
        create_button.clicked.connect(self._create_template)
        button_layout.addWidget(create_button)
        
        refresh_button = StyledButton("🔄 Refresh")
        refresh_button.clicked.connect(self._refresh_templates)
        button_layout.addWidget(refresh_button)
        
        button_layout.addStretch()
        list_layout.addLayout(button_layout)
        
        layout.addWidget(list_group)
        self._refresh_templates()
        
        return widget
    
    def _create_winetricks_tab(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(16)
        
        desc = QLabel("Install Windows components and DLLs using Winetricks")
        desc.setStyleSheet("color: #86868B; font-size: 13px; margin-bottom: 8px;")
        layout.addWidget(desc)
        
        list_group = QGroupBox("Common Components")
        list_layout = QVBoxLayout(list_group)
        
        self.component_list = QListWidget()
        components = self.winetricks.list_common_components()
        for category, items in components.items():
            for item, desc in items.items():
                self.component_list.addItem(f"{item} - {desc}")
        list_layout.addWidget(self.component_list)
        
        button_layout = QHBoxLayout()
        install_button = StyledButton("📥 Install to Prefix", primary=True)
        install_button.clicked.connect(self._install_component)
        button_layout.addWidget(install_button)
        
        button_layout.addStretch()
        list_layout.addLayout(button_layout)
        
        layout.addWidget(list_group)
        
        return widget
    
    def _create_wine_versions_tab(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(16)
        
        desc = QLabel("Manage multiple Wine versions and assign them to prefixes")
        desc.setStyleSheet("color: #86868B; font-size: 13px; margin-bottom: 8px;")
        layout.addWidget(desc)
        
        list_group = QGroupBox("Installed Wine Versions")
        list_layout = QVBoxLayout(list_group)
        
        self.wine_version_list = QListWidget()
        list_layout.addWidget(self.wine_version_list)
        
        button_layout = QHBoxLayout()
        download_button = StyledButton("⬇️ Download Version", primary=True)
        download_button.clicked.connect(self._download_wine_version)
        button_layout.addWidget(download_button)
        
        switch_button = StyledButton("🔄 Set for Prefix")
        switch_button.clicked.connect(self._switch_wine_version)
        button_layout.addWidget(switch_button)
        
        delete_button = StyledButton("🗑️ Delete")
        delete_button.clicked.connect(self._delete_wine_version)
        button_layout.addWidget(delete_button)
        
        refresh_button = StyledButton("🔄 Refresh")
        refresh_button.clicked.connect(self._refresh_wine_versions)
        button_layout.addWidget(refresh_button)
        
        button_layout.addStretch()
        list_layout.addLayout(button_layout)
        
        layout.addWidget(list_group)
        self._refresh_wine_versions()
        
        return widget
    
    def _create_game_stores_tab(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(16)
        
        desc = QLabel("Integrate with Steam and Epic Games to import your library")
        desc.setStyleSheet("color: #86868B; font-size: 13px; margin-bottom: 8px;")
        layout.addWidget(desc)
        
        steam_group = QGroupBox("Steam Library")
        steam_layout = QVBoxLayout(steam_group)
        
        steam_button_layout = QHBoxLayout()
        scan_steam_button = StyledButton("🔍 Scan Steam", primary=True)
        scan_steam_button.clicked.connect(self._scan_steam)
        steam_button_layout.addWidget(scan_steam_button)
        
        import_steam_button = StyledButton("📥 Import to Library")
        import_steam_button.clicked.connect(self._import_steam)
        steam_button_layout.addWidget(import_steam_button)
        
        install_steam_button = StyledButton("💿 Install Steam")
        install_steam_button.clicked.connect(self._install_steam)
        steam_button_layout.addWidget(install_steam_button)
        
        steam_button_layout.addStretch()
        steam_layout.addLayout(steam_button_layout)
        
        self.steam_games_label = QLabel("Click 'Scan Steam' to find games")
        self.steam_games_label.setStyleSheet("color: #86868B; padding: 8px;")
        steam_layout.addWidget(self.steam_games_label)
        
        layout.addWidget(steam_group)
        
        epic_group = QGroupBox("Epic Games Library")
        epic_layout = QVBoxLayout(epic_group)
        
        epic_button_layout = QHBoxLayout()
        scan_epic_button = StyledButton("🔍 Scan Epic Games", primary=True)
        scan_epic_button.clicked.connect(self._scan_epic)
        epic_button_layout.addWidget(scan_epic_button)
        
        import_epic_button = StyledButton("📥 Import to Library")
        import_epic_button.clicked.connect(self._import_epic)
        epic_button_layout.addWidget(import_epic_button)
        
        epic_button_layout.addStretch()
        epic_layout.addLayout(epic_button_layout)
        
        self.epic_games_label = QLabel("Click 'Scan Epic Games' to find games")
        self.epic_games_label.setStyleSheet("color: #86868B; padding: 8px;")
        epic_layout.addWidget(self.epic_games_label)
        
        layout.addWidget(epic_group)
        layout.addStretch()
        
        return widget
    
    def _add_to_library(self):
        name, ok = QInputDialog.getText(self, "Add Application", "Application name:")
        if not ok or not name:
            return
        
        prefix, ok = QInputDialog.getText(self, "Add Application", "Prefix name:")
        if not ok or not prefix:
            return
        
        exe_path, _ = QFileDialog.getOpenFileName(self, "Select Executable")
        if not exe_path:
            return
        
        category, ok = QInputDialog.getText(self, "Add Application", "Category:", text="Games")
        if not ok:
            category = "Games"
        
        app_id = self.app_library.add_app(name, prefix, exe_path, category)
        if app_id:
            QMessageBox.information(self, "Success", f"Application '{name}' added to library")
            self._refresh_library()
        else:
            QMessageBox.warning(self, "Error", "Failed to add application")
    
    def _remove_from_library(self):
        selected = self.library_list.currentItem()
        if not selected:
            QMessageBox.warning(self, "Warning", "Please select an application")
            return
        
        app_text = selected.text()
        app_id = app_text.split(" -")[0]
        
        reply = QMessageBox.question(self, "Confirm", f"Remove '{app_text}' from library?")
        if reply == QMessageBox.StandardButton.Yes:
            if self.app_library.remove_app(app_id):
                QMessageBox.information(self, "Success", "Application removed")
                self._refresh_library()
            else:
                QMessageBox.warning(self, "Error", "Failed to remove application")
    
    def _refresh_library(self):
        self.library_list.clear()
        apps = self.app_library.list_apps()
        for app in apps:
            self.library_list.addItem(f"{app['id']} - {app['name']} ({app['category']})")
    
    def _apply_template(self):
        selected = self.template_list.currentItem()
        if not selected:
            QMessageBox.warning(self, "Warning", "Please select a template")
            return
        
        template_name = selected.text().split(" -")[0]
        prefix, ok = QInputDialog.getText(self, "Apply Template", "Target prefix name:")
        if not ok or not prefix:
            return
        
        success, message = self.templates.apply_template(template_name, prefix)
        if success:
            QMessageBox.information(self, "Success", message)
            self._refresh_prefixes()
        else:
            QMessageBox.warning(self, "Error", message)
    
    def _create_template(self):
        prefix, ok = QInputDialog.getText(self, "Create Template", "Source prefix name:")
        if not ok or not prefix:
            return
        
        name, ok = QInputDialog.getText(self, "Create Template", "Template name:")
        if not ok or not name:
            return
        
        desc, ok = QInputDialog.getText(self, "Create Template", "Description (optional):")
        if not ok:
            desc = ""
        
        if prefix not in self.wine_manager.prefixes:
            QMessageBox.warning(self, "Error", f"Prefix '{prefix}' not found")
            return
        
        prefix_path = self.wine_manager.prefixes[prefix]
        success, message = self.templates.create_template_from_prefix(name, prefix_path, desc)
        if success:
            QMessageBox.information(self, "Success", message)
            self._refresh_templates()
        else:
            QMessageBox.warning(self, "Error", message)
    
    def _refresh_templates(self):
        self.template_list.clear()
        templates = self.templates.list_templates()
        for template in templates:
            self.template_list.addItem(f"{template['name']} - {template['description']}")
    
    def _install_component(self):
        selected = self.component_list.currentItem()
        if not selected:
            QMessageBox.warning(self, "Warning", "Please select a component")
            return
        
        component = selected.text().split(" -")[0]
        prefix, ok = QInputDialog.getText(self, "Install Component", "Target prefix name:")
        if not ok or not prefix:
            return
        
        if prefix not in self.wine_manager.prefixes:
            QMessageBox.warning(self, "Error", f"Prefix '{prefix}' not found")
            return
        
        success, message = self.winetricks.install_component(prefix, component)
        if success:
            QMessageBox.information(self, "Success", message)
        else:
            QMessageBox.warning(self, "Error", message)
    
    def _download_wine_version(self):
        version, ok = QInputDialog.getText(self, "Download Wine", 
                                          "Version identifier (e.g., 'stable-8.0', 'staging-9.0', 'proton-8.0'):")
        if not ok or not version:
            return
        
        self.statusBar().showMessage(f"Downloading Wine {version}...")
        success, message = self.wine_versions.download_wine_version(version)
        if success:
            QMessageBox.information(self, "Success", message)
            self._refresh_wine_versions()
        else:
            QMessageBox.warning(self, "Error", message)
        self.statusBar().showMessage("Ready")
    
    def _switch_wine_version(self):
        selected = self.wine_version_list.currentItem()
        if not selected:
            QMessageBox.warning(self, "Warning", "Please select a Wine version")
            return
        
        version_name = selected.text().split(" (")[0]
        prefix, ok = QInputDialog.getText(self, "Switch Wine Version", "Prefix name:")
        if not ok or not prefix:
            return
        
        success, message = self.wine_versions.set_prefix_wine_version(prefix, version_name)
        if success:
            QMessageBox.information(self, "Success", message)
        else:
            QMessageBox.warning(self, "Error", message)
    
    def _delete_wine_version(self):
        selected = self.wine_version_list.currentItem()
        if not selected:
            QMessageBox.warning(self, "Warning", "Please select a Wine version")
            return
        
        version_name = selected.text().split(" (")[0]
        reply = QMessageBox.question(self, "Confirm", f"Delete Wine version '{version_name}'?")
        if reply == QMessageBox.StandardButton.Yes:
            success, message = self.wine_versions.delete_wine_version(version_name)
            if success:
                QMessageBox.information(self, "Success", message)
                self._refresh_wine_versions()
            else:
                QMessageBox.warning(self, "Error", message)
    
    def _refresh_wine_versions(self):
        self.wine_version_list.clear()
        versions = self.wine_versions.list_installed_versions()
        for version in versions:
            self.wine_version_list.addItem(f"{version.name} ({version.version_type})")
    
    def _scan_steam(self):
        self.statusBar().showMessage("Scanning Steam library...")
        games = self.game_stores.scan_steam_library()
        self.steam_games_label.setText(f"Found {len(games)} Steam games")
        self.statusBar().showMessage("Ready")
    
    def _import_steam(self):
        reply = QMessageBox.question(self, "Confirm", "Import all Steam games to library?")
        if reply == QMessageBox.StandardButton.Yes:
            count = self.game_stores.auto_import_games('steam')
            QMessageBox.information(self, "Success", f"Imported {count} games")
            self._refresh_library()
    
    def _install_steam(self):
        prefix, ok = QInputDialog.getText(self, "Install Steam", "Prefix name:")
        if not ok or not prefix:
            return
        
        self.statusBar().showMessage(f"Installing Steam to '{prefix}'...")
        success, message = self.game_stores.install_steam(prefix)
        if success:
            QMessageBox.information(self, "Success", message)
        else:
            QMessageBox.warning(self, "Error", message)
        self.statusBar().showMessage("Ready")
    
    def _scan_epic(self):
        self.statusBar().showMessage("Scanning Epic Games library...")
        games = self.game_stores.scan_epic_library()
        self.epic_games_label.setText(f"Found {len(games)} Epic games")
        self.statusBar().showMessage("Ready")
    
    def _import_epic(self):
        reply = QMessageBox.question(self, "Confirm", "Import all Epic games to library?")
        if reply == QMessageBox.StandardButton.Yes:
            count = self.game_stores.auto_import_games('epic')
            QMessageBox.information(self, "Success", f"Imported {count} games")
            self._refresh_library()
    
    def _update_system_info(self):
        info = self.platform.get_system_info()
        text = f"Platform: {info.get('platform', 'Unknown')}\n"
        text += f"Architecture: {info.get('architecture', 'Unknown')}\n"
        
        if 'version' in info:
            text += f"OS Version: {info['version']}\n"
        
        if 'is_apple_silicon' in info:
            text += f"Apple Silicon: {'Yes' if info['is_apple_silicon'] else 'No'}\n"
        
        text += "\n"
        
        wine_version = self.wine_manager.get_wine_version()
        if wine_version:
            text += f"Wine: {wine_version}\n"
            if self.wine_manager.wine_path:
                text += f"Wine Path: {self.wine_manager.wine_path}\n"
        else:
            text += "Wine: Not installed\n"
        
        text += f"\nPrefixes Directory:\n{self.platform.get_default_prefix_location()}\n"
        text += f"\nConfig File:\n{self.config.config_path}"
        
        self.system_info.setPlainText(text)
    
    def _setup_keyboard_shortcuts(self):
        """Setup keyboard shortcuts for common actions."""
        # Refresh - Command+R
        refresh_shortcut = QShortcut(QKeySequence("Ctrl+R"), self)
        refresh_shortcut.activated.connect(self._refresh_all)
        
        # Create Prefix - Command+N
        create_prefix_shortcut = QShortcut(QKeySequence.StandardKey.New, self)
        create_prefix_shortcut.activated.connect(self._on_create_prefix)
        
        # Quit - Command+Q
        quit_shortcut = QShortcut(QKeySequence.StandardKey.Quit, self)
        quit_shortcut.activated.connect(self.close)
        
        # Help - Command+?
        help_shortcut = QShortcut(QKeySequence("Ctrl+?"), self)
        help_shortcut.activated.connect(self._show_keyboard_shortcuts)
        
        # Export Logs - Command+E
        export_logs_shortcut = QShortcut(QKeySequence("Ctrl+E"), self)
        export_logs_shortcut.activated.connect(self._export_logs)
    
    def _show_keyboard_shortcuts(self):
        """Show keyboard shortcuts help dialog."""
        shortcuts_text = """
<h3>Keyboard Shortcuts</h3>
<table>
<tr><td><b>⌘+?</b></td><td>Show this help</td></tr>
<tr><td><b>⌘+R</b></td><td>Refresh all lists</td></tr>
<tr><td><b>⌘+N</b></td><td>Create new prefix</td></tr>
<tr><td><b>⌘+E</b></td><td>Export logs</td></tr>
<tr><td><b>⌘+Q</b></td><td>Quit application</td></tr>
</table>
        """
        QMessageBox.information(self, "Keyboard Shortcuts", shortcuts_text)
    
    def _export_logs(self):
        """Export logs to a zip file."""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Export Logs", str(Path.home() / "winvora_logs.zip"),
            "ZIP Files (*.zip)"
        )
        
        if file_path:
            self.statusBar().showMessage("Exporting logs...")
            QApplication.processEvents()
            
            if self.logger.export_logs(Path(file_path)):
                QMessageBox.information(
                    self, "Success", 
                    f"Logs exported to:\\n{file_path}"
                )
                self.notifications.notify_success("Logs Exported", "Logs successfully exported")
            else:
                QMessageBox.warning(self, "Error", "Failed to export logs")
            
            self.statusBar().showMessage("Ready")
    
    def _refresh_all(self):
        \"\"\"Refresh all lists.\"\"\"
        self.statusBar().showMessage("Refreshing...")
        QApplication.processEvents()
        self._refresh_prefixes()
        self._refresh_library()
        self.statusBar().showMessage("Ready")
    
    def _start_auto_refresh(self):
        self._refresh_prefixes()
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._auto_refresh)
        self.timer.start(5000)
    
    def _auto_refresh(self):
        if self.isVisible():
            current_tab = self.findChild(QTabWidget).currentIndex()
            if current_tab == 2:
                self._refresh_processes()


def main():
    if not PYQT_AVAILABLE:
        print("Error: PyQt6 is required to run the GUI application")
        print("Install with: pip install PyQt6")
        return 1
    
    app = QApplication(sys.argv)
    app.setApplicationName("Winvora")
    app.setOrganizationName("Winvora")
    app.setStyle('Fusion')
    
    window = WinvoraMainWindow()
    window.show()
    
    return app.exec()


if __name__ == '__main__':
    sys.exit(main())
