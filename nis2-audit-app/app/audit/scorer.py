"""
Compliance scoring for NIS2 audit results.
"""
import logging
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)
from dataclasses import dataclass

from .checklist import (
    ChecklistSection, 
    ChecklistQuestion, 
    ComplianceStatus,
    get_checklist_sections,
    calculate_domain_weight
)
from ..models import ComplianceScore, GapScore


@dataclass
class DomainScore:
    """Score for a specific domain."""
    domain: str
    weight: float
    total_questions: int
    compliant: int
    partially_compliant: int
    non_compliant: int
    not_applicable: int
    score: float


class ComplianceScorer:
    """
    Calculate compliance scores based on checklist responses.
    """
    
    # Score mapping
    SCORES = {
        ComplianceStatus.COMPLIANT: 1.0,
        ComplianceStatus.PARTIALLY_COMPLIANT: 0.5,
        ComplianceStatus.NON_COMPLIANT: 0.0,
        ComplianceStatus.NOT_APPLICABLE: None,  # Exclude from calculation
        ComplianceStatus.NOT_STARTED: 0.0,
    }
    
    # Rating thresholds
    RATING_THRESHOLDS = [
        (90, "Compliant"),
        (75, "Substantially Compliant"),
        (50, "Partially Compliant"),
        (0, "Non-Compliant"),
    ]
    
    def calculate_domain_score(self, questions: List[ChecklistQuestion]) -> DomainScore:
        """
        Calculate score for a domain.
        
        Args:
            questions: List of questions in the domain
        
        Returns:
            DomainScore
        """
        if not questions:
            return DomainScore(
                domain="unknown",
                weight=0.0,
                total_questions=0,
                compliant=0,
                partially_compliant=0,
                non_compliant=0,
                not_applicable=0,
                score=0.0
            )
        
        domain = questions[0].domain
        weight = calculate_domain_weight(domain)
        
        # Use local variables for faster lookup
        scores_map = self.SCORES
        COMPLIANT = ComplianceStatus.COMPLIANT
        PARTIALLY_COMPLIANT = ComplianceStatus.PARTIALLY_COMPLIANT
        
        total_score = 0.0
        applicable_count = 0
        compliant = 0
        partially_compliant = 0
        non_compliant = 0
        not_applicable = 0
        
        for question in questions:
            score_value = scores_map.get(question.status)
            
            if score_value is None:  # Not applicable
                not_applicable += 1
                continue
            
            applicable_count += 1
            total_score += score_value
            
            status = question.status
            if status == COMPLIANT:
                compliant += 1
            elif status == PARTIALLY_COMPLIANT:
                partially_compliant += 1
            else:
                non_compliant += 1
        
        # Calculate average score
        avg_score = (total_score / applicable_count * 100) if applicable_count > 0 else 0.0
        
        return DomainScore(
            domain=domain,
            weight=weight,
            total_questions=len(questions),
            compliant=compliant,
            partially_compliant=partially_compliant,
            non_compliant=non_compliant,
            not_applicable=not_applicable,
            score=avg_score
        )
    
    def calculate_overall_score(self, sections: List[ChecklistSection]) -> tuple[float, str]:
        """
        Calculate overall compliance score.
        
        Args:
            sections: List of checklist sections with responses
        
        Returns:
            Tuple of (score, rating)
        """
        total_weighted_score = 0.0
        total_weight = 0.0
        
        _calculate_domain_score = self.calculate_domain_score  # Local for faster lookup
        
        for section in sections:
            domain_score = _calculate_domain_score(section.questions)
            
            if domain_score.total_questions > 0:
                total_weighted_score += domain_score.score * domain_score.weight
                total_weight += domain_score.weight
        
        # Normalize if weights don't sum to 1.0
        overall_score = (total_weighted_score / total_weight) if total_weight > 0 else 0.0
        
        # Determine rating
        rating = self._get_rating(overall_score)
        
        return overall_score, rating
    
    def _get_rating(self, score: float) -> str:
        """Get compliance rating based on score."""
        # Use bisect for O(log n) lookup instead of O(n) linear search
        # Since the list is small (4 items), unroll the loop for speed
        if score >= 90:
            return "Compliant"
        if score >= 75:
            return "Substantially Compliant"
        if score >= 50:
            return "Partially Compliant"
        return "Non-Compliant"
    
    def generate_compliance_score(
        self,
        session_id: str,
        sections: List[ChecklistSection]
    ) -> ComplianceScore:
        """
        Generate full compliance score object.
        
        Args:
            session_id: Audit session ID
            sections: Checklist sections with responses
        
        Returns:
            ComplianceScore model
        """
        overall_score, rating = self.calculate_overall_score(sections)
        
        # Calculate domain scores in a single pass
        _calculate_domain_score = self.calculate_domain_score
        domain_scores = {
            section.domain: _calculate_domain_score(section.questions)
            for section in sections
        }
        
        # Count findings by severity in a single pass
        total_findings = 0
        critical_findings = 0
        high_findings = 0
        medium_findings = 0
        low_findings = 0
        
        NON_COMPLIANT = ComplianceStatus.NON_COMPLIANT
        PARTIALLY_COMPLIANT = ComplianceStatus.PARTIALLY_COMPLIANT
        
        for section in sections:
            for q in section.questions:
                status = q.status
                if status == NON_COMPLIANT:
                    total_findings += 1
                    high_findings += 1  # Non-compliant = high
                elif status == PARTIALLY_COMPLIANT:
                    total_findings += 1
                    medium_findings += 1  # Partial = medium
        
        # Create GapScore objects for each domain - inlined for performance
        domains = ("governance", "technical_controls", "incident_response", 
                   "supply_chain", "documentation", "management_oversight")
        
        gap_scores = []
        for domain in domains:
            ds = domain_scores.get(domain)
            if ds:
                gap_scores.append(GapScore(
                    domain=domain,
                    score=ds.score,
                    weight=ds.weight,
                    weighted_score=ds.score * ds.weight,
                    findings_count=ds.non_compliant + ds.partially_compliant
                ))
            else:
                gap_scores.append(GapScore(
                    domain=domain,
                    score=0.0,
                    weight=calculate_domain_weight(domain),
                    weighted_score=0.0,
                    findings_count=0
                ))
        
        return ComplianceScore(
            session_id=session_id,
            overall_score=overall_score,
            rating=rating,  # type: ignore
            governance_score=gap_scores[0],
            technical_controls_score=gap_scores[1],
            incident_response_score=gap_scores[2],
            supply_chain_score=gap_scores[3],
            documentation_score=gap_scores[4],
            management_oversight_score=gap_scores[5],
            total_findings=total_findings,
            critical_findings=critical_findings,
            high_findings=high_findings,
            medium_findings=medium_findings,
            low_findings=low_findings,
        )
    
    def get_score_breakdown(self, sections: List[ChecklistSection]) -> Dict:
        """
        Get detailed score breakdown.
        
        Args:
            sections: Checklist sections
        
        Returns:
            Dict with detailed scoring information
        """
        overall_score, rating = self.calculate_overall_score(sections)
        
        _calculate_domain_score = self.calculate_domain_score
        domain_breakdown = [
            {
                "domain": ds.domain,
                "title": section.title,
                "weight": ds.weight,
                "score": round(ds.score, 1),
                "weighted_score": round(ds.score * ds.weight, 1),
                "questions": ds.total_questions,
                "compliant": ds.compliant,
                "partially_compliant": ds.partially_compliant,
                "non_compliant": ds.non_compliant,
                "not_applicable": ds.not_applicable,
            }
            for section in sections
            for ds in [_calculate_domain_score(section.questions)]
        ]
        
        return {
            "overall_score": round(overall_score, 1),
            "rating": rating,
            "domains": domain_breakdown,
        }


