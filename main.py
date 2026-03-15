#!/usr/bin/env python3
"""
NIS2 Compliance Assessment System - Main Entry Point

This application provides a comprehensive NIS2 compliance assessment
system with multiple specialized agents for classification, audit,
enforcement, gap analysis, and reporting.

Usage:
    python main.py [command] [options]

Commands:
    classify      Classify an entity under NIS2
    audit         Run full audit assessment
    gap           Run gap analysis
    enforce       Calculate enforcement actions
    report        Generate compliance report
    interactive   Start interactive CLI
"""

# Add project root to Python path BEFORE any imports
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

import argparse
import json
from typing import Optional

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt, IntPrompt, FloatPrompt, Confirm
from rich import box

from core import Orchestrator
from shared.data.mock_entities import (
    EE_ENERGY, IE_MANUFACTURING, IE_DIGITAL, RO_HOSPITAL,
    ALL_MOCK_ENTITIES, list_mock_entities
)

# Import Romanian audit assessor
try:
    from agents.romanian_audit import RomanianAuditAssessor
    ROMANIAN_AUDIT_AVAILABLE = True
except ImportError:
    ROMANIAN_AUDIT_AVAILABLE = False
from shared.schemas import EntityInput, CrossBorderInfo


console = Console()


def print_banner():
    """Print application banner."""
    console.print(Panel.fit(
        "[bold blue]NIS2 Compliance Assessment System[/bold blue]\n"
        "[dim]Directive (EU) 2022/2555 - Cybersecurity Risk Management[/dim]",
        title="🇪🇺 NIS2",
        border_style="blue"
    ))


def create_orchestrator() -> Orchestrator:
    """Create and return orchestrator instance."""
    return Orchestrator()


def cmd_classify(args):
    """Handle classify command."""
    orchestrator = create_orchestrator()
    
    if args.mock:
        entity = get_mock_entity(args.mock)
    else:
        entity = prompt_for_entity()
    
    console.print(f"\n[bold]Classifying entity:[/bold] {entity.legal_name}")
    
    session_id = orchestrator.start_session(entity)
    result = orchestrator.classify_entity(session_id)
    
    display_classification_result(result, entity)
    
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(result, f, indent=2)
        console.print(f"\n[green]Result saved to:[/green] {args.output}")


def cmd_audit(args):
    """Handle audit command."""
    orchestrator = create_orchestrator()
    
    if args.mock:
        entity = get_mock_entity(args.mock)
    else:
        entity = prompt_for_entity()
    
    console.print(f"\n[bold]Running audit for:[/bold] {entity.legal_name}")
    
    session_id = orchestrator.start_session(entity)
    
    # Run classification first
    classify_result = orchestrator.classify_entity(session_id)
    if classify_result.get("state") in ["non_qualifying"]:
        console.print("[yellow]Entity is non-qualifying. Audit not required.[/yellow]")
        return
    
    # Check if Romanian entity
    is_romanian = classify_result.get("is_romanian_entity", False)
    
    if is_romanian and ROMANIAN_AUDIT_AVAILABLE:
        # Run Romanian-specific audit
        with console.status("[bold green]Executare audit NIS2 România..."):
            # Get necessary data
            ro_classification = classify_result.get("ro_classification", {})
            
            # Run CyFun assessment - handle dataclass result
            cyfun_raw = orchestrator.run_cyfun_maturity_assessment(session_id)
            if isinstance(cyfun_raw, dict):
                cyfun_data = cyfun_raw.get("cyfun_result", {})
            else:
                cyfun_data = {}
            
            # Run ENIRE assessment - handle dataclass result
            enire_raw = orchestrator.run_enire_risk_assessment(session_id)
            if isinstance(enire_raw, dict):
                enire_data = enire_raw.get("enire_result", {})
            else:
                enire_data = {}
            
            # Create Romanian audit assessor
            ro_auditor = RomanianAuditAssessor()
            audit_result = ro_auditor.execute_audit(
                entity_data=entity,
                ro_classification=ro_classification,
                cyfun_result=cyfun_data,
                enire_result=enire_data
            )
        
        display_romanian_audit_result(audit_result)
        
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                json.dump(audit_result.to_dict(), f, indent=2, ensure_ascii=False)
            console.print(f"\n[green]Rezultat salvat în:[/green] {args.output}")
    else:
        # Run standard EU audit
        with console.status("[bold green]Running 5-phase audit..."):
            result = orchestrator.run_audit(session_id)
        
        display_audit_result(result)
        
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(result, f, indent=2)
            console.print(f"\n[green]Result saved to:[/green] {args.output}")


