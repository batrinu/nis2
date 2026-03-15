# NIS2 Field Audit Tool - Visual Showcase

## 🎨 Visual Design Philosophy

The NIS2 Field Audit Tool features a **retro amber/green phosphor terminal aesthetic** inspired by 1980s Romanian university computing (MECIPT era). The design evokes the golden age of computing with a distinctive academic computing feel.

### Color Palette

| Element | Color | Hex Code |
|---------|-------|----------|
| Background | Dark terminal black | `#0c0c00` |
| Primary text | Amber phosphor | `#ffb000` |
| Headers/Accents | Academic green | `#00ff41` |
| Secondary text | Muted amber | `#b8b000` |
| Borders | Dark amber | `#333300` |
| Error/Severity | Romanian gold accent | `#fcd116` |

---

## 🖥️ Screen Previews

### 1. Splash Screen (Boot Sequence)

```
╔══════════════════════════════════════════════════════════════════╗
║     ██╗  ██╗██╗███████╗██████╗     █████╗ ██╗   ██╗██████╗ ██╗████████╗    ║
║     ██║  ██║██║██╔════╝██╔══██╗   ██╔══██╗██║   ██║██╔══██╗██║╚══██╔══╝    ║
║     ███████║██║███████╗██████╔╝   ███████║██║   ██║██║  ██║██║   ██║       ║
║     ██╔══██║██║╚════██║██╔═══╝    ██╔══██║██║   ██║██║  ██║██║   ██║       ║
║     ██║  ██║██║███████║██║        ██║  ██║╚██████╔╝██████╔╝██║   ██║       ║
║     ╚═╝  ╚═╝╚═╝╚══════╝╚═╝        ╚═╝  ╚═╝ ╚═════╝ ╚═════╝ ╚═╝   ╚═╝       ║
╠══════════════════════════════════════════════════════════════════╣
║        SISTEM DE AUDIT PENTRU DIRECTIVA NIS2                    ║
║        © 2024 - Spiritul MECIPT continua...                     ║
╚══════════════════════════════════════════════════════════════════╝

    [████████████████████░░░░░░░░░░] 66%

    > INIȚIALIZARE SISTEM DE OPERARE...
    > VERIFICARE MEMORIE TAMPO...
    > CONECTARE LA BAZA DE DATE LOCALA...
    
    💡 Tip: Press F1 for help anytime
```

**Features:**
- Retro ASCII art header with "NIS2 AUDIT" block letters
- Romanian academic touches ("Sistem de Audit pentru Directiva NIS2")
- "Spiritul MECIPT continua..." (MECIPT spirit continues)
- Progress bar with amber fill
- Boot messages in Romanian computing style

---

### 2. Dashboard (Main Screen)

```
┌─ 🚀 QUICK ACTIONS ───┬─ 📋 RECENT AUDIT SESSIONS ─────────────────────────┐
│                      │                                                    │
│  🆕 New Audit        │   ╔═══════════════════════════════════════════╗    │
│  🔄 Refresh          │   ║                                           ║    │
│  ❓ Help [F1]        │   ║      Welcome! Let's start                 ║    │
│  ❌ Exit             │   ║      your first audit.                    ║    │
│                      │   ║                                           ║    │
│  📊 STATISTICS       │   ╚═══════════════════════════════════════════╝    │
│                      │                                                    │
│  📋 Total Audits: 0  │   [✨ Create Your First Audit]                     │
│                      │                                                    │
└──────────────────────┴────────────────────────────────────────────────────┘
💡 Tip: Press 'N' to create a new audit, or F1 for help
```

**Features:**
- Split-pane layout with quick actions sidebar
- Empty state with helpful call-to-action
- Keyboard shortcuts prominently displayed
- Statistics panel showing audit counts

---

### 3. New Session Wizard

```
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
```

**Features:**
- Progress bar showing current step
- Form fields with validation indicators (*)
- Dropdown selectors with hints
- Auto-save indicator
- Navigation buttons

---

### 4. Network Scanner

```
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
```

**Features:**
- Real-time scan progress with visual bar
- Live device discovery log
- Network topology visualization
- Educational tips during scanning
- Cancel functionality

---

### 5. Compliance Checklist

```
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
```

**Features:**
- Visual compliance score with progress bar
- Section navigation sidebar
- Question area with context
- Multiple choice answers with keyboard shortcuts
- Optional notes field
- Help available for each question

---

### 6. Findings (Security Issues)

```
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
```

**Features:**
- Severity-based color coding (Critical/High/Medium/Low)
- Statistics summary at top
- Filter dropdown
- Action buttons for each finding
- NIS2 Article references
- How to fix guidance

---

## ⌨️ Keyboard Shortcuts

### Global Shortcuts
| Key | Action |
|-----|--------|
| `F1` | Show help for current screen |
| `?` | Show keyboard shortcuts overlay |
| `Esc` | Go back / Cancel / Close |
| `Tab` | Next field |
| `Shift+Tab` | Previous field |

### Dashboard
| Key | Action |
|-----|--------|
| `N` | New audit session |
| `R` | Refresh |
| `↑/↓` | Navigate sessions |

### Checklist
| Key | Action |
|-----|--------|
| `Y` | Answer Yes |
| `N` | Answer No |
| `P` | Answer Partial |
| `?` | Answer N/A |
| `→/Space` | Next question |
| `←` | Previous question |
| `S` | Skip question |
| `H` | Toggle help |
| `Ctrl+S` | Save progress |

---

## 🎭 Theme Variants

The app supports multiple themes:

1. **Amber** (default) - Classic phosphor terminal
2. **Green** - Alternative phosphor look
3. **Modern** - Clean contemporary design

---

## 🏛️ Romanian Academic Touches

The design pays homage to Romanian computing history:

- **MECIPT References**: "Spiritul MECIPT continua..." 
- **Romanian Language**: Boot messages in Romanian style
- **Academic Aesthetic**: University computing lab feel
- **Historical Nods**: 1980s computing era styling

---

## 📱 Terminal-Based UI

Built with [Textual](https://textual.textualize.io/), the app provides:
- **Mouse Support**: Clickable buttons and widgets
- **Keyboard Navigation**: Full keyboard control
- **Responsive Layout**: Adapts to terminal size
- **Smooth Animations**: Progress bars and transitions
- **Rich Text**: Colors, styles, and formatting

---

## 🔧 Technical Highlights

- **TUI Framework**: Textual (Python)
- **Database**: SQLite with WAL mode
- **Security**: AES-256-GCM encryption for sensitive data
- **Scanning**: Nmap integration for network discovery
- **SSH**: Paramiko for device connections
- **Export**: Multiple formats (Markdown, JSON, DOCX)
