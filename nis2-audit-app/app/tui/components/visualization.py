"""
Data Visualization Components
ASCII charts, compliance meters, and network topology for the TUI.
"""
from textual.widgets import Static
from textual.containers import Vertical, Horizontal
from textual.reactive import reactive


class ASCIIChart(Static):
    """ASCII bar chart widget."""
    
    DEFAULT_CSS = """
    ASCIIChart {
        height: auto;
        padding: 1;
    }
    """
    
    def __init__(self, data: dict = None, title: str = "", **kwargs):
        super().__init__(**kwargs)
        self.data = data or {}
        self.title = title
    
    def render_chart(self, max_width: int = 30) -> str:
        """Render ASCII bar chart."""
        if not self.data:
            return "No data available"
        
        lines = [f"📊 {self.title}" if self.title else ""]
        
        # Find max value for scaling
        max_value = max(self.data.values()) if self.data else 1
        if max_value == 0:
            max_value = 1
        
        # Find longest label
        max_label_len = max(len(str(k)) for k in self.data.keys()) if self.data else 0
        
        for label, value in self.data.items():
            # Calculate bar length
            bar_len = int((value / max_value) * max_width)
            bar = "█" * bar_len
            
            # Format label and value
            label_str = str(label).ljust(max_label_len)
            value_str = f"{value:.0f}%" if isinstance(value, float) else str(value)
            
            lines.append(f"{label_str} │{bar:<{max_width}}│ {value_str}")
        
        return "\n".join(lines)
    
    def on_mount(self):
        """Render on mount."""
        self.update(self.render_chart())


class ComplianceMeter(Static):
    """Visual compliance score meter."""
    
    DEFAULT_CSS = """
    ComplianceMeter {
        height: auto;
        padding: 1;
        text-align: center;
    }
    """
    
    score = reactive(0)
    
    def __init__(self, score: float = 0, label: str = "Compliance", **kwargs):
        super().__init__(**kwargs)
        self.score = max(0, min(100, score))
        self.label = label
    
    def watch_score(self, value: float):
        """Update display when score changes."""
        self.update(self._render_meter())
    
    def _render_meter(self) -> str:
        """Render the compliance meter."""
        # Determine color and emoji based on score
        if self.score >= 80:
            color = "green"
            emoji = "🟢"
            status = "COMPLIANT"
        elif self.score >= 50:
            color = "yellow"
            emoji = "🟡"
            status = "PARTIAL"
        else:
            color = "red"
            emoji = "🔴"
            status = "AT RISK"
        
        # Build meter bar
        filled = int(self.score / 5)  # 20 segments
        empty = 20 - filled
        meter = "█" * filled + "░" * empty
        
        return f"""
{self.label}

[{color}]{emoji} {self.score:.1f}% - {status}[/{color}]

│{meter}│

0%                    50%                   100%
        """.strip()


class TrendChart(Static):
    """Simple ASCII line chart for trends."""
    
    DEFAULT_CSS = """
    TrendChart {
        height: auto;
        padding: 1;
    }
    """
    
    def __init__(self, data: list = None, title: str = "", **kwargs):
        super().__init__(**kwargs)
        self.data = data or []
        self.title = title
    
    def render_chart(self, height: int = 8) -> str:
        """Render ASCII line chart."""
        if not self.data or len(self.data) < 2:
            return "Not enough data for trend"
        
        lines = [f"📈 {self.title}" if self.title else ""]
        
        # Normalize data to chart height
        max_val = max(self.data)
        min_val = min(self.data)
        if max_val == min_val:
            max_val = min_val + 1
        
        normalized = [
            int((v - min_val) / (max_val - min_val) * (height - 1))
            for v in self.data
        ]
        
        # Build chart rows from top to bottom
        for row in range(height - 1, -1, -1):
            row_str = ""
            for val in normalized:
                if val >= row:
                    row_str += "█"
                else:
                    row_str += " "
            lines.append(f"│{row_str}│")
        
        # Bottom border
        lines.append("└" + "─" * len(self.data) + "┘")
        
        return "\n".join(lines)
    
    def on_mount(self):
        """Render on mount."""
        self.update(self.render_chart())


