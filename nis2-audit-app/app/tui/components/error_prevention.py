"""
Error Prevention Components - Loop 4
Confirmation dialogs, soft validation, and auto-correction.
"""
from textual.screen import ModalScreen
from textual.widgets import Static, Button, Input
from textual.containers import Vertical, Horizontal
from textual.reactive import reactive
from textual.binding import Binding
from typing import Optional, Callable, Any, List
import re


class ConfirmationDialog(ModalScreen):
    """Confirmation dialog with consequence explanation."""
    
    CSS = """
    #confirm-dialog {
        width: 60;
        height: auto;
        border: thick $warning;
        background: $surface;
        padding: 2;
    }
    
    #confirm-title {
        text-align: center;
        text-style: bold;
        color: $warning;
        margin-bottom: 1;
        border-bottom: solid $warning;
    }
    
    #confirm-message {
        text-align: center;
        margin: 1 0;
        height: auto;
    }
    
    #confirm-consequences {
        border: solid $error-darken-2;
        background: $error-darken-3;
        color: $text;
        padding: 1;
        margin: 1 0;
        height: auto;
    }
    
    #consequences-title {
        text-style: bold;
        color: $error;
        margin-bottom: 1;
    }
    
    #confirm-actions {
        align: center middle;
        margin-top: 2;
    }
    
    #confirm-actions Button {
        margin: 0 1;
    }
    
    #confirm-dont-ask {
        margin-top: 1;
        text-align: center;
        color: $text-muted;
    }
    """
    
    BINDINGS = [
        Binding("escape", "cancel", "Cancel"),
        Binding("y", "confirm", "Yes"),
        Binding("n", "cancel", "No"),
    ]
    
    def __init__(self,
                 title: str = "Confirm Action",
                 message: str = "",
                 consequences: List[str] = None,
                 confirm_label: str = "Yes, Proceed",
                 cancel_label: str = "No, Cancel",
                 danger: bool = False,
                 **kwargs):
        super().__init__(**kwargs)
        self.title = title
        self.message = message
        self.consequences = consequences or []
        self.confirm_label = confirm_label
        self.cancel_label = cancel_label
        self.danger = danger
    
    def compose(self):
        with Vertical(id="confirm-dialog"):
            yield Static(f"⚠️  {self.title}", id="confirm-title")
            yield Static(self.message, id="confirm-message")
            
            if self.consequences:
                with Vertical(id="confirm-consequences"):
                    yield Static("📋 This will:", id="consequences-title")
                    for consequence in self.consequences:
                        yield Static(f"  • {consequence}")
            
            with Horizontal(id="confirm-actions"):
                confirm_variant = "error" if self.danger else "primary"
                yield Button(self.cancel_label, id="btn-cancel")
                yield Button(self.confirm_label, variant=confirm_variant, id="btn-confirm")
            
            yield Static("Press Y to confirm, N to cancel", id="confirm-dont-ask")
    
    def on_button_pressed(self, event):
        """Handle button presses."""
        if event.button.id == "btn-confirm":
            self.dismiss(True)
        else:
            self.dismiss(False)
    
    def action_confirm(self):
        """Confirm via keyboard."""
        self.dismiss(True)
    
    def action_cancel(self):
        """Cancel via keyboard."""
        self.dismiss(False)


