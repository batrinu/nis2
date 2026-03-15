"""
Pydantic models for audit sessions.
"""
from datetime import datetime, timezone
from typing import Literal, Optional
from pydantic import BaseModel, Field

from .entity import EntityInput, EntityClassification


class AuditSession(BaseModel):
    """An audit session tracking the full workflow."""
    session_id: str = Field(default_factory=lambda: f"AUDIT-{datetime.now(timezone.utc).timestamp()}")
    
    # Entity info
    entity_input: EntityInput
    classification: Optional[EntityClassification] = None
    
    # Session status
    status: Literal[
        "created",
        "entity_classified",
        "network_scanned",
        "devices_interrogated",
        "checklist_completed",
        "gap_analysis_done",
        "report_generated",
        "closed"
    ] = "created"
    
    # Metadata
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    # Auditor info
    auditor_name: Optional[str] = None
    auditor_organization: Optional[str] = None
    
    # Location/context
    audit_location: Optional[str] = None
    network_segment: Optional[str] = None  # e.g., "192.168.1.0/24"
    
    # Summary (populated as audit progresses)
    device_count: int = 0
    finding_count: int = 0
    compliance_score: Optional[float] = None
    
    # Notes
    notes: str = ""
    
    # Storage path
    db_path: str = "./audit_sessions.db"


class SessionSummary(BaseModel):
    """Summary of an audit session for listings."""
    session_id: str
    entity_name: str
    entity_sector: str
    status: str
    classification: Optional[str] = None
    device_count: int = 0
    finding_count: int = 0
    compliance_score: Optional[float] = None
    created_at: datetime
    updated_at: datetime
