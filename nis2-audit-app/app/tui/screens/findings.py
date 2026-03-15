"""Enhanced findings review screen with cards and actionable guidance."""
from datetime import datetime, timezone
from textual.screen import Screen, ModalScreen
from textual.widgets import Button, Static, Select, Label
from textual.containers import Horizontal, Vertical
from textual.reactive import reactive
from textual.binding import Binding
from ...storage.db import AuditStorage
from ...models.finding import AuditFinding
from ...utils import get_db_path
from ...i18n import get_text as _
import logging

logger = logging.getLogger(__name__)


# Severity configurations
SEVERITY_CONFIG = {
    "critical": {"emoji": "🔴", "color": "#ff4444", "label": "CRITIC"},
    "high": {"emoji": "🟠", "color": "#ff8800", "label": "RIDICAT"},
    "medium": {"emoji": "🟡", "color": "#ffcc00", "label": "MEDIU"},
    "low": {"emoji": "🟢", "color": "#00ff41", "label": "SCĂZUT"},
    "info": {"emoji": "⚪", "color": "#888888", "label": "INFO"},
}


class FixGuidanceModal(ModalScreen):
    """Modal showing detailed fix guidance for a finding."""
    
    CSS = """
    #fix-modal {
        width: 70;
        height: auto;
        max-height: 45;
        border: thick $primary;
        background: $surface;
        padding: 1 2;
    }
    
    #fix-title {
        text-align: center;
        text-style: bold;
        color: $primary;
        margin-bottom: 1;
        border-bottom: solid $primary;
    }
    
    #fix-severity {
        text-align: center;
        margin-bottom: 1;
    }
    
    #fix-description {
        border: solid $surface-lighten-1;
        background: $surface-darken-1;
        padding: 1;
        margin: 1 0;
    }
    
    #fix-steps {
        border: solid $success;
        background: $success-darken-3;
        padding: 1;
        margin: 1 0;
    }
    
    .step-item {
        margin: 1 0;
        height: auto;
    }
    
    #fix-actions {
        margin-top: 2;
        align: center middle;
    }
    """
    
    def __init__(self, finding):
        super().__init__()
        self.finding = finding
    
    def compose(self):
        with Vertical(id="fix-modal"):
            yield Static("🔧 Cum să Repari", id="fix-title")
            
            severity = self.finding.get("severity", "info")
            config = SEVERITY_CONFIG.get(severity, SEVERITY_CONFIG["info"])
            
            yield Static(
                f"{config['emoji']} {self.finding.get('title', 'Fără titlu')}",
                id="fix-severity"
            )
            
            yield Static(
                f"[b]Descriere:[/b]\n{self.finding.get('description', 'Fără descriere')}",
                id="fix-description"
            )
            
            with Vertical(id="fix-steps"):
                yield Static("[b]✓ Pași Recomandați pentru Remediere:[/b]")
                
                # Generate steps from recommendation
                recommendation = self.finding.get('recommendation', 'Nicio recomandare specifică')
                steps = self._parse_steps(recommendation)
                
                for i, step in enumerate(steps, 1):
                    yield Static(f"{i}. {step}", classes="step-item")
            
            with Horizontal(id="fix-actions"):
                yield Button("✓ Marchează Rezolvat", variant="success", id="btn-resolve")
                yield Button("Închide", variant="primary", id="btn-close")
    
    def _parse_steps(self, recommendation: str) -> list:
        """Parse recommendation into steps."""
        # Try to split by sentences or numbered items
        steps = []
        for line in recommendation.split('\n'):
            line = line.strip()
            if line and not line.startswith('#'):
                # Remove common prefixes
                for prefix in ['1.', '2.', '3.', '4.', '5.', '-', '•', '*']:
                    if line.startswith(prefix):
                        line = line[len(prefix):].strip()
                if line:
                    steps.append(line)
        
        if not steps:
            steps = [recommendation]
        
        return steps[:5]  # Limit to 5 steps
    
    def on_button_pressed(self, event):
        if event.button.id == "btn-close":
            self.dismiss()
        elif event.button.id == "btn-resolve":
            self.dismiss("resolve")


