"""
Pydantic schemas for Entity data.
"""
from datetime import datetime
from typing import Literal, Optional
from pydantic import BaseModel, Field, field_validator


class Address(BaseModel):
    """Physical address model."""
    street: str
    city: str
    postal_code: str
    country: str = Field(..., pattern=r"^[A-Z]{2}$")  # ISO-3166 alpha-2
    
    
class SizeDetails(BaseModel):
    """Enterprise size details."""
    employee_count: int
    annual_turnover_eur: float
    balance_sheet_total: Optional[float] = None
    
    @property
    def is_medium_enterprise(self) -> bool:
        """Check if meets medium enterprise threshold."""
        return (
            50 <= self.employee_count <= 249 and
            (self.annual_turnover_eur >= 10_000_000 or
             (self.balance_sheet_total and self.balance_sheet_total >= 10_000_000))
        )
    
    @property
    def is_large_enterprise(self) -> bool:
        """Check if meets large enterprise threshold."""
        return (
            self.employee_count >= 250 and
            (self.annual_turnover_eur >= 50_000_000 or
             (self.balance_sheet_total and self.balance_sheet_total >= 43_000_000))
        )


class CrossBorderInfo(BaseModel):
    """Cross-border operation details."""
    operates_cross_border: bool
    member_states: list[str] = Field(default_factory=list)  # ISO-3166 alpha-2
    main_establishment: Optional[str] = None
    decision_location: Optional[str] = None
    majority_employees_location: Optional[str] = None
    highest_turnover_location: Optional[str] = None


class EntityInput(BaseModel):
    """Input data for entity classification."""
    entity_id: Optional[str] = None
    legal_name: str
    sector: str
    annual_turnover_eur: float
    employee_count: int
    balance_sheet_total: Optional[float] = None
    service_scope: list[str] = Field(default_factory=list)
    cross_border_operations: CrossBorderInfo
    is_public_admin: bool = False
    is_trust_service_provider: bool = False
    is_tld_registry: bool = False
    is_dns_provider: bool = False
    
    @property
    def size_details(self) -> SizeDetails:
        return SizeDetails(
            employee_count=self.employee_count,
            annual_turnover_eur=self.annual_turnover_eur,
            balance_sheet_total=self.balance_sheet_total
        )


class EntityClassification(BaseModel):
    """Classification result for an entity."""
    entity_id: str
    classification: Literal["Essential Entity", "Important Entity", "Non-Qualifying"]
    legal_basis: str
    annex: Literal["Annex I", "Annex II", None] = None
    sector_classification: str
    size_qualification: bool
    size_details: SizeDetails
    cross_border: CrossBorderInfo
    lead_authority: str  # Member State code
    confidence_score: float = Field(..., ge=0.0, le=1.0)
    edge_cases: list[str] = Field(default_factory=list)
    reasoning_chain: list[str] = Field(default_factory=list)
    classified_at: datetime = Field(default_factory=datetime.utcnow)
    
    @field_validator('confidence_score')
    @classmethod
    def validate_confidence(cls, v: float) -> float:
        if not 0.0 <= v <= 1.0:
            raise ValueError("Confidence score must be between 0.0 and 1.0")
        return round(v, 2)


class ComplianceHistory(BaseModel):
    """Historical compliance record."""
    previous_violations: int = 0
    last_violation_date: Optional[datetime] = None
    cooperation_level: Literal["excellent", "good", "satisfactory", "poor"] = "satisfactory"
    remediation_timeliness: float = 0.0  # Percentage on-time


class SanctionRecord(BaseModel):
    """Record of previous sanctions."""
    sanction_id: str
    date: datetime
    type: Literal["warning", "fine", "restriction"]
    amount_eur: Optional[float] = None
    articles_violated: list[str]
    status: Literal["active", "completed", "appealed"]


class AuditHistory(BaseModel):
    """Record of previous audits."""
    audit_id: str
    date: datetime
    rating: Literal["Compliant", "Substantially Compliant", "Partially Compliant", "Non-Compliant"]
    score: float
    key_findings: list[str]


class EntityProfile(BaseModel):
    """Complete entity profile."""
    entity_id: str
    legal_name: str
    trading_names: list[str] = Field(default_factory=list)
    registration_number: Optional[str] = None
    legal_address: Address
    operational_addresses: list[Address] = Field(default_factory=list)
    
    # Classification
    primary_sector: str
    secondary_sectors: list[str] = Field(default_factory=list)
    classification: Literal["EE", "IE", "Non-Qualifying"]
    annex: Literal["Annex_I", "Annex_II", None] = None
    
    # Size
    employee_count: int
    annual_turnover_eur: float
    balance_sheet_total: Optional[float] = None
    
    # Operations
    member_states: list[str] = Field(default_factory=list)
    main_establishment: str
    cross_border_operations: bool = False
    lead_authority: str
    
    # History
    previous_audits: list[AuditHistory] = Field(default_factory=list)
    compliance_history: ComplianceHistory = Field(default_factory=ComplianceHistory)
    sanctions_history: list[SanctionRecord] = Field(default_factory=list)
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    version: int = 1
