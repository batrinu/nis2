"""
Gamification System
Progress tracking, streaks, achievements, and celebrations.
"""
from textual.widgets import Static
from textual.containers import Vertical, Horizontal
from textual.reactive import reactive
from textual.screen import ModalScreen
from datetime import datetime, timedelta
import json
import os


# Achievement definitions
ACHIEVEMENTS = {
    "first_audit": {
        "name": "🎯 First Steps",
        "description": "Complete your first audit session",
        "icon": "🎯",
    },
    "scan_master": {
        "name": "🔍 Scan Master",
        "description": "Scan 10 different networks",
        "icon": "🔍",
    },
    "device_detective": {
        "name": "🕵️ Device Detective",
        "description": "Discover 50 devices",
        "icon": "🕵️",
    },
    "compliance_champion": {
        "name": "🏆 Compliance Champion",
        "description": "Achieve 100% compliance score",
        "icon": "🏆",
    },
    "finding_fixer": {
        "name": "🔧 Finding Fixer",
        "description": "Resolve 10 security findings",
        "icon": "🔧",
    },
    "report_generator": {
        "name": "📄 Report Generator",
        "description": "Generate 5 audit reports",
        "icon": "📄",
    },
    "week_warrior": {
        "name": "⚔️ Week Warrior",
        "description": "Complete an audit every day for 7 days",
        "icon": "⚔️",
    },
    "speed_demon": {
        "name": "⚡ Speed Demon",
        "description": "Complete an audit in under 15 minutes",
        "icon": "⚡",
    },
}


class AchievementManager:
    """Manages user achievements and progress."""
    
    def __init__(self):
        self.config_dir = os.path.expanduser("~/.nis2-audit")
        self.achievements_file = os.path.join(self.config_dir, "achievements.json")
        self.stats_file = os.path.join(self.config_dir, "stats.json")
        self._achievements = self._load_achievements()
        self._stats = self._load_stats()
    
    def _load_achievements(self) -> set:
        """Load unlocked achievements."""
        try:
            if os.path.exists(self.achievements_file):
                with open(self.achievements_file, 'r') as f:
                    return set(json.load(f))
        except Exception:
            pass
        return set()
    
    def _load_stats(self) -> dict:
        """Load user statistics."""
        try:
            if os.path.exists(self.stats_file):
                with open(self.stats_file, 'r') as f:
                    return json.load(f)
        except Exception:
            pass
        return self._default_stats()
    
    def _default_stats(self) -> dict:
        """Get default stats."""
        return {
            "audits_completed": 0,
            "devices_discovered": 0,
            "networks_scanned": 0,
            "findings_resolved": 0,
            "reports_generated": 0,
            "total_audit_time": 0,  # seconds
            "first_audit_date": None,
            "last_audit_date": None,
            "current_streak": 0,
            "longest_streak": 0,
        }
    
    def _save(self):
        """Save achievements and stats."""
        try:
            os.makedirs(self.config_dir, exist_ok=True)
            with open(self.achievements_file, 'w') as f:
                json.dump(list(self._achievements), f)
            with open(self.stats_file, 'w') as f:
                json.dump(self._stats, f, indent=2)
        except Exception:
            pass
    
    def unlock_achievement(self, achievement_id: str) -> bool:
        """Unlock an achievement. Returns True if newly unlocked."""
        if achievement_id not in self._achievements:
            self._achievements.add(achievement_id)
            self._save()
            return True
        return False
    
    def has_achievement(self, achievement_id: str) -> bool:
        """Check if achievement is unlocked."""
        return achievement_id in self._achievements
    
    def get_unlocked_achievements(self) -> list:
        """Get list of unlocked achievements."""
        return [
            {"id": aid, **ACHIEVEMENTS[aid]}
            for aid in self._achievements
            if aid in ACHIEVEMENTS
        ]
    
    def get_locked_achievements(self) -> list:
        """Get list of locked achievements."""
        return [
            {"id": aid, **info}
            for aid, info in ACHIEVEMENTS.items()
            if aid not in self._achievements
        ]
    
    def update_stat(self, stat_name: str, value: int = 1, increment: bool = True):
        """Update a statistic."""
        if increment:
            self._stats[stat_name] = self._stats.get(stat_name, 0) + value
        else:
            self._stats[stat_name] = value
        self._save()
    
    def get_stats(self) -> dict:
        """Get all statistics."""
        return self._stats.copy()
    
    def record_audit_completion(self, duration_seconds: int = 0):
        """Record completion of an audit."""
        now = datetime.now().isoformat()
        
        self._stats["audits_completed"] += 1
        self._stats["total_audit_time"] += duration_seconds
        
        if self._stats["first_audit_date"] is None:
            self._stats["first_audit_date"] = now
        
        # Check streak
        last_date = self._stats.get("last_audit_date")
        if last_date:
            try:
                last = datetime.fromisoformat(last_date)
            except (ValueError, TypeError):
                last = None
            today = datetime.now()
            if last is None:
                self._stats["current_streak"] = 1
            if (today - last).days == 1:
                self._stats["current_streak"] += 1
            elif (today - last).days > 1:
                self._stats["current_streak"] = 1
        else:
            self._stats["current_streak"] = 1
        
        self._stats["longest_streak"] = max(
            self._stats["longest_streak"],
            self._stats["current_streak"]
        )
        self._stats["last_audit_date"] = now
        
        self._save()
        
        # Check for achievements
        return self._check_achievements()
    
    def _check_achievements(self) -> list:
        """Check and unlock any newly earned achievements."""
        newly_unlocked = []
        
        checks = [
            ("first_audit", self._stats["audits_completed"] >= 1),
            ("scan_master", self._stats["networks_scanned"] >= 10),
            ("device_detective", self._stats["devices_discovered"] >= 50),
            ("finding_fixer", self._stats["findings_resolved"] >= 10),
            ("report_generator", self._stats["reports_generated"] >= 5),
            ("week_warrior", self._stats["current_streak"] >= 7),
        ]
        
        for achievement_id, condition in checks:
            if condition and self.unlock_achievement(achievement_id):
                newly_unlocked.append(achievement_id)
        
        return newly_unlocked


