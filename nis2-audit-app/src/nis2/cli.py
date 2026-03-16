#!/usr/bin/env python3
"""
NIS2 Compliance Assessment CLI.
"""
import argparse
import json
import sys
from typing import Optional

from .models import EntityInput, CrossBorderInfo
from .classifier import classify_entity, check_national_designation
from .audit import run_audit, run_gap_analysis
from .report import generate_markdown_report, generate_json_report


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="NIS2 Compliance Assessment Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m nis2 classify --name "Example Corp" --sector energy --employees 150 --turnover 25000000
  python -m nis2 audit --entity-file entity.json
  python -m nis2 gap --entity-file entity.json
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # Classify command
    classify_parser = subparsers.add_parser("classify", help="Classify an entity")
    classify_parser.add_argument("--name", required=True, help="Legal entity name")
    classify_parser.add_argument("--sector", required=True, help="Sector (e.g., energy, banking, health)")
    classify_parser.add_argument("--employees", type=int, required=True, help="Employee count")
    classify_parser.add_argument("--turnover", type=float, required=True, help="Annual turnover (EUR)")
    classify_parser.add_argument("--balance", type=float, default=0, help="Balance sheet total (EUR)")
    classify_parser.add_argument("--country", default="RO", help="Main country code (ISO-3166)")
    classify_parser.add_argument("--output", "-o", help="Output file (JSON)")
    
    # Audit command
    audit_parser = subparsers.add_parser("audit", help="Run compliance audit")
    audit_parser.add_argument("--entity-file", required=True, help="JSON file with entity data")
    audit_parser.add_argument("--output", "-o", help="Output file")
    audit_parser.add_argument("--format", choices=["markdown", "json"], default="markdown")
    
    # Gap command
    gap_parser = subparsers.add_parser("gap", help="Run gap analysis")
    gap_parser.add_argument("--entity-file", required=True, help="JSON file with entity data")
    gap_parser.add_argument("--mode", choices=["quick_scan", "deep_dive"], default="quick_scan")
    gap_parser.add_argument("--output", "-o", help="Output file")
    
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
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_classify(args):
    """Handle classify command."""
    entity = EntityInput(
        entity_id=None,
        legal_name=args.name,
        sector=args.sector,
        employee_count=args.employees,
        annual_turnover_eur=args.turnover,
        balance_sheet_total=args.balance,
        cross_border_operations=CrossBorderInfo(
            operates_cross_border=False,
            main_establishment=args.country
        )
    )
    
    result = classify_entity(entity)
    
    print(f"\n{'='*60}")
    print(f"NIS2 Entity Classification")
    print(f"{'='*60}")
    print(f"Entity: {args.name}")
    print(f"Classification: {result.classification}")
    print(f"Legal Basis: {result.legal_basis}")
    print(f"Annex: {result.annex or 'N/A'}")
    print(f"Lead Authority: {result.lead_authority}")
    print(f"Confidence: {result.confidence_score * 100:.0f}%")
    print(f"\nReasoning:")
    for reason in result.reasoning_chain:
        print(f"  • {reason}")
    
    # Check national designation
    national = check_national_designation(entity)
    if national["applicable"]:
        print(f"\n⚠️  {national['reason']}")
        print(f"   Action: {national['action_required']}")
    
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(result.model_dump(), f, indent=2)
        print(f"\n✓ Saved to {args.output}")


def cmd_audit(args):
    """Handle audit command."""
    entity, classification = load_entity_file(args.entity_file)
    
    print(f"\nRunning NIS2 compliance audit for {entity.legal_name}...")
    
    audit_result = run_audit(entity, classification)
    
    if args.format == "markdown":
        report = generate_markdown_report(classification, audit=audit_result)
    else:
        report = json.dumps(
            generate_json_report(classification, audit=audit_result),
            indent=2
        )
    
    if args.output:
        with open(args.output, 'w') as f:
            f.write(report)
        print(f"✓ Report saved to {args.output}")
    else:
        print("\n" + report)


def cmd_gap(args):
    """Handle gap command."""
    entity, classification = load_entity_file(args.entity_file)
    
    print(f"\nRunning {args.mode} gap analysis for {entity.legal_name}...")
    
    gap_result = run_gap_analysis(entity, classification, mode=args.mode)
    
    print(f"\n{'='*60}")
    print(f"Gap Analysis Results")
    print(f"{'='*60}")
    print(f"Mode: {gap_result.mode}")
    print(f"Overall Maturity: {gap_result.overall_maturity:.1f}/5.0")
    print(f"Compliance Readiness: {gap_result.compliance_readiness:.0f}%")
    print(f"Estimated Timeline: {gap_result.estimated_timeline}")
    
    if gap_result.gaps:
        print(f"\nIdentified Gaps:")
        for gap in gap_result.gaps:
            print(f"  [{gap.priority}] {gap.gap_id}: {gap.description[:50]}...")
    
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(gap_result.model_dump(), f, indent=2)
        print(f"\n✓ Saved to {args.output}")


def load_entity_file(filepath: str) -> tuple[EntityInput, any]:
    """Load entity from JSON file."""
    import json
    
    with open(filepath) as f:
        data = json.load(f)
    
    entity = EntityInput(**data)
    classification = classify_entity(entity)
    
    return entity, classification


if __name__ == "__main__":
    main()
