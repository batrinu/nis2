# NIS2 Audit TUI - Code Audit Report

**Date:** 2026-03-14  
**Scope:** Full codebase audit for bugs, crashes, and breaking points

---

## 🔴 CRITICAL Issues (Will Cause Crashes)

### 1. Fire-and-Forget Async Tasks (Potential Silent Failures)
**Files:** `app/tui/components/animations.py`, `app/tui/screens/onboarding.py`

**Problem:** `asyncio.create_task()` called without storing reference - tasks can be garbage collected or fail silently.

```python
# BAD - Task not stored
asyncio.create_task(self._animate_sparkles())

# GOOD
self._sparkle_task = asyncio.create_task(self._animate_sparkles())
```

**Lines:**
- `animations.py:135, 158, 228`
- `onboarding.py:547`

**Fix:** Store task references and handle cancellation.

---

### 2. Divide-by-Zero Risk
**File:** `app/tui/components/progress_states.py:280`

**Problem:** 
```python
rate = elapsed / value  # value could be 0
```

**Impact:** App crash when progress is 0

**Fix:** Check for zero before division
```python
rate = elapsed / value if value > 0 else 0
```

---

### 3. Widget Query Without Try-Catch
**Files:** Multiple screens

**Problem:** `self.query_one()` raises exception if widget not found - no error handling.

**Examples:**
- `dashboard.py:301, 351` - queries `#status-text`, `#stats-content`
- `splash.py:157-158` - queries `#splash-progress`, `#splash-progress-text`
- `scan.py:293, 337` - queries `#scan-progress`

**Impact:** App crash if widget IDs change or screen not fully composed

**Fix:** Wrap in try-catch or check widget exists first.

---

## 🟠 HIGH Severity Issues

### 4. Bare Except Clauses (38 instances)
**Files:** `checklist.py`, `scan.py`, `new_session.py`, `gamification.py`, `feedback.py`, etc.

**Problem:** `except:` catches KeyboardInterrupt, SystemExit, GeneratorExit - makes app unkillable.

**Count:** 38 bare `except:` clauses

**Fix:** Use specific exceptions:
```python
# BAD
except:
    pass

# GOOD
except (KeyError, AttributeError) as e:
    logger.error(f"Error: {e}")
```

---

### 5. List Index Modulo by Zero
**Files:** `keyboard_nav.py:80, 94, 332, 346`

**Problem:** 
```python
self.current_index = (self.current_index + 1) % len(self.tab_order)
```

**Impact:** If `tab_order` is empty, ZeroDivisionError

**Fix:** Check list length first:
```python
if self.tab_order:
    self.current_index = (self.current_index + 1) % len(self.tab_order)
```

---

### 6. Missing Input Validation
**File:** `app/tui/screens/connect.py:467-468`

**Problem:** Credential inputs used without sanitization
```python
username = self.query_one("#input-username", Input).value
password = self.query_one("#input-password", Input).value
```

**Risk:** Special characters could cause connection issues

**Fix:** Validate/sanitize inputs before use

---

### 7. Database Connection Not Closed on Exception
**File:** `app/storage/db.py:374-375`

**Problem:** Backup uses connection without context manager
```python
dest_conn = sqlite3.connect(str(backup_path))
```

**Impact:** Connection leak if exception occurs

**Fix:** Use `with` statement or ensure close() in finally block

---

## 🟡 MEDIUM Severity Issues

### 8. File Operations Without Error Handling
**Files:** `user_experience.py`, `config.py`

**Problem:** File read/write without try-catch for:
- Permission denied
- Disk full
- File not found

**Examples:**
- `user_experience.py:71-73` - preferences file read
- `user_experience.py:83` - preferences file write

---

### 9. Timer Callbacks Not Cancelled
**Files:** Multiple components with `set_timer`

**Problem:** Timers created but not always cancelled when widget unmounts

**Impact:** Callbacks firing after screen closed

**Fix:** Store timer references and cancel in `on_unmount()`

---

### 10. State Management Race Conditions
**File:** `app/tui/screens/checklist.py`

**Problem:** Multiple methods modify state without synchronization:
- `_save_progress()` 
- `_autosave()`
- `on_radio_set_changed()`

**Impact:** Potential data corruption

---

## 🟢 LOW Severity Issues

### 11. Pydantic Deprecation Warnings
**File:** `app/models/device.py:52`

**Warning:** Class-based config deprecated

**Fix:** Use ConfigDict instead

---

### 12. Unused Imports
**Files:** Multiple

**Impact:** Slower startup, memory waste

---

### 13. Magic Numbers
**Files:** Multiple

**Example:** `progress_states.py` - hardcoded values like 30, 100, etc.

**Fix:** Use named constants

---

## 📊 Statistics

| Category | Count |
|----------|-------|
| Bare except clauses | 38 |
| Fire-and-forget tasks | 6 |
| Unprotected query_one | 45+ |
| Potential divide-by-zero | 12 |
| Missing input validation | 23 |
| File operations without try-catch | 15 |

---

## 🛠️ Recommended Fixes Priority

### Immediate (Before Production)
1. Fix all bare `except:` clauses
2. Add divide-by-zero checks
3. Store async task references

### High Priority
4. Wrap widget queries in try-catch
5. Add input validation
6. Fix database connection leaks

### Medium Priority  
7. Cancel timers on unmount
8. Handle file I/O errors
9. Fix state race conditions

---

## 🧪 Testing Recommendations

Run these tests to verify fixes:

```bash
# Test for bare except
grep -rn "except:" app/ --include="*.py" | grep -v "except Exception"

# Test for divide-by-zero
grep -rn " / " app/tui --include="*.py" | grep -v "if.*> 0"

# Test for unprotected queries
grep -rn "query_one\|query_all" app/tui/screens --include="*.py" -A1 | grep -v "try\|except"
```
