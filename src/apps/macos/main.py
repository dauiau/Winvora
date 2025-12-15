"""
Winvora macOS Desktop Application

GUI application for macOS using native frameworks.
This uses PyQt6 for cross-compatibility (also works on Linux).
"""

import sys
from pathlib import Path
from typing import Optional

try:
    from PyQt6.QtWidgets import (
        QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
        QPushButton, QListWidget, QLabel, QTabWidget, QMessageBox,
        QFileDialog, QInputDialog, QTextEdit, QGroupBox
    )
    from PyQt6.QtCore import Qt, QThread, pyqtSignal
    from PyQt6.QtGui import QIcon
    PYQT_AVAILABLE = True
except ImportError:
    PYQT_AVAILABLE = False
    print("PyQt6 not available. Install with: pip install PyQt6")

from core.wine_manager import WineManager
from core.config import Config
from platforms.macos import MacOSPlatform


class WinvoraMainWindow(QMainWindow):
    """
    Main window for Winvora macOS application.
    
    Features:
    - Prefix management (create, list, delete)
    - Application installation and launching
    - Wine configuration
    - Process monitoring
    - System information
    """
    
    def __init__(self):
        """Initialize the main window."""
        super().__init__()
        
        self.wine_manager = WineManager()
        self.config = Config()
        self.platform = MacOSPlatform()
        
        self.setWindowTitle("Winvora - Wine Manager")
        self.setMinimumSize(900, 600)
        
        self._init_ui()
    
    def _init_ui(self):
        """Initialize the user interface."""
        # Central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Create tab widget for different sections
        tabs = QTabWidget()
        main_layout.addWidget(tabs)
        
        # Add tabs
        tabs.addTab(self._create_prefixes_tab(), "Wine Prefixes")
        tabs.addTab(self._create_applications_tab(), "Applications")
        tabs.addTab(self._create_processes_tab(), "Processes")
        tabs.addTab(self._create_settings_tab(), "Settings")
        
        # Status bar
        self.statusBar().showMessage("Ready")
    
    def _create_prefixes_tab(self) -> QWidget:
        """
        Create the Wine prefixes management tab.
        
        Returns:
            Widget containing prefix management UI.
        """
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Header
        header = QLabel("Wine Prefixes")
        header.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(header)
        
        # Description
        desc = QLabel("Manage Wine prefixes for different applications and configurations")
        desc.setStyleSheet("color: gray;")
        layout.addWidget(desc)
        
        # Prefix list
        list_group = QGroupBox("Available Prefixes")
        list_layout = QVBoxLayout(list_group)
        
        self.prefix_list = QListWidget()
        list_layout.addWidget(self.prefix_list)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        create_btn = QPushButton("Create Prefix")
        create_btn.clicked.connect(self._on_create_prefix)
        button_layout.addWidget(create_btn)
        
        delete_btn = QPushButton("Delete Prefix")
        delete_btn.clicked.connect(self._on_delete_prefix)
        button_layout.addWidget(delete_btn)
        
        info_btn = QPushButton("Prefix Info")
        info_btn.clicked.connect(self._on_prefix_info)
        button_layout.addWidget(info_btn)
        
        button_layout.addStretch()
        list_layout.addLayout(button_layout)
        
        layout.addWidget(list_group)
        
        # Refresh button
        refresh_btn = QPushButton("Refresh List")
        refresh_btn.clicked.connect(self._refresh_prefixes)
        layout.addWidget(refresh_btn)
        
        return widget
    
    def _create_applications_tab(self) -> QWidget:
        """
        Create the applications management tab.
        
        Returns:
            Widget containing application management UI.
        """
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Header
        header = QLabel("Windows Applications")
        header.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(header)
        
        # Application list
        list_group = QGroupBox("Installed Applications")
        list_layout = QVBoxLayout(list_group)
        
        self.app_list = QListWidget()
        list_layout.addWidget(self.app_list)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        install_btn = QPushButton("Install Application")
        install_btn.clicked.connect(self._on_install_app)
        button_layout.addWidget(install_btn)
        
        run_btn = QPushButton("Run Application")
        run_btn.clicked.connect(self._on_run_app)
        button_layout.addWidget(run_btn)
        
        browse_btn = QPushButton("Browse .exe")
        browse_btn.clicked.connect(self._on_browse_exe)
        button_layout.addWidget(browse_btn)
        
        button_layout.addStretch()
        list_layout.addLayout(button_layout)
        
        layout.addWidget(list_group)
        
        return widget
    
    def _create_processes_tab(self) -> QWidget:
        """
        Create the process monitoring tab.
        
        Returns:
            Widget containing process monitoring UI.
        """
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Header
        header = QLabel("Running Wine Processes")
        header.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(header)
        
        # Process list
        self.process_list = QListWidget()
        layout.addWidget(self.process_list)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(self._refresh_processes)
        button_layout.addWidget(refresh_btn)
        
        kill_btn = QPushButton("Kill Selected")
        kill_btn.clicked.connect(self._on_kill_process)
        button_layout.addWidget(kill_btn)
        
        kill_all_btn = QPushButton("Kill All Wine")
        kill_all_btn.clicked.connect(self._on_kill_all)
        button_layout.addWidget(kill_all_btn)
        
        button_layout.addStretch()
        layout.addLayout(button_layout)
        
        return widget
    
    def _create_settings_tab(self) -> QWidget:
        """
        Create the settings tab.
        
        Returns:
            Widget containing settings UI.
        """
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Header
        header = QLabel("Winvora Settings")
        header.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(header)
        
        # System info
        info_group = QGroupBox("System Information")
        info_layout = QVBoxLayout(info_group)
        
        self.system_info = QTextEdit()
        self.system_info.setReadOnly(True)
        self._update_system_info()
        info_layout.addWidget(self.system_info)
        
        layout.addWidget(info_group)
        
        # Wine check
        check_btn = QPushButton("Check Wine Installation")
        check_btn.clicked.connect(self._on_check_wine)
        layout.addWidget(check_btn)
        
        layout.addStretch()
        
        return widget
    
    # Event handlers (placeholder implementations)
    
    def _on_create_prefix(self):
        """Handle create prefix button click."""
        name, ok = QInputDialog.getText(self, "Create Prefix", "Enter prefix name:")
        if ok and name:
            self.statusBar().showMessage(f"Creating prefix '{name}'...")
            success, message = self.wine_manager.create_prefix(name)
            if success:
                QMessageBox.information(self, "Success", message)
                self._refresh_prefixes()
            else:
                QMessageBox.warning(self, "Error", message)
            self.statusBar().showMessage("Ready")
    
    def _on_delete_prefix(self):
        """Handle delete prefix button click."""
        current = self.prefix_list.currentItem()
        if current:
            reply = QMessageBox.question(
                self, "Confirm Delete",
                f"Delete prefix '{current.text()}'?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.Yes:
                self.statusBar().showMessage(f"Deleting prefix...")
                success, message = self.wine_manager.delete_prefix(current.text())
                if success:
                    QMessageBox.information(self, "Success", message)
                    self._refresh_prefixes()
                else:
                    QMessageBox.warning(self, "Error", message)
                self.statusBar().showMessage("Ready")
    
    def _on_prefix_info(self):
        """Handle prefix info button click."""
        current = self.prefix_list.currentItem()
        if current:
            info_dict = self.wine_manager.get_prefix_info(current.text())
            if info_dict:
                info_text = f"Prefix: {info_dict['name']}\n"
                info_text += f"Path: {info_dict['path']}\n"
                info_text += f"Exists: {'Yes' if info_dict['exists'] else 'No'}\n"
                if 'windows_version' in info_dict:
                    info_text += f"Windows Version: {info_dict['windows_version']}"
                QMessageBox.information(self, "Prefix Information", info_text)
            else:
                QMessageBox.warning(self, "Error", f"Could not get info for prefix '{current.text()}'")
    
    def _on_install_app(self):
        """Handle install application button click."""
        # First, get the prefix to install into
        prefixes = self.wine_manager.list_prefixes()
        if not prefixes:
            QMessageBox.warning(self, "No Prefixes", "Create a prefix first before installing applications.")
            return
        
        prefix, ok = QInputDialog.getItem(
            self, "Select Prefix", "Install into prefix:", prefixes, 0, False
        )
        if not ok:
            return
        
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Installer",
            str(Path.home()),
            "Windows Executables (*.exe *.msi)"
        )
        if file_path:
            self.statusBar().showMessage(f"Installing {Path(file_path).name}...")
            success, message = self.wine_manager.install_application(prefix, Path(file_path))
            if success:
                QMessageBox.information(self, "Success", "Installation completed")
            else:
                QMessageBox.warning(self, "Error", f"Installation failed:\n{message}")
            self.statusBar().showMessage("Ready")
    
    def _on_run_app(self):
        """Handle run application button click."""
        current = self.app_list.currentItem()
        if current:
            self.statusBar().showMessage(f"Launching {current.text()}...")
            # Placeholder implementation
    
    def _on_browse_exe(self):
        """Handle browse exe button click."""
        # First, get the prefix to run in
        prefixes = self.wine_manager.list_prefixes()
        if not prefixes:
            QMessageBox.warning(self, "No Prefixes", "Create a prefix first before running applications.")
            return
        
        prefix, ok = QInputDialog.getItem(
            self, "Select Prefix", "Run in prefix:", prefixes, 0, False
        )
        if not ok:
            return
        
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Windows Executable",
            str(Path.home()),
            "Windows Executables (*.exe)"
        )
        if file_path:
            self.statusBar().showMessage(f"Running {Path(file_path).name}...")
            success, message = self.wine_manager.run_application(prefix, Path(file_path), background=True)
            if success:
                QMessageBox.information(self, "Success", message)
            else:
                QMessageBox.warning(self, "Error", f"Failed to run:\n{message}")
            self.statusBar().showMessage("Ready")
    
    def _on_kill_process(self):
        """Handle kill process button click."""
        current = self.process_list.currentItem()
        if current:
            # Extract PID from the list item text
            text = current.text()
            pid = text.split()[1]  # "PID 12345: ..." -> "12345"
            
            reply = QMessageBox.question(
                self, "Confirm Kill",
                f"Kill process {pid}?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.Yes:
                self.statusBar().showMessage("Killing process...")
                success, message = self.wine_manager.kill_process(pid)
                if success:
                    QMessageBox.information(self, "Success", message)
                    self._refresh_processes()
                else:
                    QMessageBox.warning(self, "Error", message)
                self.statusBar().showMessage("Ready")
    success, message = self.wine_manager.kill_all_wine()
            if success:
                QMessageBox.information(self, "Success", message)
                self._refresh_processes()
            else:
                QMessageBox.warning(self, "Error", message)
            self.statusBar().showMessage("Ready")
    def _on_kill_all(self):
        """Handle kill all Wine processes button click."""
        reply = QMessageBox.question(
            self, "Confirm Kill All",
            "Kill all Wine processes?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.statusBar().showMessage("Killing all Wine processes...")
            wine_version = self.wine_manager.get_wine_version()
            msg = "✓ Wine is installed and accessible"
            if wine_version:
                msg += f"\n\nVersion: {wine_version}"
            if self.wine_manager.wine_path:
                msg += f"\nPath: {self.wine_manager.wine_path}"
            QMessageBox.information(self, "Wine Check", msg
    
    def _on_check_wine(self):
        """Handle check Wine installation button click."""
        is_installed = self.wine_manager.verify_wine_installation()
        if is_installed:
            QMessageBox.information(self, "Wine Check", "✓ Wine is installed and accessible")
        else:
            QMessageBox.warning(
                self, "Wine Check",
                "✗ Wine not found\n\nInstall with: brew install wine-stable"
            )
    
    def _refresh_prefixes(self):
        """Refresh the prefix list."""
        self.prefix_list.clear()
        prefixes = self.wine_manager.list_prefixes()
        for prefix in prefixes:
        processes = self.wine_manager.get_running_processes()
        for proc in processes:
            self.process_list.addItem(f"PID {proc['pid']}: {proc['command']}")
        self.statusBar().showMessage(f"Found {len(processes)} Wine process(es))
    
    def _refresh_processes(self):
        """Refresh the process list."""
        self.process_list.clear()
        # Placeholder implementation
        self.statusBar().showMessage("Process list refreshed")
    
    def _update_system_info(self):
        """Update system information display."""
        info = self.platform.get_system_info()
"""
        
        if 'version' in info:
            text += f"Version: {info['version']}\n"
        
        if 'is_apple_silicon' in info:
            text += f"Apple Silicon: {'Yes' if info['is_apple_silicon'] else 'No'}\n"
        
        wine_version = self.wine_manager.get_wine_version()
        if wine_version:
            text += f"\nWine Version: {wine_version}\n"
        else:
            text += f"\nWine: Not installed\n"
        
        if self.wine_manager.wine_path:
            text += f"Wine Path: {self.wine_manager.wine_path}\n"
        
        text += f"\nDefault Prefix Location:\n{self.platform.get_default_prefix_location()}"
        e Path: {self.platform.get_wine_paths()[0] if self.platform.get_wine_paths() else 'Not found'}
Default Prefix Location: {self.platform.get_default_prefix_location()}
"""
        self.system_info.setPlainText(text)


def main():
    """Main entry point for the macOS application."""
    if not PYQT_AVAILABLE:
        print("Error: PyQt6 is required to run the GUI application")
        print("Install with: pip install PyQt6")
        return 1
    
    app = QApplication(sys.argv)
    app.setApplicationName("Winvora")
    app.setOrganizationName("Winvora")
    
    window = WinvoraMainWindow()
    window.show()
    
    return app.exec()


if __name__ == '__main__':
    sys.exit(main())
