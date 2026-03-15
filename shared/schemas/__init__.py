"""
Shared schemas for the NIS2 compliance assessment system.
"""
from .entity import (
    Address,
    SizeDetails,
    CrossBorderInfo,
    EntityInput,
    EntityClassification,
    ComplianceHistory,
    SanctionRecord,
    AuditHistory,
    EntityProfile,
)
from .incident import (
    ImpactAssessment,
    IncidentTimeline,
    IncidentNotification,
    SignificantIncident,
)
from .compliance import (
    ComplianceStatus,
    DomainScore,
    Finding,
    Recommendation,
    RemediationItem,
    ComplianceReport,
    GapAnalysisReport,
    AuditAssessment,
)
from .sanction import (
    Violation,
    FineCalculation,
    Sanction,
    RemediationPlan,
    AppealRights,
    ProportionalityFactors,
    ProportionalityAssessment,
    SanctionNotice,
    SanctionPackage,
)

__all__ = [
    # Entity schemas
    "Address",
    "SizeDetails",
    "CrossBorderInfo",
    "EntityInput",
    "EntityClassification",
    "ComplianceHistory",
    "SanctionRecord",
    "AuditHistory",
    "EntityProfile",
    # Incident schemas
    "ImpactAssessment",
    "IncidentTimeline",
    "IncidentNotification",
    "SignificantIncident",
    # Compliance schemas
    "ComplianceStatus",
    "DomainScore",
    "Finding",
    "Recommendation",
    "RemediationItem",
    "ComplianceReport",
    "GapAnalysisReport",
    "AuditAssessment",
    # Sanction schemas
    "Violation",
    "FineCalculation",
    "Sanction",
    "RemediationPlan",
    "AppealRights",
    "ProportionalityFactors",
    "ProportionalityAssessment",
    "SanctionNotice",
    "SanctionPackage",
]
