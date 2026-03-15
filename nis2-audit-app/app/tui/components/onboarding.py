"""
Onboarding Flow - Loop 15
First-time user experience and guided tours.
"""
from textual.screen import ModalScreen
from textual.widgets import Static, Button, ProgressBar
from textual.containers import Vertical, Horizontal
from textual.reactive import reactive
from textual.binding import Binding
from typing import List, Dict, Callable


class OnboardingStep:
    """Single step in the onboarding flow."""
    
    def __init__(self,
                 title: str,
                 content: str,
                 action_text: str = "Continue",
                 validate: Callable = None):
        self.title = title
        self.content = content
        self.action_text = action_text
        self.validate = validate


class OnboardingWizard(ModalScreen):
    """Wizard for first-time user onboarding."""
    
    CSS = """
    #onboarding-wizard {
        width: 70;
        height: auto;
        max-height: 80%;
        border: thick $primary;
        background: $surface;
        padding: 2;
    }
    
    #ob-header {
        text-align: center;
        margin-bottom: 1;
    }
    
    #ob-title {
        text-style: bold;
        color: $primary;
        font-size: 2;
    }
    
    #ob-welcome {
        color: $text-muted;
        text-style: italic;
        margin-top: 1;
    }
    
    #ob-progress {
        margin: 1 0;
    }
    
    #ob-step-indicator {
        text-align: center;
        color: $text-muted;
        margin-bottom: 1;
    }
    
    #ob-content {
        border: solid $surface-lighten-1;
        background: $surface-darken-1;
        padding: 2;
        margin: 1 0;
        height: auto;
        min-height: 10;
    }
    
    #ob-step-title {
        text-style: bold;
        color: $primary;
        margin-bottom: 1;
        border-bottom: solid $primary;
        padding-bottom: 1;
    }
    
    #ob-step-content {
        height: auto;
    }
    
    #ob-actions {
        align: center middle;
        margin-top: 2;
    }
    
    #ob-skip {
        text-align: center;
        color: $text-muted;
        margin-top: 1;
    }
    """
    
    BINDINGS = [
        Binding("right,space", "next_step", "Next"),
        Binding("left", "prev_step", "Previous"),
        Binding("escape", "skip", "Skip"),
    ]
    
    current_step = reactive(0)
    
    STEPS = [
        OnboardingStep(
            title="👋 Welcome to NIS2 Audit Tool!",
            content="""
This tool helps you assess compliance with the NIS2 Directive.

NIS2 (Network and Information Security Directive 2) is an EU regulation that requires certain organizations to implement cybersecurity measures.

Don't worry - we'll guide you through everything!
            """.strip(),
        ),
        OnboardingStep(
            title="📋 What You'll Do",
            content="""
Here's what a typical audit looks like:

1. 📝 Create an audit session for an entity
2. 🔍 Scan their network to find devices
3. ✅ Complete the NIS2 compliance checklist
4. 🔧 Review and fix any security findings
5. 📄 Generate a compliance report

Each step is designed to be straightforward, even if you're not a security expert.
            """.strip(),
        ),
        OnboardingStep(
            title="🎯 Entity Classification",
            content="""
Organizations are classified as:

• ESSENTIAL ENTITIES (EE) - Critical sectors like energy, banking
• IMPORTANT ENTITIES (IE) - Other important sectors
• NON-QUALIFYING - Smaller organizations

The tool automatically classifies entities based on sector and size.
            """.strip(),
        ),
        OnboardingStep(
            title="🔍 Network Scanning",
            content="""
The scanner discovers devices on the network:

• Routers and switches
• Firewalls
• Servers and workstations
• IoT devices

Just enter a network range (like 192.168.1.0/24) and click Scan!
            """.strip(),
        ),
        OnboardingStep(
            title="✅ Compliance Checklist",
            content="""
The checklist covers NIS2 Article 21 requirements:

• Risk management
• Incident handling
• Business continuity
• Encryption and MFA
• And more...

Answer honestly - the tool will calculate your compliance score.
            """.strip(),
        ),
        OnboardingStep(
            title="🚀 Ready to Start!",
            content="""
You're all set to begin your first NIS2 audit!

Tips:
• Press '?' anytime for help
• Your work auto-saves every 30 seconds
• Take your time with each question

Click 'Start First Audit' to create your first session!
            """.strip(),
            action_text="🚀 Start First Audit",
        ),
    ]
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    
    def compose(self):
        with Vertical(id="onboarding-wizard"):
            with Vertical(id="ob-header"):
                yield Static("🛡️ NIS2 Audit Tool", id="ob-title")
                yield Static("Your first time? Let's get you started!", id="ob-welcome")
            
            yield ProgressBar(total=len(self.STEPS), id="ob-progress")
            yield Static(f"Step 1 of {len(self.STEPS)}", id="ob-step-indicator")
            
            with Vertical(id="ob-content"):
                yield from self._render_step()
            
            with Horizontal(id="ob-actions"):
                yield Button("◀ Previous", id="btn-prev", disabled=True)
                yield Button("Next ▶", variant="primary", id="btn-next")
            
            yield Static("Press Esc to skip onboarding", id="ob-skip")
    
    def _render_step(self):
        """Render current step content."""
        step = self.STEPS[self.current_step]
        
        yield Static(step.title, id="ob-step-title")
        yield Static(step.content, id="ob-step-content")
    
    def watch_current_step(self, step: int):
        """Update UI when step changes."""
        try:
            # Update progress
            self.query_one("#ob-progress", ProgressBar).update(progress=step + 1)
            self.query_one("#ob-step-indicator", Static).update(
                f"Step {step + 1} of {len(self.STEPS)}"
            )
            
            # Update buttons
            prev_btn = self.query_one("#btn-prev", Button)
            next_btn = self.query_one("#btn-next", Button)
            
            prev_btn.disabled = step == 0
            
            if step == len(self.STEPS) - 1:
                next_btn.label = self.STEPS[step].action_text
                next_btn.variant = "success"
            else:
                next_btn.label = "Next ▶"
                next_btn.variant = "primary"
            
            # Update content
            content = self.query_one("#ob-content", Vertical)
            content.remove_children()
            content.mount_all(list(self._render_step()))
            
        except Exception:
            pass
    
    def on_button_pressed(self, event):
        """Handle button presses."""
        if event.button.id == "btn-next":
            if self.current_step < len(self.STEPS) - 1:
                self.current_step += 1
            else:
                self.dismiss("complete")
        
        elif event.button.id == "btn-prev":
            if self.current_step > 0:
                self.current_step -= 1
    
    def action_next_step(self):
        """Go to next step."""
        if self.current_step < len(self.STEPS) - 1:
            self.current_step += 1
        else:
            self.dismiss("complete")
    
    def action_prev_step(self):
        """Go to previous step."""
        if self.current_step > 0:
            self.current_step -= 1
    
    def action_skip(self):
        """Skip onboarding."""
        self.dismiss("skipped")


