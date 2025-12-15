import os
import sys
from pathlib import Path
from typing import Optional

try:
    from kivy.app import App
    from kivy.uix.screenmanager import ScreenManager, Screen
    from kivy.uix.boxlayout import BoxLayout
    from kivy.uix.button import Button
    from kivy.uix.label import Label
    from kivy.uix.scrollview import ScrollView
    from kivy.uix.gridlayout import GridLayout
    from kivy.uix.popup import Popup
    from kivy.uix.textinput import TextInput
    from kivy.uix.filechooser import FileChooserListView
    from kivy.clock import Clock
    from kivy.graphics import Color, RoundedRectangle
    KIVY_AVAILABLE = True
except ImportError:
    KIVY_AVAILABLE = False

from core.wine_manager import WineManager
from core.config import Config
from core.winetricks import WineTricksManager
from core.app_library import AppLibrary
from core.dxvk import DXVKManager
from core.prefix_templates import PrefixTemplateManager
from core.wine_versions import WineVersionManager
from core.game_stores import GameStoreIntegration
from platforms.android import AndroidPlatform


class StyledButton(Button):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_color = (0, 0.48, 1, 1)
        self.color = (1, 1, 1, 1)
        self.size_hint_y = None
        self.height = 50
        self.bold = True


class SecondaryButton(Button):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_color = (0.96, 0.96, 0.97, 1)
        self.color = (0.11, 0.11, 0.12, 1)
        self.size_hint_y = None
        self.height = 50


class PrefixesScreen(Screen):
    def __init__(self, wine_manager, **kwargs):
        super().__init__(**kwargs)
        self.wine_manager = wine_manager
        
        layout = BoxLayout(orientation='vertical', padding=15, spacing=10)
        
        header = Label(
            text='Wine Prefixes',
            size_hint_y=None,
            height=60,
            font_size=28,
            bold=True,
            color=(0.11, 0.11, 0.12, 1)
        )
        layout.add_widget(header)
        
        desc = Label(
            text='Manage Wine prefixes',
            size_hint_y=None,
            height=30,
            font_size=14,
            color=(0.53, 0.53, 0.56, 1)
        )
        layout.add_widget(desc)
        
        scroll = ScrollView()
        self.prefix_list = GridLayout(cols=1, spacing=5, size_hint_y=None)
        self.prefix_list.bind(minimum_height=self.prefix_list.setter('height'))
        scroll.add_widget(self.prefix_list)
        layout.add_widget(scroll)
        
        btn_layout = BoxLayout(size_hint_y=None, height=60, spacing=10)
        
        create_btn = StyledButton(text='Create Prefix')
        create_btn.bind(on_press=self.show_create_popup)
        btn_layout.add_widget(create_btn)
        
        refresh_btn = SecondaryButton(text='↻ Refresh')
        refresh_btn.bind(on_press=lambda x: self.load_prefixes())
        btn_layout.add_widget(refresh_btn)
        
        layout.add_widget(btn_layout)
        self.add_widget(layout)
        
        Clock.schedule_once(lambda dt: self.load_prefixes(), 0.1)
    
    def load_prefixes(self):
        self.prefix_list.clear_widgets()
        prefixes = self.wine_manager.list_prefixes()
        
        for prefix in prefixes:
            item_layout = BoxLayout(size_hint_y=None, height=60, spacing=10)
            
            label = Label(
                text=f'🍷 {prefix}',
                size_hint_x=0.6,
                font_size=16
            )
            item_layout.add_widget(label)
            
            info_btn = SecondaryButton(text='Info', size_hint_x=0.2)
            info_btn.bind(on_press=lambda x, p=prefix: self.show_info(p))
            item_layout.add_widget(info_btn)
            
            delete_btn = SecondaryButton(text='Delete', size_hint_x=0.2)
            delete_btn.bind(on_press=lambda x, p=prefix: self.confirm_delete(p))
            item_layout.add_widget(delete_btn)
            
            self.prefix_list.add_widget(item_layout)
    
    def show_create_popup(self, instance):
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        content.add_widget(Label(text='Enter prefix name:', size_hint_y=0.3))
        
        text_input = TextInput(multiline=False, size_hint_y=0.3)
        content.add_widget(text_input)
        
        btn_layout = BoxLayout(size_hint_y=0.4, spacing=10)
        
        def create_prefix(instance):
            name = text_input.text.strip()
            if name:
                popup.dismiss()
                success, message = self.wine_manager.create_prefix(name)
                self.show_message('Success' if success else 'Error', message)
                if success:
                    self.load_prefixes()
        
        create_btn = StyledButton(text='Create')
        create_btn.bind(on_press=create_prefix)
        btn_layout.add_widget(create_btn)
        
        cancel_btn = SecondaryButton(text='Cancel')
        cancel_btn.bind(on_press=lambda x: popup.dismiss())
        btn_layout.add_widget(cancel_btn)
        
        content.add_widget(btn_layout)
        
        popup = Popup(title='Create Prefix', content=content, size_hint=(0.9, 0.5))
        popup.open()
    
    def confirm_delete(self, prefix):
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        content.add_widget(Label(
            text=f'Delete prefix "{prefix}"?\n\nThis cannot be undone.',
            size_hint_y=0.6
        ))
        
        btn_layout = BoxLayout(size_hint_y=0.4, spacing=10)
        
        def do_delete(instance):
            popup.dismiss()
            success, message = self.wine_manager.delete_prefix(prefix)
            self.show_message('Success' if success else 'Error', message)
            if success:
                self.load_prefixes()
        
        delete_btn = StyledButton(text='Delete')
        delete_btn.bind(on_press=do_delete)
        btn_layout.add_widget(delete_btn)
        
        cancel_btn = SecondaryButton(text='Cancel')
        cancel_btn.bind(on_press=lambda x: popup.dismiss())
        btn_layout.add_widget(cancel_btn)
        
        content.add_widget(btn_layout)
        
        popup = Popup(title='Confirm Delete', content=content, size_hint=(0.9, 0.4))
        popup.open()
    
    def show_info(self, prefix):
        info_dict = self.wine_manager.get_prefix_info(prefix)
        if info_dict:
            info_text = f"Prefix: {info_dict['name']}\n"
            info_text += f"Path: {info_dict['path']}\n"
            info_text += f"Status: {'Active' if info_dict['exists'] else 'Missing'}"
            self.show_message('Prefix Information', info_text)
        else:
            self.show_message('Error', f'Could not get info for prefix "{prefix}"')
    
    def show_message(self, title, message):
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        content.add_widget(Label(text=message, size_hint_y=0.7))
        
        btn = StyledButton(text='OK', size_hint_y=0.3)
        btn.bind(on_press=lambda x: popup.dismiss())
        content.add_widget(btn)
        
        popup = Popup(title=title, content=content, size_hint=(0.9, 0.5))
        popup.open()


