"""
Network scanner using nmap for device discovery.
"""
import ipaddress
import logging
import subprocess
import re
# SECURITY (Pass 8): Use secure XML parsing with XXE protection
try:
    from defusedxml import ElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from typing import Optional, Tuple

from ..models import ScanResult, DiscoveredHost
from ..utils import check_scan_rate_limit
from ..security_utils import safe_regex_match, RegexTimeoutError

logger = logging.getLogger(__name__)

# SECURITY: Sensitive IP ranges that should not be scanned
# These include cloud metadata endpoints, loopback, and link-local addresses
# Pre-compute sensitive IP networks for faster lookup
_SENSITIVE_IP_NETWORKS = (
    ipaddress.ip_network("169.254.0.0/16"),   # Link-local (cloud metadata)
    ipaddress.ip_network("127.0.0.0/8"),      # IPv4 loopback
    ipaddress.ip_network("::1/128"),          # IPv6 loopback
    ipaddress.ip_network("fc00::/7"),         # IPv6 unique local
    ipaddress.ip_network("fe80::/10"),        # IPv6 link-local
)

# Cache for network reasons to avoid repeated string comparisons
_NETWORK_REASONS = {
    _SENSITIVE_IP_NETWORKS[0]: "Cloud metadata IP - protected range, cannot scan",
    _SENSITIVE_IP_NETWORKS[1]: "Loopback address - protected range, cannot scan",
    _SENSITIVE_IP_NETWORKS[2]: "IPv6 loopback - protected range, cannot scan",
}


def is_sensitive_ip(ip_str: str) -> tuple[bool, Optional[str]]:
    """
    Check if an IP address is in a sensitive range.
    
    Args:
        ip_str: IP address string to check
        
    Returns:
        Tuple of (is_sensitive, reason_message)
    """
    try:
        ip = ipaddress.ip_address(ip_str)
        for network in _SENSITIVE_IP_NETWORKS:
            if ip in network:
                # Use cached reason if available, else return generic message
                return True, _NETWORK_REASONS.get(network, "Sensitive IP range - protected, cannot scan")
        return False, None
    except ValueError:
        return False, "Invalid IP address"


class InvalidTargetError(Exception):
    """Raised when scan target is invalid or too large."""
    pass


