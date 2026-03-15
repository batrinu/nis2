"""Main dashboard cu NIS2 guidance îmbunătățit și aesthetic retro."""
import os
from textual.screen import Screen
from textual.widgets import DataTable, Static, Button, Footer
from textual.containers import Horizontal, Vertical, Grid
from textual.reactive import reactive
from ...storage.db import AuditStorage
from ...utils import get_db_path
from ...models import SessionSummary
from ...startup_checks import is_first_run
from ...i18n import get_text as _
from ..ascii_art import HEADER_MINIMAL
from ..components.error_prevention import ConfirmationDialog, DELETE_SESSION_CONSEQUENCES
import logging

logger = logging.getLogger(__name__)


# ASCII art for empty state
EMPTY_STATE_ART = """
    ╔═══════════════════════════════════════╗
    ║                                       ║
    ║   🔐  📊  🖥️  🔍  📋                  ║
    ║                                       ║
    ║      Niciun Audit Session Încă        ║
    ║                                       ║
    ╚═══════════════════════════════════════╝
"""


class Dashboard(Screen):
    """
    Dashboard principal afișând sessions și navigation.
    Design cu aesthetic de computing universitar românesc din anii '80.
    """
    
    DEFAULT_CSS = """
    #dashboard-container {
        layout: grid;
        grid-size: 2;
        grid-columns: 25 1fr;
        grid-gutter: 1;
        padding: 1;
        height: 100%;
        background: #0c0c00;
    }
    
    #sidebar {
        width: 100%;
        height: 100%;
        border: solid #4a4a00;
        background: #141400;
        padding: 1;
    }
    
    #main-content {
        width: 100%;
        height: 100%;
        border: solid #4a4a00;
        background: #141400;
        padding: 1;
    }
    
    #welcome-panel {
        height: auto;
        border: solid #4a4a00;
        background: #0c0c00;
        padding: 1;
        margin-bottom: 1;
    }
    
    #first-run-banner {
        height: auto;
        border: double #00ff41;
        background: #0c3c0c;
        padding: 1;
        margin-bottom: 1;
    }
    
    #first-run-banner .banner-title {
        text-align: center;
        text-style: bold;
        color: #00ff41;
    }
    
    #first-run-banner .banner-content {
        text-align: center;
        color: #b8ffb8;
    }
    
    #empty-state {
        height: 1fr;
        border: solid #4a4a00;
        background: #0c0c00;
        padding: 2;
        align: center middle;
    }
    
    #empty-state-title {
        text-align: center;
        text-style: bold;
        color: #ffb000;
        margin-bottom: 1;
    }
    
    #empty-state-art {
        text-align: center;
        color: #4a4a00;
        margin-bottom: 1;
    }
    
    #empty-state-message {
        text-align: center;
        color: #b8b000;
        margin-bottom: 1;
    }
    
    #empty-state-button {
        width: auto;
        margin-top: 1;
    }
    
    #status-bar {
        height: auto;
        border: solid #4a4a00;
        background: #0c1c0c;
        padding: 0 1;
        margin-top: 1;
    }
    
    #status-text {
        color: #00ff41;
    }
    
    #auto-save-indicator {
        color: #888866;
        text-style: italic;
    }
    
    #session-table {
        height: 1fr;
        margin-bottom: 1;
    }
    
    #help-hint {
        text-align: center;
        color: #666600;
        text-style: italic;
        margin-top: 1;
    }
    
    .sidebar-title {
        text-align: center;
        text-style: bold underline;
        color: #ffff00;
        margin-bottom: 1;
    }
    
    .stats-box {
        border: solid #4a4a00;
        background: #0c0c00;
        padding: 1;
        margin-top: 1;
    }
    
    .button-row {
        height: auto;
        margin-top: 1;
        align: center middle;
    }
    
    .quick-action-card {
        border: solid #4a4a00;
        background: #141400;
        padding: 1;
        margin: 0 1;
        text-align: center;
    }
    
    .quick-action-card:hover {
        background: #1a1a00;
        border: solid #6a6a00;
    }
    """
    
    BINDINGS = [
        ("n", "new_session", "Audit Nou"),
        ("r", "refresh", "Reîmprospătează"),
        ("h", "help", "Ajutor [F1]"),
        ("q", "quit", "Ieșire"),
        ("?", "shortcuts", "Shortcuts"),
    ]
    
    sessions = reactive(list)
    selected_session = reactive(None)
    show_help = reactive(False)
    
    def __init__(self, db_path: str = None):
        super().__init__()
        self.storage = AuditStorage(db_path or get_db_path())
        # Check if this is the first run (for welcome banner)
        config_dir = os.path.expanduser("~/.nis2-audit")
        self._is_first_run = is_first_run(config_dir)
    
    def compose(self):
        """Construiește dashboard UI layout.
        
        Creează un grid layout cu sidebar (quick actions, stats) și
        main content (welcome panel, session table, status bar).
        """
        # Retro header
        yield Static(HEADER_MINIMAL, classes="header")
        
        with Grid(id="dashboard-container"):
            # Sidebar with actions and stats
            with Vertical(id="sidebar"):
                yield Static(_("[b]🚀 ACȚIUNI RAPIDE[/b]"), classes="sidebar-title")
                yield Button(_("🆕 Audit Session Nou"), id="btn-new", variant="primary")
                yield Button(_("🔄 Reîmprospătează"), id="btn-refresh")
                yield Button(_("❓ Ajutor [F1]"), id="btn-help")
                yield Button(_("❌ Ieșire"), id="btn-quit", variant="error")
                
                # Statistics box
                with Vertical(classes="stats-box"):
                    yield Static(_("[b]📊 STATISTICI[/b]"), classes="sidebar-title")
                    yield Static(_("Se încarcă..."), id="stats-content")
            
            # Main content area
            with Vertical(id="main-content"):
                # First-run welcome banner (only shown for new users)
                if self._is_first_run:
                    with Vertical(id="first-run-banner"):
                        yield Static(_("🎉 Bine ai venit la NIS2 Field Audit Tool!"), classes="banner-title")
                        yield Static(
                            _("Apasă 'N' pentru a crea primul tău audit, sau F1 pentru ajutor."),
                            classes="banner-content"
                        )
                
                # Welcome panel with guidance
                with Vertical(id="welcome-panel"):
                    yield Static(_("[b]👋 Bine ai venit la NIS2 Field Audit Tool![/b]"))
                    yield Static(_("""
Acest tool te ajută să evaluezi compliance cu Directiva NIS2.

PAȘII AUDIT:
1. Creează un session și clasifică organizația ta
2. Scanează network-ul pentru a descoperi device-uri
3. Conectează-te la device-uri pentru a colecta evidence
4. Completează NIS2 compliance checklist
5. Generează un report cu findings și remediation

💡 Sfat: Apasă F1 oricând pentru ajutor!
                    """).strip(), classes="help-text")
                
                # Session table (only shown when there are sessions)
                yield Static(_("[b]📋 AUDIT SESSIONS RECENTE[/b]"), classes="section-title")
                
                # Container that will show either table or empty state
                with Vertical(id="sessions-container"):
                    table = DataTable(id="session-table")
                    table.cursor_type = "row"
                    table.add_columns("ID", "ENTITY", "SECTOR", "STATUS", "CLASIFICARE", "DEVICE-URI")
                    yield table
                    
                    # Empty state (shown when no sessions)
                    with Vertical(id="empty-state"):
                        yield Static(EMPTY_STATE_ART, id="empty-state-art")
                        yield Static(_("Bine ai venit! Să începem primul tău audit."), id="empty-state-title")
                        yield Static(
                            _("Un audit session te ajută să urmărești NIS2 compliance\n"
                            "pentru o organizație sau network specific."),
                            id="empty-state-message"
                        )
                        yield Button(_("✨ Creează Primul Tău Audit"), id="btn-first-audit", variant="success")
                
                # Status bar with auto-save indicator
                with Horizontal(id="status-bar"):
                    yield Static(_("🟢 Gata"), id="status-text")
                    yield Static(_("• Auto-salvat: Chiar acum"), id="auto-save-indicator")
                
                # Help hint
                yield Static(_("[F1] Ajutor | [↑↓] Navighează | [Enter] Selectează | [N] Nou | [?] Shortcuts"), id="help-hint")
        
        yield Footer()
    
    def on_mount(self):
        """Încarcă sessions la mount."""
        self.load_sessions()
    
    def load_sessions(self):
        """Încarcă sessions din database cu styling retro."""
        self.sessions = self.storage.list_sessions(limit=50)
        table = self.query_one("#session-table", DataTable)
        table.clear()
        
        # Get container widgets
        try:
            empty_state = self.query_one("#empty-state", Vertical)
            session_table = self.query_one("#session-table", DataTable)
        except Exception as error:
            logger.debug(f"Query failed for container widgets: {error}")
            empty_state = None
            session_table = None
        
        if not self.sessions:
            # Show empty state, hide table
            if empty_state:
                empty_state.styles.display = "block"
            if session_table:
                session_table.styles.display = "none"
            # Update status
            self.query_one("#status-text", Static).update(_("🟡 Nicio session - creează primul tău audit!"))
            return
        else:
            # Hide empty state, show table
            if empty_state:
                empty_state.styles.display = "none"
            if session_table:
                session_table.styles.display = "block"
        
        for session in self.sessions:
            short_id = session.session_id.split("-")[-1][:8] if "-" in session.session_id else session.session_id[:8]
            classification = session.classification or _("N/A")
            
            # Add styling based on classification
            if classification == "Essential Entity":
                classification_display = "🔴 [EE] Esențial"
            elif classification == "Important Entity":
                classification_display = "🟠 [IE] Important"
            elif classification == "Non-Qualifying":
                classification_display = "🟢 [NC] Non-Qual."
            else:
                classification_display = classification
            
            table.add_row(
                short_id,
                session.entity_name[:20] or _("—"),
                session.entity_sector[:12] or _("—"),
                session.status[:15],
                classification_display,
                str(session.device_count),
            )
        
        # Update stats
        self._update_stats()
    
    def _update_stats(self):
        """Actualizează statistics display."""
        total = len(self.sessions)
        essential = sum(1 for s in self.sessions if s.classification == "Essential Entity")
        important = sum(1 for s in self.sessions if s.classification == "Important Entity")
        non_qual = sum(1 for s in self.sessions if s.classification == "Non-Qualifying")
        
        if total == 0:
            stats_text = _("Niciun audit încă.\nCreează primul!")
        else:
            stats_text = _("""Total Audits: {total}
Essential Entities: {essential}
Important Entities: {important}
Non-Qualifying: {non_qual}""").format(total=total, essential=essential, important=important, non_qual=non_qual)
        
        self.query_one("#stats-content", Static).update(stats_text)
    
    def on_data_table_row_selected(self, event):
        """Gestionează session selection."""
        if self.sessions and event.cursor_row < len(self.sessions):
            self.selected_session = self.sessions[event.cursor_row]
    
    def on_button_pressed(self, event):
        """Gestionează button clicks."""
        button_id = event.button.id
        
        if button_id == "btn-first-audit":
            # New user creating their first audit
            self.app.push_screen("new_session")
        elif button_id == "btn-new":
            self.app.push_screen("new_session")
        elif button_id == "btn-refresh":
            self.load_sessions()
            self.notify(_("✓ Sessions reîmprospătate!"), severity="information")
        elif button_id == "btn-help":
            self._show_help()
        elif button_id == "btn-quit":
            self.app.exit()
    
    def _show_help(self):
        """Afișează contextual help dialog."""
        # Use the app's help action
        self.app.action_show_help()
    
    def action_new_session(self):
        """Acțiune: Creează audit session nou.
        
        Push-uiește new_session screen pentru a începe crearea unui audit nou.
        Bound la tasta 'n'.
        """
        self.app.push_screen("new_session")
    
    def action_refresh(self):
        """Acțiune: Reîmprospătează lista de sessions.
        
        Reîncarcă sessions din database și actualizează display-ul.
        Bound la tasta 'r'.
        """
        self.load_sessions()
        self.notify(_("Sessions reîmprospătate"), severity="information", title="Actualizare")
    
    def action_help(self):
        """Acțiune: Afișează help screen.
        
        Afișează contextual help dialog.
        Bound la tasta 'h'.
        """
        self._show_help()
    
    def action_shortcuts(self):
        """Acțiune: Afișează keyboard shortcuts.
        
        Afișează un screen cu toate keyboard shortcuts disponibile.
        Bound la tasta '?'.
        """
        self.app.action_show_shortcuts()
    
    def action_quit(self):
        """Acțiune: Ieșire din aplicație.
        
        Bound la tasta 'q'.
        """
        self.app.exit()
    
    def action_delete_session(self):
        """Acțiune: Șterge session-ul selectat.
        
        Arată confirmation dialog înainte de ștergere.
        Elimină session-ul curent selectat din database
        și reîmprospătează lista de sessions doar după confirmare.
        """
        if not self.selected_session:
            self.notify(_("Selectează un session mai întâi"), severity="warning")
            return
        
        entity_name = self.selected_session.entity_name or _("Session fără nume")
        
        dialog = ConfirmationDialog(
            title=_("Confirmare Ștergere"),
            message=_("Ești sigur că vrei să ștergi session-ul pentru:\n\n[b]'{entity}'[/b]?").format(entity=entity_name),
            consequences=[
                _("Șterge permanent acest audit session"),
                _("Elimină toate device-urile asociate"),
                _("Șterge toate răspunsurile din checklist"),
                _("Elimină toate findings și report-urile"),
                _("Această acțiune nu poate fi anulată"),
            ],
            confirm_label=_("Da, Șterge"),
            cancel_label=_("Nu, Anulează"),
            danger=True,
        )
        
        self.app.push_screen(dialog, callback=self._on_delete_confirmed)
    
    def _on_delete_confirmed(self, confirmed: bool):
        """Callback apelat după ce utilizatorul răspunde la dialog.
        
        Args:
            confirmed: True dacă utilizatorul a confirmat ștergerea
        """
        if confirmed and self.selected_session:
            session_id = self.selected_session.session_id
            entity_name = self.selected_session.entity_name or _("Session")
            
            try:
                self.storage.delete_session(session_id)
                self.selected_session = None
                self.load_sessions()
                self.notify(
                    _("✓ Session '{entity}' șters").format(entity=entity_name),
                    severity="information"
                )
            except Exception as e:
                self.notify(
                    _("✗ Eroare la ștergere: {error}").format(error=str(e)),
                    severity="error"
                )
