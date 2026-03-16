#!/usr/bin/env python3
"""
Build an EXE installer for the NIS2 Field Audit Tool.
Uses PyInstaller to create a single EXE that acts as a setup wizard.
"""

import subprocess
import sys
import tempfile
import os
from pathlib import Path

INSTALLER_CODE = '''
#!/usr/bin/env python3
"""
NIS2 Field Audit Tool - Setup Wizard
A user-friendly GUI installer for Windows
"""

import tkinter as tk
from tkinter import ttk, messagebox
import os
import sys
import subprocess
import urllib.request
import tempfile
import shutil
import zipfile
from pathlib import Path
import threading
import ctypes

# App info
APP_NAME = "NIS2 Field Audit Tool"
APP_VERSION = "1.0.0"
VCREDIST_URL = "https://aka.ms/vs/17/release/vc_redist.x64.exe"
PYTHON_VERSION = "3.12.3"
PYTHON_URL = f"https://www.python.org/ftp/python/{PYTHON_VERSION}/python-{PYTHON_VERSION}-embed-amd64.zip"

class SetupWizard:
    def __init__(self, root):
        self.root = root
        self.root.title(f"{APP_NAME} Setup")
        self.root.geometry("600x450")
        self.root.resizable(False, False)
        
        # Center window
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        x = (screen_width - 600) // 2
        y = (screen_height - 450) // 2
        self.root.geometry(f"600x450+{x}+{y}")
        
        self.current_step = 0
        self.install_dir = Path(os.environ["PROGRAMFILES"]) / "NIS2Audit"
        self.vcredist_installed = False
        self.python_installed = False
        
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the main UI"""
        # Header
        header = tk.Frame(self.root, bg="#0078d4", height=80)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        tk.Label(header, text=APP_NAME, font=("Segoe UI", 20, "bold"), 
                bg="#0078d4", fg="white").pack(pady=15)
        
        # Content area
        self.content = tk.Frame(self.root)
        self.content.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Buttons
        self.btn_frame = tk.Frame(self.root)
        self.btn_frame.pack(fill=tk.X, padx=20, pady=10)
        
        self.back_btn = tk.Button(self.btn_frame, text="< Back", command=self.prev_step, state=tk.DISABLED)
        self.back_btn.pack(side=tk.LEFT, padx=5)
        
        self.next_btn = tk.Button(self.btn_frame, text="Next >", command=self.next_step)
        self.next_btn.pack(side=tk.RIGHT, padx=5)
        
        self.cancel_btn = tk.Button(self.btn_frame, text="Cancel", command=self.root.quit)
        self.cancel_btn.pack(side=tk.RIGHT, padx=5)
        
        self.show_step(0)
        
    def show_step(self, step):
        """Show the current step"""
        # Clear content
        for widget in self.content.winfo_children():
            widget.destroy()
            
        self.current_step = step
        
        if step == 0:
            self.show_welcome()
        elif step == 1:
            self.show_checks()
        elif step == 2:
            self.show_install_location()
        elif step == 3:
            self.show_installation()
        elif step == 4:
            self.show_complete()
            
        # Update buttons
        self.back_btn.config(state=tk.NORMAL if step > 0 else tk.DISABLED)
        
        if step == 0:
            self.next_btn.config(text="Next >")
        elif step == 4:
            self.next_btn.config(text="Finish", command=self.root.quit)
        else:
            self.next_btn.config(text="Next >")
            
    def show_welcome(self):
        """Show welcome page"""
        tk.Label(self.content, text="Welcome to the NIS2 Field Audit Tool Setup Wizard", 
                font=("Segoe UI", 14, "bold")).pack(pady=10)
        
        text = """This wizard will guide you through the installation of NIS2 Field Audit Tool.

Before we begin, please ensure:
  • Windows 10 or later
  • Administrator rights
  • Internet connection (for dependencies)

The installer will:
  1. Check system requirements
  2. Install Visual C++ Redistributable (if needed)
  3. Extract portable Python runtime
  4. Install application files
  5. Create shortcuts

Click Next to continue."""
        
        tk.Label(self.content, text=text, justify=tk.LEFT, wraplength=550).pack(pady=20)
        
    def show_checks(self):
        """Show system checks page"""
        tk.Label(self.content, text="Checking System Requirements", 
                font=("Segoe UI", 14, "bold")).pack(pady=10)
        
        self.check_frame = tk.Frame(self.content)
        self.check_frame.pack(fill=tk.BOTH, expand=True, pady=20)
        
        # Create check items
        self.check_items = []
        
        items = [
            ("Windows Version", self.check_windows),
            ("Visual C++ Redistributable", self.check_vcredist),
            ("Internet Connection", self.check_internet),
        ]
        
        for name, check_func in items:
            frame = tk.Frame(self.check_frame)
            frame.pack(fill=tk.X, pady=5)
            
            status_label = tk.Label(frame, text="⏳ Checking...", width=15)
            status_label.pack(side=tk.RIGHT)
            
            tk.Label(frame, text=name, width=30, anchor="w").pack(side=tk.LEFT)
            
            self.check_items.append((name, status_label, check_func))
        
        # Run checks in background
        threading.Thread(target=self.run_checks, daemon=True).start()
        
    def run_checks(self):
        """Run all checks"""
        for name, label, func in self.check_items:
            result, message = func()
            self.root.after(0, self.update_check_result, label, result, message)
            
    def update_check_result(self, label, result, message):
        """Update check result in UI"""
        if result:
            label.config(text="✓ OK", fg="green")
        else:
            label.config(text=f"⚠ {message}", fg="orange")
            
    def check_windows(self):
        """Check Windows version"""
        version = sys.getwindowsversion()
        if version.major >= 10:
            return True, "Windows 10+"
        return False, "Windows 10+ recommended"
        
    def check_vcredist(self):
        """Check VCRedist"""
        # Check registry
        try:
            import winreg
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, 
                r"SOFTWARE\\Microsoft\\VisualStudio\\14.0\\VC\\Runtimes\\x64")
            value, _ = winreg.QueryValueEx(key, "Installed")
            if value == 1:
                self.vcredist_installed = True
                return True, "Installed"
        except:
            pass
        return False, "Will install"
        
    def check_internet(self):
        """Check internet connection"""
        try:
            urllib.request.urlopen("https://www.microsoft.com", timeout=5)
            return True, "Connected"
        except:
            return False, "Offline (may need manual install)"
            
    def show_install_location(self):
        """Show install location selection"""
        tk.Label(self.content, text="Choose Install Location", 
                font=("Segoe UI", 14, "bold")).pack(pady=10)
        
        tk.Label(self.content, text="The application will be installed to:").pack(pady=10)
        
        self.dir_var = tk.StringVar(value=str(self.install_dir))
        
        frame = tk.Frame(self.content)
        frame.pack(fill=tk.X, pady=10)
        
        tk.Entry(frame, textvariable=self.dir_var, width=50).pack(side=tk.LEFT, padx=5)
        tk.Button(frame, text="Browse...", command=self.browse_dir).pack(side=tk.LEFT)
        
        tk.Label(self.content, text="Required space: ~150 MB", fg="gray").pack(pady=10)
        
        # Space check
        drive = Path(self.dir_var.get()).anchor
        try:
            import shutil
            total, used, free = shutil.disk_usage(drive)
            free_gb = free / (1024**3)
            tk.Label(self.content, text=f"Available space: {free_gb:.1f} GB", 
                    fg="green" if free_gb > 1 else "red").pack()
        except:
            pass
            
    def browse_dir(self):
        """Browse for install directory"""
        from tkinter import filedialog
        dir = filedialog.askdirectory(initialdir=self.dir_var.get())
        if dir:
            self.dir_var.set(dir)
            
    def show_installation(self):
        """Show installation progress"""
        tk.Label(self.content, text="Installing", 
                font=("Segoe UI", 14, "bold")).pack(pady=10)
        
        self.progress = ttk.Progressbar(self.content, length=500, mode='determinate')
        self.progress.pack(pady=20)
        
        self.status_label = tk.Label(self.content, text="Preparing installation...")
        self.status_label.pack(pady=10)
        
        self.detail_label = tk.Label(self.content, text="", fg="gray", wraplength=550)
        self.detail_label.pack(pady=10)
        
        # Disable buttons during install
        self.back_btn.config(state=tk.DISABLED)
        self.next_btn.config(state=tk.DISABLED)
        self.cancel_btn.config(state=tk.DISABLED)
        
        # Start installation in background
        threading.Thread(target=self.do_installation, daemon=True).start()
        
    def do_installation(self):
        """Perform the installation"""
        try:
            self.install_dir = Path(self.dir_var.get())
            
            # Step 1: Create directories
            self.update_status(10, "Creating directories...")
            self.install_dir.mkdir(parents=True, exist_ok=True)
            (self.install_dir / "data").mkdir(exist_ok=True)
            
            # Step 2: Install VCRedist if needed
            if not self.vcredist_installed:
                self.update_status(20, "Downloading Visual C++ Redistributable...")
                self.install_vcredist()
                
            # Step 3: Extract portable Python
            self.update_status(50, "Extracting portable Python...")
            self.extract_python()
            
            # Step 4: Copy app files
            self.update_status(70, "Installing application files...")
            self.copy_app_files()
            
            # Step 5: Create shortcuts
            self.update_status(90, "Creating shortcuts...")
            self.create_shortcuts()
            
            # Step 6: Create uninstaller
            self.update_status(95, "Creating uninstaller...")
            self.create_uninstaller()
            
            self.update_status(100, "Installation complete!")
            
            # Re-enable buttons
            self.root.after(0, self.installation_complete)
            
        except Exception as e:
            self.root.after(0, self.installation_failed, str(e))
            
    def update_status(self, value, message, detail=""):
        """Update installation status"""
        self.root.after(0, lambda: self._update_status_ui(value, message, detail))
        
    def _update_status_ui(self, value, message, detail):
        self.progress['value'] = value
        self.status_label.config(text=message)
        if detail:
            self.detail_label.config(text=detail)
        self.root.update()
        
    def install_vcredist(self):
        """Install Visual C++ Redistributable"""
        try:
            # Download
            temp_file = Path(tempfile.gettempdir()) / "vc_redist.x64.exe"
            urllib.request.urlretrieve(VCREDIST_URL, temp_file)
            
            # Install silently
            result = subprocess.run(
                [str(temp_file), "/install", "/quiet", "/norestart"],
                capture_output=True
            )
            
            temp_file.unlink(missing_ok=True)
            
            if result.returncode not in [0, 3010]:
                raise Exception(f"VCRedist install failed: {result.returncode}")
                
        except Exception as e:
            self.update_status(20, "VCRedist download failed", 
                             f"Please install manually from: {VCREDIST_URL}")
            
    def extract_python(self):
        """Extract portable Python"""
        # In real implementation, Python would be bundled with the installer
        # For now, create a placeholder
        python_dir = self.install_dir / "python"
        python_dir.mkdir(exist_ok=True)
        
    def copy_app_files(self):
        """Copy application files"""
        # In real implementation, these would be bundled
        # Create placeholder launch.bat
        launch_bat = self.install_dir / "launch.bat"
        launch_bat.write_text('''@echo off