class ApplicationsScreen(Screen):
    def __init__(self, wine_manager, **kwargs):
        super().__init__(**kwargs)
        self.wine_manager = wine_manager
        
        layout = BoxLayout(orientation='vertical', padding=15, spacing=10)
        
        header = Label(
            text='Applications',
            size_hint_y=None,
            height=60,
            font_size=28,
            bold=True,
            color=(0.11, 0.11, 0.12, 1)
        )
        layout.add_widget(header)
        
        desc = Label(
            text='Install and run Windows apps',
            size_hint_y=None,
            height=30,
            font_size=14,
            color=(0.53, 0.53, 0.56, 1)
        )
        layout.add_widget(desc)
        
        btn_layout = BoxLayout(
            orientation='vertical',
            spacing=10,
            size_hint_y=None,
            height=240
        )
        
        install_btn = StyledButton(text='Install Application')
        install_btn.bind(on_press=self.show_install_popup)
        btn_layout.add_widget(install_btn)
        
        run_btn = StyledButton(text='Run .exe File')
        run_btn.bind(on_press=self.show_run_popup)
        btn_layout.add_widget(run_btn)
        
        cfg_btn = SecondaryButton(text='Configure Wine')
        cfg_btn.bind(on_press=self.show_configure_popup)
        btn_layout.add_widget(cfg_btn)
        
        layout.add_widget(btn_layout)
        layout.add_widget(Label())
        
        self.add_widget(layout)
    
    def show_install_popup(self, instance):
        prefixes = self.wine_manager.list_prefixes()
        if not prefixes:
            self.show_message('No Prefixes', 'Create a Wine prefix first')
            return
        
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        content.add_widget(Label(text='Select prefix:', size_hint_y=0.2))
        
        scroll = ScrollView(size_hint_y=0.5)
        prefix_layout = GridLayout(cols=1, spacing=5, size_hint_y=None)
        prefix_layout.bind(minimum_height=prefix_layout.setter('height'))
        
        selected_prefix = [None]
        
        for prefix in prefixes:
            btn = SecondaryButton(text=prefix)
            def select_prefix(instance, p=prefix):
                selected_prefix[0] = p
                popup.dismiss()
                self.select_installer_file(p)
            btn.bind(on_press=select_prefix)
            prefix_layout.add_widget(btn)
        
        scroll.add_widget(prefix_layout)
        content.add_widget(scroll)
        
        cancel_btn = SecondaryButton(text='Cancel', size_hint_y=0.3)
        cancel_btn.bind(on_press=lambda x: popup.dismiss())
        content.add_widget(cancel_btn)
        
        popup = Popup(title='Select Prefix', content=content, size_hint=(0.9, 0.7))
        popup.open()
    
    def select_installer_file(self, prefix):
        content = BoxLayout(orientation='vertical')
        
        filechooser = FileChooserListView(
            path='/storage/emulated/0/',
            filters=['*.exe', '*.msi']
        )
        content.add_widget(filechooser)
        
        btn_layout = BoxLayout(size_hint_y=None, height=60, spacing=10)
        
        def install_file(instance):
            if filechooser.selection:
                popup.dismiss()
                file_path = Path(filechooser.selection[0])
                success, message = self.wine_manager.install_application(prefix, file_path)
                self.show_message('Success' if success else 'Error', message)
        
        install_btn = StyledButton(text='Install')
        install_btn.bind(on_press=install_file)
        btn_layout.add_widget(install_btn)
        
        cancel_btn = SecondaryButton(text='Cancel')
        cancel_btn.bind(on_press=lambda x: popup.dismiss())
        btn_layout.add_widget(cancel_btn)
        
        content.add_widget(btn_layout)
        
        popup = Popup(title='Select Installer', content=content, size_hint=(0.95, 0.9))
        popup.open()
    
    def show_run_popup(self, instance):
        prefixes = self.wine_manager.list_prefixes()
        if not prefixes:
            self.show_message('No Prefixes', 'Create a Wine prefix first')
            return
        
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        content.add_widget(Label(text='Select prefix:', size_hint_y=0.2))
        
        scroll = ScrollView(size_hint_y=0.5)
        prefix_layout = GridLayout(cols=1, spacing=5, size_hint_y=None)
        prefix_layout.bind(minimum_height=prefix_layout.setter('height'))
        
        for prefix in prefixes:
            btn = SecondaryButton(text=prefix)
            def select_prefix(instance, p=prefix):
                popup.dismiss()
                self.select_exe_file(p)
            btn.bind(on_press=select_prefix)
            prefix_layout.add_widget(btn)
        
        scroll.add_widget(prefix_layout)
        content.add_widget(scroll)
        
        cancel_btn = SecondaryButton(text='Cancel', size_hint_y=0.3)
        cancel_btn.bind(on_press=lambda x: popup.dismiss())
        content.add_widget(cancel_btn)
        
        popup = Popup(title='Select Prefix', content=content, size_hint=(0.9, 0.7))
        popup.open()
    
    def select_exe_file(self, prefix):
        content = BoxLayout(orientation='vertical')
        
        filechooser = FileChooserListView(
            path='/storage/emulated/0/',
            filters=['*.exe']
        )
        content.add_widget(filechooser)
        
        btn_layout = BoxLayout(size_hint_y=None, height=60, spacing=10)
        
        def run_file(instance):
            if filechooser.selection:
                popup.dismiss()
                file_path = Path(filechooser.selection[0])
                success, message = self.wine_manager.run_application(prefix, file_path, background=True)
                self.show_message('Success' if success else 'Error', message)
        
        run_btn = StyledButton(text='Run')
        run_btn.bind(on_press=run_file)
        btn_layout.add_widget(run_btn)
        
        cancel_btn = SecondaryButton(text='Cancel')
        cancel_btn.bind(on_press=lambda x: popup.dismiss())
        btn_layout.add_widget(cancel_btn)
        
        content.add_widget(btn_layout)
        
        popup = Popup(title='Select Executable', content=content, size_hint=(0.95, 0.9))
        popup.open()
    
    def show_configure_popup(self, instance):
        prefixes = self.wine_manager.list_prefixes()
        if not prefixes:
            self.show_message('No Prefixes', 'Create a Wine prefix first')
            return
        
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        content.add_widget(Label(text='Select prefix to configure:', size_hint_y=0.2))
        
        scroll = ScrollView(size_hint_y=0.5)
        prefix_layout = GridLayout(cols=1, spacing=5, size_hint_y=None)
        prefix_layout.bind(minimum_height=prefix_layout.setter('height'))
        
        for prefix in prefixes:
            btn = SecondaryButton(text=prefix)
            def configure_prefix(instance, p=prefix):
                popup.dismiss()
                success, message = self.wine_manager.configure_prefix(p)
                self.show_message('Info', message)
            btn.bind(on_press=configure_prefix)
            prefix_layout.add_widget(btn)
        
        scroll.add_widget(prefix_layout)
        content.add_widget(scroll)
        
        cancel_btn = SecondaryButton(text='Cancel', size_hint_y=0.3)
        cancel_btn.bind(on_press=lambda x: popup.dismiss())
        content.add_widget(cancel_btn)
        
        popup = Popup(title='Configure Wine', content=content, size_hint=(0.9, 0.7))
        popup.open()
    
    def show_message(self, title, message):
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        content.add_widget(Label(text=message, size_hint_y=0.7))
        
        btn = StyledButton(text='OK', size_hint_y=0.3)
        btn.bind(on_press=lambda x: popup.dismiss())
        content.add_widget(btn)
        
        popup = Popup(title=title, content=content, size_hint=(0.9, 0.5))
        popup.open()


