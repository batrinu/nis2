"""
Empty States - Loop 7
Friendly empty states with illustrations, explanations, and CTAs.
"""
from textual.widgets import Static, Button
from textual.containers import Vertical, Horizontal
from textual.reactive import reactive
from ...i18n import get_text as _


# ASCII art illustrations for empty states
EMPTY_STATE_ART = {
    "no_sessions": """
    ╭────────────────────────────────────╮
    │                                    │
    │     📋                             │
    │    ╱│╲    Nici o sesiune de audit        │
    │   ╱ │ ╲   gasita inca!               │
    │     │                              │
    │    ╱ ╲                             │
    │                                    │
    ╰────────────────────────────────────╯
    """,
    
    "no_devices": """
    ╭────────────────────────────────────╮
    │                                    │
    │        🔌  📱  💻                  │
    │           ╳                        │
    │     Nici un dispozitiv descoperit          │
    │                                    │
    │   Ruleaza o scanare sa gasesti dispozitive       │
    │                                    │
    ╰────────────────────────────────────╯
    """,
    
    "no_findings": """
    ╭────────────────────────────────────╮
    │                                    │
    │    🛡️                              │
    │   ╱✓╲    Nici o constatare inca!          │
    │  ╱   ╲                             │
    │ ╱     ╲   Completeaza checklist-ul   │
    │╱       ╲   sa vezi rezultatele          │
    │                                    │
    ╰────────────────────────────────────╯
    """,
    
    "no_reports": """
    ╭────────────────────────────────────╮
    │                                    │
    │    📄                              │
    │   ┌───┐    Nici un raport generat    │
    │   │   │                            │
    │   │ ✍️│    Completeaza un audit       │
    │   │   │    sa generezi rapoarte     │
    │   └───┘                            │
    │                                    │
    ╰────────────────────────────────────╯
    """,
    
    "search_empty": """
    ╭────────────────────────────────────╮
    │                                    │
    │    🔍                              │
    │   ╱  ╲    Nici un rezultat gasit         │
    │  │ ⚪ │   pentru cautarea ta          │
    │   ╲  ╱                             │
    │    ‾‾      Incearca alti termeni     │
    │                                    │
    ╰────────────────────────────────────╯
    """,
    
    "network_empty": """
    ╭────────────────────────────────────╮
    │                                    │
    │    🌐                              │
    │   ╱│╲╱│╲   Reteaua nu e scanata     │
    │  ╱ │╳│ │╲                           │
    │    │ │     Introdu un range si       │
    │    ╲ ╱     apasa Start Scan        │
    │                                    │
    ╰────────────────────────────────────╯
    """,
    
    "checklist_empty": """
    ╭────────────────────────────────────╮
    │                                    │
    │    ✅                              │
    │   ┌───┐    Totul e la zi!          │
    │   │ ✓ │                            │
    │   └───┘    Ai raspuns la toate     │
    │            intrebarile           │
    │                                    │
    ╰────────────────────────────────────╯
    """,
    
    "first_time": """
    ╭────────────────────────────────────╮
    │                                    │
    │    🎉                              │
    │   ╱✓✓╲   Bine ai venit!                  │
    │  │ ✓✓ │                            │
    │   ╲✓✓╱   Hai sa setam primul tau   │
    │    ‾‾    audit NIS2                 │
    │                                    │
    ╰────────────────────────────────────╯
    """,
}

