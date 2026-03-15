"""
User Experience Module for NIS2 Field Audit Tool
Passes 122-142: User-Friendly TUI Features

This module provides user experience enhancements to make the NIS2 audit tool
accessible and easy to use, especially for users who may not be technical experts.
"""

import os
import json
import time
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any, Callable, Iterator
from dataclasses import dataclass, asdict
from enum import Enum

logger = logging.getLogger(__name__)

# ============================================================================
# Custom Exceptions
# ============================================================================

class BackupError(Exception):
    """Raised when backup creation or restoration fails."""
    pass


# ============================================================================
# Pass 122: User Preference Management
# ============================================================================

class ThemeMode(Enum):
    """Available theme modes for accessibility."""
    DEFAULT = "default"
    HIGH_CONTRAST = "high_contrast"
    COLORBLIND_DEUTERANOPIA = "colorblind_deuteranopia"
    COLORBLIND_PROTANOPIA = "colorblind_protanopia"
    COLORBLIND_TRITANOPIA = "colorblind_tritanopia"
    MONOCHROME = "monochrome"
    DARK_MODE = "dark"
    LIGHT_MODE = "light"


@dataclass
class UserPreferences:
    """User preference settings for personalized experience."""
    theme: str = ThemeMode.DEFAULT.value
    font_size: str = "medium"  # small, medium, large
    animations_enabled: bool = True
    sound_enabled: bool = False
    auto_save: bool = True
    auto_save_interval: int = 300  # seconds
    confirm_destructive_actions: bool = True
    show_help_tips: bool = True
    language: str = "en"
    date_format: str = "%Y-%m-%d"
    time_format: str = "%H:%M"
    timezone: str = "local"
    keyboard_mode: str = "default"  # default, vim, emacs
    screen_reader_mode: bool = False
    reduced_motion: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'UserPreferences':
        return cls(**data)


class PreferenceManager:
    """Manages user preferences with persistence."""
    
    def __init__(self, config_dir: str = None):
        self.config_dir = Path(config_dir or Path.home() / ".nis2-audit")
        self.preferences_file = self.config_dir / "preferences.json"
        self._preferences = UserPreferences()
        self._load_preferences()
    
    def _load_preferences(self) -> None:
        """Load preferences from disk."""
        if self.preferences_file.exists():
            try:
                with open(self.preferences_file, 'r') as f:
                    data = json.load(f)
                    self._preferences = UserPreferences.from_dict(data)
            except (json.JSONDecodeError, TypeError):
                # Use defaults if file is corrupted
                self._preferences = UserPreferences()
    
    def save_preferences(self) -> None:
        """Save preferences to disk."""
        try:
            self.config_dir.mkdir(parents=True, exist_ok=True)
            with open(self.preferences_file, 'w') as f:
                json.dump(self._preferences.to_dict(), f, indent=2)
        except (OSError, IOError) as e:
            logger.warning(f"Failed to save preferences: {e}")
    
    def get(self) -> UserPreferences:
        """Get current preferences."""
        return self._preferences
    
    def update(self, **kwargs) -> None:
        """Update preferences."""
        for key, value in kwargs.items():
            if hasattr(self._preferences, key):
                setattr(self._preferences, key, value)
        self.save_preferences()
    
    def reset_to_defaults(self) -> None:
        """Reset all preferences to defaults."""
        self._preferences = UserPreferences()
        self.save_preferences()


# ============================================================================
# Pass 123: Accessibility Theme Engine
# ============================================================================

class ThemeEngine:
    """Provides accessibility-friendly color themes."""
    
    THEMES = {
        ThemeMode.DEFAULT: {
            'primary': '#0A84FF',
            'success': '#30D158',
            'warning': '#FFD60A',
            'error': '#FF453A',
            'info': '#5E5CE6',
            'text': '#FFFFFF',
            'background': '#1C1C1E',
            'border': '#48484A',
            'muted': '#8E8E93',
        },
        ThemeMode.HIGH_CONTRAST: {
            'primary': '#00BFFF',
            'success': '#00FF00',
            'warning': '#FFFF00',
            'error': '#FF0000',
            'info': '#00FFFF',
            'text': '#FFFFFF',
            'background': '#000000',
            'border': '#FFFFFF',
            'muted': '#CCCCCC',
        },
        ThemeMode.COLORBLIND_DEUTERANOPIA: {
            # Red-green colorblind friendly (blue-yellow palette)
            'primary': '#0066CC',
            'success': '#E6A700',
            'warning': '#FFCC00',
            'error': '#9900CC',
            'info': '#0099CC',
            'text': '#FFFFFF',
            'background': '#1A1A1A',
            'border': '#666666',
            'muted': '#999999',
        },
        ThemeMode.COLORBLIND_PROTANOPIA: {
            # Red-green colorblind friendly (avoids red)
            'primary': '#4477AA',
            'success': '#DDCC77',
            'warning': '#FFCC00',
            'error': '#AA3377',
            'info': '#66CCEE',
            'text': '#FFFFFF',
            'background': '#1A1A1A',
            'border': '#666666',
            'muted': '#999999',
        },
        ThemeMode.MONOCHROME: {
            'primary': '#FFFFFF',
            'success': '#CCCCCC',
            'warning': '#999999',
            'error': '#666666',
            'info': '#AAAAAA',
            'text': '#FFFFFF',
            'background': '#000000',
            'border': '#FFFFFF',
            'muted': '#888888',
        },
    }
    
    @classmethod
    def get_theme(cls, theme_mode: ThemeMode) -> Dict[str, str]:
        """Get color palette for theme."""
        return cls.THEMES.get(theme_mode, cls.THEMES[ThemeMode.DEFAULT])
    
    @classmethod
    def get_symbol(cls, symbol_type: str, theme_mode: ThemeMode) -> str:
        """Get accessible symbol (not relying on color alone)."""
        symbols = {
            'success': {
                ThemeMode.DEFAULT: '✓',
                ThemeMode.HIGH_CONTRAST: '[OK]',
                ThemeMode.MONOCHROME: '[OK]',
            },
            'error': {
                ThemeMode.DEFAULT: '✗',
                ThemeMode.HIGH_CONTRAST: '[ERR]',
                ThemeMode.MONOCHROME: '[ERR]',
            },
            'warning': {
                ThemeMode.DEFAULT: '⚠',
                ThemeMode.HIGH_CONTRAST: '[WARN]',
                ThemeMode.MONOCHROME: '[WARN]',
            },
            'info': {
                ThemeMode.DEFAULT: 'ℹ',
                ThemeMode.HIGH_CONTRAST: '[INFO]',
                ThemeMode.MONOCHROME: '[INFO]',
            },
        }
        return symbols.get(symbol_type, {}).get(theme_mode, symbols[symbol_type][ThemeMode.DEFAULT])