class ProcessesScreen(Screen):
    def __init__(self, wine_manager, **kwargs):
        super().__init__(**kwargs)
        self.wine_manager = wine_manager
        
        layout = BoxLayout(orientation='vertical', padding=15, spacing=10)
        
        header = Label(
            text='Wine Processes',
            size_hint_y=None,
            height=60,
            font_size=28,
            bold=True,
            color=(0.11, 0.11, 0.12, 1)
        )
        layout.add_widget(header)
        
        desc = Label(
            text='Monitor running processes',
            size_hint_y=None,
            height=30,
            font_size=14,
            color=(0.53, 0.53, 0.56, 1)
        )
        layout.add_widget(desc)
        
        scroll = ScrollView()
        self.process_list = GridLayout(cols=1, spacing=5, size_hint_y=None)
        self.process_list.bind(minimum_height=self.process_list.setter('height'))
        scroll.add_widget(self.process_list)
        layout.add_widget(scroll)
        
        btn_layout = BoxLayout(size_hint_y=None, height=60, spacing=10)
        
        refresh_btn = StyledButton(text='↻ Refresh')
        refresh_btn.bind(on_press=lambda x: self.load_processes())
        btn_layout.add_widget(refresh_btn)
        
        kill_all_btn = SecondaryButton(text='Kill All Wine')
        kill_all_btn.bind(on_press=self.confirm_kill_all)
        btn_layout.add_widget(kill_all_btn)
        
        layout.add_widget(btn_layout)
        self.add_widget(layout)
        
        Clock.schedule_once(lambda dt: self.load_processes(), 0.1)
    
    def load_processes(self):
        self.process_list.clear_widgets()
        processes = self.wine_manager.get_running_processes()
        
        if not processes:
            self.process_list.add_widget(Label(
                text='No Wine processes running',
                size_hint_y=None,
                height=60,
                color=(0.53, 0.53, 0.56, 1)
            ))
            return
        
        for proc in processes:
            item_layout = BoxLayout(size_hint_y=None, height=60, spacing=10)
            
            label = Label(
                text=f"PID {proc['pid']}: {proc['command'][:30]}...",
                size_hint_x=0.7,
                font_size=14
            )
            item_layout.add_widget(label)
            
            kill_btn = SecondaryButton(text='Kill', size_hint_x=0.3)
            kill_btn.bind(on_press=lambda x, p=proc['pid']: self.confirm_kill(p))
            item_layout.add_widget(kill_btn)
            
            self.process_list.add_widget(item_layout)
    
    def confirm_kill(self, pid):
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        content.add_widget(Label(
            text=f'Kill process {pid}?',
            size_hint_y=0.6
        ))
        
        btn_layout = BoxLayout(size_hint_y=0.4, spacing=10)
        
        def do_kill(instance):
            popup.dismiss()
            success, message = self.wine_manager.kill_process(pid)
            self.show_message('Success' if success else 'Error', message)
            if success:
                self.load_processes()
        
        kill_btn = StyledButton(text='Kill')
        kill_btn.bind(on_press=do_kill)
        btn_layout.add_widget(kill_btn)
        
        cancel_btn = SecondaryButton(text='Cancel')
        cancel_btn.bind(on_press=lambda x: popup.dismiss())
        btn_layout.add_widget(cancel_btn)
        
        content.add_widget(btn_layout)
        
        popup = Popup(title='Confirm Kill', content=content, size_hint=(0.9, 0.4))
        popup.open()
    
    def confirm_kill_all(self, instance):
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        content.add_widget(Label(
            text='Kill all Wine processes?\n\nThis closes all Windows apps.',
            size_hint_y=0.6
        ))
        
        btn_layout = BoxLayout(size_hint_y=0.4, spacing=10)
        
        def do_kill_all(instance):
            popup.dismiss()
            success, message = self.wine_manager.kill_all_wine()
            self.show_message('Success' if success else 'Error', message)
            if success:
                self.load_processes()
        
        kill_btn = StyledButton(text='Kill All')
        kill_btn.bind(on_press=do_kill_all)
        btn_layout.add_widget(kill_btn)
        
        cancel_btn = SecondaryButton(text='Cancel')
        cancel_btn.bind(on_press=lambda x: popup.dismiss())
        btn_layout.add_widget(cancel_btn)
        
        content.add_widget(btn_layout)
        
        popup = Popup(title='Confirm Kill All', content=content, size_hint=(0.9, 0.4))
        popup.open()
    
    def show_message(self, title, message):
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        content.add_widget(Label(text=message, size_hint_y=0.7))
        
        btn = StyledButton(text='OK', size_hint_y=0.3)
        btn.bind(on_press=lambda x: popup.dismiss())
        content.add_widget(btn)
        
        popup = Popup(title=title, content=content, size_hint=(0.9, 0.5))
        popup.open()


