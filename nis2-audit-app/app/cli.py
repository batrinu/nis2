#!/usr/bin/env python3
"""
NIS2 Field Audit App - CLI Entry Point
A Python CLI for on-site NIS2 compliance audits.
"""
import logging
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console

logger = logging.getLogger(__name__)
from rich.panel import Panel
from rich.table import Table

from .models import EntityInput, CrossBorderInfo, AuditSession, DeviceCredentials
from .audit.classifier import EntityClassifier
from .audit.checklist import get_checklist_sections, ComplianceStatus
from .audit.scorer import ComplianceScorer, format_score_report
from .audit.gap_analyzer import GapAnalyzer
from .audit.finding_generator import FindingGenerator, prioritize_findings, get_findings_summary
from .report.generator import ReportGenerator, SanctionCalculator
from .storage.db import AuditStorage
from .utils import get_db_path
from .scanner.network_scanner import NmapScanner, NetworkScannerError
from .scanner.device_fingerprint import DeviceFingerprinter
from .tui.device_table import display_device_inventory
from .connector import ConnectionManager, CommandRunner, ConfigParser

app = typer.Typer(
    name="nis2-audit",
    help="NIS2 Field Audit App - On-site compliance assessment tool",
    rich_markup_mode="rich",
)
console = Console()


def print_banner() -> None:
    """Print the application banner."""
    banner = Panel(
        "[bold blue]NIS2 Field Audit App[/bold blue]\n"
        "[dim]On-site compliance assessment for Directive (EU) 2022/2555[/dim]",
        title="🇪🇺 v0.1.0",
        border_style="blue",
    )
    console.print(banner)


@app.callback()
def main(
    db_path: Optional[str] = typer.Option(
        get_db_path(),
        "--db",
        "-d",
        help="Path to SQLite database",
    ),
) -> None:
    """NIS2 Field Audit App - Command line interface."""
    # Store db_path in context for subcommands
    typer.get_current_context().ensure_object(dict)
    typer.get_current_context().obj["db_path"] = db_path


@app.command()
def new(
    name: str = typer.Option(..., "--name", "-n", help="Entity legal name"),
    sector: str = typer.Option(..., "--sector", "-s", help="Entity sector (e.g., energy, healthcare, manufacturing)"),
    employees: int = typer.Option(..., "--employees", "-e", help="Number of employees"),
    turnover: float = typer.Option(..., "--turnover", "-t", help="Annual turnover in EUR"),
    country: str = typer.Option("DE", "--country", "-c", help="Country code (ISO-3166 alpha-2)"),
    balance: Optional[float] = typer.Option(None, "--balance", "-b", help="Balance sheet total in EUR"),
    public_admin: bool = typer.Option(False, "--public-admin", help="Is public administration body"),
    dns_provider: bool = typer.Option(False, "--dns", help="Is DNS provider"),
    tld_registry: bool = typer.Option(False, "--tld", help="Is TLD registry"),
    trust_service: bool = typer.Option(False, "--trust", help="Is trust service provider"),
    location: Optional[str] = typer.Option(None, "--location", "-l", help="Audit location"),
    network: Optional[str] = typer.Option(None, "--network", help="Network segment (e.g., 192.168.1.0/24)"),
) -> None:
    """Create a new audit session for an entity."""
    print_banner()
    
    ctx = typer.get_current_context()
    storage = AuditStorage(ctx.obj["db_path"])
    
    entity_input = EntityInput(
        legal_name=name,
        sector=sector,
        employee_count=employees,
        annual_turnover_eur=turnover,
        balance_sheet_total=balance,
        cross_border_operations=CrossBorderInfo(
            operates_cross_border=False,
            main_establishment=country,
        ),
        is_public_admin=public_admin,
        is_dns_provider=dns_provider,
        is_tld_registry=tld_registry,
        is_trust_service_provider=trust_service,
    )
    
    session = AuditSession(
        entity_input=entity_input,
        audit_location=location,
        network_segment=network,
    )
    
    classifier = EntityClassifier()
    classification = classifier.classify(entity_input)
    session.classification = classification
    session.status = "entity_classified"
    
    storage.create_session(session)
    
    console.print(f"\n[bold green]✓[/bold green] Created new audit session: [cyan]{session.session_id}[/cyan]")
    console.print(f"\n[bold]Entity:[/bold] {name}")
    console.print(f"[bold]Sector:[/bold] {sector}")
    
    if classification.classification == "Essential Entity":
        console.print(f"\n[bold red]Classification: Essential Entity[/bold red]")
    elif classification.classification == "Important Entity":
        console.print(f"\n[bold yellow]Classification: Important Entity[/bold yellow]")
    else:
        console.print(f"\n[bold green]Classification: Non-Qualifying[/bold green]")
    
    console.print(f"[dim]{classification.legal_basis}[/dim]")
    console.print(f"\n[bold]Confidence:[/bold] {classification.confidence_score:.0%}")
    
    if classification.edge_cases:
        console.print("\n[yellow]⚠ Edge cases detected:[/yellow]")
        for edge in classification.edge_cases:
            console.print(f"  • {edge}")
    
    console.print(f"\n[dim]Next steps:[/dim]")
    console.print(f"  1. Run [cyan]nis2-audit scan {session.session_id}[/cyan] to discover devices")
    console.print(f"  2. Run [cyan]nis2-audit dashboard[/cyan] to open the TUI")