# ============================================================================
# Pass 124: Contextual Help System
# ============================================================================

class HelpSystem:
    """Provides contextual help for UI elements."""
    
    HELP_TOPICS = {
        'main_menu': {
            'title': 'Main Menu',
            'description': 'Navigate through audit functions using arrow keys or number keys.',
            'shortcuts': ['↑/↓ - Navigate', 'Enter - Select', 'q - Quit', '? - Help'],
        },
        'device_scan': {
            'title': 'Device Scan',
            'description': 'Scan network devices for security compliance.',
            'shortcuts': ['Tab - Next field', 'Enter - Start scan', 'Esc - Cancel'],
            'tips': ['Use IP ranges like 192.168.1.1-254', 'SSH credentials required for deep scans'],
        },
        'audit_report': {
            'title': 'Audit Report',
            'description': 'View and export compliance audit results.',
            'shortcuts': ['e - Export', 'f - Filter', 's - Sort', 'r - Refresh'],
        },
        'configuration': {
            'title': 'Configuration',
            'description': 'Manage audit settings and preferences.',
            'shortcuts': ['Tab - Next field', 'Ctrl+S - Save', 'Esc - Cancel changes'],
        },
        'incident_response': {
            'title': 'Incident Response',
            'description': 'Document and track security incidents.',
            'shortcuts': ['n - New incident', 'u - Update', 'a - Assign'],
            'tips': ['NIS2 requires 24-hour initial reporting', 'Document all remediation steps'],
        },
        'first_run': {
            'title': 'Welcome! First Time Here?',
            'description': 'This is your first time using the NIS2 Field Audit Tool. Let\'s get you started!',
            'shortcuts': [
                '↑/↓ or Tab - Navigate menus',
                'Enter - Select / Confirm',
                'Esc - Go back / Cancel',
                'F1 - Show this help',
                '? - Keyboard shortcuts',
                'Space - Toggle checkboxes',
            ],
            'tips': [
                'Follow the onboarding wizard to set up your preferences',
                'Choose a theme that works best for your eyes',
                'Enable accessibility options if needed',
                'Press F1 anytime for context-sensitive help',
                'Your work auto-saves every 5 minutes',
            ],
        },
        'onboarding_wizard': {
            'title': 'Onboarding Wizard',
            'description': 'This wizard helps you set up the application for the first time.',
            'shortcuts': [
                '→ or Space - Next step',
                '← - Previous step',
                'Esc - Skip tutorial',
                'Tab - Navigate options',
                'Space - Select radio button or toggle checkbox',
            ],
            'tips': [
                'High contrast mode is great for bright environments',
                'Large text mode helps if you\'re sitting far from the screen',
                'You can change these settings anytime in the menu',
                'Skip the tutorial if you\'re already familiar with the tool',
            ],
        },
        'dashboard': {
            'title': 'Dashboard',
            'description': 'Your home screen showing recent audits and quick actions.',
            'shortcuts': [
                'N - New audit session',
                'D - View devices',
                'S - Scan network',
                'C - Compliance checklist',
                'F - Findings',
                'R - Reports',
                'F1 - Help',
                '? - Shortcuts',
            ],
            'tips': [
                'Start by creating a new audit session (press N)',
                'Add devices to scan before running compliance checks',
                'Your recent sessions appear here for quick access',
            ],
        },
    }
    
    def __init__(self):
        self._current_context = 'main_menu'
    
    def set_context(self, context: str) -> None:
        """Set current help context."""
        self._current_context = context
    
    def get_help(self, context: str = None) -> Dict[str, Any]:
        """Get help content for current or specified context."""
        topic = context or self._current_context
        return self.HELP_TOPICS.get(topic, {
            'title': 'Help',
            'description': 'No specific help available for this screen.',
            'shortcuts': ['? - Toggle help', 'Esc - Close help'],
        })
    
    def format_help_panel(self, context: str = None) -> str:
        """Format help content for display."""
        help_data = self.get_help(context)
        lines = [
            f"┌─ {help_data['title']} Help {'─' * (50 - len(help_data['title']))}┐",
            f"│ {help_data['description']:<58} │",
            "├─ Keyboard Shortcuts ─────────────────────────────────────┤",
        ]
        for shortcut in help_data.get('shortcuts', []):
            lines.append(f"│  • {shortcut:<55} │")
        
        if 'tips' in help_data:
            lines.append("├─ Tips ───────────────────────────────────────────────────┤")
            for tip in help_data['tips']:
                lines.append(f"│  💡 {tip:<54} │")
        
        lines.append("└──────────────────────────────────────────────────────────┘")
        return '\n'.join(lines)


