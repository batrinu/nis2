"""
Contextual Help System - Loop 3
Tooltip widget and context-aware help for non-technical users.
"""
from textual.widgets import Static
from textual.containers import Horizontal, Vertical
from textual.reactive import reactive

from typing import Optional, Dict, List
import random

from nis2_audit_app.app.i18n import get_text as _


# Contextual help database for different contexts
CONTEXTUAL_HELP_DB = {
    # Form fields
    "entity_name": {
        "tooltip": _("The legal name of the organization being audited"),
        "explanation": _("This should match the official business registration name."),
        "why": _("We need this to properly identify the entity in reports and legal documents."),
        "tips": [
            _("Use the full legal name, not abbreviations"),
            _("Include any suffix like 'SRL' or 'SA' if applicable"),
            _("This will appear on official compliance reports"),
        ],
    },
    "sector": {
        "tooltip": _("The industry sector determines NIS2 classification"),
        "explanation": _("Different sectors have different obligations under NIS2."),
        "why": _("Sector is one of the primary factors for determining if you're an Essential or Important Entity."),
        "tips": [
            _("Energy, Transport, Banking = usually Essential Entity"),
            _("Manufacturing, Digital = usually Important Entity"),
            _("When in doubt, choose the closest match"),
        ],
    },
    "employees": {
        "tooltip": _("Total number of employees (full-time equivalent)"),
        "explanation": _("Employee count helps determine entity size classification."),
        "why": _("NIS2 thresholds: Large = 250+ employees OR €50M+ turnover."),
        "tips": [
            _("Count full-time equivalents"),
            _("Include all subsidiaries if auditing a group"),
            _("€50M+ turnover can also qualify as large"),
        ],
    },
    "network_range": {
        "tooltip": _("IP range to scan (e.g., 192.168.1.0/24)"),
        "explanation": _("We'll scan this network range to discover devices."),
        "why": _("Automatic discovery saves time and ensures nothing is missed."),
        "tips": [
            _("/24 = 254 addresses (common for small networks)"),
            _("Start small - scan one subnet at a time"),
            _("Ensure you have permission to scan"),
        ],
    },
    # Screen contexts
    "dashboard": {
        "tooltip": _("Your audit command center"),
        "explanation": _("Manage all your audit sessions from here."),
        "why": _("Centralized view helps you track progress across multiple audits."),
        "tips": [
            _("Press 'N' for a new session"),
            _("Sessions auto-save every 30 seconds"),
            _("Click any session to continue where you left off"),
        ],
    },
    "scan": {
        "tooltip": _("Network device discovery"),
        "explanation": _("Scan your network to automatically inventory devices."),
        "why": _("Knowing what devices you have is the first step to securing them."),
        "tips": [
            _("Scans typically take 1-5 minutes"),
            _("Some devices may not respond to ping"),
            _("Found devices appear in real-time"),
        ],
    },
    "checklist": {
        "tooltip": _("NIS2 compliance assessment"),
        "explanation": _("Answer questions about your cybersecurity measures."),
        "why": _("This determines your compliance score and identifies gaps."),
        "tips": [
            _("Use Y/N/P/? keys for quick answers"),
            _("Hover over terms for definitions"),
            _("Your progress auto-saves"),
        ],
    },
    "findings": {
        "tooltip": _("Security issues found during audit"),
        "explanation": _("Review and track remediation of security gaps."),
        "why": _("Fixing findings is essential for NIS2 compliance."),
        "tips": [
            _("Start with Critical and High severity"),
            _("Click 'How to Fix' for guidance"),
            _("Mark resolved when fixed"),
        ],
    },
}

# Rotating quick tips
QUICK_TIPS = [
    _("💡 Tip: Press '?' anytime for help on the current screen"),
    _("💡 Tip: Your work auto-saves every 30 seconds"),
    _("💡 Tip: Use Tab to move between fields quickly"),
    _("💡 Tip: Hover over labels to see what they mean"),
    _("💡 Tip: Start with Critical findings first"),
    _("💡 Tip: NIS2 requires incident reporting within 24-72 hours"),
    _("💡 Tip: Document everything - auditors love paper trails"),
    _("💡 Tip: Regular backups are required by Article 21"),
    _("💡 Tip: MFA is mandatory for all admin accounts"),
    _("💡 Tip: Encryption protects data in transit AND at rest"),
]


