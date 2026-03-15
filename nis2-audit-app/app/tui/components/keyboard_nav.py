"""
Keyboard Navigation Enhancement - Loop 6
Tab order management, focus indicators, and shortcut hints.
"""
from textual.widgets import Button, Input, Select, Static
from textual.containers import Container, Horizontal
from textual.reactive import reactive
from textual.binding import Binding
from typing import List, Optional, Dict, Any


class ShortcutHint(Static):
    """Keyboard shortcut hint badge."""
    
    DEFAULT_CSS = """
    ShortcutHint {
        background: $surface-darken-2;
        color: $text-muted;
        padding: 0 1;
        text-style: bold;
    }
    """
    
    def __init__(self, shortcut: str, **kwargs):
        super().__init__(f"[{shortcut}]", **kwargs)


class NavigableButton(Button):
    """Button with enhanced keyboard navigation."""
    
    DEFAULT_CSS = """
    NavigableButton {
        border: solid $primary;
    }
    
    NavigableButton:focus {
        border: double $primary-lighten-2;
        background: $primary-darken-2;
    }
    
    NavigableButton:focus .shortcut-hint {
        color: $primary-lighten-2;
    }
    """
    
    def __init__(self, label: str, shortcut: str = "", **kwargs):
        # Add shortcut to label
        display_label = f"{label} [{shortcut}]" if shortcut else label
        super().__init__(display_label, **kwargs)
        self.shortcut = shortcut
        self.base_label = label
    
    def action_focus_next(self):
        """Focus next widget."""
        self.app.focus_next()
    
    def action_focus_previous(self):
        """Focus previous widget."""
        self.app.focus_previous()


class TabOrderManager:
    """Manages tab order for widgets."""
    
    def __init__(self, screen):
        self.screen = screen
        self.tab_order: List[str] = []  # Widget IDs in tab order
        self.current_index = 0
    
    def set_order(self, widget_ids: List[str]):
        """Set the tab order for widgets."""
        self.tab_order = widget_ids
        self.current_index = 0
    
    def focus_next(self):
        """Focus the next widget in tab order."""
        if not self.tab_order:
            return
        
        self.current_index = (self.current_index + 1) % len(self.tab_order)
        widget_id = self.tab_order[self.current_index]
        
        try:
            widget = self.screen.query_one(f"#{widget_id}")
            widget.focus()
        except Exception:
            pass
    
    def focus_previous(self):
        """Focus the previous widget in tab order."""
        if not self.tab_order:
            return
        
        self.current_index = (self.current_index - 1) % len(self.tab_order)
        widget_id = self.tab_order[self.current_index]
        
        try:
            widget = self.screen.query_one(f"#{widget_id}")
            widget.focus()
        except Exception:
            pass


class FocusIndicator(Static):
    """Visual indicator showing which element has focus."""
    
    DEFAULT_CSS = """
    FocusIndicator {
        width: 3;
        height: auto;
        color: $primary;
        text-align: center;
        visibility: hidden;
    }
    
    FocusIndicator.visible {
        visibility: visible;
    }
    """
    
    def show(self):
        """Show focus indicator."""
        self.update("▶")
        self.add_class("visible")
    
    def hide(self):
        """Hide focus indicator."""
        self.remove_class("visible")


class KeyboardNavigationHelp(Static):
    """Help panel showing available keyboard shortcuts."""
    
    DEFAULT_CSS = """
    KeyboardNavigationHelp {
        height: auto;
        border: solid $surface-lighten-1;
        background: $surface-darken-1;
        padding: 1;
    }
    
    #nav-help-title {
        text-style: bold;
        color: $primary;
        text-align: center;
        border-bottom: solid $surface-lighten-1;
        margin-bottom: 1;
    }
    
    .shortcut-row {
        height: auto;
        margin: 0 1;
    }
    
    .shortcut-key {
        width: 12;
        color: $warning;
        text-style: bold;
    }
    
    .shortcut-desc {
        color: $text;
    }
    """
    
    def __init__(self, shortcuts: Dict[str, str], **kwargs):
        super().__init__(**kwargs)
        self.shortcuts = shortcuts
    
    def compose(self):
        yield Static("⌨️  Keyboard Shortcuts", id="nav-help-title")
        
        for key, description in self.shortcuts.items():
            with Horizontal(classes="shortcut-row"):
                yield Static(key, classes="shortcut-key")
                yield Static(description, classes="shortcut-desc")


