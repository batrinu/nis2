"""
Search and Filter Components - Loop 17
Powerful search, filtering, and sorting capabilities.
"""
from textual.widgets import Input, Static, Button, Select
from textual.containers import Horizontal, Vertical
from textual.reactive import reactive
from typing import List, Callable, Any
import re


class SmartSearch(Input):
    """Smart search input with suggestions."""
    
    DEFAULT_CSS = """
    SmartSearch {
        border: solid $surface-lighten-1;
    }
    
    SmartSearch:focus {
        border: solid $primary;
    }
    
    SmartSearch.active {
        border: solid $success;
    }
    """
    
    def __init__(self,
                 placeholder: str = "Search...",
                 search_fields: List[str] = None,
                 **kwargs):
        super().__init__(placeholder=placeholder, **kwargs)
        self.search_fields = search_fields or []
        self._search_callback: Optional[Callable] = None
    
    def watch_value(self, value: str):
        """Trigger search on value change."""
        if value:
            self.add_class("active")
        else:
            self.remove_class("active")
        
        self.post_message(self.SearchQuery(value))
    
    def set_search_callback(self, callback: Callable):
        """Set callback for search results."""
        self._search_callback = callback
    
    class SearchQuery:
        """Message sent when search query changes."""
        def __init__(self, query: str):
            self.query = query


class FilterChip(Static):
    """Filter chip that can be toggled."""
    
    DEFAULT_CSS = """
    FilterChip {
        width: auto;
        height: auto;
        padding: 0 1;
        margin: 0 1 0 0;
        border: solid $surface-lighten-1;
        background: $surface-darken-1;
        cursor: pointer;
    }
    
    FilterChip:hover {
        background: $surface-lighten-1;
    }
    
    FilterChip.active {
        background: $primary;
        color: $text;
        border-color: $primary;
    }
    """
    
    def __init__(self, label: str, filter_key: str, filter_value: Any, **kwargs):
        super().__init__(**kwargs)
        self.chip_label = label
        self.filter_key = filter_key
        self.filter_value = filter_value
        self.active = False
    
    def compose(self):
        yield Static(self.chip_label)
    
    def on_click(self):
        """Toggle active state."""
        self.active = not self.active
        if self.active:
            self.add_class("active")
        else:
            self.remove_class("active")
        
        self.post_message(self.FilterToggled(
            self.filter_key,
            self.filter_value,
            self.active
        ))
    
    class FilterToggled:
        """Message sent when filter is toggled."""
        def __init__(self, key: str, value: Any, active: bool):
            self.key = key
            self.value = value
            self.active = active


class FilterBar(Horizontal):
    """Bar containing filter chips."""
    
    DEFAULT_CSS = """
    FilterBar {
        height: auto;
        margin: 1 0;
    }
    
    #filter-label {
        width: 10;
        text-style: bold;
        align: center middle;
    }
    
    #filter-chips {
        width: 1fr;
        height: auto;
    }
    
    #filter-clear {
        width: auto;
    }
    """
    
    def __init__(self, filters: List[Dict], **kwargs):
        super().__init__(**kwargs)
        self.available_filters = filters
        self.active_filters: Dict[str, Any] = {}
    
    def compose(self):
        yield Static("Filter:", id="filter-label")
        
        with Horizontal(id="filter-chips"):
            for f in self.available_filters:
                yield FilterChip(
                    f["label"],
                    f["key"],
                    f["value"]
                )
        
        yield Button("Clear", id="filter-clear")
    
    def on_filter_chip_filter_toggled(self, event: FilterChip.FilterToggled):
        """Handle filter toggle."""
        if event.active:
            if event.key not in self.active_filters:
                self.active_filters[event.key] = []
            self.active_filters[event.key].append(event.value)
        else:
            if event.key in self.active_filters:
                if event.value in self.active_filters[event.key]:
                    self.active_filters[event.key].remove(event.value)
        
        self.post_message(self.FiltersChanged(self.active_filters))
    
    def on_button_pressed(self, event):
        """Clear all filters."""
        if event.button.id == "filter-clear":
            self.active_filters.clear()
            # Reset all chips
            for chip in self.query(FilterChip):
                chip.active = False
                chip.remove_class("active")
            self.post_message(self.FiltersChanged(self.active_filters))
    
    class FiltersChanged:
        """Message sent when filters change."""
        def __init__(self, filters: Dict[str, Any]):
            self.filters = filters


class SortSelector(Vertical):
    """Sort order selector."""
    
    DEFAULT_CSS = """
    SortSelector {
        width: auto;
        height: auto;
    }
    
    #sort-label {
        text-style: bold;
        margin-bottom: 1;
    }
    """
    
    sort_field = reactive("")
    sort_ascending = reactive(True)
    
    def __init__(self, fields: List[tuple], **kwargs):
        super().__init__(**kwargs)
        self.sort_fields = fields  # [(label, value), ...]
    
    def compose(self):
        yield Static("Sort by:", id="sort-label")
        yield Select(self.sort_fields, id="sort-field")
        yield Button("▲ Ascending", id="sort-direction")
    
    def on_select_changed(self, event):
        """Handle field change."""
        if event.select.id == "sort-field":
            self.sort_field = event.value or ""
            self._notify_change()
    
    def on_button_pressed(self, event):
        """Toggle sort direction."""
        if event.button.id == "sort-direction":
            self.sort_ascending = not self.sort_ascending
            event.button.label = "▲ Ascending" if self.sort_ascending else "▼ Descending"
            self._notify_change()
    
    def _notify_change(self):
        """Notify parent of sort change."""
        self.post_message(self.SortChanged(
            self.sort_field,
            self.sort_ascending
        ))
    
    class SortChanged:
        """Message sent when sort changes."""
        def __init__(self, field: str, ascending: bool):
            self.field = field
            self.ascending = ascending


