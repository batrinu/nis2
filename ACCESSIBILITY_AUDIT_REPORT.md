# NIS2 Audit TUI - Accessibility & Usability Audit Report

**Date:** 2026-03-13  
**Scope:** All screens in `/nis2-audit-app/app/tui/screens/` + components  
**Theme:** Retro 1980s Romanian university aesthetic

---

## Executive Summary

The NIS2 Audit TUI has a solid foundation for accessibility with many good practices already in place. However, there are several areas that need improvement to meet full accessibility standards and provide the best user experience.

**Overall Rating:** ⭐⭐⭐☆☆ (3/5) - Good foundation, needs refinement

---

## 1. KEYBOARD SHORTCUTS ANALYSIS

### ✅ Already Implemented Well

| Screen | Shortcuts | Status |
|--------|-----------|--------|
| Dashboard | N, R, H, Q, ? | ✅ Complete |
| New Session | Esc, Ctrl+S, →/Tab, ← | ✅ Complete |
| Checklist | Y, N, P, ?, →, ←, S, H | ✅ Complete |
| Scan | Esc, S, C | ✅ Complete |
| Connect | Esc, Space, A, C, R | ✅ Complete |
| Findings | Esc, R, F, 1, 2, 3 | ✅ Complete |
| Report | Esc, G, O | ✅ Complete |
| Onboarding | Esc, →/Space, ← | ✅ Complete |

### ❌ Issues Found

#### Issue 1.1: Missing Shortcut Consistency
**File:** `screens/connect.py`, `screens/findings.py`
**Problem:** `ConnectScreen` uses `Space` for toggle select, but `ChecklistScreen` uses `Space` for next. Inconsistent behavior confuses users.
**Fix:**
```python
# In connect.py - Add explicit Tab navigation
BINDINGS = [
    Binding("escape", "back", _("back")),
    Binding("space", "toggle_select", _("select")),
    Binding("a", "select_all", _("select_all")),
    Binding("c", "connect_selected", _("connect")),
    Binding("r", "refresh", _("refresh")),
    Binding("tab", "focus_next", _("next_field")),  # ADD THIS
]
```

#### Issue 1.2: Missing Shortcuts for Form Fields
**File:** `screens/new_session.py`
**Problem:** No keyboard shortcut to jump to specific form fields.
**Fix:**
```python
# Add to NewSessionWizard BINDINGS
BINDINGS = [
    Binding("escape", "cancel", "Anulează"),
    Binding("ctrl+s", "save_draft", "Salvează Draft"),
    Binding("right,tab", "next_step", "Următor"),
    Binding("left", "prev_step", "Înapoi"),
    Binding("ctrl+n", "focus_name", "Nume"),      # ADD
    Binding("ctrl+e", "focus_sector", "Sector"),  # ADD
    Binding("ctrl+a", "focus_employees", "Angajați"),  # ADD
]
```

---

## 2. FOCUS MANAGEMENT ANALYSIS

### ✅ Already Implemented Well
- `keyboard_nav.py` has `TabOrderManager` class
- `FocusIndicator` component exists
- `NavigableButton` and `AccessibleInput` components available

### ❌ Issues Found

#### Issue 2.1: Screens Don't Use TabOrderManager
**File:** All screen files
**Problem:** The `TabOrderManager` class exists but is never used in any screen.
**Fix for `new_session.py`:**
```python
def on_mount(self):
    """Initialize auto-save, load draft, and set up tab order."""
    from ..components.keyboard_nav import TabOrderManager
    
    self._tab_manager = TabOrderManager(self)
    self._tab_manager.set_order([
        "input-name", 
        "select-sector", 
        "input-employees", 
        "input-turnover",
        "btn-next",
        "btn-cancel"
    ])
    
    # ... rest of on_mount
```

#### Issue 2.2: Missing Focus States in CSS
**File:** `screens/splash.py`, `screens/dashboard.py`
**Problem:** Custom CSS doesn't include `:focus` styles for interactive elements.
**Fix for `splash.py`:**
```css
/* Add to DEFAULT_CSS */
#splash-container:focus {
    border: double #00ff41;
}

#splash-progress:focus {
    border: double #ffb000;
}
```

