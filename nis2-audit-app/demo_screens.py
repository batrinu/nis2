#!/usr/bin/env python3
"""
Demo script showing what each screen looks like.
Run this to see the UI without launching the full TUI.
"""

DEMO = """
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║                    🛡️  NIS2 FIELD AUDIT TOOL  🛡️                            ║
║                                                                              ║
║                         [DEMO MODE]                                          ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝

═══════════════════════════════════════════════════════════════════════════════
 SCREEN 1: DASHBOARD (First Launch)
═══════════════════════════════════════════════════════════════════════════════

┌─ 🚀 QUICK ACTIONS ───┬─ 📋 RECENT AUDIT SESSIONS ─────────────────────────┐
│                      │                                                    │
│  🆕 New Audit        │   ╔═══════════════════════════════════════════╗    │
│  🔄 Refresh          │   ║                                           ║    │
│  ❓ Help [F1]        │   ║   🔐  📊  🖥️  🔍  📋                      ║    │
│  ❌ Exit             │   ║                                           ║    │
│                      │   ║      Welcome! Let's start                 ║    │
│  📊 STATISTICS       │   ║      your first audit.                    ║    │
│                      │   ║                                           ║    │
│  📋 Total Audits: 0  │   ╚═══════════════════════════════════════════╝    │
│                      │                                                    │
│  Create your first!  │   [✨ Create Your First Audit]                     │
│                      │                                                    │
└──────────────────────┴────────────────────────────────────────────────────┘
💡 Tip: Press 'N' to create a new audit, or F1 for help

═══════════════════════════════════════════════════════════════════════════════
 SCREEN 2: NEW SESSION WIZARD (Step 1 of 4)
═══════════════════════════════════════════════════════════════════════════════

┌─ NEW AUDIT SESSION ─────────────────────────────────────────────────────────┐
│                                                                             │
│  Step 1 of 4: Entity Information                                            │
│  [████████░░░░░░░░░░] 25%                                                   │
│                                                                             │
│  Enter the basic information about the entity being audited.                │
│                                                                             │
│  Entity Name:*    [________________________]  ← Type here                   │
│                                                                             │
│  Sector:*         [▼ Energy                 ]  ← Press Space to open        │
│                                                                             │
│  Employee Count:* [________________________]                                │
│                                                                             │
│  Annual Turnover  [________________________]  (Optional)                    │
│                                                                             │
│  💾 Auto-save ready                                                         │
│                                                                             │
│  [◀ Back] [Next ▶] [Cancel]                                                 │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘

═══════════════════════════════════════════════════════════════════════════════
 SCREEN 3: NETWORK SCAN
═══════════════════════════════════════════════════════════════════════════════

┌─ 🔍 NETWORK SCANNER ────────────────────────────────────────────────────────┐
│                                                                             │
│  Target: [192.168.1.0/24____] [▶ Start Scan (S)] [⏹ Cancel (C)]             │
│                                                                             │
│  🔍 Scanning 192.168.1.0/24...                                              │
│  [████████████████████░░░░░░░░░░] 66%                                       │
│                                                                             │
│  💡 Did you know? NIS2 applies to over 160,000 organizations across the EU  │
│                                                                             │
│  📡 Live Device Discovery                        Found: 3 devices           │
│  ┌─────────────────────────────────────────┐                                │
│  │ 🚀 Starting scan of 192.168.1.0/24...   │                                │
│  │ 📡 Host discovery phase...              │                                │
│  │ 🌐 Found router at 192.168.1.1          │                                │
│  │ 🖥️  Found server at 192.168.1.10        │                                │
│  │ 🖨️  Found printer at 192.168.1.20       │                                │
│  └─────────────────────────────────────────┘                                │
│                                                                             │
│  🗺️ Network Topology                                                        │
│       ┌─────────────┐                                                       │
│       │   Scanner   │                                                       │
│       └──────┬──────┘                                                       │
│              ├── 🌐 router                                                  │
│              ├── 🖥️  server                                                 │
│              └── 🖨️  printer                                                │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘

═══════════════════════════════════════════════════════════════════════════════
 SCREEN 4: COMPLIANCE CHECKLIST
═══════════════════════════════════════════════════════════════════════════════

┌─ ✅ NIS2 COMPLIANCE ASSESSMENT ─────────────────────────────────────────────┐
│                                                                             │
│  📊 Compliance Score: [████████████████░░░░░░] 73%                          │
│                                                                             │
│  ┌─ 📋 Sections ─┬─ QUESTION AREA ──────────────────────────────────────┐   │
│  │               │                                                      │   │
│  │ 📋 Sections   │  Section: Risk Management                            │   │
│  │               │                                                      │   │
│  │ ☑ Risk Mgmt   │  Question 2/5 in this section                        │   │
│  │ ☐ Incident    │  Overall progress: 12/25 answered                    │   │
│  │ ☐ Access      │                                                      │   │
│  │ ☐ Data Prot   │  Q2: Do you have documented incident                 │   │
│  │               │      response procedures?                            │   │
│  │               │                                                      │   │
│  │               │  💡 Why are we asking this? (Press H)                │   │
│  │               │                                                      │   │
│  │               │  [✓ Yes - Fully implemented]                         │   │
│  │               │  [~ Partial - Partially implemented]                  │   │
│  │               │  [✗ No - Not implemented]                            │   │
│  │               │  [- N/A - Not applicable]                            │   │
│  │               │                                                      │   │
│  │               │  Notes (optional):                                   │   │
│  │               │  [________________________]                          │   │
│  │               │                                                      │   │
│  │               │  Shortcuts: Y=Yes N=No P=Partial ?=N/A | ←/→=Navigate│   │
│  │               │                                                      │   │
│  └───────────────┴──────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘

═══════════════════════════════════════════════════════════════════════════════
 SCREEN 5: FINDINGS (Security Issues)
═══════════════════════════════════════════════════════════════════════════════

┌─ 🔍 AUDIT FINDINGS ─────────────────────────────────────────────────────────┐
│                                                                             │
│  📊 Statistics: 5 Total | 🔴 1 Critical | 🟠 1 High | 🟡 2 Medium | 🟢 1 Low│
│                                                                             │
│  [All Findings ▼] [🔄 Refresh (R)] [◀ Back (Esc)]                           │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────────┐│
│  │ 🔴 CRITICAL                                                             ││
│  │ Outdated firewall firmware                                              ││
│  │ Firewall is running firmware version with 3 known CVE vulnerabilities   ││
│  │ Article 21(2)(a)                    [🔧 How to Fix] [✓ Mark Resolved]  ││
│  └─────────────────────────────────────────────────────────────────────────┘│
│  ┌─────────────────────────────────────────────────────────────────────────┐│
│  │ 🟠 HIGH                                                                 ││
│  │ Missing MFA on admin accounts                                           ││
│  │ Administrative accounts do not have multi-factor authentication         ││
│  │ Article 21(2)(c)                    [🔧 How to Fix] [✓ Mark Resolved]  ││
│  └─────────────────────────────────────────────────────────────────────────┘│
│                                                                             │
│  💡 Tip: Resolving all critical and high findings is essential              │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘

═══════════════════════════════════════════════════════════════════════════════
 KEYBOARD SHORTCUTS (Press ? anywhere to see this)
═══════════════════════════════════════════════════════════════════════════════

  Global Shortcuts:
    F1          Show help for current screen
    ?           Show this keyboard shortcuts overlay
    Esc         Go back / Cancel / Close
    Tab         Next field
    Shift+Tab   Previous field

  Dashboard:
    N           New audit session
    R           Refresh
    ↑/↓         Navigate sessions

  Checklist:
    Y/N/P/?     Answer Yes/No/Partial/N/A
    →/Space     Next question
    ←           Previous question
    S           Skip question
    H           Toggle help
    Ctrl+S      Save progress

═══════════════════════════════════════════════════════════════════════════════
"""

print(DEMO)