# ============================================================================
# Pass 125: Progress Feedback System
# ============================================================================

class ProgressTracker:
    """Tracks and displays operation progress with accessibility support."""
    
    def __init__(self, total_steps: int, operation_name: str = "Operation"):
        self.total_steps = total_steps
        self.current_step = 0
        self.operation_name = operation_name
        self.start_time = time.time()
        self._cancelled = False
    
    def update(self, step: int = None, message: str = "") -> str:
        """Update progress and return formatted progress string."""
        if step is not None:
            self.current_step = step
        else:
            self.current_step += 1
        
        percentage = min(100, int((self.current_step / self.total_steps) * 100))
        elapsed = time.time() - self.start_time
        
        # Calculate ETA
        if self.current_step > 0:
            eta_seconds = (elapsed / self.current_step) * (self.total_steps - self.current_step)
            eta = f"{int(eta_seconds)}s remaining"
        else:
            eta = "calculating..."
        
        # Create progress bar
        bar_width = 30
        filled = int(bar_width * percentage / 100)
        bar = '█' * filled + '░' * (bar_width - filled)
        
        # Format for screen readers (text-based, no visual bar)
        screen_reader_format = (
            f"{self.operation_name}: {percentage}% complete, "
            f"step {self.current_step} of {self.total_steps}. {message}"
        )
        
        return {
            'visual': f"{self.operation_name}: [{bar}] {percentage}% ({self.current_step}/{self.total_steps}) - {eta}",
            'screen_reader': screen_reader_format,
            'percentage': percentage,
            'message': message,
        }
    
    def is_complete(self) -> bool:
        """Check if operation is complete."""
        return self.current_step >= self.total_steps
    
    def cancel(self) -> None:
        """Cancel the operation."""
        self._cancelled = True
    
    def is_cancelled(self) -> bool:
        """Check if operation was cancelled."""
        return self._cancelled


# ============================================================================
# Pass 126: Confirmation Dialog System
# ============================================================================

class ConfirmationDialog:
    """Provides accessible confirmation dialogs for destructive actions."""
    
    DIALOG_TYPES = {
        'delete': {
            'title': 'Confirm Deletion',
            'message': 'Are you sure you want to delete {item}? This action cannot be undone.',
            'confirm_label': 'Delete',
            'cancel_label': 'Cancel',
            'severity': 'high',
        },
        'overwrite': {
            'title': 'Confirm Overwrite',
            'message': 'File {item} already exists. Do you want to overwrite it?',
            'confirm_label': 'Overwrite',
            'cancel_label': 'Cancel',
            'severity': 'medium',
        },
        'exit_unsaved': {
            'title': 'Unsaved Changes',
            'message': 'You have unsaved changes. Do you want to save before exiting?',
            'confirm_label': 'Save & Exit',
            'cancel_label': 'Exit Without Saving',
            'alt_action': 'Cancel',
            'severity': 'medium',
        },
        'bulk_action': {
            'title': 'Confirm Bulk Action',
            'message': 'This will affect {count} items. Are you sure?',
            'confirm_label': 'Proceed',
            'cancel_label': 'Cancel',
            'severity': 'high',
        },
    }
    
    @classmethod
    def format_dialog(cls, dialog_type: str, **kwargs) -> Dict[str, str]:
        """Format a confirmation dialog."""
        template = cls.DIALOG_TYPES.get(dialog_type, cls.DIALOG_TYPES['delete'])
        
        message = template['message'].format(**kwargs)
        
        # Create visual box
        width = 60
        lines = [
            '┌' + '─' * width + '┐',
            '│' + template['title'].center(width) + '│',
            '├' + '─' * width + '┤',
        ]
        
        # Wrap message
        words = message.split()
        line = '│ '
        for word in words:
            if len(line) + len(word) + 1 > width - 1:
                lines.append(line.ljust(width) + '│')
                line = '│ ' + word + ' '
            else:
                line += word + ' '
        lines.append(line.ljust(width) + '│')
        
        lines.extend([
            '├' + '─' * width + '┤',
            f"│  [Y] {template['confirm_label']:<20}  [N] {template['cancel_label']:<20} │",
            '└' + '─' * width + '┘',
        ])
        
        return {
            'visual': '\n'.join(lines),
            'title': template['title'],
            'message': message,
            'confirm': template['confirm_label'],
            'cancel': template['cancel_label'],
            'severity': template['severity'],
        }


# ============================================================================
# Pass 127: Undo/Redo System
# ============================================================================

class UndoManager:
    """Manages undo/redo operations for user actions."""
    
    def __init__(self, max_history: int = 50):
        self._history: List[Dict[str, Any]] = []
        self._redo_stack: List[Dict[str, Any]] = []
        self._max_history = max_history
    
    def record_action(self, action_type: str, undo_callback: Callable, 
                      redo_callback: Callable, data: Dict = None) -> None:
        """Record an action that can be undone."""
        action = {
            'type': action_type,
            'timestamp': datetime.now().isoformat(),
            'undo': undo_callback,
            'redo': redo_callback,
            'data': data or {},
        }
        self._history.append(action)
        self._redo_stack.clear()  # Clear redo on new action
        
        # Limit history size
        if len(self._history) > self._max_history:
            self._history.pop(0)
    
    def can_undo(self) -> bool:
        """Check if undo is available."""
        return len(self._history) > 0
    
    def can_redo(self) -> bool:
        """Check if redo is available."""
        return len(self._redo_stack) > 0
    
    def undo(self) -> Optional[str]:
        """Undo last action."""
        if not self.can_undo():
            return None
        
        action = self._history.pop()
        try:
            action['undo'](action['data'])
            self._redo_stack.append(action)
            return f"Undone: {action['type']}"
        except Exception as e:
            logger.warning(f"Undo failed: {e}")
            return f"Undo failed: {e}"
    
    def redo(self) -> Optional[str]:
        """Redo last undone action."""
        if not self.can_redo():
            return None
        
        action = self._redo_stack.pop()
        try:
            action['redo'](action['data'])
            self._history.append(action)
            return f"Redone: {action['type']}"
        except Exception as e:
            logger.warning(f"Redo failed: {e}")
            return f"Redo failed: {e}"
    
    def get_history_summary(self) -> List[str]:
        """Get summary of recent actions."""
        return [f"{a['type']} - {a['timestamp']}" for a in reversed(self._history[-10:])]