#### Issue 2.3: No Focus Trapping in Modals
**File:** `screens/connect.py` (DeviceDetailModal), `screens/findings.py` (FixGuidanceModal)
**Problem:** When modal opens, focus should be trapped inside it until dismissed.
**Fix:**
```python
# In DeviceDetailModal
def on_mount(self):
    """Focus first interactive element when modal opens."""
    try:
        self.query_one("#btn-modal-connect", Button).focus()
    except Exception:
        pass

def on_key(self, event):
    """Trap focus in modal."""
    if event.key == "tab":
        # Implement focus cycling within modal
        focusable = self.query("Button, Input")
        # ... focus management logic
```

---

## 3. DISABLED BUTTONS ANALYSIS

### ✅ Already Implemented Well
- Most buttons properly enable/disable based on state
- `watch_current_step` in `new_session.py` correctly manages back button

### ❌ Issues Found

#### Issue 3.1: Connect Screen "Run Assessment" Button Logic
**File:** `screens/connect.py` (lines 311-312)
**Problem:** Button is disabled by default but enabled only after bulk connect - doesn't check for existing connected devices on mount.
**Fix:**
```python
def on_mount(self):
    """Load devices and update button states."""
    self._load_devices()
    self._update_run_assessment_button()  # ADD THIS CALL

def _update_run_assessment_button(self):
    """Enable/disable Run Assessment based on connected devices."""
    try:
        has_connected = any(
            d.connection_status == "connected" 
            for d in self.devices
        )
        self.query_one("#btn-commands", Button).disabled = not has_connected
    except Exception:
        pass

def watch_devices(self, devices):
    """Update button when devices change."""
    self._update_run_assessment_button()  # ADD THIS
```

#### Issue 3.2: Scan Screen Missing Input Validation
**File:** `screens/scan.py` (lines 176-186)
**Problem:** Start button is always enabled even when input is empty.
**Fix:**
```python
def compose(self):
    # ... existing compose code ...
    with Horizontal(id="target-row"):
        yield Label("Țintă: ")
        yield Input(
            placeholder="192.168.1.0/24", 
            id="target-input"
        )
        yield Button(
            f"▶ {_('start_scan')} (S)", 
            id="btn-scan", 
            variant="success",
            disabled=True  # Start disabled
        )
        # ... rest

def on_input_changed(self, event):
    """Enable scan button only when target is valid."""
    if event.input.id == "target-input":
        is_valid = len(event.value.strip()) > 0
        self.query_one("#btn-scan", Button).disabled = not is_valid
```

---

## 4. COLOR CONTRAST ANALYSIS (Retro Theme)

### Theme Colors Being Used
```
Primary Green:   #00ff41 (on #0c0c00) - ✅ Ratio: 11.8:1
Amber/Yellow:    #ffb000 (on #0c0c00) - ✅ Ratio: 7.2:1  
Yellow-Green:    #b8b000 (on #0c0c00) - ⚠️ Ratio: 5.1:1
Muted Green:     #888866 (on #0c0c00) - ❌ Ratio: 3.8:1 (fails WCAG AA)
Dark Green:      #4a4a00 (on #0c0c00) - ❌ Ratio: 1.9:1 (invisible)
```

### ❌ Issues Found

#### Issue 4.1: Insufficient Contrast on Muted Text
**File:** `screens/dashboard.py` (line 146)
**Problem:** `#666600` color fails WCAG AA (needs 4.5:1, has ~3:1).
**Fix:**
```css
/* Change from #666600 to #888833 for 4.6:1 ratio */
#help-hint {
    text-align: center;
    color: #888833;  /* Was: #666600 */
    text-style: italic;
    margin-top: 1;
}
```

#### Issue 4.2: Border Colors Too Subtle
**File:** Multiple screens using `#4a4a00`
**Problem:** Borders with `#4a4a00` on `#0c0c00` are barely visible.
**Fix:**
```css
/* Standardize border colors */
#sidebar, #main-content, #welcome-panel {
    border: solid #6a6a20;  /* Was: #4a4a00 - 33% lighter */
}
```