def validate_scan_target(target: str) -> tuple[bool, Optional[str]]:
    """
    Validate a scan target to prevent accidental huge scans.
    
    Args:
        target: Network target (e.g., "192.168.1.0/24", "10.0.0.1-50")
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not target or not isinstance(target, str):
        return False, "Target must be a non-empty string"
    
    # SECURITY (2026): Character allowlist to prevent command injection
    # CVE-2026-3484 pattern: shell metacharacters in target can inject commands
    allowed_chars = set(
        "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ.-/,"
    )
    if not all(c in allowed_chars for c in target):
        invalid_chars = set(c for c in target if c not in allowed_chars)
        return False, f"Target contains invalid characters: {invalid_chars}"
    
    # Check for dangerous patterns (Pass 11: ReDoS-safe regex)
    dangerous_patterns = [
        (r"^0\.0\.0\.0", "0.0.0.0 is not allowed (default route)"),
        (r"^255\.", "Cannot scan broadcast addresses"),
        (r"/0$", "/0 is too broad - would scan the entire internet!"),
    ]
    
    for pattern, message in dangerous_patterns:
        try:
            if safe_regex_match(pattern, target) or re.search(pattern, target):
                return False, message
        except RegexTimeoutError:
            return False, "Target validation timed out - possible attack"
    
    # Check CIDR size (Pass 11: Bounded regex)
    try:
        cidr_match = safe_regex_match(r"/([0-9]{1,2})$", target) or re.search(
            r"/(\d+)$", target
        )
    except RegexTimeoutError:
        return False, "CIDR validation timed out"
    if cidr_match:
        cidr = int(cidr_match.group(1))
        if cidr < 16:  # /16 = 65,534 hosts, /8 = 16 million hosts
            return False, f"CIDR /{cidr} is too large (max /16 allowed for safety)"
    
    # Check IP range size (e.g., "192.168.1.1-255")
    try:
        range_match = safe_regex_match(r"([0-9]{1,3})-([0-9]{1,3})$", target) or re.search(
            r"(\d+)-(\d+)$", target
        )
    except RegexTimeoutError:
        return False, "Range validation timed out"
    if range_match:
        start, end = int(range_match.group(1)), int(range_match.group(2))
        if end - start > 254:
            return False, f"IP range {start}-{end} is too large (max 254 hosts)"
    
    # Validate it's a valid IP or network and check for sensitive IPs
    try:
        # Try as network
        if "/" in target:
            network = ipaddress.ip_network(target, strict=False)
            # Check if any IP in the network is sensitive
            # For large networks, just check the network address
            is_sensitive, reason = is_sensitive_ip(str(network.network_address))
            if is_sensitive:
                return False, f"Cannot scan protected network: {reason}"
            # Also check broadcast address
            is_sensitive, reason = is_sensitive_ip(str(network.broadcast_address))
            if is_sensitive:
                return False, f"Cannot scan protected network: {reason}"
        else:
            # Try as IP or hostname
            ip_part = target.split("-")[0].split(",")[0]
            try:
                ipaddress.ip_address(ip_part)
                # It's a valid IP, check if sensitive
                is_sensitive, reason = is_sensitive_ip(ip_part)
                if is_sensitive:
                    return False, f"Cannot scan protected IP: {reason}"
            except ValueError:
                # Might be a hostname, which is okay for nmap
                # But check for common cloud metadata hostnames
                lower_target = ip_part.lower()
                if any(
                    x in lower_target
                    for x in ['metadata', 'metadata.google', '169.254.169.254']
                ):
                    return False, "Cannot scan cloud metadata endpoints"
                pass
    except ValueError as e:
        return False, f"Invalid IP address or network: {e}"
    
    return True, None


class NetworkScannerError(Exception):
    """Raised when network scanning fails."""
    pass


class NmapScanner:
    """
    Nmap-based network scanner for discovering devices.
    Requires nmap to be installed on the system.
    """
    
    # Common NIS2-relevant ports to check
    COMMON_PORTS = "22,23,80,443,161,162,3389,5900,8291,8080,8443"
    
    def __init__(self):
        self._check_nmap_installed()
    
    def _check_nmap_installed(self) -> None:
        """Check if nmap is available."""
        try:
            subprocess.run(
                ["nmap", "--version"],
                capture_output=True,
                check=True
            )
        except (subprocess.CalledProcessError, FileNotFoundError):
            raise NetworkScannerError(
                "nmap is not installed. Please install nmap first:\n"
                "  Ubuntu/Debian: sudo apt-get install nmap\n"
                "  macOS: brew install nmap\n"
                "  Windows: https://nmap.org/download.html"
            )
    
    def scan_subnet(
        self,
        target: str,
        session_id: str,
        scan_type: str = "quick",
        timing_template: int = 4,
    ) -> ScanResult:
        """
        Scan a network subnet for active devices.
        
        Args:
            target: Network target (e.g., "192.168.1.0/24", "10.0.0.1-50")
            session_id: Associated audit session ID
            scan_type: "quick" (host discovery + common ports) or 
                      "comprehensive" (detailed port scan + OS detection)
            timing_template: Nmap timing (0=paranoid, 5=insane), default 4 (aggressive)
        
        Returns:
            ScanResult with discovered hosts
            
        Raises:
            InvalidTargetError: If target is invalid or too large
            NetworkScannerError: If nmap fails
        """
        # Security: Check rate limit to prevent flooding (2026 fix)
        check_scan_rate_limit()
        
        # Validate target
        is_valid, error = validate_scan_target(target)
        if not is_valid:
            raise InvalidTargetError(error)
        
        result = ScanResult(
            session_id=session_id,
            target_network=target,
            scan_type=scan_type,
        )
        
        started_at = datetime.now(timezone.utc)
        
        try:
            if scan_type == "quick":
                hosts = self._quick_scan(target, timing_template)
            else:
                hosts = self._comprehensive_scan(target, timing_template)
            
            result.hosts = hosts
            result.hosts_up = len(hosts)
            result.status = "completed"
            
            # Count device types in a single pass
            router_count = switch_count = firewall_count = server_count = unknown_count = 0
            for host in hosts:
                dt = host.device_type
                if dt == "router":
                    router_count += 1
                elif dt == "switch":
                    switch_count += 1
                elif dt == "firewall":
                    firewall_count += 1
                elif dt == "server":
                    server_count += 1
                else:
                    unknown_count += 1
            
            result.router_count = router_count
            result.switch_count = switch_count
            result.firewall_count = firewall_count
            result.server_count = server_count
            result.unknown_count = unknown_count
            
        except Exception as e:
            result.status = "failed"
            result.error_message = str(e)
        
        completed_at = datetime.now(timezone.utc)
        result.completed_at = completed_at
        result.duration_seconds = (completed_at - started_at).total_seconds()
        
        return result
    
    def _quick_scan(self, target: str, timing: int) -> list[DiscoveredHost]:
        """
        Quick scan: Host discovery + common port check.
        
        Command: nmap -sn -PS22,23,80,443... -T4 -oX - target
        """
        cmd = [
            "nmap",
            "-sn",  # Ping scan (host discovery only, no port scan)
            f"-PS{self.COMMON_PORTS}",  # TCP SYN ping on common ports
            f"-T{timing}",
            "-oX", "-",  # XML output to stdout
            target
        ]
        
        return self._run_nmap(cmd)
    
    def _comprehensive_scan(self, target: str, timing: int) -> list[DiscoveredHost]:
        """
        Comprehensive scan: OS detection, version detection, all common ports.
        
        Command: nmap -A -p22,23,80,443... -T4 -oX - target
        """
        cmd = [
            "nmap",
            "-A",  # OS detection, version detection, script scanning, traceroute
            f"-p{self.COMMON_PORTS}",
            f"-T{timing}",
            "-oX", "-",
            target
        ]
        
        return self._run_nmap(cmd)
    
    def _run_nmap(self, cmd: list[str]) -> list[DiscoveredHost]:
        """Execute nmap command and parse XML output."""
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        )
        
        if result.returncode != 0:
            raise NetworkScannerError(f"nmap failed: {result.stderr}")
        
        return self._parse_nmap_xml(result.stdout)
    
    def _parse_nmap_xml(self, xml_output: str) -> list[DiscoveredHost]:
        """Parse nmap XML output into DiscoveredHost objects."""
        try:
            root = ET.fromstring(xml_output)
        except ET.ParseError as e:
            raise NetworkScannerError(f"Failed to parse nmap output: {e}")
        
        # Use list comprehension with filter for better performance
        return [
            host
            for host in (self._parse_host_element(elem) for elem in root.findall("host"))
            if host is not None
        ]
    
    def _parse_host_element(self, host_elem: ET.Element) -> Optional[DiscoveredHost]:
        """Parse a single host element from nmap XML."""
        # Check if host is up
        status = host_elem.find("status")
        if status is not None and status.get("state") != "up":
            return None
        
        # Get IP address
        address_elem = host_elem.find("address[@addrtype='ipv4']")
        if address_elem is None:
            return None
        
        ip_address = address_elem.get("addr")
        vendor = address_elem.get("vendor")
        
        host = DiscoveredHost(
            ip_address=ip_address,
            vendor=vendor,
        )
        
        # Get MAC address if available
        mac_elem = host_elem.find("address[@addrtype='mac']")
        if mac_elem is not None:
            host.mac_address = mac_elem.get("addr")
            if not vendor:
                host.vendor = mac_elem.get("vendor")
        
        # Get hostname
        hostnames = host_elem.find("hostnames")
        if hostnames is not None:
            hostname_elem = hostnames.find("hostname")
            if hostname_elem is not None:
                host.hostname = hostname_elem.get("name")
        
        # Parse ports
        ports_elem = host_elem.find("ports")
        if ports_elem is not None:
            for port_elem in ports_elem.findall("port"):
                self._parse_port_element(port_elem, host)
        
        # Parse OS detection
        os_elem = host_elem.find("os")
        if os_elem is not None:
            self._parse_os_element(os_elem, host)
        
        # Guess device type from ports and OS
        host.device_type = self._guess_device_type(host)
        host.os_family = self._guess_os_family(host)
        
        return host
    
    def _parse_port_element(self, port_elem: ET.Element, host: DiscoveredHost) -> None:
        """Parse a port element and update host."""
        port_id = port_elem.get("portid")
        if not port_id:
            return
        
        try:
            port_num = int(port_id)
        except ValueError:
            return
        
        # Check if port is open - use local variables for faster lookup
        state_elem = port_elem.find("state")
        if state_elem is not None and state_elem.get("state") == "open":
            host.open_ports.append(port_num)
            
            # Get service name - single lookup
            service_elem = port_elem.find("service")
            if service_elem is not None:
                host.port_services[port_num] = service_elem.get("name", "unknown")
    
    def _parse_os_element(self, os_elem: ET.Element, host: DiscoveredHost) -> None:
        """Parse OS detection element."""
        # Get the most likely OS match
        osmatch = os_elem.find("osmatch")
        if osmatch is not None:
            host.os_guess = osmatch.get("name")
            accuracy = osmatch.get("accuracy")
            if accuracy:
                try:
                    host.os_accuracy = int(accuracy)
                except ValueError:
                    pass
            
            # Get OS family
            osclass = osmatch.find("osclass")
            if osclass is not None:
                host.os_family = osclass.get("osfamily")
    
    def _guess_device_type(self, host: DiscoveredHost) -> str:
        """Guess device type based on ports and OS."""
        ports = host.open_ports  # Use list directly, avoid set creation overhead
        os_guess = (host.os_guess or "").lower()
        
        # Router indicators - use simple 'in' checks for small lists
        if 8291 in ports:  # Winbox (MikroTik)
            return "router"
        if "cisco ios" in os_guess or "router" in os_guess:
            return "router"
        
        # Firewall indicators
        if "firewall" in os_guess:
            if 443 in ports or 8443 in ports:
                return "firewall"
        if "asa" in os_guess:
            return "firewall"
        
        # Switch indicators
        if "switch" in os_guess:
            return "switch"
        
        # Server indicators - check OS first (cheaper), then ports
        if "windows" in os_guess or "linux" in os_guess or "unix" in os_guess:
            if any(p in ports for p in (22, 80, 443, 3389)):
                return "server"
        
        # Default to unknown
        return "unknown"
    
    def _guess_os_family(self, host: DiscoveredHost) -> str:
        """Guess OS family."""
        if host.os_family:
            return host.os_family
        
        os_guess = (host.os_guess or "").lower()
        
        # Use tuple of (keyword, result) for efficient checking
        os_checks = (
            ("cisco", "Cisco IOS"),
            ("juniper", "Juniper"),
            ("linux", "Linux"),
            ("windows", "Windows"),
            ("mikrotik", "MikroTik"),
            ("fortinet", "Fortinet"),
            ("fortios", "Fortinet"),
        )
        
        for keyword, result in os_checks:
            if keyword in os_guess:
                return result
        
        return "Unknown"
    
    def get_local_subnets(self) -> list[str]:
        """
        Get list of local network subnets.
        Uses ip route / ifconfig to determine local networks.
        
        Returns:
            List of CIDR network strings
        """
        subnets = []
        
        try:
            # Try ip route first (Linux)
            result = subprocess.run(
                ["ip", "route", "show"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                # Parse routes - compile regex once for efficiency
                pattern = re.compile(r"(\d+\.\d+\.\d+\.\d+/\d+)")
                
                for line in result.stdout.split("\n"):
                    # Look for lines like: 192.168.1.0/24 dev eth0
                    if "linkdown" not in line:
                        match = pattern.search(line)
                        if match:
                            subnet = match.group(1)
                            # Skip loopback and link-local (cheaper string prefix check)
                            if not subnet.startswith(("127.", "169.254.")):
                                subnets.append(subnet)
            
        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            logger.debug(f"Could not get local subnets: {e}")
        
        # Fallback to common private subnets if nothing found
        return subnets if subnets else ["192.168.1.0/24", "10.0.0.0/24", "172.16.0.0/24"]


def quick_scan(target: str, session_id: str) -> ScanResult:
    """
    Convenience function for quick scanning.
    
    Args:
        target: Network to scan (e.g., "192.168.1.0/24")
        session_id: Audit session ID
    
    Returns:
        ScanResult
    """
    scanner = NmapScanner()
    return scanner.scan_subnet(target, session_id, scan_type="quick")


def comprehensive_scan(target: str, session_id: str) -> ScanResult:
    """
    Convenience function for comprehensive scanning.
    
    Args:
        target: Network to scan
        session_id: Audit session ID
    
    Returns:
        ScanResult
    """
    scanner = NmapScanner()
    return scanner.scan_subnet(target, session_id, scan_type="comprehensive")
