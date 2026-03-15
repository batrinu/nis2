"""
Progress States & Loading - Loop 9
Skeleton screens, progress bars, and step indicators.
"""
from textual.widgets import Static, ProgressBar, Button
from textual.containers import Vertical, Horizontal
from textual.reactive import reactive
from typing import Optional, List
from datetime import datetime


class SkeletonScreen(Static):
    """Skeleton loading placeholder."""
    
    DEFAULT_CSS = """
    SkeletonScreen {
        width: 100%;
        height: auto;
        padding: 1;
    }
    
    .skeleton-header {
        height: 2;
        background: $surface-lighten-1;
        margin-bottom: 1;
    }
    
    .skeleton-line {
        height: 1;
        background: $surface-lighten-1;
        margin: 1 0;
    }
    
    .skeleton-line.short {
        width: 60%;
    }
    
    .skeleton-line.medium {
        width: 80%;
    }
    
    .skeleton-card {
        height: 5;
        background: $surface-lighten-1;
        margin: 1 0;
        border: solid $surface-darken-1;
    }
    """
    
    def __init__(self, lines: int = 5, cards: int = 0, **kwargs):
        super().__init__(**kwargs)
        self.lines = lines
        self.cards = cards
        self._pulse = True
    
    def compose(self):
        yield Static("", classes="skeleton-header")
        
        for i in range(self.lines):
            width_class = "short" if i % 3 == 0 else ("medium" if i % 3 == 1 else "")
            yield Static("", classes=f"skeleton-line {width_class}")
        
        for _ in range(self.cards):
            yield Static("", classes="skeleton-card")
    
    def on_mount(self):
        """Start pulsing animation."""
        self.set_interval(0.8, self._pulse_animation)
    
    def _pulse_animation(self):
        """Pulse the skeleton."""
        if self._pulse:
            self.styles.opacity = 0.6
        else:
            self.styles.opacity = 1.0
        self._pulse = not self._pulse


class StepProgressIndicator(Vertical):
    """Step-by-step progress indicator."""
    
    DEFAULT_CSS = """
    StepProgressIndicator {
        height: auto;
        margin: 1 0;
    }
    
    #steps-container {
        height: auto;
        align: center middle;
    }
    
    .step {
        width: auto;
        height: auto;
        padding: 0 1;
        text-align: center;
    }
    
    .step.completed {
        color: $success;
    }
    
    .step.current {
        color: $primary;
        text-style: bold;
    }
    
    .step.pending {
        color: $text-muted;
    }
    
    .step-connector {
        color: $text-muted;
    }
    
    #step-detail {
        text-align: center;
        margin-top: 1;
        color: $text-muted;
        text-style: italic;
        height: auto;
    }
    """
    
    current_step = reactive(0)
    
    def __init__(self, steps: List[str], **kwargs):
        super().__init__(**kwargs)
        self.steps = steps
    
    def compose(self):
        with Horizontal(id="steps-container"):
            for i, step in enumerate(self.steps):
                # Step indicator
                if i < self.current_step:
                    status = "completed"
                    icon = "✓"
                elif i == self.current_step:
                    status = "current"
                    icon = "●"
                else:
                    status = "pending"
                    icon = "○"
                
                yield Static(f"{icon} {step}", classes=f"step {status}")
                
                # Connector
                if i < len(self.steps) - 1:
                    connector = "→" if i < self.current_step else "-"
                    yield Static(connector, classes="step-connector")
        
        # Current step detail
        if self.current_step < len(self.steps):
            yield Static(f"Current: {self.steps[self.current_step]}", id="step-detail")
    
    def watch_current_step(self, step: int):
        """Update when step changes."""
        self.refresh()
    
    def next_step(self):
        """Advance to next step."""
        if self.current_step < len(self.steps) - 1:
            self.current_step += 1
    
    def previous_step(self):
        """Go back to previous step."""
        if self.current_step > 0:
            self.current_step -= 1


