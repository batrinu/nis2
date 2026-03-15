"""
Data Visualization Components - Loop 16
Charts, graphs, and visual data representation for TUI.
"""
from textual.widgets import Static
from textual.containers import Vertical, Horizontal
from textual.reactive import reactive
from typing import List, Tuple, Optional, Dict, Any
import math


class BarChart(Static):
    """ASCII bar chart."""
    
    DEFAULT_CSS = """
    BarChart {
        width: 100%;
        height: auto;
        padding: 1;
    }
    
    #bc-title {
        text-style: bold;
        text-align: center;
        margin-bottom: 1;
    }
    
    .bc-row {
        height: auto;
        margin: 0 1;
    }
    
    .bc-label {
        width: 15;
        text-align: right;
        margin-right: 1;
    }
    
    .bc-bar-container {
        width: 1fr;
    }
    
    .bc-bar {
        background: $primary;
        color: $text;
        text-style: bold;
    }
    
    .bc-value {
        width: 8;
        text-align: right;
        margin-left: 1;
    }
    
    #bc-scale {
        text-align: center;
        color: $text-muted;
        margin-top: 1;
    }
    """
    
    def __init__(self,
                 data: List[Tuple[str, float]],
                 title: str = "",
                 max_bar_width: int = 30,
                 unit: str = "",
                 **kwargs):
        super().__init__(**kwargs)
        self.chart_data = data
        self.chart_title = title
        self.max_bar_width = max_bar_width
        self.unit = unit
    
    def compose(self):
        if self.chart_title:
            yield Static(self.chart_title, id="bc-title")
        
        # Find max value for scaling
        max_value = max(v for _, v in self.chart_data) if self.chart_data else 1
        
        for label, value in self.chart_data:
            with Horizontal(classes="bc-row"):
                yield Static(label, classes="bc-label")
                
                # Calculate bar width
                bar_width = int((value / max_value) * self.max_bar_width) if max_value > 0 else 0
                bar_char = "█" * bar_width
                
                yield Static(bar_char, classes="bc-bar")
                yield Static(f"{value:.0f}{self.unit}", classes="bc-value")
        
        # Scale
        yield Static(f"0{' ' * (self.max_bar_width - 5)}{max_value:.0f}{self.unit}", id="bc-scale")


class HorizontalBarChart(Static):
    """Horizontal bar chart (stacked bars)."""
    
    DEFAULT_CSS = """
    HorizontalBarChart {
        width: 100%;
        height: auto;
        padding: 1;
    }
    
    #hbc-title {
        text-style: bold;
        text-align: center;
        margin-bottom: 1;
    }
    
    .hbc-bar {
        height: 2;
        margin: 1 0;
        border: solid $surface-lighten-1;
    }
    
    .hbc-label {
        text-align: center;
        margin-top: 1;
    }
    """
    
    def __init__(self,
                 data: List[Tuple[str, float, str]],  # (label, value, color_class)
                 title: str = "",
                 width: int = 40,
                 **kwargs):
        super().__init__(**kwargs)
        self.chart_data = data
        self.chart_title = title
        self.chart_width = width
    
    def compose(self):
        if self.chart_title:
            yield Static(self.chart_title, id="hbc-title")
        
        total = sum(v for _, v, _ in self.chart_data) if self.chart_data else 1
        
        # Build stacked bar
        bar_parts = []
        for label, value, color in self.chart_data:
            width = int((value / total) * self.chart_width) if total > 0 else 0
            if width > 0:
                bar_parts.append((label, width, value, color))
        
        # Render bar
        bar_text = ""
        for label, width, value, color in bar_parts:
            bar_text += "█" * width
        
        yield Static(bar_text, classes="hbc-bar")
        
        # Legend
        legend_parts = []
        for label, _, value, _ in bar_parts:
            pct = (value / total * 100) if total > 0 else 0
            legend_parts.append(f"{label}: {pct:.0f}%")
        
        yield Static(" | ".join(legend_parts), classes="hbc-label")


class Sparkline(Static):
    """Sparkline chart for trends."""
    
    DEFAULT_CSS = """
    Sparkline {
        width: auto;
        height: auto;
    }
    """
    
    CHARS = "▁▂▃▄▅▆▇█"
    
    def __init__(self, data: List[float], width: int = 20, **kwargs):
        super().__init__(**kwargs)
        self.spark_data = data
        self.spark_width = width
    
    def on_mount(self):
        """Render sparkline."""
        if not self.spark_data:
            self.update("")
            return
        
        # Normalize data to 0-7 range
        min_val = min(self.spark_data)
        max_val = max(self.spark_data)
        
        if max_val == min_val:
            normalized = [0] * len(self.spark_data)
        else:
            normalized = [
                int(((v - min_val) / (max_val - min_val)) * 7)
                for v in self.spark_data
            ]
        
        # Sample if too many points
        if len(normalized) > self.spark_width:
            step = len(normalized) / self.spark_width
            sampled = []
            for i in range(self.spark_width):
                idx = int(i * step)
                sampled.append(normalized[idx])
            normalized = sampled
        
        # Build sparkline
        spark = "".join(self.CHARS[v] for v in normalized)
        self.update(spark)