@app.command()
def list() -> None:
    """List all audit sessions."""
    ctx = typer.get_current_context()
    storage = AuditStorage(ctx.obj["db_path"])
    
    sessions = storage.list_sessions()
    
    if not sessions:
        console.print("[yellow]No audit sessions found.[/yellow]")
        console.print("Create one with: nis2-audit new --name ...")
        return
    
    table = Table(title="Audit Sessions")
    table.add_column("Session ID", style="cyan")
    table.add_column("Entity", style="green")
    table.add_column("Sector", style="dim")
    table.add_column("Classification")
    table.add_column("Status", style="blue")
    table.add_column("Devices")
    table.add_column("Findings")
    table.add_column("Created", style="dim")
    
    for s in sessions:
        classification_style = {
            "Essential Entity": "red",
            "Important Entity": "yellow",
            "Non-Qualifying": "green",
        }.get(s.classification, "white")
        
        table.add_row(
            s.session_id[:20] + "..." if len(s.session_id) > 20 else s.session_id,
            s.entity_name[:30],
            s.entity_sector[:20],
            f"[{classification_style}]{s.classification or 'N/A'}[/{classification_style}]",
            s.status,
            str(s.device_count),
            str(s.finding_count),
            s.created_at.strftime("%Y-%m-%d %H:%M"),
        )
    
    console.print(table)


@app.command()
def show(
    session_id: str = typer.Argument(..., help="Session ID"),
) -> None:
    """Show details of an audit session."""
    ctx = typer.get_current_context()
    storage = AuditStorage(ctx.obj["db_path"])
    
    session = storage.get_session(session_id)
    if not session:
        console.print(f"[red]Session not found: {session_id}[/red]")
        raise typer.Exit(1)
    
    console.print(Panel(
        f"[bold]{session.entity_input.legal_name}[/bold]\n"
        f"[dim]Session ID:[/dim] {session.session_id}\n"
        f"[dim]Status:[/dim] {session.status}\n"
        f"[dim]Created:[/dim] {session.created_at.strftime('%Y-%m-%d %H:%M:%S')}",
        title="Audit Session",
        border_style="blue",
    ))
    
    entity_table = Table(title="Entity Details")
    entity_table.add_column("Field")
    entity_table.add_column("Value")
    entity_table.add_row("Legal Name", session.entity_input.legal_name)
    entity_table.add_row("Sector", session.entity_input.sector)
    entity_table.add_row("Employees", str(session.entity_input.employee_count))
    entity_table.add_row("Turnover", f"€{session.entity_input.annual_turnover_eur:,.0f}")
    if session.entity_input.balance_sheet_total:
        entity_table.add_row("Balance Sheet", f"€{session.entity_input.balance_sheet_total:,.0f}")
    console.print(entity_table)
    
    if session.classification:
        classification_color = {
            "Essential Entity": "red",
            "Important Entity": "yellow",
            "Non-Qualifying": "green",
        }.get(session.classification.classification, "white")
        
        console.print(f"\n[bold {classification_color}]Classification: {session.classification.classification}[/]")
        console.print(f"[dim]{session.classification.legal_basis}[/dim]")
        console.print(f"Confidence: {session.classification.confidence_score:.1%}")
    
    if session.audit_location or session.network_segment:
        console.print(f"\n[bold]Audit Context:[/bold]")
        if session.audit_location:
            console.print(f"  Location: {session.audit_location}")
        if session.network_segment:
            console.print(f"  Network: {session.network_segment}")
    
    console.print(f"\n[bold]Progress:[/bold]")
    console.print(f"  Devices discovered: {session.device_count}")
    console.print(f"  Findings: {session.finding_count}")
    if session.compliance_score:
        console.print(f"  Compliance Score: {session.compliance_score:.1f}%")