class Tooltip(Static):
    """Tooltip that appears on hover/focus."""
    
    DEFAULT_CSS = """
    Tooltip {
        background: $surface-darken-2;
        color: $text;
        padding: 1;
        border: solid $primary;
        width: auto;
        height: auto;
        max-width: 50;
        display: none;
        layer: overlay;
    }
    """
    
    def __init__(self, text: str = "", **kwargs):
        super().__init__(text, **kwargs)
        self._hide_timer: Optional[Timer] = None
    
    def show(self, text: str, x: int = 0, y: int = 0):
        """Show tooltip with text at position."""
        self.update(text)
        self.styles.display = "block"
        self.styles.offset = (x, y)
        
        # Auto-hide after 5 seconds
        if self._hide_timer:
            self._hide_timer.stop()
        self._hide_timer = self.set_timer(5, self.hide)
    
    def hide(self):
        """Hide tooltip."""
        self.styles.display = "none"


class ContextualHelpPanel(Vertical):
    """Side panel showing context-aware help."""
    
    DEFAULT_CSS = """
    ContextualHelpPanel {
        width: 35;
        height: 100%;
        background: $surface-darken-1;
        border-left: solid $primary;
        padding: 1;
    }
    
    #help-header {
        text-style: bold;
        color: $primary;
        text-align: center;
        border-bottom: solid $primary;
        margin-bottom: 1;
        padding-bottom: 1;
    }
    
    #help-context {
        color: $success;
        text-style: bold;
        margin-bottom: 1;
    }
    
    #help-explanation {
        margin: 1 0;
        height: auto;
    }
    
    #help-why {
        color: $warning;
        text-style: italic;
        margin: 1 0;
        height: auto;
    }
    
    #help-tips {
        margin-top: 1;
        border-top: solid $surface-lighten-1;
        padding-top: 1;
    }
    
    .tip-item {
        color: $text-muted;
        margin-left: 1;
        height: auto;
    }
    
    #quick-tip {
        margin-top: 1;
        padding-top: 1;
        border-top: dashed $surface-lighten-1;
        color: $primary-lighten-2;
        text-style: italic;
        text-align: center;
        height: auto;
    }
    """
    
    current_context = reactive("")
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._tip_rotation_timer: Optional[Timer] = None
    
    def compose(self):
        yield Static(_("📖 Contextual Help"), id="help-header")
        yield Static("", id="help-context")
        yield Static("", id="help-explanation")
        yield Static("", id="help-why")
        yield Static("", id="help-tips")
        yield Static("", id="quick-tip")
    
    def on_mount(self):
        """Start tip rotation."""
        self._tip_rotation_timer = self.set_interval(10, self._rotate_tip)
        self._rotate_tip()
    
    def watch_current_context(self, context: str):
        """Update help content when context changes."""
        self._update_help(context)
    
    def _update_help(self, context: str):
        """Update help panel with context info."""
        help_data = CONTEXTUAL_HELP_DB.get(context, {
            "tooltip": _("Hover over elements for help"),
            "explanation": _("Select a field or element to see detailed help here."),
            "why": _("Contextual help adapts to what you're doing."),
            "tips": [_("Try clicking on different elements")],
        })
        
        try:
            self.query_one("#help-context", Static).update(f"▶ {context.replace('_', ' ').title()}")
            self.query_one("#help-explanation", Static).update(help_data.get("explanation", ""))
            self.query_one("#help-why", Static).update(_("❓ Why: {why}").format(why=help_data.get('why', '')))
            
            tips = help_data.get("tips", [])
            tips_text = _("💡 Quick Tips:\n") + "\n".join(f"  • {tip}" for tip in tips)
            self.query_one("#help-tips", Static).update(tips_text)
        except Exception:
            pass
    
    def _rotate_tip(self):
        """Rotate to a new quick tip."""
        try:
            tip = random.choice(QUICK_TIPS)
            self.query_one("#quick-tip", Static).update(tip)
        except Exception:
            pass
    
    def set_context(self, context: str):
        """Set the current help context."""
        self.current_context = context