class SettingsScreen(Screen):
    def __init__(self, wine_manager, platform, config, **kwargs):
        super().__init__(**kwargs)
        self.wine_manager = wine_manager
        self.platform = platform
        self.config = config
        
        layout = BoxLayout(orientation='vertical', padding=15, spacing=10)
        
        header = Label(
            text='Settings',
            size_hint_y=None,
            height=60,
            font_size=28,
            bold=True,
            color=(0.11, 0.11, 0.12, 1)
        )
        layout.add_widget(header)
        
        desc = Label(
            text='System information',
            size_hint_y=None,
            height=30,
            font_size=14,
            color=(0.53, 0.53, 0.56, 1)
        )
        layout.add_widget(desc)
        
        scroll = ScrollView()
        self.info_label = Label(
            size_hint_y=None,
            halign='left',
            valign='top',
            font_size=13,
            color=(0.33, 0.33, 0.33, 1)
        )
        self.info_label.bind(texture_size=self.info_label.setter('size'))
        scroll.add_widget(self.info_label)
        layout.add_widget(scroll)
        
        check_btn = StyledButton(text='Check Wine Installation', size_hint_y=None, height=60)
        check_btn.bind(on_press=self.check_wine)
        layout.add_widget(check_btn)
        
        self.add_widget(layout)
        
        Clock.schedule_once(lambda dt: self.update_info(), 0.1)
    
    def update_info(self):
        info = self.platform.get_system_info()
        text = f"Platform: {info.get('platform', 'Unknown')}\n"
        text += f"Architecture: {info.get('architecture', 'Unknown')}\n"
        
        if 'android_version' in info:
            text += f"Android: {info['android_version']}\n"
        
        text += "\n"
        
        wine_version = self.wine_manager.get_wine_version()
        if wine_version:
            text += f"Wine: {wine_version}\n"
            if self.wine_manager.wine_path:
                text += f"Wine Path: {self.wine_manager.wine_path}\n"
        else:
            text += "Wine: Not installed\n"
        
        text += f"\nPrefixes:\n{self.platform.get_default_prefix_location()}\n"
        text += f"\nConfig:\n{self.config.config_path}"
        
        self.info_label.text = text
    
    def check_wine(self, instance):
        is_installed = self.wine_manager.verify_wine_installation()
        if is_installed:
            wine_version = self.wine_manager.get_wine_version()
            msg = "✓ Wine is installed\n\n"
            if wine_version:
                msg += f"Version: {wine_version}\n"
            if self.wine_manager.wine_path:
                msg += f"Path: {self.wine_manager.wine_path}"
            self.show_message('Wine Check', msg)
        else:
            self.show_message(
                'Wine Not Found',
                'Wine is not installed.\n\nInstall Wine in Termux with:\npkg install wine'
            )
    
    def show_message(self, title, message):
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        content.add_widget(Label(text=message, size_hint_y=0.7))
        
        btn = StyledButton(text='OK', size_hint_y=0.3)
        btn.bind(on_press=lambda x: popup.dismiss())
        content.add_widget(btn)
        
        popup = Popup(title=title, content=content, size_hint=(0.9, 0.5))
        popup.open()


