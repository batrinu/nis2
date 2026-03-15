"""
Smart Form Components with Auto-Save, Validation, and Smart Defaults
Makes forms intelligent and forgiving for non-technical users.
"""
import re
from datetime import datetime
from typing import Optional, Callable, Any, Dict
from dataclasses import dataclass
from textual.reactive import reactive
from textual.widgets import Input, Static
from textual.containers import Vertical
from textual.timer import Timer
from ...i18n import get_text as _


@dataclass
class ValidationRule:
    """Validation rule for form fields."""
    name: str
    validator: Callable[[str], bool]
    error_message: str
    warning_message: Optional[str] = None


@dataclass
class SmartDefault:
    """Smart default value with context."""
    value: Any
    description: str
    condition: Optional[Callable] = None


class ValidatedInput(Input):
    """Input with real-time validation and visual feedback."""
    
    DEFAULT_CSS = """
    ValidatedInput {
        border: solid $primary;
    }
    ValidatedInput.valid {
        border: solid $success;
    }
    ValidatedInput.invalid {
        border: solid $error;
    }
    ValidatedInput.warning {
        border: solid $warning;
    }
    """
    
    # Reactive validation state
    is_valid = reactive(True)
    validation_message = reactive("")
    validation_level = reactive("")  # "valid", "invalid", "warning"
    
    def __init__(self, *args, 
                 validators: list = None,
                 required: bool = False,
                 hint: str = "",
                 **kwargs):
        """Initialize validated input with validation rules.
        
        Args:
            validators: List of ValidationRule objects for validation.
            required: Whether this field is required.
            hint: Hint text to display when field is empty.
            *args: Additional arguments passed to Input.
            **kwargs: Additional keyword arguments passed to Input.
        """
        super().__init__(*args, **kwargs)
        self.validators = validators or []
        self.required = required
        self.hint = hint
        self._validation_delay = 0.5  # seconds
        self._validation_timer: Optional[Timer] = None
    
    def validate(self, value: str) -> tuple[bool, str, str]:
        """
        Validate current value.
        Returns: (is_valid, level, message)
        """
        if self.required and not value.strip():
            return False, "invalid", _("This field is required")
        
        if not value:
            return True, "", self.hint
        
        for rule in self.validators:
            if not rule.validator(value):
                return False, "invalid", rule.error_message
        
        return True, "valid", _("✓ Looks good")
    
    def watch_value(self, value: str):
        """Trigger validation on value change with debounce."""
        if self._validation_timer:
            self._validation_timer.stop()
        
        self._validation_timer = self.set_timer(
            self._validation_delay,
            lambda: self._do_validation(value)
        )
    
    def _do_validation(self, value: str):
        """Perform validation and update state."""
        is_valid, level, message = self.validate(value)
        self.is_valid = is_valid
        self.validation_level = level
        self.validation_message = message
        
        # Update visual state
        self.remove_class("valid", "invalid", "warning")
        if level:
            self.add_class(level)


