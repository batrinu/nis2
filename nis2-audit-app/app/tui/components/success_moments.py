"""
Success Moments & Celebrations - Loop 10
Confetti, achievements, streaks, and positive reinforcement.
"""
from textual.widgets import Static, Button
from textual.containers import Vertical, Horizontal
from textual.reactive import reactive
from textual.timer import Timer
from textual.screen import ModalScreen
import random
import asyncio
from typing import List, Dict, Optional
from datetime import datetime


# Achievement definitions
ACHIEVEMENTS = {
    "first_session": {
        "title": "Getting Started",
        "description": "Created your first audit session",
        "icon": "🎯",
        "points": 10,
    },
    "first_scan": {
        "title": "Network Explorer",
        "description": "Completed your first network scan",
        "icon": "🔍",
        "points": 15,
    },
    "ten_devices": {
        "title": "Device Whisperer",
        "description": "Discovered 10+ devices in a single scan",
        "icon": "💻",
        "points": 20,
    },
    "first_finding": {
        "title": "Security Sleuth",
        "description": "Identified your first security finding",
        "icon": "🕵️",
        "points": 15,
    },
    "checklist_complete": {
        "title": "Compliance Champion",
        "description": "Completed a full NIS2 checklist",
        "icon": "✅",
        "points": 50,
    },
    "high_score": {
        "title": "Overachiever",
        "description": "Achieved 90%+ compliance score",
        "icon": "⭐",
        "points": 100,
    },
    "perfect_score": {
        "title": "NIS2 Ninja",
        "description": "Achieved 100% compliance score",
        "icon": "🏆",
        "points": 250,
    },
    "five_sessions": {
        "title": "Audit Veteran",
        "description": "Created 5 audit sessions",
        "icon": "📊",
        "points": 50,
    },
    "first_report": {
        "title": "Report Master",
        "description": "Generated your first audit report",
        "icon": "📄",
        "points": 25,
    },
    "night_owl": {
        "title": "Night Owl",
        "description": "Worked on an audit after midnight",
        "icon": "🦉",
        "points": 10,
    },
    "early_bird": {
        "title": "Early Bird",
        "description": "Started an audit before 8 AM",
        "icon": "🐦",
        "points": 10,
    },
    "streak_3": {
        "title": "On a Roll",
        "description": "3 days of audit activity",
        "icon": "🔥",
        "points": 30,
    },
    "streak_7": {
        "title": "Week Warrior",
        "description": "7 days of audit activity",
        "icon": "🔥🔥",
        "points": 75,
    },
    "streak_30": {
        "title": "Monthly Master",
        "description": "30 days of audit activity",
        "icon": "🔥🔥🔥",
        "points": 300,
    },
}

# Encouraging messages
GREAT_JOB_MESSAGES = [
    "🎉 Great job!",
    "⭐ Fantastic work!",
    "🌟 Excellent!",
    "💪 Well done!",
    "🎯 Nailed it!",
    "🏆 Outstanding!",
    "✨ Amazing!",
    "🚀 Crushing it!",
    "👏 Bravo!",
    "🎊 Way to go!",
]

# Confetti patterns
CONFETTI_PATTERNS = [
    ["✨", "🎉", "✨", "🎊", "✨"],
    ["🌟", "⭐", "✨", "💫", "🌟"],
    ["🎈", "🎊", "🎉", "🎈", "🎊"],
    ["💥", "✨", "🌟", "✨", "💥"],
]


class ConfettiAnimation(Static):
    """ASCII confetti celebration animation."""
    
    DEFAULT_CSS = """
    ConfettiAnimation {
        width: 100%;
        height: auto;
        text-align: center;
        color: $warning;
    }
    """
    
    def __init__(self, intensity: str = "medium", **kwargs):
        super().__init__(**kwargs)
        self.intensity = intensity  # low, medium, high
        self._frame = 0
        self._max_frames = 20 if intensity == "high" else (10 if intensity == "medium" else 5)
    
    def on_mount(self):
        """Start animation."""
        self.set_interval(0.1, self._animate)
    
    def _animate(self):
        """Animate confetti."""
        if self._frame >= self._max_frames:
            self.remove()
            return
        
        # Generate random confetti pattern
        lines = []
        height = 6 if self.intensity == "high" else 4
        width = 40
        
        for _ in range(height):
            line = ""
            for _ in range(width):
                if random.random() < 0.15:
                    line += random.choice(["✨", "⭐", "🎉", "🎊", "🌟", "💫"])
                else:
                    line += " "
            lines.append(line)
        
        self.update("\n".join(lines))
        self._frame += 1


