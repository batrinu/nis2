# NIS2 Audit Tool - Code Audit: Breaking Issues

**Audit Date:** 2026-03-14  
**Scope:** Full codebase analysis for issues that can cause crashes, data loss, or security vulnerabilities  
**Files Analyzed:** 91 Python files

---

## 🔴 CRITICAL ISSUES (Can Cause Crashes/Data Loss)

### 1. Socket Resource Leak in SSH Verification
**File:** `app/connector/device_manager.py:297-307`

```python
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.settimeout(5)
sock.connect((self.device.ip_address, self.credentials.port))
transport = paramiko.Transport(sock)
transport.start_client(timeout=5)
server_key = transport.get_remote_server_key()
transport.close()
sock.close()  # Never reached if exception occurs
```

**Risk:** If an exception occurs before `sock.close()`, the socket is never closed. Repeated failures will exhaust file descriptors.

**Fix:**
```python
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    sock.settimeout(5)
    sock.connect((self.device.ip_address, self.credentials.port))
    transport = paramiko.Transport(sock)
    try:
        transport.start_client(timeout=5)
        server_key = transport.get_remote_server_key()
    finally:
        transport.close()
finally:
    sock.close()
```

---

### 2. File Descriptor Leak in atomic_write
**File:** `app/security_utils.py:403-413`

```python
temp_fd, temp_path = tempfile.mkstemp(...)
try:
    if 'b' in mode:
        temp_file = os.fdopen(temp_fd, mode)  # If this fails...
    else:
        temp_file = os.fdopen(temp_fd, mode, encoding=encoding)
    # ...
except Exception:
    try:
        temp_file.close()  # temp_file doesn't exist if fdopen failed
    except Exception:
        pass
```

**Risk:** If `os.fdopen()` fails, `temp_fd` is never closed.

**Fix:** Close `temp_fd` explicitly if `os.fdopen()` fails.

---

### 3. Unprotected datetime.fromisoformat() Calls
**File:** `app/storage/db.py` (multiple lines)

Lines 711, 712, 735, 736, 737, 928, 932, 933, 1102, 1104 all call `datetime.fromisoformat()` on database values without error handling.

```python
created_at=datetime.fromisoformat(row["created_at"]),  # Line 711
updated_at=datetime.fromisoformat(row["created_at"]),  # Line 712 - BUG: should be updated_at?
```

**Risk:** Database corruption or manual tampering will crash the app during session loading.

**Example crash:**
```
ValueError: Invalid isoformat string: 'corrupted-date'
```

**Fix:** Wrap all datetime parsing in try/except and return None or default date on failure.

---

### 4. Error Handler Can Crash with KeyError
**File:** `app/error_handling.py:183-185`

```python
if error.exception_type in category_info['actions']:
    action = category_info['actions'][error.exception_type]
else:
    action = category_info['actions']['default']  # KeyError if 'default' missing
```

**Risk:** If `category_info['actions']` doesn't have a 'default' key, the error handler itself crashes, masking the original error.

**Also affected:** `app/user_friendly_errors.py:175-176`

---

### 5. Unprotected JSON Loading in Config
**File:** `app/security_utils.py:3353`

```python
return json.loads(content)  # No try/except
```

**Risk:** Corrupted config file crashes the app on startup.

---

### 6. SQL Injection via Column Names
**File:** `app/storage/db.py` (multiple locations)

Lines 620, 850, 858, 1035, 1043, 1155 use f-strings to construct SQL queries with column names:

```python
# Line 850
update_fields = ", ".join(f"{k} = ?" for k in device_data.keys())
conn.execute(f"UPDATE devices SET {update_fields} WHERE device_id = ?", values)
```

**Risk:** While values are parameterized, column names come from dictionary keys. If an attacker can control model field names, they could inject SQL.

**Fix:** Whitelist allowed column names against the database schema.

---

### 7. ReDoS in RegexValidator
**File:** `app/security_utils.py:304`

```python
self._compiled = re.compile(pattern)  # User-controlled pattern
```

**Risk:** If user input reaches this, it's a direct ReDoS vector. The pattern is compiled without validation or timeout.

---

### 8. Chained Dict Access Without Guards
**File:** `app/tui/components/smart_defaults.py:217-222`

```python
suggestions.extend(self.SUGGESTIONS["network_scan"]["first_time"])  # KeyError?
patterns = self.SUGGESTIONS["entity_sector"]["based_on_name"]  # KeyError?
```