class ArrowKeyList(Container):
    """List navigable with arrow keys."""
    
    DEFAULT_CSS = """
    ArrowKeyList {
        height: auto;
        border: solid $surface-lighten-1;
    }
    
    ArrowKeyList:focus {
        border: double $primary;
    }
    """
    
    BINDINGS = [
        Binding("up", "navigate_up", "Previous", show=False),
        Binding("down", "navigate_down", "Next", show=False),
        Binding("home", "navigate_first", "First", show=False),
        Binding("end", "navigate_last", "Last", show=False),
        Binding("enter", "select_current", "Select", show=False),
    ]
    
    selected_index = reactive(0)
    
    def __init__(self, items: List[str] = None, **kwargs):
        super().__init__(**kwargs)
        self.items = items or []
        self._item_widgets: List[Static] = []
    
    def compose(self):
        for i, item in enumerate(self.items):
            item_widget = Static(item, classes="list-item")
            item_widget.data_index = i
            self._item_widgets.append(item_widget)
            yield item_widget
    
    def watch_selected_index(self, index: int):
        """Update visual selection."""
        for i, widget in enumerate(self._item_widgets):
            widget.remove_class("selected")
            if i == index:
                widget.add_class("selected")
    
    def action_navigate_up(self):
        """Move selection up."""
        if self.selected_index > 0:
            self.selected_index -= 1
    
    def action_navigate_down(self):
        """Move selection down."""
        if self.selected_index < len(self.items) - 1:
            self.selected_index += 1
    
    def action_navigate_first(self):
        """Jump to first item."""
        self.selected_index = 0
    
    def action_navigate_last(self):
        """Jump to last item."""
        self.selected_index = len(self.items) - 1
    
    def action_select_current(self):
        """Select current item."""
        self.post_message(self.ItemSelected(self.selected_index, self.items[self.selected_index]))
    
    class ItemSelected:
        """Message sent when item is selected."""
        def __init__(self, index: int, item: str):
            self.index = index
            self.item = item


class ShortcutBar(Horizontal):
    """Status bar showing global shortcuts."""
    
    DEFAULT_CSS = """
    ShortcutBar {
        height: 1;
        background: $surface-darken-2;
        color: $text-muted;
        padding: 0 1;
    }
    
    ShortcutBar:focus {
        background: $primary-darken-3;
    }
    """
    
    def __init__(self, shortcuts: Dict[str, str], **kwargs):
        super().__init__(**kwargs)
        self.shortcuts = shortcuts
    
    def compose(self):
        shortcut_texts = [f"{key}: {desc}" for key, desc in self.shortcuts.items()]
        yield Static("  |  ".join(shortcut_texts))


class AccessibleInput(Input):
    """Input with enhanced accessibility features."""
    
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
    
    AccessibleInput.valid {
        border: solid $success;
    }
    """
    
    def __init__(self, label: str = "", help_text: str = "", **kwargs):
        super().__init__(**kwargs)
        self.input_label = label
        self.help_text = help_text
    
    def on_focus(self):
        """Announce focus for accessibility."""
        # Could emit message for screen reader
        pass


class NavigableForm(Container):
    """Form container with managed tab order."""
    
    DEFAULT_CSS = """
    NavigableForm {
        height: auto;
    }
    """
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.tab_order: List[str] = []
        self.current_tab_index = 0
    
    def register_field(self, field_id: str):
        """Register a field in the tab order."""
        self.tab_order.append(field_id)
    
    def focus_next_field(self):
        """Focus the next field in tab order."""
        if not self.tab_order:
            return
        
        self.current_tab_index = (self.current_tab_index + 1) % len(self.tab_order)
        field_id = self.tab_order[self.current_tab_index]
        
        try:
            field = self.query_one(f"#{field_id}")
            field.focus()
        except Exception:
            pass
    
    def focus_previous_field(self):
        """Focus the previous field in tab order."""
        if not self.tab_order:
            return
        
        self.current_tab_index = (self.current_tab_index - 1) % len(self.tab_order)
        field_id = self.tab_order[self.current_tab_index]
        
        try:
            field = self.query_one(f"#{field_id}")
            field.focus()
        except Exception:
            pass


# Standard shortcut sets for common screens
DASHBOARD_SHORTCUTS = {
    "N": "New session",
    "R": "Refresh",
    "↑↓": "Navigate",
    "Enter": "Select",
    "?": "Help",
}

FORM_SHORTCUTS = {
    "Tab": "Next field",
    "Shift+Tab": "Previous field",
    "Ctrl+S": "Save draft",
    "Esc": "Cancel",
}

CHECKLIST_SHORTCUTS = {
    "Y": "Yes",
    "N": "No",
    "P": "Partial",
    "?": "N/A",
    "→/Space": "Next",
    "←": "Previous",
}

SCAN_SHORTCUTS = {
    "S": "Start scan",
    "C": "Cancel",
    "R": "Refresh results",
}


def get_shortcuts_for_screen(screen_name: str) -> Dict[str, str]:
    """Get standard shortcuts for a screen."""
    shortcuts = {
        "dashboard": DASHBOARD_SHORTCUTS,
        "new_session": FORM_SHORTCUTS,
        "checklist": CHECKLIST_SHORTCUTS,
        "scan": SCAN_SHORTCUTS,
    }
    return shortcuts.get(screen_name, {})
