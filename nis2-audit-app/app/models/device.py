"""
Pydantic models for network devices discovered during audits.
"""
from datetime import datetime, timezone
from typing import Literal, Optional, Any
from pydantic import BaseModel, ConfigDict, Field


class DeviceCredentials(BaseModel):
    """Credentials for device access."""
    username: str
    password: str
    enable_password: Optional[str] = None
    ssh_key_path: Optional[str] = None
    port: int = 22


class NetworkInterface(BaseModel):
    """Network interface information."""
    name: str
    ip_address: Optional[str] = None
    mac_address: Optional[str] = None
    status: Literal["up", "down", "administratively down", "unknown"] = "unknown"
    vlan: Optional[int] = None
    speed: Optional[str] = None
    duplex: Optional[str] = None


class DeviceConfig(BaseModel):
    """Device configuration snapshot."""
    running_config: Optional[str] = None
    startup_config: Optional[str] = None
    firmware_version: Optional[str] = None
    hostname: Optional[str] = None
    domain_name: Optional[str] = None
    ntp_servers: list[str] = Field(default_factory=list)
    syslog_servers: list[str] = Field(default_factory=list)
    snmp_community: Optional[str] = None  # Will be sanitized in reports
    ssh_version: Optional[str] = None


class DeviceCommandResult(BaseModel):
    """Result of running a command on a device."""
    command: str
    raw_output: str
    parsed_output: Optional[dict[str, Any]] = None
    success: bool
    error_message: Optional[str] = None
    execution_time_ms: Optional[int] = None


class NetworkDevice(BaseModel):
    """Network device discovered or interrogated during audit."""
    device_id: str = Field(
        default_factory=lambda: f"DEV-{datetime.now(timezone.utc).timestamp()}",
        max_length=64
    )
    session_id: str = Field(..., max_length=64)
    
    # Discovery info
    ip_address: str = Field(..., max_length=45)  # IPv6 max length
    hostname: Optional[str] = Field(None, max_length=253)  # DNS max length
    mac_address: Optional[str] = Field(None, max_length=17)  # AA:BB:CC:DD:EE:FF
    
    # Identification
    vendor: Optional[str] = Field(None, max_length=100)
    device_type: Optional[str] = Field(None, max_length=50)
    os_version: Optional[str] = Field(None, max_length=200)
    model: Optional[str] = Field(None, max_length=200)
    
    # Network info
    interfaces: list[NetworkInterface] = Field(default_factory=list)
    open_ports: list[int] = Field(default_factory=list)
    
    # Audit status
    discovery_method: Literal["nmap_scan", "manual_entry", "snmp_poll"] = "nmap_scan"
    connection_status: Literal["pending", "connected", "failed", "not_attempted"] = "pending"
    last_seen: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    # Configuration (populated after interrogation)
    config: Optional[DeviceConfig] = None
    command_results: list[DeviceCommandResult] = Field(default_factory=list)
    
    # Credentials (NOT stored in DB - kept only in memory during active sessions)
    # SECURITY: For security, credentials are never persisted to disk
    credentials: Optional[DeviceCredentials] = None
    
    # Metadata
    notes: str = Field("", max_length=10000)  # Limit notes size
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    model_config = ConfigDict(
        json_encoders={
            datetime: lambda v: v.isoformat()
        }
    )