class LibraryScreen(Screen):
    def __init__(self, app_library, **kwargs):
        super().__init__(**kwargs)
        self.app_library = app_library
        
        layout = BoxLayout(orientation='vertical', padding=15, spacing=10)
        
        title = Label(
            text='Application Library',
            size_hint_y=None,
            height=50,
            font_size=24,
            bold=True
        )
        layout.add_widget(title)
        
        scroll = ScrollView()
        self.apps_list = GridLayout(cols=1, spacing=5, size_hint_y=None)
        self.apps_list.bind(minimum_height=self.apps_list.setter('height'))
        scroll.add_widget(self.apps_list)
        layout.add_widget(scroll)
        
        button_layout = BoxLayout(size_hint_y=None, height=60, spacing=5)
        
        refresh_btn = StyledButton(text='🔄 Refresh')
        refresh_btn.bind(on_press=self.refresh_library)
        button_layout.add_widget(refresh_btn)
        
        layout.add_widget(button_layout)
        self.add_widget(layout)
        
        Clock.schedule_once(lambda dt: self.refresh_library(None))
    
    def refresh_library(self, instance):
        self.apps_list.clear_widgets()
        apps = self.app_library.list_apps()
        
        if not apps:
            label = Label(text='No applications in library', size_hint_y=None, height=50)
            self.apps_list.add_widget(label)
            return
        
        for app in apps:
            btn = SecondaryButton(
                text=f"{app['name']} ({app['category']})",
                size_hint_y=None,
                height=60
            )
            self.apps_list.add_widget(btn)