def cmd_gap(args):
    """Handle gap analysis command."""
    orchestrator = create_orchestrator()
    
    if args.mock:
        entity = get_mock_entity(args.mock)
    else:
        entity = prompt_for_entity()
    
    mode = args.mode or "deep_dive"
    
    console.print(f"\n[bold]Running {mode} gap analysis for:[/bold] {entity.legal_name}")
    
    session_id = orchestrator.start_session(entity)
    
    with console.status(f"[bold green]Running {mode} analysis..."):
        result = orchestrator.run_gap_analysis(session_id, mode=mode)
    
    display_gap_result(result)
    
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(result, f, indent=2)
        console.print(f"\n[green]Result saved to:[/green] {args.output}")


def cmd_interactive(args):
    """Run interactive CLI mode."""
    print_banner()
    
    orchestrator = create_orchestrator()
    
    console.print("\n[bold]Welcome to the NIS2 Compliance Assessment System[/bold]")
    console.print("This tool helps assess NIS2 compliance for Essential and Important Entities.\n")
    
    # Show mock entity options
    console.print("[bold cyan]Available Sample Entities:[/bold cyan]")
    for i, entity in enumerate(ALL_MOCK_ENTITIES, 1):
        console.print(f"  {i}. {entity.legal_name} ({entity.sector}, {entity.employee_count} employees)")
    console.print("  5. Enter custom entity details")
    
    choice = IntPrompt.ask(
        "\nSelect an entity",
        choices=[str(i) for i in range(1, 6)],
        default=1
    )
    
    if choice <= 4:
        entity = ALL_MOCK_ENTITIES[choice - 1]
    else:
        entity = prompt_for_entity()
    
    console.print(f"\n[bold]Selected:[/bold] {entity.legal_name}\n")
    
    # Start session
    session_id = orchestrator.start_session(entity)
    
    # Classification
    with console.status("[bold green]Classifying entity..."):
        classify_result = orchestrator.classify_entity(session_id)
    
    display_classification_result(classify_result, entity)
    
    # Check if national designation may apply
    from agents.entity_classifier import EntityClassifier
    from shared.knowledge_base import NIS2KnowledgeBase
    from shared.schemas import EntityClassification, SizeDetails
    
    kb = NIS2KnowledgeBase()
    classifier = EntityClassifier(kb)
    
    classification_data = classify_result.get("classification", {})
    temp_classification = EntityClassification(
        entity_id=classification_data.get("entity_id", ""),
        classification=classification_data.get("classification", ""),
        legal_basis=classification_data.get("legal_basis", ""),
        annex=classification_data.get("annex"),
        sector_classification=classification_data.get("sector_classification", ""),
        size_qualification=classification_data.get("size_qualification", False),
        size_details=SizeDetails(
            employee_count=entity.employee_count,
            annual_turnover_eur=entity.annual_turnover_eur,
            balance_sheet_total=entity.balance_sheet_total
        ),
        cross_border=entity.cross_border_operations,
        lead_authority=classification_data.get("lead_authority", "XX"),
        confidence_score=classification_data.get("confidence_score", 0),
        edge_cases=classification_data.get("edge_cases", []),
        reasoning_chain=classification_data.get("reasoning_chain", [])
    )
    
    national_check = classifier.check_national_designation(entity, temp_classification)
    
    if classify_result.get("state") == "non_qualifying" and not national_check.get("applicable"):
        console.print("\n[yellow]Entity is non-qualifying. No further assessment required.[/yellow]")
        return
    
    if classify_result.get("state") == "non_qualifying" and national_check.get("applicable"):
        console.print("\n[cyan]This entity may be designated as Essential under national rules.[/cyan]")
        if not Confirm.ask("Would you like to proceed with a compliance assessment?"):
            return
    
    # Ask what to do next
    console.print("\n[bold cyan]Next Steps:[/bold cyan]")
    console.print("  1. Run full audit")
    console.print("  2. Run gap analysis")
    console.print("  3. Exit")
    
    next_action = IntPrompt.ask("Select action", choices=["1", "2", "3"], default=1)
    
    if next_action == 1:
        with console.status("[bold green]Running full audit..."):
            audit_result = orchestrator.run_audit(session_id)
        display_audit_result(audit_result)
        
        # Offer report generation
        if Confirm.ask("\nGenerate compliance report?"):
            report = orchestrator.generate_report(session_id, "executive_summary", "markdown")
            console.print("\n[bold]Report Generated:[/bold]")
            console.print(report.get("content", "No content"))
    
    elif next_action == 2:
        mode = Prompt.ask("Analysis mode", choices=["quick_scan", "deep_dive"], default="deep_dive")
        with console.status(f"[bold green]Running {mode}..."):
            gap_result = orchestrator.run_gap_analysis(session_id, mode=mode)
        display_gap_result(gap_result)


