"""
Pydantic models for audit findings and gaps.
"""
from datetime import datetime, timezone
from typing import Literal, Optional
from pydantic import BaseModel, Field


class AuditFinding(BaseModel):
    """An audit finding/gap identified during assessment."""
    finding_id: str = Field(default_factory=lambda: f"FIND-{datetime.now(timezone.utc).timestamp()}", max_length=64)
    session_id: str = Field(..., max_length=64)
    
    # Finding details
    title: str = Field(..., max_length=255)
    description: str = Field(..., max_length=10000)
    severity: Literal["critical", "high", "medium", "low", "info"] = "medium"
    
    # NIS2 mapping
    nis2_article: Optional[str] = Field(None, max_length=50)
    nis2_domain: Optional[str] = Field(None, max_length=100)
    
    # Evidence
    evidence: str = Field("", max_length=10000)
    device_ids: list[str] = Field(default_factory=list)  # Related devices
    config_snippets: list[str] = Field(default_factory=list)  # Relevant config
    
    # Remediation
    recommendation: str = Field("", max_length=5000)
    remediation_steps: list[str] = Field(default_factory=list)
    estimated_effort: Optional[str] = Field(None, max_length=50)
    
    # Status
    status: Literal["open", "in_progress", "resolved", "accepted_risk"] = "open"
    resolved_at: Optional[datetime] = None
    resolved_by: Optional[str] = Field(None, max_length=100)
    
    # Metadata
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    created_by: str = Field("system", max_length=100)


class GapScore(BaseModel):
    """Score for a specific NIS2 domain."""
    domain: str
    score: float = Field(..., ge=0.0, le=100.0)
    weight: float = Field(..., ge=0.0, le=1.0)
    weighted_score: float = Field(..., ge=0.0, le=100.0)
    findings_count: int = 0


class ComplianceScore(BaseModel):
    """Overall compliance scoring breakdown."""
    session_id: str
    overall_score: float = Field(..., ge=0.0, le=100.0)
    rating: Literal["Compliant", "Substantially Compliant", "Partially Compliant", "Non-Compliant"]
    
    # Domain scores
    governance_score: GapScore
    technical_controls_score: GapScore
    incident_response_score: GapScore
    supply_chain_score: GapScore
    documentation_score: GapScore
    management_oversight_score: GapScore
    
    # Summary
    total_findings: int = 0
    critical_findings: int = 0
    high_findings: int = 0
    medium_findings: int = 0
    low_findings: int = 0
    
    calculated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