class TemplatesScreen(Screen):
    def __init__(self, templates, wine_manager, **kwargs):
        super().__init__(**kwargs)
        self.templates = templates
        self.wine_manager = wine_manager
        
        layout = BoxLayout(orientation='vertical', padding=15, spacing=10)
        
        title = Label(
            text='Prefix Templates',
            size_hint_y=None,
            height=50,
            font_size=24,
            bold=True
        )
        layout.add_widget(title)
        
        scroll = ScrollView()
        self.template_list = GridLayout(cols=1, spacing=5, size_hint_y=None)
        self.template_list.bind(minimum_height=self.template_list.setter('height'))
        scroll.add_widget(self.template_list)
        layout.add_widget(scroll)
        
        button_layout = BoxLayout(size_hint_y=None, height=60, spacing=5)
        
        refresh_btn = StyledButton(text='🔄 Refresh')
        refresh_btn.bind(on_press=self.refresh_templates)
        button_layout.add_widget(refresh_btn)
        
        layout.add_widget(button_layout)
        self.add_widget(layout)
        
        Clock.schedule_once(lambda dt: self.refresh_templates(None))
    
    def refresh_templates(self, instance):
        self.template_list.clear_widgets()
        templates = self.templates.list_templates()
        
        if not templates:
            label = Label(text='No templates available', size_hint_y=None, height=50)
            self.template_list.add_widget(label)
            return
        
        for template in templates:
            btn = SecondaryButton(
                text=f"{template['name']} - {template['description']}",
                size_hint_y=None,
                height=80
            )
            self.template_list.add_widget(btn)