def prompt_for_entity() -> EntityInput:
    """Prompt user for entity details."""
    console.print("\n[bold cyan]Enter Entity Details:[/bold cyan]")
    
    name = Prompt.ask("Legal name")
    sector = Prompt.ask("Sector (e.g., energy, banking, health)")
    employees = IntPrompt.ask("Employee count")
    turnover = FloatPrompt.ask("Annual turnover (EUR)")
    
    # Always ask for country code for lead authority determination
    country = Prompt.ask("Country code (e.g., RO, DE, FR)", default="RO").strip().upper()
    
    cross_border = Prompt.ask(
        "Does the entity operate cross-border?",
        choices=["y", "n"],
        default="n"
    ) == "y"
    
    member_states = [country]
    if cross_border:
        ms_input = Prompt.ask("Additional member states (comma-separated, e.g., DE,FR,NL)")
        additional = [m.strip().upper() for m in ms_input.split(",") if m.strip()]
        member_states.extend(additional)
    
    return EntityInput(
        entity_id=f"ENT-{hash(name) & 0xFFFFFFFF:08x}",
        legal_name=name,
        sector=sector,
        employee_count=employees,
        annual_turnover_eur=turnover,
        cross_border_operations=CrossBorderInfo(
            operates_cross_border=cross_border,
            member_states=member_states,
            main_establishment=country
        )
    )


def get_mock_entity(mock_id: str) -> EntityInput:
    """Get mock entity by ID or index."""
    if mock_id.isdigit():
        idx = int(mock_id) - 1
        if 0 <= idx < len(ALL_MOCK_ENTITIES):
            return ALL_MOCK_ENTITIES[idx]
    
    for entity in ALL_MOCK_ENTITIES:
        if entity.entity_id == mock_id or entity.legal_name.lower().replace(" ", "_") == mock_id.lower():
            return entity
    
    raise ValueError(f"Mock entity not found: {mock_id}")