class AutoSaveForm(Vertical):
    """
    Form container with auto-save functionality.
    Saves form data automatically to prevent data loss.
    """
    
    DEFAULT_CSS = """
    AutoSaveForm {
        height: auto;
    }
    #autosave-status {
        text-align: right;
        color: $text-muted;
        text-style: italic;
        height: 1;
    }
    #autosave-status.saving {
        color: $warning;
    }
    #autosave-status.saved {
        color: $success;
    }
    """
    
    # Reactive state
    has_unsaved_changes = reactive(False)
    last_saved = reactive(None)
    save_status = reactive("ready")  # ready, saving, saved, error
    
    def __init__(self, 
                 form_id: str,
                 storage_path: Optional[str] = None,
                 auto_save_interval: int = 30,
                 *args, **kwargs):
        """Initialize auto-save form container.
        
        Args:
            form_id: Unique identifier for this form.
            storage_path: Path to store draft data. Uses default if not provided.
            auto_save_interval: Seconds between auto-save attempts. 0 to disable.
            *args: Additional arguments passed to Vertical.
            **kwargs: Additional keyword arguments passed to Vertical.
        """
        super().__init__(*args, **kwargs)
        self.form_id = form_id
        self.storage_path = storage_path or self._get_default_storage_path()
        self.auto_save_interval = auto_save_interval
        self._form_data: Dict[str, Any] = {}
        self._save_timer: Optional[Timer] = None
        self._draft_key = f"{form_id}_draft"
    
    def _get_default_storage_path(self) -> str:
        """Get default path for draft storage."""
        import os
        config_dir = os.path.expanduser("~/.nis2-audit")
        os.makedirs(config_dir, exist_ok=True)
        return os.path.join(config_dir, "form_drafts.json")
    
    def compose(self):
        """Compose form with auto-save indicator."""
        yield Static(_("💾 Auto-save ready"), id="autosave-status")
    
    def on_mount(self):
        """Initialize auto-save timer and load draft."""
        self._start_auto_save_timer()
        self._load_draft()
    
    def _start_auto_save_timer(self):
        """Start periodic auto-save."""
        if self.auto_save_interval > 0:
            self._save_timer = self.set_interval(
                self.auto_save_interval,
                self._auto_save
            )
    
    def watch_has_unsaved_changes(self, has_changes: bool):
        """Update status when changes occur.
        
        Reactive watcher triggered when has_unsaved_changes changes.
        
        Args:
            has_changes: Whether there are unsaved changes.
        """
        if has_changes:
            self._update_status(_("● Unsaved changes"), "warning")
        elif self.last_saved:
            time_str = self.last_saved.strftime("%H:%M")
            self._update_status(_("✓ Saved at {time_str}").format(time_str=time_str), "saved")
    
    def watch_save_status(self, status: str):
        """Update visual status indicator.
        
        Reactive watcher triggered when save_status changes.
        
        Args:
            status: Current save status (ready, saving, saved, error).
        """
        status_messages = {
            "ready": (_("💾 Auto-save ready"), ""),
            "saving": (_("⏳ Saving..."), "saving"),
            "saved": (_("✓ Saved at {time}").format(time=self.last_saved.strftime('%H:%M')) if self.last_saved else _("✓ Saved"), "saved"),
            "error": (_("⚠ Save failed - retrying..."), "error"),
        }
        message, style = status_messages.get(status, ("Unknown", ""))
        self._update_status(message, style)
    
    def _update_status(self, message: str, style: str):
        """Update status label."""
        try:
            status_label = self.query_one("#autosave-status", Static)
            status_label.update(message)
            status_label.remove_class("saving", "saved", "error")
            if style:
                status_label.add_class(style)
        except Exception:
            pass
    
    def update_field(self, field_id: str, value: Any):
        """Update a form field value."""
        old_value = self._form_data.get(field_id)
        self._form_data[field_id] = value
        
        if old_value != value:
            self.has_unsaved_changes = True
    
    def get_field(self, field_id: str, default: Any = None) -> Any:
        """Get a form field value."""
        return self._form_data.get(field_id, default)
    
    def get_all_data(self) -> Dict[str, Any]:
        """Get all form data."""
        return self._form_data.copy()
    
    def _auto_save(self):
        """Auto-save form data."""
        if self.has_unsaved_changes:
            self.save_draft()
    
    def save_draft(self) -> bool:
        """
        Save form data as draft.
        Returns True if successful.
        """
        self.save_status = "saving"
        
        try:
            import json
            import os
            
            # Load existing drafts
            drafts = {}
            if os.path.exists(self.storage_path):
                try:
                    with open(self.storage_path, 'r') as f:
                        drafts = json.load(f)
                except (OSError, IOError, json.JSONDecodeError) as e:
                    logger.warning(f"Failed to load existing drafts: {e}")
                    drafts = {}
            
            # Update with current draft
            drafts[self._draft_key] = {
                'data': self._form_data,
                'timestamp': datetime.now().isoformat(),
                'form_id': self.form_id,
            }
            
            # Save back
            try:
                with open(self.storage_path, 'w') as f:
                    json.dump(drafts, f, indent=2)
            except (OSError, IOError) as e:
                logger.error(f"Failed to save draft: {e}")
                self.save_status = "error"
                return False
            
            self.has_unsaved_changes = False
            self.last_saved = datetime.now()
            self.save_status = "saved"
            return True
            
        except Exception as e:
            logger.error(f"Unexpected error saving draft: {e}")
            self.save_status = "error"
            return False
    
    def _load_draft(self) -> bool:
        """
        Load saved draft if exists.
        Returns True if draft was loaded.
        """
        try:
            import json
            import os
            
            if not os.path.exists(self.storage_path):
                return False
            
            with open(self.storage_path, 'r') as f:
                drafts = json.load(f)
            
            draft = drafts.get(self._draft_key)
            if draft:
                self._form_data = draft.get('data', {})
                saved_time = draft.get('timestamp', '')
                try:
                    self.last_saved = datetime.fromisoformat(saved_time) if saved_time else None
                except (ValueError, TypeError):
                    self.last_saved = None
                self.save_status = "saved"
                return True
            
            return False
            
        except Exception:
            return False
    
    def clear_draft(self):
        """Clear saved draft after successful submission."""
        try:
            import json
            import os
            
            if os.path.exists(self.storage_path):
                with open(self.storage_path, 'r') as f:
                    drafts = json.load(f)
                
                drafts.pop(self._draft_key, None)
                
                with open(self.storage_path, 'w') as f:
                    json.dump(drafts, f, indent=2)
            
            self._form_data = {}
            self.has_unsaved_changes = False
            self.last_saved = None
            
        except Exception:
            pass
    
    def format_smart_default(self, field_type: str, context: Dict = None) -> Optional[str]:
        """
        Generate smart default value based on context.
        Returns None if no smart default available.
        """
        context = context or {}
        
        defaults = {
            'date': lambda: datetime.now().strftime("%Y-%m-%d"),
            'datetime': lambda: datetime.now().strftime("%Y-%m-%d %H:%M"),
            'year': lambda: str(datetime.now().year),
            'auditor': lambda: context.get('current_user', ''),
            'location': lambda: context.get('default_location', ''),
            'network_segment': lambda: self._suggest_network_segment(),
        }
        
        default_fn = defaults.get(field_type)
        if default_fn:
            try:
                return default_fn()
            except Exception:
                return None
        return None
    
    def _suggest_network_segment(self) -> Optional[str]:
        """Suggest common network segment based on context."""
        # Common private network ranges
        return "192.168.1.0/24"
    
    def validate_all(self, required_fields: list) -> tuple[bool, list]:
        """
        Validate all required fields.
        Returns (is_valid, list_of_errors).
        """
        errors = []
        
        for field_id in required_fields:
            value = self._form_data.get(field_id)
            if not value or (isinstance(value, str) and not value.strip()):
                errors.append(_("'{field_id}' is required").format(field_id=field_id))
        
        return len(errors) == 0, errors


