"""Wizard de checklist Conformitate cu divulgare progresivă și previzualizare live a scorului."""
from dataclasses import dataclass, field
from typing import Optional
from textual.screen import Screen
from textual.widgets import Button, Static, RadioSet, RadioButton, ProgressBar, TextArea, Label
from textual.containers import Horizontal, Vertical, Grid
from textual.reactive import reactive
from textual.binding import Binding
from ...storage.db import AuditStorage
from ...utils import get_db_path
from ...i18n import get_text as _
from ...audit.checklist import get_checklist_sections, ComplianceStatus
from ..components.gamification import (
    get_achievement_manager,
    CelebrationModal,
    get_celebration_message,
)
import logging

logger = logging.getLogger(__name__)


@dataclass
class ChecklistResponse:
    """Response for a checklist question."""
    question_id: str
    status: ComplianceStatus
    notes: Optional[str] = None


# Question help text - explains why we ask
QUESTION_HELP = {
    "risk_management": (
        "NIS2 necesită o abordare comprehensivă a risk management. "
        "Acest lucru ajută la identificarea dacă organizația are procese formale în loc."
    ),
    "incident_response": (
        "Incident response rapid este critic sub NIS2. Trebuie să raportați "
        "incidente semnificative în 24 de ore autorității relevante."
    ),
    "access_control": (
        "Access control puternic previne accesul neautorizat la sisteme critice. "
        "Multi-factor authentication este acum obligatoriu."
    ),
    "encryption": (
        "Encryption protejează datele în tranzit și în repaus. NIS2 în mod specific "
        "mandatează encryption pentru date sensibile."
    ),
    "backup": (
        "Backup-uri regulate asigură continuitatea afacerii. NIS2 necesită capabilități de "
        "disaster recovery și testare regulată."
    ),
    "monitoring": (
        "Monitoring continuu ajută la detectarea amenințărilor devreme. Articolul 21 NIS2 "
        "mandatează măsuri adecvate de monitoring."
    ),
}