@app.command()
def delete(
    session_id: str = typer.Argument(..., help="Session ID to delete"),
    force: bool = typer.Option(False, "--force", "-f", help="Skip confirmation"),
):
    """Delete an audit session."""
    ctx = typer.get_current_context()
    storage = AuditStorage(ctx.obj["db_path"])
    
    session = storage.get_session(session_id)
    if not session:
        console.print(f"[red]Session not found: {session_id}[/red]")
        raise typer.Exit(1)
    
    if not force:
        confirm = typer.confirm(
            f"Delete session for '{session.entity_input.legal_name}'? This cannot be undone."
        )
        if not confirm:
            console.print("Cancelled.")
            raise typer.Exit(0)
    
    storage.delete_session(session_id)
    console.print(f"[green]✓ Deleted session {session_id}[/green]")


@app.command()
def scan(
    session_id: str = typer.Argument(..., help="Session ID to associate devices with"),
    target: Optional[str] = typer.Option(None, "--target", "-t", help="Network to scan (e.g., 192.168.1.0/24)"),
    scan_type: str = typer.Option("quick", "--type", help="Scan type: quick or comprehensive"),
    list_subnets: bool = typer.Option(False, "--list-subnets", "-l", help="List local network subnets"),
) -> None:
    """Scan network for devices and add to session."""
    print_banner()
    
    ctx = typer.get_current_context()
    storage = AuditStorage(ctx.obj["db_path"])
    
    session = storage.get_session(session_id)
    if not session:
        console.print(f"[red]Session not found: {session_id}[/red]")
        raise typer.Exit(1)
    
    # List subnets if requested
    if list_subnets:
        try:
            scanner = NmapScanner()
            subnets = scanner.get_local_subnets()
            console.print("[bold]Local network subnets:[/bold]")
            for subnet in subnets:
                console.print(f"  • {subnet}")
            console.print(f"\nUse: nis2-audit scan {session_id} --target <subnet>")
            return
        except NetworkScannerError as e:
            console.print(f"[yellow]{e}[/yellow]")
            console.print("\nEnter subnet manually, e.g., 192.168.1.0/24")
            return
    
    # Determine target
    if not target:
        if session.network_segment:
            target = session.network_segment
            console.print(f"[dim]Using session network segment: {target}[/dim]")
        else:
            # Try to auto-detect
            try:
                scanner = NmapScanner()
                subnets = scanner.get_local_subnets()
                if subnets:
                    target = subnets[0]
                    console.print(f"[dim]Auto-detected subnet: {target}[/dim]")
                else:
                    console.print("[red]No target specified and auto-detection failed.[/red]")
                    console.print("Use: nis2-audit scan <session> --target 192.168.1.0/24")
                    raise typer.Exit(1)
            except NetworkScannerError as e:
                console.print(f"[red]{e}[/red]")
                raise typer.Exit(1)
    
    console.print(f"\n[bold]Scanning network:[/bold] {target}")
    console.print(f"[dim]Scan type:[/dim] {scan_type}")
    console.print(f"[dim]Session:[/dim] {session.entity_input.legal_name}")
    console.print()
    
    try:
        scanner = NmapScanner()
        with console.status("[bold green]Scanning network... This may take a few minutes."):
            result = scanner.scan_subnet(target, session_id, scan_type=scan_type)
        
        if result.status == "failed":
            console.print(f"[red]Scan failed: {result.error_message}[/red]")
            raise typer.Exit(1)
        
        console.print(f"[bold green]✓[/bold green] Scan complete in {result.duration_seconds:.1f}s")
        console.print(f"[bold]Hosts discovered:[/bold] {result.hosts_up}")
        
        # Fingerprint and save devices
        devices = []
        for host in result.hosts:
            device = DeviceFingerprinter.fingerprint(host)
            device.session_id = session_id
            storage.save_device(device)
            devices.append(device)
        
        session.status = "network_scanned"
        session.device_count = len(devices)
        storage.update_session(session)
        
        if devices:
            display_device_inventory(devices, session.entity_input.legal_name)
        else:
            console.print("[yellow]No devices discovered on this network.[/yellow]")
        
        console.print(f"\n[dim]Next steps:[/dim]")
        console.print(f"  1. Connect to devices: [cyan]nis2-audit connect {session_id}[/cyan]")
        console.print(f"  2. View session: [cyan]nis2-audit show {session_id}[/cyan]")
        
    except NetworkScannerError as e:
        console.print(f"[red]{e}[/red]")
        raise typer.Exit(1)
    except Exception as e:
        logger.error(f"Scan failed: {e}")
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def connect(
    session_id: str = typer.Argument(..., help="Session ID"),
    device_id: Optional[str] = typer.Option(None, "--device", help="Specific device ID (default: all pending)"),
    username: str = typer.Option(..., "--username", "-u", help="SSH username"),
    password: str = typer.Option(..., "--password", "-p", help="SSH password", prompt=True, hide_input=True),
    enable_password: Optional[str] = typer.Option(None, "--enable", help="Enable/secret password", hide_input=True),
    port: int = typer.Option(22, "--port", help="SSH port"),
    quick: bool = typer.Option(True, "--quick/--full", help="Run quick or full audit"),
    auto_detect: bool = typer.Option(True, "--auto-detect/--no-auto-detect", help="Auto-detect device type"),
) -> None:
    """Connect to devices via SSH and run NIS2 audit commands."""
    print_banner()
    
    ctx = typer.get_current_context()
    storage = AuditStorage(ctx.obj["db_path"])
    
    session = storage.get_session(session_id)
    if not session:
        console.print(f"[red]Session not found: {session_id}[/red]")
        raise typer.Exit(1)
    
    # Get devices to connect to
    devices = storage.get_devices(session_id)
    
    if device_id:
        # Specific device
        device = next((d for d in devices if d.device_id == device_id), None)
        if not device:
            console.print(f"[red]Device not found: {device_id}[/red]")
            raise typer.Exit(1)
        devices = [device]
    else:
        # All pending devices
        devices = [d for d in devices if d.connection_status == "pending"]
        if not devices:
            console.print("[yellow]No pending devices found. All devices have been attempted.[/yellow]")
            console.print(f"Use --device to retry a specific device.")
            raise typer.Exit(0)
    
    console.print(f"\n[bold]Connecting to {len(devices)} device(s)[/bold]")
    console.print(f"[dim]Session:[/dim] {session.entity_input.legal_name}")
    console.print(f"[dim]Username:[/dim] {username}")
    console.print(f"[dim]Audit type:[/dim] {'Quick' if quick else 'Full'}")
    console.print()
    
    credentials = DeviceCredentials(
        username=username,
        password=password,
        enable_password=enable_password,
        port=port,
    )
    
    # Connect and audit devices
    cm = ConnectionManager()
    runner = CommandRunner(cm)
    
    success_count = 0
    failed_count = 0
    
    for device in devices:
        console.print(f"Connecting to [cyan]{device.ip_address}[/cyan]... ", end="")
        
        # Connect
        result = cm.connect_device(device, credentials, auto_detect=auto_detect)
        
        if not result.success:
            console.print(f"[red]Failed[/red]")
            console.print(f"  [dim]{result.error_message}[/dim]")
            device.connection_status = "failed"
            storage.save_device(device)
            failed_count += 1
            continue
        
        console.print(f"[green]Connected[/green] ({result.device_type_detected or 'unknown type'})")
        
        try:
            if quick:
                console.print(f"  Running quick audit... ", end="")
                cmd_results = runner.run_quick_audit(device)
            else:
                console.print(f"  Running full audit... ", end="")
                cmd_results = runner.run_audit_on_device(device)
            
            console.print(f"[green]{len([r for r in cmd_results if r.success])}/{len(cmd_results)} commands[/green]")
            
            device.command_results = cmd_results
            
            # Extract config info
            config = ConfigParser.extract_config_info(cmd_results, device.vendor)
            device.config = config
            
            device.connection_status = "connected"
            storage.save_device(device)
            
            success_count += 1
            
        except Exception as e:
            logger.error(f"Audit failed for device {device.device_id}: {e}")
            console.print(f"[red]Audit failed: {e}[/red]")
            device.connection_status = "failed"
            storage.save_device(device)
            failed_count += 1
        finally:
            # Disconnect
            cm.disconnect_device(device.device_id)
    
    if success_count > 0:
        session.status = "devices_interrogated"
        storage.update_session(session)
    
    console.print()
    console.print(f"[bold]Results:[/bold] {success_count} connected, {failed_count} failed")
    
    if success_count > 0:
        console.print(f"\n[dim]Next steps:[/dim]")
        console.print(f"  1. Run checklist: [cyan]nis2-audit checklist {session_id}[/cyan]")
        console.print(f"  2. View devices: [cyan]nis2-audit devices {session_id}[/cyan]")


