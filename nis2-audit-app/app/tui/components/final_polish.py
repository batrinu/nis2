"""
Final Polish & Micro-Interactions - Loop 19-21
Last details, microcopy, and delightful touches.
"""
from textual.widgets import Static, Button
from textual.containers import Vertical, Horizontal
from textual.reactive import reactive
from textual.timer import Timer
import random
from datetime import datetime
from typing import List, Optional


# Microcopy - helpful small text throughout the app
MICROCOPY = {
    "form": {
        "entity_name_placeholder": "e.g., Acme Energy Corporation SRL",
        "network_placeholder": "e.g., 192.168.1.0/24",
        "email_placeholder": "your.email@company.com",
        "required_hint": "* Required fields",
        "save_hint": "💾 Auto-saves every 30 seconds",
        "validation_hint": "✓ Field looks good!",
    },
    "buttons": {
        "next": "Next ▶",
        "next_hint": "Continue to next step",
        "back": "◀ Back",
        "back_hint": "Return to previous step",
        "cancel": "Cancel",
        "cancel_hint": "Discard changes and exit",
        "save": "💾 Save",
        "save_hint": "Save your progress",
        "scan": "🔍 Start Scan",
        "scan_hint": "Begin network discovery",
        "generate": "📄 Generate Report",
        "generate_hint": "Create compliance report",
    },
    "tooltips": {
        "dashboard_new": "Create a new audit session (N)",
        "dashboard_refresh": "Refresh the session list (R)",
        "scan_range": "Enter network range like 192.168.1.0/24",
        "checklist_yes": "Fully implemented",
        "checklist_no": "Not implemented",
        "checklist_partial": "Partially implemented",
        "checklist_na": "Not applicable",
    },
    "loading": [
        "Initializing...",
        "Loading resources...",
        "Preparing workspace...",
        "Almost there...",
        "Finalizing...",
    ],
    "success": [
        "✓ Done!",
        "✓ Success!",
        "✓ Completed!",
        "✓ All set!",
    ],
    "encouragement": [
        "You're doing great!",
        "Keep it up!",
        "Making good progress!",
        "Almost there!",
        "Looking good!",
    ],
}

# Easter eggs and fun messages
EASTER_EGGS = {
    "boot_messages": [
        "Initializing quantum entanglement...",
        "Calibrating flux capacitor...",
        "Reticulating splines...",
        "Consulting the Oracle...",
        "Brewing coffee...",
        "Teaching hamsters to run faster...",
        "Untangling the web...",
        "Polishing pixels...",
        "Feeding the digital hamsters...",
        "Aligning cyber-chakras...",
    ],
    "completion_messages": [
        "Mission accomplished! 🚀",
        "Another one bites the dust! 🎸",
        "You shall pass! ✓",
        "To infinity and beyond! 🚀",
        "Houston, we have compliance! 🛰️",
    ],
    "friday_messages": [
        "It's Friday! Time to secure some networks! 🎉",
        "Friday audit mode: activated! 🔥",
        "Weekend's coming, let's finish strong! 💪",
    ],
}


class MicrocopyManager:
    """Manager for contextual microcopy."""
    
    def __init__(self):
        self.context = {}
    
    def get(self, key: str, category: str = "form") -> str:
        """Get microcopy for a key."""
        return MICROCOPY.get(category, {}).get(key, "")
    
    def get_random(self, category: str) -> str:
        """Get random message from category."""
        messages = MICROCOPY.get(category, [])
        if messages:
            return random.choice(messages)
        return ""
    
    def get_placeholder(self, field_type: str) -> str:
        """Get placeholder text for field type."""
        placeholders = {
            "entity_name": MICROCOPY["form"]["entity_name_placeholder"],
            "network": MICROCOPY["form"]["network_placeholder"],
            "email": MICROCOPY["form"]["email_placeholder"],
        }
        return placeholders.get(field_type, "Enter value...")


