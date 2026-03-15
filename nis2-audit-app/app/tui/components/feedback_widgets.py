"""
Visual Feedback Widgets - Loop 5
Success animations, error effects, loading states, and hover effects.
"""
from textual.widgets import Static, Button
from textual.containers import Container
from textual.reactive import reactive
from textual.timer import Timer
import asyncio
from typing import Optional, List


class SuccessCheckmark(Static):
    """Animated success checkmark."""
    
    DEFAULT_CSS = """
    SuccessCheckmark {
        width: auto;
        height: auto;
        text-align: center;
        color: $success;
    }
    """
    
    # Animation frames for checkmark
    FRAMES = [
        "    \n    \n    ",
        "    \n  ✓ \n    ",
        " ╱  \n  ✓ \n    ",
        " ╱╲ \n  ✓ \n    ",
        " ╱╲ \n ╱✓ \n    ",
        " ╱╲ \n ╱✓╲\n    ",
        " ╱╲ \n ╱✓╲\n╱   ",
        " ╱╲ \n ╱✓╲\n╱  ╲",
        "✓",
    ]
    
    def __init__(self, text: str = "Success!", **kwargs):
        super().__init__(**kwargs)
        self.text = text
        self._frame = 0
    
    def on_mount(self):
        """Start animation."""
        self._animate()
    
    def _animate(self):
        """Animate checkmark."""
        if self._frame < len(self.FRAMES):
            self.update(self.FRAMES[self._frame])
            self._frame += 1
            self.set_timer(0.05, self._animate)
        else:
            self.update(f"✓ {self.text}")
            # Pulse effect after completion
            self.set_timer(0.5, self._pulse)
    
    def _pulse(self):
        """Pulse animation."""
        self.styles.animate("opacity", 0.5, duration=0.3)
        self.set_timer(0.3, lambda: self.styles.animate("opacity", 1.0, duration=0.3))


class ErrorShake(Static):
    """Error message with shake animation."""
    
    DEFAULT_CSS = """
    ErrorShake {
        width: auto;
        height: auto;
        text-align: center;
        color: $error;
        text-style: bold;
    }
    """
    
    # Shake offset patterns
    SHAKES = [0, 1, -1, 2, -2, 1, -1, 0]
    
    def __init__(self, message: str = "Error!", **kwargs):
        super().__init__(**kwargs)
        self.message = message
        self._shake_index = 0
    
    def on_mount(self):
        """Start shake animation."""
        self._shake()
    
    def _shake(self):
        """Perform shake animation."""
        if self._shake_index < len(self.SHAKES):
            offset = self.SHAKES[self._shake_index]
            spaces = " " * abs(offset) if offset >= 0 else " " * abs(offset)
            self.update(f"{spaces}✗ {self.message}")
            self._shake_index += 1
            self.set_timer(0.05, self._shake)
        else:
            self.update(f"✗ {self.message}")


class LoadingSpinner(Static):
    """Animated loading spinner with progress text."""
    
    DEFAULT_CSS = """
    LoadingSpinner {
        width: auto;
        height: auto;
        text-align: center;
        color: $primary;
    }
    """
    
    FRAMES = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
    
    def __init__(self, text: str = "Loading", show_dots: bool = True, **kwargs):
        super().__init__(**kwargs)
        self.base_text = text
        self.show_dots = show_dots
        self._frame = 0
        self._timer: Optional[Timer] = None
    
    def on_mount(self):
        """Start animation."""
        self._timer = self.set_interval(0.1, self._animate)
    
    def _animate(self):
        """Update spinner frame."""
        frame = self.FRAMES[self._frame % len(self.FRAMES)]
        dots = "." * (self._frame % 4) if self.show_dots else ""
        self.update(f"{frame} {self.base_text}{dots}")
        self._frame += 1
    
    def stop(self, final_message: str = "✓ Done"):
        """Stop spinner with final message."""
        if self._timer:
            self._timer.stop()
        self.update(final_message)


