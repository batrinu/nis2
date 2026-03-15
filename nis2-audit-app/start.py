#!/usr/bin/env python3
"""
NIS2 Field Audit Tool - Universal Starter Script
Checks dependencies, installs if needed, and launches the app.
"""

import sys
import subprocess
import os
import platform
from pathlib import Path

# Configuration
MIN_PYTHON_VERSION = (3, 10)
REQUIRED_PACKAGES = [
    "pydantic>=2.0.0",
    "python-dateutil>=2.8.0",
    "typer>=0.9.0",
    "rich>=13.0.0",
    "textual>=0.50.0",
    "netmiko>=4.3.0",
    "paramiko>=3.4.0",
    "cryptography>=42.0.0",
    "textfsm>=1.2.0",
    "jinja2>=3.1.0",
    "markdown>=3.5.0",
]

# Colors for terminal output
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_header():
    """Print welcome header."""
    print(f"""
{Colors.CYAN}{Colors.BOLD}
╔══════════════════════════════════════════════════════════════════╗
║                    🛡️  NIS2 FIELD AUDIT TOOL  🛡️                ║
║                       Universal Starter                          ║
╚══════════════════════════════════════════════════════════════════╝
{Colors.END}""")

def print_success(msg):
    print(f"{Colors.GREEN}✓{Colors.END} {msg}")

def print_warning(msg):
    print(f"{Colors.YELLOW}⚠{Colors.END} {msg}")

def print_error(msg):
    print(f"{Colors.RED}✗{Colors.END} {msg}")

def print_info(msg):
    print(f"{Colors.BLUE}ℹ{Colors.END} {msg}")

def print_step(msg):
    print(f"\n{Colors.BOLD}{msg}{Colors.END}")

def check_python_version():
    """Check if Python version is sufficient."""
    print_step("Checking Python version...")
    version = sys.version_info
    current = (version.major, version.minor)
    
    if current >= MIN_PYTHON_VERSION:
        print_success(f"Python {version.major}.{version.minor}.{version.micro} (OK)")
        return True
    else:
        print_error(f"Python {version.major}.{version.minor} is too old")
        print_info(f"Need Python {MIN_PYTHON_VERSION[0]}.{MIN_PYTHON_VERSION[1]} or higher")
        print_info("Download from: https://python.org/downloads/")
        return False

def check_pip():
    """Check if pip is available."""
    print_step("Checking pip...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "--version"], 
                      check=True, capture_output=True)
        print_success("pip is available")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print_error("pip not found")
        print_info("Install pip: https://pip.pypa.io/en/stable/installation/")
        return False

def check_package(package_name):
    """Check if a package is installed."""
    try:
        # Extract base package name (remove version specifier)
        base_name = package_name.split('>=')[0].split('==')[0].split('<')[0]
        __import__(base_name.lower().replace('-', '_'))
        return True
    except ImportError:
        return False

def install_packages():
    """Install required packages."""
    print_step("Checking dependencies...")
    
    missing = []
    for pkg in REQUIRED_PACKAGES:
        if not check_package(pkg):
            missing.append(pkg)
    
    if not missing:
        print_success("All dependencies are installed")
        return True
    
    print_warning(f"Missing {len(missing)} packages")
    print_info(f"Packages to install: {', '.join(m.split('>=')[0] for m in missing)}")
    
    print_step("Installing packages...")
    print("(This may take a minute...)")
    
    try:
        cmd = [sys.executable, "-m", "pip", "install", "--quiet"] + missing
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print_success("Dependencies installed successfully")
            return True
        else:
            print_error("Failed to install dependencies")
            print(f"Error: {result.stderr}")
            return False
    except Exception as e:
        print_error(f"Installation error: {e}")
        return False

def check_nmap():
    """Check if nmap is installed."""
    print_step("Checking optional dependency: nmap...")
    
    try:
        result = subprocess.run(["nmap", "--version"], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            version_line = result.stdout.split('\n')[0]
            print_success(f"nmap found: {version_line}")
            return True
    except FileNotFoundError:
        pass
    
    print_warning("nmap not found (optional)")
    print_info("Network scanning requires nmap")
    print_info("Install:")
    print("  Ubuntu/Debian: sudo apt install nmap")
    print("  macOS:         brew install nmap")
    print("  Windows:       https://nmap.org/download.html")
    return False

def setup_directories():
    """Create necessary directories."""
    print_step("Setting up directories...")
    
    # Get the app directory
    app_dir = Path(__file__).parent.absolute()
    
    # Create data directory
    data_dir = Path.home() / ".local" / "share" / "nis2-audit"
    data_dir.mkdir(parents=True, exist_ok=True)
    
    print_success(f"Data directory: {data_dir}")
    return True

def check_terminal_size():
    """Check if terminal is large enough."""
    print_step("Checking terminal size...")
    
    try:
        import shutil
        cols, rows = shutil.get_terminal_size()
        
        if cols >= 80 and rows >= 24:
            print_success(f"Terminal size: {cols}x{rows} (OK)")
            return True
        else:
            print_warning(f"Terminal size: {cols}x{rows}")
            print_info("Recommended: 80x24 or larger")
            print_info("Please resize your terminal for best experience")
            return False
    except Exception:
        print_warning("Could not detect terminal size")
        return True  # Don't block on this

def launch_app():
    """Launch the NIS2 Field Audit Tool."""
    print_step("Starting NIS2 Field Audit Tool...")
    print()
    print(f"{Colors.CYAN}{Colors.BOLD}Launching... Press F1 for help, Q to quit{Colors.END}")
    print()
    
    # Small delay so user can see the message
    import time
    time.sleep(1)
    
    # Get the app directory
    app_dir = Path(__file__).parent.absolute()
    
    # Add app directory to Python path
    sys.path.insert(0, str(app_dir))
    
    try:
        # Import and run the app
        from app.textual_app import NIS2AuditApp
        
        app = NIS2AuditApp()
        app.run()
        
        return True
    except Exception as e:
        print_error(f"Failed to start app: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main entry point."""
    print_header()
    
    print("This script will check your system and start the NIS2 Field Audit Tool.")
    print("Checking dependencies...\n")
    
    # Run checks
    checks = [
        ("Python version", check_python_version),
        ("pip", check_pip),
        ("Dependencies", install_packages),
        ("Optional: nmap", check_nmap),
        ("Directories", setup_directories),
        ("Terminal size", check_terminal_size),
    ]
    
    failed = []
    for name, check_func in checks:
        try:
            if not check_func():
                # Some checks are warnings, not failures
                if name in ["Python version", "pip"]:
                    failed.append(name)
        except Exception as e:
            print_error(f"Error in {name}: {e}")
            if name in ["Python version", "pip"]:
                failed.append(name)
    
    # Check if any critical checks failed
    if failed:
        print()
        print_error("Critical checks failed:")
        for f in failed:
            print(f"  - {f}")
        print()
        print_info("Please fix the issues above and try again.")
        sys.exit(1)
    
    # Launch the app
    print()
    print("=" * 66)
    print_success("All checks passed!")
    print("=" * 66)
    print()
    
    if launch_app():
        print()
        print_success("App closed normally")
    else:
        print()
        print_error("App failed to start")
        sys.exit(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print()
        print_warning("Interrupted by user")
        sys.exit(0)
    except Exception as e:
        print()
        print_error(f"Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
