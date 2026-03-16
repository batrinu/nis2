#!/usr/bin/env python3
"""
NIS2 Field Audit Tool - Portable Build Script

Creates a self-contained portable distribution that:
- Includes embedded Python (no installation required)
- Works without admin rights
- Runs from USB drive
- Easy to update (just replace folder)

Usage:
    python scripts/build_portable.py

Output:
    dist/nis2-audit-portable.zip
"""

import os
import sys
import shutil
import zipfile
import urllib.request
from pathlib import Path

# Configuration
APP_NAME = "nis2-audit"
APP_VERSION = "1.0.2"
PYTHON_VERSION = "3.12.3"
PYTHON_URL = f"https://www.python.org/ftp/python/{PYTHON_VERSION}/python-{PYTHON_VERSION}-embed-amd64.zip"


def download_python(dest_dir: Path) -> bool:
    """Download and extract embedded Python."""
    print(f"Downloading Python {PYTHON_VERSION}...")
    
    try:
        python_zip = dest_dir / "python.zip"
        urllib.request.urlretrieve(PYTHON_URL, python_zip)
        
        print("Extracting Python...")
        python_dir = dest_dir / "python"
        python_dir.mkdir(exist_ok=True)
        
        with zipfile.ZipFile(python_zip, 'r') as zf:
            zf.extractall(python_dir)
        
        python_zip.unlink()
        
        # Enable site packages by modifying python312._pth
        pth_file = python_dir / f"python{PYTHON_VERSION.split('.')[0]}{PYTHON_VERSION.split('.')[1]}._pth"
        if pth_file.exists():
            content = pth_file.read_text()
            content = content.replace("#import site", "import site")
            pth_file.write_text(content)
        
        print("✓ Python ready")
        return True
        
    except Exception as e:
        print(f"✗ Failed to download Python: {e}")
        return False