class SoftValidationInput(Input):
    """Input with soft validation (warnings vs errors)."""
    
    DEFAULT_CSS = """
    SoftValidationInput {
        border: solid $surface-lighten-1;
    }
    
    SoftValidationInput:focus {
        border: solid $primary;
    }
    
    SoftValidationInput.error {
        border: solid $error;
        background: $error-darken-3;
    }
    
    SoftValidationInput.warning {
        border: solid $warning;
        background: $warning-darken-3;
    }
    
    SoftValidationInput.valid {
        border: solid $success;
    }
    """
    
    validation_state = reactive("")  # "", "valid", "warning", "error"
    
    def __init__(self,
                 validators: List[tuple] = None,
                 auto_correct: bool = False,
                 **kwargs):
        super().__init__(**kwargs)
        self.validators = validators or []  # List of (check_fn, level, message)
        self.auto_correct = auto_correct
        self._last_value = ""
    
    def validate(self, value: str) -> tuple[str, str, Optional[str]]:
        """
        Validate value.
        Returns: (level, message, suggestion)
        """
        for check_fn, level, message in self.validators:
            if not check_fn(value):
                # Get correction suggestion if available
                suggestion = None
                if hasattr(check_fn, 'suggest_correction'):
                    suggestion = check_fn.suggest_correction(value)
                return level, message, suggestion
        
        return "valid", "✓ Looks good", None
    
    def watch_value(self, value: str):
        """Validate on value change."""
        if value != self._last_value:
            self._last_value = value
            level, message, suggestion = self.validate(value)
            self.validation_state = level
            
            # Auto-correct if enabled and suggestion available
            if self.auto_correct and suggestion and level == "error":
                self._suggest_correction(suggestion)
            
            # Update visual state
            self.remove_class("valid", "warning", "error")
            if level != "":
                self.add_class(level)
            
            # Emit validation message
            self.post_message(self.ValidationChanged(level, message, suggestion))
    
    def _suggest_correction(self, suggestion: str):
        """Show correction suggestion."""
        self.post_message(self.CorrectionSuggested(self.value, suggestion))
    
    class ValidationChanged:
        """Message sent when validation state changes."""
        def __init__(self, level: str, message: str, suggestion: Optional[str]):
            self.level = level
            self.message = message
            self.suggestion = suggestion
    
    class CorrectionSuggested:
        """Message sent when auto-correction is suggested."""
        def __init__(self, original: str, suggestion: str):
            self.original = original
            self.suggestion = suggestion


class AutoCorrectionButton(Static):
    """Button to apply suggested correction."""
    
    DEFAULT_CSS = """
    AutoCorrectionButton {
        height: auto;
        background: $primary-darken-2;
        color: $text;
        padding: 0 1;
        margin: 0 1;
        cursor: pointer;
    }
    
    AutoCorrectionButton:hover {
        background: $primary;
    }
    """
    
    def __init__(self, original: str, suggestion: str, **kwargs):
        super().__init__(**kwargs)
        self.original = original
        self.suggestion = suggestion
    
    def compose(self):
        yield Static(f"💡 Did you mean: '{self.suggestion}'? (Click to apply)")
    
    def on_click(self):
        """Apply correction."""
        self.post_message(self.ApplyCorrection(self.suggestion))
    
    class ApplyCorrection:
        """Message to apply correction."""
        def __init__(self, value: str):
            self.value = value


class DestructiveActionButton(Button):
    """Button for destructive actions with confirmation."""
    
    def __init__(self,
                 label: str,
                 action_name: str = "",
                 consequences: List[str] = None,
                 **kwargs):
        super().__init__(label, variant="error", **kwargs)
        self.action_name = action_name or label
        self.consequences = consequences or []
        self._confirmed = False
    
    async def on_press(self):
        """Show confirmation before action."""
        if not self._confirmed and self.consequences:
            dialog = ConfirmationDialog(
                title=f"Confirm: {self.action_name}",
                message=f"Are you sure you want to {self.action_name.lower()}?",
                consequences=self.consequences,
                danger=True,
            )
            result = await self.app.push_screen_wait(dialog)
            
            if result:
                self._confirmed = True
                # Re-trigger the press
                self.press()
            else:
                self._confirmed = False
        else:
            self._confirmed = False
            await super().on_press()