class FindingsScreen(Screen):
    """Enhanced audit findings review with cards and actionable guidance."""
    
    DEFAULT_CSS = """
    #findings-container {
        padding: 1;
        height: 100%;
    }
    
    #findings-header {
        text-style: bold;
        color: $primary;
        margin-bottom: 1;
        text-align: center;
    }
    
    #stats-row {
        height: auto;
        margin-bottom: 1;
    }
    
    .stat-box {
        width: 1fr;
        height: auto;
        border: solid $surface-lighten-1;
        padding: 1;
        text-align: center;
        margin: 0 1;
    }
    
    .stat-number {
        text-style: bold;
        text-align: center;
    }
    
    .stat-label {
        color: $text-muted;
        text-align: center;
    }
    
    #filter-row {
        height: auto;
        margin-bottom: 1;
        align: center middle;
    }
    
    #findings-scroll {
        height: 1fr;
        overflow: auto;
    }
    
    .finding-card {
        height: auto;
        border: solid $surface-lighten-1;
        background: $surface-darken-1;
        padding: 1;
        margin: 1 0;
    }
    
    .finding-card.resolved {
        border: solid $success;
        opacity: 0.7;
    }
    
    .finding-header {
        height: auto;
        margin-bottom: 1;
    }
    
    .finding-severity {
        width: 15;
        text-style: bold;
    }
    
    .finding-title {
        width: 1fr;
        text-style: bold;
    }
    
    .finding-article {
        width: 20;
        color: $text-muted;
        text-align: right;
    }
    
    .finding-summary {
        color: $text-muted;
        height: auto;
        margin: 1 0;
    }
    
    .finding-actions {
        height: auto;
        margin-top: 1;
    }
    
    #empty-state {
        text-align: center;
        color: $text-muted;
        margin-top: 4;
    }
    
    #empty-state-title {
        text-style: bold;
        color: $success;
        margin-bottom: 1;
    }
    """
    
    BINDINGS = [
        Binding("escape", "back", "Înapoi"),
        Binding("r", "refresh", "Reîmprospătează"),
        Binding("f", "filter", "Filtrează"),
        Binding("1", "filter_critical", "Doar Critice"),
        Binding("2", "filter_high", "Doar Ridicate"),
        Binding("3", "filter_all", "Arată Toate"),
    ]
    
    findings = reactive(list)
    selected_finding = reactive(None)
    filter_severity = reactive(None)
    resolved_findings = reactive(set)
    
    def __init__(self, db_path: str = None, session_id: str = None):
        super().__init__()
        self.storage = AuditStorage(db_path or get_db_path())
        self.session_id = session_id
    
    def compose(self):
        with Vertical(id="findings-container"):
            yield Static("🔍 Constatări Audit", id="findings-header")
            
            # Statistics row
            with Horizontal(id="stats-row"):
                with Vertical(classes="stat-box"):
                    yield Static("0", id="stat-total", classes="stat-number")
                    yield Static("Total", classes="stat-label")
                with Vertical(classes="stat-box"):
                    yield Static("0", id="stat-critical", classes="stat-number")
                    yield Static("Critice", classes="stat-label")
                with Vertical(classes="stat-box"):
                    yield Static("0", id="stat-high", classes="stat-number")
                    yield Static("Ridicate", classes="stat-label")
                with Vertical(classes="stat-box"):
                    yield Static("0", id="stat-resolved", classes="stat-number")
                    yield Static("Rezolvate", classes="stat-label")
            
            # Filter row
            with Horizontal(id="filter-row"):
                yield Select([
                    ("Toate Constatările (3)", None),
                    ("🔴 Doar Critice", "critical"),
                    ("🟠 Doar Ridicate", "high"),
                    ("🟡 Doar Medii", "medium"),
                    ("🟢 Doar Scăzute", "low"),
                    ("⚪ Doar Info", "info"),
                ], id="filter-severity", value=None)
                yield Button("🔄 Reîmprospătează (R)", id="btn-refresh")
                yield Button("◀ Înapoi (Esc)", id="btn-back")
            
            # Findings cards container
            with Vertical(id="findings-scroll"):
                yield Static("Se încarcă constatările...", id="empty-state")
    
    def on_mount(self):
        """Load findings."""
        self.load_findings()
    
    def watch_findings(self, findings):
        """Update display when findings change."""
        self._update_stats()
        self._refresh_findings_list()
    
    def watch_filter_severity(self, severity):
        """Refresh when filter changes."""
        self._refresh_findings_list()
    
    def watch_resolved_findings(self, resolved):
        """Refresh when findings are resolved."""
        self._update_stats()
        self._refresh_findings_list()
    
    def _update_stats(self):
        """Update statistics display."""
        findings = self.findings
        
        total = len(findings)
        critical = sum(1 for f in findings if f.get("severity") == "critical")
        high = sum(1 for f in findings if f.get("severity") == "high")
        
        # Query actual resolved count from database instead of in-memory set
        resolved = 0
        try:
            if self.session_id:
                db_findings = self.storage.get_findings(self.session_id)
                resolved = sum(1 for f in db_findings if f.status == "resolved")
            else:
                # Fallback to in-memory count for mock findings
                resolved = len(self.resolved_findings)
        except Exception as error:
            logger.error(f"Failed to query resolved count from database: {error}")
            resolved = len(self.resolved_findings)
        
        try:
            self.query_one("#stat-total", Static).update(str(total))
            self.query_one("#stat-critical", Static).update(str(critical))
            self.query_one("#stat-high", Static).update(str(high))
            self.query_one("#stat-resolved", Static).update(str(resolved))
        except Exception as error:
            logger.debug(f"Stats update failed: {error}")
    
    def load_findings(self):
        """Load findings from database."""
        if self.session_id:
            self.findings = self.storage.get_findings(self.session_id)
        
        # Add mock findings if empty
        if not self.findings:
            self.findings = [
                {
                    "finding_id": "FIND-001",
                    "title": "Lipsește MFA pe conturile de admin",
                    "description": "Conturile administrative nu au autentificare multi-factor activată. Aceasta încalcă cerințele Articolului 21 NIS2 pentru controlul accesului.",
                    "severity": "high",
                    "nis2_article": "Art. 21(2)(c)",
                    "status": "open",
                    "recommendation": "1. Activează MFA pe toate conturile de admin\n2. Folosește aplicații de autentificare sau chei hardware\n3. Documentează politicile MFA\n4. Instruiește personalul despre utilizarea MFA"
                },
                {
                    "finding_id": "FIND-002",
                    "title": "Firmware firewall învechit",
                    "description": "Firewall rulează firmware versiunea 2.1.0 care are 3 vulnerabilități CVE cunoscute. Actualizare imediată necesară.",
                    "severity": "critical",
                    "nis2_article": "Art. 21(2)(a)",
                    "status": "open",
                    "recommendation": "1. Programează fereastra de mentenanță\n2. Fă backup la configurația curentă\n3. Actualizează la firmware v3.2.1\n4. Verifică regulile după actualizare"
                },
                {
                    "finding_id": "FIND-003",
                    "title": "Niciun plan de răspuns la incidente documentat",
                    "description": "Nu a fost găsit un plan formal de răspuns la incidente. NIS2 necesită proceduri documentate pentru gestionarea incidentelor de securitate.",
                    "severity": "medium",
                    "nis2_article": "Art. 21(2)(h)",
                    "status": "open",
                    "recommendation": "1. Creează echipa de răspuns la incidente\n2. Documentează procedurile de răspuns\n3. Definește căile de escaladare\n4. Programează exerciții anuale"
                },
            ]
    
    def _refresh_findings_list(self):
        """Refresh the findings cards display."""
        container = self.query_one("#findings-scroll", Vertical)
        container.remove_children()
        
        filtered = self.findings
        if self.filter_severity:
            filtered = [f for f in filtered if f.get("severity") == self.filter_severity]
        
        if not filtered:
            if self.filter_severity:
                container.mount(Static(
                    f"Nicio constatare {self.filter_severity}. Lucru bun! 🎉",
                    id="empty-state"
                ))
            else:
                container.mount(Static(
                    "🎉 Nicio constatare! Rețeaua ta este securizată.",
                    id="empty-state"
                ))
            return
        
        for finding in filtered:
            card = self._create_finding_card(finding)
            container.mount(card)
    
    def _create_finding_card(self, finding):
        """Create a finding card widget."""
        severity = finding.get("severity", "info")
        config = SEVERITY_CONFIG.get(severity, SEVERITY_CONFIG["info"])
        finding_id = finding.get("finding_id", "")
        is_resolved = finding_id in self.resolved_findings
        
        card_classes = "finding-card"
        if is_resolved:
            card_classes += " resolved"
        
        card = Vertical(classes=card_classes)
        
        # Header
        header = Horizontal(classes="finding-header")
        header.mount(Static(
            f"{config['emoji']} {config['label']}",
            classes="finding-severity"
        ))
        header.mount(Static(finding.get("title", "Fără titlu"), classes="finding-title"))
        header.mount(Static(finding.get("nis2_article", "-"), classes="finding-article"))
        card.mount(header)
        
        # Summary
        desc = finding.get("description", "")
        if len(desc) > 100:
            desc = desc[:97] + "..."
        card.mount(Static(desc, classes="finding-summary"))
        
        # Actions
        actions = Horizontal(classes="finding-actions")
        if is_resolved:
            actions.mount(Button("✓ Rezolvat", variant="success", disabled=True))
        else:
            actions.mount(Button("🔧 Cum să Repari", variant="primary", id=f"fix-{finding_id}"))
            actions.mount(Button("✓ Marchează Rezolvat", variant="success", id=f"resolve-{finding_id}"))
        card.mount(actions)
        
        return card
    
    def on_button_pressed(self, event):
        """Handle button clicks."""
        button_id = event.button.id
        
        if button_id == "btn-refresh":
            self.action_refresh()
        elif button_id == "btn-back":
            self.action_back()
        elif button_id and button_id.startswith("fix-"):
            finding_id = button_id[4:]
            self._show_fix_guidance(finding_id)
        elif button_id and button_id.startswith("resolve-"):
            finding_id = button_id[8:]
            self._resolve_finding(finding_id)
    
    def _show_fix_guidance(self, finding_id: str):
        """Show fix guidance modal."""
        finding = next((f for f in self.findings if f.get("finding_id") == finding_id), None)
        if finding:
            self.push_screen(FixGuidanceModal(finding), self._on_fix_modal_close)
    
    def _on_fix_modal_close(self, result):
        """Handle fix modal close."""
        if result == "resolve":
            # Find the finding that was just viewed
            # For now, we don't track which one was viewed
            pass
    
    def _resolve_finding(self, finding_id: str):
        """Mark a finding as resolved."""
        # Find the finding in memory
        finding_dict = next((f for f in self.findings if f.get("finding_id") == finding_id), None)
        if not finding_dict:
            self.notify("Eroare: Constatarea nu a fost găsită", severity="error")
            logger.error(f"Finding {finding_id} not found in memory")
            return
        
        try:
            # Convert dict finding to AuditFinding model
            finding = AuditFinding(
                finding_id=finding_dict.get("finding_id", ""),
                session_id=self.session_id or finding_dict.get("session_id", ""),
                title=finding_dict.get("title", ""),
                description=finding_dict.get("description", ""),
                severity=finding_dict.get("severity", "medium"),
                nis2_article=finding_dict.get("nis2_article"),
                nis2_domain=finding_dict.get("nis2_domain"),
                evidence=finding_dict.get("evidence", ""),
                device_ids=finding_dict.get("device_ids", []),
                config_snippets=finding_dict.get("config_snippets", []),
                recommendation=finding_dict.get("recommendation", ""),
                remediation_steps=finding_dict.get("remediation_steps", []),
                estimated_effort=finding_dict.get("estimated_effort"),
                status="resolved",  # Update status to resolved
                resolved_at=datetime.now(timezone.utc),  # Add resolved_at timestamp
                resolved_by=finding_dict.get("created_by", "system"),
                created_at=finding_dict.get("created_at", datetime.now(timezone.utc)),
                created_by=finding_dict.get("created_by", "system"),
            )
            
            # Update finding status in the database first
            self.storage.save_finding(finding)
            logger.info(f"Finding {finding_id} marked as resolved in database")
            
            # Only update in-memory state after successful database update
            self.resolved_findings = self.resolved_findings | {finding_id}
            
            # Record for achievements
            from ..components.gamification import get_achievement_manager
            am = get_achievement_manager()
            am.update_stat("findings_resolved")
            
            # Celebration messages based on severity
            celebration_messages = [
                "🎉 Constatare rezolvată! Rețeaua ta este mai securizată!",
                "✨ Lucru bun remediind această problemă!",
                "🛡️ Securitate îmbunătățită! Continuă așa!",
                "⭐ Încă un pas spre conformitate!",
            ]
            import random
            message = random.choice(celebration_messages)
            
            self.notify(message, severity="success", timeout=4)
            
        except Exception as error:
            logger.error(f"Failed to resolve finding {finding_id}: {error}")
            self.notify(
                "Eroare la salvarea constatării. Încercați din nou.",
                severity="error",
                timeout=5
            )
    
    def on_select_changed(self, event):
        """Handle filter change."""
        if event.select.id == "filter-severity":
            self.filter_severity = event.value
    
    def action_refresh(self):
        """Refresh findings."""
        self.load_findings()
        self.notify("✓ Constatări reîmprospătate", severity="information")
    
    def action_back(self):
        """Go back to dashboard."""
        self.app.pop_screen()
    
    def action_filter(self):
        """Focus filter control."""
        self.query_one("#filter-severity", Select).focus()
    
    def action_filter_critical(self):
        """Filter to critical only."""
        self.filter_severity = "critical"
        self.query_one("#filter-severity", Select).value = "critical"
    
    def action_filter_high(self):
        """Filter to high only."""
        self.filter_severity = "high"
        self.query_one("#filter-severity", Select).value = "high"
    
    def action_filter_all(self):
        """Show all findings."""
        self.filter_severity = None
        self.query_one("#filter-severity", Select).value = None