# ============================================================================
# Pass 128: Auto-Save Functionality
# ============================================================================

class AutoSaveManager:
    """Manages auto-save functionality for data protection."""
    
    def __init__(self, save_callback: Callable, interval: int = 300):
        self._save_callback = save_callback
        self._interval = interval
        self._last_save = time.time()
        self._dirty = False
        self._enabled = True
    
    def mark_dirty(self) -> None:
        """Mark data as modified."""
        self._dirty = True
    
    def check_and_save(self) -> Optional[str]:
        """Check if auto-save is needed and perform save."""
        if not self._enabled or not self._dirty:
            return None
        
        elapsed = time.time() - self._last_save
        if elapsed >= self._interval:
            return self.save_now()
        return None
    
    def save_now(self) -> str:
        """Force immediate save."""
        try:
            self._save_callback()
            self._last_save = time.time()
            self._dirty = False
            return f"Auto-saved at {datetime.now().strftime('%H:%M:%S')}"
        except Exception as e:
            logger.error(f"Auto-save failed: {e}")
            return f"Auto-save failed: {e}"
    
    def set_enabled(self, enabled: bool) -> None:
        """Enable/disable auto-save."""
        self._enabled = enabled
    
    def get_status(self) -> Dict[str, Any]:
        """Get auto-save status."""
        return {
            'enabled': self._enabled,
            'dirty': self._dirty,
            'last_save': self._last_save,
            'next_save_in': max(0, self._interval - (time.time() - self._last_save)) if self._dirty else None,
        }


# ============================================================================
# Pass 129: Search and Filter System
# ============================================================================

class SearchFilter:
    """Provides search and filter functionality with accessibility."""
    
    def __init__(self):
        self._search_history: List[str] = []
        self._filters: Dict[str, Any] = {}
    
    def search(self, query: str, items: List[Dict], 
               fields: List[str] = None) -> List[Dict]:
        """Search items with accessibility-friendly results."""
        if not query:
            return items
        
        query_lower = query.lower()
        results = []
        
        for item in items:
            if fields:
                # Search specific fields
                searchable = ' '.join(str(item.get(f, '')) for f in fields)
            else:
                # Search all fields
                searchable = ' '.join(str(v) for v in item.values())
            
            if query_lower in searchable.lower():
                results.append(item)
        
        # Add to history
        if query not in self._search_history:
            self._search_history.insert(0, query)
            self._search_history = self._search_history[:10]  # Keep last 10
        
        return results
    
    def apply_filters(self, items: List[Dict]) -> List[Dict]:
        """Apply active filters to items."""
        results = items
        
        for field, value in self._filters.items():
            if value is not None:
                results = [item for item in results 
                          if str(item.get(field, '')).lower() == str(value).lower()]
        
        return results
    
    def set_filter(self, field: str, value: Any) -> None:
        """Set a filter."""
        self._filters[field] = value
    
    def clear_filters(self) -> None:
        """Clear all filters."""
        self._filters.clear()
    
    def format_results_summary(self, total: int, filtered: int) -> str:
        """Format accessible results summary."""
        if self._filters:
            filter_desc = ', '.join(f"{k}={v}" for k, v in self._filters.items())
            return f"Showing {filtered} of {total} results (filtered by: {filter_desc})"
        return f"Showing {filtered} of {total} results"


# ============================================================================
# Pass 130: Keyboard Navigation Helper
# ============================================================================

class KeyboardNavigation:
    """Provides enhanced keyboard navigation for accessibility."""
    
    KEYBOARD_MODES = {
        'default': {
            'up': 'up',
            'down': 'down',
            'left': 'left',
            'right': 'right',
            'select': 'enter',
            'back': 'esc',
            'help': '?',
            'search': '/',
            'quit': 'q',
        },
        'vim': {
            'up': 'k',
            'down': 'j',
            'left': 'h',
            'right': 'l',
            'select': 'enter',
            'back': 'esc',
            'help': '?',
            'search': '/',
            'quit': 'q',
        },
    }
    
    def __init__(self, mode: str = 'default'):
        self._mode = mode
        self._shortcuts = self.KEYBOARD_MODES.get(mode, self.KEYBOARD_MODES['default'])
    
    def set_mode(self, mode: str) -> None:
        """Set keyboard navigation mode."""
        self._mode = mode
        self._shortcuts = self.KEYBOARD_MODES.get(mode, self.KEYBOARD_MODES['default'])
    
    def get_shortcut(self, action: str) -> str:
        """Get shortcut key for action."""
        return self._shortcuts.get(action, '')
    
    def format_help(self) -> str:
        """Format keyboard help."""
        lines = [f"Keyboard Shortcuts ({self._mode} mode):", '-' * 30]
        for action, key in self._shortcuts.items():
            lines.append(f"  {action:12} : {key}")
        return '\n'.join(lines)