class WinetricksScreen(Screen):
    def __init__(self, winetricks, wine_manager, **kwargs):
        super().__init__(**kwargs)
        self.winetricks = winetricks
        self.wine_manager = wine_manager
        
        layout = BoxLayout(orientation='vertical', padding=15, spacing=10)
        
        title = Label(
            text='Winetricks Components',
            size_hint_y=None,
            height=50,
            font_size=24,
            bold=True
        )
        layout.add_widget(title)
        
        scroll = ScrollView()
        self.component_list = GridLayout(cols=1, spacing=5, size_hint_y=None)
        self.component_list.bind(minimum_height=self.component_list.setter('height'))
        scroll.add_widget(self.component_list)
        layout.add_widget(scroll)
        
        self.add_widget(layout)
        
        Clock.schedule_once(lambda dt: self.load_components())
    
    def load_components(self):
        self.component_list.clear_widgets()
        components = self.winetricks.list_common_components()
        
        for category, items in components.items():
            cat_label = Label(
                text=f'\n{category}',
                size_hint_y=None,
                height=40,
                bold=True
            )
            self.component_list.add_widget(cat_label)
            
            for item, desc in list(items.items())[:5]:
                btn = SecondaryButton(
                    text=f"{item} - {desc}",
                    size_hint_y=None,
                    height=60
                )
                self.component_list.add_widget(btn)


class WineVersionsScreen(Screen):
    def __init__(self, wine_versions, **kwargs):
        super().__init__(**kwargs)
        self.wine_versions = wine_versions
        
        layout = BoxLayout(orientation='vertical', padding=15, spacing=10)
        
        title = Label(
            text='Wine Versions',
            size_hint_y=None,
            height=50,
            font_size=24,
            bold=True
        )
        layout.add_widget(title)
        
        scroll = ScrollView()
        self.version_list = GridLayout(cols=1, spacing=5, size_hint_y=None)
        self.version_list.bind(minimum_height=self.version_list.setter('height'))
        scroll.add_widget(self.version_list)
        layout.add_widget(scroll)
        
        button_layout = BoxLayout(size_hint_y=None, height=60, spacing=5)
        
        refresh_btn = StyledButton(text='🔄 Refresh')
        refresh_btn.bind(on_press=self.refresh_versions)
        button_layout.add_widget(refresh_btn)
        
        layout.add_widget(button_layout)
        self.add_widget(layout)
        
        Clock.schedule_once(lambda dt: self.refresh_versions(None))
    
    def refresh_versions(self, instance):
        self.version_list.clear_widgets()
        versions = self.wine_versions.list_installed_versions()
        
        if not versions:
            label = Label(text='No Wine versions installed', size_hint_y=None, height=50)
            self.version_list.add_widget(label)
            return
        
        for version in versions:
            btn = SecondaryButton(
                text=f"{version.name} ({version.version_type})",
                size_hint_y=None,
                height=60
            )
            self.version_list.add_widget(btn)


