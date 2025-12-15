"""
Winvora Android Application

Mobile application for Android using Kivy framework.
Note: This is a simplified mobile UI designed for touch interfaces.
"""

import sys
from pathlib import Path

try:
    from kivy.app import App
    from kivy.uix.boxlayout import BoxLayout
    from kivy.uix.button import Button
    from kivy.uix.label import Label
    from kivy.uix.scrollview import ScrollView
    from kivy.uix.gridlayout import GridLayout
    from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelItem
    from kivy.uix.popup import Popup
    from kivy.uix.textinput import TextInput
    KIVY_AVAILABLE = True
except ImportError:
    KIVY_AVAILABLE = False
    print("Kivy not available. Install with: pip install kivy")

from core.wine_manager import WineManager
from core.config import Config
from platforms.android import AndroidPlatform


if KIVY_AVAILABLE:
    class PrefixesTab(BoxLayout):
        """Tab for managing Wine prefixes."""
        
        def __init__(self, wine_manager, **kwargs):
            super().__init__(orientation='vertical', **kwargs)
            self.wine_manager = wine_manager
            
            # Header
            header = Label(
                text='Wine Prefixes',
                size_hint=(1, 0.1),
                font_size='20sp',
                bold=True
            )
            self.add_widget(header)
            
            # Prefix list (scrollable)
            scroll = ScrollView(size_hint=(1, 0.7))
            self.prefix_list = GridLayout(cols=1, spacing=10, size_hint_y=None)
            self.prefix_list.bind(minimum_height=self.prefix_list.setter('height'))
            scroll.add_widget(self.prefix_list)
            self.add_widget(scroll)
            
            # Buttons
            button_layout = GridLayout(cols=3, size_hint=(1, 0.2), spacing=10, padding=10)
            
            create_btn = Button(text='Create', on_press=self.create_prefix)
            button_layout.add_widget(create_btn)
            
            delete_btn = Button(text='Delete', on_press=self.delete_prefix)
            button_layout.add_widget(delete_btn)
            
            refresh_btn = Button(text='Refresh', on_press=self.refresh_list)
            button_layout.add_widget(refresh_btn)
            
            self.add_widget(button_layout)
            
            self.refresh_list()
        
        def refresh_list(self, *args):
            """Refresh the prefix list."""
            self.prefix_list.clear_widgets()
            prefixes = self.wine_manager.list_prefixes()
            
            if not prefixes:
                label = Label(text='No prefixes found', size_hint_y=None, height=40)
                self.prefix_list.add_widget(label)
            else:
                for prefix in prefixes:
                    btn = Button(
                        text=prefix,
                        size_hint_y=None,
                        height=60,
                        on_press=lambda x, p=prefix: self.show_prefix_info(p)
                    )
                    self.prefix_list.add_widget(btn)
        
        def create_prefix(self, *args):
            """Show dialog to create a new prefix."""
            content = BoxLayout(orientation='vertical', padding=10, spacing=10)
            
            content.add_widget(Label(text='Enter prefix name:'))
            name_input = TextInput(multiline=False, size_hint=(1, 0.3))
            content.add_widget(name_input)
            
            button_layout = BoxLayout(size_hint=(1, 0.3), spacing=10)
            
            popup = Popup(title='Create Prefix', content=content, size_hint=(0.9, 0.4))
            
            def on_create(*args):
                if name_input.text:
                    success, message = self.wine_manager.create_prefix(name_input.text)
                    popup.dismiss()
                    
                    # Show result popup
                    result_popup = Popup(
                        title='Success' if success else 'Error',
                        content=Label(text=message),
                        size_hint=(0.8, 0.3)
                    )
                    result_popup.open()
                    
                    if success:
                        self.refresh_list()
            
            create_btn = Button(text='Create', on_press=on_create)
            cancel_btn = Button(text='Cancel', on_press=popup.dismiss)
            
            button_layout.add_widget(create_btn)
            button_layout.add_widget(cancel_btn)
            content.add_widget(button_layout)
            
            popup.open()
        
        def delete_prefix(self, *args):
            """Delete selected prefix."""
            # Placeholder implementation
            pass
        
        def show_prefix_info(self, prefix_name):
            """Show information about a prefix."""
            content = BoxLayout(orientation='vertical', padding=10, spacing=10)
            
            info_dict = self.wine_manager.get_prefix_info(prefix_name)
            if info_dict:
                info = f"Prefix: {info_dict['name']}\n"
                info += f"Path: {info_dict['path']}\n"
                info += f"Exists: {'Yes' if info_dict['exists'] else 'No'}\n"
                if 'windows_version' in info_dict:
                    info += f"Windows Version: {info_dict['windows_version']}"
            else:
                info = f"Could not load info for {prefix_name}"
            
            content.add_widget(Label(text=info))
            
            close_btn = Button(text='Close', size_hint=(1, 0.2))
            popup = Popup(title='Prefix Info', content=content, size_hint=(0.8, 0.4))
            close_btn.bind(on_press=popup.dismiss)
            content.add_widget(close_btn)
            
            popup.open()


    class ApplicationsTab(BoxLayout):
        """Tab for managing applications."""
        
        def __init__(self, wine_manager, **kwargs):
            super().__init__(orientation='vertical', **kwargs)
            self.wine_manager = wine_manager
            
            # Header
            header = Label(
                text='Windows Applications',
                size_hint=(1, 0.1),
                font_size='20sp',
                bold=True
            )
            self.add_widget(header)
            
            # App list (scrollable)
            scroll = ScrollView(size_hint=(1, 0.7))
            self.app_list = GridLayout(cols=1, spacing=10, size_hint_y=None)
            self.app_list.bind(minimum_height=self.app_list.setter('height'))
            scroll.add_widget(self.app_list)
            self.add_widget(scroll)
            
            # Buttons
            button_layout = GridLayout(cols=2, size_hint=(1, 0.2), spacing=10, padding=10)
            
            install_btn = Button(text='Install App', on_press=self.install_app)
            button_layout.add_widget(install_btn)
            
            browse_btn = Button(text='Browse Files', on_press=self.browse_files)
            button_layout.add_widget(browse_btn)
            
            self.add_widget(button_layout)
        
        def install_app(self, *args):
            """Show dialog to install an application."""
            # Placeholder implementation
            popup = Popup(
                title='Install Application',
                content=Label(text='File browser not implemented'),
                size_hint=(0.8, 0.3)
            )
            popup.open()
        
        def browse_files(self, *args):
            """Browse for executable files."""
            # Placeholder implementation
            pass


    class SystemTab(BoxLayout):
        """Tab for system information and settings."""
        
        def __init__(self, platform, wine_manager, **kwargs):
            super().__init__(orientation='vertical', **kwargs)
            self.platform = platform
            self.wine_manager = wine_manager
            
            # Header
            header = Label(
                text='System Information',
                size_hint=(1, 0.1),
                font_size='20sp',
                bold=True
            )
            self.add_widget(header)
            
            # System info (scrollable)
            scroll = ScrollView(size_hint=(1, 0.7))
            info = self.platform.get_system_info()
            info_text = f"""Platform: {info.get('platform', 'Unknown')}
API Level: {info.get('api_level', 'Unknown')}
Architecture: {info.get('architecture', 'Unknown')}

Default Prefix Location:
{self.platform.get_default_prefix_location()}

Note: Wine on Android requires special builds
(e.g., Wine-Android or Termux with Wine)
"""
            info_label = Label(
                text=info_text,
                size_hint_y=None,
                height=400,
                text_size=(None, None)
            )
            scroll.add_widget(info_label)
            self.add_widget(scroll)
            
            # Check button
            check_btn = Button(
                text='Check Wine Installation',
                size_hint=(1, 0.2),
                on_press=self.check_wine
            )
            self.add_widget(check_btn)
        
        def check_wine(self, *args):
            """Check Wine installation."""
            is_compatible, compat_message = self.platform.check_compatibility()
            is_installed = self.wine_manager.verify_wine_installation()
            
            status = "✓ Wine installed" if is_installed else "✗ Wine not found"
            
            if is_installed:
                wine_version = self.wine_manager.get_wine_version()
                if wine_version:
                    status += f"\n\nVersion: {wine_version}"
            
            if not is_compatible:
                status += f"\n\nCompatibility: {compat_message}"
            
            popup = Popup(
                title='Wine Check',
                content=Label(text=status),
                size_hint=(0.8, 0.5)
            )
            popup.open()


    class WinvoraApp(App):
        """
        Main Kivy application for Android.
        
        Features:
        - Touch-optimized interface
        - Prefix management
        - Application launching
        - System information
        """
        
        def __init__(self, **kwargs):
            super().__init__(**kwargs)
            self.wine_manager = WineManager()
            self.config_manager = Config()
            self.platform = AndroidPlatform()
        
        def build(self):
            """Build the application UI."""
            # Create tabbed panel
            tab_panel = TabbedPanel(do_default_tab=False)
            
            # Prefixes tab
            prefixes_tab = TabbedPanelItem(text='Prefixes')
            prefixes_tab.add_widget(PrefixesTab(self.wine_manager))
            tab_panel.add_widget(prefixes_tab)
            
            # Applications tab
            apps_tab = TabbedPanelItem(text='Apps')
            apps_tab.add_widget(ApplicationsTab(self.wine_manager))
            tab_panel.add_widget(apps_tab)
            
            # System tab
            system_tab = TabbedPanelItem(text='System')
            system_tab.add_widget(SystemTab(self.platform, self.wine_manager))
            tab_panel.add_widget(system_tab)
            
            return tab_panel


def main():
    """Main entry point for the Android application."""
    if not KIVY_AVAILABLE:
        print("Error: Kivy is required to run the Android application")
        print("Install with: pip install kivy")
        return 1
    
    WinvoraApp().run()
    return 0


if __name__ == '__main__':
    sys.exit(main())
