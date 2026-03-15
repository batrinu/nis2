"""
Performance & Feedback System
Visual feedback, progress indicators, and operation cancellation.
"""
from textual.widgets import Static, ProgressBar, Button
from textual.containers import Vertical, Horizontal
from textual.reactive import reactive

import asyncio

from app.i18n import get_text as _


class AnimatedSpinner(Static):
    """Animated spinner with status text."""
    
    DEFAULT_CSS = """
    AnimatedSpinner {
        height: auto;
        text-align: center;
        color: $primary;
    }
    """
    
    frames = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
    
    def __init__(self, text: str = _("Loading..."), **kwargs):
        super().__init__(**kwargs)
        self.text = text
        self._frame_index = 0
        self._timer = None
    
    def on_mount(self):
        """Start animation."""
        self._timer = self.set_interval(0.1, self._animate)
    
    def _animate(self):
        """Update animation frame."""
        frame = self.frames[self._frame_index % len(self.frames)]
        self.update(f"{frame} {self.text}")
        self._frame_index += 1
    
    def stop(self):
        """Stop animation."""
        if self._timer:
            self._timer.stop()


class SkeletonLoader(Static):
    """Skeleton loading placeholder."""
    
    DEFAULT_CSS = """
    SkeletonLoader {
        height: auto;
        color: $surface-lighten-1;
    }
    """
    
    def __init__(self, lines: int = 3, **kwargs):
        super().__init__(**kwargs)
        self.lines = lines
    
    def compose(self) -> None:
        """Render the placeholder content."""
        content = "\n".join(["█" * 40 for _ in range(self.lines)])
        self.update(content)


class ProgressIndicator(Vertical):
    """Progress indicator with status text and cancel button."""
    
    DEFAULT_CSS = """
    ProgressIndicator {
        height: auto;
        border: solid $surface-lighten-1;
        background: $surface-darken-1;
        padding: 1;
    }
    
    #progress-status {
        text-align: center;
        margin-bottom: 1;
    }
    
    #progress-bar {
        margin: 1 0;
    }
    
    #progress-detail {
        text-align: center;
        color: $text-muted;
        margin: 1 0;
    }
    
    #progress-actions {
        align: center middle;
        margin-top: 1;
    }
    """
    
    progress = reactive(0)
    status = reactive("")
    detail = reactive("")
    cancellable = reactive(True)
    
    def __init__(self, title: str = _("Working..."), **kwargs):
        super().__init__(**kwargs)
        self.title = title
        self._cancelled = False
    
    def compose(self):
        """Render the progress indicator UI."""
        yield Static(self.title, id="progress-status")
        yield ProgressBar(total=100, id="progress-bar")
        yield Static("", id="progress-detail")
        
        with Horizontal(id="progress-actions"):
            yield Button(_("⏹ Cancel"), variant="error", id="btn-cancel")
    
    def watch_progress(self, value: int):
        """Update progress bar."""
        try:
            self.query_one("#progress-bar", ProgressBar).update(progress=value)
        except Exception:
            pass
    
    def watch_status(self, text: str):
        """Update status text."""
        try:
            self.query_one("#progress-status", Static).update(text)
        except Exception:
            pass
    
    def watch_detail(self, text: str):
        """Update detail text."""
        try:
            self.query_one("#progress-detail", Static).update(text)
        except Exception:
            pass
    
    def watch_cancellable(self, enabled: bool):
        """Update cancel button state."""
        try:
            btn = self.query_one("#btn-cancel", Button)
            btn.disabled = not enabled
        except Exception:
            pass
    
    def on_button_pressed(self, event):
        """Handle cancel button."""
        if event.button.id == "btn-cancel":
            self._cancelled = True
            self.status = _("Cancelling...")
            event.button.disabled = True
    
    def is_cancelled(self) -> bool:
        """Check if operation was cancelled."""
        return self._cancelled


class ToastNotification(Static):
    """Toast notification popup."""
    
    DEFAULT_CSS = """
    ToastNotification {
        width: auto;
        height: auto;
        padding: 1 2;
        border: solid;
        background: $surface;
    }
    
    ToastNotification.success {
        border: solid $success;
        background: $success-darken-3;
    }
    
    ToastNotification.error {
        border: solid $error;
        background: $error-darken-3;
    }
    
    ToastNotification.warning {
        border: solid $warning;
        background: $warning-darken-3;
    }
    
    ToastNotification.info {
        border: solid $primary;
        background: $surface-darken-1;
    }
    """
    
    def __init__(self, message: str, severity: str = "info", **kwargs):
        super().__init__(message, **kwargs)
        self.add_class(severity)
        self._timer = None
    
    def on_mount(self):
        """Auto-dismiss after delay."""
        self._timer = self.set_timer(3, self.dismiss)
    
    def dismiss(self):
        """Remove the toast."""
        if self._timer:
            self._timer.stop()
        self.remove()


