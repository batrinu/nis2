"""
Form UX Enhancements - Loop 8
Inline validation, field help, smart defaults, and auto-save.
"""
from textual.widgets import Static, Input, Label, Button
from textual.containers import Horizontal, Vertical
from textual.reactive import reactive
from textual.timer import Timer
from typing import Optional, Callable, Any, Dict, List
import re


class SmartInput(Input):
    """Input with smart features for better UX."""
    
    DEFAULT_CSS = """
    SmartInput {
        border: solid $surface-lighten-1;
    }
    
    SmartInput:focus {
        border: solid $primary;
    }
    
    SmartInput.valid {
        border: solid $success;
    }
    
    SmartInput.invalid {
        border: solid $error;
    }
    
    SmartInput.warning {
        border: solid $warning;
    }
    """
    
    validation_state = reactive("")
    
    def __init__(self,
                 label: str = "",
                 help_text: str = "",
                 placeholder: str = "",
                 validators: List[tuple] = None,
                 formatter: Callable = None,
                 smart_default: Callable = None,
                 **kwargs):
        super().__init__(placeholder=placeholder, **kwargs)
        self.label = label
        self.help_text = help_text
        self.validators = validators or []
        self.formatter = formatter
        self.smart_default_fn = smart_default
        self._validation_timer: Optional[Timer] = None
    
    def on_mount(self):
        """Apply smart default if field is empty."""
        if not self.value and self.smart_default_fn:
            default_value = self.smart_default_fn()
            if default_value:
                self.value = default_value
                self.add_class("has-default")
    
    def watch_value(self, value: str):
        """Validate with debounce."""
        if self._validation_timer:
            self._validation_timer.stop()
        
        self._validation_timer = self.set_timer(0.5, lambda: self._do_validation(value))
        
        # Apply formatter if provided
        if self.formatter:
            formatted = self.formatter(value)
            if formatted != value:
                self.value = formatted
    
    def _do_validation(self, value: str):
        """Perform validation."""
        for validator_fn, level, message in self.validators:
            if not validator_fn(value):
                self.validation_state = level
                self.remove_class("valid", "invalid", "warning")
                self.add_class(level)
                self.post_message(self.ValidationResult(self, level, message))
                return
        
        self.validation_state = "valid"
        self.remove_class("invalid", "warning")
        self.add_class("valid")
        self.post_message(self.ValidationResult(self, "valid", "✓ Looks good"))
    
    class ValidationResult:
        """Message sent when validation completes."""
        def __init__(self, input_widget, level: str, message: str):
            self.input = input_widget
            self.level = level
            self.message = message


class FieldHelp(Static):
    """Help text for a form field."""
    
    DEFAULT_CSS = """
    FieldHelp {
        height: auto;
        margin: 0 0 1 0;
    }
    
    FieldHelp.info {
        color: $text-muted;
        text-style: italic;
    }
    
    FieldHelp.valid {
        color: $success;
    }
    
    FieldHelp.invalid {
        color: $error;
    }
    
    FieldHelp.warning {
        color: $warning;
    }
    
    #field-help-icon {
        width: 2;
    }
    
    #field-help-text {
        width: 1fr;
    }
    """
    
    ICONS = {
        "info": "ℹ️",
        "valid": "✓",
        "invalid": "✗",
        "warning": "⚠️",
    }
    
    def __init__(self, text: str = "", level: str = "info", **kwargs):
        super().__init__(**kwargs)
        self.help_text = text
        self.level = level
    
    def compose(self):
        self.add_class(self.level)
        yield Static(self.ICONS.get(self.level, ""), id="field-help-icon")
        yield Static(self.help_text, id="field-help-text")
    
    def update_help(self, text: str, level: str = "info"):
        """Update help text and level."""
        self.remove_class("info", "valid", "invalid", "warning")
        self.add_class(level)
        
        try:
            self.query_one("#field-help-icon", Static).update(self.ICONS.get(level, ""))
            self.query_one("#field-help-text", Static).update(text)
        except Exception:
            pass


