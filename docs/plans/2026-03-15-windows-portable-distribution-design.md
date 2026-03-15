# Design: NIS2 Windows Portable Distribution (Zero-Install)

**Date:** 2026-03-15
**Status:** Approved
**Goal:** Provide a robust, transparent, and "Zero-Install" experience for Windows users, particularly in restricted corporate environments.

## 1. Architecture Overview
The application will be distributed as a "Folder-Based" Portable ZIP containing a pre-configured Python environment.

### Folder Structure (`nis2-audit-portable/`)
- `python/`: Official Windows Python embeddable distribution (3.12+).
- `lib/`: Pre-installed project dependencies (Pydantic, Rich, Textual, etc.).
- `app/`: Core NIS2 Field Audit Tool source code.
- `data/`: Local storage for `audit_sessions.db` and generated reports.
- `launch.bat`: The primary entry point and environment configurator.
- `tools/`: (Optional) Portable `nmap` binaries for network discovery.

## 2. Launch Strategy (`launch.bat`)
The `launch.bat` script handles the heavy lifting of environment setup and error recovery:
1. **Dependency Check:** Verifies `vcruntime140.dll` exists; if not, prompts for MS VC++ Redistributable installation.
2. **Path Sanitization:** Ensures the execution path is safe and handles potential Windows `MAX_PATH` (260 character) limits.
3. **Isolation:** Sets `PYTHONHOME`, `PYTHONPATH`, and `PYTHONDONTWRITEBYTECODE=1` to prevent conflicts with other Python installs.
4. **Error Capture:** Uses a `pause` on exit if an error occurs, preventing the window from closing before the user can read the traceback.

## 3. Windows-Specific Robustness
- **Portable Mode Detection:** The app detects the `.\python` folder and automatically redirects all database and report output to the local `data/` directory.
- **Write Permission Checks:** Validates write access to the current folder and falls back to `%USERPROFILE%` if the app is run from a read-only location (e.g., a protected network share).
- **Antivirus Interaction:** Catching `PermissionError` specifically to provide user-friendly guidance if Windows Defender "Controlled Folder Access" blocks database writes.
- **Privacy/Cleanup:** Automated routine to clear transient data from `%TEMP%` on startup and exit.

## 4. Implementation Path
1. Create a build script to automate the assembly of the portable folder.
2. Develop the `launch.bat` with robust error handling.
3. Update the app's configuration logic to support "Portable Mode" path resolution.
4. Add the `vcruntime140.dll` check and prompt logic.
