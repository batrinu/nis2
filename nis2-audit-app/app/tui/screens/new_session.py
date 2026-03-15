"""Enhanced new session wizard with NIS2 guidance and smart defaults.
RomEnglish localization: Technical terms in English, actions in Romanian.
"""
from textual.screen import Screen
from textual.widgets import Input, Select, Button, Static, ProgressBar, Label
from textual.containers import Horizontal, Vertical, Grid
from textual.reactive import reactive
from textual.binding import Binding
from ...models import EntityInput, CrossBorderInfo
from ...audit.classifier import EntityClassifier
from ...storage.db import AuditStorage
from ...utils import get_db_path
from datetime import datetime
from ..ascii_art import NIS2_GUIDANCE
from ..components.smart_form import AutoSaveForm, FormHelper
from ...i18n import get_text as _
import logging

logger = logging.getLogger(__name__)


class NewSessionWizard(Screen):
    """
    4-step wizard for creating new audit sessions.
    Enhanced with plain language NIS2 explanations, auto-save, and smart defaults.
    """
    
    # Keyboard shortcuts
    BINDINGS = [
        Binding("escape", "cancel", "Anulează"),
        Binding("ctrl+s", "save_draft", "Salvează Draft"),
        Binding("right,tab", "next_step", "Următor"),
        Binding("left", "prev_step", "Înapoi"),
    ]
    
    DEFAULT_CSS = """
    #wizard-container {
        width: 85;
        height: auto;
        border: double #ffb000;
        background: #0c0c00;
        padding: 2;
        align: center middle;
    }
    
    #wizard-title {
        text-align: center;
        text-style: bold;
        color: #ffb000;
        margin-bottom: 1;
        border-bottom: solid #4a4a00;
    }
    
    #wizard-progress {
        margin-bottom: 2;
        color: #00ff41;
    }
    
    #step-indicator {
        text-align: center;
        color: #888866;
        margin-bottom: 1;
    }
    
    #step-content {
        padding: 1;
        min-height: 15;
        border: solid #4a4a00;
        background: #141400;
    }
    
    .form-row {
        height: auto;
        margin: 1 0;
        align: left middle;
    }
    
    .form-label {
        width: 22;
        color: #b8b000;
        text-align: right;
        margin-right: 1;
    }
    
    .form-input {
        width: 1fr;
    }
    
    #autosave-row {
        height: auto;
        margin-top: 1;
        align: center middle;
    }
    
    #autosave-status {
        text-align: center;
        color: #888866;
        text-style: italic;
    }
    
    #autosave-status.saving {
        color: #ffb000;
    }
    
    #autosave-status.saved {
        color: #00ff41;
    }
    
    #autosave-status.error {
        color: #ff4444;
    }
    
    #button-row {
        height: auto;
        margin-top: 1;
        align: center middle;
    }
    
    #classification-preview {
        border: solid #00aa00;
        background: #001a00;
        color: #88ff88;
        padding: 1;
        margin: 1 0;
        height: auto;
    }
    
    #guidance-panel {
        border: solid #4a4a00;
        background: #0c0c00;
        color: #888866;
        padding: 1;
        margin-top: 1;
        height: auto;
    }
    
    .step-header {
        text-style: bold underline;
        color: #ffff00;
        margin-bottom: 1;
    }
    
    .help-text {
        color: #888866;
        text-style: italic;
        margin: 1 0;
    }
    """
    
    current_step = reactive(1)
    total_steps = 4
    
    # Form data
    entity_name = reactive("")
    sector = reactive("")
    employees = reactive(0)
    turnover = reactive(0.0)
    
    # Step 3 form data (persisted)
    auditor = reactive("")
    location = reactive("")
    network = reactive("")
    notes = reactive("")
    
    def __init__(self, db_path: str = None):
        super().__init__()
        self.storage = AuditStorage(db_path or get_db_path())
        self.classifier = EntityClassifier()
        self.classification = None
        self._autosave_timer = None
        self._has_unsaved_changes = False
    
    def on_mount(self):
        """Initialize auto-save and load draft."""
        # Set up auto-save timer (every 30 seconds)
        self._autosave_timer = self.set_interval(30, self._auto_save)
        
        # Try to load draft data
        if self._load_draft_data():
            # Populate inputs with draft data
            self._populate_inputs_from_draft()
            self.notify("Restaurat din draft", severity="information", timeout=3)
    
    def _populate_inputs_from_draft(self):
        """Populate form inputs with loaded draft data."""
        self._populate_inputs_from_reactive()
    
    def _populate_inputs_from_reactive(self):
        """Populate form inputs from reactive variables."""
        try:
            name_input = self.query_one("#input-name", Input)
            name_input.value = self.entity_name
        except Exception as error:
            logger.warning(f"Failed to populate name input: {error}")
        
        try:
            emp_input = self.query_one("#input-employees", Input)
            emp_input.value = str(self.employees) if self.employees > 0 else ""
        except Exception as error:
            logger.warning(f"Failed to populate employees input: {error}")
        
        try:
            turn_input = self.query_one("#input-turnover", Input)
            turn_input.value = str(self.turnover) if self.turnover > 0 else ""
        except Exception as error:
            logger.warning(f"Failed to populate turnover input: {error}")
        
        try:
            sector_select = self.query_one("#select-sector", Select)
            if self.sector:
                sector_select.value = self.sector
        except Exception as error:
            logger.warning(f"Failed to populate sector select: {error}")
        
        # Step 3 inputs
        # Step 3 inputs - populate from reactive variables
        try:
            auditor_input = self.query_one("#input-auditor", Input)
            auditor_input.value = self.auditor
        except Exception as error:
            logger.warning(f"Failed to populate auditor input: {error}")
        
        try:
            location_input = self.query_one("#input-location", Input)
            location_input.value = self.location
        except Exception as error:
            logger.warning(f"Failed to populate location input: {error}")
        
        try:
            network_input = self.query_one("#input-network", Input)
            network_input.value = self.network
        except Exception as error:
            logger.warning(f"Failed to populate network input: {error}")
        
        try:
            notes_input = self.query_one("#input-notes", Input)
            notes_input.value = self.notes
        except Exception as error:
            logger.warning(f"Failed to populate notes input: {error}")
    
    def on_unmount(self):
        """Clean up timers when screen is dismissed."""
        if self._autosave_timer:
            self._autosave_timer.stop()
            self._autosave_timer = None
    
    def _auto_save(self):
        """Auto-save form data periodically."""
        if self._has_unsaved_changes:
            self._save_draft_data()
            self._has_unsaved_changes = False
    
    def watch_entity_name(self, value):
        """Track changes for auto-save."""
        self._has_unsaved_changes = True
    
    def watch_sector(self, value):
        """Track changes for auto-save."""
        self._has_unsaved_changes = True
    
    def watch_employees(self, value):
        """Track changes for auto-save."""
        self._has_unsaved_changes = True
    
    def watch_turnover(self, value):
        """Track changes for auto-save."""
        self._has_unsaved_changes = True
    
    def watch_auditor(self, value):
        """Track changes for auto-save."""
        self._has_unsaved_changes = True
    
    def watch_location(self, value):
        """Track changes for auto-save."""
        self._has_unsaved_changes = True
    
    def watch_network(self, value):
        """Track changes for auto-save."""
        self._has_unsaved_changes = True
    
    def watch_notes(self, value):
        """Track changes for auto-save."""
        self._has_unsaved_changes = True
    
    def compose(self):
        """Build the new session wizard UI layout.
        
        Creates a wizard container with title, progress bar, step indicator,
        dynamic step content, auto-save status, and navigation buttons.
        """
        with Vertical(id="wizard-container"):
            yield Static(f"🆕 {_('audit').upper()} NOU", id="wizard-title")
            
            progress = ProgressBar(total=self.total_steps, id="wizard-progress")
            progress.update(progress=self.current_step)
            yield progress
            
            yield Static(f"Pasul {self.current_step} din {self.total_steps}", id="step-indicator")
            
            # Step content container
            with Vertical(id="step-content"):
                yield from self._render_step()
            
            # Auto-save status indicator
            with Horizontal(id="autosave-row"):
                yield Static("💾 Auto-save pregătit", id="autosave-status")
            
            with Horizontal(id="button-row"):
                yield Button(f"◀ {_('back').title()}", id="btn-back", variant="primary", disabled=True)
                yield Button(f"Următor ▶", id="btn-next", variant="success")
                yield Button(_("cancel").title(), id="btn-cancel", variant="error")
    
    def _render_step(self):
        """Render current step content with NIS2 guidance."""
        if self.current_step == 1:
            yield Label("[b]PASUL 1: Informații Entitate[/b]", classes="step-header")
            yield Label("Introdu informațiile de bază despre entitatea auditată.", classes="help-text")
            
            with Grid(classes="form-row"):
                yield Label("Nume Entitate:*", classes="form-label")
                yield Input(placeholder="ex: EnergieCorp SRL", id="input-name", classes="form-input")
            
            with Grid(classes="form-row"):
                yield Label("Sector:*", classes="form-label")
                yield Select([
                    ("Energy", "energy"),
                    ("Transport", "transport"),
                    ("Banking", "banking"),
                    ("Financial Services", "financial"),
                    ("Healthcare", "health"),
                    ("Drinking Water", "water"),
                    ("Wastewater", "wastewater"),
                    ("Digital Infrastructure", "digital"),
                    ("ICT Management", "ict"),
                    ("Public Administration", "public_admin"),
                    ("Food Production", "food"),
                    ("Industrial Production", "manufacturing"),
                    ("Other", "other"),
                ], id="select-sector", classes="form-input")
            
            with Grid(classes="form-row"):
                yield Label("Număr Angajați:*", classes="form-label")
                yield Input(placeholder="ex: 250", id="input-employees", classes="form-input")
            
            with Grid(classes="form-row"):
                yield Label("Cifra de Afaceri Anuală (€):", classes="form-label")
                yield Input(placeholder="ex: 50000000", id="input-turnover", classes="form-input")
            
            # Guidance panel
            with Vertical(id="guidance-panel"):
                yield Static("""[b]De ce contează aceste informații?[/b]

Directiva NIS2 clasifică entitățile bazat pe:
• Sectorul de activitate (Anexa I sau II)
• Dimensiunea economică (număr angajați, cifra de afaceri)

Entitățile mari din sectoare critice sunt "Essential Entities" (EE)
Entitățile mari din alte sectoare sunt "Important Entities" (IE)""")
        
        elif self.current_step == 2:
            yield Label("[b]PASUL 2: Clasificare NIS2[/b]", classes="step-header")
            yield Label("Sistemul a analizat datele și a determinat clasificarea.", classes="help-text")
            
            self._update_classification()
            
            if self.classification:
                classification = self.classification.classification
                
                # Get the guidance text based on classification
                if classification == "Essential Entity":
                    guidance = NIS2_GUIDANCE["essential_entity"]
                    color = "red"
                    badge = "[EE] ESSENTIAL ENTITY"
                elif classification == "Important Entity":
                    guidance = NIS2_GUIDANCE["important_entity"]
                    color = "yellow"
                    badge = "[IE] IMPORTANT ENTITY"
                else:
                    guidance = NIS2_GUIDANCE["non_qualifying"]
                    color = "green"
                    badge = "[NC] NON-QUALIFYING"
                
                # Classification badge
                yield Static(f"[b]CLASIFICARE:[/b] [{color}]{badge}[/{color}]", id="classification-preview")
                
                # Detailed explanation
                yield Static(guidance, id="guidance-panel")
                
                # Technical details
                yield Static(f"""
[b]Detalii Tehnice:[/b]
• Bază Legală: {self.classification.legal_basis}
• Anexa: {self.classification.annex or "N/A"}
• Autoritate Principală: {self.classification.lead_authority}
• Scor Încredere: {self.classification.confidence_score:.0%}
                """.strip())
            else:
                yield Static("Completează datele în Pasul 1 pentru a vedea clasificarea.", id="classification-preview")
        
        elif self.current_step == 3:
            yield Label("[b]PASUL 3: Context Audit[/b]", classes="step-header")
            yield Label("Informații suplimentare pentru această sesiune de audit.", classes="help-text")
            
            with Grid(classes="form-row"):
                yield Label("Auditor:", classes="form-label")
                yield Input(placeholder="Numele tău", id="input-auditor", classes="form-input")
            
            with Grid(classes="form-row"):
                yield Label("Locație:", classes="form-label")
                yield Input(placeholder="ex: Sediu Central", id="input-location", classes="form-input")
            
            with Grid(classes="form-row"):
                yield Label(f"{_('network')} Segment:", classes="form-label")
                yield Input(placeholder="ex: 192.168.1.0/24", id="input-network", classes="form-input")
            
            with Grid(classes="form-row"):
                yield Label("Note:", classes="form-label")
                yield Input(placeholder="Note suplimentare...", id="input-notes", classes="form-input")
            
            with Vertical(id="guidance-panel"):
                yield Static(f"""[b]Tips Audit:[/b]

• {_('network')} segment ajută la scanarea automată
• Notele sunt private și nu apar în {_('report').lower()} final
• Poți modifica aceste informații mai târziu""")
        
        elif self.current_step == 4:
            yield Label("[b]PASUL 4: Rezumat & Confirmare[/b]", classes="step-header")
            yield Label("Revizuiește datele înainte de a crea sesiunea.", classes="help-text")
            
            classification_str = "Non-qualifying"
            if self.classification:
                classification_str = self.classification.classification
            
            # Get additional data from inputs
            auditor = self._get_input_value("input-auditor", "Nespecificat")
            location = self._get_input_value("input-location", "Nespecificată")
            network = self._get_input_value("input-network", "Nespecificat")
            
            summary = f"""
[b]Entitate:[/b] {self.entity_name or "[Nesetat]"}
[b]Sector:[/b] {self.sector or "[Nesetat]"}
[b]Clasificare:[/b] {classification_str}
[b]Angajați:[/b] {self.employees or "[Nesetat]"}
[b]Cifra Anuală:[/b] €{self.turnover:,.0f}
[b]Auditor:[/b] {auditor}
[b]Locație:[/b] {location}
[b]Network:[/b] {network}

[b]Ce se întâmplă după creare:[/b]
1. Poți scana {_('network').lower()}-ul pentru inventar
2. Vei evalua conformitatea NIS2
3. Vei genera {_('report').lower()}-ul de {_('audit').lower()}

Apasă [b]Creează[/b] pentru a începe {_('audit').lower()}-ul.
            """.strip()
            
            yield Static(summary, id="classification-preview")
    
    def _update_classification(self):
        """Update classification based on current form data."""
        if self.entity_name and self.sector:
            try:
                entity_input = EntityInput(
                    legal_name=self.entity_name,
                    sector=self.sector,
                    employee_count=self.employees,
                    annual_turnover_eur=self.turnover,
                    cross_border_operations=CrossBorderInfo(
                        operates_cross_border=False,
                        main_establishment="RO"
                    )
                )
                self.classification = self.classifier.classify(entity_input)
            except Exception as error:
                logger.warning(f"Classification update failed: {error}")
    
    def watch_current_step(self, step):
        """Update UI when step changes."""
        try:
            self.query_one("#step-indicator", Static).update(f"Pasul {step} din {self.total_steps}")
            self.query_one("#wizard-progress", ProgressBar).update(progress=step)
            
            back_btn = self.query_one("#btn-back", Button)
            next_btn = self.query_one("#btn-next", Button)
            
            back_btn.disabled = step == 1
            
            if step == self.total_steps:
                next_btn.label = "✓ Creează"
            else:
                next_btn.label = "Următor ▶"
            
            content = self.query_one("#step-content", Vertical)
            content.remove_children()
            content.mount_all(list(self._render_step()))
            
            # Populate inputs from reactive variables after re-rendering
            self._populate_inputs_from_reactive()
            
            # Apply smart defaults for step 3
            if step == 3:
                self._apply_smart_defaults()
                
        except Exception as error:
            logger.warning(f"UI update failed in watch_current_step: {error}")
    
    def on_input_changed(self, event):
        """Update form data when inputs change."""
        input_id = event.input.id
        value = event.value
        
        if input_id == "input-name":
            self.entity_name = value
        elif input_id == "input-employees":
            try:
                self.employees = int(value) if value else 0
            except ValueError:
                pass  # Keep default value
        elif input_id == "input-turnover":
            try:
                self.turnover = float(value) if value else 0.0
            except ValueError:
                pass
        # Step 3 inputs - track changes
        elif input_id == "input-auditor":
            self.auditor = value
        elif input_id == "input-location":
            self.location = value
        elif input_id == "input-network":
            self.network = value
        elif input_id == "input-notes":
            self.notes = value
    
    def on_select_changed(self, event):
        """Handle select changes."""
        if event.select.id == "select-sector":
            self.sector = event.value or ""
    
    def on_button_pressed(self, event):
        """Handle button clicks."""
        button_id = event.button.id
        
        if button_id == "btn-cancel":
            self.app.pop_screen()
        
        elif button_id == "btn-back":
            if self.current_step > 1:
                self.current_step -= 1
        
        elif button_id == "btn-next":
            if self.current_step < self.total_steps:
                # Validate step 1 before proceeding
                if self.current_step == 1:
                    if not self._validate_step_1():
                        return
                self.current_step += 1
            else:
                self._create_session()
    
    def _validate_step_1(self) -> bool:
        """Validate step 1 form data before proceeding.
        
        Returns:
            True if valid, False otherwise
        """
        errors = []
        
        if not self.entity_name or not self.entity_name.strip():
            errors.append("Numele entității este obligatoriu")
        
        if not self.sector:
            errors.append("Sectorul este obligatoriu")
        
        if self.employees <= 0:
            errors.append("Numărul de angajați trebuie să fie mai mare decât 0")
        
        if errors:
            for error in errors:
                self.notify(error, severity="error", title="Eroare Validare")
            return False
        
        return True
    
    def _get_input_value(self, input_id: str, default: str = "") -> str:
        """Safely get input value."""
        try:
            return self.query_one(f"#{input_id}", Input).value or default
        except Exception as error:
            logger.debug(f"Failed to get input value for #{input_id}: {error}")
            return default
    
    def _apply_smart_defaults(self):
        """Apply smart default values based on context."""
        try:
            # Set current date/time context for defaults
            context = {
                'current_user': '',
                'default_location': '',
            }
            
            # Network segment smart default - only if not already set
            network_input = self.query_one("#input-network", Input)
            if not network_input.value and not self.network:
                network_input.value = "192.168.1.0/24"
                self.network = "192.168.1.0/24"
                
        except Exception as error:
            logger.warning(f"Failed to apply smart defaults: {error}")
    
    def _create_session(self):
        """Create the audit session."""
        errors = []
        if not self.entity_name or not self.entity_name.strip():
            errors.append("Numele entității este obligatoriu")
        if not self.sector:
            errors.append("Sectorul este obligatoriu")
        if self.employees <= 0:
            errors.append("Numărul de angajați trebuie să fie mai mare decât 0")
        
        if errors:
            for error in errors:
                self.notify(error, severity="error", title="Eroare Validare")
            # Go back to step 1 if validation fails
            if self.current_step != 1:
                self.current_step = 1
            return
        
        if not self.classification:
            self._update_classification()
        
        # Get additional inputs
        auditor = self._get_input_value("input-auditor")
        location = self._get_input_value("input-location")
        network = self._get_input_value("input-network")
        notes = self._get_input_value("input-notes")
        
        # Validate network format if provided
        if network:
            is_valid, msg = FormHelper.validate_ip_range(network)
            if not is_valid:
                self.notify(f"Format {_('network').lower()}: {msg}", severity="warning")
        
        # Create session
        from ...models import AuditSession
        session = AuditSession(
            session_id=f"AUDIT-{datetime.now().timestamp()}",
            entity_input=self.classifier._last_input if hasattr(self.classifier, '_last_input') else None,
            classification=self.classification,
            status="entity_classified",
            auditor_name=auditor,
            audit_location=location,
            network_segment=network,
            notes=notes
        )
        
        self.storage.create_session(session)
        
        # Clear any saved draft
        self._clear_draft()
        
        self.notify(f"✓ {_('audit')} creat cu succes!", severity="success", title="Succes")
        self.app.pop_screen()
        
        # Refresh dashboard
        try:
            dashboard = self.app.get_screen("dashboard")
            if hasattr(dashboard, 'load_sessions'):
                dashboard.load_sessions()
        except Exception as error:
            logger.warning(f"Failed to refresh dashboard: {error}")
    
    def _save_draft_data(self):
        """Save current form data as draft."""
        try:
            import json
            import os
            
            draft_data = {
                'entity_name': self.entity_name,
                'sector': self.sector,
                'employees': self.employees,
                'turnover': self.turnover,
                'current_step': self.current_step,
            }
            
            # Add additional fields from step 3 (from reactive variables)
            draft_data['auditor'] = self.auditor
            draft_data['location'] = self.location
            draft_data['network'] = self.network
            draft_data['notes'] = self.notes
            
            config_dir = os.path.expanduser("~/.nis2-audit")
            os.makedirs(config_dir, exist_ok=True)
            draft_path = os.path.join(config_dir, "new_session_draft.json")
            
            with open(draft_path, 'w') as f:
                json.dump(draft_data, f, indent=2)
                
            self._update_autosave_status("✓ Draft salvat", "saved")
            
        except Exception as error:
            logger.warning(f"Failed to save draft data: {error}")
    
    def _load_draft_data(self) -> bool:
        """Load saved draft data if exists."""
        try:
            import json
            import os
            
            config_dir = os.path.expanduser("~/.nis2-audit")
            draft_path = os.path.join(config_dir, "new_session_draft.json")
            
            if not os.path.exists(draft_path):
                return False
            
            with open(draft_path, 'r') as f:
                draft = json.load(f)
            
            self.entity_name = draft.get('entity_name', '')
            self.sector = draft.get('sector', '')
            self.employees = draft.get('employees', 0)
            self.turnover = draft.get('turnover', 0.0)
            self.auditor = draft.get('auditor', '')
            self.location = draft.get('location', '')
            self.network = draft.get('network', '')
            self.notes = draft.get('notes', '')
            
            return True
            
        except Exception as error:
            logger.warning(f"Failed to load draft data: {error}")
            return False
    
    def _clear_draft(self):
        """Clear saved draft after successful submission."""
        try:
            import os
            config_dir = os.path.expanduser("~/.nis2-audit")
            draft_path = os.path.join(config_dir, "new_session_draft.json")
            if os.path.exists(draft_path):
                os.remove(draft_path)
        except Exception as error:
            logger.debug(f"Failed to clear draft: {error}")
    
    def _update_autosave_status(self, message: str, style: str = ""):
        """Update the auto-save status label."""
        try:
            status = self.query_one("#autosave-status", Static)
            status.update(message)
            status.remove_class("saving", "saved", "error")
            if style:
                status.add_class(style)
        except Exception as error:
            logger.debug(f"Failed to update autosave status: {error}")
    
    # Action handlers
    def action_cancel(self):
        """Action: Cancel wizard and return to dashboard.
        
        Saves current form data as draft before exiting.
        Bound to 'escape' key.
        """
        self._save_draft_data()  # Save before canceling
        self.app.pop_screen()
    
    def action_save_draft(self):
        """Action: Manually save form draft.
        
        Saves current form data to disk for later recovery.
        Bound to 'ctrl+s' key.
        """
        self._save_draft_data()
        self.notify("Draft salvat", severity="information")
    
    def action_next_step(self):
        """Action: Go to next step or create session.
        
        Advances to the next wizard step, or creates the session
        if already on the final step.
        Bound to 'right' and 'tab' keys.
        """
        if self.current_step < self.total_steps:
            self.current_step += 1
        else:
            self._create_session()
    
    def action_prev_step(self):
        """Action: Go to previous step.
        
        Returns to the previous wizard step if not on the first step.
        Bound to 'left' key.
        """
        if self.current_step > 1:
            self.current_step -= 1
