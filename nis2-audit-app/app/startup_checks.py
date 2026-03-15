"""
Startup Checks Module for NIS2 Field Audit Tool
Provides uncle-friendly pre-flight checks and error messages.
"""

import shutil
import subprocess
from pathlib import Path
from typing import Tuple
from .config import is_portable_mode, get_data_directory


class StartupError(Exception):
    """Custom exception for startup errors with helpful messages."""
    pass


def check_python() -> Tuple[bool, str]:
    """
    Check if Python 3.10+ is available.
    
    Returns:
        Tuple of (success, python_command)
    """
    # Try different Python commands
    for cmd in ['python3', 'python', 'py']:
        try:
            result = subprocess.run(
                [cmd, '--version'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                # Parse version
                version_str = result.stdout.strip() or result.stderr.strip()
                # Extract version number (e.g., "Python 3.10.4" -> "3.10.4")
                version_parts = version_str.split()
                if len(version_parts) >= 2:
                    version = version_parts[1]
                    major, minor = version.split('.')[:2]
                    if int(major) == 3 and int(minor) >= 10:
                        return True, cmd
        except (FileNotFoundError, subprocess.TimeoutExpired):
            continue
    
    return False, ""


def check_terminal_size(min_cols: int = 80, min_rows: int = 24) -> Tuple[bool, int, int]:
    """
    Check if terminal is large enough.
    
    Returns:
        Tuple of (is_large_enough, cols, rows)
    """
    try:
        cols, rows = shutil.get_terminal_size()
        return cols >= min_cols and rows >= min_rows, cols, rows
    except Exception:
        # If we can't determine size, assume it's okay
        return True, 80, 24


def check_write_permissions(directory: Path) -> bool:
    """Check if the directory is writable."""
    try:
        # Ensure directory exists first
        directory.mkdir(parents=True, exist_ok=True)
        test_file = directory / ".write_test"
        test_file.touch()
        test_file.unlink()
        return True
    except (IOError, PermissionError):
        return False


def format_python_not_found_error() -> str:
    """Format a friendly error message for missing Python."""
    return """
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║  🔴 Python Not Found                                                         ║
║                                                                              ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                              ║
║  The NIS2 Field Audit Tool requires Python 3.10 or newer.                    ║
║                                                                              ║
║  📥 Please download and install Python:                                      ║
║                                                                              ║
║     https://python.org/downloads                                             ║
║                                                                              ║
║  ⚠️  IMPORTANT: During installation, check:                                  ║
║                                                                              ║
║     "☑ Add Python to PATH"  (Windows)                                        ║
║     "☑ Install for all users" (optional but recommended)                     ║
║                                                                              ║
║  🖥️  Platform-specific instructions:                                          ║
║                                                                              ║
║     Windows:                                                                 ║
║       1. Download Python 3.10+ from python.org                               ║
║       2. Run the installer                                                   ║
║       3. Check "Add Python to PATH" at the bottom                            ║
║       4. Click "Install Now"                                                 ║
║                                                                              ║
║     macOS:                                                                   ║
║       Option 1: brew install python3                                         ║
║       Option 2: Download from python.org                                     ║
║                                                                              ║
║     Linux (Ubuntu/Debian):                                                   ║
║       sudo apt update && sudo apt install python3 python3-venv python3-pip   ║
║                                                                              ║
║     Linux (RHEL/CentOS/Fedora):                                              ║
║       sudo dnf install python3 python3-venv python3-pip                      ║
║                                                                              ║
║  After installation, run START.bat (Windows) or START.sh (Mac/Linux) again.  ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""


def format_terminal_too_small_error(cols: int, rows: int, min_cols: int = 80, min_rows: int = 24) -> str:
    """Format a friendly error message for small terminal."""
    return f"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║  🟡 Terminal Window Too Small                                                ║
║                                                                              ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                              ║
║  Your terminal window is too small to display the application properly.      ║
║                                                                              ║
║  📊 Current size:     {cols} columns × {rows} rows                              ║
║  📐 Minimum required: {min_cols} columns × {min_rows} rows                              ║
║                                                                              ║
║  🛠️  How to resize:                                                           ║
║                                                                              ║
║     Windows:                                                                 ║
║       • Drag the window edges to make it larger                              ║
║       • Or maximize the window                                               ║
║                                                                              ║
║     Mac:                                                                     ║
║       • Drag the bottom-right corner to resize                               ║
║       • Or press the green maximize button                                   ║
║                                                                              ║
║     Linux:                                                                   ║
║       • Most terminals: Ctrl++ to zoom in                                    ║
║       • Or drag window edges to resize                                       ║
║                                                                              ║
║  After resizing, run START.bat (Windows) or START.sh (Mac/Linux) again.      ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""


def format_write_permission_error(directory: Path) -> str:
    """Format a friendly error message for write permission issues."""
    return f"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║  🔴 Write Permission Denied                                                  ║
║                                                                              ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                              ║
║  The application cannot write to the required data directory:                ║
║                                                                              ║
║  📂 {str(directory):<74} ║
║                                                                              ║
║  This is required for Portable Mode to store your audit data.                ║
║                                                                              ║
║  🛠️  How to fix:                                                           ║
║                                                                              ║
║     1. Move the application folder                                           ║
║        • Try moving the 'nis2' folder to your Documents or Desktop           ║
║        • Avoid 'Program Files' or other system folders                       ║
║                                                                              ║
║     2. Run as Administrator                                                  ║
║        • Right-click START.bat → "Run as administrator"                     ║
║                                                                              ║
║     3. Check folder permissions                                              ║
║        • Right-click the folder → Properties → Security                      ║
║        • Ensure your user has "Full control"                                 ║
║                                                                              ║
║  After fixing, run START.bat (Windows) or START.sh (Mac/Linux) again.        ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""


def format_dependency_error(error_details: str) -> str:
    """Format a friendly error message for dependency installation failure."""
    return f"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║  🟠 Package Installation Issue                                               ║
║                                                                              ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                              ║
║  Could not install required packages.                                        ║
║                                                                              ║
║  Error details:                                                              ║
║  {error_details:<76} ║
║                                                                              ║
║  🛠️  Try these solutions:                                                     ║
║                                                                              ║
║     1. Check your internet connection                                        ║
║        • Try opening a web browser                                           ║
║        • Some corporate networks block PyPI                                  ║
║                                                                              ║
║     2. Run with elevated permissions                                         ║
║        • Windows: Right-click START.bat → "Run as administrator"             ║
║        • Mac/Linux: Not usually required                                     ║
║                                                                              ║
║     3. Update pip manually                                                   ║
║        • python -m pip install --upgrade pip                                 ║
║        • Then run START.bat/START.sh again                                   ║
║                                                                              ║
║     4. Clear the virtual environment                                         ║
║        • Delete the .venv folder                                             ║
║        • Run START.bat/START.sh again                                        ║
║                                                                              ║
║     5. Check antivirus/firewall                                              ║
║        • Some antivirus software blocks pip                                  ║
║        • Try temporarily disabling it                                        ║
║                                                                              ║
║  If problems continue, check the log files in:                               ║
║     ~/.nis2-audit/logs/                                                      ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""


def format_virtualenv_error(error_details: str) -> str:
    """Format a friendly error message for virtual environment creation failure."""
    return f"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║  🟠 Virtual Environment Creation Failed                                      ║
║                                                                              ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                              ║
║  Could not create the virtual environment.                                   ║
║                                                                              ║
║  Error details:                                                              ║
║  {error_details:<76} ║
║                                                                              ║
║  🛠️  Platform-specific solutions:                                             ║
║                                                                              ║
║     Linux (Ubuntu/Debian):                                                   ║
║       sudo apt install python3-venv python3-pip                              ║
║                                                                              ║
║     Linux (RHEL/CentOS/Fedora):                                              ║
║       sudo dnf install python3-venv python3-pip                              ║
║                                                                              ║
║     macOS:                                                                   ║
║       Usually included with Python from python.org                           ║
║       If using Homebrew: brew install python3                                ║
║                                                                              ║
║     Windows:                                                                 ║
║       Usually included with Python installer                                 ║
║       Re-run Python installer and select "Modify" → "pip" and "venv"         ║
║                                                                              ║
║  🛠️  Other solutions:                                                         ║
║                                                                              ║
║     1. Check disk space                                                      ║
║        • Virtual environment needs ~100MB free space                         ║
║                                                                              ║
║     2. Check permissions                                                     ║
║        • Make sure you can write to the app folder                           ║
║        • Try running from your home directory                                ║
║                                                                              ║
║     3. Check Python installation                                             ║
║        • python -m venv --help  (should show help, not error)                ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""


def format_app_crash_error(exit_code: int, log_path: str) -> str:
    """Format a friendly error message for application crashes."""
    return f"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║  🔴 Application Crashed                                                      ║
║                                                                              ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                              ║
║  The NIS2 Field Audit Tool exited unexpectedly.                              ║
║                                                                              ║
║  Exit code: {exit_code:<66} ║
║                                                                              ║
║  📝 Log file location:                                                       ║
║     {log_path:<76} ║
║                                                                              ║
║  🛠️  Try these solutions:                                                     ║
║                                                                              ║
║     1. Restart the application                                               ║
║        • Some errors are temporary                                           ║
║                                                                              ║
║     2. Clear and rebuild the environment                                     ║
║        • Delete the .venv folder                                             ║
║        • Run START.bat/START.sh again                                        ║
║                                                                              ║
║     3. Check system resources                                                ║
║        • Free disk space (need ~100MB)                                       ║
║        • Available RAM (need ~512MB)                                         ║
║                                                                              ║
║     4. Check database integrity                                              ║
║        • Delete audit_sessions.db (you'll lose saved data)                   ║
║        • Run START.bat/START.sh again                                        ║
║                                                                              ║
║     5. Run in debug mode                                                     ║
║        • cd nis2-audit-app                                                   ║
║        • source .venv/bin/activate  (Mac/Linux)                              ║
║        • .venv\\Scripts\\activate.bat  (Windows)                             ║
║        • python -m app.textual_app                                           ║
║                                                                              ║
║  If problems continue, please report the issue with the log file.            ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""


def perform_startup_checks() -> None:
    """
    Perform all startup checks and raise StartupError with friendly message if any fail.
    
    Raises:
        StartupError: If any check fails, with a user-friendly error message.
    """
    python_ok, python_cmd = check_python()
    if not python_ok:
        raise StartupError(format_python_not_found_error())
    
    size_ok, cols, rows = check_terminal_size()
    if not size_ok:
        raise StartupError(format_terminal_too_small_error(cols, rows))

    # Task 2: Implement Write Permission Checks
    if is_portable_mode():
        data_dir = get_data_directory()
        if not check_write_permissions(data_dir):
            raise StartupError(format_write_permission_error(data_dir))


def is_first_run(config_dir: str = "~/.nis2-audit") -> bool:
    """
    Check if this is the first time the app is being run.
    
    Args:
        config_dir: Directory where preferences are stored
        
    Returns:
        True if no preferences file exists (first run)
    """
    config_path = Path(config_dir).expanduser()
    prefs_file = config_path / "preferences.json"
    return not prefs_file.exists()


if __name__ == "__main__":
    # Test the error messages
    print(format_python_not_found_error())
    print(format_terminal_too_small_error(60, 20))
    print(format_dependency_error("Could not find a version that satisfies the requirement"))