class AchievementPopup(Static):
    """Popup notification for unlocked achievements."""
    
    DEFAULT_CSS = """
    AchievementPopup {
        width: 40;
        height: auto;
        border: thick $warning;
        background: $warning-darken-3;
        padding: 1;
        align: center middle;
    }
    
    #achievement-header {
        text-align: center;
        color: $warning;
        text-style: bold;
        margin-bottom: 1;
    }
    
    #achievement-icon {
        text-align: center;
        text-style: bold;
        font-size: 3;
        margin: 1 0;
    }
    
    #achievement-title {
        text-align: center;
        text-style: bold;
        color: $text;
        margin: 1 0;
    }
    
    #achievement-desc {
        text-align: center;
        color: $text-muted;
        text-style: italic;
    }
    
    #achievement-points {
        text-align: center;
        color: $success;
        text-style: bold;
        margin-top: 1;
    }
    """
    
    def __init__(self, achievement_id: str, **kwargs):
        super().__init__(**kwargs)
        self.achievement = ACHIEVEMENTS.get(achievement_id, {})
    
    def compose(self):
        yield Static("🏆 ACHIEVEMENT UNLOCKED!", id="achievement-header")
        yield Static(self.achievement.get("icon", "⭐"), id="achievement-icon")
        yield Static(self.achievement.get("title", "Unknown"), id="achievement-title")
        yield Static(self.achievement.get("description", ""), id="achievement-desc")
        yield Static(f"+{self.achievement.get('points', 0)} points", id="achievement-points")
    
    def on_mount(self):
        """Auto-dismiss after delay."""
        self.set_timer(4, self.remove)


class StreakDisplay(Static):
    """Display current activity streak."""
    
    DEFAULT_CSS = """
    StreakDisplay {
        width: auto;
        height: auto;
        text-align: center;
    }
    
    StreakDisplay.streak-0 {
        color: $text-muted;
    }
    
    StreakDisplay.streak-low {
        color: $warning;
    }
    
    StreakDisplay.streak-high {
        color: $error;
        text-style: bold;
    }
    
    #streak-count {
        text-style: bold;
    }
    """
    
    streak = reactive(0)
    
    def watch_streak(self, value: int):
        """Update display on streak change."""
        self.remove_class("streak-0", "streak-low", "streak-high")
        
        if value == 0:
            self.add_class("streak-0")
            fire = "🔥"
        elif value < 7:
            self.add_class("streak-low")
            fire = "🔥"
        else:
            self.add_class("streak-high")
            fire = "🔥🔥"
        
        day_word = "day" if value == 1 else "days"
        self.update(f"{fire} {value} {day_word} {fire}")


class CelebrationModal(ModalScreen):
    """Modal for major celebrations."""
    
    CSS = """
    #celebration-modal {
        width: 60;
        height: auto;
        border: thick $success;
        background: $surface;
        padding: 2;
    }
    
    #celebration-title {
        text-align: center;
        text-style: bold;
        color: $success;
        font-size: 2;
        margin-bottom: 1;
    }
    
    #celebration-message {
        text-align: center;
        margin: 1 0;
        height: auto;
    }
    
    #celebration-stats {
        border: solid $primary;
        background: $surface-darken-1;
        padding: 1;
        margin: 1 0;
        height: auto;
    }
    
    #celebration-actions {
        align: center middle;
        margin-top: 2;
    }
    """
    
    def __init__(self, title: str, message: str, stats: Dict = None, **kwargs):
        super().__init__(**kwargs)
        self.celebration_title = title
        self.message = message
        self.stats = stats or {}
    
    def compose(self):
        with Vertical(id="celebration-modal"):
            yield Static(self.celebration_title, id="celebration-title")
            yield Static(self.message, id="celebration-message")
            
            if self.stats:
                with Vertical(id="celebration-stats"):
                    yield Static("📊 Your Stats:", classes="stats-header")
                    for key, value in self.stats.items():
                        yield Static(f"  • {key}: {value}")
            
            with Horizontal(id="celebration-actions"):
                yield Button("🎉 Awesome!", variant="success", id="btn-close")
    
    def on_button_pressed(self, event):
        """Dismiss celebration."""
        self.dismiss()


class GreatJobBanner(Static):
    """Banner showing encouraging message."""
    
    DEFAULT_CSS = """
    GreatJobBanner {
        width: 100%;
        height: auto;
        text-align: center;
        padding: 1;
        background: $success-darken-2;
        color: $text;
        text-style: bold;
        animation: fade-in 0.5s;
    }
    
    @keyframes fade-in {
        from { opacity: 0; transform: translateY(-10); }
        to { opacity: 1; transform: translateY(0); }
    }
    """
    
    def __init__(self, custom_message: str = "", **kwargs):
        super().__init__(**kwargs)
        self.message = custom_message or random.choice(GREAT_JOB_MESSAGES)
    
    def on_mount(self):
        """Auto-dismiss after delay."""
        self.update(self.message)
        self.set_timer(3, self.remove)


