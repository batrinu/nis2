"""
Help & Support System
Contextual help, glossary, and walkthrough mode for the NIS2 Audit Tool.
"""
from textual.screen import ModalScreen
from textual.widgets import Static, Button, Input, Label
from textual.containers import Vertical, Horizontal, ScrollableContainer
from textual.reactive import reactive
from textual.binding import Binding
from ...i18n import get_text as _


# NIS2 Glossary terms
NIS2_GLOSSARY = {
    "essential entity": {
        "short": _("Organizatii mari in sectoare critice"),
        "full": _("Entitati Esentiale (EE) sunt organizatii mari care opereaza in sectoare critice precum energie, transport, banci si sanatate. Acestea se confrunta cu cele mai stricte cerinte NIS2."),
    },
    "important entity": {
        "short": _("Organizatii mari in sectoare importante"), 
        "full": _("Entitati Importante (IE) sunt organizatii mari in sectoare precum infrastructura digitala, productia alimentara si manufactura. Au cerinte usor mai usoare decat Entitatile Esentiale."),
    },
    "article 21": {
        "short": _("Cerinte de baza cybersecurity"),
        "full": _("Articolul 21 din NIS2 enumera 10 masuri de cybersecurity de baza pe care toate entitatile in-scop trebuie sa le implementeze, inclusiv managementul riscurilor, raspunsul la incidente si encryptia."),
    },
    "incident reporting": {
        "short": _("Cerinte de raportare 24h/72h"),
        "full": _("NIS2 cere ca incidentele semnificative sa fie raportate in 24 ore (alerta initiala) si 72 ore (raport complet) catre CSIRT national sau autoritatea competenta."),
    },
    "compliance": {
        "short": _("Indeplinirea cerintelor NIS2"),
        "full": _("Compliance inseamna implementarea tuturor masurilor de cybersecurity necesare, mentinerea documentatiei si capacitatea de a demonstra conformitatea cu cerintele NIS2 in timpul auditurilor."),
    },
    "risk management": {
        "short": _("Identificarea si mitigarea riscurilor"),
        "full": _("Managementul riscurilor implica identificarea riscurilor de cybersecurity, evaluarea impactului acestora si implementarea de controale adecvate pentru reducerea riscurilor la niveluri acceptabile."),
    },
    "mfa": {
        "short": _("Autentificare multi-factor"),
        "full": _("Autentificarea multi-factor (MFA) cere utilizatorilor sa furnizeze doi sau mai multi factori de verificare pentru acces. NIS2 impune MFA pentru toate conturile administrative."),
    },
    "encryption": {
        "short": _("Protectia datelor prin encryptie"),
        "full": _("Encryptia protejeaza datele convertindu-le intr-un format ilizibil. NIS2 cere encryptie pentru datele sensibile atat in tranzit cat si in repaus."),
    },
}