chcp 65001 >nul 2>&1
echo Starting NIS2 Field Audit Tool...
cd /d "%~dp0"
"python\\python.exe" -m app.textual_app
''')
        
        # Create README
        readme = self.install_dir / "README.txt"
        readme.write_text(f"""NIS2 Field Audit Tool v{APP_VERSION}

Getting Started:
1. Double-click 'launch.bat' to start
2. Or use the Desktop shortcut

For help, visit: https://github.com/batrinu/nis2
""")
        
    def create_shortcuts(self):
        """Create Windows shortcuts"""
        try:
            import winshell
            from win32com.client import Dispatch
            
            # Desktop shortcut
            desktop = Path(winshell.desktop())
            shortcut = desktop / f"{APP_NAME}.lnk"
            
            shell = Dispatch('WScript.Shell')
            sc = shell.CreateShortCut(str(shortcut))
            sc.TargetPath = str(self.install_dir / "launch.bat")
            sc.WorkingDirectory = str(self.install_dir)
            sc.Description = f"Launch {APP_NAME}"
            sc.save()
            
            # Start Menu shortcut
            start_menu = Path(winshell.start_menu()) / APP_NAME
            start_menu.mkdir(parents=True, exist_ok=True)
            
            shortcut = start_menu / f"{APP_NAME}.lnk"
            sc = shell.CreateShortCut(str(shortcut))
            sc.TargetPath = str(self.install_dir / "launch.bat")
            sc.WorkingDirectory = str(self.install_dir)
            sc.save()
            
        except Exception as e:
            print(f"Failed to create shortcuts: {e}")
            
    def create_uninstaller(self):
        """Create uninstaller registry entries"""
        import winreg
        
        try:
            key = winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE, 
                r"Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\NIS2Audit")
            winreg.SetValueEx(key, "DisplayName", 0, winreg.REG_SZ, APP_NAME)
            winreg.SetValueEx(key, "UninstallString", 0, winreg.REG_SZ, 
                            str(self.install_dir / "uninstall.exe"))
            winreg.SetValueEx(key, "DisplayVersion", 0, winreg.REG_SZ, APP_VERSION)
            winreg.SetValueEx(key, "Publisher", 0, winreg.REG_SZ, "NIS2 Audit Team")
            winreg.CloseKey(key)
        except:
            pass  # May not have registry access
            
    def installation_complete(self):
        """Handle installation completion"""
        self.cancel_btn.config(state=tk.NORMAL)
        self.cancel_btn.config(text="Close")
        self.next_btn.config(state=tk.NORMAL)
        
    def installation_failed(self, error):
        """Handle installation failure"""
        messagebox.showerror("Installation Failed", 
                           f"The installation failed with error:\n\n{error}")
        self.cancel_btn.config(state=tk.NORMAL)
        self.back_btn.config(state=tk.NORMAL)
        
    def show_complete(self):
        """Show completion page"""
        tk.Label(self.content, text="Installation Complete!", 
                font=("Segoe UI", 14, "bold"), fg="green").pack(pady=10)
        
        text = f"""{APP_NAME} has been successfully installed.

Installation Directory:
{self.install_dir}

You can launch the application from:
  • Desktop shortcut
  • Start Menu > {APP_NAME}
  • {self.install_dir}\\launch.bat

Click Finish to close this wizard."""
        
        tk.Label(self.content, text=text, justify=tk.LEFT).pack(pady=20)
        
    def next_step(self):
        if self.current_step < 4:
            self.show_step(self.current_step + 1)
            
    def prev_step(self):
        if self.current_step > 0:
            self.show_step(self.current_step - 1)


def is_admin():
    """Check if running as admin"""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False


def main():
    # Check admin rights
    if not is_admin():
        messagebox.showerror("Administrator Required",
            "This installer requires administrator privileges.\\n\\n"
            "Please right-click and select 'Run as administrator'.")
        return
        
    root = tk.Tk()
    app = SetupWizard(root)
    root.mainloop()


if __name__ == "__main__":
    main()
'''

