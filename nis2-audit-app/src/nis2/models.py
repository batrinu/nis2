"""
Pydantic models for NIS2 compliance assessment.
"""
from datetime import datetime
from typing import Literal, Optional
from pydantic import BaseModel, Field


class CrossBorderInfo(BaseModel):
    """Cross-border operation details."""
    operates_cross_border: bool = False
    member_states: list[str] = Field(default_factory=list)
    main_establishment: Optional[str] = None


class EntityInput(BaseModel):
    """Input data for entity classification."""
    entity_id: Optional[str] = None
    legal_name: str
    sector: str
    annual_turnover_eur: float
    employee_count: int
    balance_sheet_total: Optional[float] = None
    cross_border_operations: CrossBorderInfo = Field(default_factory=CrossBorderInfo)
    is_public_admin: bool = False
    is_trust_service_provider: bool = False
    is_tld_registry: bool = False
    is_dns_provider: bool = False


class EntityClassification(BaseModel):
    """Classification result."""
    entity_id: str
    classification: Literal["Essential Entity", "Important Entity", "Non-Qualifying"]
    legal_basis: str
    annex: Literal["Annex I", "Annex II", None] = None
    sector_classification: str
    size_qualification: bool
    lead_authority: str
    confidence_score: float = Field(..., ge=0.0, le=1.0)
    reasoning_chain: list[str] = Field(default_factory=list)


class Finding(BaseModel):
    """Audit finding."""
    id: str
    domain: str
    title: str
    description: str
    severity: Literal["Critical", "High", "Medium", "Low"]
    article_reference: str
    recommendation: str


class AuditResult(BaseModel):
    """Audit assessment result."""
    entity_id: str
    overall_score: float
    rating: Literal["Compliant", "Substantially Compliant", "Partially Compliant", "Non-Compliant"]
    findings: list[Finding] = Field(default_factory=list)
    domain_scores: dict[str, float] = Field(default_factory=dict)


class GapItem(BaseModel):
    """Identified compliance gap."""
    gap_id: str
    article: str
    description: str
    priority: Literal["High", "Medium", "Low"]
    estimated_effort_days: int


class GapAnalysis(BaseModel):
    """Gap analysis result."""
    entity_id: str
    mode: Literal["quick_scan", "deep_dive"]
    overall_maturity: float
    compliance_readiness: float
    gaps: list[GapItem] = Field(default_factory=list)
    estimated_timeline: str = ""