def install_dependencies(app_dir: Path, python_exe: Path) -> bool:
    """Install required packages."""
    print("Installing dependencies...")
    
    try:
        # Download get-pip.py
        get_pip = app_dir / "get-pip.py"
        urllib.request.urlretrieve(
            "https://bootstrap.pypa.io/get-pip.py",
            get_pip
        )
        
        # Install pip
        import subprocess
        result = subprocess.run(
            [str(python_exe), str(get_pip), "--no-warn-script-location"],
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            print(f"✗ Failed to install pip: {result.stderr}")
            return False
        
        get_pip.unlink()
        
        # Install requirements
        requirements = app_dir.parent / "requirements.txt"
        if requirements.exists():
            result = subprocess.run(
                [str(python_exe), "-m", "pip", "install", 
                 "--no-warn-script-location", "-r", str(requirements)],
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                print(f"✗ Failed to install requirements: {result.stderr}")
                return False
        
        print("✓ Dependencies installed")
        return True
        
    except Exception as e:
        print(f"✗ Failed to install dependencies: {e}")
        return False


def create_launcher_scripts(app_dir: Path) -> None:
    """Create launcher scripts for Windows."""
    
    # Windows launcher
    launch_bat = app_dir / "launch.bat"
    launch_bat.write_text(f'''@echo off
setlocal

REM NIS2 Field Audit Tool v{APP_VERSION} - Portable
REM No installation required!

cd /d "%~dp0"

chcp 65001 >nul 2>&1
set "PYTHONIOENCODING=utf-8"
set "FORCE_COLOR=1"

python\\python.exe -m app.main

exit /b %errorlevel%
''')
    
    # Mac/Linux launcher (for completeness)
    launch_sh = app_dir / "launch.sh"
    launch_sh.write_text(f'''#!/bin/bash
# NIS2 Field Audit Tool v{APP_VERSION} - Portable
# Note: On Mac/Linux, uses system Python (embedded Python is Windows-only)

cd "$(dirname "$0")"

# Check for Python 3
if command -v python3 &> /dev/null; then
    PYTHON=python3
elif command -v python &> /dev/null; then
    PYTHON=python
else
    echo "Python 3 is required but not installed."
    echo "Please install Python 3.10 or newer."
    exit 1
fi

$PYTHON -m app.main
''')
    launch_sh.chmod(0o755)
    
    # README for uncle
    readme = app_dir / "README.txt"
    readme.write_text(f'''NIS2 Field Audit Tool v{APP_VERSION}
=====================================

GETTING STARTED:
1. Double-click "launch.bat" to start
2. That's it!

NO INSTALLATION REQUIRED:
- No admin rights needed
- No registry changes
- Just extract and run

FOR UNCLE:
- Windows: Double-click launch.bat
- Mac/Linux: Double-click launch.sh

UPDATING:
1. Download new version
2. Extract to new folder
3. Copy your data folder from old version
4. Delete old folder

SUPPORT:
- Press F1 in the app for help
- Visit: https://github.com/batrinu/nis2

VERSION: {APP_VERSION}
''')
    
    print("✓ Launcher scripts created")


def copy_application_files(source_dir: Path, dest_dir: Path) -> None:
    """Copy application code."""
    print("Copying application files...")
    
    # Copy app directory
    app_source = source_dir / "app"
    app_dest = dest_dir / "app"
    
    if app_dest.exists():
        shutil.rmtree(app_dest)
    
    shutil.copytree(app_source, app_dest, ignore=shutil.ignore_patterns(
        "__pycache__", "*.pyc", "*.pyo", ".git"
    ))
    
    # Copy requirements
    req_source = source_dir / "requirements.txt"
    if req_source.exists():
        shutil.copy2(req_source, dest_dir / "requirements.txt")
    
    # Create VERSION file
    version_file = dest_dir / "VERSION"
    version_file.write_text(APP_VERSION)
    
    print("✓ Application files copied")


def create_distribution(source_dir: Path, output_dir: Path) -> bool:
    """Create the complete portable distribution."""
    
    print(f"\n{'='*50}")
    print(f"Building NIS2 Field Audit Tool v{APP_VERSION}")
    print(f"{'='*50}\n")
    
    app_dir = output_dir / f"{APP_NAME}-{APP_VERSION}"
    
    # Clean previous build
    if app_dir.exists():
        shutil.rmtree(app_dir)
    app_dir.mkdir(parents=True)
    
    # Download Python
    if not download_python(app_dir):
        print("\n✗ Build failed: Could not download Python")
        return False
    
    # Copy application
    copy_application_files(source_dir, app_dir)
    
    # Install dependencies
    python_exe = app_dir / "python" / "python.exe"
    if not install_dependencies(app_dir, python_exe):
        print("\n⚠ Warning: Some dependencies may not have installed correctly")
    
    # Create launchers
    create_launcher_scripts(app_dir)
    
    # Create data directory (empty, for user data)
    (app_dir / "data").mkdir(exist_ok=True)
    
    # Create zip archive
    print("\nCreating distribution archive...")
    zip_path = output_dir / f"{APP_NAME}-portable-v{APP_VERSION}.zip"
    
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        for file_path in app_dir.rglob("*"):
            if file_path.is_file():
                arcname = file_path.relative_to(app_dir)
                zf.write(file_path, arcname)
    
    print(f"\n{'='*50}")
    print(f"✓ Build complete!")
    print(f"{'='*50}")
    print(f"\nOutput: {zip_path}")
    print(f"Size: {zip_path.stat().st_size / 1024 / 1024:.1f} MB")
    print(f"\nTo test:")
    print(f"  1. Extract: {zip_path}")
    print(f"  2. Run: {app_dir / 'launch.bat'}")
    
    return True


def main():
    """Main entry point."""
    # Determine directories
    script_dir = Path(__file__).parent.resolve()
    source_dir = script_dir.parent  # nis2-audit-app directory
    output_dir = source_dir / "dist"
    output_dir.mkdir(exist_ok=True)
    
    # Check if running on Windows
    if sys.platform != "win32":
        print("⚠ Warning: Building on non-Windows system.")
        print("  The portable Python is Windows-only.")
        print("  The build will still work but Python won't be included.\n")
    
    # Create distribution
    success = create_distribution(source_dir, output_dir)
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