# ============================================================================
# Pass 131: Notification System
# ============================================================================

class NotificationManager:
    """Manages user notifications with accessibility support."""
    
    def __init__(self):
        self._notifications: List[Dict[str, Any]] = []
        self._max_notifications = 5
    
    def notify(self, message: str, level: str = 'info', 
               duration: int = 5, actions: Dict[str, Callable] = None) -> None:
        """Add a notification."""
        notification = {
            'id': len(self._notifications),
            'message': message,
            'level': level,  # info, success, warning, error
            'timestamp': datetime.now(),
            'duration': duration,
            'actions': actions or {},
        }
        self._notifications.insert(0, notification)
        
        # Keep only recent notifications
        self._notifications = self._notifications[:self._max_notifications]
    
    def get_notifications(self, level: str = None) -> List[Dict]:
        """Get current notifications."""
        if level:
            return [n for n in self._notifications if n['level'] == level]
        return self._notifications
    
    def format_notification(self, notification: Dict, theme_mode: ThemeMode = ThemeMode.DEFAULT) -> str:
        """Format notification for display with accessible symbols."""
        level = notification['level']
        symbol = ThemeEngine.get_symbol(level, theme_mode)
        message = notification['message']
        
        # Format with timestamp for screen readers
        time_str = notification['timestamp'].strftime('%H:%M')
        
        return f"{symbol} [{time_str}] {message}"
    
    def dismiss(self, notification_id: int) -> None:
        """Dismiss a notification."""
        self._notifications = [n for n in self._notifications if n['id'] != notification_id]
    
    def clear_all(self) -> None:
        """Clear all notifications."""
        self._notifications.clear()


# ============================================================================
# Pass 132: User Onboarding Wizard
# ============================================================================

class OnboardingWizard:
    """Guides new users through initial setup."""
    
    STEPS = [
        {
            'title': 'Welcome to NIS2 Field Audit Tool',
            'content': 'This tool helps you perform cybersecurity audits for NIS2 compliance.',
            'action': None,
        },
        {
            'title': 'Configure Your Preferences',
            'content': 'Set up your theme, accessibility options, and default settings.',
            'action': 'preferences',
        },
        {
            'title': 'Add Your First Device',
            'content': 'Add a network device to start auditing. You\'ll need IP address and credentials.',
            'action': 'add_device',
        },
        {
            'title': 'Run Your First Audit',
            'content': 'Perform a basic compliance audit to see how it works.',
            'action': 'run_audit',
        },
        {
            'title': 'You\'re Ready!',
            'content': 'Press F1 anytime for help. Use ? to see keyboard shortcuts.',
            'action': 'complete',
        },
    ]
    
    def __init__(self):
        self._current_step = 0
        self._completed = False
    
    def get_current_step(self) -> Dict[str, Any]:
        """Get current onboarding step."""
        if self._current_step < len(self.STEPS):
            step = self.STEPS[self._current_step]
            return {
                **step,
                'step_number': self._current_step + 1,
                'total_steps': len(self.STEPS),
                'is_first': self._current_step == 0,
                'is_last': self._current_step == len(self.STEPS) - 1,
            }
        return None
    
    def next_step(self) -> bool:
        """Advance to next step."""
        if self._current_step < len(self.STEPS) - 1:
            self._current_step += 1
            return True
        self._completed = True
        return False
    
    def previous_step(self) -> bool:
        """Go back to previous step."""
        if self._current_step > 0:
            self._current_step -= 1
            return True
        return False
    
    def is_completed(self) -> bool:
        """Check if onboarding is completed."""
        return self._completed
    
    def skip(self) -> None:
        """Skip onboarding."""
        self._completed = True
    
    def format_step(self, step: Dict) -> str:
        """Format step for display."""
        progress = f"Step {step['step_number']} of {step['total_steps']}"
        lines = [
            '╔' + '═' * 58 + '╗',
            '║' + step['title'].center(58) + '║',
            '╠' + '═' * 58 + '╣',
        ]
        
        # Wrap content
        words = step['content'].split()
        line = '║ '
        for word in words:
            if len(line) + len(word) + 1 > 57:
                lines.append(line.ljust(57) + '║')
                line = '║ ' + word + ' '
            else:
                line += word + ' '
        lines.append(line.ljust(57) + '║')
        
        lines.extend([
            '╠' + '═' * 58 + '╣',
            '║' + progress.center(58) + '║',
            '╚' + '═' * 58 + '╝',
        ])
        
        return '\n'.join(lines)


# ============================================================================
# Pass 133: Validation Feedback System
# ============================================================================

class ValidationFeedback:
    """Provides clear validation feedback for user inputs."""
    
    def __init__(self):
        self._errors: Dict[str, List[str]] = {}
        self._warnings: Dict[str, List[str]] = {}
    
    def add_error(self, field: str, message: str) -> None:
        """Add validation error."""
        if field not in self._errors:
            self._errors[field] = []
        self._errors[field].append(message)
    
    def add_warning(self, field: str, message: str) -> None:
        """Add validation warning."""
        if field not in self._warnings:
            self._warnings[field] = []
        self._warnings[field].append(message)
    
    def clear(self) -> None:
        """Clear all validation messages."""
        self._errors.clear()
        self._warnings.clear()
    
    def has_errors(self) -> bool:
        """Check if there are errors."""
        return len(self._errors) > 0
    
    def has_warnings(self) -> bool:
        """Check if there are warnings."""
        return len(self._warnings) > 0
    
    def format_feedback(self, theme_mode: ThemeMode = ThemeMode.DEFAULT) -> str:
        """Format validation feedback for display."""
        lines = []
        
        if self._errors:
            error_symbol = ThemeEngine.get_symbol('error', theme_mode)
            lines.append(f"{error_symbol} Errors:")
            for field, messages in self._errors.items():
                for msg in messages:
                    lines.append(f"  • {field}: {msg}")
        
        if self._warnings:
            warning_symbol = ThemeEngine.get_symbol('warning', theme_mode)
            lines.append(f"{warning_symbol} Warnings:")
            for field, messages in self._warnings.items():
                for msg in messages:
                    lines.append(f"  • {field}: {msg}")
        
        return '\n'.join(lines) if lines else "✓ All validations passed"