class FormHelper:
    """Static helper methods for form operations."""
    
    @staticmethod
    def sanitize_input(value: str, max_length: int = 255) -> str:
        """Sanitize user input for safety."""
        if not value:
            return ""
        
        # Remove control characters
        sanitized = re.sub(r'[\x00-\x1F\x7F]', '', value)
        
        # Limit length
        sanitized = sanitized[:max_length]
        
        return sanitized.strip()
    
    @staticmethod
    def format_number(value: str, as_int: bool = False) -> Optional[float]:
        """Parse and format number input."""
        try:
            # Remove common separators
            cleaned = value.replace(',', '').replace(' ', '')
            if as_int:
                return int(cleaned)
            return float(cleaned)
        except ValueError:
            return None
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """Validate email format."""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    @staticmethod
    def validate_ip_range(ip_range: str) -> tuple[bool, str]:
        """Validate IP range format."""
        # Support formats: 192.168.1.0/24, 192.168.1.0-255, 192.168.1.0/255.255.255.0
        patterns = [
            r'^(\d{1,3}\.){3}\d{1,3}/\d{1,2}$',  # CIDR
            r'^(\d{1,3}\.){3}\d{1,3}-\d{1,3}$',  # Range
            r'^(\d{1,3}\.){3}\d{1,3}$',  # Single IP
        ]
        
        for pattern in patterns:
            if re.match(pattern, ip_range):
                return True, _("Valid format")
        
        return False, _("Use format: 192.168.1.0/24")
    
    @staticmethod
    def format_currency(amount: float, currency: str = "€") -> str:
        """Format currency amount."""
        if amount >= 1_000_000:
            return f"{currency}{amount/1_000_000:.1f}M"
        elif amount >= 1_000:
            return f"{currency}{amount/1_000:.1f}k"
        return f"{currency}{amount:,.0f}"



