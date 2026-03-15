"""
Pydantic models for Entity data in the NIS2 Field Audit App.
Adapted from the core shared schemas.
"""
from datetime import datetime
from typing import Literal, Optional
from pydantic import BaseModel, Field


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
    
    @property
    def qualifies(self) -> bool:
        """Check if qualifies as medium or large enterprise."""
        return self.is_medium_enterprise or self.is_large_enterprise


class CrossBorderInfo(BaseModel):
    """Cross-border operation details."""
    operates_cross_border: bool = False
    member_states: list[str] = Field(default_factory=list)  # ISO-3166 alpha-2
    main_establishment: Optional[str] = None
    decision_location: Optional[str] = None
    majority_employees_location: Optional[str] = None
    highest_turnover_location: Optional[str] = None


class EntityInput(BaseModel):
    """Input data for entity classification."""
    entity_id: Optional[str] = Field(None, max_length=64)
    legal_name: str = Field(..., max_length=255)
    sector: str = Field(..., max_length=100)
    annual_turnover_eur: float
    employee_count: int
    balance_sheet_total: Optional[float] = None
    service_scope: list[str] = Field(default_factory=list)
    cross_border_operations: CrossBorderInfo = Field(default_factory=CrossBorderInfo)
    is_public_admin: bool = False
    is_trust_service_provider: bool = False
    is_tld_registry: bool = False
    is_dns_provider: bool = False
    address: Optional[Address] = None
    contact_email: Optional[str] = Field(None, max_length=255)
    
    @property
    def size_details(self) -> SizeDetails:
        """Generate size details from input values."""
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


class EntityProfile(BaseModel):
    """Complete entity profile for audit sessions."""
    entity_id: str
    legal_name: str
    classification: EntityClassification
    address: Optional[Address] = None
    contact_email: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
