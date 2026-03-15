"""
Accessibility Enhancements - Loop 13
Screen reader support, high contrast, and keyboard navigation.
"""
from textual.widgets import Static, Button, Input
from textual.containers import Container, Horizontal, Vertical
from textual.reactive import reactive

from typing import Optional, List, Callable


class ScreenReaderAnnouncer:
    """Announcer for screen reader messages."""
    
    def __init__(self, app):
        self.app = app
        self.message_queue: List[str] = []
        self._announcement_delay = 0.1
    
    def announce(self, message: str, priority: str = "polite"):
        """
        Announce a message to screen readers.
        
        priority: "polite" (wait for current speech) or "assertive" (interrupt)
        """
        # In a real implementation, this would update an ARIA live region
        # For now, we can log or store the announcement
        self.message_queue.append(message)
        
        # In a screen reader environment, this would trigger:
        # - ARIA live region update
        # - Or direct screen reader API call
    
    def announce_page_change(self, page_name: str):
        """Announce navigation to a new page."""
        self.announce(f"Navigated to {page_name}", "assertive")
    
    def announce_form_error(self, field_name: str, error: str):
        """Announce form validation error."""
        self.announce(f"Error in {field_name}: {error}", "assertive")
    
    def announce_success(self, message: str):
        """Announce success message."""
        self.announce(f"Success: {message}", "polite")
    
    def announce_progress(self, current: int, total: int, description: str):
        """Announce progress update."""
        percentage = int((current / total) * 100) if total > 0 else 0
        self.announce(f"{description}: {percentage} percent complete", "polite")


class AccessibleButton(Button):
    """Button with enhanced accessibility."""
    
    DEFAULT_CSS = """
    AccessibleButton:focus {
        border: double $primary;
        background: $primary-darken-2;
    }
    """
    
    def __init__(self, label: str, aria_label: str = "", help_text: str = "", **kwargs):
        super().__init__(label, **kwargs)
        self.aria_label = aria_label or label
        self.help_text = help_text
    
    def on_focus(self):
        """Announce focus for screen readers."""
        # Would announce via screen reader
        pass


class AccessibleInput(Input):
    """Input with accessibility enhancements."""
    
    DEFAULT_CSS = """
    AccessibleInput {
        border: solid $surface-lighten-1;
    }
    
    AccessibleInput:focus {
        border: double $primary;
        background: $primary-darken-3;
    }
    
    AccessibleInput.invalid {
        border: solid $error;
    }
    """
    
    def __init__(self, 
                 label: str = "",
                 aria_describedby: str = "",
                 required: bool = False,
                 **kwargs):
        super().__init__(**kwargs)
        self.input_label = label
        self.aria_describedby = aria_describedby
        self.required = required
        self.error_message: Optional[str] = None
    
    def on_focus(self):
        """Announce field focus."""
        message = self.input_label or "Input field"
        if self.required:
            message += ", required"
        if self.help_text:
            message += f". {self.help_text}"
    
    def set_error(self, message: str):
        """Set error state and announce."""
        self.error_message = message
        self.add_class("invalid")
        # Would announce error
    
    def clear_error(self):
        """Clear error state."""
        self.error_message = None
        self.remove_class("invalid")


class HighContrastMode:
    """High contrast mode manager."""
    
    HIGH_CONTRAST_CSS = """
    Screen {
        background: black;
        color: white;
    }
    
    Button {
        background: black;
        color: white;
        border: solid white;
    }
    
    Button:focus {
        background: white;
        color: black;
        border: double yellow;
    }
    
    Input {
        background: black;
        color: white;
        border: solid white;
    }
    
    Input:focus {
        border: double yellow;
    }
    
    Static {
        color: white;
    }
    
    .error {
        color: yellow;
        text-style: bold underline;
    }
    
    .success {
        color: cyan;
        text-style: bold;
    }
    
    .warning {
        color: yellow;
        text-style: bold;
    }
    """
    
    def __init__(self, app):
        self.app = app
        self.enabled = False
    
    def enable(self):
        """Enable high contrast mode."""
        self.enabled = True
        # Would apply high contrast CSS
    
    def disable(self):
        """Disable high contrast mode."""
        self.enabled = False
        # Would restore normal CSS
    
    def toggle(self):
        """Toggle high contrast mode."""
        if self.enabled:
            self.disable()
        else:
            self.enable()