class Gauge(Static):
    """Gauge/progress indicator with visual."""
    
    DEFAULT_CSS = """
    Gauge {
        width: auto;
        height: auto;
        text-align: center;
        padding: 1;
    }
    
    #gauge-title {
        margin-bottom: 1;
    }
    
    #gauge-visual {
        text-style: bold;
        font-size: 2;
    }
    
    #gauge-value {
        margin-top: 1;
        text-style: bold;
    }
    
    Gauge.success #gauge-visual { color: $success; }
    Gauge.warning #gauge-visual { color: $warning; }
    Gauge.error #gauge-visual { color: $error; }
    """
    
    GAUGE_CHARS = ["○", "◔", "◑", "◕", "●"]
    
    def __init__(self, value: float, max_value: float = 100, title: str = "", **kwargs):
        super().__init__(**kwargs)
        self.gauge_value = value
        self.max_value = max_value
        self.gauge_title = title
    
    def compose(self):
        if self.gauge_title:
            yield Static(self.gauge_title, id="gauge-title")
        
        # Calculate gauge level
        ratio = self.gauge_value / self.max_value if self.max_value > 0 else 0
        level = min(int(ratio * 4), 4)
        
        # Set color class
        if ratio >= 0.8:
            self.add_class("success")
        elif ratio >= 0.5:
            self.add_class("warning")
        else:
            self.add_class("error")
        
        yield Static(self.GAUGE_CHARS[level], id="gauge-visual")
        yield Static(f"{self.gauge_value:.0f}%", id="gauge-value")


class ComplianceScore(Static):
    """Compliance score display with color coding."""
    
    DEFAULT_CSS = """
    ComplianceScore {
        width: auto;
        height: auto;
        text-align: center;
        padding: 2;
        border: thick;
    }
    
    ComplianceScore.excellent {
        border-color: $success;
        background: $success-darken-3;
    }
    
    ComplianceScore.good {
        border-color: $warning;
        background: $warning-darken-3;
    }
    
    ComplianceScore.needs-work {
        border-color: $error;
        background: $error-darken-3;
    }
    
    #cs-score {
        text-style: bold;
        font-size: 4;
    }
    
    ComplianceScore.excellent #cs-score { color: $success; }
    ComplianceScore.good #cs-score { color: $warning; }
    ComplianceScore.needs-work #cs-score { color: $error; }
    
    #cs-label {
        margin-top: 1;
        text-style: bold;
    }
    
    #cs-detail {
        color: $text-muted;
        text-style: italic;
        margin-top: 1;
    }
    """
    
    def __init__(self, score: float, label: str = "Compliance Score", **kwargs):
        super().__init__(**kwargs)
        self.score = score
        self.label = label
    
    def compose(self):
        # Determine rating
        if self.score >= 90:
            rating = "excellent"
            detail = "Excellent! NIS2 Ready"
        elif self.score >= 70:
            rating = "good"
            detail = "Good progress, some gaps to address"
        else:
            rating = "needs-work"
            detail = "Needs attention - significant gaps found"
        
        self.add_class(rating)
        
        yield Static(f"{self.score:.0f}%", id="cs-score")
        yield Static(self.label, id="cs-label")
        yield Static(detail, id="cs-detail")


class Timeline(Static):
    """Timeline visualization."""
    
    DEFAULT_CSS = """
    Timeline {
        width: 100%;
        height: auto;
        padding: 1;
    }
    
    #timeline-title {
        text-style: bold;
        text-align: center;
        margin-bottom: 1;
    }
    
    .timeline-event {
        height: auto;
        margin: 1 0;
        padding-left: 3;
        border-left: solid $surface-lighten-1;
    }
    
    .timeline-event.completed {
        border-left-color: $success;
    }
    
    .timeline-event.current {
        border-left-color: $primary;
        border-left: thick $primary;
    }
    
    .timeline-event.pending {
        border-left-color: $text-muted;
    }
    
    .event-time {
        color: $text-muted;
        text-style: italic;
        font-size: 0.8;
    }
    
    .event-title {
        text-style: bold;
    }
    
    .event-desc {
        color: $text-muted;
    }
    """
    
    def __init__(self, events: List[Dict], title: str = "Timeline", **kwargs):
        super().__init__(**kwargs)
        self.events = events  # [{"time": str, "title": str, "description": str, "status": str}]
        self.timeline_title = title
    
    def compose(self):
        yield Static(self.timeline_title, id="timeline-title")
        
        for event in self.events:
            status = event.get("status", "pending")
            with Vertical(classes=f"timeline-event {status}"):
                yield Static(event.get("time", ""), classes="event-time")
                yield Static(event.get("title", ""), classes="event-title")
                if event.get("description"):
                    yield Static(event["description"], classes="event-desc")