def display_classification_result(result: dict, entity_data=None):
    """Display classification result - handles both EU and Romanian formats."""
    
    # Check if this is a Romanian classification result
    is_romanian = result.get("is_romanian_entity", False)
    
    if is_romanian and "ro_classification" in result:
        # Display Romanian classification
        ro = result["ro_classification"]
        
        table = Table(title="[bold green]Clasificare NIS2 România[/bold green]", box=box.ROUNDED)
        table.add_column("Atribut", style="cyan")
        table.add_column("Valoare", style="green")
        
        table.add_row("Clasificare", f"[bold]{ro.get('classification', 'Necunoscut').upper()}[/bold]")
        table.add_row("Nivel CyFunRO", ro.get('cyfun_level', 'N/A'))
        table.add_row("Sector", ro.get('sector_name', 'N/A'))
        table.add_row("Cod Sector", result.get('ro_sector_code', 'N/A') or "")
        table.add_row("Dimensiune", ro.get('size_category', 'N/A'))
        table.add_row("Anexa", str(ro.get('annex', 'N/A')))
        table.add_row("Prioritate", str(ro.get('priority_level', 'N/A')))
        table.add_row("Înregistrare DNSC", "[bold red]OBLIGATORIE[/bold red]" if ro.get('dnsc_registration_required') else "Nu")
        
        console.print(table)
        
        # Display legal basis
        console.print(f"\n[cyan]Bază legală:[/cyan]")
        console.print(f"  {ro.get('legal_basis', 'N/A')}")
        
        # Display reasoning
        if ro.get('reasoning'):
            console.print(f"\n[cyan]Raționament:[/cyan]")
            for r in ro.get('reasoning', [])[:3]:
                console.print(f"  • {r}")
        
        # Display Art 9 info if applicable
        if ro.get('art9_required'):
            console.print("\n[bold yellow]⚠️  NECESITĂ ANALIZĂ ARTICOLUL 9[/bold yellow]")
            console.print("[yellow]Entitatea nu îndeplinește pragurile de dimensiune dar[/yellow]")
            console.print("[yellow]poate fi desemnată Esențială în baza Art 9 din OUG 155/2024[/yellow]")
        
        # Display EU classification for comparison
        if "eu_classification" in result:
            eu = result["eu_classification"]
            console.print(f"\n[dim]Clasificare UE (comparație): {eu.get('classification', 'N/A')}[/dim]")
    
    else:
        # Display EU classification (original format)
        classification = result.get("classification", {})
        
        table = Table(title="Entity Classification Result", box=box.ROUNDED)
        table.add_column("Attribute", style="cyan")
        table.add_column("Value", style="green")
        
        table.add_row("Classification", classification.get("classification", "Unknown"))
        table.add_row("Legal Basis", classification.get("legal_basis", "N/A"))
        table.add_row("Annex", classification.get("annex", "N/A"))
        table.add_row("Sector", classification.get("sector_classification", "N/A"))
        table.add_row("Lead Authority", classification.get("lead_authority", "N/A"))
        table.add_row("Confidence", f"{classification.get('confidence_score', 0) * 100:.1f}%")
        
        edge_cases = classification.get("edge_cases", [])
        if edge_cases:
            table.add_row("Edge Cases", "\n".join(edge_cases))
        
        console.print(table)
        
        # Confidence warning
        if classification.get("confidence_score", 1.0) < 0.70:
            console.print("\n[yellow]⚠️  Low confidence - manual review recommended[/yellow]")
            if national_check.get('action_required'):
                console.print(f"[bold red]Action Required:[/bold red] {national_check.get('action_required')}")


def display_audit_result(result: dict):
    """Display audit result."""
    audit = result.get("audit_result", {})
    
    # Overall score
    score = audit.get("overall_score", 0)
    rating = audit.get("rating", "Unknown")
    
    color = "green" if score >= 90 else "yellow" if score >= 75 else "red"
    console.print(f"\n[bold]Overall Score:[/bold] [{color}]{score:.1f}%[/{color}] - {rating}")
    
    # Domain scores
    table = Table(title="Domain Scores", box=box.ROUNDED)
    table.add_column("Domain", style="cyan")
    table.add_column("Score", style="green")
    table.add_column("Weight", style="dim")
    
    for domain in audit.get("domain_scores", []):
        table.add_row(
            domain.get("domain", "Unknown"),
            f"{domain.get('score', 0):.1f}%",
            f"{domain.get('weight', 0) * 100:.0f}%"
        )
    
    console.print(table)
    
    # Findings summary
    findings = audit.get("findings", [])
    if findings:
        console.print(f"\n[bold]Findings:[/bold] {len(findings)} total")
        for finding in findings[:5]:
            severity = finding.get("severity", "Unknown")
            color = {"Critical": "red", "High": "orange", "Medium": "yellow"}.get(severity, "white")
            console.print(f"  [{color}]• {finding.get('id', 'N/A')}: {finding.get('title', 'N/A')}[/{color}]")