@app.command()
def checklist(
    session_id: str = typer.Argument(..., help="Session ID"),
    auto: bool = typer.Option(True, "--auto/--manual", help="Auto-analyze device configs"),
    skip_interactive: bool = typer.Option(False, "--skip-questions", help="Skip interactive questions (use auto only)"),
) -> None:
    """Run NIS2 Article 21 checklist assessment."""
    print_banner()
    
    ctx = typer.get_current_context()
    storage = AuditStorage(ctx.obj["db_path"])
    
    session = storage.get_session(session_id)
    if not session:
        console.print(f"[red]Session not found: {session_id}[/red]")
        raise typer.Exit(1)
    
    console.print(f"\n[bold]NIS2 Article 21 Compliance Assessment[/bold]")
    console.print(f"[dim]Entity:[/dim] {session.entity_input.legal_name}")
    console.print(f"[dim]Session:[/dim] {session_id}")
    console.print()
    
    # Get checklist sections
    sections = get_checklist_sections()
    
    # Get devices for auto-analysis
    devices = storage.get_devices(session_id)
    
    # Auto-analyze devices if requested
    if auto and devices:
        console.print("[bold]Auto-analyzing device configurations...[/bold]")
        
        analyzer = GapAnalyzer()
        device_gaps = analyzer.analyze_all_devices(devices)
        
        # Correlate gaps with checklist
        for section in sections:
            section.questions = analyzer.correlate_with_checklist(
                section.questions, device_gaps
            )
        
        gap_summary = analyzer.generate_gap_summary(device_gaps)
        console.print(f"  [green]✓[/green] Analyzed {gap_summary['affected_devices']} devices")
        console.print(f"  [green]✓[/green] Found {gap_summary['total_gaps']} configuration gaps")
        console.print()
    
    # Interactive questionnaire (unless skipped)
    if not skip_interactive:
        console.print("[bold]Interactive Assessment[/bold]")
        console.print("[dim]Answer the following questions (yes/partial/no/na)[/dim]")
        console.print()
        
        for section in sections:
            console.print(f"\n[bold blue]{section.title}[/bold blue]")
            console.print(f"[dim]{section.description}[/dim]")
            
            for question in section.questions:
                # Skip if already answered by device analysis
                if question.status != ComplianceStatus.NOT_STARTED:
                    console.print(f"  [dim]{question.id}: {question.question[:50]}... [auto-detected][/dim]")
                    continue
                
                console.print(f"\n  [bold]{question.id}: {question.question}[/bold]")
                if question.guidance:
                    console.print(f"  [dim]Guidance: {question.guidance}[/dim]")
                
                # Get response (simulate for now - in real TUI would be interactive)
                # For now, leave as NOT_STARTED for manual review
                console.print(f"  [dim]Status: {question.status.value}[/dim]")
    
    # Calculate scores
    console.print("\n[bold]Calculating compliance scores...[/bold]")
    
    scorer = ComplianceScorer()
    score = scorer.generate_compliance_score(session_id, sections)
    
    session.compliance_score = score.overall_score
    session.status = "checklist_completed"
    storage.update_session(session)
    
    # Generate findings
    generator = FindingGenerator()
    
    # Get all questions flattened
    all_questions = []
    for section in sections:
        all_questions.extend(section.questions)
    
    # Regenerate device gaps for finding generation
    device_gaps = {}
    if devices and auto:
        analyzer = GapAnalyzer()
        device_gaps = analyzer.analyze_all_devices(devices)
    
    findings = generator.generate_all_findings(all_questions, device_gaps, session_id)
    findings = prioritize_findings(findings)
    
    for finding in findings:
        storage.save_finding(finding)
    
    session.finding_count = len(findings)
    storage.update_session(session)
    
    console.print()
    console.print(format_score_report(score))
    
    if findings:
        summary = get_findings_summary(findings)
        console.print("\n[bold]Findings Generated:[/bold]")
        for sev, count in summary["by_severity"].items():
            if count > 0:
                color = {"critical": "red", "high": "yellow", "medium": "blue", "low": "dim"}.get(sev, "white")
                console.print(f"  [{color}]{sev.capitalize()}: {count}[/{color}]")
    
    console.print(f"\n[dim]Next steps:[/dim]")
    console.print(f"  1. View findings: [cyan]nis2-audit findings {session_id}[/cyan]")
    console.print(f"  2. Generate report: [cyan]nis2-audit report {session_id}[/cyan]")