class PieChart(Static):
    """Simple ASCII pie chart."""
    
    DEFAULT_CSS = """
    PieChart {
        width: auto;
        height: auto;
        text-align: center;
        padding: 1;
    }
    
    #pie-title {
        text-style: bold;
        margin-bottom: 1;
    }
    
    #pie-visual {
        text-style: bold;
    }
    
    #pie-legend {
        margin-top: 1;
        text-align: left;
    }
    """
    
    PIE_CHARS = ["◴", "◵", "◶", "◷"]
    COLORS = ["primary", "success", "warning", "error", "text"]
    
    def __init__(self, data: List[Tuple[str, float]], title: str = "", **kwargs):
        super().__init__(**kwargs)
        self.pie_data = data
        self.pie_title = title
    
    def compose(self):
        if self.pie_title:
            yield Static(self.pie_title, id="pie-title")
        
        total = sum(v for _, v in self.pie_data) if self.pie_data else 1
        
        # Simple representation using characters
        segments = []
        for i, (label, value) in enumerate(self.pie_data):
            pct = (value / total * 100) if total > 0 else 0
            char = self.PIE_CHARS[i % len(self.PIE_CHARS)]
            segments.append(f"{char} {label}: {pct:.0f}%")
        
        yield Static("  ".join(self.PIE_CHARS[:len(self.pie_data)]), id="pie-visual")
        yield Static("\n".join(segments), id="pie-legend")


class SeverityBadge(Static):
    """Badge showing severity level with color."""
    
    DEFAULT_CSS = """
    SeverityBadge {
        width: auto;
        height: auto;
        padding: 0 1;
        text-style: bold;
    }
    
    SeverityBadge.critical {
        background: $error;
        color: $text;
    }
    
    SeverityBadge.high {
        background: $error-darken-2;
        color: $text;
    }
    
    SeverityBadge.medium {
        background: $warning;
        color: $text;
    }
    
    SeverityBadge.low {
        background: $success;
        color: $text;
    }
    """
    
    def __init__(self, severity: str, **kwargs):
        super().__init__(**kwargs)
        self.severity = severity.lower()
        self.add_class(self.severity)
    
    def compose(self):
        yield Static(self.severity.upper())


class TrendIndicator(Static):
    """Indicator showing trend direction."""
    
    DEFAULT_CSS = """
    TrendIndicator {
        width: auto;
        height: auto;
    }
    
    TrendIndicator.up {
        color: $success;
    }
    
    TrendIndicator.down {
        color: $error;
    }
    
    TrendIndicator.flat {
        color: $text-muted;
    }
    """
    
    def __init__(self, current: float, previous: float, **kwargs):
        super().__init__(**kwargs)
        self.current = current
        self.previous = previous
    
    def compose(self):
        diff = self.current - self.previous
        
        if diff > 0:
            self.add_class("up")
            icon = "▲"
            sign = "+"
        elif diff < 0:
            self.add_class("down")
            icon = "▼"
            sign = ""
        else:
            self.add_class("flat")
            icon = "▶"
            sign = ""
        
        pct = abs(diff / self.previous * 100) if self.previous != 0 else 0
        yield Static(f"{icon} {sign}{pct:.1f}%")


class MetricCard(Static):
    """Card displaying a metric with optional trend."""
    
    DEFAULT_CSS = """
    MetricCard {
        width: auto;
        height: auto;
        min-width: 20;
        border: solid $surface-lighten-1;
        background: $surface-darken-1;
        padding: 1;
        margin: 0 1;
    }
    
    #metric-label {
        color: $text-muted;
        text-style: italic;
        font-size: 0.8;
    }
    
    #metric-value {
        text-style: bold;
        font-size: 2;
        margin: 1 0;
    }
    
    #metric-delta {
        color: $text-muted;
        font-size: 0.8;
    }
    """
    
    def __init__(self,
                 label: str,
                 value: str,
                 delta: str = "",
                 **kwargs):
        super().__init__(**kwargs)
        self.metric_label = label
        self.metric_value = value
        self.metric_delta = delta
    
    def compose(self):
        yield Static(self.metric_label, id="metric-label")
        yield Static(self.metric_value, id="metric-value")
        if self.metric_delta:
            yield Static(self.metric_delta, id="metric-delta")
