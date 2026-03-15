"""
Responsive Design Components
Terminal size adaptation, responsive layouts, and terminal compatibility.
"""
from textual.widgets import Static, Button
from textual.containers import Vertical, Horizontal
from textual.reactive import reactive



class ResponsiveLayout:
    """Helper for responsive layout decisions."""
    
    # Breakpoints
    SMALL = 80
    MEDIUM = 120
    LARGE = 160
    
    @classmethod
    def get_layout_type(cls, width: int, height: int) -> str:
        """Determine layout type based on terminal size."""
        if width < cls.SMALL or height < 24:
            return "compact"
        elif width < cls.MEDIUM:
            return "standard"
        elif width < cls.LARGE:
            return "wide"
        else:
            return "full"
    
    @classmethod
    def should_show_sidebar(cls, width: int) -> bool:
        """Check if sidebar should be shown."""
        return width >= cls.MEDIUM
    
    @classmethod
    def get_table_columns(cls, width: int) -> int:
        """Get optimal number of table columns."""
        if width < cls.SMALL:
            return 3
        elif width < cls.MEDIUM:
            return 4
        else:
            return 6


class TerminalSizeWarning(ModalScreen):
    """Warning shown when terminal is too small."""
    
    CSS = """
    #size-warning-modal {
        width: 50;
        height: auto;
        border: thick $warning;
        background: $surface;
        padding: 1 2;
    }
    
    #size-warning-title {
        text-align: center;
        text-style: bold;
        color: $warning;
        margin-bottom: 1;
    }
    
    #size-warning-content {
        text-align: center;
        margin: 1 0;
    }
    
    #size-warning-actions {
        margin-top: 1;
        align: center middle;
    }
    """
    
    def __init__(self, current_width: int, current_height: int, **kwargs):
        super().__init__(**kwargs)
        self.current_width = current_width
        self.current_height = current_height
    
    def compose(self):
        with Vertical(id="size-warning-modal"):
            yield Static("⚠️ Terminal Too Small", id="size-warning-title")
            
            yield Static(f"""
Your terminal is currently {self.current_width}x{self.current_height}.

For the best experience, we recommend:
• Minimum: 80 columns x 24 rows
• Optimal: 120 columns x 30 rows

You can:
1. Resize your terminal window
2. Zoom out (Ctrl+- or Cmd+-)
3. Continue anyway (some features may be hidden)
            """.strip(), id="size-warning-content")
            
            with Horizontal(id="size-warning-actions"):
                yield Button("Try Anyway", variant="primary", id="btn-continue")


class TerminalInfo:
    """Information about the terminal environment."""
    
    @staticmethod
    def is_tmux() -> bool:
        """Check if running inside tmux."""
        import os
        return "TMUX" in os.environ
    
    @staticmethod
    def is_screen() -> bool:
        """Check if running inside GNU screen."""
        import os
        return "STY" in os.environ
    
    @staticmethod
    def is_ssh() -> bool:
        """Check if running over SSH."""
        import os
        return "SSH_CLIENT" in os.environ or "SSH_TTY" in os.environ
    
    @staticmethod
    def supports_truecolor() -> bool:
        """Check if terminal supports truecolor."""
        import os
        colorterm = os.environ.get("COLORTERM", "")
        return colorterm in ("truecolor", "24bit")
    
    @staticmethod
    def supports_unicode() -> bool:
        """Check if terminal supports Unicode."""
        import os
        # Most modern terminals support Unicode
        # Check for explicit disable
        return os.environ.get("LANG", "").lower().find("utf") >= 0
    
    @staticmethod
    def get_terminal_name() -> str:
        """Get terminal name."""
        import os
        return os.environ.get("TERM", "unknown")


class CopyFriendlyFormatter:
    """Formatter for copy-paste friendly output."""
    
    @staticmethod
    def strip_ansi(text: str) -> str:
        """Remove ANSI escape codes from text."""
        import re
        ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
        return ansi_escape.sub('', text)
    
    @staticmethod
    def format_table_for_copy(headers: list, rows: list) -> str:
        """Format table as plain text for copying."""
        lines = []
        
        # Header
        lines.append(" | ".join(headers))
        lines.append("-" * len(lines[0]))
        
        # Rows
        for row in rows:
            lines.append(" | ".join(str(cell) for cell in row))
        
        return "\n".join(lines)
    
    @staticmethod
    def format_csv(headers: list, rows: list) -> str:
        """Format data as CSV."""
        import csv
        import io
        
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(headers)
        writer.writerows(rows)
        return output.getvalue()


