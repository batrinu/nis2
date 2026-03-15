"""
Splash screen with retro 1980s Romanian university boot sequence.
Enhanced with friendly UX for first-time users.
RomEnglish localization: Technical terms in English, actions in Romanian.
"""
import os
from textual.screen import Screen
from textual.widgets import Static, ProgressBar, Label
from textual.containers import Vertical
from textual.reactive import reactive
from asyncio import sleep
import random

from ..ascii_art import HEADER_COMPACT, BOOT_MESSAGES, EASTER_EGGS
from ...startup_checks import is_first_run
from ...i18n import get_text as _
import logging

logger = logging.getLogger(__name__)


# Friendly loading tips that rotate during boot (RomEnglish)
LOADING_TIPS = [
    f"💡 Tip: Apasă F1 oricând pentru {_('help')}",
    "💡 Tip: Datele tale sunt encriptate și securizate",
    "💡 Tip: Folosește Tab pentru navigare între câmpuri",
    f"💡 Tip: Apasă '?' pentru a vedea scurtăturile",
    "💡 Tip: Munca ta se salvează automat la fiecare 5 minute",
    f"💡 Tip: Începe cu un {_('network')} mic pentru a învăța",
    f"💡 Tip: Toate {_('reports').lower()} pot fi exportate în PDF",
    f"💡 Tip: Conformitatea NIS2 ajută la protejarea organizației tale",
]


class SplashScreen(Screen):
    """
    Initial loading screen with retro 1980s Romanian university aesthetic.
    Inspired by MECIPT computers and academic computing of that era.
    """
    
    DEFAULT_CSS = """
    #splash-container {
        align: center middle;
        width: 80;
        height: auto;
        border: double #ffb000;
        background: #0c0c00;
        padding: 2 4;
    }
    
    #splash-ascii {
        text-align: center;
        color: #00ff41;
        text-style: bold;
        margin-bottom: 1;
    }
    
    #splash-welcome {
        text-align: center;
        color: #ffb000;
        text-style: bold;
        margin-bottom: 1;
        padding: 1;
        border: solid #4a4a00;
        background: #141400;
    }
    
    #splash-subtitle {
        text-align: center;
        color: #b8b000;
        text-style: italic;
        margin-bottom: 1;
    }
    
    #splash-version {
        text-align: center;
        color: #888866;
        margin-bottom: 1;
    }
    
    #splash-progress {
        margin: 1 0;
        color: #ffb000;
    }
    
    #splash-progress-text {
        text-align: center;
        color: #888866;
        margin-top: 0;
    }
    
    #splash-status {
        text-align: left;
        color: #00ff41;
        margin-top: 1;
        text-style: none;
        height: 8;
        border: solid #1a1a00;
        padding: 1;
        background: #0a0a00;
    }
    
    #splash-tip {
        text-align: center;
        color: #66b3ff;
        margin-top: 1;
        text-style: italic;
        height: 1;
    }
    
    #splash-easter-egg {
        text-align: center;
        color: #4a4a00;
        text-style: italic;
        margin-top: 1;
        display: none;
    }
    """
    
    status_text = reactive("")
    progress = reactive(0.0)
    boot_messages = reactive([])
    
    def __init__(self):
        super().__init__()
        self.max_boot_lines = 6
        
    def compose(self):
        """Build the splash screen UI layout.
        
        Creates a centered container with ASCII art header, welcome message,
        progress bar, status log, and rotating tips.
        """
        with Vertical(id="splash-container"):
            # ASCII art header
            yield Static(HEADER_COMPACT, id="splash-ascii")
            
            # Friendly welcome message
            yield Static(f"{_('welcome').title()}! Să facem {_('audit')} pentru securitatea {_('network').lower()}-ului 🔐", id="splash-welcome")
            
            yield Static("NIS2 Field Audit Tool", id="splash-subtitle")
            yield Static("v2.0 © 2024 | Secure • Simple • Compliant", id="splash-version")
            
            # Progress bar with percentage
            yield ProgressBar(total=100, show_eta=False, id="splash-progress")
            yield Static("Se pornește...", id="splash-progress-text")
            
            # Status log (like old terminal boot)
            yield Static("", id="splash-status")
            
            # Rotating tips
            yield Static(random.choice(LOADING_TIPS), id="splash-tip")
            
            # Easter egg (hidden initially)
            yield Static(random.choice(EASTER_EGGS), id="splash-easter-egg")
    
    async def on_mount(self):
        """Start the retro boot sequence."""
        self.run_worker(self._boot_sequence())
    
    async def _boot_sequence(self):
        """
        Simulate a retro computer boot sequence with friendly UX.
        Inspired by 1980s Romanian university computers like MECIPT.
        """
        status_widget = self.query_one("#splash-status", Static)
        progress_bar = self.query_one("#splash-progress", ProgressBar)
        progress_text = self.query_one("#splash-progress-text", Static)
        tip_widget = self.query_one("#splash-tip", Static)
        
        boot_log = []
        
        # Initial delay (like old computers)
        await sleep(0.3)
        
        # Boot sequence with retro messages
        total_messages = len(BOOT_MESSAGES)
        for i, message in enumerate(BOOT_MESSAGES):
            # Add timestamp like old systems
            timestamp = f"[{i*10:02d}ms]"
            log_line = f"{timestamp} {message}"
            boot_log.append(log_line)
            
            # Keep only last N lines
            if len(boot_log) > self.max_boot_lines:
                boot_log = boot_log[-self.max_boot_lines:]
            
            # Update display
            status_widget.update("\n".join(boot_log))
            
            # Update progress
            progress = ((i + 1) / total_messages) * 100
            progress_bar.update(progress=progress)
            progress_text.update(f"Se încarcă... {int(progress)}%")
            
            # Rotate tips every few messages
            if i % 3 == 0:
                tip_widget.update(random.choice(LOADING_TIPS))
            
            # Random delay for retro feel (50-200ms)
            await sleep(random.uniform(0.05, 0.2))
        
        # Final "ready" state
        await sleep(0.3)
        boot_log.append(f"[OK] Sistem pregătit! Se pornește aplicația...")
        status_widget.update("\n".join(boot_log))
        progress_bar.update(progress=100)
        progress_text.update(f"Gata! ✓")
        tip_widget.update(f"🎉 {_('welcome').title()} la NIS2 Field Audit Tool!")
        
        # Show easter egg briefly
        easter = self.query_one("#splash-easter-egg", Static)
        easter.styles.display = "block"
        
        # Pause at 100% for dramatic effect
        await sleep(0.8)
        
        # Determine where to go next
        config_dir = os.path.expanduser("~/.nis2-audit")
        first_run = is_first_run(config_dir)
        
        # Navigate to onboarding for first-time users, dashboard for returning users
        # Try onboarding first (only installed for first run), fall back to dashboard
        if first_run:
            try:
                self.app.push_screen("onboarding")
            except Exception as error:
                logger.warning(f"Failed to push onboarding screen: {error}")
                self.app.push_screen("dashboard")
        else:
            self.app.push_screen("dashboard")