# ============================================================================
# Pass 134: Audit Trail Visualization
# ============================================================================

class AuditTrailVisualizer:
    """Visualizes audit history in an accessible way."""
    
    def __init__(self, audit_entries: List[Dict] = None):
        self._entries = audit_entries or []
    
    def add_entry(self, action: str, user: str, details: str = "") -> None:
        """Add audit entry."""
        entry = {
            'timestamp': datetime.now(),
            'action': action,
            'user': user,
            'details': details,
        }
        self._entries.append(entry)
    
    def format_timeline(self, entries: int = 10) -> str:
        """Format audit trail as timeline."""
        recent = self._entries[-entries:]
        lines = ['Audit Trail:', '─' * 50]
        
        for entry in recent:
            time_str = entry['timestamp'].strftime('%Y-%m-%d %H:%M')
            lines.append(f"{time_str} | {entry['user']:<15} | {entry['action']}")
            if entry['details']:
                lines.append(f"           {entry['details']}")
        
        return '\n'.join(lines)
    
    def format_summary(self) -> str:
        """Format audit summary statistics."""
        total = len(self._entries)
        today = len([e for e in self._entries 
                    if e['timestamp'].date() == datetime.now().date()])
        
        return f"Total audit events: {total} | Today: {today}"


# ============================================================================
# Pass 135: Export Preview System
# ============================================================================

class ExportPreview:
    """Provides preview of export formats before saving."""
    
    def __init__(self):
        self._formats = {
            'json': self._preview_json,
            'csv': self._preview_csv,
            'pdf': self._preview_pdf,
            'html': self._preview_html,
        }
    
    def preview(self, data: Any, format_type: str) -> str:
        """Generate preview of export."""
        preview_func = self._formats.get(format_type, self._preview_text)
        return preview_func(data)
    
    def _preview_json(self, data: Any) -> str:
        """Preview JSON export."""
        preview = json.dumps(data, indent=2)[:500]
        return f"JSON Preview:\n{preview}\n... (truncated)"
    
    def _preview_csv(self, data: List[Dict]) -> str:
        """Preview CSV export."""
        if not data:
            return "CSV Preview: (empty data)"
        headers = list(data[0].keys())
        lines = [','.join(headers)]
        for row in data[:5]:
            lines.append(','.join(str(row.get(h, '')) for h in headers))
        if len(data) > 5:
            lines.append(f"... ({len(data) - 5} more rows)")
        return "CSV Preview:\n" + '\n'.join(lines)
    
    def _preview_pdf(self, data: Any) -> str:
        """Preview PDF export info."""
        return f"PDF Preview:\nWill generate report with {len(data) if isinstance(data, list) else 'N/A'} items"
    
    def _preview_html(self, data: Any) -> str:
        """Preview HTML export."""
        return f"HTML Preview:\nWill generate styled HTML report with tables and charts"
    
    def _preview_text(self, data: Any) -> str:
        """Default text preview."""
        return f"Preview:\n{str(data)[:500]}"


# ============================================================================
# Pass 136: Batch Operation Manager
# ============================================================================

class BatchOperationManager:
    """Manages batch operations with progress tracking."""
    
    def __init__(self):
        self._operations: List[Dict] = []
        self._results: List[Dict] = []
    
    def add_operation(self, name: str, callback: Callable, 
                      items: List[Any]) -> None:
        """Add batch operation."""
        self._operations.append({
            'name': name,
            'callback': callback,
            'items': items,
            'total': len(items),
        })
    
    def execute(self) -> Iterator[Dict]:
        """Execute batch operations with progress updates."""
        for op in self._operations:
            tracker = ProgressTracker(op['total'], op['name'])
            
            for i, item in enumerate(op['items']):
                try:
                    result = op['callback'](item)
                    self._results.append({
                        'item': item,
                        'success': True,
                        'result': result,
                    })
                except Exception as e:
                    self._results.append({
                        'item': item,
                        'success': False,
                        'error': str(e),
                    })
                
                yield tracker.update(i + 1)
    
    def get_summary(self) -> Dict[str, int]:
        """Get batch operation summary."""
        successful = len([r for r in self._results if r['success']])
        failed = len([r for r in self._results if not r['success']])
        return {
            'total': len(self._results),
            'successful': successful,
            'failed': failed,
        }


# ============================================================================
# Pass 137: Data Backup and Restore
# ============================================================================

