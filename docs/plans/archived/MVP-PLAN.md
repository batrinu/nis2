# NIS2 Field Audit App — MVP Plan

## What We're Building

A Python CLI + TUI app that your uncle uses **on-site** to perform NIS2 compliance audits. He connects his laptop to a client's network (wired or wireless), and the app guides him through the full audit workflow — from entity classification to network device interrogation to final report generation.

## Who Uses This

- **Your uncle** = the auditor. Goes on-location with his laptop.
- **You** = build the MVP with Kimi Code.
- **He** = polishes/extends it with GitHub Copilot CLI.

## Core User Journey

```
1. ARRIVE ON-SITE
   └─> Launch app, create new audit session
   └─> Input entity info (name, sector, size, turnover)
   └─> App classifies: Essential Entity / Important Entity / Out of scope

2. NETWORK DISCOVERY
   └─> Connect laptop to client network (Ethernet or WiFi)
   └─> App scans the local subnet(s) for active devices
   └─> Identifies routers, switches, firewalls, servers by fingerprinting
   └─> Presents a device inventory map

3. DEVICE INTERROGATION
   └─> Auditor provides credentials for each device (or group creds)
   └─> App connects via SSH/Telnet to routers, switches, firewalls
   └─> Auto-discovers device type (Cisco, Juniper, MikroTik, etc.)
   └─> Runs NIS2-relevant show commands:
       - Running config (sanitized)
       - Firmware version (patch compliance)
       - ACL/firewall rules
       - Port security settings
       - SNMP configuration
       - NTP/logging settings
       - User accounts & privileges
       - Interface status & VLANs
       - Routing tables
       - Encryption/VPN settings

4. GUIDED ASSESSMENT
   └─> App walks auditor through NIS2 Article 21 checklist
   └─> For each domain (Governance, Technical, Incident Response, etc.)
       auditor answers questions + app correlates with device data
   └─> Scores each domain using the existing scoring framework

5. GAP ANALYSIS & FINDINGS
   └─> App identifies gaps between device configs and NIS2 requirements
   └─> Generates prioritized findings with severity levels
   └─> Maps findings to specific NIS2 articles

6. REPORT GENERATION
   └─> Produces audit report (JSON + Markdown + PDF)
   └─> Includes device inventory, configs (sanitized), scores, gaps
   └─> Calculates potential sanctions exposure
```

## Tech Stack

| Component | Technology | Why |
|---|---|---|
| Language | Python 3.11+ | Existing codebase, great network libraries |
| CLI Framework | Typer + Rich | Beautiful TUI, progress bars, tables |
| Network Scanning | Nmap (python-nmap) | Industry standard, device fingerprinting |
| Device SSH/CLI | Netmiko | 80+ device types, auto-detection, handles CLI quirks |
| Device Abstraction | NAPALM (optional) | Structured data from multi-vendor devices |
| Data Models | Pydantic (existing) | Already in the codebase |
| Config Parsing | TextFSM + NTC Templates | Parse show command output into structured data |
| Reports | Jinja2 + weasyprint | Markdown templates → PDF |
| Storage | SQLite | Portable, single-file, works offline |
| Wifi Analysis | scapy (optional) | Wireless security assessment |

## MVP Scope (v0.1)

### IN SCOPE
- [ ] Entity classification (reuse existing classifier agent)
- [ ] Network discovery via nmap (scan local subnet)
- [ ] SSH connection to devices via Netmiko with credential input
- [ ] Auto-detect device type
- [ ] Run pre-defined NIS2 audit commands per device type
- [ ] Guided checklist walkthrough (Article 21 domains)
- [ ] Basic gap analysis correlating device data with requirements
- [ ] Markdown report generation
- [ ] SQLite session persistence (resume interrupted audits)
- [ ] Rich TUI with colors, progress bars, device tables

### OUT OF SCOPE (v0.2+)
- SNMP polling
- Wireless security scanning (WiFi assessment)
- PDF generation
- Auto-remediation suggestions
- Dashboard / web UI
- Multi-auditor collaboration
- Cloud sync of audit sessions
- Vulnerability scanning integration (Nessus, OpenVAS)
- Full NAPALM abstraction layer

## Project Structure