@app.command()
def findings(
    session_id: str = typer.Argument(..., help="Session ID"),
    severity: Optional[str] = typer.Option(None, "--severity", "-s", help="Filter by severity"),
):
    """Show audit findings for a session."""
    ctx = typer.get_current_context()
    storage = AuditStorage(ctx.obj["db_path"])
    
    session = storage.get_session(session_id)
    if not session:
        console.print(f"[red]Session not found: {session_id}[/red]")
        raise typer.Exit(1)
    
    findings = storage.get_findings(session_id)
    
    if severity:
        findings = [f for f in findings if f.severity == severity]
    
    if not findings:
        console.print("[yellow]No findings found.[/yellow]")
        console.print(f"Run: nis2-audit checklist {session_id}")
        return
    
    console.print(f"\n[bold]Audit Findings for {session.entity_input.legal_name}[/bold]")
    console.print()
    
    for i, finding in enumerate(findings[:20], 1):  # Show first 20
        color = {
            "critical": "red",
            "high": "yellow",
            "medium": "blue",
            "low": "dim",
        }.get(finding.severity, "white")
        
        console.print(f"{i}. [{color}]{finding.severity.upper()}[/{color}] {finding.title}")
        console.print(f"   [dim]Article: {finding.nis2_article}[/dim]")
        if finding.recommendation:
            console.print(f"   [dim]Recommendation: {finding.recommendation[:80]}...[/dim]")
        console.print()
    
    if len(findings) > 20:
        console.print(f"[dim]... and {len(findings) - 20} more findings[/dim]")


