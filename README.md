# NIS2 Compliance Assessment System

A comprehensive multi-agent system and interactive toolkit for assessing compliance with Directive (EU) 2022/2555 (NIS2) on cybersecurity risk management measures.

## 🚀 Two Ways to Audit

The system consists of two primary components designed to work together or independently:

### 1. NIS2 Field Audit Tool (Interactive TUI)
Located in `nis2-audit-app/`, this is a cross-platform terminal application for on-site audits.
- **Interactive UI**: Rich dashboard, splash screens, and step-by-step wizards.
- **Network Discovery**: Built-in nmap-based scanning to inventory devices.
- **SSH Interrogation**: Connect to devices (Cisco, Linux, etc.) to gather configuration evidence.
- **Portable Distribution**: A "Zero-Install" Windows version is available (no Python required).
- **Professional Windows Installer**: EXE setup wizard with dependency auto-install.
- **Windows Optimized**: Full UTF-8 support for Romanian, terminal size auto-detection, color support.
- **[Go to Field Audit Tool Guide](docs/guides/USER_QUICKSTART.md)**

### 2. NIS2 Assessment Engine (Multi-Agent Backend)
The core logic located in the root directory, providing specialized AI agents for deep regulatory analysis.
- **Specialized Agents**: Classifier, Assessor, Enforcement Officer, Gap Analyst, and Sector Specialists.
- **Orchestration**: Coordinated 5-phase audit methodology.
- **[Go to Developer Guide](docs/guides/DEVELOPER_GUIDE.md)**

---

## 📖 Documentation

All documentation is centralized in the [docs/](docs/) directory:

- 🏁 **[User QuickStart](docs/guides/USER_QUICKSTART.md)** — Start your first audit in minutes.
- 🪟 **[Windows Setup](docs/guides/WINDOWS_SETUP.md)** — Detailed instructions for Windows users.
- 📦 **[Windows EXE Installer](docs/guides/WINDOWS_INSTALLER.md)** — Professional installer creation guide.
- 👨‍💼 **[Uncle Experience Guide](docs/guides/UNCLE_EXPERIENCE.md)** — Designed for non-technical users.
- 🛠️ **[Developer Guide](docs/guides/DEVELOPER_GUIDE.md)** — Architecture and internal TUI components.
- 📊 **[Reports & Summaries](docs/reports/)** — Security audits and accessibility summaries.
- 📐 **[Technical Specs](docs/specs/ORCHESTRATOR_SPEC.md)** — Agent and orchestrator specifications.
- 🛡️ **[Security Hardening](docs/security/SECURITY.md)** — Details on the 32 security passes.

---

## ⚡ Quick Start (Engine)

### Installation
```bash
pip install -r requirements.txt
```

### Command Line Usage
```bash
# Interactive engine mode
python main.py interactive

# Run full audit on a mock entity
python main.py audit --mock EE-ENERGY-001 --output audit.json
```

---

## 🏛️ Architecture

```
nis2-assessment/
├── nis2-audit-app/           # Interactive Field Audit Tool (TUI)
├── agents/                   # Specialized AI Agents (Classifier, Assessor, etc.)
├── core/                     # Orchestrator and coordination logic
├── docs/                     # Centralized Documentation
├── scripts/                  # Build and utility scripts
├── shared/                   # Pydantic models and Knowledge Base
└── main.py                   # Engine CLI entry point
```

---

## 🛡️ Security & Hardening

This application implements **32 security hardening passes** with production-grade measures based on 2026 vulnerability research, including:

- **CVE Protections**: Fixes for CVE-2026-26007, CVE-2026-3484, and many others.
- **Network Safety**: SSRF prevention, DNS rebinding protection, and SSH prefix truncation patches.
- **Data Integrity**: Atomic writes, secure file permissions (0o600), and encrypted credential handling.
- **Supply Chain**: TYposquatting protection and hash-verified dependencies.

**[Read the Full Security Specification](docs/security/SECURITY.md)**

---

## ⚖️ Legal Disclaimer

This system is for regulatory compliance assessment purposes under Directive (EU) 2022/2555. It does not constitute legal advice. Entities should consult qualified legal counsel for interpretation of specific obligations.

## 📄 License

MIT License - See LICENSE file for details.
