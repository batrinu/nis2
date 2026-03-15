# NIS2 Field Audit Tool

A cross-platform terminal-based network compliance auditing tool for NIS2 assessments. Built with Python and Textual for a rich, interactive experience on Windows, macOS, and Linux.

## Features

- 🏢 **Entity Classification** — Automatic NIS2 scope determination (Essential/Important/Non-Qualifying)
- 🔍 **Network Scanning** — Discover and inventory network devices
- 🔐 **SSH Assessment** — Connect to devices and gather configuration evidence
- ✅ **Compliance Checklist** — Interactive wizard for NIS2 Articles 20-21 assessment
- 📊 **Findings & Reports** — Auto-generated findings with severity ratings
- 📄 **Report Export** — Generate audit reports (Markdown, HTML, JSON)

## Quick Start

### Windows (PowerShell)
```powershell
pip install nis2-field-audit
nis2-audit
```

Or download and run directly:
```powershell
cd nis2-audit-app
.\nis2-audit.ps1
```

### Windows (CMD)
```cmd
pip install nis2-field-audit
nis2-audit
```

Or:
```cmd
cd nis2-audit-app
nis2-audit.bat
```

### macOS / Linux
```bash
pip install nis2-field-audit
nis2-audit
```

Or:
```bash
cd nis2-audit-app
python -m app.textual_app
```

## Installation

### Prerequisites

- **Python 3.10+** (only requirement!)
- Optional: **nmap** for network scanning

### Install from Source

```bash
cd nis2-audit-app
pip install -e .
```

## Usage

Simply run:
```
nis2-audit
```

This launches the interactive terminal UI with:
- **Splash Screen** — Loading and initialization
- **Dashboard** — Recent audits and quick actions
- **New Session Wizard** — 4-step entity creation
- **Scan Screen** — Network discovery
- **Connect Screen** — SSH device assessment
- **Checklist Wizard** — Compliance assessment
- **Findings Screen** — Review discovered issues
- **Report Screen** — Generate and export reports

### Keyboard Navigation

| Key | Action |
|-----|--------|
| ↑/↓ or Tab | Navigate |
| Enter | Select |
| Escape | Go back |
| Ctrl+C | Exit |

### CLI Commands (Optional)

For scripting and automation:

```bash
# Classic CLI mode
nis2-audit-cli --help

# List sessions
nis2-audit-cli list

# Create session
nis2-audit-cli new --name "Acme Corp" --sector energy --employees 500
```

## Data Storage

All audit data is stored in a local SQLite database (`audit_sessions.db`):
- Session metadata and entity information
- Discovered devices and configurations
- Compliance responses and scores
- Generated findings

## Architecture

```
┌─────────────────────────────────────────────┐
│           Textual TUI (Python)              │
│  ┌─────────┐ ┌─────────┐ ┌───────────────┐  │
│  │ Screens │ │ Widgets │ │ CSS Styling   │  │
│  └─────────┘ └─────────┘ └───────────────┘  │
│                                             │
│  Direct Python calls (no IPC needed)        │
│  ┌─────────┐ ┌─────────┐ ┌───────────────┐  │
│  │ Scanner │ │ Audit   │ │ Report Gen    │  │
│  └─────────┘ └─────────┘ └───────────────┘  │
└─────────────────────────────────────────────┘
```

**Why Textual?**
- Single runtime (Python only)
- Native Windows support (CMD, PowerShell, Windows Terminal)
- No Node.js, npm, or build steps
- Same code works on all platforms
- Modern widget-based TUI

## Project Structure

```
nis2-audit-app/
├── app/
│   ├── textual_app.py      # Main Textual application
│   ├── cli.py              # Classic CLI (Typer)
│   ├── tui/
│   │   ├── app.css         # TUI styling
│   │   └── screens/        # All 8 screens
│   │       ├── splash.py
│   │       ├── dashboard.py
│   │       ├── new_session.py
│   │       ├── scan.py
│   │       ├── connect.py
│   │       ├── checklist.py
│   │       ├── findings.py
│   │       └── report.py
│   ├── audit/              # Compliance logic
│   ├── scanner/            # Network scanning
│   ├── connector/          # SSH connections
│   ├── report/             # Report generation
│   └── storage/            # SQLite database
├── nis2-audit.bat          # Windows CMD launcher
├── nis2-audit.ps1          # PowerShell launcher
└── pyproject.toml          # Package config
```

## License

MIT — Built for security auditors and compliance teams.