class DelightfulLoader(Static):
    """Loading indicator with changing messages."""
    
    DEFAULT_CSS = """
    DelightfulLoader {
        text-align: center;
        color: $primary;
    }
    """
    
    MESSAGES = [
        "Initializing...",
        "Gathering data...",
        "Analyzing patterns...",
        "Almost there...",
        "Finalizing...",
    ]
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._message_index = 0
        self._frame = 0
    
    def on_mount(self):
        """Start animation."""
        self.set_interval(2, self._change_message)
        self.set_interval(0.1, self._animate)
    
    def _change_message(self):
        """Cycle through messages."""
        self._message_index = (self._message_index + 1) % len(self.MESSAGES)
        self._update_display()
    
    def _animate(self):
        """Animate loading dots."""
        self._frame = (self._frame + 1) % 4
        self._update_display()
    
    def _update_display(self):
        """Update display."""
        message = self.MESSAGES[self._message_index]
        dots = "." * self._frame
        self.update(f"⏳ {message}{dots}")


class EasterEggTrigger(Static):
    """Hidden Easter egg that triggers on specific input."""
    
    EGG_TRIGGERS = {
        "mecipt": "🖥️ Remembering MECIPT-1, Romania's first computer (1961)",
        "fortran": "💾 FORTRAN is still cool, change my mind",
        "1985": "📅 The year TIM-S computers were in every Romanian school",
        "nostalgia": "🕰️ Those were the days of punch cards and magnetic tapes...",
        "coffee": "☕ The programmer's best friend",
    }
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._buffer = ""
    
    def on_key(self, event):
        """Check for Easter egg triggers."""
        self._buffer += event.key.lower()
        
        # Check if any trigger matches
        for trigger, message in self.EGG_TRIGGERS.items():
            if trigger in self._buffer:
                self._show_easter_egg(message)
                self._buffer = ""
                break
        
        # Keep buffer manageable
        if len(self._buffer) > 50:
            self._buffer = self._buffer[-20:]
    
    def _show_easter_egg(self, message: str):
        """Show Easter egg message."""
        self.update(f"✨ {message} ✨")
        self.set_timer(5, lambda: self.update(""))


class ContextualEncouragement(Static):
    """Shows encouraging messages based on progress."""
    
    DEFAULT_CSS = """
    ContextualEncouragement {
        text-align: center;
        color: $success;
        text-style: italic;
        height: auto;
        margin: 1 0;
    }
    """
    
    MESSAGES = {
        0: ["Let's get started! You've got this! 💪"],
        25: ["Good start! Keep going! 🌟"],
        50: ["Halfway there! You're doing great! ⭐"],
        75: ["Almost done! Finish strong! 🔥"],
        90: ["So close! Just a bit more! 🎯"],
        100: ["Perfect! Amazing work! 🎉"],
    }
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.progress = 0
    
    def update_progress(self, progress: int):
        """Update based on progress percentage."""
        self.progress = progress
        
        # Find appropriate message bucket
        for threshold in sorted(self.MESSAGES.keys(), reverse=True):
            if progress >= threshold:
                messages = self.MESSAGES[threshold]
                self.update(random.choice(messages))
                break


class FriendlyTimeDisplay(Static):
    """Time display with friendly formatting."""
    
    DEFAULT_CSS = """
    FriendlyTimeDisplay {
        color: $text-muted;
    }
    """
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    
    def on_mount(self):
        """Update time."""
        self._update()
        self.set_interval(60, self._update)
    
    def _update(self):
        """Update friendly time."""
        now = datetime.now()
        hour = now.hour
        
        if 5 <= hour < 12:
            greeting = "morning"
        elif 12 <= hour < 17:
            greeting = "afternoon"
        elif 17 <= hour < 22:
            greeting = "evening"
        else:
            greeting = "night"
        
        # Check for special days
        weekday = now.weekday()
        if weekday == 4:  # Friday
            self.update(f"Happy Friday {greeting}! 🎉")
        elif weekday == 0:  # Monday
            self.update(f"Monday {greeting}! Fresh start! ☕")
        else:
            self.update(f"Good {greeting}! 👋")