def display_romanian_audit_result(result):
    """Display detailed Romanian audit result."""
    from rich.panel import Panel
    
    # Header with entity info
    console.print(Panel(
        f"[bold white]RAPORT DE AUDIT NIS2 - ROMÂNIA[/bold white]\n"
        f"[cyan]{result.nume_entitate}[/cyan]\n"
        f"[dim]ID Audit: {result.id_audit} | Data: {result.data_audit.strftime('%Y-%m-%d %H:%M')}[/dim]",
        border_style="blue"
    ))
    
    # Classification info
    clasificare_color = {
        "ESENTIAL": "red",
        "IMPORTANT": "orange",
        "BASIC": "green"
    }.get(result.clasificare, "white")
    
    console.print(f"\n[bold]Clasificare Entitate:[/bold] [{clasificare_color}]{result.clasificare}[/{clasificare_color}]")
    console.print(f"[bold]Nivel CyFunRO:[/bold] {result.nivel_cyfun}")
    console.print(f"[bold]Cod Sector:[/bold] {result.cod_sector}")
    
    # ENIRE Score if available
    if result.enire_score:
        enire_color = "red" if result.enire_score >= 200 else ("orange" if result.enire_score >= 100 else "green")
        console.print(f"[bold]Scor ENIRE:[/bold] [{enire_color}]{result.enire_score}[/{enire_color}] ({result.enire_cyfun_level or 'N/A'})")
    
    # Overall score with color
    scor = result.scor_general
    target = result.target_maturity
    if scor >= 4.0:
        scor_color = "green"
        scor_text = "CONFORM"
    elif scor >= 3.5:
        scor_color = "yellow"
        scor_text = "PARȚIAL CONFORM"
    elif scor >= 3.0:
        scor_color = "orange"
        scor_text = "NECONFORM"
    else:
        scor_color = "red"
        scor_text = "CRITIC"
    
    console.print(f"\n[bold]Scor General Conformitate:[/bold] [{scor_color}]{scor:.2f}/5.0[/{scor_color}] (Țintă: {target})")
    console.print(f"[bold]Status:[/bold] {scor_text}")
    
    # Category scores table
    console.print("\n[bold cyan]Scoruri pe Categorii CyFun:[/bold cyan]")
    table = Table(box=box.ROUNDED, show_header=True)
    table.add_column("Categorie", style="cyan")
    table.add_column("Denumire", style="white")
    table.add_column("Scor", style="green", justify="center")
    table.add_column("Status", style="yellow")
    
    categorii = {
        "GV": ("Guvernanță", result.scor_guvernanta),
        "ID": ("Identificare", result.scor_identificare),
        "PR": ("Protecție", result.scor_protectie),
        "DE": ("Detectare", result.scor_detectare),
        "RS": ("Răspuns", result.scor_raspuns),
        "RC": ("Recuperare", result.scor_recuperare),
    }
    
    threshold = 3.5 if result.clasificare == "ESSENTIAL" else 3.0
    
    for cod, (nume, scor_cat) in categorii.items():
        status = "✓" if scor_cat >= threshold else "✗"
        status_color = "green" if scor_cat >= threshold else "red"
        table.add_row(
            cod,
            nume,
            f"{scor_cat:.2f}",
            f"[{status_color}]{status}[/{status_color}]"
        )
    
    console.print(table)
    
    # Findings summary
    console.print("\n[bold cyan]Constatări Audit:[/bold cyan]")
    findings_table = Table(box=box.ROUNDED)
    findings_table.add_column("Nivel", style="bold")
    findings_table.add_column("Număr", justify="center")
    findings_table.add_column("Termen Remediere", style="dim")
    
    crit_count = len(result.constatari_critice)
    maj_count = len(result.constatari_majore)
    min_count = len(result.constatari_minore)
    
    if crit_count > 0:
        findings_table.add_row(
            "[red]CRITICE[/red]",
            f"[red]{crit_count}[/red]",
            f"[red]{result.termen_remediere_critice}[/red]"
        )
    if maj_count > 0:
        findings_table.add_row(
            "[orange]MAJORE[/orange]",
            f"[orange]{maj_count}[/orange]",
            f"[orange]{result.termen_remediere_majore}[/orange]"
        )
    if min_count > 0:
        findings_table.add_row(
            "[yellow]MINORE[/yellow]",
            f"[yellow]{min_count}[/yellow]",
            f"[yellow]{result.termen_remediere_minore}[/yellow]"
        )
    
    if crit_count == 0 and maj_count == 0 and min_count == 0:
        findings_table.add_row("[green]Nicio constatare[/green]", "-", "-")
    
    console.print(findings_table)
    
    # Detailed critical findings
    if result.constatari_critice:
        console.print("\n[bold red]⚠️  CONSTATĂRI CRITICE (Acțiune Imediată Necesară):[/bold red]")
        for i, const in enumerate(result.constatari_critice[:3], 1):
            console.print(Panel(
                f"[bold]{const.descriere}[/bold]\n\n"
                f"[cyan]Referință Legală:[/cyan] {const.referinta_legal}\n"
                f"[cyan]Recomandare:[/cyan] {const.recomandare}\n"
                f"[red]Termen: {const.termen_remediere}[/red]",
                title=f"[red]C{i}: {const.cod}[/red]",
                border_style="red"
            ))
    
    # Major findings
    if result.constatari_majore:
        console.print(f"\n[bold yellow]📋 Constatări Majore ({len(result.constatari_majore)}):[/bold yellow]")
        for const in result.constatari_majore[:3]:
            console.print(f"  [yellow]• {const.cod}:[/yellow] {const.descriere[:80]}...")
    
    # Conformity status
    console.print("\n[bold cyan]Status Conformitate:[/bold cyan]")
    conform_table = Table(box=box.ROUNDED)
    conform_table.add_column("Indicator", style="cyan")
    conform_table.add_column("Status", style="green")
    
    # Determine actual compliance based on score vs target
    actual_compliant = result.scor_general >= result.target_maturity
    conform_status = "[green]✓ CONFORM[/green]" if actual_compliant else "[red]✗ NECONFORM[/red]"
    conform_table.add_row("Conformitate CyFunRO", conform_status)
    
    plan_status = "[red]DA - OBLIGATORIU[/red]" if (not actual_compliant or result.plan_remediere_necesar) else "[green]NU[/green]"
    conform_table.add_row("Plan Remediere Necesar", plan_status)
    
    conform_table.add_row("Nivel General", result.nivel_conformitate_general)
    
    console.print(conform_table)
    
    # Detailed Domain Assessments
    console.print("\n[bold cyan]📊 Evaluări Detaliate pe Domenii:[/bold cyan]")
    for evaluare in result.evaluari_domenii:
        progress = evaluare.masuri_implementate / evaluare.masuri_necesare if evaluare.masuri_necesare > 0 else 0
        bar_filled = int(progress * 20)
        bar_empty = 20 - bar_filled
        progress_bar = "█" * bar_filled + "░" * bar_empty
        
        status_color = "green" if evaluare.scor >= 3.5 else ("yellow" if evaluare.scor >= 3.0 else "red")
        console.print(f"\n  [{status_color}]▸ {evaluare.domeniu}[/{status_color}]")
        console.print(f"    Scor: {evaluare.scor:.2f}/5.0 | Măsuri: {evaluare.masuri_implementate}/{evaluare.masuri_necesare}")
        console.print(f"    [{status_color}]{progress_bar}[/{status_color}] {progress*100:.0f}%")
        
        if evaluare.constatari:
            for const in evaluare.constatari[:2]:
                console.print(f"    ⚠️  {const.descriere[:60]}...")
    
    # Detailed Major Findings
    if result.constatari_majore:
        console.print("\n[bold yellow]📋 Detalii Constatări Majore:[/bold yellow]")
        for i, const in enumerate(result.constatari_majore, 1):
            console.print(Panel(
                f"[bold]{const.descriere}[/bold]\n\n"
                f"[cyan]Categorie:[/cyan] {const.categorie}\n"
                f"[cyan]Referință Legală:[/cyan] {const.referinta_legal}\n"
                f"[yellow]Recomandare:[/yellow] {const.recomandare}\n"
                f"[red]⏱️ Termen Remediere: {const.termen_remediere}[/red]",
                title=f"[yellow]M{i}: {const.cod} | Nivel: {const.nivel_risc}[/yellow]",
                border_style="yellow"
            ))
    
    # Remediation Timeline
    console.print("\n[bold cyan]📅 Plan de Remediere și Termene:[/bold cyan]")
    timeline = Table(box=box.ROUNDED)
    timeline.add_column("Etapă", style="cyan")
    timeline.add_column("Termen", style="yellow")
    timeline.add_column("Acțiuni", style="white")
    
    if result.constatari_critice:
        timeline.add_row(
            "🔴 Remediere Critică",
            f"[red]{result.termen_remediere_critice}[/red]",
            f"Rezolvarea a {len(result.constatari_critice)} constatări critice"
        )
    if result.constatari_majore:
        timeline.add_row(
            "🟠 Remediere Majoră",
            f"[yellow]{result.termen_remediere_majore}[/yellow]",
            f"Rezolvarea a {len(result.constatari_majore)} constatări majore"
        )
    if result.constatari_minore:
        timeline.add_row(
            "🟡 Remediere Minoră",
            f"[yellow]{result.termen_remediere_minore}[/yellow]",
            f"Rezolvarea a {len(result.constatari_minore)} constatări minore"
        )
    
    timeline.add_row(
        "📊 Verificare Intermediară",
        "6 luni",
        "Evaluarea progresului remediere"
    )
    timeline.add_row(
        "📝 Audit Următor",
        result.data_urmator_audit,
        "Audit de conformitate anual"
    )
    
    console.print(timeline)
    
    # Immediate actions
    if result.actiuni_imediate:
        console.print("\n[bold cyan]⚡ Acțiuni Imediat Necesare:[/bold cyan]")
        for i, actiune in enumerate(result.actiuni_imediate[:5], 1):
            console.print(f"  {i}. {actiune}")
    
    # Priority recommendations
    if result.recomandari_prioritare:
        console.print("\n[bold cyan]💡 Recomandări Prioritare:[/bold cyan]")
        for i, rec in enumerate(result.recomandari_prioritare[:5], 1):
            console.print(f"  {i}. {rec}")
    
    # Sanctions information
    console.print("\n[bold red]⚠️  Sancțiuni pentru Neconformitate:[/bold red]")
    if result.clasificare == "ESSENTIAL":
        console.print(Panel(
            "[bold]Conform Art. 32 din OUG 155/2024:[/bold]\n\n"
            "• [red]Avertisment[/red] - pentru încălcări minore\n"
            "• [red]Obligația de a informa[/red] - entitățile afectate de încălcări\n"
            "• [red]Ordin de încetare[/red] - pentru încălcări grave\n"
            "• [red]Amendă contravențională[/red] - până la 200.000 RON (~€40.000)\n"
            "• [red]Amendă procentuală[/red] - până la 2% din cifra globală de afaceri\n\n"
            "[bold]Pentru entități esențiale - nivel maxim de sancțiuni.[/bold]",
            title="[red]Regim Sancționator[/red]",
            border_style="red"
        ))
    
    # Essential entity specific requirements
    if result.clasificare == "ESSENTIAL":
        console.print("\n[bold red]📋 Obligații Specifice Entități Esențiale:[/bold red]")
        req_table = Table(box=box.ROUNDED)
        req_table.add_column("Obligație", style="cyan")
        req_table.add_column("Termen", style="yellow")
        req_table.add_column("Platformă/Autoritate", style="green")
        
        req_table.add_row(
            "Înregistrare NIS2@RO",
            "30 zile de la clasificare",
            "platforma.nis2.ro"
        )
        req_table.add_row(
            "Numire CISO",
            "30 zile de la clasificare",
            "Notificare către DNSC"
        )
        req_table.add_row(
            "Evaluare risc ENIRE",
            "60 zile de la clasificare",
            "Portal DNSC"
        )
        req_table.add_row(
            "Raportare incidente",
            "24 ore (semnificativ)",
            "CSIRT-RO / DNSC"
        )
        req_table.add_row(
            "Certificare CyFun",
            "18 luni de la clasificare",
 "Auditor acreditat DNSC"
        )
        req_table.add_row(
            "Audit anual",
            "Anual",
            "Auditor acreditat DNSC"
        )
        
        console.print(req_table)
    
    # Next audit date
    console.print(f"\n[dim]📅 Următorul audit programat: {result.data_urmator_audit}[/dim]")
    
    # Legal basis footer
    console.print(f"\n[dim]📚 Bază legală:[/dim]")
    for lege in result.baza_legala:
        console.print(f"  • {lege}")
    
    # DNSC Contact
    console.print("\n[dim]📞 Contact DNSC: www.dnsic.ro | nis2@dnsic.ro | Tel: 021 316 10 00[/dim]")


