#!/usr/bin/env python3
"""
NIS2 Windows Portable Build Script
Automates the creation of a zero-install portable distribution.
"""

import os
import shutil
import subprocess
import urllib.request
import zipfile
from pathlib import Path
import sys

# Configuration
PYTHON_VERSION = "3.12.3"
PYTHON_ZIP_URL = f"https://www.python.org/ftp/python/{PYTHON_VERSION}/python-{PYTHON_VERSION}-embed-amd64.zip"
PROJECT_ROOT = Path(__file__).parent.parent.absolute()
TARGET_DIR = PROJECT_ROOT / "dist" / "portable"
PYTHON_DIR = TARGET_DIR / "python"
LIB_DIR = TARGET_DIR / "lib"
APP_SOURCE_DIR = PROJECT_ROOT / "nis2-audit-app" / "app"
LAUNCH_BAT_SOURCE = PROJECT_ROOT / "nis2-audit-app" / "launch.bat"
REQUIREMENTS_FILE = PROJECT_ROOT / "nis2-audit-app" / "requirements.txt"

def setup_directories():
    """Create the target directory structure."""
    print(f"[*] Setting up directories in {TARGET_DIR}...")
    if TARGET_DIR.exists():
        print(f"[*] Removing existing {TARGET_DIR}...")
        shutil.rmtree(TARGET_DIR)
    
    TARGET_DIR.mkdir(parents=True)
    PYTHON_DIR.mkdir()
    LIB_DIR.mkdir()
    (TARGET_DIR / "data").mkdir()
    print("[+] Directories created.")

def download_python():
    """Download and extract the Windows Embeddable Python distribution."""
    zip_path = TARGET_DIR / "python_embed.zip"
    print(f"[*] Downloading Windows Embeddable Python {PYTHON_VERSION}...")
    print(f"[*] URL: {PYTHON_ZIP_URL}")
    
    try:
        urllib.request.urlretrieve(PYTHON_ZIP_URL, zip_path)
    except Exception as e:
        print(f"[!] Failed to download Python: {e}")
        raise

    print(f"[*] Extracting Python to {PYTHON_DIR}...")
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(PYTHON_DIR)
    except Exception as e:
        print(f"[!] Failed to extract Python: {e}")
        raise
    finally:
        if zip_path.exists():
            zip_path.unlink()
    print("[+] Python environment ready.")

def install_dependencies():
    """Install dependencies from requirements.txt into the lib/ folder."""
    print(f"[*] Installing dependencies to {LIB_DIR}...")
    if not REQUIREMENTS_FILE.exists():
        print(f"[!] Requirements file not found: {REQUIREMENTS_FILE}")
        return

    try:
        # Use sys.executable to ensure we use the same pip as the current environment
        subprocess.check_call([
            sys.executable, "-m", "pip", "install",
            "--target", str(LIB_DIR),
            "-r", str(REQUIREMENTS_FILE),
            "--no-cache-dir"
        ])
    except subprocess.CalledProcessError as e:
        print(f"[!] Failed to install dependencies: {e}")
        raise
    print("[+] Dependencies installed.")

def copy_app_files():
    """Copy application source code and launch scripts."""
    print(f"[*] Copying app files and launch.bat...")
    
    if not APP_SOURCE_DIR.exists():
        print(f"[!] App source directory not found: {APP_SOURCE_DIR}")
        raise FileNotFoundError(f"{APP_SOURCE_DIR} not found")

    # Copy the app package
    shutil.copytree(APP_SOURCE_DIR, TARGET_DIR / "app")
    
    # Copy launch.bat
    if LAUNCH_BAT_SOURCE.exists():
        shutil.copy2(LAUNCH_BAT_SOURCE, TARGET_DIR / "launch.bat")
    else:
        print(f"[!] Warning: {LAUNCH_BAT_SOURCE} not found. Skipping.")
    
    # Create the .portable marker file
    (TARGET_DIR / ".portable").touch()
    
    print("[+] App files copied and .portable marker created.")

def main():
    """Main execution flow."""
    print("=== NIS2 Portable Build Started ===")
    try:
        setup_directories()
        download_python()
        install_dependencies()
        copy_app_files()
        print("\n[SUCCESS] Portable build complete!")
        print(f"[+] Target: {TARGET_DIR}")
        print("[+] You can now ZIP the 'dist/portable' folder for distribution.")
    except Exception as e:
        print(f"\n[ERROR] Build failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
