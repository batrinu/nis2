"""
Animation and Micro-Interaction Components
Adds life and feedback to the TUI for a delightful experience.
"""
from textual.widgets import Static
from textual.reactive import reactive
from textual.containers import Container
import asyncio


class TypingText(Static):
    """Text that appears character by character like typing."""
    
    DEFAULT_CSS = """
    TypingText {
        text-style: none;
    }
    """
    
    full_text = reactive("")
    display_text = reactive("")
    
    def __init__(self, text: str = "", speed: float = 0.03, **kwargs):
        super().__init__(**kwargs)
        self.full_text = text
        self.speed = speed
        self._typing_task = None
    
    def on_mount(self):
        """Start typing animation."""
        self._typing_task = asyncio.create_task(self._type_text())
    
    async def _type_text(self):
        """Animate text appearing."""
        for i in range(len(self.full_text) + 1):
            self.display_text = self.full_text[:i]
            self.update(self.display_text)
            await asyncio.sleep(self.speed)
    
    def watch_full_text(self, text: str):
        """Restart animation when text changes."""
        if self._typing_task:
            self._typing_task.cancel()
        self.on_mount()


class PulsingText(Static):
    """Text that pulses to draw attention."""
    
    DEFAULT_CSS = """
    PulsingText {
        animation: pulse 2s ease-in-out infinite;
    }
    
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.5; }
    }
    """


class AnimatedBorder(Container):
    """Container with animated border for focus/importance."""
    
    DEFAULT_CSS = """
    AnimatedBorder {
        border: solid $primary;
        animation: border-pulse 2s ease-in-out infinite;
    }
    
    @keyframes border-pulse {
        0%, 100% { border-color: $primary; }
        50% { border-color: $primary-lighten-2; }
    }
    """


class LoadingDots(Static):
    """Animated loading dots."""
    
    DEFAULT_CSS = """
    LoadingDots {
        text-style: bold;
    }
    """
    
    def __init__(self, text: str = "Loading", **kwargs):
        super().__init__(**kwargs)
        self.base_text = text
        self._animation_task = None
    
    def on_mount(self):
        """Start animation."""
        self._animation_task = asyncio.create_task(self._animate())
    
    async def _animate(self):
        """Animate dots."""
        dots = ["", ".", "..", "..."]
        i = 0
        while True:
            self.update(f"{self.base_text}{dots[i % 4]}")
            await asyncio.sleep(0.5)
            i += 1
    
    def stop(self):
        """Stop animation."""
        if self._animation_task:
            self._animation_task.cancel()


class ProgressCelebration(Static):
    """Celebration animation for progress milestones."""
    
    DEFAULT_CSS = """
    ProgressCelebration {
        text-align: center;
        height: auto;
    }
    """
    
    def __init__(self, milestone: int = 50, **kwargs):
        super().__init__(**kwargs)
        self.milestone = milestone
        self._celebration_task = None
    
    def trigger(self):
        """Trigger celebration animation."""
        frames = {
            25: ["✨", "⭐", "✨"],
            50: ["🎉", "🎊", "🎉"],
            75: ["🔥", "⚡", "🔥"],
            100: ["🏆", "🌟", "🏆"],
        }
        
        icons = frames.get(self.milestone, ["✨"])
        if self._celebration_task:
            self._celebration_task.cancel()
        self._celebration_task = asyncio.create_task(self._animate_celebration(icons))
    
    async def _animate_celebration(self, icons: list):
        """Animate celebration."""
        for _ in range(3):
            for icon in icons:
                self.update(f"  {icon}  ")
                await asyncio.sleep(0.2)
        self.update("")


class CounterAnimation(Static):
    """Animated counter that counts up to a value."""
    
    def __init__(self, target: int = 0, prefix: str = "", suffix: str = "", **kwargs):
        super().__init__(**kwargs)
        self.target = target
        self.prefix = prefix
        self.suffix = suffix
        self.current = 0
        self._count_task = None
    
    def on_mount(self):
        """Start counting."""
        if self._count_task:
            self._count_task.cancel()
        self._count_task = asyncio.create_task(self._count_up())
    
    async def _count_up(self):
        """Animate counting."""
        duration = 1.0  # seconds
        steps = min(self.target, 30)  # Max 30 steps
        step_value = self.target / steps
        step_duration = duration / steps
        
        for i in range(steps + 1):
            value = int(i * step_value)
            self.update(f"{self.prefix}{value}{self.suffix}")
            await asyncio.sleep(step_duration)
        
        # Ensure final value is exact
        self.update(f"{self.prefix}{self.target}{self.suffix}")


class FadeInContainer(Container):
    """Container that fades in when mounted."""
    
    DEFAULT_CSS = """
    FadeInContainer {
        animation: fade-in 0.3s ease-out;
    }
    
    @keyframes fade-in {
        from { opacity: 0; }
        to { opacity: 1; }
    }
    """


class SlideInContainer(Container):
    """Container that slides in from the side."""
    
    DEFAULT_CSS = """
    SlideInContainer {
        animation: slide-in 0.3s ease-out;
    }
    
    @keyframes slide-in {
        from { offset-x: -100%; }
        to { offset-x: 0; }
    }
    """


class BounceText(Static):
    """Text that bounces for emphasis."""
    
    DEFAULT_CSS = """
    BounceText {
        animation: bounce 0.5s ease-in-out;
    }
    
    @keyframes bounce {
        0%, 100% { transform: translateY(0); }
        50% { transform: translateY(-2); }
    }
    """


class SparkleEffect(Static):
    """Sparkle effect for special moments."""
    
    sparkles = ["✨", "⭐", "🌟", "💫", "⚡"]
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._sparkle_task = None
    
    def trigger(self):
        """Trigger sparkle animation."""
        if self._sparkle_task:
            self._sparkle_task.cancel()
        self._sparkle_task = asyncio.create_task(self._animate_sparkles())
    
    async def _animate_sparkles(self):
        """Show random sparkles."""
        import random
        for _ in range(10):
            sparkle = random.choice(self.sparkles)
            x = random.randint(0, 20)
            self.update(f"{' ' * x}{sparkle}")
            await asyncio.sleep(0.1)
        self.update("")