class ProgressWithETA(Vertical):
    """Progress bar with ETA calculation."""
    
    DEFAULT_CSS = """
    ProgressWithETA {
        width: 100%;
        height: auto;
        border: solid $surface-lighten-1;
        background: $surface-darken-1;
        padding: 1;
    }
    
    #progress-header {
        height: auto;
        margin-bottom: 1;
    }
    
    #progress-title {
        text-style: bold;
    }
    
    #progress-percent {
        text-align: right;
    }
    
    #progress-bar {
        margin: 1 0;
    }
    
    #progress-detail {
        height: auto;
        margin-top: 1;
    }
    
    #progress-eta {
        color: $text-muted;
        text-style: italic;
    }
    
    #progress-rate {
        color: $text-muted;
        text-align: right;
    }
    
    #progress-actions {
        align: center middle;
        margin-top: 1;
    }
    """
    
    progress = reactive(0)
    total_items = reactive(0)
    completed_items = reactive(0)
    
    def __init__(self, title: str = "Working...", show_cancel: bool = True, **kwargs):
        super().__init__(**kwargs)
        self.title = title
        self.show_cancel = show_cancel
        self.start_time: Optional[datetime] = None
        self._cancelled = False
    
    def compose(self):
        with Horizontal(id="progress-header"):
            yield Static(self.title, id="progress-title")
            yield Static("0%", id="progress-percent")
        
        yield ProgressBar(total=100, id="progress-bar")
        
        with Horizontal(id="progress-detail"):
            yield Static("Calculating ETA...", id="progress-eta")
            yield Static("", id="progress-rate")
        
        if self.show_cancel:
            with Horizontal(id="progress-actions"):
                yield Button("⏹ Cancel", variant="error", id="btn-cancel")
    
    def on_mount(self):
        """Start timing."""
        self.start_time = datetime.now()
    
    def watch_progress(self, value: int):
        """Update progress and ETA."""
        try:
            # Update progress bar
            bar = self.query_one("#progress-bar", ProgressBar)
            bar.update(progress=value)
            
            # Update percentage
            self.query_one("#progress-percent", Static).update(f"{value}%")
            
            # Update ETA
            self._update_eta(value)
            
        except Exception:
            pass
    
    def _update_eta(self, value: int):
        """Calculate and display ETA."""
        if value == 0 or not self.start_time:
            return
        
        try:
            elapsed = (datetime.now() - self.start_time).total_seconds()
            
            if value > 0 and value < 100:
                # Calculate rate and ETA
                rate = elapsed / value  # seconds per percent
                remaining = rate * (100 - value)
                
                eta_text = self._format_duration(remaining)
                self.query_one("#progress-eta", Static).update(f"ETA: {eta_text}")
                
                # Update rate
                items_per_sec = self.completed_items / elapsed if elapsed > 0 else 0
                if items_per_sec > 0:
                    self.query_one("#progress-rate", Static).update(
                        f"{items_per_sec:.1f} items/sec"
                    )
            
            elif value >= 100:
                self.query_one("#progress-eta", Static).update("Complete!")
                
        except Exception:
            pass
    
    def _format_duration(self, seconds: float) -> str:
        """Format seconds as human-readable duration."""
        if seconds < 60:
            return f"{int(seconds)}s"
        elif seconds < 3600:
            return f"{int(seconds / 60)}m {int(seconds % 60)}s"
        else:
            hours = int(seconds / 3600)
            mins = int((seconds % 3600) / 60)
            return f"{hours}h {mins}m"
    
    def update_progress(self, completed: int, total: int, message: str = ""):
        """Update progress with item counts."""
        self.total_items = total
        self.completed_items = completed
        
        if total > 0:
            self.progress = int((completed / total) * 100)
        
        if message:
            try:
                self.query_one("#progress-title", Static).update(message)
            except Exception:
                pass
    
    def on_button_pressed(self, event):
        """Handle cancel button."""
        if event.button.id == "btn-cancel":
            self._cancelled = True
            event.button.disabled = True
            event.button.label = "Cancelling..."
    
    def is_cancelled(self) -> bool:
        """Check if operation was cancelled."""
        return self._cancelled


