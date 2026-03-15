# Windows Portable Distribution Implementation Plan

> **For Gemini:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Create a self-contained, zero-install Windows portable distribution for the NIS2 Field Audit Tool.

**Architecture:**
1. **Portable Mode:** The app detects if it's running from a `python/` subdirectory (embedded distribution) and redirects all data/logs/exports to a local `data/` folder.
2. **Robust Entry Point:** A `launch.bat` script handles environment isolation, C++ Redistributable checks, and error reporting.
3. **Build Automation:** A Python script to assemble the portable ZIP by downloading the embedded Python runtime and pre-installing dependencies.

**Tech Stack:**
- Python 3.12 (Windows Embeddable Distribution)
- Batch Scripting (for `launch.bat`)
- PyPi/Pip (for dependency bundling)

---

### Task 1: Add Portable Mode Detection to `config.py`

**Files:**
- Modify: `nis2-audit-app/app/config.py`

**Step 1: Implement `is_portable_mode()` and update path resolution**

Update `nis2-audit-app/app/config.py` to detect the `python` directory and override `get_config_directory` and `get_data_directory`.

```python
def is_portable_mode() -> bool:
    """Check if the app is running in portable mode."""
    # Check if we are running from a 'python' subdirectory in the app root
    # or if a '.portable' marker file exists.
    app_root = Path(sys.executable).parent.parent
    return (app_root / "python").exists() or (app_root / ".portable").exists()

def get_portable_data_directory() -> Path:
    """Get the data directory for portable mode."""
    app_root = Path(sys.executable).parent.parent
    data_dir = app_root / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir

# Update get_config_directory and get_data_directory to use portable logic
```

**Step 2: Verify path resolution**

Write a temporary script to verify that `get_data_directory()` returns the local `data/` folder when a `.portable` file is present.

**Step 3: Commit**

```bash
git add nis2-audit-app/app/config.py
git commit -m "feat: add portable mode detection to config"
```

---

### Task 2: Implement Write Permission Checks in `startup_checks.py`

**Files:**
- Modify: `nis2-audit-app/app/startup_checks.py`

**Step 1: Add `check_write_permissions()` function**

```python
def check_write_permissions(directory: Path) -> bool:
    """Check if the directory is writable."""
    try:
        test_file = directory / ".write_test"
        test_file.touch()
        test_file.unlink()
        return True
    except (IOError, PermissionError):
        return False
```

**Step 2: Update `perform_startup_checks()` to verify data directory**

If in portable mode and the directory isn't writable, it should raise a `StartupError` with instructions to move the app or run as admin.

**Step 3: Commit**

```bash
git add nis2-audit-app/app/startup_checks.py
git commit -m "feat: add write permission checks on startup"
```

---

### Task 3: Create the `launch.bat` Entry Point

**Files:**
- Create: `nis2-audit-app/launch.bat`

**Step 1: Write the robust Batch script**

The script must:
1. Check for `vcruntime140.dll` in `C:\Windows\System32`.
2. Set `PYTHONHOME` and `PYTHONPATH` to the bundled folders.
3. Launch `python\python.exe -m app.textual_app`.
4. Use `pause` if the exit code is non-zero.

**Step 2: Commit**

```bash
git add nis2-audit-app/launch.bat
git commit -m "feat: add launch.bat for windows portable"
```

---

### Task 4: Create Portable Build Script

**Files:**
- Create: `scripts/build_windows_portable.py`

**Step 1: Implement the assembly logic**

The script should:
1. Download the Windows Embeddable Python ZIP.
2. Extract it to `dist/portable/python`.
3. Install dependencies from `requirements.txt` into `dist/portable/lib`.
4. Copy `app/` and `launch.bat` to `dist/portable/`.
5. Create a `data/` folder and a `.portable` marker.

**Step 2: Commit**

```bash
git add scripts/build_windows_portable.py
git commit -m "feat: add portable build script"
```

---

### Task 5: Final Validation and Packaging

**Step 1: Run the build script**

Run: `python scripts/build_windows_portable.py`
Expected: A `dist/portable` directory is created with all components.

**Step 2: Verify the portable structure**

Check that `dist/portable/python/python.exe` exists and `dist/portable/lib` contains dependencies.

**Step 3: Final Commit**

```bash
git add .
git commit -m "chore: complete windows portable distribution setup"
```
