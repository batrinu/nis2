"""
NIS2 Audit functions.
"""
from datetime import datetime
from typing import Literal
from .models import EntityInput, EntityClassification, AuditResult, Finding
from .knowledge_base import AUDIT_CHECKLIST


def run_audit(
    entity: EntityInput,
    classification: EntityClassification,
    checklist_responses: dict[str, bool] | None = None
) -> AuditResult:
    """
    Run NIS2 compliance audit.
    
    Args:
        entity: Entity being audited
        classification: Classification result
        checklist_responses: Optional pre-filled checklist responses
        
    Returns:
        Audit result
    """
    if checklist_responses is None:
        # Simulate audit with some findings based on entity type
        checklist_responses = _simulate_checklist_responses(classification)
    
    # Calculate domain scores
    domain_scores = {}
    findings = []
    
    for domain, items in AUDIT_CHECKLIST.items():
        score = 0.0
        for item in items:
            key = f"{domain}:{item['id']}"
            if checklist_responses.get(key, False):
                score += 1.0
            else:
                # Create finding for missing control
                severity = _determine_severity(domain, classification)
                findings.append(Finding(
                    id=item['id'],
                    domain=domain,
                    title=f"Missing: {item['text'][:50]}...",
                    description=f"Control not implemented: {item['text']}",
                    severity=severity,
                    article_reference=item['article'],
                    recommendation=f"Implement {item['text'].lower()}"
                ))
        
        domain_scores[domain] = score / len(items) if items else 0.0
    
    # Calculate overall score
    overall = sum(domain_scores.values()) / len(domain_scores) if domain_scores else 0.0
    
    # Determine rating
    rating = _score_to_rating(overall, classification)
    
    return AuditResult(
        entity_id=entity.entity_id or "unknown",
        overall_score=round(overall * 100, 1),
        rating=rating,
        findings=findings,
        domain_scores={k: round(v * 100, 1) for k, v in domain_scores.items()}
    )


def _simulate_checklist_responses(classification: EntityClassification) -> dict[str, bool]:
    """Simulate checklist responses based on entity type."""
    import random
    
    # Essential entities should have better scores
    if classification.classification == "Essential Entity":
        compliance_rate = 0.75
    elif classification.classification == "Important Entity":
        compliance_rate = 0.60
    else:
        compliance_rate = 0.40
    
    responses = {}
    for domain, items in AUDIT_CHECKLIST.items():
        for item in items:
            key = f"{domain}:{item['id']}"
            responses[key] = random.random() < compliance_rate
    
    return responses


def _determine_severity(
    domain: str,
    classification: EntityClassification
) -> Literal["Critical", "High", "Medium", "Low"]:
    """Determine finding severity based on domain and entity type."""
    if classification.classification == "Essential Entity":
        severities = {"governance": "High", "incident_response": "Critical",
                     "technical_controls": "High", "business_continuity": "High",
                     "supply_chain": "Medium"}
    elif classification.classification == "Important Entity":
        severities = {"governance": "High", "incident_response": "High",
                     "technical_controls": "Medium", "business_continuity": "Medium",
                     "supply_chain": "Low"}
    else:
        return "Low"
    
    return severities.get(domain, "Medium")


def _score_to_rating(
    score: float,
    classification: EntityClassification
) -> Literal["Compliant", "Substantially Compliant", "Partially Compliant", "Non-Compliant"]:
    """Convert score to compliance rating."""
    thresholds = {
        "Essential Entity": (0.90, 0.75, 0.60),
        "Important Entity": (0.85, 0.70, 0.50),
        "Non-Qualifying": (0.80, 0.60, 0.40)
    }
    
    compliant, substantial, partial = thresholds.get(
        classification.classification, 
        (0.85, 0.70, 0.50)
    )
    
    if score >= compliant:
        return "Compliant"
    elif score >= substantial:
        return "Substantially Compliant"
    elif score >= partial:
        return "Partially Compliant"
    else:
        return "Non-Compliant"


def run_gap_analysis(
    entity: EntityInput,
    classification: EntityClassification,
    mode: Literal["quick_scan", "deep_dive"] = "quick_scan"
) -> dict:
    """
    Run gap analysis against NIS2 requirements.
    
    Args:
        entity: Entity being analyzed
        classification: Classification result
        mode: Analysis depth
        
    Returns:
        Gap analysis results
    """
    from .models import GapItem, GapAnalysis
    
    # Simulate gap findings
    gaps = []
    if classification.classification == "Essential Entity":
        gaps = [
            GapItem(gap_id="GAP-001", article="21(2)(a)", 
                   description="Risk analysis documentation incomplete",
                   priority="High", estimated_effort_days=30),
            GapItem(gap_id="GAP-002", article="21(2)(b)",
                   description="Incident response procedures not tested",
                   priority="High", estimated_effort_days=14),
        ]
        maturity = 3.5
        readiness = 65.0
        timeline = "6-9 months"
    elif classification.classification == "Important Entity":
        gaps = [
            GapItem(gap_id="GAP-001", article="21(2)(a)",
                   description="Risk analysis needs update",
                   priority="Medium", estimated_effort_days=14),
        ]
        maturity = 2.8
        readiness = 45.0
        timeline = "9-12 months"
    else:
        maturity = 2.0
        readiness = 25.0
        timeline = "12-18 months"
    
    return GapAnalysis(
        entity_id=entity.entity_id or "unknown",
        mode=mode,
        overall_maturity=maturity,
        compliance_readiness=readiness,
        gaps=gaps,
        estimated_timeline=timeline
    )


def generate_remediation_plan(findings: list[Finding]) -> list[dict]:
    """
    Generate remediation plan from findings.
    
    Args:
        findings: List of audit findings
        
    Returns:
        Prioritized remediation actions
    """
    priority_order = {"Critical": 0, "High": 1, "Medium": 2, "Low": 3}
    
    sorted_findings = sorted(findings, key=lambda f: priority_order.get(f.severity, 99))
    
    plan = []
    for finding in sorted_findings:
        timeline = {
            "Critical": "Immediate (30 days)",
            "High": "Short-term (90 days)",
            "Medium": "Medium-term (6 months)",
            "Low": "Long-term (12 months)"
        }.get(finding.severity, "TBD")
        
        plan.append({
            "finding_id": finding.id,
            "priority": finding.severity,
            "action": finding.recommendation,
            "timeline": timeline,
            "article": finding.article_reference
        })
    
    return plan