class BackupManager:
    """Manages data backup and restore operations."""
    
    def __init__(self, backup_dir: str = None):
        self.backup_dir = Path(backup_dir or Path.home() / ".nis2-audit/backups")
        self.backup_dir.mkdir(parents=True, exist_ok=True)
    
    def create_backup(self, data: Dict, name: str = None) -> str:
        """Create backup with timestamp."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        name = name or f"backup_{timestamp}"
        filename = f"{name}.json"
        filepath = self.backup_dir / filename
        
        backup_data = {
            'timestamp': timestamp,
            'name': name,
            'data': data,
        }
        
        try:
            with open(filepath, 'w') as f:
                json.dump(backup_data, f, indent=2)
            return str(filepath)
        except (OSError, IOError) as e:
            logger.error(f"Failed to create backup: {e}")
            raise BackupError(f"Failed to create backup: {e}")
    
    def list_backups(self) -> List[Dict]:
        """List available backups."""
        backups = []
        for filepath in self.backup_dir.glob('*.json'):
            try:
                with open(filepath, 'r') as f:
                    data = json.load(f)
                    backups.append({
                        'filename': filepath.name,
                        'timestamp': data.get('timestamp', 'unknown'),
                        'name': data.get('name', filepath.name),
                    })
            except json.JSONDecodeError:
                continue
        return sorted(backups, key=lambda x: x['timestamp'], reverse=True)
    
    def restore_backup(self, filename: str) -> Dict:
        """Restore backup from file."""
        filepath = self.backup_dir / filename
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
                return data.get('data', {})
        except (OSError, IOError, json.JSONDecodeError) as e:
            logger.error(f"Failed to restore backup {filename}: {e}")
            raise BackupError(f"Failed to restore backup: {e}")


# ============================================================================
# Pass 138: Error Recovery System
# ============================================================================

class ErrorRecovery:
    """Provides graceful error recovery and user guidance."""
    
    ERROR_GUIDANCE = {
        'connection_failed': {
            'message': 'Could not connect to device.',
            'steps': [
                'Check if the device is powered on',
                'Verify network connectivity',
                'Confirm IP address is correct',
                'Check firewall settings',
            ],
        },
        'authentication_failed': {
            'message': 'Login credentials rejected.',
            'steps': [
                'Verify username and password',
                'Check if account is locked',
                'Confirm SSH key is properly configured',
                'Try accessing via alternative method',
            ],
        },
        'permission_denied': {
            'message': 'Insufficient permissions.',
            'steps': [
                'Run with elevated privileges if needed',
                'Check file/directory permissions',
                'Verify user is in required groups',
            ],
        },
        'timeout': {
            'message': 'Operation timed out.',
            'steps': [
                'Check network stability',
                'Increase timeout settings',
                'Try during off-peak hours',
                'Check for network congestion',
            ],
        },
    }
    
    @classmethod
    def get_recovery_steps(cls, error_type: str) -> Dict[str, Any]:
        """Get recovery guidance for error type."""
        return cls.ERROR_GUIDANCE.get(error_type, {
            'message': 'An unexpected error occurred.',
            'steps': ['Check logs for details', 'Try the operation again', 'Contact support if issue persists'],
        })
    
    @classmethod
    def format_recovery(cls, error_type: str) -> str:
        """Format recovery guidance."""
        guidance = cls.get_recovery_steps(error_type)
        lines = [
            f"Error: {guidance['message']}",
            'Recovery steps:',
        ]
        for i, step in enumerate(guidance['steps'], 1):
            lines.append(f"  {i}. {step}")
        return '\n'.join(lines)


# ============================================================================
# Pass 139: Screen Reader Support
# ============================================================================

class ScreenReaderSupport:
    """Provides screen reader friendly output formatting."""
    
    @staticmethod
    def format_heading(text: str, level: int = 1) -> str:
        """Format heading with screen reader markers."""
        prefix = f"Heading level {level}: "
        return f"{prefix}{text}"
    
    @staticmethod
    def format_list(items: List[str], list_type: str = 'bullet') -> str:
        """Format list with screen reader markers."""
        lines = []
        for i, item in enumerate(items, 1):
            if list_type == 'numbered':
                lines.append(f"{i} of {len(items)}: {item}")
            else:
                lines.append(f"• {item}")
        return '\n'.join(lines)
    
    @staticmethod
    def format_table(headers: List[str], rows: List[List[str]]) -> str:
        """Format table in screen reader friendly way."""
        lines = ['Table:']
        for i, row in enumerate(rows, 1):
            lines.append(f"Row {i}:")
            for header, cell in zip(headers, row):
                lines.append(f"  {header}: {cell}")
        return '\n'.join(lines)
    
    @staticmethod
    def announce_change(message: str) -> str:
        """Announce dynamic content change."""
        return f"[Update] {message}"


# ============================================================================
# Pass 140: Configuration Wizard
# ============================================================================

class ConfigurationWizard:
    """Interactive configuration setup wizard."""
    
    STEPS = [
        {
            'id': 'company_info',
            'title': 'Company Information',
            'fields': [
                {'name': 'company_name', 'label': 'Company Name', 'type': 'text', 'required': True},
                {'name': 'sector', 'label': 'Sector', 'type': 'choice',
                 'options': ['Energy', 'Transport', 'Banking', 'Health', 'Digital', 'Other']},
                {'name': 'entity_type', 'label': 'Entity Type', 'type': 'choice',
                 'options': ['Essential', 'Important']},
            ],
        },
        {
            'id': 'audit_settings',
            'title': 'Audit Settings',
            'fields': [
                {'name': 'audit_frequency', 'label': 'Audit Frequency', 'type': 'choice',
                 'options': ['Daily', 'Weekly', 'Monthly', 'Quarterly']},
                {'name': 'auto_report', 'label': 'Auto-generate Reports', 'type': 'boolean'},
                {'name': 'report_recipients', 'label': 'Report Recipients', 'type': 'text'},
            ],
        },
        {
            'id': 'compliance_framework',
            'title': 'Compliance Framework',
            'fields': [
                {'name': 'framework', 'label': 'Primary Framework', 'type': 'choice',
                 'options': ['NIS2', 'ISO27001', 'NIST', 'Custom']},
                {'name': 'risk_threshold', 'label': 'Risk Threshold', 'type': 'choice',
                 'options': ['Low', 'Medium', 'High']},
            ],
        },
    ]
    
    def __init__(self):
        self._current_step = 0
        self._data = {}
    
    def get_current_step(self) -> Dict:
        """Get current wizard step."""
        if self._current_step < len(self.STEPS):
            return {
                **self.STEPS[self._current_step],
                'step_number': self._current_step + 1,
                'total_steps': len(self.STEPS),
                'progress': int((self._current_step / len(self.STEPS)) * 100),
            }
        return None
    
    def set_field_value(self, field_name: str, value: Any) -> None:
        """Set field value."""
        step_id = self.STEPS[self._current_step]['id']
        if step_id not in self._data:
            self._data[step_id] = {}
        self._data[step_id][field_name] = value
    
    def next_step(self) -> bool:
        """Advance to next step."""
        if self._current_step < len(self.STEPS) - 1:
            self._current_step += 1
            return True
        return False
    
    def previous_step(self) -> bool:
        """Go back to previous step."""
        if self._current_step > 0:
            self._current_step -= 1
            return True
        return False
    
    def get_configuration(self) -> Dict[str, Any]:
        """Get completed configuration."""
        return self._data


# ============================================================================
# Pass 141: Quick Action Shortcuts
# ============================================================================

class QuickActions:
    """Provides quick action shortcuts for common tasks."""
    
    ACTIONS = {
        'F1': {'name': 'Help', 'description': 'Show help for current screen'},
        'F2': {'name': 'Save', 'description': 'Save current work'},
        'F3': {'name': 'Search', 'description': 'Open search dialog'},
        'F4': {'name': 'Filter', 'description': 'Apply filters to current view'},
        'F5': {'name': 'Refresh', 'description': 'Refresh data'},
        'F6': {'name': 'Export', 'description': 'Export current view'},
        'F7': {'name': 'New', 'description': 'Create new item'},
        'F8': {'name': 'Delete', 'description': 'Delete selected item'},
        'F9': {'name': 'Settings', 'description': 'Open settings'},
        'F10': {'name': 'Menu', 'description': 'Open main menu'},
        '?': {'name': 'Shortcuts', 'description': 'Show keyboard shortcuts'},
        'Ctrl+Q': {'name': 'Quit', 'description': 'Exit application'},
        'Ctrl+Z': {'name': 'Undo', 'description': 'Undo last action'},
        'Ctrl+Y': {'name': 'Redo', 'description': 'Redo last undone action'},
    }
    
    @classmethod
    def get_action(cls, key: str) -> Optional[Dict[str, str]]:
        """Get action by key."""
        return cls.ACTIONS.get(key)
    
    @classmethod
    def format_cheatsheet(cls) -> str:
        """Format quick reference cheatsheet."""
        lines = ['Quick Actions Reference:', '─' * 40]
        for key, action in cls.ACTIONS.items():
            lines.append(f"  {key:<10} {action['name']:<12} - {action['description']}")
        return '\n'.join(lines)


# ============================================================================
# Pass 142: User Feedback Collector
# ============================================================================

class FeedbackCollector:
    """Collects and manages user feedback."""
    
    def __init__(self, storage_path: str = None):
        self.storage_path = Path(storage_path or Path.home() / ".nis2-audit/feedback.json")
        self._feedback = []
        self._load()
    
    def _load(self) -> None:
        """Load existing feedback."""
        if self.storage_path.exists():
            try:
                with open(self.storage_path, 'r') as f:
                    self._feedback = json.load(f)
            except json.JSONDecodeError:
                self._feedback = []
    
    def submit_feedback(self, category: str, message: str, 
                        rating: int = None, context: str = "") -> None:
        """Submit user feedback."""
        feedback = {
            'timestamp': datetime.now().isoformat(),
            'category': category,  # bug, feature, usability, other
            'message': message,
            'rating': rating,
            'context': context,
        }
        self._feedback.append(feedback)
        self._save()
    
    def _save(self) -> None:
        """Save feedback to disk."""
        try:
            self.storage_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.storage_path, 'w') as f:
                json.dump(self._feedback, f, indent=2)
        except (OSError, IOError) as e:
            logger.warning(f"Failed to save feedback: {e}")
    
    def get_statistics(self) -> Dict[str, int]:
        """Get feedback statistics."""
        categories = {}
        for f in self._feedback:
            cat = f['category']
            categories[cat] = categories.get(cat, 0) + 1
        return categories
    
    def format_feedback_summary(self) -> str:
        """Format feedback summary."""
        stats = self.get_statistics()
        lines = ['Your Feedback History:', '─' * 30]
        for cat, count in stats.items():
            lines.append(f"  {cat.capitalize()}: {count} items")
        lines.append(f"\nTotal feedback submitted: {len(self._feedback)}")
        return '\n'.join(lines)


# Export all classes
__all__ = [
    'UserPreferences',
    'PreferenceManager',
    'ThemeMode',
    'ThemeEngine',
    'HelpSystem',
    'ProgressTracker',
    'ConfirmationDialog',
    'UndoManager',
    'AutoSaveManager',
    'SearchFilter',
    'KeyboardNavigation',
    'NotificationManager',
    'OnboardingWizard',
    'ValidationFeedback',
    'AuditTrailVisualizer',
    'ExportPreview',
    'BatchOperationManager',
    'BackupManager',
    'ErrorRecovery',
    'ScreenReaderSupport',
    'ConfigurationWizard',
    'QuickActions',
    'FeedbackCollector',
]
