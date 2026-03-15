"""
Enhanced Notification System - Loop 11
Toast notifications, notification center, and history.
"""
from textual.widgets import Static, Button
from textual.containers import Vertical, Horizontal, ScrollableContainer
from textual.reactive import reactive
from textual.timer import Timer
from textual.screen import ModalScreen
from datetime import datetime
from typing import List, Optional, Dict
from enum import Enum
from ...i18n import get_text as _


class NotificationSeverity(Enum):
    """Notification severity levels."""
    INFO = "info"
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"


class Toast(Static):
    """Toast notification popup."""
    
    DEFAULT_CSS = """
    Toast {
        width: 50;
        height: auto;
        padding: 1;
        border: solid;
        margin: 1 0;
        layer: notification;
    }
    
    Toast.info {
        border: solid $primary;
        background: $primary-darken-3;
    }
    
    Toast.success {
        border: solid $success;
        background: $success-darken-3;
    }
    
    Toast.warning {
        border: solid $warning;
        background: $warning-darken-3;
    }
    
    Toast.error {
        border: solid $error;
        background: $error-darken-3;
    }
    
    #toast-header {
        height: auto;
        margin-bottom: 1;
    }
    
    #toast-icon {
        width: 3;
        text-style: bold;
    }
    
    #toast-title {
        text-style: bold;
    }
    
    #toast-time {
        text-align: right;
        color: $text-muted;
    }
    
    #toast-message {
        height: auto;
        color: $text;
    }
    
    #toast-actions {
        height: auto;
        margin-top: 1;
        align: right middle;
    }
    """
    
    ICONS = {
        NotificationSeverity.INFO: "ℹ️",
        NotificationSeverity.SUCCESS: "✓",
        NotificationSeverity.WARNING: "⚠️",
        NotificationSeverity.ERROR: "✗",
    }
    
    def __init__(self,
                 message: str,
                 title: str = "",
                 severity: NotificationSeverity = NotificationSeverity.INFO,
                 actions: List[tuple] = None,
                 timeout: float = 5.0,
                 **kwargs):
        super().__init__(**kwargs)
        self.message = message
        default_titles = {
            NotificationSeverity.INFO: _("Info"),
            NotificationSeverity.SUCCESS: _("Succes"),
            NotificationSeverity.WARNING: _("Avertisment"),
            NotificationSeverity.ERROR: _("Eroare"),
        }
        self.title = title or default_titles.get(severity, severity.value.title())
        self.severity = severity
        self.actions = actions or []
        self.timeout = timeout
        self.timestamp = datetime.now()
        self._timer: Optional[Timer] = None
    
    def compose(self):
        self.add_class(self.severity.value)
        
        with Horizontal(id="toast-header"):
            yield Static(self.ICONS.get(self.severity, "ℹ️"), id="toast-icon")
            yield Static(self.title, id="toast-title")
            yield Static(self._format_time(), id="toast-time")
        
        yield Static(self.message, id="toast-message")
        
        if self.actions:
            with Horizontal(id="toast-actions"):
                for action_id, action_label in self.actions:
                    yield Button(action_label, id=f"action-{action_id}")
    
    def _format_time(self) -> str:
        """Format timestamp for display."""
        return self.timestamp.strftime("%H:%M")
    
    def on_mount(self):
        """Start auto-dismiss timer."""
        if self.timeout > 0:
            self._timer = self.set_timer(self.timeout, self.dismiss)
    
    def on_enter(self):
        """Pause auto-dismiss on hover."""
        if self._timer:
            self._timer.stop()
    
    def on_leave(self):
        """Resume auto-dismiss on leave."""
        if self.timeout > 0:
            self._timer = self.set_timer(self.timeout / 2, self.dismiss)
    
    def on_click(self):
        """Dismiss on click."""
        self.dismiss()
    
    def dismiss(self):
        """Remove the toast."""
        if self._timer:
            self._timer.stop()
        self.remove()
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for history."""
        return {
            "message": self.message,
            "title": self.title,
            "severity": self.severity.value,
            "timestamp": self.timestamp.isoformat(),
        }


class NotificationCenter(ModalScreen):
    """Modal showing notification history."""
    
    CSS = """
    #notification-center {
        width: 70;
        height: 80%;
        border: thick $primary;
        background: $surface;
        padding: 1;
    }
    
    #nc-header {
        height: auto;
        border-bottom: solid $primary;
        margin-bottom: 1;
        padding-bottom: 1;
    }
    
    #nc-title {
        text-style: bold;
        color: $primary;
    }
    
    #nc-clear {
        text-align: right;
    }
    
    #nc-list {
        height: 1fr;
        overflow: auto;
    }
    
    .notification-item {
        height: auto;
        border: solid $surface-lighten-1;
        background: $surface-darken-1;
        padding: 1;
        margin: 1 0;
    }
    
    .notification-item.info {
        border-left: solid $primary;
    }
    
    .notification-item.success {
        border-left: solid $success;
    }
    
    .notification-item.warning {
        border-left: solid $warning;
    }
    
    .notification-item.error {
        border-left: solid $error;
    }
    
    .nc-item-time {
        color: $text-muted;
        text-style: italic;
    }
    
    .nc-item-title {
        text-style: bold;
        margin: 1 0;
    }
    
    .nc-item-message {
        color: $text;
    }
    
    #nc-empty {
        text-align: center;
        color: $text-muted;
        text-style: italic;
        margin-top: 5;
    }
    
    #nc-footer {
        height: auto;
        border-top: solid $surface-lighten-1;
        margin-top: 1;
        padding-top: 1;
        align: center middle;
    }
    """
    
    BINDINGS = [
        ("escape", "dismiss", "Close"),
        ("c", "clear", "Clear All"),
    ]
    
    def __init__(self, notifications: List[Dict], **kwargs):
        super().__init__(**kwargs)
        self.notifications = notifications
    
    def compose(self):
        with Vertical(id="notification-center"):
            with Horizontal(id="nc-header"):
                yield Static(f"📬 {_("Centru de Notificări")}", id="nc-title")
                yield Button(_("Șterge Tot"), id="nc-clear")
            
            if self.notifications:
                with ScrollableContainer(id="nc-list"):
                    for notif in reversed(self.notifications):
                        with Vertical(classes=f"notification-item {notif['severity']}"):
                            try:
                                ts = datetime.fromisoformat(notif['timestamp']).strftime("%Y-%m-%d %H:%M")
                            except (ValueError, TypeError):
                                ts = _("Timp necunoscut")
                            yield Static(ts, classes="nc-item-time")
                            yield Static(notif['title'], classes="nc-item-title")
                            yield Static(notif['message'], classes="nc-item-message")
            else:
                yield Static(_("Încă nu există notificări"), id="nc-empty")
            
            with Horizontal(id="nc-footer"):
                yield Button(f"✓ {_("Închide")} (Esc)", variant="primary", id="btn-close")
    
    def on_button_pressed(self, event):
        """Handle button presses."""
        if event.button.id == "btn-close":
            self.dismiss()
        elif event.button.id == "nc-clear":
            self.dismiss("clear")
    
    def action_clear(self):
        """Clear all notifications."""
        self.dismiss("clear")


class NotificationManager:
    """Manager for application notifications."""
    
    def __init__(self, app, max_history: int = 100):
        self.app = app
        self.max_history = max_history
        self.history: List[Dict] = []
        self.active_toasts: List[Toast] = []
        self.unread_count = 0
    
    def notify(self,
               message: str,
               title: str = "",
               severity: str = "info",
               timeout: float = 5.0,
               actions: List[tuple] = None):
        """Show a notification toast."""
        # Map string severity to enum
        severity_map = {
            "info": NotificationSeverity.INFO,
            "success": NotificationSeverity.SUCCESS,
            "warning": NotificationSeverity.WARNING,
            "error": NotificationSeverity.ERROR,
        }
        sev = severity_map.get(severity, NotificationSeverity.INFO)
        
        # Create toast
        toast = Toast(
            message=message,
            title=title,
            severity=sev,
            actions=actions,
            timeout=timeout,
        )
        
        # Mount to notification area
        # Would typically mount to a container in the app
        # self.app.query_one("#notification-area").mount(toast)
        
        # Add to history
        self.history.append(toast.to_dict())
        if len(self.history) > self.max_history:
            self.history.pop(0)
        
        self.unread_count += 1
        self.active_toasts.append(toast)
        
        # Clean up closed toasts
        toast.watch("removed", lambda: self._on_toast_closed(toast))
    
    def _on_toast_closed(self, toast: Toast):
        """Handle toast closure."""
        if toast in self.active_toasts:
            self.active_toasts.remove(toast)
    
    def show_notification_center(self):
        """Show notification history modal."""
        center = NotificationCenter(self.history)
        self.unread_count = 0
        # self.app.push_screen(center, self._on_center_closed)
    
    def _on_center_closed(self, result):
        """Handle notification center close."""
        if result == "clear":
            self.clear_history()
    
    def clear_history(self):
        """Clear notification history."""
        self.history.clear()
        self.unread_count = 0
    
    def get_unread_count(self) -> int:
        """Get count of unread notifications."""
        return self.unread_count
    
    def success(self, message: str, title: str = "", timeout: float = 3.0):
        """Show success notification."""
        self.notify(message, title or _("Succes"), "success", timeout)
    
    def error(self, message: str, title: str = "", timeout: float = 8.0):
        """Show error notification."""
        self.notify(message, title or _("Eroare"), "error", timeout)
    
    def warning(self, message: str, title: str = "", timeout: float = 5.0):
        """Show warning notification."""
        self.notify(message, title or _("Avertisment"), "warning", timeout)
    
    def info(self, message: str, title: str = "", timeout: float = 4.0):
        """Show info notification."""
        self.notify(message, title or _("Info"), "info", timeout)


class NotificationBadge(Static):
    """Badge showing unread notification count."""
    
    DEFAULT_CSS = """
    NotificationBadge {
        width: auto;
        height: auto;
        background: $error;
        color: $text;
        text-style: bold;
        padding: 0 1;
        text-align: center;
    }
    
    NotificationBadge:zero {
        display: none;
    }
    """
    
    count = reactive(0)
    
    def watch_count(self, value: int):
        """Update display."""
        if value == 0:
            self.add_class("zero")
            self.update("")
        else:
            self.remove_class("zero")
            self.update(str(value) if value < 100 else "99+")


class PersistentNotification(Static):
    """Notification that persists until dismissed."""
    
    DEFAULT_CSS = """
    PersistentNotification {
        width: 100%;
        height: auto;
        border: solid $warning;
        background: $warning-darken-3;
        padding: 1;
        margin: 1 0;
    }
    
    #pn-icon {
        width: 3;
        text-style: bold;
    }
    
    #pn-content {
        height: auto;
    }
    
    #pn-dismiss {
        width: auto;
    }
    """
    
    def __init__(self, message: str, icon: str = "⚠️", **kwargs):
        super().__init__(**kwargs)
        self.message = message
        self.icon = icon
    
    def compose(self):
        with Horizontal():
            yield Static(self.icon, id="pn-icon")
            yield Static(self.message, id="pn-content")
            yield Button("✓", id="pn-dismiss")
    
    def on_button_pressed(self, event):
        """Dismiss notification."""
        if event.button.id == "pn-dismiss":
            self.remove()


# Quick notification helpers

def notify_success(app, message: str, title: str = ""):
    """Quick success notification."""
    app.notify(message, title=title or _("Succes"), severity="success")


def notify_error(app, message: str, title: str = ""):
    """Quick error notification."""
    app.notify(message, title=title or _("Eroare"), severity="error")


def notify_warning(app, message: str, title: str = ""):
    """Quick warning notification."""
    app.notify(message, title=title or _("Avertisment"), severity="warning")


def notify_info(app, message: str, title: str = ""):
    """Quick info notification."""
    app.notify(message, title=title or _("Info"), severity="information")
