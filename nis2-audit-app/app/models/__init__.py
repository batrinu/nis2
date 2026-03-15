"""
Pydantic models for the NIS2 Field Audit App.
"""
from .entity import (
    Address,
    SizeDetails,
    CrossBorderInfo,
    EntityInput,
    EntityClassification,
    EntityProfile,
)
from .device import (
    DeviceCredentials,
    NetworkInterface,
    DeviceConfig,
    DeviceCommandResult,
    NetworkDevice,
)
from .finding import (
    AuditFinding,
    GapScore,
    ComplianceScore,
)
from .audit_session import (
    AuditSession,
    SessionSummary,
)
from .scan_result import (
    DiscoveredHost,
    ScanResult,
    SubnetInfo,
)

__all__ = [
    # Entity
    "Address",
    "SizeDetails",
    "CrossBorderInfo",
    "EntityInput",
    "EntityClassification",
    "EntityProfile",
    # Device
    "DeviceCredentials",
    "NetworkInterface",
    "DeviceConfig",
    "DeviceCommandResult",
    "NetworkDevice",
    # Finding
    "AuditFinding",
    "GapScore",
    "ComplianceScore",
    # Audit Session
    "AuditSession",
    "SessionSummary",
    # Scan Result
    "DiscoveredHost",
    "ScanResult",
    "SubnetInfo",
]
