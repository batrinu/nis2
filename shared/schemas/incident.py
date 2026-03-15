"""
Pydantic schemas for Incident reporting.
"""
from datetime import datetime
from typing import Literal, Optional
from pydantic import BaseModel, Field


class ImpactAssessment(BaseModel):
    """Assessment of incident impact."""
    financial_loss_eur: Optional[float] = None
    users_affected: Optional[int] = None
    service_unavailability_hours: Optional[float] = None
    data_records_affected: Optional[int] = None
    personal_data_breach: bool = False
    
    @property
    def is_significant(self) -> bool:
        """Check if incident meets significance thresholds."""
        thresholds = [
            self.financial_loss_eur and self.financial_loss_eur >= 1_000_000,
            self.users_affected and self.users_affected >= 100_000,
            self.service_unavailability_hours and self.service_unavailability_hours >= 12,
            self.data_records_affected and self.data_records_affected >= 100_000,
            self.personal_data_breach
        ]
        return any(thresholds)


class IncidentTimeline(BaseModel):
    """Timeline of incident events."""
    detected_at: datetime
    contained_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    reported_to_ca_at: Optional[datetime] = None


class IncidentNotification(BaseModel):
    """NIS2 incident notification structure."""
    incident_id: str
    entity_id: str
    
    # Classification
    severity: Literal["low", "medium", "high", "critical"]
    incident_type: str
    
    # Timeline
    timeline: IncidentTimeline
    
    # Impact
    impact: ImpactAssessment
    
    # Description
    description: str
    affected_systems: list[str]
    root_cause: Optional[str] = None
    
    # Response
    response_actions: list[str]
    lessons_learned: Optional[str] = None
    
    # Reporting
    notification_type: Literal["early_warning", "intermediate", "final"]
    legal_basis: str = "Article 23"
    
    # Cross-border
    cross_border_impact: bool = False
    affected_member_states: list[str] = Field(default_factory=list)
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class SignificantIncident(IncidentNotification):
    """Significant incident as defined by Article 23(3)."""
    notification_type: Literal["early_warning", "intermediate", "final"]
    
    @property
    def reporting_deadline(self) -> Optional[datetime]:
        """Calculate reporting deadline based on notification type."""
        if self.notification_type == "early_warning":
            # 24 hours from detection
            return self.timeline.detected_at.replace(
                hour=self.timeline.detected_at.hour + 24
            )
        elif self.notification_type == "intermediate":
            # 72 hours from detection
            return self.timeline.detected_at.replace(
                hour=self.timeline.detected_at.hour + 72
            )
        elif self.notification_type == "final":
            # 1 month from detection
            month = self.timeline.detected_at.month + 1
            year = self.timeline.detected_at.year
            if month > 12:
                month = 1
                year += 1
            return self.timeline.detected_at.replace(year=year, month=month)
        return None
