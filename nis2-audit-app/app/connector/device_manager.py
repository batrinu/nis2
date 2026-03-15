"""
Device connection manager using Netmiko for SSH/Telnet connections.
"""
import ipaddress
import logging
from typing import Optional, Dict, Any, Tuple
from dataclasses import dataclass

from ..models import NetworkDevice, DeviceCredentials
from ..utils import check_connection_rate_limit, check_ip_connection_rate_limit
from ..security_pinning import HostKeyPinningManager, PinnedSSHVerifier

logger = logging.getLogger(__name__)


# SECURITY: Sensitive IP ranges that should not be connected to
SENSITIVE_IP_RANGES = [
    ipaddress.ip_network("169.254.0.0/16"),   # Link-local (cloud metadata)
    ipaddress.ip_network("127.0.0.0/8"),      # IPv4 loopback
    ipaddress.ip_network("::1/128"),          # IPv6 loopback
    ipaddress.ip_network("fc00::/7"),         # IPv6 unique local
    ipaddress.ip_network("fe80::/10"),        # IPv6 link-local
]


def is_sensitive_ip(ip_str: str) -> Tuple[bool, Optional[str]]:
    """
    Check if an IP address is in a sensitive/protected range.
    
    Args:
        ip_str: IP address string
        
    Returns:
        Tuple of (is_sensitive, reason)
    """
    try:
        ip = ipaddress.ip_address(ip_str)
        for network in SENSITIVE_IP_RANGES:
            if ip in network:
                return True, f"{ip_str} is in protected range {network}"
        return False, None
    except ValueError:
        return False, None