# ============================================================================
# Error Prevention Enhancements - Loop 4
# ============================================================================

from textual.screen import ModalScreen
from textual.binding import Binding
from textual.widgets import Button
from textual.containers import Vertical, Horizontal
from typing import List


class ConfirmationDialog(ModalScreen):
    """Confirmation dialog with consequence explanation for destructive actions."""
    
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
    """
    
    BINDINGS = [
        Binding("escape", "cancel", "Cancel"),
        Binding("y", "confirm", "Yes"),
        Binding("n", "cancel", "No"),
    ]
    
    def __init__(self,
                 title: str = _("Confirm Action"),
                 message: str = "",
                 consequences: List[str] = None,
                 confirm_label: str = _("Yes, Proceed"),
                 cancel_label: str = _("No, Cancel"),
                 danger: bool = False,
                 **kwargs):
        """Initialize confirmation dialog.
        
        Args:
            title: Dialog title displayed at the top.
            message: Main message describing the action.
            consequences: List of consequences to display to the user.
            confirm_label: Label for the confirm button.
            cancel_label: Label for the cancel button.
            danger: Whether this is a dangerous action (uses error styling).
            **kwargs: Additional keyword arguments passed to ModalScreen.
        """
        super().__init__(**kwargs)
        self.dialog_title = title
        self.message = message
        self.consequences = consequences or []
        self.confirm_label = confirm_label
        self.cancel_label = cancel_label
        self.danger = danger
    
    def compose(self):
        with Vertical(id="confirm-dialog"):
            yield Static(f"⚠️  {self.dialog_title}", id="confirm-title")
            yield Static(self.message, id="confirm-message")
            
            if self.consequences:
                with Vertical(id="confirm-consequences"):
                    yield Static(_("📋 This will:"), id="consequences-title")
                    for consequence in self.consequences:
                        yield Static(f"  • {consequence}")
            
            with Horizontal(id="confirm-actions"):
                confirm_variant = "error" if self.danger else "primary"
                yield Button(self.cancel_label, id="btn-cancel")
                yield Button(self.confirm_label, variant=confirm_variant, id="btn-confirm")
    
    def on_button_pressed(self, event):
        """Handle button presses."""
        if event.button.id == "btn-confirm":
            self.dismiss(True)
        else:
            self.dismiss(False)
    
    def action_confirm(self):
        """Confirm via keyboard shortcut (y key).
        
        Dismisses the dialog with True result.
        """
        self.dismiss(True)
    
    def action_cancel(self):
        """Cancel via keyboard shortcut (n or escape key).
        
        Dismisses the dialog with False result.
        """
        self.dismiss(False)


class SoftValidationInput(ValidatedInput):
    """Input with soft validation (warnings vs errors)."""
    
    DEFAULT_CSS = """
    SoftValidationInput {
        border: solid $primary;
    }
    
    SoftValidationInput.valid {
        border: solid $success;
    }
    
    SoftValidationInput.invalid {
        border: solid $error;
        background: $error-darken-3;
    }
    
    SoftValidationInput.warning {
        border: solid $warning;
        background: $warning-darken-3;
    }
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.soft_validators = []  # (check_fn, level, message)
    
    def add_soft_validator(self, check_fn, level: str, message: str):
        """Add a soft validator with level ('warning' or 'error')."""
        self.soft_validators.append((check_fn, level, message))
    
    def validate(self, value: str) -> tuple[bool, str, str]:
        """Validate with soft warnings."""
        # Check required
        if self.required and not value.strip():
            return False, "invalid", _("This field is required")
        
        # Check hard validators first
        for rule in self.validators:
            if not rule.validator(value):
                return False, "invalid", rule.error_message
        
        # Check soft validators
        for check_fn, level, message in self.soft_validators:
            if not check_fn(value):
                return True, level, message  # Return as warning, not error
        
        return True, "valid", _("✓ Looks good")


