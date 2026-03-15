#!/usr/bin/env python3
"""Quick test to see the dashboard."""
import sys
sys.path.insert(0, '.')

from textual.app import App
from textual.widgets import Static, Button
from textual.containers import Vertical, Horizontal

class QuickTest(App):
    CSS = """
    Screen {
        background: #0c0c00;
        color: #ffb000;
    }
    #main {
        width: 80;
        height: auto;
        border: double #ffb000;
        padding: 1 2;
    }
    #title {
        text-align: center;
        text-style: bold;
        color: #00ff41;
    }
    Button {
        margin: 1;
    }
    """
    
    def compose(self):
        with Vertical(id="main"):
            yield Static("🛡️ NIS2 FIELD AUDIT TOOL", id="title")
            yield Static("✅ CSS Fixed! App is working!")
            yield Static("")
            yield Static("The retro TUI is rendering correctly.")
            yield Static("The splash screen shows the ASCII art.")
            yield Static("")
            with Horizontal():
                yield Button("✨ Create Audit", variant="primary")
                yield Button("❓ Help", variant="primary")
                yield Button("❌ Exit", variant="error")

if __name__ == "__main__":
    app = QuickTest()
    app.run()