class SearchHighlighter:
    """Utility to highlight search terms in text."""
    
    def __init__(self, query: str, case_sensitive: bool = False):
        self.query = query
        self.case_sensitive = case_sensitive
    
    def highlight(self, text: str) -> str:
        """Highlight search terms in text."""
        if not self.query:
            return text
        
        flags = 0 if self.case_sensitive else re.IGNORECASE
        pattern = re.compile(re.escape(self.query), flags)
        
        return pattern.sub(f"[bold reverse]{self.query}[/]", text)
    
    def matches(self, text: str) -> bool:
        """Check if text matches query."""
        if not self.query:
            return True
        
        flags = 0 if self.case_sensitive else re.IGNORECASE
        return bool(re.search(re.escape(self.query), text, flags))


class Paginator(Static):
    """Pagination controls."""
    
    DEFAULT_CSS = """
    Paginator {
        height: auto;
        align: center middle;
        margin: 1 0;
    }
    
    #page-info {
        margin: 0 2;
        text-style: bold;
    }
    
    Paginator Button {
        margin: 0 1;
    }
    
    Paginator Button:disabled {
        visibility: hidden;
    }
    """
    
    current_page = reactive(1)
    total_pages = reactive(1)
    
    def __init__(self, items_per_page: int = 10, **kwargs):
        super().__init__(**kwargs)
        self.items_per_page = items_per_page
        self.total_items = 0
    
    def compose(self):
        yield Button("◀ First", id="btn-first")
        yield Button("← Previous", id="btn-prev")
        yield Static("Page 1 of 1", id="page-info")
        yield Button("Next →", id="btn-next")
        yield Button("Last ▶", id="btn-last")
    
    def set_total_items(self, total: int):
        """Set total number of items."""
        self.total_items = total
        self.total_pages = max(1, (total + self.items_per_page - 1) // self.items_per_page)
        self._update_ui()
    
    def watch_current_page(self, page: int):
        """Update UI when page changes."""
        self._update_ui()
        self.post_message(self.PageChanged(page))
    
    def _update_ui(self):
        """Update UI elements."""
        try:
            info = self.query_one("#page-info", Static)
            info.update(f"Page {self.current_page} of {self.total_pages}")
            
            # Update button states
            first_btn = self.query_one("#btn-first", Button)
            prev_btn = self.query_one("#btn-prev", Button)
            next_btn = self.query_one("#btn-next", Button)
            last_btn = self.query_one("#btn-last", Button)
            
            first_btn.disabled = self.current_page == 1
            prev_btn.disabled = self.current_page == 1
            next_btn.disabled = self.current_page >= self.total_pages
            last_btn.disabled = self.current_page >= self.total_pages
            
        except Exception:
            pass
    
    def on_button_pressed(self, event):
        """Handle pagination."""
        if event.button.id == "btn-first":
            self.current_page = 1
        elif event.button.id == "btn-prev":
            if self.current_page > 1:
                self.current_page -= 1
        elif event.button.id == "btn-next":
            if self.current_page < self.total_pages:
                self.current_page += 1
        elif event.button.id == "btn-last":
            self.current_page = self.total_pages
    
    class PageChanged:
        """Message sent when page changes."""
        def __init__(self, page: int):
            self.page = page


class ResultsCounter(Static):
    """Display result count with filter status."""
    
    DEFAULT_CSS = """
    ResultsCounter {
        height: auto;
        color: $text-muted;
        text-style: italic;
        margin: 1 0;
    }
    
    ResultsCounter.filtered {
        color: $primary;
    }
    """
    
    total = reactive(0)
    showing = reactive(0)
    
    def watch_showing(self, value: int):
        """Update display."""
        if value != self.total:
            self.add_class("filtered")
            self.update(f"Showing {value} of {self.total} results")
        else:
            self.remove_class("filtered")
            self.update(f"{self.total} results")


class QuickFilter(Button):
    """Quick filter button for common filters."""
    
    DEFAULT_CSS = """
    QuickFilter {
        margin: 0 1;
    }
    
    QuickFilter.active {
        background: $primary;
    }
    """
    
    def __init__(self, label: str, filter_fn: Callable, **kwargs):
        super().__init__(label, **kwargs)
        self.filter_fn = filter_fn
        self.active = False
    
    def on_click(self):
        """Toggle filter."""
        self.active = not self.active
        if self.active:
            self.add_class("active")
        else:
            self.remove_class("active")
        
        self.post_message(self.QuickFilterToggled(self.filter_fn, self.active))
    
    class QuickFilterToggled:
        """Message sent when quick filter toggles."""
        def __init__(self, filter_fn: Callable, active: bool):
            self.filter_fn = filter_fn
            self.active = active


# Filter functions

def filter_by_severity(items: List[Dict], severities: List[str]) -> List[Dict]:
    """Filter items by severity."""
    return [item for item in items if item.get("severity", "").lower() in [s.lower() for s in severities]]


def filter_by_status(items: List[Dict], statuses: List[str]) -> List[Dict]:
    """Filter items by status."""
    return [item for item in items if item.get("status", "").lower() in [s.lower() for s in statuses]]


def filter_by_date_range(items: List[Dict], start_date: str, end_date: str) -> List[Dict]:
    """Filter items by date range."""
    # Implementation would parse dates and compare
    return items


def search_items(items: List[Dict], query: str, fields: List[str]) -> List[Dict]:
    """Search items across multiple fields."""
    if not query:
        return items
    
    query_lower = query.lower()
    results = []
    
    for item in items:
        for field in fields:
            value = str(item.get(field, "")).lower()
            if query_lower in value:
                results.append(item)
                break
    
    return results