class ResponsiveContainer(Vertical):
    """Container that adapts to terminal size."""
    
    DEFAULT_CSS = """
    ResponsiveContainer {
        height: 100%;
    }
    """
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._layout_type = "standard"
    
    def on_mount(self):
        """Set up resize handler."""
        self._update_layout()
    
    def _update_layout(self):
        """Update layout based on current size."""
        size = self.size
        if size:
            self._layout_type = ResponsiveLayout.get_layout_type(
                size.width, size.height
            )
            self._apply_layout()
    
    def _apply_layout(self):
        """Apply current layout. Override in subclasses."""
        pass


class ResponsiveSidebar(Horizontal):
    """Sidebar that collapses on small screens."""
    
    DEFAULT_CSS = """
    ResponsiveSidebar {
        height: 100%;
    }
    
    ResponsiveSidebar.collapsed #sidebar {
        display: none;
    }
    
    ResponsiveSidebar.collapsed #content {
        width: 100%;
    }
    """
    
    collapsed = reactive(False)
    
    def watch_collapsed(self, collapsed: bool):
        """Handle collapse state change."""
        if collapsed:
            self.add_class("collapsed")
        else:
            self.remove_class("collapsed")


class ResponsiveGrid:
    """Helper for responsive grid layouts."""
    
    @staticmethod
    def get_columns(width: int) -> int:
        """Get number of columns based on width."""
        if width < 80:
            return 1
        elif width < 120:
            return 2
        elif width < 160:
            return 3
        else:
            return 4
    
    @staticmethod
    def distribute_items(items: list, num_columns: int) -> list:
        """Distribute items into columns."""
        columns = [[] for _ in range(num_columns)]
        for i, item in enumerate(items):
            columns[i % num_columns].append(item)
        return columns


class MobileFriendlyInput:
    """Input helpers for constrained terminals."""
    
    @staticmethod
    def truncate_for_width(text: str, max_width: int, suffix: str = "...") -> str:
        """Truncate text to fit width."""
        if len(text) <= max_width:
            return text
        return text[:max_width - len(suffix)] + suffix
    
    @staticmethod
    def wrap_text(text: str, width: int) -> list:
        """Wrap text to fit width."""
        import textwrap
        return textwrap.wrap(text, width)
    
    @staticmethod
    def abbreviate(text: str, max_length: int) -> str:
        """Abbreviate text if too long."""
        if len(text) <= max_length:
            return text
        
        # Try to keep first and last parts
        if max_length > 10:
            return text[:max_length//2 - 2] + ".." + text[-max_length//2 + 2:]
        return text[:max_length-3] + "..."


# Terminal compatibility checks
def check_terminal_compatibility() -> dict:
    """Check terminal compatibility."""
    info = TerminalInfo()
    
    return {
        "tmux": info.is_tmux(),
        "screen": info.is_screen(),
        "ssh": info.is_ssh(),
        "truecolor": info.supports_truecolor(),
        "unicode": info.supports_unicode(),
        "terminal": info.get_terminal_name(),
    }


def get_compatibility_recommendations(checks: dict) -> list:
    """Get recommendations based on compatibility checks."""
    recommendations = []
    
    if checks.get("tmux"):
        recommendations.append("Running in tmux - mouse support may need enabling")
    
    if checks.get("screen"):
        recommendations.append("Running in screen - some features may be limited")
    
    if not checks.get("truecolor"):
        recommendations.append("Limited color support - using 256-color palette")
    
    if not checks.get("unicode"):
        recommendations.append("Unicode not detected - using ASCII alternatives")
    
    return recommendations


# Minimum size enforcement
MIN_WIDTH = 60
MIN_HEIGHT = 20


def is_terminal_sufficiently_large(size) -> bool:
    """Check if terminal meets minimum size requirements."""
    if size is None:
        return True
    return size.width >= MIN_WIDTH and size.height >= MIN_HEIGHT


class ExportFormatter:
    """Format data for various export formats."""
    
    @staticmethod
    def to_markdown_table(headers: list, rows: list) -> str:
        """Format as Markdown table."""
        lines = []
        
        # Header
        lines.append("| " + " | ".join(headers) + " |")
        lines.append("|" + "|".join([" --- " for _ in headers]) + "|")
        
        # Rows
        for row in rows:
            lines.append("| " + " | ".join(str(cell) for cell in row) + " |")
        
        return "\n".join(lines)
    
    @staticmethod
    def to_jsonl(headers: list, rows: list) -> str:
        """Format as JSON Lines."""
        import json
        lines = []
        for row in rows:
            obj = dict(zip(headers, row))
            lines.append(json.dumps(obj))
        return "\n".join(lines)
