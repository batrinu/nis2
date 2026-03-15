"""
Onboarding Wizard Screen for NIS2 Field Audit Tool
Interactive, hands-on tutorial for first-time users.
"""

from textual.screen import Screen
from textual.widgets import (
    Static, Button, Label, RadioSet, RadioButton, 
    Checkbox, Input, Select, ProgressBar
)
from textual.containers import Vertical, Horizontal, Container, Grid
from textual.reactive import reactive
from textual.binding import Binding
from textual.color import Color

import asyncio

from ...user_experience import OnboardingWizard, PreferenceManager, ThemeMode
from ...i18n import get_text as _
from ..components.animations import TypingText, CounterAnimation, FadeInContainer, SparkleEffect


# Interactive tutorial steps with hands-on practice
INTERACTIVE_STEPS = [
    {
        'id': 'welcome',
        'title': '🎉 Bine ai venit la NIS2 Field Audit Tool!',
        'content': 'Acest tutorial te va ajuta să începi.\n\n'
                   'Vom exersa bazele pentru a te simți încrezător.',
        'interactive': False,
    },
    {
        'id': 'practice_nav',
        'title': '🎮 Exersează: Navigarea',
        'content': 'Folosește tasta ↓ (săgeată jos) pentru a continua.\n\n'
                   'Încearcă acum! Apasă ↓ pentru a merge la pasul următor.',
        'interactive': True,
        'key': 'down',
        'hint': 'Apasă tasta săgeată jos ↓',
    },
    {
        'id': 'practice_select',
        'title': '🖱️ Exersează: Selectarea',
        'content': 'Excelent! Acum să exersăm selectarea.\n\n'
                   'Apasă Enter sau Space pentru a selecta opțiunea de mai jos.',
        'interactive': True,
        'key': 'enter',
        'hint': 'Apasă Enter sau Space',
    },
    {
        'id': 'practice_help',
        'title': '❓ Exersează: Cum ceri Ajutor',
        'content': 'Ori de câte ori ai nevoie de ajutor, apasă F1.\n\n'
                   'Încearcă să apeși F1 acum pentru a vedea cum arată ajutorul!',
        'interactive': True,
        'key': 'f1',
        'hint': 'Apasă tasta F1',
    },
    {
        'id': 'preferences',
        'title': '⚙️ Personalizează-ți Experiența',
        'content': 'Să configurăm aplicația să funcționeze optim pentru tine.',
        'interactive': False,
    },
    {
        'id': 'first_device',
        'title': '🔐 Adaugă Primul tău Device',
        'content': 'Să adăugăm un device de exersare.\n\n'
                   'Îl poți șterge mai târziu.',
        'interactive': False,
    },
    {
        'id': 'complete',
        'title': '🎊 Ești Gata!',
        'content': 'Felicitări! Ai completat tutorialul.\n\n'
                   'Apasă "Începe" pentru a începe primul tău audit.',
        'interactive': False,
    },
]


