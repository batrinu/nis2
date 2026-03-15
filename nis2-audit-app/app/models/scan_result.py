"""
Pydantic models for network scan results.
"""
from datetime import datetime, timezone
from typing import Optional
from pydantic import BaseModel, Field


class DiscoveredHost(BaseModel):
    """A host discovered during network scanning."""
    ip_address: str
    hostname: Optional[str] = None
    mac_address: Optional[str] = None
    vendor: Optional[str] = None  # Device vendor from MAC OUI
    
    # Port scan results
    open_ports: list[int] = Field(default_factory=list)
    port_services: dict[int, str] = Field(default_factory=dict)  # port -> service name
    
    # OS detection
    os_guess: Optional[str] = None
    os_family: Optional[str] = None  # Linux, Windows, Cisco IOS, etc.
    os_accuracy: Optional[int] = None  # Percentage confidence
    
    # Device type detection
    device_type: Optional[str] = None  # router, switch, firewall, server, workstation
    
    # Scan metadata
    scan_time_ms: Optional[int] = None
    discovered_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ScanResult(BaseModel):
    """Results of a network scan."""
    scan_id: str = Field(default_factory=lambda: f"SCAN-{datetime.now(timezone.utc).timestamp()}")
    session_id: str
    
    # Scan parameters
    target_network: str  # e.g., "192.168.1.0/24"
    scan_type: str = "quick"  # quick, comprehensive, custom
    
    # Results
    hosts: list[DiscoveredHost] = Field(default_factory=list)
    hosts_up: int = 0
    hosts_down: int = 0
    total_hosts: int = 0
    
    # Timing
    started_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: Optional[datetime] = None
    duration_seconds: Optional[float] = None
    
    # Status
    status: str = "pending"  # pending, running, completed, failed
    error_message: Optional[str] = None
    
    # Device breakdown
    router_count: int = 0
    switch_count: int = 0
    firewall_count: int = 0
    server_count: int = 0
    unknown_count: int = 0


class SubnetInfo(BaseModel):
    """Information about a local subnet."""
    interface: str
    ip_address: str
    netmask: str
    network_cidr: str
    gateway: Optional[str] = None
    is_default: bool = False