class GameStoresScreen(Screen):
    def __init__(self, game_stores, app_library, **kwargs):
        super().__init__(**kwargs)
        self.game_stores = game_stores
        self.app_library = app_library
        
        layout = BoxLayout(orientation='vertical', padding=15, spacing=10)
        
        title = Label(
            text='Game Store Integration',
            size_hint_y=None,
            height=50,
            font_size=24,
            bold=True
        )
        layout.add_widget(title)
        
        steam_section = BoxLayout(orientation='vertical', size_hint_y=None, height=150, spacing=5)
        steam_label = Label(text='Steam Library', bold=True, size_hint_y=None, height=30)
        steam_section.add_widget(steam_label)
        
        self.steam_info = Label(text='Click scan to find games', size_hint_y=None, height=30)
        steam_section.add_widget(self.steam_info)
        
        steam_buttons = BoxLayout(size_hint_y=None, height=60, spacing=5)
        
        scan_steam = StyledButton(text='🔍 Scan')
        scan_steam.bind(on_press=self.scan_steam)
        steam_buttons.add_widget(scan_steam)
        
        import_steam = SecondaryButton(text='📥 Import')
        import_steam.bind(on_press=self.import_steam)
        steam_buttons.add_widget(import_steam)
        
        steam_section.add_widget(steam_buttons)
        layout.add_widget(steam_section)
        
        epic_section = BoxLayout(orientation='vertical', size_hint_y=None, height=150, spacing=5)
        epic_label = Label(text='Epic Games Library', bold=True, size_hint_y=None, height=30)
        epic_section.add_widget(epic_label)
        
        self.epic_info = Label(text='Click scan to find games', size_hint_y=None, height=30)
        epic_section.add_widget(self.epic_info)
        
        epic_buttons = BoxLayout(size_hint_y=None, height=60, spacing=5)
        
        scan_epic = StyledButton(text='🔍 Scan')
        scan_epic.bind(on_press=self.scan_epic)
        epic_buttons.add_widget(scan_epic)
        
        import_epic = SecondaryButton(text='📥 Import')
        import_epic.bind(on_press=self.import_epic)
        epic_buttons.add_widget(import_epic)
        
        epic_section.add_widget(epic_buttons)
        layout.add_widget(epic_section)
        
        layout.add_widget(Label())
        self.add_widget(layout)
    
    def scan_steam(self, instance):
        games = self.game_stores.scan_steam_library()
        self.steam_info.text = f"Found {len(games)} Steam games"
    
    def import_steam(self, instance):
        count = self.game_stores.auto_import_games('steam')
        self.steam_info.text = f"Imported {count} games to library"
    
    def scan_epic(self, instance):
        games = self.game_stores.scan_epic_library()
        self.epic_info.text = f"Found {len(games)} Epic games"
    
    def import_epic(self, instance):
        count = self.game_stores.auto_import_games('epic')
        self.epic_info.text = f"Imported {count} games to library"


class WinvoraApp(App):
    def build(self):
        self.wine_manager = WineManager()
        self.config = Config()
        self.platform = AndroidPlatform()
        self.winetricks = WineTricksManager(self.wine_manager)
        self.app_library = AppLibrary(self.config)
        self.dxvk = DXVKManager(self.wine_manager)
        self.templates = PrefixTemplateManager(self.config)
        self.wine_versions = WineVersionManager(self.config)
        self.game_stores = GameStoreIntegration(self.wine_manager, self.app_library)
        
        sm = ScreenManager()
        sm.add_widget(PrefixesScreen(self.wine_manager, name='prefixes'))
        sm.add_widget(ApplicationsScreen(self.wine_manager, name='apps'))
        sm.add_widget(LibraryScreen(self.app_library, name='library'))
        sm.add_widget(TemplatesScreen(self.templates, self.wine_manager, name='templates'))
        sm.add_widget(WinetricksScreen(self.winetricks, self.wine_manager, name='winetricks'))
        sm.add_widget(WineVersionsScreen(self.wine_versions, name='versions'))
        sm.add_widget(GameStoresScreen(self.game_stores, self.app_library, name='stores'))
        sm.add_widget(ProcessesScreen(self.wine_manager, name='processes'))
        sm.add_widget(SettingsScreen(
            self.wine_manager, self.platform, self.config, name='settings'
        ))
        
        root = BoxLayout(orientation='vertical')
        root.add_widget(sm)
        
        nav = BoxLayout(size_hint_y=None, height=70, spacing=2)
        
        nav_buttons = [
            ('🍷 Prefixes', 'prefixes'),
            ('📦 Apps', 'apps'),
            ('📚 Library', 'library'),
            ('📋 Templates', 'templates'),
            ('🧰 Tools', 'winetricks'),
            ('🍾 Versions', 'versions'),
            ('🎮 Stores', 'stores'),
            ('⚙️ Processes', 'processes'),
            ('🔧 Settings', 'settings')
        ]
        
        for text, screen_name in nav_buttons:
            btn = SecondaryButton(text=text)
            btn.bind(on_press=lambda x, s=screen_name: setattr(sm, 'current', s))
            nav.add_widget(btn)
        
        root.add_widget(nav)
        
        return root


def main():
    if not KIVY_AVAILABLE:
        print("Error: Kivy is required")
        print("Install: pip install kivy")
        return 1
    
    WinvoraApp().run()
    return 0


if __name__ == '__main__':
    sys.exit(main())