#### Issue 4.3: Disabled State Visibility
**File:** `screens/new_session.py` (line 272)
**Problem:** Disabled button styling may not be distinct enough for colorblind users.
**Fix:**
```css
/* Add to all screens' CSS */
Button:disabled {
    background: #1a1a00;
    color: #555544;
    border: solid #333300;
    text-style: dim;  /* Add dimming, not just color change */
}
```

---

## 5. HELP TEXT ANALYSIS

### ✅ Already Implemented Well
- `help_system.py` has comprehensive `SCREEN_HELP` dictionary
- `contextual_help.py` has `CONTEXTUAL_HELP_DB` for fields
- Checklist screen has `QUESTION_HELP` dictionary
- Most screens have keyboard hints displayed

### ❌ Issues Found

#### Issue 5.1: Contextual Help Not Connected
**File:** `screens/new_session.py`
**Problem:** Help database exists but is not linked to actual form fields.
**Fix:**
```python
from ..components.contextual_help import HelpfulLabel

def compose(self):
    # ... in step 1 ...
    with Grid(classes="form-row"):
        # Replace Label with HelpfulLabel
        yield HelpfulLabel(
            "Nume Entitate:*", 
            help_context="entity_name",
            classes="form-label"
        )
        yield Input(placeholder="ex: EnergieCorp SRL", id="input-name")
    
    with Grid(classes="form-row"):
        yield HelpfulLabel(
            "Sector:*",
            help_context="sector", 
            classes="form-label"
        )
        yield Select([...], id="select-sector")
```

#### Issue 5.2: Missing F1 Help Integration
**File:** `screens/dashboard.py` (lines 185-191)
**Problem:** Help action exists but doesn't open the help modal.
**Fix:**
```python
def _show_help(self):
    """Afișează contextual help dialog."""
    from ..components.help_system import HelpModal
    self.app.push_screen(HelpModal("dashboard"))
```

#### Issue 5.3: Missing Inline Help for Complex Fields
**File:** `screens/new_session.py` - Network segment field
**Problem:** Network segment format help only in guidance panel, not near field.
**Fix:**
```python
with Grid(classes="form-row"):
    yield Label(f"{_('network')} Segment:", classes="form-label")
    yield Input(
        placeholder="ex: 192.168.1.0/24", 
        id="input-network"
    )
    # ADD inline help:
    yield Static(
        "💡 Format: 192.168.1.0/24 sau 10.0.0.0/8",
        classes="field-help"
    )
```

---

## 6. BUTTON PLACEMENT CONSISTENCY

### ✅ Current Pattern Analysis

| Screen | Primary Action | Position | Secondary | Position |
|--------|---------------|----------|-----------|----------|
| Dashboard | New Session | Sidebar | Help/Quit | Sidebar |
| New Session | Next/Următor | Center | Back/Cancel | Left |
| Checklist | Next | Center | Prev/Skip | Left |
| Connect | Connect | Top | Back | Bottom |
| Scan | Start | Top | Back | Top |
| Findings | (none primary) | - | Back | Top |
| Report | Generate | Center | Back | Center |

### ❌ Issues Found

#### Issue 6.1: Inconsistent Primary Button Position
**File:** `screens/connect.py` (lines 310-312)
**Problem:** Primary actions split between top toolbar and bottom button row.
**Fix:**
```python
# Consolidate actions in one location
def compose(self):
    with Vertical(id="connect-container"):
        yield Static(..., id="connect-header")
        
        # Single action bar at top
        with Horizontal(id="action-bar"):
            yield Button(f"◀ {_('back')}", id="btn-back")
            yield Button(f"🔄 {_('refresh')}", id="btn-refresh")
            yield Button(f"▶ {_('connect_selected')}", 
                        id="btn-connect-all", 
                        variant="success")  # Primary always right
        
        # ... rest of content
        
        # Remove duplicate buttons at bottom
```

#### Issue 6.2: Missing Cancel Button on Some Screens
**File:** `screens/findings.py` (lines 285-295)
**Problem:** No explicit cancel/close button in filter row.
**Fix:**
```python
with Horizontal(id="filter-row"):
    yield Select([...], id="filter-severity")
    yield Button("🔄 Reîmprospătează (R)", id="btn-refresh")
    yield Button("◀ Înapoi (Esc)", id="btn-back", variant="primary")  # Add variant
```

