"""
Desktop notification support for Winvora.
Provides cross-platform desktop notifications.
"""

from typing import Optional
from pathlib import Path
import platform
import subprocess


class NotificationManager:
    """Manages desktop notifications across platforms."""
    
    def __init__(self):
        self.platform = platform.system().lower()
        self.enabled = True
    
    def send_notification(self, title: str, message: str, 
                         urgency: str = "normal",
                         icon: Optional[str] = None) -> bool:
        """
        Send a desktop notification.
        
        Args:
            title: Notification title
            message: Notification message
            urgency: Urgency level (low, normal, critical)
            icon: Path to icon file (optional)
        
        Returns:
            True if notification was sent successfully
        """
        if not self.enabled:
            return False
        
        try:
            if self.platform == 'linux':
                return self._send_linux_notification(title, message, urgency, icon)
            elif self.platform == 'darwin':
                return self._send_macos_notification(title, message)
            else:
                return False
        except Exception:
            return False
    
    def _send_linux_notification(self, title: str, message: str, 
                                 urgency: str, icon: Optional[str]) -> bool:
        """Send notification on Linux using notify-send."""
        try:
            cmd = ['notify-send']
            cmd.extend(['-u', urgency])
            
            if icon and Path(icon).exists():
                cmd.extend(['-i', icon])
            else:
                cmd.extend(['-i', 'application-x-wine'])
            
            cmd.extend([title, message])
            
            subprocess.run(cmd, capture_output=True, timeout=5)
            return True
        except (subprocess.SubprocessError, FileNotFoundError):
            return False
    
    def _send_macos_notification(self, title: str, message: str) -> bool:
        """Send notification on macOS using osascript."""
        try:
            script = f'display notification "{message}" with title "{title}"'
            subprocess.run(['osascript', '-e', script], 
                         capture_output=True, timeout=5)
            return True
        except (subprocess.SubprocessError, FileNotFoundError):
            return False
    
    def notify_success(self, title: str, message: str):
        """Send a success notification."""
        self.send_notification(f"✅ {title}", message, urgency="normal")
    
    def notify_error(self, title: str, message: str):
        """Send an error notification."""
        self.send_notification(f"❌ {title}", message, urgency="critical")
    
    def notify_info(self, title: str, message: str):
        """Send an info notification."""
        self.send_notification(f"ℹ️ {title}", message, urgency="low")
    
    def notify_progress_complete(self, operation: str):
        """Notify when a long operation completes."""
        self.notify_success(
            "Winvora",
            f"{operation} completed successfully"
        )
    
    def set_enabled(self, enabled: bool):
        """Enable or disable notifications."""
        self.enabled = enabled


# Singleton instance
_notification_manager = None


def get_notification_manager() -> NotificationManager:
    """Get the global notification manager instance."""
    global _notification_manager
    if _notification_manager is None:
        _notification_manager = NotificationManager()
    return _notification_manager