class UndoableAction:
    """Mixin for actions that can be undone."""
    
    def __init__(self):
        self._undo_stack: List[Any] = []
        self._redo_stack: List[Any] = []
        self._max_undo = 10
    
    def do_action(self, action: Any):
        """Perform an action and add to undo stack."""
        self._undo_stack.append(action)
        self._redo_stack.clear()
        
        # Limit undo stack size
        if len(self._undo_stack) > self._max_undo:
            self._undo_stack.pop(0)
    
    def undo(self) -> Optional[Any]:
        """Undo last action."""
        if self._undo_stack:
            action = self._undo_stack.pop()
            self._redo_stack.append(action)
            return action
        return None
    
    def redo(self) -> Optional[Any]:
        """Redo last undone action."""
        if self._redo_stack:
            action = self._redo_stack.pop()
            self._undo_stack.append(action)
            return action
        return None
    
    def can_undo(self) -> bool:
        """Check if undo is available."""
        return len(self._undo_stack) > 0
    
    def can_redo(self) -> bool:
        """Check if redo is available."""
        return len(self._redo_stack) > 0


class SafeInput(Input):
    """Input with safety features to prevent data loss."""
    
    DEFAULT_CSS = """
    SafeInput {
        border: solid $surface-lighten-1;
    }
    
    SafeInput.dirty {
        border: solid $warning;
    }
    
    SafeInput:focus.dirty {
        border: solid $primary;
    }
    """
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._original_value = ""
        self._is_dirty = False
    
    def on_mount(self):
        """Store original value."""
        self._original_value = self.value
    
    def watch_value(self, value: str):
        """Track changes."""
        self._is_dirty = (value != self._original_value)
        if self._is_dirty:
            self.add_class("dirty")
        else:
            self.remove_class("dirty")
    
    def has_changes(self) -> bool:
        """Check if input has unsaved changes."""
        return self._is_dirty
    
    def reset(self):
        """Reset to original value."""
        self.value = self._original_value
        self._is_dirty = False
        self.remove_class("dirty")
    
    def confirm(self):
        """Confirm current value as new baseline."""
        self._original_value = self.value
        self._is_dirty = False
        self.remove_class("dirty")


# Common validators with auto-correction suggestions

def validate_ip_range(value: str) -> bool:
    """Validate IP range format."""
    if not value:
        return True  # Empty is OK for optional fields
    
    # CIDR notation
    cidr_pattern = r'^(\d{1,3}\.){3}\d{1,3}/\d{1,2}$'
    # Range notation
    range_pattern = r'^(\d{1,3}\.){3}\d{1,3}-\d{1,3}$'
    # Single IP
    ip_pattern = r'^(\d{1,3}\.){3}\d{1,3}$'
    
    return bool(re.match(cidr_pattern, value) or 
                re.match(range_pattern, value) or 
                re.match(ip_pattern, value))

validate_ip_range.suggest_correction = lambda v: suggest_ip_fix(v)


def suggest_ip_fix(value: str) -> Optional[str]:
    """Suggest fix for common IP range mistakes."""
    # Missing CIDR slash
    if re.match(r'^(\d{1,3}\.){3}\d{1,3}$', value):
        return f"{value}/24"
    
    # Wrong slash direction
    if '\\' in value:
        return value.replace('\\', '/')
    
    # Missing dots
    if re.match(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\d{1,3}', value):
        parts = value.split('.')
        if len(parts) == 3:
            last_two = parts[2]
            if len(last_two) > 3:
                return f"{parts[0]}.{parts[1]}.{last_two[:3]}.{last_two[3:]}"
    
    return None


def validate_email(value: str) -> bool:
    """Validate email format."""
    if not value:
        return True
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, value))


def validate_positive_number(value: str) -> bool:
    """Validate positive number."""
    if not value:
        return True
    try:
        return float(value) >= 0
    except ValueError:
        return False


# Predefined consequence lists
DELETE_SESSION_CONSEQUENCES = [
    "Permanently delete this audit session",
    "Remove all associated device data",
    "Delete all checklist responses",
    "Remove all findings and reports",
    "This action cannot be undone",
]

CLEAR_SCAN_CONSEQUENCES = [
    "Remove all discovered devices",
    "Delete device fingerprinting data",
    "Clear connection history",
    "You'll need to rescan to restore this data",
]

RESET_CHECKLIST_CONSEQUENCES = [
    "Clear all your answers",
    "Reset compliance score to 0%",
    "Remove all generated findings",
    "This cannot be undone (though you can re-answer)",
]