def display_gap_result(result: dict):
    """Display gap analysis result."""
    gap = result.get("gap_analysis", {})
    
    mode = gap.get("mode", "unknown")
    maturity = gap.get("overall_maturity", 0)
    readiness = gap.get("compliance_readiness", 0)
    
    console.print(f"\n[bold]Gap Analysis ({mode}):[/bold]")
    console.print(f"  Overall Maturity: {maturity}/5")
    console.print(f"  Compliance Readiness: {readiness:.1f}%")
    console.print(f"  Estimated Timeline: {gap.get('estimated_timeline', 'N/A')}")
    
    # Domain scores
    domain_scores = gap.get("domain_scores", {})
    if domain_scores:
        table = Table(title="Domain Maturity", box=box.ROUNDED)
        table.add_column("Domain", style="cyan")
        table.add_column("Score", style="green")
        
        for domain, score in domain_scores.items():
            table.add_row(domain, f"{score}/5")
        
        console.print(table)
    
    # Gaps
    gaps = gap.get("gaps", [])
    if gaps:
        console.print(f"\n[bold]Identified Gaps:[/bold] {len(gaps)}")
        for g in gaps[:5]:
            console.print(f"  • {g.get('gap_id')}: {g.get('description', 'N/A')[:60]}...")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="NIS2 Compliance Assessment System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py classify --mock 1
  python main.py audit --mock EE-ENERGY-001 --output audit.json
  python main.py gap --mock 2 --mode quick_scan
  python main.py interactive
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Classify command
    classify_parser = subparsers.add_parser("classify", help="Classify an entity")
    classify_parser.add_argument("--mock", help="Use mock entity (ID or number)")
    classify_parser.add_argument("--output", "-o", help="Output file (JSON)")
    
    # Audit command
    audit_parser = subparsers.add_parser("audit", help="Run full audit")
    audit_parser.add_argument("--mock", help="Use mock entity (ID or number)")
    audit_parser.add_argument("--output", "-o", help="Output file (JSON)")
    
    # Gap command
    gap_parser = subparsers.add_parser("gap", help="Run gap analysis")
    gap_parser.add_argument("--mock", help="Use mock entity (ID or number)")
    gap_parser.add_argument("--mode", choices=["quick_scan", "deep_dive"], default="deep_dive")
    gap_parser.add_argument("--output", "-o", help="Output file (JSON)")
    
    # Interactive command
    interactive_parser = subparsers.add_parser("interactive", help="Start interactive mode")
    
    # List mocks command
    list_parser = subparsers.add_parser("list-mocks", help="List available mock entities")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    try:
        if args.command == "classify":
            cmd_classify(args)
        elif args.command == "audit":
            cmd_audit(args)
        elif args.command == "gap":
            cmd_gap(args)
        elif args.command == "interactive":
            cmd_interactive(args)
        elif args.command == "list-mocks":
            print_banner()
            console.print("\n[bold]Available Mock Entities:[/bold]")
            table = Table(box=box.ROUNDED)
            table.add_column("#", style="dim")
            table.add_column("ID", style="cyan")
            table.add_column("Name", style="green")
            table.add_column("Sector", style="yellow")
            table.add_column("Employees")
            table.add_column("Turnover (EUR)")
            
            for i, entity in enumerate(ALL_MOCK_ENTITIES, 1):
                table.add_row(
                    str(i),
                    entity.entity_id,
                    entity.legal_name,
                    entity.sector,
                    str(entity.employee_count),
                    f"{entity.annual_turnover_eur:,.0f}"
                )
            
            console.print(table)
        else:
            parser.print_help()
    except Exception as e:
        console.print(f"\n[red]Error:[/red] {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