class HelpfulLabel(Static):
    """Label with built-in contextual help on hover."""
    
    DEFAULT_CSS = """
    HelpfulLabel {
        height: auto;
        padding: 0 1;
    }
    
    HelpfulLabel:hover {
        background: $primary-darken-2;
    }
    
    HelpfulLabel:focus {
        background: $primary-darken-2;
    }
    """
    
    def __init__(self, text: str, help_context: str = "", **kwargs):
        super().__init__(text, **kwargs)
        self.help_context = help_context
        self.tooltip_text = ""
        
        # Get tooltip from database
        if help_context in CONTEXTUAL_HELP_DB:
            self.tooltip_text = CONTEXTUAL_HELP_DB[help_context].get("tooltip", "")
    
    def on_enter(self):
        """Show tooltip on hover."""
        if self.tooltip_text:
            # Notify parent to show tooltip
            self.post_message(self.TooltipRequest(self, self.tooltip_text))
        
        # Update contextual help panel
        if self.help_context:
            self.post_message(self.ContextRequest(self.help_context))
    
    def on_leave(self):
        """Hide tooltip on leave."""
        self.post_message(self.TooltipHide(self))
    
    class TooltipRequest:
        """Message to request tooltip display."""
        def __init__(self, sender, text: str):
            self.sender = sender
            self.text = text
    
    class TooltipHide:
        """Message to hide tooltip."""
        def __init__(self, sender):
            self.sender = sender
    
    class ContextRequest:
        """Message to request context change."""
        def __init__(self, context: str):
            self.context = context


class WhyAmISeeingThis(Static):
    """Expandable 'Why am I seeing this?' explanation."""
    
    DEFAULT_CSS = """
    WhyAmISeeingThis {
        height: auto;
        margin: 1 0;
    }
    
    #why-header {
        color: $primary;
        text-style: underline;
        cursor: pointer;
    }
    
    #why-header:hover {
        color: $primary-lighten-2;
    }
    
    #why-content {
        display: none;
        color: $text-muted;
        text-style: italic;
        margin: 1 0 1 2;
        height: auto;
    }
    
    WhyAmISeeingThis.expanded #why-content {
        display: block;
    }
    """
    
    def __init__(self, explanation: str, **kwargs):
        super().__init__(**kwargs)
        self.explanation = explanation
    
    def compose(self):
        yield Static(_("🤔 Why am I seeing this? (click)"), id="why-header")
        yield Static(self.explanation, id="why-content")
    
    def on_click(self):
        """Toggle expansion."""
        self.toggle_class("expanded")


class SmartTooltipManager:
    """Manager for tooltips across the application."""
    
    def __init__(self, app):
        self.app = app
        self.tooltip = None
    
    def setup(self):
        """Setup tooltip overlay."""
        # Create tooltip widget (would be mounted to app)
        self.tooltip = Tooltip()
        # self.app.mount(self.tooltip)  # Would be called in app setup
    
    def show(self, text: str, x: int = 0, y: int = 0):
        """Show tooltip."""
        if self.tooltip:
            self.tooltip.show(text, x, y)
    
    def hide(self):
        """Hide tooltip."""
        if self.tooltip:
            self.tooltip.hide()


def get_help_for_field(field_name: str) -> Dict:
    """Get help information for a field."""
    return CONTEXTUAL_HELP_DB.get(field_name, {
        "tooltip": "",
        "explanation": "",
        "why": "",
        "tips": [],
    })


def format_help_tip(tip: str, max_width: int = 50) -> str:
    """Format a help tip for display."""
    if len(tip) <= max_width:
        return tip
    
    # Simple word wrap
    words = tip.split()
    lines = []
    current_line = ""
    
    for word in words:
        if len(current_line) + len(word) + 1 <= max_width:
            current_line += " " + word if current_line else word
        else:
            lines.append(current_line)
            current_line = word
    
    if current_line:
        lines.append(current_line)
    
    return "\n".join(lines)