class SuccessAnimation(Static):
    """Success checkmark animation."""
    
    DEFAULT_CSS = """
    SuccessAnimation {
        text-align: center;
        color: $success;
        text-style: bold;
    }
    """
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._frame = 0
    
    def on_mount(self):
        """Start animation."""
        self.update("○")
        self.set_timer(0.1, self._animate_step1)
    
    def _animate_step1(self):
        self.update("◐")
        self.set_timer(0.1, self._animate_step2)
    
    def _animate_step2(self):
        self.update("◑")
        self.set_timer(0.1, self._animate_step3)
    
    def _animate_step3(self):
        self.update("◒")
        self.set_timer(0.1, self._animate_step4)
    
    def _animate_step4(self):
        self.update("✓")


class ErrorShake(Static):
    """Error shake animation effect."""
    
    DEFAULT_CSS = """
    ErrorShake {
        text-align: center;
        color: $error;
    }
    """
    
    def __init__(self, message: str = _("Error!"), **kwargs):
        super().__init__(**kwargs)
        self.message = message
        self._shake_frames = ["  ", " ▌", " █", "▐ ", "  "]
        self._frame = 0
    
    def on_mount(self):
        """Start shake animation."""
        self._animate()
    
    def _animate(self):
        if self._frame < len(self._shake_frames) * 2:
            frame = self._shake_frames[self._frame % len(self._shake_frames)]
            self.update(f"{frame} {self.message} {frame}")
            self._frame += 1
            self.set_timer(0.05, self._animate)
        else:
            self.update(f"✗ {self.message}")


class OptimisticUpdate:
    """Helper for optimistic UI updates."""
    
    def __init__(self, widget, rollback_delay: float = 3.0):
        self.widget = widget
        self.rollback_delay = rollback_delay
        self._original_state = None
        self._timer = None
    
    def apply(self, new_state: dict):
        """Apply optimistic state change."""
        self._original_state = self._get_current_state()
        self._apply_state(new_state)
    
    def confirm(self):
        """Confirm the optimistic update."""
        if self._timer:
            self._timer.stop()
        self._original_state = None
    
    def rollback(self):
        """Rollback to original state."""
        if self._original_state:
            self._apply_state(self._original_state)
        self._original_state = None
    
    def _get_current_state(self) -> dict:
        """Get current widget state."""
        # Override in subclasses
        return {}
    
    def _apply_state(self, state: dict):
        """Apply state to widget."""
        # Override in subclasses
        pass


class CancellableOperation:
    """Wrapper for cancellable long-running operations."""
    
    def __init__(self, operation, on_cancel=None):
        self.operation = operation
        self.on_cancel = on_cancel
        self._cancelled = False
        self._progress = 0
    
    async def run(self, *args, **kwargs):
        """Run the operation with cancellation support."""
        try:
            result = await self.operation(*args, **kwargs)
            if self._cancelled:
                return None
            return result
        except asyncio.CancelledError:
            if self.on_cancel:
                await self.on_cancel()
            return None
    
    def cancel(self):
        """Request cancellation."""
        self._cancelled = True
    
    def is_cancelled(self) -> bool:
        """Check if operation was cancelled."""
        return self._cancelled
    
    def set_progress(self, value: int):
        """Update progress (0-100)."""
        self._progress = max(0, min(100, value))


# Performance monitoring
class PerformanceMonitor:
    """Simple performance monitoring."""
    
    def __init__(self):
        self._operations = {}
    
    def start(self, name: str):
        """Start timing an operation."""
        import time
        self._operations[name] = time.time()
    
    def end(self, name: str) -> float:
        """End timing and return duration."""
        import time
        if name in self._operations:
            duration = time.time() - self._operations[name]
            del self._operations[name]
            return duration
        return 0.0
    
    def log(self, name: str, duration: float):
        """Log operation duration."""
        import logging
        logger = logging.getLogger(__name__)
        logger.debug(_("Operation '{}' took {:.3f}s").format(name, duration))


# Global performance monitor
_performance_monitor = PerformanceMonitor()


def start_timing(name: str):
    """Start timing an operation."""
    _performance_monitor.start(name)


def end_timing(name: str) -> float:
    """End timing an operation."""
    return _performance_monitor.end(name)
