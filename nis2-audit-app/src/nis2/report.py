"""
Report generation functions.
"""
from datetime import datetime
from .models import EntityClassification, AuditResult, GapAnalysis


def generate_markdown_report(
    classification: EntityClassification,
    audit: AuditResult | None = None,
    gap_analysis: GapAnalysis | None = None
) -> str:
    """
    Generate a Markdown compliance report.
    
    Args:
        classification: Entity classification
        audit: Optional audit result
        gap_analysis: Optional gap analysis
        
    Returns:
        Markdown report string
    """
    lines = [
        "# NIS2 Compliance Assessment Report",
        "",
        f"**Entity ID:** {classification.entity_id}",
        f"**Generated:** {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}",
        "",
        "## Entity Classification",
        "",
        f"| Attribute | Value |",
        f"|-----------|-------|",
        f"| **Classification** | {classification.classification} |",
        f"| **Legal Basis** | {classification.legal_basis} |",
        f"| **Annex** | {classification.annex or 'N/A'} |",
        f"| **Sector** | {classification.sector_classification} |",
        f"| **Lead Authority** | {classification.lead_authority} |",
        f"| **Confidence** | {classification.confidence_score * 100:.0f}% |",
        "",
        "### Reasoning",
        "",
    ]
    
    for reason in classification.reasoning_chain:
        lines.append(f"- {reason}")
    
    lines.append("")
    
    # Add audit results if available
    if audit:
        lines.extend([
            "## Audit Results",
            "",
            f"**Overall Score:** {audit.overall_score:.1f}%",
            f"**Rating:** {audit.rating}",
            "",
            "### Domain Scores",
            "",
            f"| Domain | Score |",
            f"|--------|-------|",
        ])
        
        for domain, score in audit.domain_scores.items():
            lines.append(f"| {domain.replace('_', ' ').title()} | {score:.1f}% |")
        
        lines.extend(["", "### Findings", ""])
        
        if audit.findings:
            for finding in audit.findings:
                lines.extend([
                    f"#### {finding.id} ({finding.severity})",
                    "",
                    f"**Domain:** {finding.domain.replace('_', ' ').title()}",
                    f"**Description:** {finding.description}",
                    f"**Article:** {finding.article_reference}",
                    f"**Recommendation:** {finding.recommendation}",
                    "",
                ])
        else:
            lines.append("No findings identified.")
        
        lines.append("")
    
    # Add gap analysis if available
    if gap_analysis:
        lines.extend([
            "## Gap Analysis",
            "",
            f"**Mode:** {gap_analysis.mode}",
            f"**Overall Maturity:** {gap_analysis.overall_maturity:.1f}/5.0",
            f"**Compliance Readiness:** {gap_analysis.compliance_readiness:.0f}%",
            f"**Estimated Timeline:** {gap_analysis.estimated_timeline}",
            "",
        ])
        
        if gap_analysis.gaps:
            lines.extend([
                "### Identified Gaps",
                "",
                f"| ID | Article | Description | Priority | Effort (days) |",
                f"|----|---------|-------------|----------|---------------|",
            ])
            
            for gap in gap_analysis.gaps:
                lines.append(
                    f"| {gap.gap_id} | {gap.article} | {gap.description[:40]}... | "
                    f"{gap.priority} | {gap.estimated_effort_days} |"
                )
            
            lines.append("")
    
    lines.extend([
        "---",
        "",
        "*This report is for assessment purposes under Directive (EU) 2022/2555 (NIS2).*",
        "*It does not constitute legal advice.*",
    ])
    
    return "\n".join(lines)


def generate_json_report(
    classification: EntityClassification,
    audit: AuditResult | None = None,
    gap_analysis: GapAnalysis | None = None
) -> dict:
    """
    Generate a JSON report.
    
    Args:
        classification: Entity classification
        audit: Optional audit result
        gap_analysis: Optional gap analysis
        
    Returns:
        Report as dictionary
    """
    report = {
        "entity_id": classification.entity_id,
        "generated_at": datetime.utcnow().isoformat(),
        "classification": {
            "type": classification.classification,
            "legal_basis": classification.legal_basis,
            "annex": classification.annex,
            "sector": classification.sector_classification,
            "lead_authority": classification.lead_authority,
            "confidence": classification.confidence_score,
            "reasoning": classification.reasoning_chain
        }
    }
    
    if audit:
        report["audit"] = {
            "score": audit.overall_score,
            "rating": audit.rating,
            "domain_scores": audit.domain_scores,
            "findings": [
                {
                    "id": f.id,
                    "domain": f.domain,
                    "severity": f.severity,
                    "description": f.description,
                    "article": f.article_reference,
                    "recommendation": f.recommendation
                }
                for f in audit.findings
            ]
        }
    
    if gap_analysis:
        report["gap_analysis"] = {
            "mode": gap_analysis.mode,
            "maturity": gap_analysis.overall_maturity,
            "readiness": gap_analysis.compliance_readiness,
            "timeline": gap_analysis.estimated_timeline,
            "gaps": [
                {
                    "id": g.gap_id,
                    "article": g.article,
                    "description": g.description,
                    "priority": g.priority,
                    "effort_days": g.estimated_effort_days
                }
                for g in gap_analysis.gaps
            ]
        }
    
    return report


def generate_executive_summary(
    classification: EntityClassification,
    audit: AuditResult | None = None
) -> str:
    """
    Generate a brief executive summary.
    
    Args:
        classification: Entity classification
        audit: Optional audit result
        
    Returns:
        Summary string
    """
    summary = [
        f"Entity {classification.entity_id} is classified as a {classification.classification} under NIS2.",
        ""
    ]
    
    if classification.classification == "Essential Entity":
        summary.append("As an Essential Entity, the organization must comply with the full requirements of Article 21.")
    elif classification.classification == "Important Entity":
        summary.append("As an Important Entity, the organization must comply with Article 21 requirements, with some flexibility.")
    else:
        summary.append("The entity does not qualify under NIS2 size thresholds but should monitor for national designation.")
    
    if audit:
        summary.extend([
            f"",
            f"Current compliance rating: {audit.rating} ({audit.overall_score:.0f}%)",
            f"Total findings: {len(audit.findings)}",
            f"Critical/High findings: {len([f for f in audit.findings if f.severity in ('Critical', 'High')])}"
        ])
    
    return "\n".join(summary)
