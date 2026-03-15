# Copilot CLI — NIS2 Audit App Polish Instructions

## Context

This app was built as an MVP with Kimi Code. Your job is to polish, extend, and harden it.
The app is a Python CLI + Rich TUI for on-site NIS2 compliance auditing. The auditor
connects to a client's network, scans for devices, SSH-es into routers/switches/firewalls
via Netmiko, collects config data, walks through an Article 21 checklist, scores compliance,
and generates reports.

## Your Priorities (in order)

### 1. Error Handling & Edge Cases
- Every Netmiko connection needs timeout handling and retry logic
- Every nmap scan needs graceful failure if nmap isn't installed
- Every user prompt needs input validation
- Every file operation needs permission error handling
- Test with: no network access, wrong credentials, unknown device types, partial scan results

### 2. Additional Device Command Sets
Add these vendor command sets (see `app/connector/command_sets/` for pattern):
- `juniper_junos.py` — Juniper routers/switches
- `cisco_asa.py` — Cisco ASA firewalls
- `fortinet.py` — FortiGate firewalls
- `hp_procurve.py` — HP/Aruba switches
- `paloalto_panos.py` — Palo Alto firewalls

Each command set maps vendor-specific `show` commands to NIS2 audit domains.
Follow the pattern in `cisco_ios.py` — dict of commands with `cmd`, `nis2` domain, and `checks`.

### 3. Config Sanitization Hardening
The `sanitize_config()` function needs to catch ALL sensitive patterns:
- Cisco: `password`, `secret`, `community`, `key-string`, `key-chain`
- Juniper: `secret`, `authentication-key`, `community`
- Linux: passwords in config files, SSH keys
- FortiGate: `set password`, `set psksecret`
- Generic: API keys, tokens, certificates (base64 blocks)

### 4. TUI Polish
- Consistent color theme throughout (use Rich Theme)
- Keyboard shortcuts shown at bottom of every screen
- Loading spinners for all async operations
- Clear error messages (not stack traces) for all failures
- Confirmation prompts before destructive actions (delete session, etc.)

### 5. Assessment Engine Refinement
- More granular Article 21 checklist questions (aim for 30-40 per domain)
- Cross-reference device findings with manual checklist answers
- Better gap analysis narratives (not just "missing X", but "X is required by Art.21.h because...")
- Sector-specific questions (energy sector has different concerns than digital infrastructure)

### 6. Testing
- Unit tests for scoring logic, sanitization, entity classification
- Integration tests for Netmiko connections (use mock devices or recorded sessions)
- Snapshot tests for report output
- Test with at least 3 different device types

## Architecture Notes

- `app/cli.py` — Typer commands. Don't add business logic here, just dispatch.
- `app/tui/` — Rich screens. Keep display separate from logic.
- `app/connector/` — Netmiko connections. One file per vendor in command_sets/.
- `app/audit/` — NIS2 engine. classifier.py, checklist.py, scorer.py, gap_analyzer.py
- `app/models/` — Pydantic v2 models. All data shapes defined here.
- `app/storage/` — SQLite via stdlib sqlite3. No ORM.
- `app/report/` — Jinja2 templates → Markdown → (optionally PDF).

## Rules

1. **READ ONLY** — The app NEVER modifies device configurations. Only `show` commands.
2. **Credentials never in reports** — Always sanitize before storing/displaying.
3. **Offline-first** — App must work without internet access.
4. **Graceful degradation** — If a tool/library isn't available, fall back, don't crash.
5. **Python 3.11+** — Use modern syntax. Type hints on all functions.
6. **Dependencies**: Typer, Rich, Netmiko, python-nmap, Pydantic v2, Jinja2, cryptography.

## Getting Started

```bash
cd nis2-audit-app
pip install -r requirements.txt
python -m app.cli --help
```