class MultiStepProgress(Vertical):
    """Progress indicator for multi-step operations."""
    
    DEFAULT_CSS = """
    MultiStepProgress {
        width: 100%;
        height: auto;
        border: solid $surface-lighten-1;
        padding: 1;
    }
    
    #msp-title {
        text-style: bold;
        text-align: center;
        margin-bottom: 1;
    }
    
    .msp-step {
        height: auto;
        margin: 1 0;
        padding: 0 1;
    }
    
    .msp-step.completed {
        color: $success;
    }
    
    .msp-step.running {
        color: $primary;
    }
    
    .msp-step.pending {
        color: $text-muted;
    }
    
    .msp-step.error {
        color: $error;
    }
    
    .step-status {
        width: 3;
        text-align: center;
    }
    
    .step-name {
        width: 1fr;
    }
    
    .step-detail {
        color: $text-muted;
        text-style: italic;
    }
    """
    
    def __init__(self, steps: List[dict], **kwargs):
        super().__init__(**kwargs)
        # Steps: [{"name": str, "description": str}]
        self.steps = steps
        self.step_statuses = ["pending"] * len(steps)  # pending, running, completed, error
        self.step_details = [""] * len(steps)
    
    def compose(self):
        yield Static("Operation Progress", id="msp-title")
        
        for i, step in enumerate(self.steps):
            status_icon = self._get_status_icon(self.step_statuses[i])
            with Horizontal(classes=f"msp-step {self.step_statuses[i]}"):
                yield Static(status_icon, classes="step-status")
                yield Static(step.get("name", f"Step {i+1}"), classes="step-name")
                if self.step_details[i]:
                    yield Static(self.step_details[i], classes="step-detail")
    
    def _get_status_icon(self, status: str) -> str:
        """Get icon for status."""
        icons = {
            "pending": "○",
            "running": "◐",
            "completed": "✓",
            "error": "✗",
        }
        return icons.get(status, "○")
    
    def update_step(self, step_index: int, status: str, detail: str = ""):
        """Update step status."""
        if 0 <= step_index < len(self.steps):
            self.step_statuses[step_index] = status
            self.step_details[step_index] = detail
            self.refresh()
    
    def start_step(self, step_index: int):
        """Mark step as running."""
        self.update_step(step_index, "running")
    
    def complete_step(self, step_index: int, detail: str = ""):
        """Mark step as completed."""
        self.update_step(step_index, "completed", detail)
    
    def error_step(self, step_index: int, error: str):
        """Mark step as errored."""
        self.update_step(step_index, "error", error)
    
    def is_complete(self) -> bool:
        """Check if all steps completed."""
        return all(s == "completed" for s in self.step_statuses)


class LoadingState(Static):
    """Loading state with multiple visual indicators."""
    
    DEFAULT_CSS = """
    LoadingState {
        width: 100%;
        height: auto;
        text-align: center;
        padding: 2;
    }
    
    #loading-spinner {
        color: $primary;
        text-style: bold;
        margin-bottom: 1;
    }
    
    #loading-text {
        margin: 1 0;
    }
    
    #loading-subtext {
        color: $text-muted;
        text-style: italic;
    }
    """
    
    SPINNER_FRAMES = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
    
    def __init__(self, text: str = "Loading...", subtext: str = "", **kwargs):
        super().__init__(**kwargs)
        self.loading_text = text
        self.subtext = subtext
        self._frame = 0
    
    def compose(self):
        yield Static(self.SPINNER_FRAMES[0], id="loading-spinner")
        yield Static(self.loading_text, id="loading-text")
        if self.subtext:
            yield Static(self.subtext, id="loading-subtext")
    
    def on_mount(self):
        """Start animation."""
        self.set_interval(0.1, self._animate)
    
    def _animate(self):
        """Animate spinner."""
        try:
            frame = self.SPINNER_FRAMES[self._frame % len(self.SPINNER_FRAMES)]
            self.query_one("#loading-spinner", Static).update(frame)
            self._frame += 1
        except Exception:
            pass
    
    def update_text(self, text: str, subtext: str = ""):
        """Update loading text."""
        try:
            self.query_one("#loading-text", Static).update(text)
            if subtext:
                sub = self.query_one("#loading-subtext", Static)
                sub.update(subtext)
                sub.styles.display = "block"
        except Exception:
            pass


class AsyncOperationTracker:
    """Track async operations with progress."""
    
    def __init__(self):
        self.operations: dict = {}
    
    def start_operation(self, op_id: str, title: str, total_steps: int = 1):
        """Start tracking an operation."""
        self.operations[op_id] = {
            "title": title,
            "total_steps": total_steps,
            "current_step": 0,
            "start_time": datetime.now(),
            "status": "running",
        }
    
    def update_operation(self, op_id: str, step: int = None, message: str = ""):
        """Update operation progress."""
        if op_id in self.operations:
            if step is not None:
                self.operations[op_id]["current_step"] = step
            if message:
                self.operations[op_id]["message"] = message
    
    def complete_operation(self, op_id: str):
        """Mark operation as complete."""
        if op_id in self.operations:
            self.operations[op_id]["status"] = "completed"
            self.operations[op_id]["end_time"] = datetime.now()
    
    def get_progress(self, op_id: str) -> dict:
        """Get operation progress."""
        return self.operations.get(op_id, {})
    
    def is_running(self, op_id: str) -> bool:
        """Check if operation is running."""
        op = self.operations.get(op_id)
        return op and op["status"] == "running"