**Risk:** Missing nested keys will crash the UI.

**Also affected:** `app/tui/components/final_polish.py:118-120`

---

## 🟠 HIGH SEVERITY ISSUES

### 9. Silent Failures in Security-Critical Code
**File:** `app/connector/device_manager.py:329-332`

```python
except Exception as e:
    logger.warning(f"Host key verification error: {e}")
    # Fail open if we can't verify, but log the issue
    return True, f"Host key verification error (proceeding with caution): {e}"
```

**Risk:** Host key verification errors are silently ignored. This is a security bypass - MITM attacks won't be detected.

**Fix:** Default to secure - return `False` instead of `True`.

---

### 10. Type Conversions Without Validation
**File:** `app/tui/screens/connect.py:413, 442, 446`

```python
index = int(checkbox_id.split("-")[1])  # ValueError if format wrong
index = int(btn_id.split("-")[-1])  # ValueError if format wrong
```

**Risk:** Malformed IDs crash the UI.

---

### 11. List Index Without Bounds Check
**File:** `app/security_utils.py:~7434`

```python
socket.getaddrinfo(...)[0][4][0]  # Multiple nested indices
```

**Risk:** If DNS returns empty list or unexpected format, IndexError crashes the app.

**Also affected:**
- `app/cli.py:321` - `subnets[0]` without check
- `app/user_experience.py:994` - `data[0]` without check
- `app/tui/screens/connect.py:413` - split result accessed without length check

---

### 12. TOCTOU Race Conditions
Multiple files check `os.path.exists()` before file operations:

**Files:**
- `app/user_experience.py:71, 1359`
- `app/tui/screens/new_session.py:604, 626`
- `app/tui/components/import_export.py:343`
- `app/tui/components/personalization.py:113, 486`
- `app/tui/components/smart_form.py:237, 270, 295`
- `app/tui/components/gamification.py:72, 82`
- `app/logging_config.py:154, 159, 160`

**Risk:** Time-of-check-time-of-use race conditions can lead to security issues or crashes.

**Fix:** Use try/except instead of exists() checks.

---

### 13. Silent Exception Handling in UI (85+ instances)

**Risk:** UI errors are silently swallowed, hiding bugs:

```python
# Pattern found in 85+ locations
try:
    self.query_one("#widget-id", Static).update(text)
except Exception:
    pass
```

This makes debugging extremely difficult when widgets fail to update.

---

## 🟡 MEDIUM SEVERITY ISSUES

### 14. Division Without Zero Check
Already fixed in previous pass - all divisions have guards.

### 15. Unprotected File Operations
**Files:** 
- `app/storage/encrypted_db.py:289-290, 303-304`
- `app/user_experience.py:83, 1119`
- `app/logging_config.py:161, 169`

**Risk:** File operations without error handling can crash on permission errors or disk full.

---

### 16. Modulo by Zero Protected
Already protected in `keyboard_nav.py` with `if not self.tab_order: return` checks.

---

## Summary by Category

| Category | Count | Files Affected |
|----------|-------|----------------|
| Resource Leaks | 2 | device_manager.py, security_utils.py |
| datetime parsing | 10 | db.py |
| SQL injection | 6 | db.py |
| KeyError crashes | 5 | error_handling.py, user_friendly_errors.py, smart_defaults.py, final_polish.py |
| Type conversion | 3 | connect.py |
| List index | 5 | security_utils.py, cli.py, user_experience.py, connect.py |
| TOCTOU races | 15+ | Multiple files |
| Silent failures | 85+ | TUI components |
| ReDoS | 2 | security_utils.py, responsive.py |
| Security bypass | 1 | device_manager.py |

---

## Priority Fix Order

1. **CRITICAL:** Fix socket leak (device_manager.py:297-307)
2. **CRITICAL:** Fix datetime parsing in db.py with try/except
3. **CRITICAL:** Fix SQL injection via column name validation
4. **HIGH:** Fix file descriptor leak in atomic_write
5. **HIGH:** Fix error handler KeyError risks
6. **HIGH:** Fix security bypass in host key verification
7. **MEDIUM:** Fix type conversions with validation
8. **MEDIUM:** Fix list index bounds checking
9. **LOW:** Address TOCTOU race conditions
10. **LOW:** Reduce silent exception handling for better debugging
