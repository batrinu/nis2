"""
Personalization & User Preferences - Loop 12
User preferences, themes, and personal touches.
"""
from textual.widgets import Static, Button, Select, Input
from textual.containers import Vertical, Horizontal
from textual.reactive import reactive
from textual.screen import ModalScreen
from typing import Dict, Any, Optional
import json
import os


# Theme definitions
THEMES = {
    "default": {
        "name": "Default",
        "description": "Clean, professional look",
        "primary": "blue",
        "background": "black",
        "accent": "cyan",
    },
    "retro": {
        "name": "Retro Green",
        "description": "Classic terminal green",
        "primary": "green",
        "background": "black",
        "accent": "bright_green",
    },
    "amber": {
        "name": "Amber Night",
        "description": "Warm amber tones",
        "primary": "dark_orange",
        "background": "black",
        "accent": "orange3",
    },
    "ocean": {
        "name": "Ocean Blue",
        "description": "Calming blue tones",
        "primary": "deep_sky_blue4",
        "background": "black",
        "accent": "sky_blue3",
    },
    "high_contrast": {
        "name": "High Contrast",
        "description": "Maximum accessibility",
        "primary": "white",
        "background": "black",
        "accent": "yellow",
    },
}

# User greeting messages based on time
TIME_GREETINGS = {
    "morning": [
        "Good morning! Ready to secure some networks?",
        "Rise and shine! Time for NIS2 compliance.",
        "Morning! Let's make some systems safer today.",
    ],
    "afternoon": [
        "Good afternoon! How's the audit going?",
        "Afternoon! Making progress on compliance?",
        "Hello! Keep up the great security work!",
    ],
    "evening": [
        "Good evening! Wrapping up for the day?",
        "Evening! Thanks for keeping systems secure.",
        "Hello! Don't forget to save your progress.",
    ],
    "night": [
        "Working late? Don't forget to take breaks!",
        "Night owl mode activated! 🦉",
        "Late night security work? You're dedicated!",
    ],
}


class UserPreferences:
    """User preferences manager."""
    
    DEFAULTS = {
        "theme": "default",
        "notifications_enabled": True,
        "sound_enabled": False,
        "auto_save_interval": 30,
        "confirm_destructive": True,
        "show_tips": True,
        "compact_mode": False,
        "language": "en",
        "date_format": "%Y-%m-%d",
        "timezone": "local",
        "default_network_range": "192.168.1.0/24",
        "favorite_sectors": [],
        "last_used_name": "",
        "show_welcome": True,
        "achievement_notifications": True,
    }
    
    def __init__(self):
        self._prefs: Dict[str, Any] = {}
        self._load()
    
    def _get_config_path(self) -> str:
        """Get path to preferences file."""
        config_dir = os.path.expanduser("~/.nis2-audit")
        os.makedirs(config_dir, exist_ok=True)
        return os.path.join(config_dir, "preferences.json")
    
    def _load(self):
        """Load preferences from file."""
        try:
            path = self._get_config_path()
            if os.path.exists(path):
                with open(path, 'r') as f:
                    loaded = json.load(f)
                    self._prefs = {**self.DEFAULTS, **loaded}
            else:
                self._prefs = self.DEFAULTS.copy()
        except Exception:
            self._prefs = self.DEFAULTS.copy()
    
    def save(self):
        """Save preferences to file."""
        try:
            path = self._get_config_path()
            with open(path, 'w') as f:
                json.dump(self._prefs, f, indent=2)
        except Exception:
            pass
    
    def get(self, key: str, default=None) -> Any:
        """Get preference value."""
        return self._prefs.get(key, default)
    
    def set(self, key: str, value: Any):
        """Set preference value."""
        self._prefs[key] = value
        self.save()
    
    def reset(self):
        """Reset to defaults."""
        self._prefs = self.DEFAULTS.copy()
        self.save()