class FeatureHighlight(Static):
    """Highlight a feature with explanation."""
    
    DEFAULT_CSS = """
    FeatureHighlight {
        height: auto;
        border: thick $warning;
        background: $warning-darken-3;
        padding: 1;
        margin: 1 0;
    }
    
    #fh-title {
        text-style: bold;
        color: $warning;
        margin-bottom: 1;
    }
    
    #fh-content {
        color: $text;
        height: auto;
    }
    
    #fh-dismiss {
        text-align: right;
        margin-top: 1;
    }
    """
    
    def __init__(self, title: str, content: str, **kwargs):
        super().__init__(**kwargs)
        self.fh_title = title
        self.fh_content = content
    
    def compose(self):
        yield Static(f"💡 {self.fh_title}", id="fh-title")
        yield Static(self.fh_content, id="fh-content")
        yield Button("Got it!", id="fh-dismiss")
    
    def on_button_pressed(self, event):
        """Dismiss highlight."""
        if event.button.id == "fh-dismiss":
            self.remove()


class TooltipTour(Static):
    """Interactive tooltip tour for features."""
    
    DEFAULT_CSS = """
    TooltipTour {
        width: 40;
        height: auto;
        border: thick $primary;
        background: $surface;
        padding: 1;
        layer: overlay;
    }
    
    #tt-title {
        text-style: bold;
        color: $primary;
        border-bottom: solid $primary;
        margin-bottom: 1;
        padding-bottom: 1;
    }
    
    #tt-content {
        height: auto;
        margin: 1 0;
    }
    
    #tt-progress {
        text-align: center;
        color: $text-muted;
        margin: 1 0;
    }
    
    #tt-actions {
        align: center middle;
    }
    """
    
    def __init__(self, steps: List[Dict], **kwargs):
        super().__init__(**kwargs)
        self.tour_steps = steps
        self.current_step = 0
    
    def compose(self):
        step = self.tour_steps[self.current_step]
        
        yield Static(f"🎯 {step['title']}", id="tt-title")
        yield Static(step['content'], id="tt-content")
        yield Static(f"Step {self.current_step + 1} of {len(self.tour_steps)}", id="tt-progress")
        
        with Horizontal(id="tt-actions"):
            if self.current_step > 0:
                yield Button("◀", id="tt-prev")
            yield Button("Next ▶" if self.current_step < len(self.tour_steps) - 1 else "✓ Done", 
                        variant="primary", id="tt-next")
            yield Button("Skip Tour", id="tt-skip")
    
    def on_button_pressed(self, event):
        """Handle navigation."""
        if event.button.id == "tt-next":
            if self.current_step < len(self.tour_steps) - 1:
                self.current_step += 1
                self.refresh()
            else:
                self.remove()
        
        elif event.button.id == "tt-prev":
            if self.current_step > 0:
                self.current_step -= 1
                self.refresh()
        
        elif event.button.id == "tt-skip":
            self.remove()