class ProgressIndicator(Static):
    """Progress bar with percentage and ETA."""
    
    DEFAULT_CSS = """
    ProgressIndicator {
        width: 100%;
        height: auto;
        padding: 1;
    }
    
    #progress-bar {
        width: 100%;
        height: 1;
        background: $surface-darken-1;
    }
    
    #progress-fill {
        width: 0%;
        height: 100%;
        background: $primary;
    }
    
    #progress-text {
        text-align: center;
        margin-top: 1;
    }
    
    #progress-eta {
        text-align: center;
        color: $text-muted;
        text-style: italic;
    }
    """
    
    progress = reactive(0)
    eta_seconds = reactive(0)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.start_time = None
    
    def compose(self):
        yield Static("", id="progress-bar")
        yield Static("0%", id="progress-text")
        yield Static("", id="progress-eta")
    
    def watch_progress(self, value: int):
        """Update progress display."""
        try:
            bar = self.query_one("#progress-bar", Static)
            text = self.query_one("#progress-text", Static)
            
            filled = int(value / 100 * 30)  # 30 chars wide
            bar_text = "█" * filled + "░" * (30 - filled)
            bar.update(f"[{bar_text}]")
            text.update(f"{value}%")
        except Exception:
            pass
    
    def update_eta(self, remaining_seconds: int):
        """Update ETA display."""
        try:
            eta_text = self.query_one("#progress-eta", Static)
            if remaining_seconds < 60:
                eta_text.update(f"About {remaining_seconds} seconds remaining")
            elif remaining_seconds < 3600:
                eta_text.update(f"About {remaining_seconds // 60} minutes remaining")
            else:
                hours = remaining_seconds // 3600
                mins = (remaining_seconds % 3600) // 60
                eta_text.update(f"About {hours}h {mins}m remaining")
        except Exception:
            pass


class HoverButton(Button):
    """Button with enhanced hover effects."""
    
    DEFAULT_CSS = """
    HoverButton {
        transition: background 0.2s, color 0.2s, border 0.2s;
    }
    
    HoverButton:hover {
        text-style: bold;
        border: double $primary-lighten-2;
    }
    
    HoverButton:focus {
        border: double $primary;
    }
    """
    
    def __init__(self, label: str, shortcut: str = "", help_text: str = "", **kwargs):
        super().__init__(label, **kwargs)
        self.shortcut = shortcut
        self.help_text = help_text
        
        # Add shortcut hint to label
        if shortcut:
            self.label = f"{label} [{shortcut}]"
    
    def on_enter(self):
        """Show help text on hover."""
        if self.help_text:
            # Could emit a message to show in status bar
            pass


class PulseRing(Static):
    """Pulsing ring for drawing attention."""
    
    DEFAULT_CSS = """
    PulseRing {
        width: auto;
        height: auto;
        text-align: center;
        color: $warning;
    }
    """
    
    FRAMES = [
        " ○ ",
        " ◎ ",
        " ● ",
        " ◎ ",
    ]
    
    def __init__(self, text: str = "", **kwargs):
        super().__init__(**kwargs)
        self.ring_text = text
        self._frame = 0
    
    def on_mount(self):
        """Start pulsing."""
        self.set_interval(0.5, self._pulse)
    
    def _pulse(self):
        """Update pulse frame."""
        frame = self.FRAMES[self._frame % len(self.FRAMES)]
        self.update(f"{frame} {self.ring_text}" if self.ring_text else frame)
        self._frame += 1


class TypingStatus(Static):
    """Status text that types out character by character."""
    
    DEFAULT_CSS = """
    TypingStatus {
        height: auto;
        color: $text-muted;
    }
    """
    
    def __init__(self, text: str = "", speed: float = 0.03, **kwargs):
        super().__init__(**kwargs)
        self.full_text = text
        self.speed = speed
        self._current_index = 0
    
    def on_mount(self):
        """Start typing animation."""
        if self.full_text:
            self._type_char()
    
    def _type_char(self):
        """Type next character."""
        if self._current_index < len(self.full_text):
            self.update(self.full_text[:self._current_index + 1])
            self._current_index += 1
            self.set_timer(self.speed, self._type_char)
    
    def set_text(self, text: str):
        """Set new text and restart animation."""
        self.full_text = text
        self._current_index = 0
        self.update("")
        self._type_char()


class FadeContainer(Container):
    """Container that fades in when mounted."""
    
    DEFAULT_CSS = """
    FadeContainer {
        animation: fade-in 0.3s ease-out;
    }
    
    @keyframes fade-in {
        from { opacity: 0; }
        to { opacity: 1; }
    }
    """