class MilestoneTracker:
    """Track user milestones and trigger celebrations."""
    
    def __init__(self, app):
        self.app = app
        self.earned_achievements: set = set()
        self.total_points = 0
        self.current_streak = 0
        self.last_activity_date: Optional[datetime] = None
    
    def record_activity(self, activity_type: str, data: Dict = None):
        """Record user activity and check for milestones."""
        data = data or {}
        
        # Check for achievements
        self._check_achievements(activity_type, data)
        
        # Update streak
        self._update_streak()
        
        # Check for celebrations
        self._check_celebrations(activity_type, data)
    
    def _check_achievements(self, activity_type: str, data: Dict):
        """Check if any achievements were unlocked."""
        new_achievements = []
        
        if activity_type == "session_created":
            new_achievements.append("first_session")
            if data.get("session_count", 0) >= 5:
                new_achievements.append("five_sessions")
        
        elif activity_type == "scan_completed":
            new_achievements.append("first_scan")
            if data.get("device_count", 0) >= 10:
                new_achievements.append("ten_devices")
        
        elif activity_type == "finding_generated":
            new_achievements.append("first_finding")
        
        elif activity_type == "checklist_completed":
            new_achievements.append("checklist_complete")
            score = data.get("score", 0)
            if score >= 100:
                new_achievements.append("perfect_score")
            elif score >= 90:
                new_achievements.append("high_score")
        
        elif activity_type == "report_generated":
            new_achievements.append("first_report")
        
        # Check time-based achievements
        hour = datetime.now().hour
        if hour < 8:
            new_achievements.append("early_bird")
        elif hour >= 0 and hour < 5:
            new_achievements.append("night_owl")
        
        # Show achievement popups
        for achievement_id in new_achievements:
            if achievement_id not in self.earned_achievements:
                self.earned_achievements.add(achievement_id)
                self.total_points += ACHIEVEMENTS.get(achievement_id, {}).get("points", 0)
                self._show_achievement(achievement_id)
    
    def _show_achievement(self, achievement_id: str):
        """Show achievement popup."""
        popup = AchievementPopup(achievement_id)
        # Would mount to app overlay
        # self.app.mount(popup)
    
    def _update_streak(self):
        """Update activity streak."""
        today = datetime.now().date()
        
        if self.last_activity_date:
            days_diff = (today - self.last_activity_date).days
            
            if days_diff == 0:
                # Already active today
                pass
            elif days_diff == 1:
                # Continued streak
                self.current_streak += 1
            else:
                # Streak broken
                self.current_streak = 1
        else:
            self.current_streak = 1
        
        self.last_activity_date = today
        
        # Check streak achievements
        if self.current_streak == 3:
            self._show_achievement("streak_3")
        elif self.current_streak == 7:
            self._show_achievement("streak_7")
        elif self.current_streak == 30:
            self._show_achievement("streak_30")
    
    def _check_celebrations(self, activity_type: str, data: Dict):
        """Check if a celebration should be triggered."""
        if activity_type == "checklist_completed":
            score = data.get("score", 0)
            if score >= 90:
                self._show_major_celebration(score)
    
    def _show_major_celebration(self, score: int):
        """Show major celebration modal."""
        title = "🎉 INCREDIBLE! 🎉" if score == 100 else "🌟 Outstanding Work! 🌟"
        message = (f"You achieved a {score}% compliance score! "
                  "This is a fantastic result for NIS2 readiness.")
        
        stats = {
            "Total Points": self.total_points,
            "Achievements Unlocked": len(self.earned_achievements),
            "Current Streak": f"{self.current_streak} days",
        }
        
        celebration = CelebrationModal(title, message, stats)
        # self.app.push_screen(celebration)


class ProgressCelebration(Static):
    """Mini celebration for progress milestones."""
    
    DEFAULT_CSS = """
    ProgressCelebration {
        width: auto;
        height: auto;
        text-align: center;
        color: $success;
    }
    """
    
    MILESTONE_ICONS = {
        25: "✨",
        50: "🎉",
        75: "🔥",
        100: "🏆",
    }
    
    def __init__(self, percentage: int, **kwargs):
        super().__init__(**kwargs)
        self.percentage = percentage
    
    def on_mount(self):
        """Show milestone celebration."""
        icon = self.MILESTONE_ICONS.get(
            ((self.percentage // 25) * 25),
            "✨"
        )
        
        self.update(f"{icon} {self.percentage}% Complete! {icon}")
        
        # Animate then remove
        self.set_timer(2, self.remove)


def get_random_celebration() -> str:
    """Get a random celebration message."""
    return random.choice(GREAT_JOB_MESSAGES)


def should_celebrate(current: int, previous: int, milestones: List[int] = None) -> bool:
    """Check if a milestone was crossed and celebration is warranted."""
    milestones = milestones or [25, 50, 75, 100]
    
    for milestone in milestones:
        if previous < milestone <= current:
            return True
    
    return False