```
nis2-audit-app/
├── app/
│   ├── __init__.py
│   ├── cli.py                    # Typer CLI entry point
│   ├── tui/                      # Rich TUI screens
│   │   ├── __init__.py
│   │   ├── dashboard.py          # Main audit dashboard
│   │   ├── device_table.py       # Device inventory display
│   │   └── checklist.py          # Interactive NIS2 checklist
│   ├── scanner/                  # Network discovery
│   │   ├── __init__.py
│   │   ├── network_scanner.py    # Nmap-based subnet scan
│   │   └── device_fingerprint.py # OS/device type identification
│   ├── connector/                # Device SSH/CLI
│   │   ├── __init__.py
│   │   ├── device_manager.py     # Connection lifecycle
│   │   ├── command_runner.py     # Execute & parse commands
│   │   └── command_sets/         # Per-vendor NIS2 commands
│   │       ├── cisco_ios.py
│   │       ├── cisco_asa.py
│   │       ├── juniper_junos.py
│   │       ├── mikrotik.py
│   │       ├── fortinet.py
│   │       ├── generic_linux.py
│   │       └── __init__.py
│   ├── audit/                    # NIS2 assessment engine
│   │   ├── __init__.py
│   │   ├── classifier.py         # Entity classification (from existing)
│   │   ├── checklist.py          # Article 21 domain questions
│   │   ├── scorer.py             # Compliance scoring
│   │   ├── gap_analyzer.py       # Device data ↔ requirements correlation
│   │   └── knowledge_base/       # NIS2 reference data (from existing)
│   ├── report/                   # Report generation
│   │   ├── __init__.py
│   │   ├── generator.py          # Compile findings → report
│   │   └── templates/            # Jinja2 report templates
│   ├── storage/                  # Session persistence
│   │   ├── __init__.py
│   │   └── db.py                 # SQLite operations
│   └── models/                   # Pydantic data models
│       ├── __init__.py
│       ├── entity.py
│       ├── device.py
│       ├── finding.py
│       ├── audit_session.py
│       └── scan_result.py
├── tests/
├── requirements.txt
├── pyproject.toml
└── README.md
```

## Implementation Batches

### Batch 1: Foundation (Kimi builds)
1. Project scaffold + models + CLI shell
2. Entity classifier (port from existing)
3. SQLite session storage
4. Basic Rich TUI dashboard

### Batch 2: Network Discovery (Kimi builds)
5. Nmap subnet scanner
6. Device fingerprinting
7. Device inventory TUI table

### Batch 3: Device Connector (Kimi builds)
8. Netmiko connection manager with credential input
9. Auto-detect device type
10. Cisco IOS command set (most common)
11. Generic Linux command set
12. Command output parsing with TextFSM

### Batch 4: Audit Engine (Kimi builds)
13. Article 21 checklist walker
14. Compliance scorer (port from existing)
15. Gap analyzer (correlate device data → NIS2 gaps)
16. Findings generator with severity levels

### Batch 5: Reports (Kimi builds)
17. Markdown report with Jinja2 templates
18. JSON export for machine consumption
19. Sanction exposure calculator (port from existing)

### Batch 6: Polish (Copilot polishes)
20. Additional device command sets (Juniper, MikroTik, Fortinet)
21. Better TUI flows and error handling
22. Edge case handling for weird device CLIs
23. More detailed Article 21 questions per sector
24. Config sanitization (mask passwords in reports)

## Key NIS2 Audit Commands by Device Type

### Cisco IOS/IOS-XE
```
show version                    # Firmware, patch level
show running-config             # Full config (sanitize passwords)
show access-lists               # ACL rules
show ip interface brief         # Interface status
show vlan brief                 # VLAN segmentation
show ntp status                 # Time sync (logging integrity)
show logging                    # Syslog config
show snmp                       # SNMP version/community
show users                      # Active sessions
show privilege                  # Privilege levels
show crypto isakmp sa           # VPN tunnels
show ip ssh                     # SSH version
show aaa                        # Authentication config
show port-security              # Port security
show spanning-tree summary      # STP (network resilience)
```

### Generic Linux (Servers/Firewalls)
```
uname -a                        # OS version
cat /etc/os-release             # Distribution
iptables -L -n                  # Firewall rules
ss -tlnp                        # Listening ports
cat /etc/ssh/sshd_config        # SSH hardening
cat /etc/passwd                 # User accounts
last -20                        # Recent logins
systemctl list-unit-files       # Running services
cat /etc/rsyslog.conf           # Logging config
timedatectl                     # NTP status
openssl version                 # Crypto version
df -h                           # Disk (backup capacity)
cat /etc/sudoers                # Privilege escalation
```

## Risk Disclaimers
- App does NOT modify any device configurations (read-only)
- Credentials are stored encrypted in local SQLite, never transmitted
- Network scanning should only be done with explicit written authorization
- This tool assists auditors — it does not replace professional judgment