class PreferencesModal(ModalScreen):
    """Modal for editing user preferences."""
    
    CSS = """
    #preferences-modal {
        width: 70;
        height: auto;
        max-height: 80%;
        border: thick $primary;
        background: $surface;
        padding: 2;
    }
    
    #prefs-title {
        text-align: center;
        text-style: bold;
        color: $primary;
        border-bottom: solid $primary;
        margin-bottom: 1;
        padding-bottom: 1;
    }
    
    #prefs-content {
        height: auto;
        overflow: auto;
    }
    
    .pref-section {
        margin: 1 0;
        height: auto;
    }
    
    .pref-label {
        text-style: bold;
        margin-bottom: 1;
    }
    
    .pref-description {
        color: $text-muted;
        text-style: italic;
        height: auto;
    }
    
    #prefs-actions {
        margin-top: 2;
        align: center middle;
        border-top: solid $surface-lighten-1;
        padding-top: 1;
    }
    """
    
    def __init__(self, preferences: UserPreferences, **kwargs):
        """Initialize preferences modal.
        
        Args:
            preferences: UserPreferences instance to edit.
            **kwargs: Additional keyword arguments passed to ModalScreen.
        """
        super().__init__(**kwargs)
        self.preferences = preferences
    
    def compose(self):
        """Compose the preferences modal with all settings."""
        with Vertical(id="preferences-modal"):
            yield Static("⚙️ User Preferences", id="prefs-title")
            
            with Vertical(id="prefs-content"):
                # Theme selection
                with Vertical(classes="pref-section"):
                    yield Static("🎨 Theme", classes="pref-label")
                    yield Static("Choose your preferred color scheme", classes="pref-description")
                    yield Select([
                        (theme["name"], key)
                        for key, theme in THEMES.items()
                    ], value=self.preferences.get("theme"), id="pref-theme")
                
                # Notifications
                with Vertical(classes="pref-section"):
                    yield Static("🔔 Notifications", classes="pref-label")
                    yield Static("Enable notification popups", classes="pref-description")
                    # Would use Switch if available, or Button toggle
                
                # Auto-save
                with Vertical(classes="pref-section"):
                    yield Static("💾 Auto-Save", classes="pref-label")
                    yield Static("Minutes between auto-saves (0 to disable)", classes="pref-description")
                    yield Input(
                        value=str(self.preferences.get("auto_save_interval")),
                        id="pref-autosave"
                    )
                
                # Confirmation dialogs
                with Vertical(classes="pref-section"):
                    yield Static("⚠️ Safety", classes="pref-label")
                    yield Static("Confirm before destructive actions", classes="pref-description")
                    # Would use Switch
                
                # Default network
                with Vertical(classes="pref-section"):
                    yield Static("🌐 Default Network", classes="pref-label")
                    yield Static("Default network range for scans", classes="pref-description")
                    yield Input(
                        value=self.preferences.get("default_network_range"),
                        id="pref-network"
                    )
                
                # Tips
                with Vertical(classes="pref-section"):
                    yield Static("💡 Tips", classes="pref-label")
                    yield Static("Show helpful tips throughout the app", classes="pref-description")
                    # Would use Switch
            
            with Horizontal(id="prefs-actions"):
                yield Button("Cancel", id="btn-cancel")
                yield Button("Save", variant="primary", id="btn-save")
                yield Button("Reset to Defaults", variant="error", id="btn-reset")
    
    def on_button_pressed(self, event):
        """Handle button presses."""
        if event.button.id == "btn-cancel":
            self.dismiss()
        elif event.button.id == "btn-save":
            self._save_preferences()
            self.dismiss("saved")
        elif event.button.id == "btn-reset":
            self.preferences.reset()
            self.dismiss("reset")
    
    def _save_preferences(self):
        """Save current preferences."""
        try:
            theme = self.query_one("#pref-theme", Select).value
            if theme:
                self.preferences.set("theme", theme)
            
            auto_save = self.query_one("#pref-autosave", Input).value
            try:
                self.preferences.set("auto_save_interval", int(auto_save))
            except ValueError:
                pass
            
            network = self.query_one("#pref-network", Input).value
            self.preferences.set("default_network_range", network)
        except Exception:
            pass


class PersonalizedGreeting(Static):
    """Greeting that adapts to time of day."""
    
    DEFAULT_CSS = """
    PersonalizedGreeting {
        height: auto;
        text-align: center;
        color: $primary;
        text-style: italic;
        margin: 1 0;
    }
    """
    
    def __init__(self, user_name: str = "", **kwargs):
        """Initialize personalized greeting widget.
        
        Args:
            user_name: Name of the user to include in greeting.
            **kwargs: Additional keyword arguments passed to Static.
        """
        super().__init__(**kwargs)
        self.user_name = user_name
    
    def on_mount(self):
        """Set greeting based on time of day when widget is mounted."""
        from datetime import datetime
        import random
        
        hour = datetime.now().hour
        
        if 5 <= hour < 12:
            time_key = "morning"
        elif 12 <= hour < 17:
            time_key = "afternoon"
        elif 17 <= hour < 22:
            time_key = "evening"
        else:
            time_key = "night"
        
        greeting = random.choice(TIME_GREETINGS[time_key])
        
        if self.user_name:
            greeting = f"Hello {self.user_name}! {greeting}"
        
        self.update(greeting)


class UserStats(Static):
    """Display user statistics and progress."""
    
    DEFAULT_CSS = """
    UserStats {
        height: auto;
        border: solid $surface-lighten-1;
        background: $surface-darken-1;
        padding: 1;
        margin: 1 0;
    }
    
    #stats-title {
        text-style: bold;
        color: $primary;
        text-align: center;
        border-bottom: solid $surface-lighten-1;
        margin-bottom: 1;
    }
    
    .stat-row {
        height: auto;
        margin: 0 1;
    }
    
    .stat-label {
        width: 25;
        color: $text-muted;
    }
    
    .stat-value {
        color: $text;
        text-style: bold;
    }
    """
    
    def __init__(self, stats: Dict[str, Any], **kwargs):
        """Initialize user stats widget.
        
        Args:
            stats: Dictionary of stat labels and values to display.
            **kwargs: Additional keyword arguments passed to Static.
        """
        super().__init__(**kwargs)
        self.stats = stats
    
    def compose(self):
        """Compose the stats display with all stat rows."""
        yield Static("📊 Your Stats", id="stats-title")
        
        for label, value in self.stats.items():
            with Horizontal(classes="stat-row"):
                yield Static(f"{label}:", classes="stat-label")
                yield Static(str(value), classes="stat-value")