class OnboardingScreen(Screen):
    """
    Interactive onboarding wizard for first-time users.
    Guides users through welcome, preferences, and first setup.
    """
    
    CSS = """
    #onboarding-container {
        width: 80;
        height: auto;
        border: thick $primary;
        background: $surface;
        padding: 1 2;
    }
    
    #step-title {
        text-align: center;
        text-style: bold;
        color: $primary;
        margin-bottom: 1;
    }
    
    #step-content {
        text-align: center;
        margin-bottom: 1;
    }
    
    #progress-container {
        height: auto;
        margin-bottom: 1;
    }
    
    #step-progress {
        color: $primary;
    }
    
    #step-counter {
        text-align: center;
        color: $text-muted;
        margin-top: 1;
    }
    
    #preferences-form {
        height: auto;
        margin: 1 0;
        padding: 1;
        border: solid $primary-darken-2;
    }
    
    #theme-select {
        margin-bottom: 1;
    }
    
    #accessibility-options {
        margin-top: 1;
    }
    
    #nav-buttons {
        height: auto;
        align: center middle;
        margin-top: 1;
    }
    
    #nav-buttons Button {
        margin: 0 1;
    }
    
    #skip-btn {
        color: $text-muted;
    }
    
    #welcome-icon {
        text-align: center;
        text-style: bold;
        color: $primary;
        margin-bottom: 1;
    }
    
    #interactive-area {
        margin: 1 0;
        padding: 2;
        border: double $success;
        background: $success-darken-3;
        text-align: center;
    }
    
    #interactive-hint {
        text-align: center;
        color: $warning;
        text-style: bold;
        margin-top: 1;
        padding: 1;
        border: solid $warning-darken-2;
        background: $warning-darken-3;
    }
    
    #success-message {
        text-align: center;
        color: $success;
        text-style: bold;
        margin-top: 1;
    }
    
    #practice-option {
        margin: 1 0;
        padding: 1;
        border: solid $primary;
        text-align: center;
    }
    
    #practice-option:focus {
        background: $primary-darken-2;
    }
    
    #confetti-art {
        text-align: center;
        color: $primary;
        margin: 1 0;
    }
    
    #tips-container {
        margin-top: 1;
        padding: 1;
        background: $primary-darken-3;
        border: solid $primary;
    }
    
    #tips-title {
        text-style: bold;
        color: $primary;
    }
    
    .tip-item {
        margin-left: 2;
    }
    
    .form-label {
        text-style: bold;
        margin-top: 1;
    }
    """
    
    BINDINGS = [
        Binding("escape", "skip", "Sari peste Tutorial"),
        Binding("right,space", "next", "Următorul"),
        Binding("left", "previous", "Înapoi"),
    ]
    
    # Reactive state
    current_step_data = reactive(None)
    selected_theme = reactive(ThemeMode.DEFAULT.value)
    font_size = reactive("medium")
    animations_enabled = reactive(True)
    show_tips = reactive(True)
    practice_completed = reactive(False)
    
    def __init__(self):
        super().__init__()
        self.wizard = OnboardingWizard()
        self.pref_manager = PreferenceManager()
        self._current_step_index = 0
        self._navigation_task = None
        self._load_step()
    
    def on_unmount(self) -> None:
        """Clean up pending tasks when screen is dismissed."""
        if self._navigation_task and not self._navigation_task.done():
            self._navigation_task.cancel()
    
    def _get_current_step(self):
        """Get current interactive step."""
        if self._current_step_index < len(INTERACTIVE_STEPS):
            return INTERACTIVE_STEPS[self._current_step_index]
        return None
    
    def _load_step(self):
        """Load current step data."""
        step = self._get_current_step()
        if step:
            # Convert to format compatible with existing code
            self.current_step_data = {
                'title': step['title'],
                'content': step['content'],
                'action': step.get('id'),
                'step_number': self._current_step_index + 1,
                'total_steps': len(INTERACTIVE_STEPS),
                'is_first': self._current_step_index == 0,
                'is_last': self._current_step_index == len(INTERACTIVE_STEPS) - 1,
            }
    
    def compose(self):
        """Build the wizard UI."""
        step = self._get_current_step()
        if not step:
            return
        
        total_steps = len(INTERACTIVE_STEPS)
        step_number = self._current_step_index + 1
        
        with Container(id="onboarding-container"):
            # Progress bar at top
            with Container(id="progress-container"):
                yield ProgressBar(
                    total=total_steps,
                    show_eta=False,
                    id="step-progress"
                )
                yield Label(
                    f"Pasul {step_number} din {total_steps}",
                    id="step-counter"
                )
            
            # Step title
            yield Label(step['title'], id="step-title")
            
            # Step content/description
            yield Label(step['content'], id="step-content")
            
            # Dynamic content based on step
            step_id = step.get('id', '')
            
            if step_id == 'welcome':
                yield Label("🔐 🖥️ 🔍 📊 📋", id="welcome-icon")
            
            elif step.get('interactive'):
                # Interactive practice step
                yield from self._build_interactive_area(step)
            
            elif step_id == 'preferences':
                yield from self._build_preferences_form()
            
            elif step_id == 'first_device':
                yield from self._build_sample_device_form()
            
            elif step_id == 'complete':
                yield from self._build_celebration()
                # Trigger sparkle effect after widget is mounted
                sparkle = SparkleEffect()
                yield sparkle
                self.call_after_refresh(sparkle.trigger)
            
            # Tips for new users (shown on later steps)
            if step_number >= 4:
                yield from self._build_tips()
            
            # Navigation buttons
            with Horizontal(id="nav-buttons"):
                if self._current_step_index > 0:
                    yield Button("← Înapoi", id="back-btn", variant="primary")
                
                yield Button("Sari peste Tutorial", id="skip-btn")
                
                if step_number == total_steps:
                    yield Button("🚀 Începe", id="next-btn", variant="success")
                elif step.get('interactive') and not self.practice_completed:
                    yield Button("Continuă →", id="next-btn", variant="primary", disabled=True)
                else:
                    yield Button("Următorul →", id="next-btn", variant="success")
    
    def _build_interactive_area(self, step: dict):
        """Build interactive practice area - yields widgets for compose()."""
        if step['id'] == 'practice_nav':
            yield Static("Zonă de exersare: Folosește săgețile pentru navigare", id="interactive-label")
        elif step['id'] == 'practice_select':
            yield Static("👆 Încearcă să selectezi această opțiune!", id="practice-option")
        elif step['id'] == 'practice_help':
            yield Static("Apasă F1 pentru a vedea panoul de ajutor", id="practice-option")
        
        # Show hint
        yield Label(f"💡 {step['hint']}", id="interactive-hint")
        
        if self.practice_completed:
            yield Label("✅ Bravo! Prinzi ideea!", id="success-message")
    
    def _build_sample_device_form(self):
        """Build sample device creation form for practice - yields widgets."""
        yield Label("🖥️ Device de Exersare", classes="form-label")
        yield Label("Acesta este un device de exersare cu care poți experimenta.")
        
        yield Label("Nume Device:", classes="form-label")
        yield Input(value="Primul meu Router", placeholder="Introdu numele device-ului")
        
        yield Label("Adresă IP:", classes="form-label")
        yield Input(value="192.168.1.1", placeholder="ex., 192.168.1.1")
        
        yield Label("Tip Device:", classes="form-label")
    
    def _build_celebration(self):
        """Build celebration screen - yields widgets."""
        # ASCII confetti
        confetti = """
    🎊  🎉  🎊  🎉  🎊  🎉  🎊
    
    🎈  Felicitări!  🎈
    
    🎊  🎉  🎊  🎉  🎊  🎉  🎊
        """
        yield Static(confetti, id="confetti-art")
        
        yield Label("Ai completat tutorialul! 🎉", id="success-message")
        yield Label("Ești gata să începi audit-ul.", id="complete-message")
    
    def _build_preferences_form(self):
        """Build the preferences form for accessibility settings - yields widgets."""
        # Theme selection
        yield Label("🎨 Alege Tema:", classes="form-label")
        
        yield RadioSet(
            RadioButton("Implicită", value=True),
            RadioButton("Contrast Ridicat"),
            RadioButton("Prietenoasă pentru daltonism (Deuteranopie)"),
            RadioButton("Prietenoasă pentru daltonism (Protanopie)"),
            RadioButton("Monocromă"),
            id="theme-select"
        )
        
        # Accessibility options
        yield Label("♿ Opțiuni de Accesibilitate:", classes="form-label")
        
        yield Checkbox("Mod text mare", id="large-text-check")
        yield Checkbox("Animații reduse", id="reduced-motion-check")
        yield Checkbox("Optimizat pentru screen reader", id="screen-reader-check")
        yield Checkbox("Afișează sfaturi de ajutor (recomandat pentru utilizatori noi)", value=True, id="show-tips-check")
    
    def _build_tips(self):
        """Build quick tips container - yields widgets."""
        yield Label("💡 Sfaturi Rapide:", id="tips-title")
        
        tips = [
            "Apasă F1 oricând pentru ajutor contextual",
            "Folosește Tab sau săgețile pentru navigare",
            "Apasă ? pentru a vedea toate scurtăturile de tastatură",
            "Munca ta se salvează automat la fiecare 5 minute",
        ]
        
        for tip in tips:
            yield Label(f"  • {tip}", classes="tip-item")
    
    def on_radio_set_changed(self, event: RadioSet.Changed) -> None:
        """Handle theme selection."""
        themes = [
            ThemeMode.DEFAULT.value,
            ThemeMode.HIGH_CONTRAST.value,
            ThemeMode.COLORBLIND_DEUTERANOPIA.value,
            ThemeMode.COLORBLIND_PROTANOPIA.value,
            ThemeMode.MONOCHROME.value,
        ]
        if event.radio_set.id == "theme-select":
            index = event.radio_set.pressed_index
            if 0 <= index < len(themes):
                self.selected_theme = themes[index]
    
    def on_checkbox_changed(self, event: Checkbox.Changed) -> None:
        """Handle checkbox changes."""
        if event.checkbox.id == "large-text-check":
            self.font_size = "large" if event.value else "medium"
        elif event.checkbox.id == "reduced-motion-check":
            self.animations_enabled = not event.value
        elif event.checkbox.id == "screen-reader-check":
            # Would integrate with screen reader support
            pass
        elif event.checkbox.id == "show-tips-check":
            self.show_tips = event.value
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        button_id = event.button.id
        
        if button_id == "next-btn":
            self._handle_next()
        elif button_id == "back-btn":
            self._handle_back()
        elif button_id == "skip-btn":
            self._handle_skip()
    
    def _handle_next(self) -> None:
        """Handle next button press."""
        step = self._get_current_step()
        
        # Save preferences if on preferences step
        if step and step.get('id') == 'preferences':
            self._save_preferences()
        
        # Advance to next step
        self._current_step_index += 1
        self.practice_completed = False
        
        if self._current_step_index >= len(INTERACTIVE_STEPS):
            # Completed all steps
            self._finish_onboarding()
        else:
            self._load_step()
            self.refresh(recompose=True)
    
    def _handle_back(self) -> None:
        """Handle back button press."""
        if self._current_step_index > 0:
            self._current_step_index -= 1
            self.practice_completed = False
            self._load_step()
            self.refresh(recompose=True)
    
    def _handle_skip(self) -> None:
        """Handle skip button press."""
        # Save default preferences
        self._save_preferences()
        self._finish_onboarding()
    
    def action_skip(self) -> None:
        """Skip tutorial action (bound to Escape key)."""
        self._handle_skip()
    
    def action_next(self) -> None:
        """Next step action (bound to Right arrow/Space)."""
        step = self._get_current_step()
        if step and step.get('interactive') and not self.practice_completed:
            self.notify(
                "Completează exercițiul de practică mai întâi!", 
                severity="warning"
            )
            return
        self._handle_next()
    
    def action_previous(self) -> None:
        """Previous step action (bound to Left arrow)."""
        self._handle_back()
    
    def on_key(self, event) -> None:
        """Handle key events for interactive practice."""
        step = self._get_current_step()
        if not step or not step.get('interactive'):
            return
        
        key = event.key
        expected_key = step.get('key', '')
        
        # Check if the pressed key matches what we're practicing
        if expected_key == 'down' and key in ('down', 'j'):
            self.practice_completed = True
            self.refresh(recompose=True)
            self.notify("✅ Perfect! Ai reușit!", severity="success")
        elif expected_key == 'enter' and key in ('enter', 'space'):
            self.practice_completed = True
            self.refresh(recompose=True)
            self.notify("✅ Excelent! Ai stăpânit selectarea!", severity="success")
        elif expected_key == 'f1' and key == 'f1':
            self.practice_completed = True
            self.refresh(recompose=True)
            self.notify("✅ Ai accesat Ajutorul! Ține minte pentru mai târziu.", severity="success")
            # Stop event propagation to prevent double handling
            event.stop()
            # Show help panel
            self.app.notify(
                "Acesta este panoul de ajutor! Apasă F1 oricând pentru a-l vedea.",
                title="❓ Ajutor",
                timeout=5
            )
    
    def _save_preferences(self) -> None:
        """Save user preferences."""
        self.pref_manager.update(
            theme=self.selected_theme,
            font_size=self.font_size,
            animations_enabled=self.animations_enabled,
            show_help_tips=self.show_tips,
        )
    
    def _finish_onboarding(self) -> None:
        """Complete onboarding and go to dashboard with celebration."""
        # Mark onboarding as complete
        self.wizard.skip()
        
        # Show completion celebration
        self.app.notify(
            "🎊 Tutorial Complet! Ești gata pentru audit!",
            title="Felicitări!",
            severity="success",
            timeout=5
        )
        
        # Small delay for the notification to be seen
        if self._navigation_task:
            self._navigation_task.cancel()
        self._navigation_task = asyncio.create_task(self._delayed_navigation())
    
    async def _delayed_navigation(self):
        """Navigate after brief delay."""
        await asyncio.sleep(0.5)
        self.app.push_screen("dashboard")
        
        # Show getting started tip
        await asyncio.sleep(1.0)
        self.app.notify(
            "💡 Sfat: Apasă 'N' pentru a crea primul tău audit, sau F1 pentru ajutor oricând!",
            title="Primii Pași",
            timeout=10
        )
