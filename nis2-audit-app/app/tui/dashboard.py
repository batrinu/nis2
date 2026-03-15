"""
Rich TUI Dashboard for the NIS2 Field Audit App.
Provides an interactive interface for managing audit sessions.
RomEnglish localization: Technical terms in English, actions in Romanian.
"""
from typing import Optional

from rich.console import Console
from rich.layout import Layout
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.live import Live
from rich import box

from ..storage.db import AuditStorage
from ..models import AuditSession, SessionSummary
from ..i18n import get_text as _


console = Console()


class Dashboard:
    """Interactive dashboard for NIS2 Field Audit App."""
    
    def __init__(self, db_path: str = "./audit_sessions.db"):
        self.storage = AuditStorage(db_path)
        self.selected_session: Optional[str] = None
        self.sessions: list[SessionSummary] = []
        self.current_view = "sessions"  # sessions, session_detail, help
    
    def refresh_sessions(self) -> None:
        """Refresh the sessions list."""
        self.sessions = self.storage.list_sessions(limit=50)
    
    def make_layout(self) -> Layout:
        """Create the dashboard layout."""
        layout = Layout(name="root")
        
        layout.split(
            Layout(name="header", size=3),
            Layout(name="main", ratio=1),
            Layout(name="footer", size=3),
        )
        
        layout["main"].split_row(
            Layout(name="sidebar", size=40),
            Layout(name="content", ratio=1),
        )
        
        return layout
    
    def render_header(self) -> Panel:
        """Render the header panel."""
        grid = Table.grid(expand=True)
        grid.add_column(justify="left")
        grid.add_column(justify="center", ratio=1)
        grid.add_column(justify="right")
        grid.add_row(
            "[bold blue]🇪🇺 NIS2 Field Audit[/bold blue]",
            "[bold]v0.1.0 MVP[/bold]",
            f"[dim]Apasă ? pentru {_('help')}[/dim]",
        )
        return Panel(grid, style="blue")
    
    def render_footer(self) -> Panel:
        """Render the footer panel."""
        shortcuts = [
            ("n", _("scan")),
            ("r", _("refresh")),
            ("Enter", f"Deschide {_('audit')}"),
            ("d", _("delete")),
            ("q", _("quit")),
        ]
        
        text = Text("  ")
        for key, desc in shortcuts:
            text.append(f"[{key}]", style="bold cyan")
            text.append(f" {desc}  ", style="dim")
        
        return Panel(text, style="dim")
    
    def render_sidebar(self) -> Panel:
        """Render the sidebar with session list."""
        table = Table(
            title=f"{_('audit')} Sessions",
            box=box.SIMPLE,
            show_header=True,
            expand=True,
        )
        table.add_column("ID", style="cyan", width=12)
        table.add_column(_("name").title(), style="green")
        table.add_column(_("status").title(), style="blue", width=10)
        
        if not self.sessions:
            table.add_row("-", f"Niciun {_('audit').lower()}", "-")
        else:
            for i, s in enumerate(self.sessions[:20]):  # Show max 20
                session_id_short = s.session_id.split("-")[-1][:8]
                if len(s.entity_name) > 20:
                    entity_short = s.entity_name[:20] + "..."
                else:
                    entity_short = s.entity_name
                
                # Highlight selected
                style = "reverse" if s.session_id == self.selected_session else ""
                
                table.add_row(
                    session_id_short,
                    entity_short,
                    s.status[:10],
                    style=style,
                )
        
        return Panel(table, border_style="blue")
    
    def render_content(self) -> Panel:
        """Render the main content area."""
        if self.current_view == "help":
            return self.render_help()
        
        if not self.selected_session:
            return self.render_welcome()
        
        session = self.storage.get_session(self.selected_session)
        if not session:
            return Panel("[red]Session not found[/red]")
        
        return self.render_session_detail(session)
    
    def render_welcome(self) -> Panel:
        """Render the welcome screen."""
        content = f"""
[bold blue]{_('welcome').title()} la NIS2 Field Audit App[/bold blue]

Acest tool te ajută să rulezi audit-uri NIS2 on-site:

1. [bold]Creează sesiune nouă[/bold] - Începe auditul unei entități
2. [bold]Clasifică entitatea[/bold] - Determină status EE/IE
3. [bold]{_('scan').title()} {_('network').lower()}[/bold] - Descoperă {_('devices').lower()}
4. [bold]Interoghează {_('devices').lower()}[/bold] - {_('ssh')} la {_('routers').lower()}, {_('switches').lower()}, {_('firewalls').lower()}
5. [bold]Rulează assessment[/bold] - Parcurge checklist NIS2 Article 21
6. [bold]Generează {_('report').lower()}[/bold] - Exportă constatările

[dim]Apasă 'n' pentru a crea o sesiune nouă sau selectează una existentă din sidebar.[/dim]
        """
        return Panel(content, title="Getting Started", border_style="green")
    
    def render_session_detail(self, session: AuditSession) -> Panel:
        """Render detailed view of a session."""
        # Classification badge
        if session.classification:
            classification = session.classification.classification
        else:
            classification = "Unknown"
        badge_color = {
            "Essential Entity": "red",
            "Important Entity": "yellow",
            "Non-Qualifying": "green",
        }.get(classification, "white")
        
        content = Table.grid(padding=1)
        content.add_column(style="bold", width=15)
        content.add_column()
        
        content.add_row("Entitate:", session.entity_input.legal_name)
        content.add_row("Sector:", session.entity_input.sector)
        content.add_row("Clasificare:", f"[{badge_color}]{classification}[/{badge_color}]")
        content.add_row(f"{_('status').title()}:", session.status)
        content.add_row("Locație:", session.audit_location or "Nesetată")
        content.add_row(f"{_('network').title()}:", session.network_segment or "Nesetat")
        
        content.add_row("", "")  # Spacer
        
        content.add_row(f"{_('devices').title()}:", str(session.device_count))
        content.add_row("Constatări:", str(session.finding_count))
        if session.compliance_score:
            content.add_row(f"{_('compliance').title()}:", f"{session.compliance_score:.1f}%")
        
        content.add_row("", "")  # Spacer
        
        content.add_row("Creat:", session.created_at.strftime("%Y-%m-%d %H:%M"))
        if session.started_at:
            content.add_row(_("started").title() + ":", session.started_at.strftime("%Y-%m-%d %H:%M"))
        
        # Progress indicator
        progress_steps = [
            ("created", f"✓ {_('audit')} Creat"),
            ("entity_classified", "✓ Entitate Clasificată"),
            ("network_scanned", f"✓ {_('network')} Scanat"),
            ("devices_interrogated", f"✓ {_('devices')} Interogate"),
            ("checklist_completed", "✓ Checklist Completat"),
            ("gap_analysis_done", "✓ Gap Analysis"),
            ("report_generated", f"✓ {_('report')} Generat"),
        ]
        
        progress_text = Text("\nProgres:\n", style="bold")
        current_status = session.status
        reached_current = False
        
        for step_key, step_label in progress_steps:
            if step_key == current_status:
                reached_current = True
                progress_text.append(f"  → {step_label}\n", style="bold blue")
            elif not reached_current:
                progress_text.append(f"  ✓ {step_label}\n", style="dim green")
            else:
                progress_text.append(f"  ○ {step_label}\n", style="dim")
        
        return Panel(
            content,
            title=f"Session: {session.session_id[:20]}...",
            border_style="blue",
        )
    
    def render_help(self) -> Panel:
        """Render help screen."""
        help_text = f"""
[bold]Scurtături Tastatură[/bold]

Global:
  [cyan]q[/cyan] sau [cyan]Ctrl+C[/cyan]  {_('quit').title()} din aplicație
  [cyan]?[/cyan]              Toggle ecran {_('help')}
  [cyan]r[/cyan]              {_('refresh').title()} lista sesiuni

Lista Sesiuni:
  [cyan]↑/↓[/cyan] sau [cyan]j/k[/cyan]    Navighează sesiuni
  [cyan]Enter[/cyan]          Deschide sesiune selectată
  [cyan]n[/cyan]              Creează sesiune nouă
  [cyan]d[/cyan]              {_('delete').title()} sesiune selectată

Vizualizare Sesiune:
  [cyan]s[/cyan]              {_('scan').title()} {_('network').lower()} pentru {_('devices').lower()}
  [cyan]c[/cyan]              {_('connect').title()} la {_('devices').lower()} ({_('ssh')})
  [cyan]a[/cyan]              Rulează assessment checklist
  [cyan]g[/cyan]              Generează {_('report').lower()}

[dim]Apasă orice tastă pentru a închide {_('help')}.[/dim]
        """
        return Panel(help_text, title=_("help").title(), border_style="yellow")
    
    def run(self) -> None:
        """Run the dashboard."""
        self.refresh_sessions()
        
        if self.sessions:
            self.selected_session = self.sessions[0].session_id
        
        layout = self.make_layout()
        
        with Live(layout, refresh_per_second=4, screen=True) as live:
            while True:
                layout["header"].update(self.render_header())
                layout["sidebar"].update(self.render_sidebar())
                layout["content"].update(self.render_content())
                layout["footer"].update(self.render_footer())
                
                # In a real implementation, we'd handle keyboard input here
                # For the MVP, we'll just display the dashboard once
                break
        
        # For now, just print a static version
        console.print(self.render_header())
        console.print()
        
        # Show session table
        if self.sessions:
            table = Table(title=f"{_('audit')} Sessions")
            table.add_column("Session ID", style="cyan")
            table.add_column("Entitate", style="green")
            table.add_column("Sector", style="dim")
            table.add_column("Clasificare")
            table.add_column(_("status").title(), style="blue")
            table.add_column(_("devices").title())
            table.add_column("Creat")
            
            for s in self.sessions[:10]:
                classification_style = {
                    "Essential Entity": "red",
                    "Important Entity": "yellow",
                    "Non-Qualifying": "green",
                }.get(s.classification, "white")
                
                table.add_row(
                    s.session_id[:20] + "...",
                    s.entity_name[:25],
                    s.entity_sector[:15],
                    f"[{classification_style}]{s.classification or 'N/A'}[/{classification_style}]",
                    s.status,
                    str(s.device_count),
                    s.created_at.strftime("%Y-%m-%d %H:%M"),
                )
            
            console.print(table)
        else:
            console.print(f"[yellow]Niciun {_('audit').lower()} session găsit.[/yellow]")
            console.print(f"\nCreează un {_('audit').lower()} nou cu:")
            console.print("  nis2-audit new --name \"Nume Entitate\" --sector energy --employees 100 --turnover 20000000")
        
        console.print()
        console.print(self.render_footer())


def run_dashboard(db_path: str = "./audit_sessions.db", session_id: Optional[str] = None) -> None:
    """Run the dashboard."""
    dashboard = Dashboard(db_path)
    if session_id:
        dashboard.selected_session = session_id
    dashboard.run()


if __name__ == "__main__":
    run_dashboard()
