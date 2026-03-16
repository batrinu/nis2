# Changelog

All notable changes to the NIS2 Field Audit Tool project.

## [1.0.1] - 2026-03-16

### 🐛 Windows Bug Fixes

#### Terminal Size Detection (Critical Fix)
- **Fixed**: Batch script variable error - `%%h` was not valid in for-loop
  - Changed to `%%x` (correct consecutive variable after `%%w`)
  - Added fallback using `mode con` when PowerShell fails
  - Error message now shows actual terminal size instead of `%h`

#### UTF-8 / Romanian Character Support
- **Added**: `chcp 65001` at startup for proper UTF-8 encoding
- **Fixed**: Romanian diacritics (ăâîșț) now display correctly on Windows
- **Added**: `PYTHONIOENCODING=utf-8` environment variable

#### Terminal Compatibility
- **Added**: PowerShell ISE detection with helpful error message
- **Added**: `FORCE_COLOR=1` for better TUI color support on Windows
- **Added**: Fallback terminal size detection via `mode con`
- **Added**: Code page restoration on exit (`chcp 437`)

#### Error Handling
- **Improved**: Virtual environment activation error messages
- **Added**: Antivirus blocking detection and guidance
- **Added**: Python path verification in launchers

### 📦 New Features

#### Windows EXE Installer
- **Created**: Professional NSIS-based installer (`scripts/NIS2_Installer.nsi`)
  - System requirement checks with visual feedback
  - Automatic Visual C++ Redistributable download & install
  - Portable Python extraction
  - Desktop & Start Menu shortcuts
  - Proper uninstaller with Add/Remove Programs entry
  
- **Created**: Python GUI installer builder (`scripts/build_installer_exe.py`)
  - Modern Tkinter wizard interface
  - Real-time progress bars
  - Dependency checks with visual status

#### Documentation
- **Added**: Comprehensive Windows Installer guide (`docs/guides/WINDOWS_INSTALLER.md`)
- **Updated**: Windows Setup guide with troubleshooting for new fixes
- **Updated**: Uncle Experience guide with Windows terminal info
- **Added**: This CHANGELOG.md

### 🔧 Files Modified

- `START.bat` - Terminal size fix, UTF-8 support, better error handling
- `nis2-audit-app/launch.bat` - Same fixes for portable version
- `docs/guides/WINDOWS_SETUP.md` - Added troubleshooting section
- `docs/guides/UNCLE_EXPERIENCE.md` - Added Windows terminal support info
- `README.md` - Updated documentation links and features

### 🙏 Thanks

Thanks to Aurel (Uncle) for reporting the terminal size issue on Windows and helping test the fixes!

---

## [1.0.0] - 2026-03-12

### 🎉 Initial Release

#### Core Features
- **Interactive TUI**: Rich terminal interface with dashboard, wizards, and forms
- **Network Discovery**: Nmap-based scanning with real-time device discovery
- **SSH Interrogation**: Connect to Cisco, Linux, and other network devices
- **Compliance Checklist**: Interactive NIS2 compliance assessment
- **Report Generation**: Export to Markdown, HTML, JSON, PDF

#### User Experience
- **21 Polish Loops**: Comprehensive UX refinement
- **Achievement System**: Gamified progress tracking
- **Accessibility**: Full keyboard navigation, screen reader support
- **Auto-Save**: Work preserved every 30-60 seconds
- **Error Recovery**: Helpful error messages with solutions

#### Security
- **32 Security Passes**: Production-grade hardening
- **CVE Protections**: Fixes for known vulnerabilities
- **Network Safety**: SSRF prevention, DNS rebinding protection
- **Data Integrity**: Secure file permissions, encrypted credentials

#### Architecture
- **Multi-Agent System**: Classifier, Assessor, Gap Analyst, Enforcement Officer
- **Orchestrator**: Coordinated 5-phase audit methodology
- **Knowledge Base**: NIS2 Directive regulatory database
- **Portable Distribution**: Zero-install Windows version

### 📁 Project Structure

```
nis2-assessment/
├── nis2-audit-app/           # Interactive Field Audit Tool (TUI)
├── agents/                   # Specialized AI Agents
├── core/                     # Orchestrator and coordination logic
├── docs/                     # Centralized Documentation
├── scripts/                  # Build and utility scripts
├── shared/                   # Pydantic models and Knowledge Base
└── main.py                   # Engine CLI entry point
```

---

## Version Format

This project follows [Semantic Versioning](https://semver.org/):

- **MAJOR**: Incompatible API changes
- **MINOR**: New functionality (backward compatible)
- **PATCH**: Bug fixes (backward compatible)
