import sys
from pathlib import Path
from typing import Optional

try:
    from PyQt6.QtWidgets import (
        QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
        QPushButton, QListWidget, QLabel, QTabWidget, QMessageBox,
        QFileDialog, QInputDialog, QTextEdit, QGroupBox, QStatusBar,
        QListWidgetItem, QSplitter
    )
    from PyQt6.QtCore import Qt, QTimer
    from PyQt6.QtGui import QFont, QColor, QPalette
    PYQT_AVAILABLE = True
except ImportError:
    PYQT_AVAILABLE = False

from core.wine_manager import WineManager
from core.config import Config
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
        
        self.setWindowTitle("Winvora")
        self.setMinimumSize(1000, 700)
        
        self._apply_modern_style()
        self._init_ui()
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