# Contextual help for screens
SCREEN_HELP = {
    "dashboard": {
        "title": _("Ajutor Dashboard"),
        "content": _("""
Dashboard-ul este baza ta pentru managementul auditurilor NIS2.

ACTIUNI RAPIDE:
• N - Creaza sesiune audit noua
• S - Scaneaza reteaua
• D - Vezi dispozitivele descoperite
• R - Vezi rapoarte
• F - Vezi constatarile

INCEPE:
1. Creaza prima ta sesiune de audit
2. Scaneaza reteaua pentru a descoperi dispozitive
3. Completeaza lista de verificare compliance
4. Revizuiesc constatarile si genereaza rapoarte

Sfat: Apasa ? oricand pentru a vedea shortcut-urile de tastatura!
        """).strip(),
    },
    "new_session": {
        "title": _("Ajutor Sesiune Noua"),
        "content": _("""
Creaza o sesiune de audit noua pentru o entitate.

CAMPURI OBLIGATORII:
• Nume Entitate - Organizatia auditata
• Sector - Sectorul industrial (determina clasificarea NIS2)
• Numar Angajati - Folosit pentru clasificarea dimensiunii

CAMPURI OPTIONALE:
• Cifra Anuala de Afaceri - Informatii suplimentare despre dimensiune
• Nume Auditor - Cine efectueaza auditul
• Segment Retea - Pentru scanare automata

CLASIFICARE NIS2:
Bazata pe sector si dimensiune, entitatile sunt clasificate ca:
• Entitate Esentiala (EE) - Sectoare critice, org mari
• Entitate Importanta (IE) - Alte sectoare, org mari
• Non-qualifying - Organizatii mici

Munca ta se salveaza automat la fiecare 30 secunde!
        """).strip(),
    },
    "scan": {
        "title": _("Ajutor Scanare Retea"),
        "content": _("""
Scaneaza reteaua pentru a descoperi dispozitive.

CUM SA SCANEZI:
1. Introdu un range de retea (ex: 192.168.1.0/24)
2. Click Start Scan sau apasa S
3. Urmareste aparitia dispozitivelor in timp real
4. Revizuieste dispozitivele descoperite

FORMATE RANGE RETEA:
• 192.168.1.0/24 - Notatie CIDR standard
• 192.168.1.0/255.255.255.0 - Format Netmask
• 192.168.1.1-254 - Format Range

CE CAUTAM:
• Routere si firewall-uri
• Switches
• Servere
• Workstation-uri
• Dispozitive IoT

SFATURI:
• Incepe cu un range mic pentru test
• Asigura-te ca ai permisiunea de a scana
• Unele dispozitive pot sa nu raspunda la ping
        """).strip(),
    },
    "checklist": {
        "title": _("Ajutor Lista Verificare Compliance"),
        "content": _("""
Completeaza evaluarea de compliance NIS2.

OPTIUNI DE RASPUNS:
• Yes - Complet implementat
• Partial - Partial implementat
• No - Nu este implementat
• N/A - Nu se aplica acestei entitati

SHORTCUT-URI TASTATURA:
• Y - Raspunde Yes
• N - Raspunde No
• P - Raspunde Partial
• ? - Raspunde N/A
• → sau Space - Intrebarea urmatoare
• ← - Intrebarea anterioara
• S - Sari peste intrebare
• H - Toggle ajutor pentru aceasta intrebare

SCOR LIVE:
Urmareste cum se actualizeaza scorul tau de compliance pe masura ce raspunzi!

SALVARE AUTO:
Progresul tau se salveaza automat la fiecare 60 secunde.
        """).strip(),
    },
    "findings": {
        "title": _("Ajutor Constatari"),
        "content": _("""
Revizuieste si gestioneaza constatarile auditului.

NIVELE DE SEVERITATE:
• 🔴 Critical - Actiune imediata necesara
• 🟠 High - Rezolva in 30 zile
• 🟡 Medium - Rezolva in 90 zile
• 🟢 Low - Rezolva cand resursele permit

ACTIUNI:
• Click \"How to Fix\" pentru guidance detaliat
• Click \"Mark Resolved\" cand este rezolvat
• Foloseste filtre pentru a te concentra pe severitati specifice

SHORTCUT-URI TASTATURA:
• 1 - Arata doar Critical
• 2 - Arata doar High
• 3 - Arata Toate
• R - Reimprospateaza constatarile

Sfat: Rezolvarea tuturor constatarilor critical si high este esentiala pentru compliance!
        """).strip(),
    },
    "report": {
        "title": _("Ajutor Generare Raport"),
        "content": _("""
Genereaza si exporteaza rapoarte de audit.

FORMATE:
• Markdown - Bun pentru editat si sharing
• HTML - Pentru vizualizare web
• JSON - Pentru integrare cu alte tool-uri
• PDF - Pentru submissions oficiale

TEMPLATE-URI:
• Standard - Detalii tehnice complete
• Executive Summary - Overview de nivel inalt
• Technical Detail - Deep dive pentru echipe IT

PREVIEW:
Vezi un preview al raportului inainte de export!

DUPA GENERARE:
• Click \"Open Folder\" pentru a gasi raportul
• Share cu stakeholder-ii
• Pastreaza pentru audit trail
        """).strip(),
    },
}