class BounceText(Static):
    """Text that bounces for emphasis."""
    
    DEFAULT_CSS = """
    BounceText {
        height: auto;
        text-align: center;
        animation: bounce 0.5s ease-in-out;
    }
    
    @keyframes bounce {
        0%, 100% { transform: translateY(0); }
        50% { transform: translateY(-1); }
    }
    """


class ConfettiCelebration(Static):
    """ASCII confetti celebration animation."""
    
    DEFAULT_CSS = """
    ConfettiCelebration {
        width: 100%;
        height: auto;
        text-align: center;
    }
    """
    
    CONFETTI_CHARS = ["✨", "🎉", "🎊", "⭐", "🌟", "💫", "🎈", "🎆"]
    
    def __init__(self, message: str = "Congratulations!", **kwargs):
        super().__init__(**kwargs)
        self.message = message
        self._frame = 0
    
    def on_mount(self):
        """Start celebration."""
        self._celebrate()
    
    def _celebrate(self):
        """Animate confetti."""
        import random
        
        if self._frame < 20:
            # Generate random confetti pattern
            lines = []
            for _ in range(5):
                line = ""
                for _ in range(40):
                    if random.random() < 0.2:
                        line += random.choice(self.CONFETTI_CHARS)
                    else:
                        line += " "
                lines.append(line)
            
            # Center message
            lines.append("")
            lines.append(f"  {self.message}  ".center(40))
            lines.append("")
            
            self.update("\n".join(lines))
            self._frame += 1
            self.set_timer(0.1, self._celebrate)
        else:
            # Final frame
            self.update(f"\n{'✨' * 10}\n\n  {self.message}  \n\n{'✨' * 10}")


class StreakCounter(Static):
    """Counter showing consecutive successes with fire animation."""
    
    DEFAULT_CSS = """
    StreakCounter {
        width: auto;
        height: auto;
        text-align: center;
    }
    
    StreakCounter.low {
        color: $text-muted;
    }
    
    StreakCounter.medium {
        color: $warning;
    }
    
    StreakCounter.high {
        color: $error;
        text-style: bold;
    }
    """
    
    streak = reactive(0)
    
    def watch_streak(self, value: int):
        """Update display when streak changes."""
        self.remove_class("low", "medium", "high")
        
        if value < 3:
            self.add_class("low")
            fire = "🔥"
        elif value < 10:
            self.add_class("medium")
            fire = "🔥🔥"
        else:
            self.add_class("high")
            fire = "🔥🔥🔥"
        
        self.update(f"{fire} {value} {fire}")


class AchievementBadge(Static):
    """Badge showing earned achievement."""
    
    DEFAULT_CSS = """
    AchievementBadge {
        width: auto;
        height: auto;
        border: solid $warning;
        background: $warning-darken-3;
        padding: 1;
        text-align: center;
    }
    
    #badge-icon {
        text-style: bold;
        color: $warning;
    }
    
    #badge-title {
        text-style: bold;
    }
    
    #badge-desc {
        color: $text-muted;
        text-style: italic;
    }
    """
    
    def __init__(self, title: str, description: str, icon: str = "🏆", **kwargs):
        super().__init__(**kwargs)
        self.badge_title = title
        self.badge_desc = description
        self.icon = icon
    
    def compose(self):
        yield Static(self.icon, id="badge-icon")
        yield Static(f"ACHIEVEMENT UNLOCKED!", id="badge-subtitle")
        yield Static(self.badge_title, id="badge-title")
        yield Static(self.badge_desc, id="badge-desc")
    
    def on_mount(self):
        """Auto-dismiss after delay."""
        self.set_timer(4, self.remove)


class HoverHighlight(Static):
    """Container that highlights on hover."""
    
    DEFAULT_CSS = """
    HoverHighlight {
        padding: 0 1;
        transition: background 0.2s;
    }
    
    HoverHighlight:hover {
        background: $primary-darken-3;
    }
    """


class FocusRing(Container):
    """Container with visible focus indicator."""
    
    DEFAULT_CSS = """
    FocusRing {
        border: solid $surface-lighten-1;
        padding: 1;
    }
    
    FocusRing:focus {
        border: double $primary;
        background: $primary-darken-3;
    }
    """
