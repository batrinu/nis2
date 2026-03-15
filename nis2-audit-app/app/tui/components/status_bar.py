"""
Status Bar Components - Loop 18
Comprehensive status bar with system info and shortcuts.
"""
from textual.widgets import Static
from textual.containers import Horizontal
from textual.reactive import reactive
from datetime import datetime
from ...i18n import get_text as _


class StatusBar(Horizontal):
    """Main status bar with multiple sections."""
    
    DEFAULT_CSS = """
    StatusBar {
        height: 1;
        background: $surface-darken-2;
        color: $text;
        padding: 0 1;
    }
    
    StatusBar Section {
        width: auto;
        height: 1;
    }
    
    StatusBar #status-left {
        width: 1fr;
        content-align: left middle;
    }
    
    StatusBar #status-center {
        width: auto;
        content-align: center middle;
    }
    
    StatusBar #status-right {
        width: 1fr;
        content-align: right middle;
    }
    """
    
    message = reactive("")
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._status_message = _("Ready")
    
    def compose(self):
        yield Static(_("Ready"), id="status-left")
        yield Static("", id="status-center")
        yield Static("", id="status-right")
    
    def watch_message(self, message: str):
        """Update status message."""
        try:
            left = self.query_one("#status-left", Static)
            left.update(message if message else self._status_message)
        except Exception:
            pass
    
    def set_status(self, message: str, timeout: float = 0):
        """Set temporary status message."""
        self.message = message
        
        if timeout > 0:
            self.set_timer(timeout, lambda: self._clear_status())
    
    def _clear_status(self):
        """Clear temporary status."""
        self.message = self._status_message


class ConnectionStatus(Static):
    """"""Indicator de stare conexiune."""
    
    DEFAULT_CSS = """
    ConnectionStatus {
        width: auto;
        height: auto;
    }
    
    ConnectionStatus.connected {
        color: $success;
    }
    
    ConnectionStatus.disconnected {
        color: $error;
    }
    
    ConnectionStatus.connecting {
        color: $warning;
    }
    """
    
    ICONS = {
        "connected": "●",
        "disconnected": "○",
        "connecting": "◐",
    }
    LABELS = {
        "connected": _("connected"),
        "disconnected": _("disconnected"),
        "connecting": _("connecting"),
    }
    
    def __init__(self, status: str = "disconnected", label: str = "", **kwargs):
        super().__init__(**kwargs)
        self.set_status(status)
        self.status_label = label
    
    def set_status(self, status: str):
        """Update connection status."""
        self.remove_class("connected", "disconnected", "connecting")
        self.add_class(status)
        
        icon = self.ICONS.get(status, "○")
        label_text = self.LABELS.get(status, status)
        label = f" {label_text}" if label_text else ""
        self.update(f"{icon}{label}")


class ProgressStatus(Static):
    """"""Indicator de progres pentru bara de stare."""
    
    DEFAULT_CSS = """
    ProgressStatus {
        width: auto;
        height: auto;
        color: $primary;
    }
    """
    
    progress = reactive(0)
    
    def watch_progress(self, value: int):
        """Update progress display."""
        filled = int(value / 100 * 10)
        bar = "█" * filled + "░" * (10 - filled)
        self.update(f"[{bar}] {value}%")


class Clock(Static):
    """"""Afisaj ceas pentru bara de stare."""
    
    DEFAULT_CSS = """
    Clock {
        width: auto;
        height: auto;
        color: $text-muted;
    }
    """
    
    def __init__(self, show_seconds: bool = False, **kwargs):
        super().__init__(**kwargs)
        self.show_seconds = show_seconds
    
    def on_mount(self):
        """Start clock."""
        self._update_time()
        self.set_interval(1 if self.show_seconds else 60, self._update_time)
    
    def _update_time(self):
        """Update time display."""
        now = datetime.now()
        if self.show_seconds:
            time_str = now.strftime("%H:%M:%S")
        else:
            time_str = now.strftime("%H:%M")
        self.update(f"🕐 {time_str}")


class ShortcutDisplay(Static):
    """"""Afisaj scurtaturi tastatura in bara de stare."""
    
    DEFAULT_CSS = """
    ShortcutDisplay {
        width: auto;
        height: auto;
        color: $text-muted;
    }
    """
    
    def __init__(self, shortcuts: Dict[str, str], **kwargs):
        super().__init__(**kwargs)
        self.shortcuts = shortcuts
    
    def compose(self):
        parts = [f"{key}={action}" for key, action in self.shortcuts.items()]
        self.update(" | ".join(parts))