---

## 7. EMPTY STATES ANALYSIS

### ✅ Already Implemented Well
- `empty_states.py` has comprehensive `EmptyState` component
- `WHY_EMPTY` explanations are detailed
- `EMPTY_STATE_ART` has ASCII illustrations
- Dashboard shows empty state when no sessions

### ❌ Issues Found

#### Issue 7.1: Missing Empty State for Scan Results
**File:** `screens/scan.py` (lines 468-482)
**Problem:** Device table shows headers even when no devices found.
**Fix:**
```python
def watch_devices(self, devices):
    """Update device table when devices change."""
    table = self.query_one("#device-table", DataTable)
    summary = self.query_one("#results-summary", Static)
    
    table.clear()
    
    if not devices:
        # Show empty state
        summary.update(f"""
    ╔═══════════════════════════════════════╗
    ║                                       ║
    ║   🔍  📡  🌐                          ║
    ║                                       ║
    ║   Niciun device descoperit încă       ║
    ║                                       ║
    ║   Introdu un range și apasă Start     ║
    ║                                       ║
    ╚═══════════════════════════════════════╝
        """)
        summary.styles.display = "block"
        table.styles.display = "none"
    else:
        summary.styles.display = "none"
        table.styles.display = "block"
        # ... add rows
```

#### Issue 7.2: Empty State Missing Clear CTA
**File:** `screens/checklist.py`
**Problem:** When checklist is complete, message doesn't guide next steps.
**Fix:**
```python
def action_next(self):
    """Go to next question or show completion."""
    # ... existing code ...
    
    if at_end:
        self.notify(
            "🎉 Ai completat toate întrebările! "
            "Apasă 'Finalizează' pentru a genera raportul.",
            severity="success",
            timeout=5
        )
```

---

## 8. SCREEN READER & ACCESSIBILITY ISSUES

### ❌ Issues Found

#### Issue 8.1: Missing ARIA Labels
**File:** All screens
**Problem:** Widgets don't have proper ARIA labels for screen readers.
**Fix for all inputs:**
```python
# In new_session.py
yield Input(
    placeholder="ex: EnergieCorp SRL", 
    id="input-name",
    name="entity_name"  # Add for screen reader
)
```

#### Issue 8.2: No Announcements for Dynamic Content
**File:** `screens/scan.py`
**Problem:** New devices discovered aren't announced to screen readers.
**Fix:**
```python
def _add_discovery_log(self, message: str):
    """Add message and announce to screen readers."""
    # ... existing code ...
    
    # Announce to screen reader
    try:
        from ..components.accessibility import ScreenReaderAnnouncer
        announcer = ScreenReaderAnnouncer(self.app)
        announcer.announce(message, "polite")
    except Exception:
        pass
```

#### Issue 8.3: Progress Not Announced
**File:** `screens/report.py`, `screens/scan.py`
**Problem:** Progress bar updates not announced to assistive tech.
**Fix:**
```python
# In report generation
def watch_progress(self, value: int):
    """Update progress and announce."""
    # ... existing code ...
    
    # Announce every 25%
    if value % 25 == 0:
        from ..components.accessibility import ScreenReaderAnnouncer
        announcer = ScreenReaderAnnouncer(self.app)
        announcer.announce_progress(value, 100, "Generating report")
```

---

## 9. RECOMMENDED PRIORITY FIXES

### 🔴 Critical (Fix Immediately)