class SafeDeleteButton(Button):
    """Button that confirms before destructive actions."""
    
    def __init__(self, label: str, item_name: str = "", consequences: List[str] = None, **kwargs):
        super().__init__(label, variant="error", **kwargs)
        self.item_name = item_name or label
        self.consequences = consequences or [f"Delete {self.item_name}"]
    
    async def on_press(self):
        """Show confirmation dialog."""
        dialog = ConfirmationDialog(
            title=_("Confirm Delete"),
            message=_("Are you sure you want to delete '{item_name}'?").format(item_name=self.item_name),
            consequences=self.consequences,
            danger=True,
        )
        result = await self.app.push_screen_wait(dialog)
        
        if result:
            # User confirmed, proceed with action
            await super().on_press()


class AutoCorrectionSuggestion(Static):
    """Suggestion for auto-correcting input."""
    
    DEFAULT_CSS = """
    AutoCorrectionSuggestion {
        height: auto;
        background: $primary-darken-3;
        color: $text;
        padding: 0 1;
        margin: 0 1;
    }
    
    AutoCorrectionSuggestion:hover {
        background: $primary;
        cursor: pointer;
    }
    """
    
    def __init__(self, original: str, suggestion: str, **kwargs):
        """Initialize auto-correction suggestion widget.
        
        Args:
            original: Original input value.
            suggestion: Suggested correction.
            **kwargs: Additional keyword arguments passed to Static.
        """
        super().__init__(**kwargs)
        self.original = original
        self.suggestion = suggestion
    
    def compose(self):
        """Compose the correction suggestion display."""
        yield Static(_("💡 Did you mean: '{suggestion}'? (Click to apply)").format(suggestion=self.suggestion))
    
    def on_click(self):
        """Apply correction when user clicks the suggestion.
        
        Posts an ApplyCorrection message with the suggested value.
        """
        self.post_message(self.ApplyCorrection(self.suggestion))
    
    class ApplyCorrection:
        """Message to apply correction."""
        def __init__(self, value: str):
            self.value = value


# Predefined consequence lists for common destructive actions
DELETE_SESSION_CONSEQUENCES = [
    _("Permanently delete this audit session"),
    _("Remove all associated device data"),
    _("Delete all checklist responses"),
    _("Remove all findings and reports"),
    _("This action cannot be undone"),
]

CLEAR_SCAN_CONSEQUENCES = [
    _("Remove all discovered devices"),
    _("Delete device fingerprinting data"),
    _("Clear connection history"),
    _("You'll need to rescan to restore this data"),
]

RESET_CHECKLIST_CONSEQUENCES = [
    _("Clear all your answers"),
    _("Reset compliance score to 0%"),
    _("Remove all generated findings"),
    _("This cannot be undone (though you can re-answer)"),
]