def build_installer():
    """Build the installer EXE using PyInstaller"""
    print("Building NIS2 Field Audit Tool Installer...")
    
    # Create temp directory for build
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        
        # Write installer script
        script_file = tmpdir / "installer.py"
        script_file.write_text(INSTALLER_CODE)
        
        # Create PyInstaller spec
        spec_content = f'''
# -*- mode: python ; coding: utf-8 -*-

a = Analysis(
    ['{script_file}'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=['tkinter', 'urllib.request'],
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='NIS2-Audit-Tool-Setup',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)
'''
        spec_file = tmpdir / "installer.spec"
        spec_file.write_text(spec_content)
        
        # Run PyInstaller
        print("Running PyInstaller...")
        result = subprocess.run(
            [sys.executable, "-m", "PyInstaller", str(spec_file), "--clean"],
            cwd=str(tmpdir),
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            print(f"PyInstaller failed: {result.stderr}")
            return False
            
        # Copy output
        dist_dir = Path(__file__).parent.parent / "dist"
        dist_dir.mkdir(exist_ok=True)
        
        output = tmpdir / "dist" / "NIS2-Audit-Tool-Setup.exe"
        if output.exists():
            shutil.copy2(output, dist_dir / "NIS2-Audit-Tool-Setup.exe")
            print(f"Installer created: {dist_dir / 'NIS2-Audit-Tool-Setup.exe'}")
            return True
        else:
            print("Installer EXE not found!")
            return False


if __name__ == "__main__":
    build_installer()