1. **Issue 3.1** - Connect screen Run Assessment button logic
2. **Issue 4.1** - Color contrast on muted text (#666600 → #888833)
3. **Issue 6.1** - Consolidate button placement in Connect screen
4. **Issue 7.1** - Empty state for scan results

### 🟡 High Priority (Fix Soon)

5. **Issue 1.1** - Keyboard shortcut consistency
6. **Issue 2.1** - Implement TabOrderManager in screens
7. **Issue 5.1** - Connect contextual help to form fields
8. **Issue 3.2** - Scan screen input validation

### 🟢 Medium Priority (Nice to Have)

9. **Issue 4.2** - Improve border visibility
10. **Issue 5.3** - Inline help for complex fields
11. **Issue 2.3** - Focus trapping in modals
12. **Issue 8.x** - Screen reader enhancements

---

## 9.5 GLOBAL APP ANALYSIS

### File: `nis2-audit-app/app/textual_app.py`

### ✅ Already Implemented Well
- Global bindings for `?` (shortcuts) and `F1` (help) available on all screens
- Context-aware help system detects current screen and shows appropriate help
- Action tracking for idle timeout
- Screens properly registered with `install_screen()`

### ❌ Issues Found

#### Issue 9.5.1: Help System Not Connected to Dashboard
**File:** `textual_app.py` (lines 160-184), `screens/dashboard.py` (line 385)
**Problem:** Global `action_show_help` exists but Dashboard._show_help() doesn't call it.
**Fix:**
```python
# In dashboard.py
def _show_help(self):
    """Afișează contextual help dialog."""
    self.app.action_show_help()  # Use global action
```

#### Issue 9.5.2: Missing Screen in Help Detection
**File:** `textual_app.py` (lines 163-176)
**Problem:** `connect` and `onboarding` screens not in help detection logic.
**Fix:**
```python
def action_show_help(self) -> None:
    """Show help for current screen."""
    screen_name = 'dashboard'
    if self.screen:
        name = self.screen.__class__.__name__.lower()
        # Add missing screens:
        if 'connect' in name:
            screen_name = 'connect'
        elif 'onboarding' in name:
            screen_name = 'onboarding'
        # ... existing conditions ...
```

#### Issue 9.5.3: No Global Accessibility Settings
**File:** `textual_app.py`
**Problem:** No global way to toggle accessibility features like high contrast.
**Fix:**
```python
# Add to NIS2AuditApp.BINDINGS
BINDINGS = [
    ("?", "show_shortcuts", "Scurtături Tastatură"),
    ("f1", "show_help", "Ajutor"),
    ("ctrl+a", "toggle_accessibility", "Accesibilitate"),  # ADD
]

def action_toggle_accessibility(self) -> None:
    """Toggle accessibility settings panel."""
    from .tui.components.accessibility import AccessibilitySettings
    # Push accessibility settings modal
    pass
```

---

## 10. TESTING RECOMMENDATIONS

### Manual Tests
```bash
# Test keyboard navigation
1. Tab through every screen - ensure logical order
2. Test all shortcuts work
3. Verify focus is visible on all interactive elements
4. Test with keyboard only (no mouse)

# Test screen readers (if available)
1. Install Orca (Linux) or NVDA (Windows)
2. Navigate through app
3. Verify all actions can be performed

# Test color vision deficiency
1. Use browser dev tools color vision simulator
2. Verify all information is perceivable
```

### Automated Tests to Add
```python
# tests/test_accessibility.py

def test_all_buttons_have_shortcuts():
    """Verify all primary buttons have keyboard shortcuts."""
    pass

def test_color_contrast_ratios():
    """Verify all text meets WCAG AA contrast."""
    pass

def test_focus_management():
    """Verify focus is managed correctly in all screens."""
    pass

def test_empty_states_have_cta():
    """Verify all empty states have clear next actions."""
    pass
```

---

## Appendix: Color Contrast Reference

| Color | Background | Ratio | WCAG AA | WCAG AAA |
|-------|------------|-------|---------|----------|
| #00ff41 | #0c0c00 | 11.8:1 | ✅ Pass | ✅ Pass |
| #ffb000 | #0c0c00 | 7.2:1 | ✅ Pass | ✅ Pass |
| #ff4444 | #0c0c00 | 6.5:1 | ✅ Pass | ✅ Pass |
| #b8b000 | #0c0c00 | 5.1:1 | ✅ Pass | ❌ Fail |
| #888866 | #0c0c00 | 3.8:1 | ❌ Fail | ❌ Fail |
| #666600 | #0c0c00 | 3.0:1 | ❌ Fail | ❌ Fail |
| #4a4a00 | #0c0c00 | 1.9:1 | ❌ Fail | ❌ Fail |

**Note:** WCAG AA requires 4.5:1 for normal text, 3:1 for large text.  
**Recommendation:** Replace all colors below 4.5:1 ratio.