class HelpModal(ModalScreen):
    """Modal help screen with contextual content."""
    
    CSS = """
    #help-modal {
        width: 70;
        height: auto;
        max-height: 45;
        border: thick $primary;
        background: $surface;
        padding: 1 2;
    }
    
    #help-title {
        text-align: center;
        text-style: bold;
        color: $primary;
        margin-bottom: 1;
        border-bottom: solid $primary;
    }
    
    #help-content {
        height: 1fr;
        overflow: auto;
        padding: 1 0;
    }
    
    #help-search {
        margin: 1 0;
        height: auto;
    }
    
    #help-footer {
        margin-top: 1;
        align: center middle;
        border-top: solid $surface-lighten-1;
        padding-top: 1;
    }
    
    .help-section {
        margin: 1 0;
        height: auto;
    }
    
    .help-heading {
        text-style: bold underline;
        color: $success;
        margin: 1 0;
    }
    """
    
    BINDINGS = [
        Binding("escape", "dismiss", "Close"),
        Binding("q", "dismiss", "Close"),
    ]
    
    def __init__(self, screen_name: str = "dashboard"):
        super().__init__()
        self.screen_name = screen_name
    
    def compose(self):
        help_data = SCREEN_HELP.get(self.screen_name, SCREEN_HELP["dashboard"])
        
        with Vertical(id="help-modal"):
            yield Static(f"❓ {help_data['title']}", id="help-title")
            
            with Horizontal(id="help-search"):
                yield Input(placeholder=_("Cauta ajutor..."), id="search-input")
                yield Button(_("🔍 Cauta"), id="btn-search")
            
            with ScrollableContainer(id="help-content"):
                for line in help_data['content'].split('\n'):
                    if line.strip().endswith(':'):
                        yield Static(line, classes="help-heading")
                    elif line.strip():
                        yield Static(line, classes="help-section")
            
            with Horizontal(id="help-footer"):
                yield Button(_("📚 Glosar Complet"), id="btn-glossary")
                yield Button(_("🎓 Tutorial"), id="btn-tutorial")
                yield Button(_("✓ Inchide (Esc)"), variant="primary", id="btn-close")
    
    def on_button_pressed(self, event):
        if event.button.id == "btn-close":
            self.dismiss()
        elif event.button.id == "btn-glossary":
            self.dismiss("glossary")
        elif event.button.id == "btn-tutorial":
            self.dismiss("tutorial")


class GlossaryModal(ModalScreen):
    """Modal showing NIS2 glossary terms."""
    
    CSS = """
    #glossary-modal {
        width: 70;
        height: auto;
        max-height: 45;
        border: thick $primary;
        background: $surface;
        padding: 1 2;
    }
    
    #glossary-title {
        text-align: center;
        text-style: bold;
        color: $primary;
        margin-bottom: 1;
        border-bottom: solid $primary;
    }
    
    #glossary-content {
        height: 1fr;
        overflow: auto;
    }
    
    .glossary-term {
        text-style: bold;
        color: $success;
        margin-top: 1;
    }
    
    .glossary-short {
        color: $warning;
        text-style: italic;
    }
    
    .glossary-full {
        color: $text;
        margin-bottom: 1;
    }
    """
    
    BINDINGS = [
        Binding("escape", "dismiss", "Close"),
    ]
    
    def compose(self):
        with Vertical(id="glossary-modal"):
            yield Static(_("📚 Glosar NIS2"), id="glossary-title")
            
            with ScrollableContainer(id="glossary-content"):
                for term, info in sorted(NIS2_GLOSSARY.items()):
                    yield Static(f"▶ {term.upper()}", classes="glossary-term")
                    yield Static(f"  {info['short']}", classes="glossary-short")
                    yield Static(f"  {info['full']}", classes="glossary-full")
            
            with Horizontal():
                yield Button(_("✓ Inchide"), variant="primary", id="btn-close")
    
    def on_button_pressed(self, event):
        if event.button.id == "btn-close":
            self.dismiss()