class SmartFormField(Vertical):
    """Complete form field with label, input, and help."""
    
    DEFAULT_CSS = """
    SmartFormField {
        height: auto;
        margin: 1 0;
    }
    
    #sff-label {
        text-style: bold;
        margin-bottom: 1;
    }
    
    #sff-label.required::after {
        content: " *";
        color: $error;
    }
    
    #sff-input-container {
        height: auto;
    }
    
    #sff-default-indicator {
        width: auto;
        color: $text-muted;
        text-style: italic;
    }
    """
    
    def __init__(self,
                 name: str,
                 label: str,
                 required: bool = False,
                 help_text: str = "",
                 placeholder: str = "",
                 validators: List[tuple] = None,
                 smart_default: Callable = None,
                 **kwargs):
        super().__init__(**kwargs)
        self.field_name = name
        self.field_label = label
        self.required = required
        self.help_text = help_text
        self.placeholder = placeholder
        self.validators = validators or []
        self.smart_default_fn = smart_default
    
    def compose(self):
        # Label
        label_text = f"{self.field_label}:"
        if self.required:
            label_text += " *"
        
        yield Static(label_text, id="sff-label")
        
        # Input with default indicator
        with Horizontal(id="sff-input-container"):
            yield SmartInput(
                placeholder=self.placeholder,
                validators=self.validators,
                smart_default=self.smart_default_fn,
                id=f"input-{self.field_name}"
            )
            yield Static("💡 auto", id="sff-default-indicator")
        
        # Help text
        yield FieldHelp(self.help_text, id=f"help-{self.field_name}")
    
    def on_smart_input_validation_result(self, event: SmartInput.ValidationResult):
        """Handle validation result."""
        try:
            help_widget = self.query_one(f"#help-{self.field_name}", FieldHelp)
            help_widget.update_help(event.message, event.level)
        except Exception:
            pass
    
    def get_value(self) -> str:
        """Get field value."""
        try:
            return self.query_one(f"#input-{self.field_name}", SmartInput).value
        except Exception:
            return ""
    
    def set_value(self, value: str):
        """Set field value."""
        try:
            self.query_one(f"#input-{self.field_name}", SmartInput).value = value
        except Exception:
            pass


class AutoSaveIndicator(Static):
    """Indicator showing auto-save status."""
    
    DEFAULT_CSS = """
    AutoSaveIndicator {
        height: auto;
        text-align: right;
        color: $text-muted;
        text-style: italic;
    }
    
    AutoSaveIndicator.saving {
        color: $warning;
    }
    
    AutoSaveIndicator.saved {
        color: $success;
    }
    
    AutoSaveIndicator.error {
        color: $error;
    }
    """
    
    STATUS_ICONS = {
        "ready": "💾",
        "saving": "⏳",
        "saved": "✓",
        "error": "⚠️",
    }
    
    def set_status(self, status: str, message: str = ""):
        """Set save status."""
        self.remove_class("saving", "saved", "error")
        
        if status in ["saving", "saved", "error"]:
            self.add_class(status)
        
        icon = self.STATUS_ICONS.get(status, "")
        self.update(f"{icon} {message}" if message else icon)


class FormProgress(Static):
    """Progress indicator for multi-step forms."""
    
    DEFAULT_CSS = """
    FormProgress {
        height: auto;
        margin: 1 0;
        padding: 1;
        border: solid $surface-lighten-1;
        background: $surface-darken-1;
    }
    
    #fp-header {
        text-align: center;
        margin-bottom: 1;
    }
    
    #fp-bar {
        height: 1;
        background: $surface-lighten-1;
    }
    
    #fp-fill {
        height: 100%;
        background: $primary;
    }
    
    #fp-text {
        text-align: center;
        margin-top: 1;
        color: $text-muted;
    }
    """
    
    completed = reactive(0)
    total = reactive(1)
    
    def __init__(self, fields: List[str], **kwargs):
        super().__init__(**kwargs)
        self.field_names = fields
        self.field_status = {f: False for f in fields}
        self.total = len(fields)
    
    def compose(self):
        yield Static("Form Completion", id="fp-header")
        
        with Static("", id="fp-bar"):
            yield Static("", id="fp-fill")
        
        yield Static("0% complete", id="fp-text")
    
    def mark_complete(self, field_name: str):
        """Mark a field as complete."""
        if field_name in self.field_status:
            self.field_status[field_name] = True
            self._update_progress()
    
    def mark_incomplete(self, field_name: str):
        """Mark a field as incomplete."""
        if field_name in self.field_status:
            self.field_status[field_name] = False
            self._update_progress()
    
    def _update_progress(self):
        """Update progress display."""
        self.completed = sum(1 for v in self.field_status.values() if v)
        percentage = int((self.completed / self.total) * 100) if self.total > 0 else 0
        
        try:
            fill = self.query_one("#fp-fill", Static)
            fill.styles.width = f"{percentage}%"
            
            self.query_one("#fp-text", Static).update(
                f"{percentage}% complete ({self.completed}/{self.total} fields)"
            )
        except Exception:
            pass