class FirstTimeHint(Static):
    """Subtle hint for first-time users."""
    
    DEFAULT_CSS = """
    FirstTimeHint {
        height: auto;
        background: $primary-darken-3;
        color: $text;
        padding: 1;
        margin: 1 0;
        border-left: thick $primary;
    }
    
    #fth-text {
        height: auto;
    }
    
    #fth-dismiss {
        text-align: right;
        margin-top: 1;
    }
    """
    
    def __init__(self, message: str, **kwargs):
        super().__init__(**kwargs)
        self.message = message
    
    def compose(self):
        yield Static(f"💡 {self.message}", id="fth-text")
        yield Button("×", id="fth-dismiss")
    
    def on_button_pressed(self, event):
        """Dismiss hint."""
        if event.button.id == "fth-dismiss":
            self.remove()


class WelcomeBanner(Static):
    """Welcome banner for returning users."""
    
    DEFAULT_CSS = """
    WelcomeBanner {
        height: auto;
        background: $success-darken-3;
        border: solid $success;
        padding: 1;
        margin: 1 0;
        text-align: center;
    }
    
    #wb-greeting {
        text-style: bold;
        color: $success;
        font-size: 2;
    }
    
    #wb-message {
        color: $text;
        margin-top: 1;
    }
    
    #wb-stats {
        color: $text-muted;
        margin-top: 1;
        text-style: italic;
    }
    """
    
    def __init__(self, user_name: str = "", stats: Dict = None, **kwargs):
        super().__init__(**kwargs)
        self.user_name = user_name
        self.stats = stats or {}
    
    def compose(self):
        from datetime import datetime
        hour = datetime.now().hour
        
        if 5 <= hour < 12:
            greeting = "Good morning"
        elif 12 <= hour < 17:
            greeting = "Good afternoon"
        else:
            greeting = "Good evening"
        
        if self.user_name:
            greeting += f", {self.user_name}"
        
        yield Static(f"👋 {greeting}!", id="wb-greeting")
        yield Static("Welcome back to NIS2 Audit Tool", id="wb-message")
        
        if self.stats:
            stats_text = " | ".join(f"{k}: {v}" for k, v in self.stats.items())
            yield Static(stats_text, id="wb-stats")
    
    def on_mount(self):
        """Auto-dismiss after delay."""
        self.set_timer(5, self.remove)