class FocusVisibleManager:
    """Manages visible focus indicators."""
    
    def __init__(self):
        self.focus_ring_enabled = True
        self.focus_color = "yellow"
    
    def get_focus_css(self) -> str:
        """Get CSS for visible focus indicators."""
        return """
        *:focus {
            outline: solid yellow;
            outline-offset: 1;
        }
        
        Button:focus {
            border: double yellow;
            background: $surface-lighten-2;
        }
        
        Input:focus {
            border: double yellow;
        }
        
        Select:focus {
            border: double yellow;
        }
        """


class SkipLink(Static):
    """Skip link for keyboard navigation."""
    
    DEFAULT_CSS = """
    SkipLink {
        position: absolute;
        top: -100;
        left: 0;
        background: $primary;
        color: $text;
        padding: 1 2;
        text-style: bold;
    }
    
    SkipLink:focus {
        top: 0;
    }
    """
    
    def __init__(self, target_id: str, **kwargs):
        super().__init__("Skip to main content", **kwargs)
        self.target_id = target_id
    
    def on_click(self):
        """Skip to target."""
        try:
            target = self.app.query_one(f"#{self.target_id}")
            target.focus()
        except Exception:
            pass


class AriaLiveRegion(Static):
    """ARIA live region for screen reader announcements."""
    
    DEFAULT_CSS = """
    AriaLiveRegion {
        position: absolute;
        left: -10000;
        width: 1;
        height: 1;
        overflow: hidden;
    }
    """
    
    def __init__(self, mode: str = "polite", **kwargs):
        super().__init__(**kwargs)
        self.mode = mode  # "polite" or "assertive"
    
    def announce(self, message: str):
        """Announce message."""
        self.update(message)


class KeyboardShortcutHelp(Static):
    """Display keyboard shortcuts for accessibility."""
    
    DEFAULT_CSS = """
    KeyboardShortcutHelp {
        height: auto;
        border: solid $surface-lighten-1;
        background: $surface-darken-1;
        padding: 1;
        margin: 1 0;
    }
    
    #ksh-title {
        text-style: bold;
        color: $primary;
        text-align: center;
        margin-bottom: 1;
    }
    
    .shortcut-item {
        height: auto;
        margin: 0 1;
    }
    
    .shortcut-key {
        width: 15;
        color: $warning;
        text-style: bold;
    }
    """
    
    def __init__(self, shortcuts: List[tuple], **kwargs):
        super().__init__(**kwargs)
        self.shortcuts = shortcuts
    
    def compose(self):
        yield Static("⌨️ Keyboard Shortcuts", id="ksh-title")
        
        for key, description in self.shortcuts:
            with Horizontal(classes="shortcut-item"):
                yield Static(key, classes="shortcut-key")
                yield Static(description)


class AccessibilitySettings(Vertical):
    """Settings for accessibility features."""
    
    DEFAULT_CSS = """
    AccessibilitySettings {
        height: auto;
        padding: 1;
    }
    
    #as-title {
        text-style: bold;
        color: $primary;
        margin-bottom: 1;
    }
    
    .setting-row {
        height: auto;
        margin: 1 0;
        align: left middle;
    }
    
    .setting-label {
        width: 30;
    }
    """
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.high_contrast = False
        self.large_text = False
        self.reduce_motion = False
        self.screen_reader_mode = False
    
    def compose(self):
        yield Static("♿ Accessibility Settings", id="as-title")
        
        with Horizontal(classes="setting-row"):
            yield Static("High Contrast Mode:", classes="setting-label")
            yield Button("Enable" if not self.high_contrast else "Disable", id="toggle-contrast")
        
        with Horizontal(classes="setting-row"):
            yield Static("Reduce Motion:", classes="setting-label")
            yield Button("Enable" if not self.reduce_motion else "Disable", id="toggle-motion")
        
        with Horizontal(classes="setting-row"):
            yield Static("Screen Reader Mode:", classes="setting-label")
            yield Button("Enable" if not self.screen_reader_mode else "Disable", id="toggle-reader")
    
    def on_button_pressed(self, event):
        """Handle button presses."""
        if event.button.id == "toggle-contrast":
            self.high_contrast = not self.high_contrast
            # Apply high contrast
        elif event.button.id == "toggle-motion":
            self.reduce_motion = not self.reduce_motion
            # Disable animations
        elif event.button.id == "toggle-reader":
            self.screen_reader_mode = not self.screen_reader_mode
            # Enable screen reader optimizations