class InlineValidationIcon(Static):
    """Icon showing validation status inline."""
    
    DEFAULT_CSS = """
    InlineValidationIcon {
        width: 3;
        text-align: center;
    }
    
    InlineValidationIcon.valid {
        color: $success;
    }
    
    InlineValidationIcon.invalid {
        color: $error;
    }
    
    InlineValidationIcon.warning {
        color: $warning;
    }
    """
    
    ICONS = {
        "valid": "✓",
        "invalid": "✗",
        "warning": "⚠️",
        "": "",
    }
    
    def set_state(self, state: str):
        """Set validation state."""
        self.remove_class("valid", "invalid", "warning")
        if state:
            self.add_class(state)
        self.update(self.ICONS.get(state, ""))


# Smart default generators

def default_current_date() -> str:
    """Generate default current date."""
    from datetime import datetime
    return datetime.now().strftime("%Y-%m-%d")


def default_current_year() -> str:
    """Generate default current year."""
    from datetime import datetime
    return str(datetime.now().year)


def default_common_network() -> str:
    """Generate common network range."""
    return "192.168.1.0/24"


def default_auditor_name(preferences: Dict) -> str:
    """Generate default auditor name from preferences."""
    return preferences.get("last_used_name", "")


# Common validators

def validate_required(value: str) -> bool:
    """Validate that field is not empty."""
    return bool(value.strip())


def validate_email(value: str) -> bool:
    """Validate email format."""
    if not value:
        return True  # Optional field
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, value))


def validate_positive_integer(value: str) -> bool:
    """Validate positive integer."""
    if not value:
        return True  # Optional field
    try:
        return int(value) > 0
    except ValueError:
        return False


def validate_ip_range(value: str) -> bool:
    """Validate IP range format."""
    if not value:
        return True  # Optional field
    
    patterns = [
        r'^(\d{1,3}\.){3}\d{1,3}/\d{1,2}$',  # CIDR
        r'^(\d{1,3}\.){3}\d{1,3}-\d{1,3}$',  # Range
        r'^(\d{1,3}\.){3}\d{1,3}$',  # Single IP
    ]
    
    return any(re.match(p, value) for p in patterns)


# Formatter functions

def format_uppercase(value: str) -> str:
    """Format as uppercase."""
    return value.upper()


def format_lowercase(value: str) -> str:
    """Format as lowercase."""
    return value.lower()


def format_trim(value: str) -> str:
    """Trim whitespace."""
    return value.strip()


def format_capitalize_words(value: str) -> str:
    """Capitalize each word."""
    return value.title()


class FormSection(Vertical):
    """Collapsible form section."""
    
    DEFAULT_CSS = """
    FormSection {
        height: auto;
        border: solid $surface-lighten-1;
        margin: 1 0;
    }
    
    #fs-header {
        height: auto;
        padding: 1;
        background: $surface-darken-1;
        cursor: pointer;
    }
    
    #fs-header:hover {
        background: $surface-lighten-1;
    }
    
    #fs-icon {
        width: 3;
    }
    
    #fs-title {
        text-style: bold;
    }
    
    #fs-content {
        height: auto;
        padding: 1;
    }
    
    FormSection.collapsed #fs-content {
        display: none;
    }
    
    FormSection.collapsed #fs-icon {
        text-style: bold;
    }
    """
    
    def __init__(self, title: str, expanded: bool = True, **kwargs):
        super().__init__(**kwargs)
        self.section_title = title
        self.expanded = expanded
    
    def compose(self):
        with Horizontal(id="fs-header"):
            yield Static("▼" if self.expanded else "▶", id="fs-icon")
            yield Static(self.section_title, id="fs-title")
        
        with Vertical(id="fs-content"):
            # Subclasses should add their content here
            pass
    
    def on_click(self):
        """Toggle expansion."""
        self.expanded = not self.expanded
        self.toggle_class("collapsed")
        
        try:
            icon = self.query_one("#fs-icon", Static)
            icon.update("▼" if self.expanded else "▶")
        except Exception:
            pass