@app.command()
def report(
    session_id: str = typer.Argument(..., help="Session ID"),
    output: str = typer.Option(..., "--output", "-o", help="Output file path"),
    format: str = typer.Option("markdown", "--format", "-f", help="Output format: markdown or json"),
) -> None:
    """Generate audit report (Markdown or JSON)."""
    print_banner()
    
    ctx = typer.get_current_context()
    storage = AuditStorage(ctx.obj["db_path"])
    
    session = storage.get_session(session_id)
    if not session:
        console.print(f"[red]Session not found: {session_id}[/red]")
        raise typer.Exit(1)
    
    console.print(f"\n[bold]Generating {format} report...[/bold]")
    console.print(f"[dim]Entity:[/dim] {session.entity_input.legal_name}")
    console.print(f"[dim]Output:[/dim] {output}")
    console.print()
    
    devices = storage.get_devices(session_id)
    findings = storage.get_findings(session_id)
    
    from .audit.checklist import get_checklist_sections
    from .audit.scorer import ComplianceScorer
    from .audit.gap_analyzer import GapAnalyzer
    
    sections = get_checklist_sections()
    
    # Auto-analyze devices
    if devices:
        analyzer = GapAnalyzer()
        device_gaps = analyzer.analyze_all_devices(devices)
        for section in sections:
            section.questions = analyzer.correlate_with_checklist(
                section.questions, device_gaps
            )
    
    # Calculate score
    scorer = ComplianceScorer()
    score = scorer.generate_compliance_score(session_id, sections)
    
    # Calculate sanction exposure
    sanction_calc = SanctionCalculator()
    sanction_exposure = sanction_calc.calculate_exposure(
        classification=session.classification.classification if session.classification else "Unknown",
        annual_turnover=session.entity_input.annual_turnover_eur,
        compliance_score=score.overall_score,
        critical_findings=score.critical_findings,
        high_findings=score.high_findings,
    )
    
    # Generate report
    generator = ReportGenerator()
    
    if format.lower() == "json":
        report_content = generator.generate_json_report(
            session, devices, findings, sections, score, sanction_exposure
        )
    else:
        report_content = generator.generate_markdown_report(
            session, devices, findings, sections, score, sanction_exposure
        )
    
    # Write to file
    output_path = Path(output)
    output_path.write_text(report_content)
    
    console.print(f"[bold green]✓[/bold green] Report saved to: {output}")
    console.print()
    
    console.print(f"[bold]Report Summary:[/bold]")
    console.print(f"  Devices: {len(devices)}")
    console.print(f"  Findings: {len(findings)}")
    console.print(f"  Compliance Score: {score.overall_score:.1f}%")
    console.print(f"  Potential Sanction: €{sanction_exposure['potential_fine_eur']:,.0f}")