class ThemePreview(Static):
    """Preview of a color theme."""
    
    DEFAULT_CSS = """
    ThemePreview {
        width: 30;
        height: auto;
        border: solid $surface-lighten-1;
        padding: 1;
        margin: 0 1;
    }
    
    ThemePreview.selected {
        border: thick $primary;
    }
    
    #theme-name {
        text-style: bold;
        text-align: center;
        margin-bottom: 1;
    }
    
    #theme-desc {
        color: $text-muted;
        text-style: italic;
        text-align: center;
        height: auto;
        margin-bottom: 1;
    }
    
    .theme-sample {
        height: 1;
        margin: 1 0;
    }
    """
    
    def __init__(self, theme_key: str, **kwargs):
        """Initialize theme preview widget.
        
        Args:
            theme_key: Key of the theme to preview.
            **kwargs: Additional keyword arguments passed to Static.
        """
        super().__init__(**kwargs)
        self.theme_key = theme_key
        self.theme = THEMES.get(theme_key, THEMES["default"])
    
    def compose(self):
        """Compose the theme preview with color samples."""
        yield Static(self.theme["name"], id="theme-name")
        yield Static(self.theme["description"], id="theme-desc")
        
        # Color samples
        yield Static("Primary", classes="theme-sample primary")
        yield Static("Accent", classes="theme-sample accent")
        yield Static("Text", classes="theme-sample text")


class WelcomeBackMessage(Static):
    """Welcome message for returning users."""
    
    DEFAULT_CSS = """
    WelcomeBackMessage {
        height: auto;
        text-align: center;
        padding: 2;
        border: solid $success;
        background: $success-darken-3;
        margin: 1 0;
    }
    
    #wb-title {
        text-style: bold;
        color: $success;
        font-size: 2;
        margin-bottom: 1;
    }
    
    #wb-message {
        color: $text;
    }
    """
    
    def __init__(self, last_session: str = "", **kwargs):
        """Initialize welcome back message widget.
        
        Args:
            last_session: Name of the last session for personalized message.
            **kwargs: Additional keyword arguments passed to Static.
        """
        super().__init__(**kwargs)
        self.last_session = last_session
    
    def compose(self):
        """Compose the welcome back message display."""
        yield Static("👋 Welcome Back!", id="wb-title")
        
        if self.last_session:
            message = f"Ready to continue with '{self.last_session}'?"
        else:
            message = "Ready to continue your NIS2 compliance journey?"
        
        yield Static(message, id="wb-message")


# User progress tracking

class UserProgress:
    """Track user progress and statistics."""
    
    def __init__(self):
        self._progress = {}
        self._load()
    
    def _get_progress_path(self) -> str:
        """Get path to progress file."""
        config_dir = os.path.expanduser("~/.nis2-audit")
        os.makedirs(config_dir, exist_ok=True)
        return os.path.join(config_dir, "progress.json")
    
    def _load(self):
        """Load progress from file."""
        try:
            path = self._get_progress_path()
            if os.path.exists(path):
                with open(path, 'r') as f:
                    self._progress = json.load(f)
        except Exception:
            self._progress = {}
    
    def save(self):
        """Save progress to file."""
        try:
            path = self._get_progress_path()
            with open(path, 'w') as f:
                json.dump(self._progress, f, indent=2)
        except Exception:
            pass
    
    def increment(self, key: str, amount: int = 1):
        """Increment a counter."""
        self._progress[key] = self._progress.get(key, 0) + amount
        self.save()
    
    def set(self, key: str, value: Any):
        """Set a value."""
        self._progress[key] = value
        self.save()
    
    def get(self, key: str, default=None):
        """Get a value."""
        return self._progress.get(key, default)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get user statistics for display."""
        return {
            "Sessions Created": self._progress.get("sessions_created", 0),
            "Scans Completed": self._progress.get("scans_completed", 0),
            "Devices Discovered": self._progress.get("devices_discovered", 0),
            "Checklists Completed": self._progress.get("checklists_completed", 0),
            "Reports Generated": self._progress.get("reports_generated", 0),
            "Total Audit Time": f"{self._progress.get('audit_time_minutes', 0)} min",
        }


def get_time_based_greeting() -> str:
    """Get a greeting based on time of day."""
    from datetime import datetime
    import random
    
    hour = datetime.now().hour
    
    if 5 <= hour < 12:
        return random.choice(TIME_GREETINGS["morning"])
    elif 12 <= hour < 17:
        return random.choice(TIME_GREETINGS["afternoon"])
    elif 17 <= hour < 22:
        return random.choice(TIME_GREETINGS["evening"])
    else:
        return random.choice(TIME_GREETINGS["night"])