def format_score_report(score: ComplianceScore) -> str:
    """
    Format a compliance score as a readable report.
    
    Args:
        score: ComplianceScore to format
    
    Returns:
        Formatted string
    """
    lines = [
        "NIS2 Compliance Score Report",
        "=" * 50,
        "",
        f"Overall Score: {score.overall_score:.1f}%",
        f"Rating: {score.rating}",
        "",
        "Domain Breakdown:",
        "-" * 50,
    ]
    
    domains = [
        ("Governance", score.governance_score),
        ("Technical Controls", score.technical_controls_score),
        ("Incident Response", score.incident_response_score),
        ("Supply Chain", score.supply_chain_score),
        ("Documentation", score.documentation_score),
        ("Management Oversight", score.management_oversight_score),
    ]
    
    for name, domain_score in domains:
        lines.append(
            f"  {name:20} {domain_score.score:5.1f}% "
            f"(weight: {domain_score.weight:.0%})"
        )
    
    lines.extend([
        "",
        "Findings Summary:",
        "-" * 50,
        f"  Total Findings: {score.total_findings}",
        f"  Critical: {score.critical_findings}",
        f"  High: {score.high_findings}",
        f"  Medium: {score.medium_findings}",
        f"  Low: {score.low_findings}",
    ])
    
    return "\n".join(lines)