# Explanations for why things are empty
WHY_EMPTY = {
    "no_sessions": """
Asta e complet normal! Nu ai creat inca nicio sesiune de audit.

O sesiune de audit urmareste tot lucrul pe care il faci pentru o entitate (organizatie).
Fiecare sesiune include:
• Clasificarea entitatii (Esentiala sau Importanta)
• Inventarul dispozitivelor din scanarile de retea
• Raspunsurile la checklist-ul de conformitate
• Constatarile si recomandarile
    """,
    
    "no_devices": """
Nu am scanat inca reteaua ta, asa ca nu sunt dispozitive de afisat.

Descoperirea dispozitivelor te ajuta sa:
• Construiesti un inventar exact
• Identifici dispozitive neautorizate
• Hartuiesti topologia retelei
• Verifici configuratiile dispozitivelor
    """,
    
    "no_findings": """
Nu s-au generat constatari pentru ca evaluarea conformitatii nu e completa.

Constatarile apar cand:
• Raspunzi "Nu" sau "Partial" la itemii din checklist
• Se identifica gap-uri de securitate
• Se adauga constatari manual

Asta e o veste buna - poate inseamna ca esti complet conform!
    """,
    
    "no_reports": """
Rapoartele se genereaza dupa finalizarea unui audit.

Un audit complet include:
1. Clasificarea entitatii ✓
2. Scanarea dispozitivelor din retea ✓
3. Checklist de conformitate ✓
4. Review-ul constatarilor ✓

Odata ce toate pasii sunt gata, poti genera rapoarte.
    """,
    
    "search_empty": """
Nu am gasit nimic care sa se potriveasca cu termenii tai de cautare.

Incearca:
• Sa folosesti alte cuvinte cheie
• Sa verifici typos
• Sa extinzi cautarea
• Sa folosesti potriviri partiale
    """,
    
    "network_empty": """
Sa descoperi dispozitive automat, trebuie sa scanezi reteaua.

Ce ai nevoie:
• Un range de retea (ca 192.168.1.0/24)
• Permisiune sa scanezi reteaua
• Cateva minute de rabdare

Scanarea e doar de citire si sigura de rulat.
    """,
    
    "checklist_empty": """
Treaba buna! Ai completat toate intrebarile de conformitate.

Pasii tai urmatori:
• Review-uieste constatarile
• Genereaza raportul de audit
• Programeaza evaluari de urmarire

Toate raspunsurile tale au fost salvate.
    """,
    
    "first_time": """
Bine ai venit la NIS2 Field Audit Tool!

Aplicatia asta te ajuta sa:
• Evaluezi conformitatea NIS2
• Generezi rapoarte de audit
• Urmaresti progresul remediilor

Hai sa incepem cu prima ta sesiune de audit.
    """,
}


class EmptyState(Vertical):
    """Friendly empty state with illustration and CTA."""
    
    DEFAULT_CSS = """
    EmptyState {
        width: 100%;
        height: auto;
        align: center middle;
        padding: 2;
    }
    
    #empty-art {
        text-align: center;
        color: $primary;
        height: auto;
        margin-bottom: 1;
    }
    
    #empty-title {
        text-align: center;
        text-style: bold;
        color: $text;
        margin: 1 0;
    }
    
    #empty-explanation {
        text-align: center;
        color: $text-muted;
        height: auto;
        margin: 1 0;
        max-width: 60;
    }
    
    #empty-why {
        text-align: center;
        color: $text-muted;
        text-style: italic;
        height: auto;
        margin: 1 0;
        max-width: 60;
        display: none;
    }
    
    EmptyState.show-why #empty-why {
        display: block;
    }
    
    #empty-actions {
        height: auto;
        margin-top: 2;
        align: center middle;
    }
    
    #empty-hint {
        text-align: center;
        color: $text-muted;
        text-style: italic;
        margin-top: 1;
        height: auto;
    }
    """
    
    def __init__(self, 
                 state_type: str,
                 title: str = "",
                 primary_action: str = "",
                 primary_label: str = _("Get Started"),
                 secondary_action: str = "",
                 secondary_label: str = _("Learn More"),
                 **kwargs):
        super().__init__(**kwargs)
        self.state_type = state_type
        self.title = title
        self.primary_action = primary_action
        self.primary_label = primary_label
        self.secondary_action = secondary_action
        self.secondary_label = secondary_label
    
    def compose(self):
        # ASCII art illustration
        art = EMPTY_STATE_ART.get(self.state_type, "")
        yield Static(art, id="empty-art")
        
        # Title
        display_title = self.title or self._get_default_title()
        yield Static(display_title, id="empty-title")
        
        # Explanation
        explanation = WHY_EMPTY.get(self.state_type, "")
        yield Static(explanation.strip(), id="empty-explanation")
        
        # Why empty (collapsible)
        yield Static(_("🤔 Why am I seeing this?") + "\n" + self._get_why_explanation(), 
                     id="empty-why")
        
        # Action buttons
        with Horizontal(id="empty-actions"):
            if self.primary_action:
                yield Button(self.primary_label, 
                           variant="primary",
                           id="btn-primary")
            if self.secondary_action:
                yield Button(self.secondary_label,
                           variant="default",
                           id="btn-secondary")
        
        # Helpful hint
        yield Static(self._get_hint(), id="empty-hint")
    
    def _get_default_title(self) -> str:
        """Get default title for state type."""
        titles = {
            "no_sessions": _("No Audit Sessions"),
            "no_devices": _("No Devices Found"),
            "no_findings": _("No Findings Yet"),
            "no_reports": _("No Reports"),
            "search_empty": _("No Results"),
            "network_empty": _("Ready to Scan"),
            "checklist_empty": _("All Complete!"),
            "first_time": _("Welcome!"),
        }
        return titles.get(self.state_type, _("Nothing Here"))
    
    def _get_why_explanation(self) -> str:
        """Get why explanation for state type."""
        return WHY_EMPTY.get(self.state_type, "").strip()
    
    def _get_hint(self) -> str:
        """Get helpful hint for state type."""
        hints = {
            "no_sessions": _("💡 Tip: Press 'N' to create a new session quickly"),
            "no_devices": _("💡 Tip: Start with a small network range first"),
            "no_findings": _("💡 Tip: Complete the checklist to generate findings"),
            "no_reports": _("💡 Tip: Reports are auto-generated from your data"),
            "search_empty": _("💡 Tip: Try using partial words"),
            "network_empty": _("💡 Tip: 192.168.1.0/24 is a common home network"),
            "checklist_empty": _("💡 Tip: Your work has been auto-saved"),
            "first_time": _("💡 Tip: Press '?' anytime for help"),
        }
        return hints.get(self.state_type, "")
    
    def on_button_pressed(self, event):
        """Handle button presses."""
        if event.button.id == "btn-primary":
            self.post_message(self.PrimaryAction())
        elif event.button.id == "btn-secondary":
            self.toggle_class("show-why")
    
    class PrimaryAction:
        """Message sent when primary action button is pressed."""
        pass