class AccessibleProgressBar(Static):
    """Progress bar with accessibility features."""
    
    DEFAULT_CSS = """
    AccessibleProgressBar {
        height: auto;
        margin: 1 0;
    }
    
    #apb-label {
        margin-bottom: 1;
    }
    
    #apb-bar {
        height: 1;
        background: $surface-darken-1;
    }
    
    #apb-fill {
        height: 100%;
        background: $primary;
    }
    
    #apb-text {
        text-align: center;
        margin-top: 1;
    }
    """
    
    progress = reactive(0)
    
    def __init__(self, label: str = "Progress", **kwargs):
        super().__init__(**kwargs)
        self.label = label
        self.aria_valuemin = 0
        self.aria_valuemax = 100
        self.aria_valuenow = 0
        self.aria_valuetext = ""
    
    def compose(self):
        yield Static(self.label, id="apb-label")
        with Static("", id="apb-bar"):
            yield Static("", id="apb-fill")
        yield Static("0%", id="apb-text")
    
    def watch_progress(self, value: int):
        """Update progress display."""
        try:
            fill = self.query_one("#apb-fill", Static)
            text = self.query_one("#apb-text", Static)
            
            bar_width = 30
            filled = int(value / 100 * bar_width)
            fill.styles.width = f"{value}%"
            
            bar_text = "█" * filled + "░" * (bar_width - filled)
            text.update(f"[{bar_text}] {value}%")
            
            # Update ARIA values
            self.aria_valuenow = value
            self.aria_valuetext = f"{value} percent"
            
        except Exception:
            pass


class AccessibleAlert(Static):
    """Accessible alert message."""
    
    DEFAULT_CSS = """
    AccessibleAlert {
        height: auto;
        padding: 1;
        margin: 1 0;
        border-left: thick;
    }
    
    AccessibleAlert.info {
        border-left-color: $primary;
        background: $primary-darken-3;
    }
    
    AccessibleAlert.success {
        border-left-color: $success;
        background: $success-darken-3;
    }
    
    AccessibleAlert.warning {
        border-left-color: $warning;
        background: $warning-darken-3;
    }
    
    AccessibleAlert.error {
        border-left-color: $error;
        background: $error-darken-3;
    }
    
    #alert-title {
        text-style: bold;
        margin-bottom: 1;
    }
    
    #alert-message {
        height: auto;
    }
    """
    
    def __init__(self, title: str, message: str, level: str = "info", **kwargs):
        super().__init__(**kwargs)
        self.alert_title = title
        self.alert_message = message
        self.level = level
    
    def compose(self):
        self.add_class(self.level)
        yield Static(self.alert_title, id="alert-title")
        yield Static(self.alert_message, id="alert-message")
    
    def on_mount(self):
        """Announce to screen readers."""
        # Would announce via ARIA live region
        pass


# Accessibility utility functions

def generate_shortcut_help(screen_name: str) -> List[tuple]:
    """Generate keyboard shortcut help for a screen."""
    common_shortcuts = [
        ("Tab", "Move to next element"),
        ("Shift+Tab", "Move to previous element"),
        ("Enter/Space", "Activate button"),
        ("Escape", "Cancel/Close"),
        ("?", "Show help"),
    ]
    
    screen_shortcuts = {
        "dashboard": [
            ("N", "New session"),
            ("R", "Refresh"),
            ("↑↓", "Navigate list"),
        ],
        "wizard": [
            ("→/Tab", "Next step"),
            ("←", "Previous step"),
            ("Ctrl+S", "Save draft"),
        ],
        "checklist": [
            ("Y", "Answer Yes"),
            ("N", "Answer No"),
            ("P", "Answer Partial"),
            ("?", "Answer N/A"),
            ("→/Space", "Next question"),
            ("←", "Previous question"),
        ],
    }
    
    return common_shortcuts + screen_shortcuts.get(screen_name, [])


def validate_accessibility_labels(widget) -> List[str]:
    """Validate that widgets have proper accessibility labels."""
    issues = []
    
    # Check for missing labels
    if hasattr(widget, 'aria_label') and not widget.aria_label:
        issues.append(f"Widget {widget.id} missing aria-label")
    
    # Check for missing descriptions
    if hasattr(widget, 'aria_describedby') and not widget.aria_describedby:
        issues.append(f"Widget {widget.id} missing aria-describedby")
    
    return issues