class NetworkTopology(Static):
    """ASCII network topology visualization."""
    
    DEFAULT_CSS = """
    NetworkTopology {
        height: auto;
        padding: 1;
    }
    """
    
    def __init__(self, devices: list = None, **kwargs):
        super().__init__(**kwargs)
        self.devices = devices or []
    
    def render_topology(self) -> str:
        """Render network topology diagram."""
        if not self.devices:
            return "No devices to display"
        
        lines = ["🗺️ Network Topology", ""]
        
        # Internet/WAN
        lines.append("         🌐 INTERNET")
        lines.append("            │")
        lines.append("            ▼")
        
        # Router (usually first or find router type)
        router = next((d for d in self.devices if d.get("type") == "router"), None)
        if router:
            lines.append(f"      ┌─────────────┐")
            lines.append(f"      │  🌐 ROUTER  │ {router.get('hostname', 'Unknown')}")
            lines.append(f"      │  {router.get('ip', 'N/A'):<11} │")
            lines.append(f"      └──────┬──────┘")
        else:
            lines.append("      ┌─────────────┐")
            lines.append("      │  🌐 GATEWAY │")
            lines.append("      └──────┬──────┘")
        
        lines.append("             │")
        lines.append("     ┌────────┴────────┐")
        
        # Group devices by type
        by_type = {}
        for d in self.devices:
            dev_type = d.get("type", "unknown")
            if dev_type != "router":
                by_type.setdefault(dev_type, []).append(d)
        
        # Show device counts by type
        lines.append("     │                 │")
        
        row_devices = []
        for dev_type, devices in list(by_type.items())[:4]:  # Max 4 types
            icon = {"switch": "🔀", "server": "🖥️", "workstation": "💻", 
                   "printer": "🖨️", "iot": "📱", "firewall": "🛡️"}.get(dev_type, "❓")
            row_devices.append(f"{icon} {len(devices)} {dev_type}")
        
        if row_devices:
            lines.append(f"  {row_devices[0] if len(row_devices) > 0 else '':<15} {row_devices[1] if len(row_devices) > 1 else '':<15}")
        if len(row_devices) > 2:
            lines.append(f"  {row_devices[2] if len(row_devices) > 2 else '':<15} {row_devices[3] if len(row_devices) > 3 else '':<15}")
        
        lines.append("")
        lines.append(f"Total devices: {len(self.devices)}")
        
        return "\n".join(lines)
    
    def on_mount(self):
        """Render on mount."""
        self.update(self.render_topology())


class SeverityDistribution(Static):
    """Severity distribution pie chart (ASCII representation)."""
    
    DEFAULT_CSS = """
    SeverityDistribution {
        height: auto;
        padding: 1;
    }
    """
    
    def __init__(self, counts: dict = None, **kwargs):
        super().__init__(**kwargs)
        self.counts = counts or {}
    
    def render_distribution(self) -> str:
        """Render severity distribution."""
        if not self.counts:
            return "No data"
        
        total = sum(self.counts.values())
        if total == 0:
            return "No findings"
        
        lines = ["📊 Finding Severity Distribution", ""]
        
        # Severity order and symbols
        severities = [
            ("critical", "🔴", "Critical"),
            ("high", "🟠", "High"),
            ("medium", "🟡", "Medium"),
            ("low", "🟢", "Low"),
            ("info", "⚪", "Info"),
        ]
        
        for sev, emoji, label in severities:
            count = self.counts.get(sev, 0)
            pct = (count / total * 100) if total > 0 else 0
            bar_len = int(pct / 5)  # 20 char max
            bar = "█" * bar_len + "░" * (20 - bar_len)
            lines.append(f"{emoji} {label:<8} │{bar}│ {count:>3} ({pct:>5.1f}%)")
        
        lines.append(f"\nTotal findings: {total}")
        
        return "\n".join(lines)
    
    def on_mount(self):
        """Render on mount."""
        self.update(self.render_distribution())


class DashboardSummary(Vertical):
    """Summary widget for dashboard."""
    
    DEFAULT_CSS = """
    DashboardSummary {
        height: auto;
        padding: 1;
        border: solid $primary;
    }
    """
    
    def __init__(self, stats: dict = None, **kwargs):
        super().__init__(**kwargs)
        self.stats = stats or {}
    
    def compose(self):
        # Top row - key metrics
        with Horizontal():
            yield Static(f"📋 Sessions: {self.stats.get('sessions', 0)}")
            yield Static(f"🔍 Devices: {self.stats.get('devices', 0)}")
            yield Static(f"⚠️ Findings: {self.stats.get('findings', 0)}")
            yield Static(f"📄 Reports: {self.stats.get('reports', 0)}")


# Utility functions for generating visualizations
def create_compliance_summary(scores: dict) -> str:
    """Create a compliance summary text."""
    lines = ["📊 Compliance Summary", ""]
    
    overall = scores.get('overall', 0)
    status = "✓ COMPLIANT" if overall >= 80 else "⚠ PARTIAL" if overall >= 50 else "✗ AT RISK"
    
    lines.append(f"Overall Score: {overall:.1f}% {status}")
    lines.append("")
    
    # Domain scores
    for domain, score in scores.items():
        if domain != 'overall':
            filled = int(score / 10)
            bar = "█" * filled + "░" * (10 - filled)
            lines.append(f"{domain:<20} │{bar}│ {score:.0f}%")
    
    return "\n".join(lines)


def create_status_indicator(status: str, message: str = "") -> str:
    """Create a status indicator."""
    indicators = {
        "ready": "🟢",
        "working": "🟡",
        "error": "🔴",
        "success": "✓",
        "warning": "⚠",
        "info": "ℹ",
    }
    emoji = indicators.get(status, "○")
    return f"{emoji} {message}" if message else emoji


def format_number_compact(n: int) -> str:
    """Format number in compact form."""
    if n >= 1000000:
        return f"{n/1000000:.1f}M"
    elif n >= 1000:
        return f"{n/1000:.1f}k"
    return str(n)


def create_mini_chart(values: list, width: int = 10) -> str:
    """Create a mini sparkline chart."""
    if not values or len(values) < 2:
        return "─" * width
    
    chars = "▁▂▃▄▅▆▇█"
    min_val = min(values)
    max_val = max(values)
    
    if max_val == min_val:
        return "─" * width
    
    # Sample values to fit width
    step = max(1, len(values) // width)
    sampled = values[::step][:width]
    
    result = ""
    for v in sampled:
        idx = int((v - min_val) / (max_val - min_val) * (len(chars) - 1))
        result += chars[idx]
    
    return result