class WalkthroughOverlay(ModalScreen):
    """Interactive walkthrough tutorial overlay."""
    
    CSS = """
    #walkthrough-modal {
        width: 60;
        height: auto;
        border: thick $warning;
        background: $surface;
        padding: 1 2;
    }
    
    #walkthrough-title {
        text-align: center;
        text-style: bold;
        color: $warning;
        margin-bottom: 1;
        border-bottom: solid $warning;
    }
    
    #walkthrough-step {
        text-align: center;
        color: $text-muted;
        margin-bottom: 1;
    }
    
    #walkthrough-content {
        margin: 1 0;
        height: auto;
    }
    
    #walkthrough-progress {
        margin: 1 0;
    }
    
    #walkthrough-actions {
        margin-top: 1;
        align: center middle;
    }
    """
    
    step = reactive(0)
    
    STEPS = [
        {
            "title": _("👋 Bine ai venit!"),
            "content": _("Acest tutorial te va invata cum sa completezi primul tau audit NIS2. Apasa Next pentru a continua!"),
        },
        {
            "title": _("📝 Pasul 1: Creaza o Sesiune"),
            "content": _("Incepe prin a crea o sesiune de audit noua. Introdu detaliile organizatiei tale si lasa aplicatia sa clasifice tipul de entitate."),
        },
        {
            "title": _("🔍 Pasul 2: Scaneaza Reteaua"),
            "content": _("Scaneaza reteaua pentru a descoperi dispozitive. Aplicatia va identifica automat routere, switch-uri si servere."),
        },
        {
            "title": _("✅ Pasul 3: Completeaza Lista"),
            "content": _("Raspunde la intrebarile de compliance onest. Foloseste tastele Y/N/P/? pentru raspunsuri rapide. Urmareste cum se actualizeaza scorul live!"),
        },
        {
            "title": _("🔧 Pasul 4: Revizuieste Constatarile"),
            "content": _("Revizuieste constatarile de securitate si urmeaza guidance-ul 'How to Fix' pentru a le rezolva."),
        },
        {
            "title": _("📄 Pasul 5: Genereaza Raportul"),
            "content": _("Genereaza raportul de compliance si share-uiește-l cu stakeholder-ii. Gata! 🎉"),
        },
    ]
    
    def compose(self):
        step_data = self.STEPS[self.step]
        
        with Vertical(id="walkthrough-modal"):
            yield Static(step_data["title"], id="walkthrough-title")
            yield Static(_("Pasul {step} din {total}").format(step=self.step + 1, total=len(self.STEPS)), id="walkthrough-step")
            yield Static(step_data["content"], id="walkthrough-content")
            
            # Progress bar
            progress = (self.step + 1) / len(self.STEPS) * 100
            bar = "█" * int(progress / 5) + "░" * (20 - int(progress / 5))
            yield Static(f"[{bar}] {progress:.0f}%", id="walkthrough-progress")
            
            with Horizontal(id="walkthrough-actions"):
                if self.step > 0:
                    yield Button(_("◀ Inapoi"), id="btn-prev")
                yield Button(_("Next ▶") if self.step < len(self.STEPS) - 1 else _("✓ Termina"), variant="success", id="btn-next")
                yield Button(_("Sari peste"), id="btn-skip")
    
    def watch_step(self, step):
        """Recompose when step changes."""
        self.compose()
    
    def on_button_pressed(self, event):
        if event.button.id == "btn-next":
            if self.step < len(self.STEPS) - 1:
                self.step += 1
            else:
                self.dismiss()
        elif event.button.id == "btn-prev":
            if self.step > 0:
                self.step -= 1
        elif event.button.id == "btn-skip":
            self.dismiss()


def get_glossary_tooltip(term: str) -> str:
    """Get tooltip text for a glossary term."""
    term_lower = term.lower()
    if term_lower in NIS2_GLOSSARY:
        return NIS2_GLOSSARY[term_lower]["short"]
    return ""


def format_help_text(text: str) -> str:
    """Format help text with proper styling."""
    lines = text.split('\n')
    formatted = []
    
    for line in lines:
        line = line.strip()
        if line.endswith(':'):
            formatted.append(f"[bold underline]{line}[/bold underline]")
        elif line.startswith('•') or line.startswith('-'):
            formatted.append(f"  {line}")
        elif line.startswith('TIP:'):
            formatted.append(f"[italic yellow]{line}[/italic yellow]")
        else:
            formatted.append(line)
    
    return '\n'.join(formatted)