# Global achievement manager
_achievement_manager = AchievementManager()


def get_achievement_manager() -> AchievementManager:
    """Get the global achievement manager."""
    return _achievement_manager


class CelebrationModal(ModalScreen):
    """Modal celebrating an achievement."""
    
    CSS = """
    #celebration-modal {
        width: 50;
        height: auto;
        border: thick $success;
        background: $surface;
        padding: 1 2;
    }
    
    #celebration-title {
        text-align: center;
        text-style: bold;
        color: $success;
        margin-bottom: 1;
    }
    
    #celebration-icon {
        text-align: center;
        text-style: bold;
        height: 3;
    }
    
    #celebration-message {
        text-align: center;
        margin: 1 0;
    }
    
    #celebration-actions {
        margin-top: 1;
        align: center middle;
    }
    """
    
    def __init__(self, achievement_id: str, **kwargs):
        """Initialize celebration modal for an achievement.
        
        Args:
            achievement_id: ID of the achievement to celebrate.
            **kwargs: Additional keyword arguments passed to ModalScreen.
        """
        super().__init__(**kwargs)
        self.achievement = ACHIEVEMENTS.get(achievement_id, {})
    
    def compose(self):
        """Compose the celebration modal with achievement details."""
        with Vertical(id="celebration-modal"):
            yield Static("🎉 Achievement Unlocked!", id="celebration-title")
            yield Static(self.achievement.get("icon", "🏆"), id="celebration-icon")
            yield Static(f"[b]{self.achievement.get('name', 'Unknown')}[/b]", id="celebration-message")
            yield Static(self.achievement.get("description", ""), id="celebration-desc")
            
            with Horizontal(id="celebration-actions"):
                yield Button("🎉 Awesome!", variant="success", id="btn-celebrate")
    
    def on_button_pressed(self, event):
        """Handle button press in celebration modal.
        
        Args:
            event: Button pressed event.
        """
        if event.button.id == "btn-celebrate":
            self.dismiss()


class ProgressWidget(Static):
    """Widget showing user progress and stats."""
    
    DEFAULT_CSS = """
    ProgressWidget {
        height: auto;
        border: solid $primary;
        padding: 1;
    }
    """
    
    def __init__(self, **kwargs):
        """Initialize progress widget with current stats."""
        super().__init__(**kwargs)
        self._update_display()
    
    def _update_display(self):
        """Update the progress display."""
        stats = _achievement_manager.get_stats()
        unlocked = len(_achievement_manager.get_unlocked_achievements())
        total = len(ACHIEVEMENTS)
        
        content = f"""
📊 Your Progress

🏆 Achievements: {unlocked}/{total}
📋 Audits Completed: {stats.get('audits_completed', 0)}
🔍 Devices Discovered: {stats.get('devices_discovered', 0)}
🔧 Findings Resolved: {stats.get('findings_resolved', 0)}
⚔️ Current Streak: {stats.get('current_streak', 0)} days
        """.strip()
        
        self.update(content)


class StreakIndicator(Static):
    """Streak indicator with fire animation."""
    
    DEFAULT_CSS = """
    StreakIndicator {
        height: auto;
        text-align: center;
    }
    
    StreakIndicator.active {
        color: $warning;
    }
    """
    
    streak = reactive(0)
    
    def __init__(self, **kwargs):
        """Initialize streak indicator with zero streak."""
        super().__init__("🔥 0 day streak", **kwargs)
    
    def watch_streak(self, value: int):
        """Update display when streak changes."""
        if value >= 7:
            self.update(f"🔥🔥🔥 {value} DAY STREAK! You're on fire! 🔥🔥🔥")
            self.add_class("active")
        elif value >= 3:
            self.update(f"🔥🔥 {value} day streak - Keep it up!")
            self.add_class("active")
        elif value > 0:
            self.update(f"🔥 {value} day streak")
        else:
            self.update("Start an audit to begin your streak!")
            self.remove_class("active")


# ASCII Confetti for celebrations
CONFETTI_FRAMES = [
    "✨  🎉      ✨",
    "🎊  ✨  🎉    ",
    "  ✨    🎊  ✨",
    "🎉  🎊  ✨    ",
]


def get_celebration_message() -> str:
    """Get a random celebration message."""
    import random
    messages = [
        "Great job! 🎉",
        "You're crushing it! 💪",
        "Fantastic work! ⭐",
        "Keep it up! 🚀",
        "Audit complete! ✅",
        "Another one done! 🎯",
        "Security improved! 🛡️",
        "Well done! 👏",
    ]
    return random.choice(messages)


def format_time_duration(seconds: int) -> str:
    """Format seconds as human-readable duration."""
    if seconds < 60:
        return f"{seconds}s"
    elif seconds < 3600:
        return f"{seconds//60}m {seconds%60}s"
    else:
        return f"{seconds//3600}h {(seconds%3600)//60}m"