class AutoSaveStatus(Static):
    """"""Indicator stare auto-salvare."""
    
    DEFAULT_CSS = """
    AutoSaveStatus {
        width: auto;
        height: auto;
    }
    
    AutoSaveStatus.saved {
        color: $success;
    }
    
    AutoSaveStatus.unsaved {
        color: $warning;
    }
    
    AutoSaveStatus.saving {
        color: $primary;
    }
    """
    
    ICONS = {
        "saved": "💾",
        "unsaved": "●",
        "saving": "⏳",
    }
    LABELS = {
        "saved": _("saved"),
        "unsaved": _("unsaved"),
        "saving": _("saving"),
    }
    
    def set_status(self, status: str):
        """Update auto-save status."""
        self.remove_class("saved", "unsaved", "saving")
        self.add_class(status)
        
        icon = self.ICONS.get(status, "")
        self.update(icon)


class SessionInfo(Static):
    """"""Afisaj informatii sesiune."""
    
    DEFAULT_CSS = """
    SessionInfo {
        width: auto;
        height: auto;
        color: $text-muted;
    }
    """
    
    def __init__(self, session_name: str = "", entity_name: str = "", **kwargs):
        super().__init__(**kwargs)
        self.session_name = session_name
        self.entity_name = entity_name
    
    def compose(self):
        if self.session_name:
            self.update(f"📋 {self.session_name}")
        elif self.entity_name:
            self.update(f"🏢 {self.entity_name}")
        else:
            self.update("")


class NotificationStatus(Static):
    """"""Indicator notificari in bara de stare."""
    
    DEFAULT_CSS = """
    NotificationStatus {
        width: auto;
        height: auto;
    }
    
    NotificationStatus.has-unread {
        color: $warning;
    }
    
    NotificationStatus.empty {
        color: $text-muted;
    }
    """
    
    unread_count = reactive(0)
    
    def watch_unread_count(self, count: int):
        """Update display."""
        if count > 0:
            self.remove_class("empty")
            self.add_class("has-unread")
            self.update(f"🔔 {count}")
        else:
            self.remove_class("has-unread")
            self.add_class("empty")
            self.update("🔔 0")


class SystemStatus(Static):
    """"""Indicator stare sistem."""
    
    DEFAULT_CSS = """
    SystemStatus {
        width: auto;
        height: auto;
        color: $text-muted;
    }
    
    SystemStatus.healthy {
        color: $success;
    }
    
    SystemStatus.warning {
        color: $warning;
    }
    
    SystemStatus.error {
        color: $error;
    }
    """
    
    def set_status(self, status: str, message: str = ""):
        """Update system status."""
        self.remove_class("healthy", "warning", "error")
        self.add_class(status)
        
        icons = {
            "healthy": "✓",
            "warning": "⚠️",
            "error": "✗",
        }
        labels = {
            "healthy": _("healthy"),
            "warning": _("warning"),
            "error": _("error"),
        }
        
        icon = icons.get(status, "?")
        status_text = message if message else labels.get(status, status)
        text = f" {status_text}" if status_text else ""
        self.update(f"{icon}{text}")


class ModeIndicator(Static):
    """"""Indicator mod curent."""
    
    DEFAULT_CSS = """
    ModeIndicator {
        width: auto;
        height: auto;
        background: $primary;
        color: $text;
        padding: 0 1;
    }
    """
    
    def __init__(self, mode: str = _("Normal"), **kwargs):
        super().__init__(**kwargs)
        self.mode = mode
    
    def compose(self):
        self.update(f"[{self.mode}]")
    
    def set_mode(self, mode: str):
        """"""Actualizeaza modul."""
        self.mode = mode
        self.update(f"[{mode}]")


# Status bar builders

def build_main_status_bar() -> StatusBar:
    """"""Construieste bara de stare principala a aplicatiei."""
    return StatusBar()


def build_dashboard_status_bar(session_name: str = "") -> StatusBar:
    """"""Construieste bara de stare pentru dashboard."""
    bar = StatusBar()
    # Would add specific dashboard elements
    return bar


def build_wizard_status_bar(step: int, total: int) -> StatusBar:
    """"""Construieste bara de stare pentru wizard."""
    bar = StatusBar()
    # Would add step indicator
    return bar