def validate_device_ip(ip_address: str) -> Tuple[bool, Optional[str]]:
    """
    Validate device IP address before connection.
    
    Args:
        ip_address: IP address to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not ip_address:
        return False, "IP address is required"
    
    # Check if it's a valid IP
    try:
        ipaddress.ip_address(ip_address)
    except ValueError:
        return False, f"Invalid IP address: {ip_address}"
    
    # Check for sensitive IPs
    is_sensitive, reason = is_sensitive_ip(ip_address)
    if is_sensitive:
        return False, f"Cannot connect to protected IP: {reason}"
    
    return True, None


# Netmiko device type mappings
DEVICE_TYPE_MAPPINGS = {
    # Cisco
    "cisco_ios": ["cisco", "ios", "cisco_ios", "cisco switch", "cisco router"],
    "cisco_xe": ["cisco_xe", "ios-xe", "csr1000v"],
    "cisco_xr": ["cisco_xr", "ios-xr", "asr9000"],
    "cisco_asa": ["cisco_asa", "asa", "cisco firewall"],
    "cisco_nxos": ["cisco_nxos", "nxos", "nexus"],
    
    # Juniper
    "juniper_junos": ["juniper", "junos", "srx", "ex", "mx"],
    
    # MikroTik
    "mikrotik_routeros": ["mikrotik", "routeros", "rb"],
    "mikrotik_switchos": ["switchos", "crs"],
    
    # Fortinet
    "fortinet": ["fortinet", "fortigate", "fortios"],
    
    # HP/Aruba
    "hp_comware": ["hp_comware", "comware", "h3c"],
    "hp_procurve": ["hp_procurve", "procurve", "aruba"],
    
    # Dell
    "dell_os9": ["dell", "dell_os9", "force10"],
    "dell_os10": ["dell_os10"],
    "dell_powerconnect": ["dell_powerconnect", "powerconnect"],
    
    # Linux/Unix
    "linux": ["linux", "ubuntu", "debian", "centos", "rhel", "fedora", "generic_linux"],
    "generic_termserver": ["terminal_server", "console_server"],
}


def guess_netmiko_device_type(vendor: Optional[str], device_type: Optional[str]) -> str:
    """
    Guess Netmiko device_type from vendor and device_type strings.
    
    Args:
        vendor: Device vendor (e.g., "Cisco")
        device_type: Device type (e.g., "router", "switch")
    
    Returns:
        Netmiko device_type string
    """
    search_str = f"{vendor or ''} {device_type or ''}".lower()
    
    for netmiko_type, keywords in DEVICE_TYPE_MAPPINGS.items():
        for keyword in keywords:
            if keyword in search_str:
                return netmiko_type
    
    # Default to cisco_ios if vendor is Cisco
    if vendor and "cisco" in vendor.lower():
        return "cisco_ios"
    
    # Default to linux for servers
    if device_type == "server":
        return "linux"
    
    # Fallback
    return "cisco_ios"


@dataclass
class ConnectionResult:
    """Result of a connection attempt."""
    success: bool
    device_type_detected: Optional[str] = None
    error_message: Optional[str] = None
    device_info: Optional[Dict[str, Any]] = None


class DeviceConnector:
    """
    Manages SSH connections to network devices using Netmiko.
    """
    
    def __init__(self, device: NetworkDevice, credentials: DeviceCredentials,
                 pinning_manager: Optional[HostKeyPinningManager] = None):
        self.device = device
        self.credentials = credentials
        self.connection: Optional[Any] = None
        self.netmiko_device_type: Optional[str] = None
        self._pinning = pinning_manager or HostKeyPinningManager()
        self._ssh_verifier = PinnedSSHVerifier(self._pinning)
    
    def connect(self, auto_detect: bool = True) -> ConnectionResult:
        """
        Establish connection to device.
        
        Args:
            auto_detect: Whether to auto-detect device type
        
        Returns:
            ConnectionResult
        """
        # Security: Validate IP address before connecting
        is_valid, error = validate_device_ip(self.device.ip_address)
        if not is_valid:
            return ConnectionResult(
                success=False,
                error_message=error
            )
        
        # Security: Check rate limit to prevent connection flooding (2026 fix)
        check_connection_rate_limit()
        
        # Security: Per-IP rate limiting (2026: CVE-2026-20080 pattern)
        if not check_ip_connection_rate_limit(self.device.ip_address):
            return ConnectionResult(
                success=False,
                error_message=f"Connection rate limit exceeded for {self.device.ip_address}. "
                              "Maximum 5 connections per minute per device."
            )
        
        try:
            # Try importing netmiko
            from netmiko import ConnectHandler
            from netmiko.ssh_autodetect import SSHAutodetect
        except ImportError:
            return ConnectionResult(
                success=False,
                error_message="Netmiko not installed. Install with: pip install netmiko"
            )
        
        # Determine device type
        if auto_detect:
            self.netmiko_device_type = self._autodetect_device_type()
        else:
            self.netmiko_device_type = guess_netmiko_device_type(
                self.device.vendor, self.device.device_type
            )
        
        if not self.netmiko_device_type:
            return ConnectionResult(
                success=False,
                error_message="Could not determine device type"
            )
        
        # Connection parameters
        conn_params = {
            "device_type": self.netmiko_device_type,
            "host": self.device.ip_address,
            "username": self.credentials.username,
            "password": self.credentials.password,
            "port": self.credentials.port,
            "timeout": 30,
            "conn_timeout": 30,
            # Security: Enable host key verification
            "ssh_strict": True,  # Reject unknown host keys
            "system_host_keys": True,  # Use system known_hosts file
            # Security: Keep connection alive during long operations
            "keepalive": 30,  # Send keepalive every 30 seconds
            "session_timeout": 60,  # Session timeout
            # Security: Authentication must complete within this time (2026 hardening)
            "auth_timeout": 30,  # Auth phase timeout
        }
        
        # Add enable password if provided
        if self.credentials.enable_password:
            conn_params["secret"] = self.credentials.enable_password
        
        # Use SSH key if provided (more secure than password)
        if self.credentials.ssh_key_path:
            conn_params["key_file"] = self.credentials.ssh_key_path
            conn_params["use_keys"] = True
        
        try:
            # SECURITY: Verify or pin host key before connecting
            # Get the host key from known_hosts or from the connection
            host_key_valid, host_key_msg = self._verify_host_key()
            if not host_key_valid:
                return ConnectionResult(
                    success=False,
                    error_message=f"Host key verification failed: {host_key_msg}"
                )
            
            logger.debug(f"Host key verification: {host_key_msg}")
            
            self.connection = ConnectHandler(**conn_params)
            
            # Enter enable mode if needed
            if self.netmiko_device_type in ["cisco_ios", "cisco_xe", "cisco_asa"]:
                self.connection.enable()
            
            # Gather device info
            device_info = self._gather_device_info()
            
            return ConnectionResult(
                success=True,
                device_type_detected=self.netmiko_device_type,
                device_info=device_info
            )
            
        except Exception as e:
            logger.error(f"Connection failed: {e}")
            return ConnectionResult(
                success=False,
                error_message=str(e)
            )
    
    def disconnect(self) -> None:
        """Close connection."""
        if self.connection:
            try:
                self.connection.disconnect()
            except Exception as e:
                # Log but don't raise - we're cleaning up
                logger.debug(f"Error during disconnect: {e}")
            finally:
                self.connection = None
    
    def _verify_host_key(self) -> Tuple[bool, str]:
        """
        Verify host key against pinned value or pin if first seen.
        
        Returns:
            Tuple of (is_valid, message)
        """
        sock = None
        transport = None
        try:
            import paramiko
            import socket
            
            # Create transport to get host key
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            sock.connect((self.device.ip_address, self.credentials.port))
            
            transport = paramiko.Transport(sock)
            transport.start_client(timeout=5)
            
            # Get server key
            server_key = transport.get_remote_server_key()
            
            if server_key is None:
                return False, "Could not retrieve server host key"
            
            # Get key details
            key_type = server_key.get_name()
            key_bytes = server_key.asbytes()
            
            # Verify or pin
            is_valid, message = self._ssh_verifier.verify_host_key(
                self.device.ip_address,
                self.credentials.port,
                key_type,
                key_bytes
            )
            
            return is_valid, message
            
        except ImportError:
            # paramiko not available, skip verification
            return True, "Host key verification skipped (paramiko not available)"
        except Exception as e:
            logger.error(f"Host key verification error: {e}")
            # SECURITY: Fail closed - don't allow connection if verification fails
            return False, f"Host key verification failed: {e}"
        finally:
            # Ensure resources are always cleaned up
            if transport:
                try:
                    transport.close()
                except Exception:
                    pass
            if sock:
                try:
                    sock.close()
                except Exception:
                    pass
    
    def _autodetect_device_type(self) -> Optional[str]:
        """
        Auto-detect device type using Netmiko's SSHAutodetect.
        
        Returns:
            Detected device type or None
        """
        try:
            from netmiko.ssh_autodetect import SSHAutodetect
            
            detector = SSHAutodetect(
                host=self.device.ip_address,
                username=self.credentials.username,
                password=self.credentials.password,
                port=self.credentials.port,
            )
            
            best_match = detector.autodetect()
            return best_match
            
        except Exception as e:
            # Fallback to guess based on vendor
            return guess_netmiko_device_type(self.device.vendor, self.device.device_type)
    
    def _gather_device_info(self) -> Dict[str, Any]:
        """Gather basic device information after connection."""
        info = {}
        
        if not self.connection:
            return info
        
        try:
            # Get prompt
            info["prompt"] = self.connection.find_prompt()
            
            # Try to get hostname from prompt
            if info["prompt"]:
                hostname = info["prompt"].strip("# >$")
                info["hostname"] = hostname
            
        except Exception:
            pass
        
        return info
    
    def execute_command(self, command: str, timeout: int = 60) -> str:
        """
        Execute a command on the device.
        
        Args:
            command: Command to execute
            timeout: Maximum time to wait for command completion (seconds)
        
        Returns:
            Command output
        
        Raises:
            RuntimeError: If not connected or command times out
        """
        if not self.connection:
            raise RuntimeError("Not connected to device")
        
        try:
            # Use delay_factor and max_loops to implement timeout
            # Netmiko doesn't have direct timeout, so we use these parameters
            return self.connection.send_command(
                command,
                delay_factor=1,
                max_loops=timeout * 2,  # Approximately timeout seconds
                strip_prompt=True,
                strip_command=True
            )
        except Exception as e:
            if "timed out" in str(e).lower() or "pattern not detected" in str(e).lower():
                raise TimeoutError(f"Command timed out after {timeout}s: {command}")
            raise
    
    def execute_commands(self, commands: list[str]) -> Dict[str, str]:
        """
        Execute multiple commands.
        
        Args:
            commands: List of commands
        
        Returns:
            Dict mapping command to output
        """
        results = {}
        for cmd in commands:
            results[cmd] = self.execute_command(cmd)
        return results
    
    def save_configuration(self) -> bool:
        """
        Save running config to startup config.
        
        Returns:
            True if successful
        """
        if not self.connection:
            return False
        
        try:
            if self.netmiko_device_type in ["cisco_ios", "cisco_xe"]:
                output = self.connection.save_config()
                return "OK" in output or "[OK]" in output
            elif self.netmiko_device_type == "cisco_asa":
                self.connection.send_command("write memory")
                return True
            elif self.netmiko_device_type in ["juniper_junos"]:
                self.connection.commit()
                return True
            else:
                # Generic save
                self.connection.save_config()
                return True
        except Exception:
            return False


class ConnectionManager:
    """Manages multiple device connections."""
    
    def __init__(self):
        self.connections: Dict[str, DeviceConnector] = {}
    
    def connect_device(
        self,
        device: NetworkDevice,
        credentials: DeviceCredentials,
        auto_detect: bool = True
    ) -> ConnectionResult:
        """
        Connect to a device and store connection.
        
        Args:
            device: Device to connect to
            credentials: Login credentials
            auto_detect: Auto-detect device type
        
        Returns:
            ConnectionResult
        """
        connector = DeviceConnector(device, credentials)
        result = connector.connect(auto_detect=auto_detect)
        
        if result.success:
            self.connections[device.device_id] = connector
            device.connection_status = "connected"
            
            # Update device info
            if result.device_info:
                if "hostname" in result.device_info:
                    device.hostname = result.device_info["hostname"]
        else:
            device.connection_status = "failed"
        
        return result
    
    def disconnect_device(self, device_id: str) -> None:
        """Disconnect from a device."""
        if device_id in self.connections:
            self.connections[device_id].disconnect()
            del self.connections[device_id]
    
    def disconnect_all(self) -> None:
        """Disconnect from all devices."""
        for connector in self.connections.values():
            connector.disconnect()
        self.connections.clear()
    
    def get_connection(self, device_id: str) -> Optional[DeviceConnector]:
        """Get active connection for device."""
        return self.connections.get(device_id)
    
    def execute_on_device(self, device_id: str, command: str) -> str:
        """
        Execute command on connected device.
        
        Args:
            device_id: Device ID
            command: Command to execute
        
        Returns:
            Command output
        """
        connector = self.get_connection(device_id)
        if not connector:
            raise RuntimeError(f"Device {device_id} not connected")
        
        return connector.execute_command(command)
