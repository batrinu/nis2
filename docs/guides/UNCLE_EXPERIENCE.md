# 🛡️ NIS2 Field Audit Tool - Uncle Experience Guide

> A comprehensive guide to the delightful, intuitive experience designed for non-technical users.

---

## 🎯 Design Philosophy

This application is designed for "Uncle" - a non-technical user who needs to:
- Feel confident using the tool without prior training
- Understand what's happening at every step
- Recover gracefully from mistakes
- Feel rewarded for completing tasks

---

## ✨ Key Delight Features

### 🎉 Celebrations & Rewards
- **First Audit Achievement**: Special celebration modal when completing your first audit
- **Finding Resolution**: Random encouraging messages when fixing security issues
- **Progress Tracking**: Visual progress bars and completion percentages throughout
- **Streak Counter**: Tracks daily audit activity with fire emoji animations

### 🆘 Help Everywhere
- **F1 Key**: Context-sensitive help on every screen
- **? Key**: Keyboard shortcuts overlay
- **Inline Tips**: Helpful tips during scans and form filling
- **Glossary**: NIS2 terms explained in plain English
- **Walkthrough Mode**: Step-by-step tutorial for first-time users

### 💾 Peace of Mind
- **Auto-Save**: Work is saved every 30-60 seconds automatically
- **Draft Recovery**: Form data persists even if app closes unexpectedly
- **Undo**: Most actions can be cancelled or reversed
- **Confirmation**: Destructive actions ask for confirmation

### 🎨 Visual Polish
- **Retro Aesthetic**: 1980s computing vibe with amber/green phosphor colors
- **Empty States**: Friendly illustrations instead of "No data" messages
- **Progress Indicators**: Always know what's happening and how long it will take
- **Smooth Transitions**: Screens fade and transition naturally

---

## 🚀 The Uncle Workflow

### 1. First Launch
- Warm welcome banner for new users
- Option to start tutorial walkthrough
- Dashboard shows friendly empty state with "Create First Audit" button

### 2. Creating an Audit (New Session)
- **Smart Defaults**: Network segment auto-fills to common value
- **Auto-Save**: Form data saved every 30 seconds
- **Validation**: Real-time validation with helpful error messages
- **Progress Bar**: 4-step wizard shows where you are
- **Classification Preview**: See your NIS2 classification immediately

### 3. Scanning Network
- **Live Discovery**: Devices appear in real-time as they're found
- **Fun Facts**: NIS2 tips rotate during scan
- **ASCII Network Map**: Visual topology of discovered devices
- **Cancel Anytime**: Stop button always available

### 4. Device Management
- **Device Cards**: Visual cards instead of boring tables
- **Bulk Selection**: Select multiple devices with Space key
- **Status Indicators**: Clear icons show connection status
- **Detail Modal**: Rich information on click

### 5. Compliance Checklist
- **Quick Answers**: Y/N/P/? keys for rapid responses
- **Auto-Advance**: Automatically moves to next question
- **Live Score**: See compliance percentage update as you answer
- **Section Sidebar**: See progress per section
- **Help Toggle**: Press H to understand why each question matters
- **Skip Option**: Can skip and return later

### 6. Reviewing Findings
- **Severity Cards**: Color-coded with clear icons
- **"How to Fix" Button**: Step-by-step remediation guidance
- **Celebrate Fixes**: Encouraging messages when resolving issues
- **Filter Options**: Focus on critical/high/medium findings

### 7. Generating Reports
- **Preview**: See report before exporting
- **Format Options**: Markdown, HTML, JSON, PDF
- **Template Selection**: Standard, Executive, or Technical
- **One-Click Open**: Open containing folder after generation

---

## ⌨️ Keyboard Shortcuts (Global)

| Key | Action |
|-----|--------|
| `F1` | Show help for current screen |
| `?` | Show keyboard shortcuts overlay |
| `Esc` | Go back / Cancel / Close |
| `Tab` | Next field |
| `Shift+Tab` | Previous field |
| `Enter` | Select / Confirm |
| `Space` | Toggle / Select |

### Screen-Specific Shortcuts

**Dashboard:**
- `N` - New audit session
- `R` - Refresh sessions
- `↑/↓` - Navigate sessions

**Checklist:**
- `Y` - Answer Yes
- `N` - Answer No
- `P` - Answer Partial
- `?` - Answer N/A
- `→/Space` - Next question
- `←` - Previous question
- `S` - Skip question
- `H` - Toggle help
- `Ctrl+S` - Save progress

**Findings:**
- `1` - Show Critical only
- `2` - Show High only
- `3` - Show All
- `R` - Refresh

---

## 🎨 Personalization

Access via Settings or press `Ctrl+P`:

### Themes
- **Amber Retro** (Default) - Classic phosphor terminal look
- **Calm Blue** - Easy on the eyes
- **High Contrast** - Maximum accessibility
- **Light Mode** - For bright environments

### Font Sizes
- Small, Medium (default), Large, Extra Large

### Layout Density
- Compact, Comfortable (default), Spacious

---

## 🎮 Achievements

Unlock achievements as you use the tool:

| Achievement | How to Unlock |
|-------------|---------------|
| 🎯 First Steps | Complete your first audit |
| 🔍 Scan Master | Scan 10 different networks |
| 🕵️ Device Detective | Discover 50 devices |
| 🏆 Compliance Champion | Achieve 100% compliance |
| 🔧 Finding Fixer | Resolve 10 security findings |
| 📄 Report Generator | Generate 5 reports |
| ⚔️ Week Warrior | 7-day audit streak |
| ⚡ Speed Demon | Complete audit in under 15 minutes |

---

## 🛟 Error Recovery

All errors show:
1. **What happened** in plain English
2. **Why it happened** with context
3. **How to fix it** with clear steps
4. **Try again** button where applicable

Example:
> **Couldn't Reach the Device**
> 
> The device isn't responding to connection attempts.
> 
> **Try this:**
> 1. Check that the device is powered on
> 2. Verify network cable is connected
> 3. Try pinging the device first
> 4. Check firewall rules

---

## 📊 Uncle Testing Checklist

Before considering the experience complete, verify:

- [ ] Uncle can create first audit without help
- [ ] Uncle understands all error messages
- [ ] Uncle can navigate with just keyboard
- [ ] Uncle knows how to get help (F1)
- [ ] Uncle feels confident using the app
- [ ] Uncle completes audit in under 15 minutes
- [ ] Uncle smiles when resolving a finding 🎉

---

## 🔧 Technical Details

### Auto-Save Intervals
- **New Session Form**: Every 30 seconds
- **Checklist**: Every 60 seconds
- **Draft Persistence**: Saved to `~/.nis2-audit/`

### Supported Terminals
- Works in any terminal 80x24 or larger
- Full support for tmux and screen
- SSH-friendly (no mouse required)
- Copy-paste friendly output

### Accessibility
- Full keyboard navigation
- Screen reader optimized
- High contrast mode available
- Reduced motion option

---

## 💝 Credits

Designed with ❤️ for security professionals and their non-technical colleagues.

**Built with:**
- Python 3.10+
- Textual TUI Framework
- NIS2 Directive knowledge
- Lots of user empathy

---

## 📝 Version History

**v1.0.0** - Initial Release
- All 21 loops of polish complete
- Full NIS2 compliance workflow
- Achievement system
- Responsive design
- Accessibility features