class ChecklistScreen(Screen):
    """Checklist interactiv îmbunătățit de Conformitate cu divulgare progresivă și scorare live."""
    
    DEFAULT_CSS = """
    #checklist-container {
        padding: 1;
        height: 100%;
        background: #0c0c00;
    }
    
    #checklist-header {
        text-style: bold;
        color: #ffb000;
        margin-bottom: 1;
        border-bottom: solid #4a4a00;
        text-align: center;
    }
    
    #main-layout {
        height: 1fr;
    }
    
    #sections-sidebar {
        width: 25;
        border-right: solid #4a4a00;
        padding: 0 1;
    }
    
    #sidebar-title {
        text-style: bold;
        color: #00ff41;
        margin-bottom: 1;
    }
    
    .section-item {
        height: auto;
        padding: 1;
        margin: 1 0;
        border: solid #4a4a00;
    }
    
    .section-item.active {
        border: double #00ff41;
        background: #0c3c0c;
    }
    
    .section-item.completed {
        border: solid #00ff41;
    }
    
    .section-name {
        text-style: bold;
    }
    
    .section-progress {
        color: #888866;
        text-style: italic;
    }
    
    #question-area {
        width: 1fr;
        padding: 0 2;
    }
    
    #score-panel {
        height: auto;
        border: solid #4a4a00;
        background: #001a00;
        padding: 1;
        margin-bottom: 1;
        text-align: center;
    }
    
    #score-value {
        text-style: bold;
        color: #00ff41;
    }
    
    #score-bar {
        height: 1;
        margin-top: 1;
    }
    
    #section-title {
        text-style: bold;
        color: #00ff41;
        margin-bottom: 1;
    }
    
    #question-progress {
        color: #888866;
        text-style: italic;
        margin-bottom: 1;
    }
    
    #question-text {
        margin: 1 0;
        padding: 1;
        border: solid #4a4a00;
        background: #141400;
        color: #ffb000;
    }
    
    #question-help {
        border: solid #4a4a00;
        background: #001a00;
        color: #88ff88;
        padding: 1;
        margin: 1 0;
        height: auto;
    }
    
    #help-toggle {
        text-align: right;
        color: #8888ff;
        text-style: underline;
        margin-bottom: 1;
    }
    
    #answer-options {
        margin: 1 0;
        border: solid #4a4a00;
        padding: 1;
    }
    
    #notes-area {
        height: 4;
        margin-top: 1;
        border: solid #4a4a00;
        background: #0c0c00;
    }
    
    #keyboard-hints {
        margin: 1 0;
        text-align: center;
        color: #666644;
    }
    
    #button-row {
        margin-top: 1;
        height: auto;
    }
    
    #status-row {
        height: auto;
        margin-top: 1;
        border-top: solid #4a4a00;
        padding-top: 1;
    }
    
    #autosave-status {
        width: 1fr;
        color: #888866;
        text-style: italic;
    }
    
    #skip-option {
        text-align: right;
        color: #888866;
    }
    """
    
    BINDINGS = [
        Binding("escape", "back", "Înapoi"),
        Binding("y", "answer_yes", "Da"),
        Binding("n", "answer_no", "Nu"),
        Binding("p", "answer_partial", "Parțial"),
        Binding("question_mark", "answer_na", "N/A"),
        Binding("right,space", "next", "Următorul"),
        Binding("left", "prev", "Precedentul"),
        Binding("ctrl+s", "save_progress", "Salvează"),
        Binding("s", "skip_question", "Sari peste"),
        Binding("h", "toggle_help", "Ajutor"),
    ]
    
    current_section = reactive(0)
    current_question = reactive(0)
    responses = reactive(dict)
    show_help = reactive(False)
    
    def __init__(self, db_path: str = None, session_id: str = None):
        super().__init__()
        self.storage = AuditStorage(db_path or get_db_path())
        self.session_id = session_id
        self.sections = get_checklist_sections()
        self._autosave_timer = None
    
    def compose(self):
        with Vertical(id="checklist-container"):
            yield Static("✅ NIS2 Conformitate Assessment", id="checklist-header")
            
            with Horizontal(id="main-layout"):
                # Sidebar with sections
                with Vertical(id="sections-sidebar"):
                    yield Static("📋 Secțiuni", id="sidebar-title")
                    for i, section in enumerate(self.sections):
                        with Vertical(classes="section-item", id=f"section-{i}"):
                            yield Static(section.title, classes="section-name")
                            yield Static("0/0", classes="section-progress")
                
                # Main question area
                with Vertical(id="question-area"):
                    # Live score panel
                    with Vertical(id="score-panel"):
                        yield Static("Scor Conformitate: --", id="score-value")
                        yield ProgressBar(total=100, id="score-bar")
                    
                    yield Static("", id="section-title")
                    yield Static("", id="question-progress")
                    yield Static("", id="question-text")
                    
                    yield Static("💡 De ce întrebăm acest lucru? (Apasă H)", id="help-toggle")
                    yield Static("", id="question-help")
                    
                    with RadioSet(id="answer-options"):
                        yield RadioButton("✓ Da - Fully implemented", id="ans-yes")
                        yield RadioButton("~ Parțial - Partially implemented", id="ans-partial")
                        yield RadioButton("✗ Nu - Not implemented", id="ans-no")
                        yield RadioButton("- N/A - Not applicable", id="ans-na")
                    
                    yield Static("Note (opțional):")
                    yield TextArea(id="notes-area")
                    
                    yield Static(
                        "[dim]Scurtături: Y=Da | N=Nu | P=Parțial | ?=N/A | "
                        "S=Sari peste | H=Ajutor | ←/→=Navighează[/dim]",
                        id="keyboard-hints"
                    )
                    
                    with Horizontal(id="button-row"):
                        yield Button("◀ Precedentul", id="btn-prev", variant="primary")
                        yield Button("Următorul ▶", id="btn-next", variant="success")
                        yield Button("Sari peste", id="btn-skip", variant="primary")
                        yield Button("✓ Finalizează", id="btn-submit", variant="primary")
                        yield Button("Anulează", id="btn-cancel", variant="error")
                    
                    with Horizontal(id="status-row"):
                        yield Static("💾 Auto-save gata", id="autosave-status")
                        yield Static("Apasă S pentru a sări peste întrebare", id="skip-option")
    
    def on_mount(self):
        """Initialize and load any saved responses."""
        self._load_saved_responses()
        self._update_question()
        self._update_sections_sidebar()
        
        # Auto-save timer
        self._autosave_timer = self.set_interval(60, self._auto_save_check)
    
    def on_unmount(self):
        """Clean up timers when screen is dismissed."""
        if self._autosave_timer:
            self._autosave_timer.stop()
            self._autosave_timer = None
    
    def _load_saved_responses(self):
        """Load any previously saved responses."""
        if self.session_id:
            session = self.storage.get_session(self.session_id)
            if session and hasattr(session, 'checklist_responses'):
                saved = session.checklist_responses
                if saved:
                    self.responses = saved
                    self.notify(f"Încărcate {len(saved)} răspunsuri salvate", severity="information")
    
    def watch_current_section(self, section_idx):
        """Update sidebar when section changes."""
        self._update_sections_sidebar()
    
    def watch_responses(self, responses):
        """Update score when responses change."""
        self._update_score_display()
        self._update_sections_sidebar()
    
    def watch_show_help(self, show):
        """Toggle help visibility."""
        try:
            help_widget = self.query_one("#question-help", Static)
            toggle = self.query_one("#help-toggle", Static)
            
            if show:
                section = self.sections[self.current_section]
                question = section.questions[self.current_question]
                help_text = self._get_help_text(question.domain)
                help_widget.update(f"💡 {help_text}")
                help_widget.styles.display = "block"
                toggle.update("💡 Ascunde explicația (Apasă H)")
            else:
                help_widget.styles.display = "none"
                toggle.update("💡 De ce întrebăm acest lucru? (Apasă H)")
        except Exception as error:
            logger.debug(f"UI update failed: {error}")
    
    def _get_help_text(self, domain: str) -> str:
        """Get help text for a question domain."""
        return QUESTION_HELP.get(domain, 
            "Această întrebare ajută la evaluarea Conformității organizației cu cerințele NIS2.")
    
    def _update_sections_sidebar(self):
        """Update the sections sidebar with progress."""
        for i, section in enumerate(self.sections):
            try:
                section_widget = self.query_one(f"#section-{i}", Vertical)
                progress_widget = section_widget.query_one(".section-progress", Static)
                
                # Count answered questions in this section
                answered = 0
                for q in section.questions:
                    qid = f"{section.domain}_{q.id}"
                    if qid in self.responses:
                        answered += 1
                
                total = len(section.questions)
                progress_widget.update(f"{answered}/{total} răspunse")
                
                # Update styling
                section_widget.remove_class("active", "completed")
                if i == self.current_section:
                    section_widget.add_class("active")
                elif answered == total and total > 0:
                    section_widget.add_class("completed")
                    
            except Exception:
                pass  # Ignore sidebar update errors
    
    def _update_score_display(self):
        """Update the live compliance score."""
        try:
            score = self._calculate_current_score()
            score_widget = self.query_one("#score-value", Static)
            score_bar = self.query_one("#score-bar", ProgressBar)
            
            # Color based on score
            color = "red"
            if score >= 80:
                color = "green"
            elif score >= 50:
                color = "yellow"
            
            score_widget.update(f"Scor Conformitate: [{color}]{score:.0f}%[/{color}]")
            score_bar.update(progress=score)
        except Exception as error:
            logger.debug(f"UI update failed: {error}")
    
    def _calculate_current_score(self) -> float:
        """Calculate current compliance score."""
        if not self.responses:
            return 0.0
        
        total_questions = sum(len(s.questions) for s in self.sections)
        if total_questions == 0:
            return 0.0
        
        score = 0.0
        for response in self.responses.values():
            if response.status == ComplianceStatus.COMPLIANT:
                score += 100
            elif response.status == ComplianceStatus.PARTIALLY_COMPLIANT:
                score += 50
            elif response.status == ComplianceStatus.NOT_APPLICABLE:
                score += 100  # N/A counts as complete
        
        return score / total_questions
    
    def _update_question(self):
        """Update UI for current question."""
        section = self.sections[self.current_section]
        question = section.questions[self.current_question]
        
        # Update section title
        self.query_one("#section-title", Static).update(
            f"Secțiune: {section.title}"
        )
        
        # Update question progress
        q_num = self.current_question + 1
        q_total = len(section.questions)
        total_answered = len(self.responses)
        total_questions = sum(len(s.questions) for s in self.sections)
        
        self.query_one("#question-progress", Static).update(
            f"Întrebarea {q_num}/{q_total} în această secțiune | "
            f"Progres general: {total_answered}/{total_questions}"
        )
        
        # Update question text
        self.query_one("#question-text", Static).update(
            f"[b]Î{q_num}:[/b] {question.question}\n\n"
            f"[dim]Articolul {question.nis2_article} | Domeniu: {question.domain}[/dim]"
        )
        
        # Update help text
        self.show_help = False  # Reset help visibility
        
        # Load saved response
        question_id = f"{section.domain}_{question.id}"
        radio_set = self.query_one("#answer-options", RadioSet)
        notes_area = self.query_one("#notes-area", TextArea)
        
        # Load saved response if exists, otherwise clear
        if question_id in self.responses:
            response = self.responses[question_id]
            status_map = {
                ComplianceStatus.COMPLIANT: 0,
                ComplianceStatus.PARTIALLY_COMPLIANT: 1,
                ComplianceStatus.NON_COMPLIANT: 2,
                ComplianceStatus.NOT_APPLICABLE: 3,
            }
            if response.status in status_map:
                radio_set.pressed_index = status_map[response.status]
            else:
                radio_set.pressed_index = None
            notes_area.text = response.notes or ""
        else:
            # No saved response - clear both answer and notes
            radio_set.pressed_index = None
            notes_area.text = ""
    
    def _save_current_response(self):
        """Save response for current question."""
        section = self.sections[self.current_section]
        question = section.questions[self.current_question]
        question_id = f"{section.domain}_{question.id}"
        
        radio_set = self.query_one("#answer-options", RadioSet)
        status_map = [
            ComplianceStatus.COMPLIANT,
            ComplianceStatus.PARTIALLY_COMPLIANT,
            ComplianceStatus.NON_COMPLIANT,
            ComplianceStatus.NOT_APPLICABLE,
        ]
        
        if radio_set.pressed_index is not None:
            status = status_map[radio_set.pressed_index]
            notes = self.query_one("#notes-area", TextArea).text
            
            self.responses[question_id] = ChecklistResponse(
                question_id=question_id,
                status=status,
                notes=notes if notes else None
            )
    
    def on_button_pressed(self, event):
        """Handle button clicks."""
        btn_id = event.button.id
        
        if btn_id == "btn-prev":
            self.action_prev()
        elif btn_id == "btn-next":
            self.action_next()
        elif btn_id == "btn-skip":
            self.action_skip_question()
        elif btn_id == "btn-submit":
            self._submit_checklist()
        elif btn_id == "btn-cancel":
            self.action_back()
    
    def _save_progress(self) -> bool:
        """Save current progress to database."""
        if not self.session_id:
            return False
        
        try:
            self._save_current_response()
            score = self._calculate_current_score()
            
            self.storage.update_session_fields(
                self.session_id,
                checklist_progress=score,
                checklist_responses=self.responses
            )
            
            now = __import__('datetime').datetime.now().strftime('%H:%M')
            self._update_autosave_status(f"✓ Salvat la {now}")
            return True
        except Exception as error:
            logger.error(f"Failed to save progress: {error}")
            self._update_autosave_status("⚠ Salvare eșuată")
            return False
    
    def _update_autosave_status(self, message: str):
        """Update auto-save status display."""
        try:
            status = self.query_one("#autosave-status", Static)
            status.update(message)
        except Exception as error:
            logger.debug(f"UI update failed: {error}")
    
    def _submit_checklist(self):
        """Submit completed checklist."""
        self._save_current_response()
        
        try:
            from ...audit.scorer import ComplianceScorer
            
            scorer = ComplianceScorer()
            score = scorer.calculate_score(self.sections, self.responses)
            
            if self.session_id:
                self.storage.update_session_fields(
                    self.session_id,
                    status="checklist_completed",
                    compliance_score=score.overall_percentage
                )
            
            # Record audit completion for achievements
            am = get_achievement_manager()
            new_achievements = am.record_audit_completion()
            
            # Show celebration for first audit
            if "first_audit" in new_achievements:
                self.app.push_screen(
                    CelebrationModal("first_audit"),
                    lambda _: self._finish_submission(score.overall_percentage)
                )
            else:
                self._finish_submission(score.overall_percentage)
                
        except Exception as error:
            self.notify(f"Eroare la salvare: {error}", severity="error", title="Eroare")
    
    def _finish_submission(self, score_percentage: float):
        """Complete the submission after any celebrations."""
        self.notify(
            f"✓ {get_celebration_message()} Final score: {score_percentage:.1f}%",
            severity="success",
            title="Succes"
        )
        self.app.pop_screen()
    
    def action_answer_yes(self):
        """Quick answer: Yes."""
        try:
            self.query_one("#answer-options", RadioSet).pressed_index = 0
            self._save_current_response()
            self._auto_advance()
        except Exception as error:
            logger.debug(f"UI update failed: {error}")
    
    def action_answer_no(self):
        """Quick answer: No."""
        try:
            self.query_one("#answer-options", RadioSet).pressed_index = 2
            self._save_current_response()
            self._auto_advance()
        except Exception as error:
            logger.debug(f"UI update failed: {error}")
    
    def action_answer_partial(self):
        """Quick answer: Partial."""
        try:
            self.query_one("#answer-options", RadioSet).pressed_index = 1
            self._save_current_response()
            self._auto_advance()
        except Exception as error:
            logger.debug(f"UI update failed: {error}")
    
    def action_answer_na(self):
        """Quick answer: N/A."""
        try:
            self.query_one("#answer-options", RadioSet).pressed_index = 3
            self._save_current_response()
            self._auto_advance()
        except Exception as error:
            logger.debug(f"UI update failed: {error}")
    
    def _auto_advance(self):
        """Auto-advance to next question after answer."""
        self.set_timer(0.3, self.action_next)
    
    def action_skip_question(self):
        """Skip current question."""
        self.notify("Întrebare sărită - poți reveni la ea mai târziu", severity="information")
        self.action_next()
    
    def action_toggle_help(self):
        """Toggle help display."""
        self.show_help = not self.show_help
    
    def action_save_progress(self):
        """Manually save progress."""
        if self._save_progress():
            self.notify("Progres salvat", severity="information")
        else:
            self.notify("Nimic de salvat", severity="warning")
    
    def _auto_save_check(self):
        """Periodic auto-save check."""
        if len(self.responses) > 0:
            self._save_progress()
    
    def action_back(self):
        """Go back to dashboard."""
        self._save_progress()
        self.app.pop_screen()
    
    def action_next(self):
        """Go to next question."""
        self._save_current_response()
        section = self.sections[self.current_section]
        
        if self.current_question < len(section.questions) - 1:
            self.current_question += 1
        elif self.current_section < len(self.sections) - 1:
            self.current_section += 1
            self.current_question = 0
        else:
            # At end, ask if they want to finish
            self.notify("Ai ajuns la final. Apasă Finalizează pentru a completa.", severity="information")
            return
        
        self._update_question()
    
    def action_prev(self):
        """Go to previous question."""
        self._save_current_response()
        
        if self.current_question > 0:
            self.current_question -= 1
        elif self.current_section > 0:
            self.current_section -= 1
            self.current_question = len(self.sections[self.current_section].questions) - 1
        
        self._update_question()
