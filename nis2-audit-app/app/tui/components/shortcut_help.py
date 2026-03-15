"""
Keyboard Shortcut Help Overlay
Context-sensitive keyboard shortcut reference for users.
"""
from textual.widgets import Static, Button, Label, DataTable
from textual.containers import Vertical, Horizontal, Container
from textual.screen import ModalScreen
from textual.binding import Binding
from ...i18n import get_text as _


# Context-specific keyboard shortcuts
SHORTCUTS = {
    'global': {
        _('Navigation'): [
            ('Tab / Shift+Tab', _('Move between fields')),
            ('↑ / ↓', _('Navigate lists')),
            ('← / →', _('Move between options')),
            ('Enter / Space', _('Select or confirm')),
            ('Escape', _('Cancel or go back')),
        ],
        _('Help'): [
            ('F1', _('Show help for current screen')),
            ('?', _('Show/hide keyboard shortcuts')),
        ],
        _('Actions'): [
            ('Ctrl+S', _('Save current work')),
            ('Ctrl+Q', _('Quit application')),
        ],
    },
    'dashboard': {
        _('Quick Actions'): [
            ('N', _('New audit session')),
            ('S', _('Scan network')),
            ('D', _('View devices')),
            ('R', _('View reports')),
            ('F', _('View findings')),
        ],
        _('Navigation'): [
            ('↑ / ↓', _('Select session')),
            ('Enter', _('Open selected session')),
            ('Delete', _('Delete selected session')),
        ],
    },
    'new_session': {
        _('Form'): [
            ('Tab', _('Next field')),
            ('Shift+Tab', _('Previous field')),
            ('Ctrl+Enter', _('Submit form')),
        ],
    },
    'scan': {
        _('Scanning'): [
            ('Enter', _('Start scan')),
            ('Space', _('Pause/Resume scan')),
            ('C', _('Cancel scan')),
        ],
    },
    'connect': {
        _('Connection'): [
            ('Enter', _('Connect to selected device')),
            ('R', _('Refresh device list')),
            ('C', _('Configure manually')),
        ],
    },
    'checklist': {
        _('Answering'): [
            ('Y', _('Mark as Yes/Compliant')),
            ('N', _('Mark as No/Non-compliant')),
            ('P', _('Mark as Partial')),
            ('?', _('Mark as Not Applicable')),
            ('Tab', _('Move to next question')),
            ('Shift+Tab', _('Move to previous question')),
        ],
        _('Navigation'): [
            ('Page Up', _('Previous section')),
            ('Page Down', _('Next section')),
        ],
    },
    'findings': {
        _('Findings'): [
            ('N', _('New finding')),
            ('E', _('Edit selected')),
            ('Delete', _('Delete selected')),
        ],
    },
    'report': {
        _('Report'): [
            ('G', _('Generate report')),
            ('E', _('Export to PDF')),
            ('S', _('Share report')),
        ],
    },
    'onboarding': {
        _('Wizard'): [
            ('→ / Space', _('Next step')),
            ('←', _('Previous step')),
            ('Esc', _('Skip tutorial')),
        ],
    },
}


class ShortcutHelpScreen(ModalScreen):
    """
    Modal screen showing keyboard shortcuts.
    Context-sensitive based on current screen.
    """
    
    # Allow dismissal with multiple methods
    BINDINGS = [
        Binding("escape", "dismiss", _("Close")),
        Binding("q", "dismiss", _("Close")),
    ]
    
    CSS = """
    #shortcut-overlay {
        width: 70;
        height: auto;
        max-height: 40;
        border: thick $primary;
        background: $surface;
        padding: 1 2;
    }
    
    #overlay-title {
        text-align: center;
        text-style: bold;
        color: $primary;
        margin-bottom: 1;
    }
    
    #context-label {
        text-align: center;
        color: $text-muted;
        margin-bottom: 1;
    }
    
    #shortcuts-container {
        height: 1fr;
        overflow-y: auto;
    }
    
    .shortcut-category {
        margin-top: 1;
        margin-bottom: 0;
        text-style: bold underline;
        color: $warning;
    }
    
    .shortcut-row {
        height: auto;
        margin: 0;
    }
    
    .shortcut-key {
        width: 20;
        color: $success;
        text-style: bold;
    }
    
    .shortcut-desc {
        width: auto;
        color: $text;
    }
    
    #close-btn {
        margin-top: 1;
        align: center middle;
    }
    
    #tip-footer {
        text-align: center;
        color: $text-muted;
        text-style: italic;
        margin-top: 1;
    }
    """
    
    def __init__(self, context: str = 'global'):
        super().__init__()
        self.context = context
    
    def compose(self):
        with Vertical(id="shortcut-overlay"):
            yield Label(f"⌨️  {_('Keyboard Shortcuts')}", id="overlay-title")
            
            context_name = self.context.replace('_', ' ').title()
            yield Label(f"{_('Current')}: {context_name}", id="context-label")
            
            with Vertical(id="shortcuts-container"):
                # Always show global shortcuts first
                if 'global' in SHORTCUTS:
                    for category, shortcuts in SHORTCUTS['global'].items():
                        yield Label(f"📌 {category}", classes="shortcut-category")
                        for key, desc in shortcuts:
                            with Horizontal(classes="shortcut-row"):
                                yield Label(key, classes="shortcut-key")
                                yield Label(_(desc), classes="shortcut-desc")
                
                # Show context-specific shortcuts
                if self.context in SHORTCUTS and self.context != 'global':
                    yield Label("", classes="shortcut-category")  # Spacer
                    for category, shortcuts in SHORTCUTS[self.context].items():
                        yield Label(f"🎯 {category}", classes="shortcut-category")
                        for key, desc in shortcuts:
                            with Horizontal(classes="shortcut-row"):
                                yield Label(key, classes="shortcut-key")
                                yield Label(_(desc), classes="shortcut-desc")
            
            yield Button(f"✓ {_('Got it!')} ({_('Press')} Esc {_('or')} Q {_('to close')})", id="close-btn", variant="primary")
            
            yield Label(f"💡 {_('Press ? anytime to toggle this help overlay')}", id="tip-footer")
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Close the overlay."""
        self.dismiss()
    
    def action_dismiss(self) -> None:
        """Close the overlay (from key binding)."""
        self.dismiss()
    
    def on_key(self, event) -> None:
        """Close on ? key toggle."""
        if event.key == '?':
            self.dismiss()