class QuickStartCard(Vertical):
    """Quick start guide for new users."""
    
    DEFAULT_CSS = """
    QuickStartCard {
        height: auto;
        border: solid $primary;
        background: $surface-darken-1;
        padding: 2;
        margin: 1;
    }
    
    #quickstart-title {
        text-style: bold;
        color: $primary;
        text-align: center;
        margin-bottom: 1;
        border-bottom: solid $primary;
        padding-bottom: 1;
    }
    
    .quickstart-step {
        height: auto;
        margin: 1 0;
        padding: 1;
        border-left: solid $success;
        background: $surface;
    }
    
    .quickstart-step.completed {
        border-left-color: $success;
        opacity: 0.7;
    }
    
    .quickstart-step.current {
        border-left-color: $warning;
        border-left: thick $warning;
    }
    
    .step-number {
        width: 3;
        color: $primary;
        text-style: bold;
    }
    
    .step-text {
        color: $text;
    }
    
    #quickstart-action {
        margin-top: 2;
        align: center middle;
    }
    """
    
    current_step = reactive(0)
    
    STEPS = [
        ("1", _("Create an audit session"), _("Set up your entity information")),
        ("2", _("Scan your network"), _("Discover devices automatically")),
        ("3", _("Complete checklist"), _("Answer compliance questions")),
        ("4", _("Review findings"), _("See security gaps identified")),
        ("5", _("Generate report"), _("Export your compliance report")),
    ]
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    
    def compose(self):
        yield Static(_("🚀 Quick Start Guide"), id="quickstart-title")
        
        for i, (num, title, desc) in enumerate(self.STEPS):
            classes = "quickstart-step"
            if i < self.current_step:
                classes += " completed"
            elif i == self.current_step:
                classes += " current"
            
            with Horizontal(classes=classes):
                yield Static(f"{num}.", classes="step-number")
                yield Static(f"{title}\n[dim]{desc}[/]", classes="step-text")
        
        if self.current_step < len(self.STEPS):
            yield Button(_("Start Step ") + self.STEPS[self.current_step][0],
                        variant="primary",
                        id="quickstart-action")
        else:
            yield Button(_("🎉 All Complete!"),
                        variant="success",
                        id="quickstart-action")
    
    def watch_current_step(self, step: int):
        """Recompose when step changes."""
        self.refresh()


class EmptyStateWithArt(Vertical):
    """Empty state with animated ASCII art."""
    
    DEFAULT_CSS = """
    EmptyStateWithArt {
        align: center middle;
        padding: 2;
    }
    
    #animated-art {
        text-align: center;
        color: $primary;
        height: auto;
    }
    """
    
    def __init__(self, art_frames: list, **kwargs):
        super().__init__(**kwargs)
        self.art_frames = art_frames
        self._frame = 0
    
    def compose(self):
        yield Static(self.art_frames[0], id="animated-art")
    
    def on_mount(self):
        """Start animation."""
        if len(self.art_frames) > 1:
            self.set_interval(0.5, self._animate)
    
    def _animate(self):
        """Animate frames."""
        self._frame = (self._frame + 1) % len(self.art_frames)
        try:
            self.query_one("#animated-art", Static).update(self.art_frames[self._frame])
        except Exception:
            pass


# Animation frames for different empty states
SCANNING_EMPTY_FRAMES = [
    """
    🔍
    ╱│╲
     │
    ╱ ╲
    """,
    """
     🔍
    ╱│╲
     │
    ╱ ╲
    """,
    """
      🔍
    ╱│╲
     │
    ╱ ╲
    """,
    """
     🔍
    ╱│╲
     │
    ╱ ╲
    """,
]
