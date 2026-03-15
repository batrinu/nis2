"""
Pydantic schemas for Compliance Reports.
"""
from datetime import date, datetime
from typing import Literal, Optional
from pydantic import BaseModel, Field


class ComplianceStatus(BaseModel):
    """Status of a specific compliance requirement."""
    requirement_id: str
    article_reference: str
    description: str
    status: Literal["compliant", "partially_compliant", "non_compliant", "not_applicable"]
    evidence_references: list[str] = Field(default_factory=list)
    gaps: list[str] = Field(default_factory=list)
    remediation_required: bool = False


class DomainScore(BaseModel):
    """Score for a compliance domain."""
    domain_name: str
    weight: float = Field(..., ge=0.0, le=1.0)
    score: float = Field(..., ge=0.0, le=100.0)
    rating: Literal["Compliant", "Substantially Compliant", "Partially Compliant", "Non-Compliant"]
    requirements: list[ComplianceStatus]


class Finding(BaseModel):
    """Audit finding."""
    finding_id: str
    severity: Literal["Critical", "High", "Medium", "Low", "Informational"]
    article_reference: str
    title: str
    description: str
    evidence: list[str] = Field(default_factory=list)
    recommendation: str
    business_impact: str


class Recommendation(BaseModel):
    """Remediation recommendation."""
    recommendation_id: str
    finding_id: str
    priority: Literal["immediate", "high", "medium", "low"]
    description: str
    specific_requirement: str
    measurable_criteria: str
    deadline: Optional[date] = None
    estimated_effort_days: Optional[int] = None


class RemediationItem(BaseModel):
    """Item in a remediation roadmap."""
    item_id: str
    violation_reference: str
    description: str
    specific: str
    measurable: str
    achievable: bool = True
    relevant: str
    time_bound: date
    owner: Optional[str] = None
    resources_required: dict = Field(default_factory=dict)
    verification_method: str
    estimated_cost_eur: Optional[float] = None
    status: Literal["pending", "in_progress", "completed", "verified"] = "pending"


class ComplianceReport(BaseModel):
    """NIS2 Compliance Report structure."""
    report_id: str
    entity_id: str
    
    # Assessment metadata
    assessment_date: datetime
    assessor: str
    report_version: str = "1.0"
    
    # Classification
    entity_classification: str
    sector: str
    
    # Scores
    overall_score: float = Field(..., ge=0.0, le=100.0)
    rating: Literal["Compliant", "Substantially Compliant", "Partially Compliant", "Non-Compliant"]
    domain_scores: list[DomainScore]
    
    # Article 21 mapping
    article_21_mapping: dict[str, ComplianceStatus]
    
    # Findings and recommendations
    findings: list[Finding]
    recommendations: list[Recommendation]
    
    # Remediation roadmap
    remediation_roadmap: list[RemediationItem]
    
    # Cross-border
    cross_border_coordination: Optional[dict] = None
    
    # Timeline
    next_assessment_date: Optional[date] = None
    
    created_at: datetime = Field(default_factory=datetime.utcnow)


class GapAnalysisReport(ComplianceReport):
    """Gap analysis specific report."""
    assessment_mode: Literal["quick_scan", "deep_dive"]
    overall_maturity: int = Field(..., ge=1, le=5)
    compliance_readiness: float = Field(..., ge=0.0, le=100.0)
    estimated_timeline_to_compliance: str
    question_responses: list[dict] = Field(default_factory=list)


class AuditAssessment(ComplianceReport):
    """Full audit assessment report."""
    audit_id: str
    auditor_reference: str
    phase_results: dict[str, dict]
    evidence_references: list[str] = Field(default_factory=list)