@app.command()
def devices(
    session_id: str = typer.Argument(..., help="Session ID"),
):
    """Show discovered devices for a session."""
    ctx = typer.get_current_context()
    storage = AuditStorage(ctx.obj["db_path"])
    
    session = storage.get_session(session_id)
    if not session:
        console.print(f"[red]Session not found: {session_id}[/red]")
        raise typer.Exit(1)
    
    devices = storage.get_devices(session_id)
    
    if not devices:
        console.print("[yellow]No devices discovered yet.[/yellow]")
        console.print(f"Run: nis2-audit scan {session_id} --target <network>")
        return
    
    display_device_inventory(devices, session.entity_input.legal_name)


@app.command()
def dashboard(
    session_id: Optional[str] = typer.Option(None, "--session", "-s", help="Open specific session"),
):
    """Launch the interactive TUI dashboard."""
    from .tui.dashboard import run_dashboard
    
    ctx = typer.get_current_context()
    db_path = ctx.obj["db_path"]
    
    run_dashboard(db_path=db_path, session_id=session_id)


@app.command()
def classify(
    name: str = typer.Option(..., "--name", "-n", help="Entity legal name"),
    sector: str = typer.Option(..., "--sector", "-s", help="Entity sector"),
    employees: int = typer.Option(..., "--employees", "-e", help="Number of employees"),
    turnover: float = typer.Option(..., "--turnover", "-t", help="Annual turnover in EUR"),
    balance: Optional[float] = typer.Option(None, "--balance", "-b", help="Balance sheet total"),
    public_admin: bool = typer.Option(False, "--public-admin", help="Is public administration"),
    dns_provider: bool = typer.Option(False, "--dns", help="Is DNS provider"),
    tld_registry: bool = typer.Option(False, "--tld", help="Is TLD registry"),
    trust_service: bool = typer.Option(False, "--trust", help="Is trust service provider"),
):
    """Classify an entity without creating a session."""
    print_banner()
    
    entity_input = EntityInput(
        legal_name=name,
        sector=sector,
        employee_count=employees,
        annual_turnover_eur=turnover,
        balance_sheet_total=balance,
        cross_border_operations=CrossBorderInfo(operates_cross_border=False),
        is_public_admin=public_admin,
        is_dns_provider=dns_provider,
        is_tld_registry=tld_registry,
        is_trust_service_provider=trust_service,
    )
    
    classifier = EntityClassifier()
    result = classifier.classify(entity_input)
    
    console.print(f"\n[bold]Entity:[/bold] {name}")
    console.print(f"[bold]Sector:[/bold] {sector}")
    console.print(f"[bold]Size:[/bold] {employees} employees, €{turnover:,.0f} turnover")
    
    if result.classification == "Essential Entity":
        console.print(f"\n[bold red on white] 🔴 ESSENTIAL ENTITY [/bold red on white]")
    elif result.classification == "Important Entity":
        console.print(f"\n[bold yellow on black] 🟡 IMPORTANT ENTITY [/bold yellow on black]")
    else:
        console.print(f"\n[bold green] 🟢 NON-QUALIFYING [/bold green]")
    
    console.print(f"\n[dim]{result.legal_basis}[/dim]")
    console.print(f"\n[bold]Annex:[/bold] {result.annex or 'N/A'}")
    console.print(f"[bold]Lead Authority:[/bold] {result.lead_authority}")
    console.print(f"[bold]Confidence:[/bold] {result.confidence_score:.1%}")
    
    # Reasoning chain
    console.print("\n[bold]Reasoning:[/bold]")
    for reason in result.reasoning_chain:
        console.print(f"  • {reason}")
    
    if result.edge_cases:
        console.print("\n[yellow]⚠ Edge Cases:[/yellow]")
        for edge in result.edge_cases:
            console.print(f"  • {edge}")


def cli_entry():
    """Entry point for console scripts."""
    app()


if __name__ == "__main__":
    cli_entry()
