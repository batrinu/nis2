"""
Pydantic schemas for Sanctions and Enforcement.
"""
from datetime import date, datetime
from typing import Literal, Optional
from pydantic import BaseModel, Field


class Violation(BaseModel):
    """Specific violation record."""
    violation_id: str
    article_violated: str
    description: str
    severity: Literal["critical", "high", "medium", "low"]
    evidence_references: list[str] = Field(default_factory=list)
    

class FineCalculation(BaseModel):
    """Detailed fine calculation."""
    proposed_fine_eur: float
    maximum_possible: float
    percentage_of_max: float
    calculation_breakdown: dict
    
    @property
    def is_capped(self) -> bool:
        return self.proposed_fine_eur >= self.maximum_possible


class Sanction(BaseModel):
    """Individual sanction."""
    sanction_type: Literal[
        "verbal_warning",
        "written_warning", 
        "formal_notice",
        "fine",
        "operational_restriction",
        "public_disclosure",
        "criminal_referral"
    ]
    amount_eur: Optional[float] = None
    description: str
    conditions: list[str] = Field(default_factory=list)
    deadline: Optional[date] = None


class RemediationPlan(BaseModel):
    """Required remediation plan."""
    mandatory_actions: list[dict]
    deadline: date
    verification_requirements: str
    progress_reporting_frequency: str = "monthly"


class AppealRights(BaseModel):
    """Appeal process information."""
    appeal_deadline: date
    appeal_procedure: str
    appeal_authority: str
    stay_of_execution: bool = False


class ProportionalityFactors(BaseModel):
    """Factors considered for proportionality."""
    gravity: float = Field(..., ge=0.0, le=1.0)
    duration: float = Field(..., ge=0.0, le=1.0)
    intentionality: float = Field(..., ge=0.0, le=1.0)
    harm_caused: float = Field(..., ge=0.0, le=1.0)
    cooperation: float = Field(..., ge=0.0, le=1.0)
    previous_compliance: float = Field(..., ge=0.0, le=1.0)
    cross_border_impact: float = Field(..., ge=0.0, le=1.0)
    sector_criticality: float = Field(..., ge=0.0, le=1.0)
    public_interest: float = Field(..., ge=0.0, le=1.0)


class ProportionalityAssessment(BaseModel):
    """Proportionality assessment result."""
    severity_score: float
    sanction_tier: Literal["warning", "notice", "moderate_fine", "severe_fine", "maximum"]
    factors: ProportionalityFactors
    reasoning: str
    legal_basis: str = "Article 34(2)"


class SanctionNotice(BaseModel):
    """Formal sanction notice structure."""
    notice_id: str
    issue_date: datetime
    effective_date: datetime
    competent_authority: str
    
    # Recipient
    entity_name: str
    entity_classification: str
    entity_address: str
    
    # Violations
    violations: list[Violation]
    
    # Legal basis
    legal_basis: str
    national_law: Optional[str] = None
    
    # Sanctions
    sanctions: list[Sanction]
    fine_calculation: Optional[FineCalculation] = None
    
    # Remediation
    remediation_requirements: RemediationPlan
    
    # Proportionality
    proportionality_assessment: ProportionalityAssessment
    
    # Appeal
    appeal_rights: AppealRights
    
    # Disclosure
    public_notification_required: bool
    notification_date: Optional[date] = None
    disclosure_scope: Optional[str] = None
    
    # Signatures
    investigating_officer: str
    legal_review: str
    authority_head: str
    
    created_at: datetime = Field(default_factory=datetime.utcnow)


class SanctionPackage(BaseModel):
    """Package of sanctions for an entity."""
    entity_id: str
    violations: list[Violation]
    sanctions: list[Sanction]
    proportionality: ProportionalityAssessment
    remediation: RemediationPlan
    fine_calculation: Optional[FineCalculation] = None
    red_flags_detected: list[str] = Field(default_factory=list)