class CompletionCelebration(Static):
    """Celebration for task completion."""
    
    DEFAULT_CSS = """
    CompletionCelebration {
        text-align: center;
        padding: 2;
        border: thick $success;
        background: $success-darken-3;
        margin: 1 0;
    }
    
    #cc-title {
        text-style: bold;
        color: $success;
        font-size: 2;
    }
    
    #cc-message {
        margin: 1 0;
        color: $text;
    }
    
    #cc-stats {
        color: $text-muted;
        text-style: italic;
    }
    """
    
    def __init__(self, title: str = "Complete!", message: str = "", stats: str = "", **kwargs):
        super().__init__(**kwargs)
        self.celebration_title = title
        self.celebration_message = message
        self.celebration_stats = stats
    
    def compose(self):
        yield Static(self.celebration_title, id="cc-title")
        if self.celebration_message:
            yield Static(self.celebration_message, id="cc-message")
        if self.celebration_stats:
            yield Static(self.celebration_stats, id="cc-stats")


class TypingIndicator(Static):
    """Indicator showing that work is happening."""
    
    DEFAULT_CSS = """
    TypingIndicator {
        color: $text-muted;
    }
    """
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._frame = 0
    
    def on_mount(self):
        """Start animation."""
        self.set_interval(0.3, self._animate)
    
    def _animate(self):
        """Animate dots."""
        dots = "." * (self._frame % 4)
        self.update(f"Working{dots}")
        self._frame += 1


class FriendlyEmptyState(Static):
    """Empty state with personality."""
    
    DEFAULT_CSS = """
    FriendlyEmptyState {
        text-align: center;
        color: $text-muted;
        padding: 4;
    }
    
    #fes-icon {
        font-size: 3;
        margin-bottom: 1;
    }
    
    #fes-title {
        text-style: bold;
        margin: 1 0;
    }
    
    #fes-hint {
        text-style: italic;
        margin-top: 1;
    }
    """
    
    STATES = {
        "no_sessions": {
            "icon": "📋",
            "title": "No sessions yet",
            "message": "Your audit sessions will appear here",
            "hint": "Press 'N' to create your first session!",
        },
        "no_results": {
            "icon": "🔍",
            "title": "No results found",
            "message": "Try adjusting your search or filters",
            "hint": "Tip: Use partial words for broader matches",
        },
        "all_done": {
            "icon": "✅",
            "title": "All caught up!",
            "message": "Nothing to do here - nice work!",
            "hint": "Take a well-deserved break ☕",
        },
    }
    
    def __init__(self, state: str, **kwargs):
        super().__init__(**kwargs)
        self.state = state
    
    def compose(self):
        info = self.STATES.get(self.state, self.STATES["no_sessions"])
        
        yield Static(info["icon"], id="fes-icon")
        yield Static(info["title"], id="fes-title")
        yield Static(info["message"])
        yield Static(info["hint"], id="fes-hint")


# Utility functions for final polish

def get_loading_message() -> str:
    """Get a random loading message."""
    return random.choice(MICROCOPY["loading"])


def get_success_message() -> str:
    """Get a random success message."""
    return random.choice(MICROCOPY["success"])


def get_encouragement() -> str:
    """Get a random encouragement message."""
    return random.choice(MICROCOPY["encouragement"])


def get_boot_message() -> str:
    """Get a random boot message (easter egg)."""
    return random.choice(EASTER_EGGS["boot_messages"])


def format_friendly_number(n: int) -> str:
    """Format number in friendly way."""
    if n == 0:
        return "none"
    elif n == 1:
        return "one"
    elif n < 10:
        return ["two", "three", "four", "five", "six", "seven", "eight", "nine"][n - 2]
    else:
        return str(n)


def get_time_greeting() -> str:
    """Get greeting based on time."""
    hour = datetime.now().hour
    
    if 5 <= hour < 12:
        return "Good morning"
    elif 12 <= hour < 17:
        return "Good afternoon"
    elif 17 <= hour < 22:
        return "Good evening"
    else:
        return "Working late"


class PolishManager:
    """Manager for all polish features."""
    
    def __init__(self):
        self.microcopy = MicrocopyManager()
        self.easter_eggs_enabled = True
    
    def enable_easter_eggs(self, enabled: bool = True):
        """Enable or disable Easter eggs."""
        self.easter_eggs_enabled = enabled
    
    def get_contextual_message(self, context: str, **kwargs) -> str:
        """Get a message appropriate for the context."""
        if context == "loading":
            return get_loading_message()
        elif context == "success":
            return get_success_message()
        elif context == "encouragement":
            return get_encouragement()
        elif context == "greeting":
            return get_time_greeting()
        else:
            return ""
