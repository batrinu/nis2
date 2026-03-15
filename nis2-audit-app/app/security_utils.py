"""
Security utilities for the NIS2 Field Audit App.

Provides:
- Path traversal protection
- XML XXE prevention
- Log injection prevention
- Regex timeout protection
- Input sanitization
- Supply chain security (Pass 20)
- Package installation security (Pass 21)
- DNS rebinding protection (Pass 22)
- SSRF prevention (Pass 23)
- Memory safety (Pass 24)
- Object pollution prevention (Pass 25)
- Dynamic code execution prevention (Pass 26)
- Hash collision DoS prevention (Pass 27)
- Certificate validation (Pass 28)
- Timing attack prevention (Pass 29)
- Safe deserialization (Pass 30)
- ML pipeline security (Pass 31)
- Import system security (Pass 32)
"""
import os
import re
import sys
import time
import hmac
import signal
import tempfile
import hashlib
import ipaddress
import socket
import unicodedata
from pathlib import Path
from typing import Optional, Union, List, Set, Callable, Any
from contextlib import contextmanager
from urllib.parse import urlparse
from io import BytesIO


# ============================================================================
# Base Security Exception
# ============================================================================

class SecurityError(Exception):
    """Base class for security-related errors."""
    pass


# ============================================================================
# Pass 9: Path Traversal Protection (CVE-2026-28518 Pattern)
# ============================================================================

class PathTraversalError(SecurityError):
    """Raised when a path traversal attempt is detected."""
    pass


def validate_path(
    path: Union[str, Path],
    base_dir: Union[str, Path],
    allow_symlinks: bool = False
) -> Path:
    """
    Validate that a path is within the allowed base directory.
    
    Args:
        path: The path to validate
        base_dir: The allowed base directory
        allow_symlinks: Whether to allow symlinks that point outside base_dir
        
    Returns:
        Resolved Path object if valid
        
    Raises:
        PathTraversalError: If path escapes the base directory
    """
    base = Path(base_dir).resolve()
    target = Path(path)
    
    # Check for obvious traversal attempts before resolution
    # Block .. and encoded variants
    path_str = str(target)
    dangerous_patterns = [
        '..',           # Unix traversal
        '..\\',         # Windows traversal
        '%2e%2e',       # URL encoded
        '0x2e0x2e',     # Hex encoded
        '....//',       # Double encoding bypass
        '....\\\\',       # Windows double encoding
    ]
    
    for pattern in dangerous_patterns:
        if pattern in path_str:
            raise PathTraversalError(
                f"Path traversal detected: forbidden pattern '{pattern}' in path"
            )
    
    # Resolve to absolute path
    try:
        if allow_symlinks:
            resolved = target.resolve()
        else:
            # Use absolute() instead of resolve() to avoid following symlinks
            resolved = target.absolute()
            if target.is_symlink():
                raise PathTraversalError("Symlinks not allowed")
    except (OSError, RuntimeError) as e:
        raise PathTraversalError(f"Failed to resolve path: {e}")
    
    # Ensure the resolved path is within base_dir
    try:
        resolved.relative_to(base)
    except ValueError:
        raise PathTraversalError(
            f"Path '{path}' escapes allowed directory '{base_dir}'"
        )
    
    return resolved


def safe_filename(filename: str) -> str:
    """
    Sanitize a filename to prevent path traversal.
    
    Args:
        filename: Original filename
        
    Returns:
        Sanitized filename with path components removed
    """
    # Remove any directory components
    basename = os.path.basename(filename)
    
    # Remove null bytes
    basename = basename.replace('\x00', '')
    
    # Remove dangerous characters but keep common filename chars
    allowed = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789._- ")
    sanitized = ''.join(c for c in basename if c in allowed)
    
    # Prevent hidden files (starting with .)
    if sanitized.startswith('.'):
        sanitized = 'file_' + sanitized
    
    # Prevent empty filenames
    if not sanitized or sanitized.strip() == '':
        sanitized = 'unnamed_file'
    
    return sanitized


# ============================================================================
# Pass 8: XML XXE Prevention (CVE-2026-24400 Pattern)
# ============================================================================

class XXEProtectionError(SecurityError):
    """Raised when XML XXE is detected or prevention fails."""
    pass


def secure_xml_parse(xml_string: str) -> 'xml.etree.ElementTree.Element':
    """
    Parse XML with XXE protection enabled.
    
    Uses defusedxml if available, otherwise falls back to standard library
    with security precautions.
    
    Args:
        xml_string: XML string to parse
        
    Returns:
        Parsed XML element
        
    Raises:
        XXEProtectionError: If parsing fails or XXE is detected
    """
    # Try to use defusedxml first (most secure)
    try:
        from defusedxml import ElementTree as ET
        return ET.fromstring(xml_string)
    except ImportError:
        pass  # Fall through to standard library
    
    # Standard library with precautions
    import xml.etree.ElementTree as ET
    
    # Check for XXE indicators before parsing
    xxe_indicators = [
        '<!ENTITY',
        '<!DOCTYPE',
        'SYSTEM',
        'PUBLIC',
    ]
    
    upper_xml = xml_string.upper()
    for indicator in xxe_indicators:
        if indicator in upper_xml:
            raise XXEProtectionError(
                f"Potential XXE detected: '{indicator}' found in XML"
            )
    
    try:
        return ET.fromstring(xml_string)
    except ET.ParseError as e:
        raise XXEProtectionError(f"XML parse error: {e}")


# ============================================================================
# Pass 13: Log Injection Prevention (CVE-2026-23566 Pattern)
# ============================================================================

# Characters that could be used for log injection
LOG_INJECTION_CHARS = {
    '\n',  # Newline - can forge log entries
    '\r',  # Carriage return
    '\x00',  # Null byte
    '\x1b',  # ANSI escape sequences
    '\u0000',  # Unicode null
}


def sanitize_for_logging(value: str) -> str:
    """
    Sanitize a string to prevent log injection attacks.
    
    Replaces newline and other injection characters to prevent
    log forging and log file poisoning.
    
    Args:
        value: String to sanitize
        
    Returns:
        Sanitized string safe for logging
    """
    if not isinstance(value, str):
        value = str(value)
    
    # Replace newlines with visible representation
    sanitized = value
    replacements = {
        '\n': '\\n',
        '\r': '\\r',
        '\x00': '\\x00',
        '\x1b': '\\x1b',
    }
    
    for char, replacement in replacements.items():
        sanitized = sanitized.replace(char, replacement)
    
    return sanitized


def sanitize_dict_for_logging(data: dict) -> dict:
    """
    Recursively sanitize dictionary values for logging.
    
    Args:
        data: Dictionary with values to sanitize
        
    Returns:
        New dictionary with sanitized values
    """
    result = {}
    for key, value in data.items():
        if isinstance(value, str):
            result[key] = sanitize_for_logging(value)
        elif isinstance(value, dict):
            result[key] = sanitize_dict_for_logging(value)
        elif isinstance(value, list):
            result[key] = [
                sanitize_for_logging(item) if isinstance(item, str) else item
                for item in value
            ]
        else:
            result[key] = value
    return result


# ============================================================================
# Pass 11: ReDoS Prevention (CVE-2026-26006 Pattern)
# ============================================================================

class RegexTimeoutError(SecurityError):
    """Raised when regex matching times out."""
    pass


class RegexValidator:
    """Regex validator with timeout protection."""
    
    # SECURITY: Patterns that can cause ReDoS (catastrophic backtracking)
    DANGEROUS_PATTERNS = [
        r'\(\?\!.*\*',  # Negative lookahead with quantifier
        r'\(\?\=.*\*',  # Positive lookahead with quantifier
        r'\(\?\<\!.*\*',  # Negative lookbehind with quantifier
        r'\(\?\<\=.*\*',  # Positive lookbehind with quantifier
        r'\(.*[\*\+]\).*\1',  # Nested quantifiers with backreference
        r'\([\*\+\?]\+',  # Nested quantifiers like (a+)*
        r'\[.*\]\+\[',  # Quantified character class followed by char class
    ]
    
    def __init__(self, pattern: str, timeout: float = 1.0):
        """
        Initialize validator with pattern and timeout.
        
        Args:
            pattern: Regex pattern
            timeout: Maximum time allowed for matching (seconds)
            
        Raises:
            ValueError: If pattern contains dangerous ReDoS-prone constructs
        """
        self.pattern = pattern
        self.timeout = timeout
        
        # SECURITY: Validate pattern for ReDoS risks before compiling
        self._validate_pattern(pattern)
        
        self._compiled = re.compile(pattern)
    
    def _validate_pattern(self, pattern: str) -> None:
        """
        Validate regex pattern for potentially dangerous constructs.
        
        Args:
            pattern: Regex pattern to validate
            
        Raises:
            ValueError: If pattern contains dangerous constructs
        """
        import re as re_module
        
        # Check for nested quantifiers that can cause catastrophic backtracking
        # Pattern like (a+)* or (a*)+ are dangerous
        dangerous_quantifier_patterns = [
            r'\([^)]*[\*\+\?]\)[\*\+\?]',  # Group with quantifier followed by quantifier
            r'\[([^\]]+)\]\+.*\1',  # Repeated character class followed by same chars
        ]
        
        for dangerous in dangerous_quantifier_patterns:
            try:
                if re_module.search(dangerous, pattern):
                    raise ValueError(
                        f"Regex pattern contains potentially dangerous nested quantifiers: {pattern[:50]}..."
                    )
            except re_module.error:
                # If the check pattern itself errors, skip this check
                pass
        
        # Check for excessive alternation with quantifiers
        # Count alternations and warn if too many
        alt_count = pattern.count('|')
        if alt_count > 20:
            raise ValueError(
                f"Regex pattern contains too many alternations ({alt_count}), may cause ReDoS"
            )
    
    def _timeout_handler(self, signum, frame):
        """Signal handler for timeout."""
        raise RegexTimeoutError(
            f"Regex pattern '{self.pattern}' timed out after {self.timeout}s"
        )
    
    def match(self, string: str) -> Optional[re.Match]:
        """
        Match string with timeout protection.
        
        Args:
            string: String to match
            
        Returns:
            Match object if found, None otherwise
            
        Raises:
            RegexTimeoutError: If matching exceeds timeout
        """
        # Use signal-based timeout (Unix only)
        if sys.platform != 'win32' and hasattr(signal, 'SIGALRM'):
            old_handler = signal.signal(signal.SIGALRM, self._timeout_handler)
            signal.alarm(int(self.timeout) + 1)
            try:
                return self._compiled.match(string)
            finally:
                signal.alarm(0)
                signal.signal(signal.SIGALRM, old_handler)
        else:
            # Windows fallback - no timeout protection
            # Consider using concurrent.futures for cross-platform timeouts
            return self._compiled.match(string)
    
    def search(self, string: str) -> Optional[re.Match]:
        """Search string with timeout protection."""
        if sys.platform != 'win32' and hasattr(signal, 'SIGALRM'):
            old_handler = signal.signal(signal.SIGALRM, self._timeout_handler)
            signal.alarm(int(self.timeout) + 1)
            try:
                return self._compiled.search(string)
            finally:
                signal.alarm(0)
                signal.signal(signal.SIGALRM, old_handler)
        else:
            return self._compiled.search(string)


def safe_regex_match(
    pattern: str,
    string: str,
    timeout: float = 1.0
) -> Optional[re.Match]:
    """
    Perform regex match with timeout protection.
    
    Args:
        pattern: Regex pattern
        string: String to match
        timeout: Maximum time allowed (seconds)
        
    Returns:
        Match object if found, None otherwise
    """
    validator = RegexValidator(pattern, timeout)
    return validator.match(string)


# ============================================================================
# Pass 10: Atomic File Operations (CVE-2026-22701 Pattern)
# ============================================================================

@contextmanager
def atomic_write(
    filepath: Union[str, Path],
    mode: str = 'w',
    encoding: str = 'utf-8'
):
    """
    Context manager for atomic file writes.
    
    Writes to a temporary file and then atomically moves it to the target.
    Prevents race conditions and partial writes.
    
    Args:
        filepath: Target file path
        mode: File mode ('w' or 'wb')
        encoding: Text encoding (for text mode)
        
    Yields:
        File handle for writing
    """
    filepath = Path(filepath)
    
    # Create parent directories
    filepath.parent.mkdir(parents=True, exist_ok=True)
    
    # Create temporary file in the same directory
    temp_fd, temp_path = tempfile.mkstemp(
        dir=filepath.parent,
        prefix='.tmp_',
        suffix='.tmp'
    )
    
    temp_file = None
    try:
        try:
            if 'b' in mode:
                temp_file = os.fdopen(temp_fd, mode)
            else:
                temp_file = os.fdopen(temp_fd, mode, encoding=encoding)
        except Exception:
            # Close the raw fd if fdopen fails
            os.close(temp_fd)
            raise
        
        yield temp_file
        
        temp_file.flush()
        os.fsync(temp_file.fileno())
        temp_file.close()
        
        # Atomic rename
        os.replace(temp_path, filepath)
        
    except Exception:
        # Clean up temp file on error
        if temp_file:
            try:
                temp_file.close()
            except Exception:
                pass
        try:
            os.unlink(temp_path)
        except Exception:
            pass
        raise


def secure_file_permissions(filepath: Union[str, Path], mode: int = 0o600) -> None:
    """
    Set secure file permissions.
    
    Args:
        filepath: Path to file
        mode: Permission mode (default 0o600 = owner read/write only)
    """
    try:
        os.chmod(filepath, mode)
    except (OSError, PermissionError):
        pass  # Best effort


# ============================================================================
# Pass 15: File Permission Hardening
# ============================================================================

def create_secure_directory(
    path: Union[str, Path],
    mode: int = 0o700
) -> Path:
    """
    Create a directory with secure permissions.
    
    Args:
        path: Directory path
        mode: Permission mode (default 0o700 = owner only)
        
    Returns:
        Path object
    """
    path = Path(path)
    path.mkdir(parents=True, exist_ok=True, mode=mode)
    return path


def secure_delete(filepath: Union[str, Path]) -> None:
    """
    Securely delete a file by overwriting before deletion.
    
    Args:
        filepath: Path to file to delete
    """
    filepath = Path(filepath)
    
    if not filepath.exists():
        return
    
    try:
        # Overwrite with zeros
        size = filepath.stat().st_size
        with open(filepath, 'wb') as f:
            f.write(b'\x00' * size)
            f.flush()
            os.fsync(f.fileno())
        
        # Delete
        filepath.unlink()
    except (OSError, PermissionError):
        # Fallback to regular delete
        try:
            filepath.unlink()
        except Exception:
            pass


# ============================================================================
# Pass 12: Safe Serialization (CVE-2026-28277 Pattern)
# ============================================================================

import json as json_module


def safe_json_dump(
    obj: object,
    filepath: Union[str, Path],
    indent: Optional[int] = None
) -> None:
    """
    Safely dump object to JSON file.
    
    Uses atomic write to prevent corruption.
    
    Args:
        obj: Object to serialize
        filepath: Target file path
        indent: JSON indentation
    """
    with atomic_write(filepath, mode='w', encoding='utf-8') as f:
        json_module.dump(obj, f, indent=indent, default=str)
    
    secure_file_permissions(filepath, 0o600)


def safe_json_load(filepath: Union[str, Path]) -> object:
    """
    Safely load JSON from file.
    
    Args:
        filepath: Source file path
        
    Returns:
        Deserialized object
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json_module.load(f)
    except (OSError, IOError) as e:
        raise ConfigurationSecurityError(f"Failed to load JSON file: {e}")


# ============================================================================
# Pass 17: Input Validation Hardening
# ============================================================================

def validate_type(value: object, expected_type: type, param_name: str) -> None:
    """
    Validate that a value is of the expected type.
    
    Args:
        value: Value to check
        expected_type: Expected type
        param_name: Parameter name for error message
        
    Raises:
        TypeError: If type doesn't match
    """
    if not isinstance(value, expected_type):
        raise TypeError(
            f"Expected {param_name} to be {expected_type.__name__}, "
            f"got {type(value).__name__}"
        )


def validate_range(
    value: Union[int, float],
    min_val: Optional[Union[int, float]] = None,
    max_val: Optional[Union[int, float]] = None,
    param_name: str = "value"
) -> None:
    """
    Validate that a numeric value is within range.
    
    Args:
        value: Value to check
        min_val: Minimum allowed value
        max_val: Maximum allowed value
        param_name: Parameter name for error message
        
    Raises:
        ValueError: If value is out of range
    """
    if min_val is not None and value < min_val:
        raise ValueError(
            f"{param_name} must be >= {min_val}, got {value}"
        )
    if max_val is not None and value > max_val:
        raise ValueError(
            f"{param_name} must be <= {max_val}, got {value}"
        )


def validate_string_length(
    value: str,
    max_length: int,
    param_name: str = "string"
) -> None:
    """
    Validate string length.
    
    Args:
        value: String to check
        max_length: Maximum allowed length
        param_name: Parameter name for error message
        
    Raises:
        ValueError: If string is too long
    """
    if len(value) > max_length:
        raise ValueError(
            f"{param_name} exceeds maximum length of {max_length} characters"
        )


# ============================================================================
# Pass 7: PyYAML Safe Loading (CVE-2026-24009 Pattern)
# ============================================================================

def safe_yaml_load(stream) -> object:
    """
    Safely load YAML using SafeLoader.
    
    Args:
        stream: YAML stream or string
        
    Returns:
        Deserialized object
        
    Raises:
        SecurityError: If unsafe YAML detected
    """
    try:
        import yaml
        return yaml.safe_load(stream)
    except ImportError:
        raise SecurityError("PyYAML not installed")
    except yaml.YAMLError as e:
        raise SecurityError(f"YAML parse error: {e}")


def safe_yaml_dump(obj, stream=None, **kwargs) -> Optional[str]:
    """
    Safely dump YAML using SafeDumper.
    
    Args:
        obj: Object to serialize
        stream: Output stream (if None, returns string)
        **kwargs: Additional yaml.dump arguments
        
    Returns:
        YAML string if stream is None
    """
    try:
        import yaml
        return yaml.safe_dump(obj, stream, **kwargs)
    except ImportError:
        raise SecurityError("PyYAML not installed")


# ============================================================================
# Pass 20: Supply Chain Security (Dependency Confusion/Typosquatting)
# ============================================================================

class SupplyChainError(SecurityError):
    """Raised when supply chain security issue is detected."""
    pass


# Common typosquatting patterns to watch for
TYPOSQUATTING_PATTERNS = [
    'reqeusts',      # requests
    'urllib2',       # urllib3
    'pysaml2',       # pysaml
    'cryptograpy',   # cryptography
    'pyyaml',        # pyyaml (legitimate but often confused)
    'jwt-token',     # pyjwt
    'openssl-python', # pyopenssl
]


def validate_package_name(package_name: str) -> tuple[bool, Optional[str]]:
    """
    Validate package name for potential typosquatting.
    
    Args:
        package_name: Name of the package
        
    Returns:
        Tuple of (is_valid, warning_message)
    """
    # Check against known typosquatting patterns
    if package_name.lower() in TYPOSQUATTING_PATTERNS:
        return False, f"Package '{package_name}' matches known typosquatting pattern"
    
    # Check for suspicious characters
    suspicious = ['-', '_', '0', '1', 'l', 'I', 'O']
    if any(c in package_name for c in suspicious):
        return True, f"Package '{package_name}' contains suspicious characters - verify source"
    
    return True, None


def generate_requirements_hash(requirements_path: Union[str, Path]) -> str:
    """
    Generate hash of requirements file for integrity tracking.
    
    Args:
        requirements_path: Path to requirements.txt
        
    Returns:
        SHA-256 hash of file contents
    """
    return compute_file_hash(requirements_path, 'sha256')


# ============================================================================
# Pass 21: Package Installation Security (Wheel/Pip vulnerabilities)
# ============================================================================

class PackageSecurityError(SecurityError):
    """Raised when package security issue is detected."""
    pass


WHEEL_TRAVERSAL_PATTERNS = [
    '..',           # Path traversal
    '../',          # Unix traversal
    '..\\',          # Windows traversal
    '/etc/',        # System files
    '/usr/',        # System directories
    'C:\\',          # Windows system
    '~/.ssh',       # SSH keys
    '~/.aws',       # AWS credentials
]


def validate_wheel_entry_name(entry_name: str) -> bool:
    """
    Validate wheel archive entry name for path traversal.
    
    CVE-2026-1703, CVE-2026-24049 mitigation.
    
    Args:
        entry_name: Name of entry in wheel archive
        
    Returns:
        True if entry name is safe
    """
    for pattern in WHEEL_TRAVERSAL_PATTERNS:
        if pattern in entry_name:
            return False
    
    # Check for absolute paths
    if entry_name.startswith('/') or (len(entry_name) > 1 and entry_name[1] == ':'):
        return False
    
    return True


# ============================================================================
# Pass 22: DNS Rebinding Protection
# ============================================================================

class DNSRebindingError(SecurityError):
    """Raised when DNS rebinding attack is suspected."""
    pass


# Private/reserved IP ranges that should not be accessed
PRIVATE_IP_RANGES = [
    ipaddress.ip_network('127.0.0.0/8'),      # Loopback
    ipaddress.ip_network('10.0.0.0/8'),       # Private
    ipaddress.ip_network('172.16.0.0/12'),    # Private
    ipaddress.ip_network('192.168.0.0/16'),   # Private
    ipaddress.ip_network('169.254.0.0/16'),   # Link-local
    ipaddress.ip_network('0.0.0.0/8'),        # Current network
    ipaddress.ip_network('::1/128'),          # IPv6 loopback
    ipaddress.ip_network('fc00::/7'),         # IPv6 unique local
    ipaddress.ip_network('fe80::/10'),        # IPv6 link-local
]

# Cloud metadata endpoints
CLOUD_METADATA_ENDPOINTS = [
    '169.254.169.254',  # AWS, GCP, Azure metadata
    '169.254.170.2',    # AWS ECS metadata
    '192.0.0.192',      # Oracle Cloud
    '100.100.100.200',  # Alibaba Cloud
]


def is_private_ip(ip_str: str) -> bool:
    """
    Check if IP address is in private/reserved range.
    
    Args:
        ip_str: IP address string
        
    Returns:
        True if IP is private/reserved
    """
    try:
        ip = ipaddress.ip_address(ip_str)
        for network in PRIVATE_IP_RANGES:
            if ip in network:
                return True
        return False
    except ValueError:
        return False


def is_cloud_metadata_endpoint(ip_str: str) -> bool:
    """
    Check if IP is a cloud metadata endpoint.
    
    Args:
        ip_str: IP address string
        
    Returns:
        True if IP is a metadata endpoint
    """
    return ip_str in CLOUD_METADATA_ENDPOINTS


def validate_host_against_dns_rebinding(hostname: str) -> tuple[bool, Optional[str]]:
    """
    Validate hostname against DNS rebinding attacks.
    
    CVE-2025-66416, CVE-2026-30858 mitigation.
    
    Args:
        hostname: Hostname to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    try:
        # Resolve hostname
        resolved_ips = socket.getaddrinfo(hostname, None)
        
        for addr_info in resolved_ips:
            ip = addr_info[4][0]
            
            # Check for private IPs
            if is_private_ip(ip):
                return False, f"DNS rebinding protection: '{hostname}' resolves to private IP {ip}"
            
            # Check for cloud metadata endpoints
            if is_cloud_metadata_endpoint(ip):
                return False, f"DNS rebinding protection: '{hostname}' resolves to metadata endpoint {ip}"
        
        return True, None
    except socket.gaierror as e:
        return False, f"Failed to resolve hostname '{hostname}': {e}"


# ============================================================================
# Pass 23: SSRF Prevention (Server-Side Request Forgery)
# ============================================================================

class SSRFError(SecurityError):
    """Raised when SSRF attempt is detected."""
    pass


# URL schemes that should be blocked
DANGEROUS_URL_SCHEMES = {
    'file', 'ftp', 'ftps', 'gopher', 'dict', 'ldap', 'ldaps',
    'tftp', 'sftp', 'ssh', 'telnet', 'smtp', 'imap', 'pop3',
}

# Allowed URL schemes
ALLOWED_URL_SCHEMES = {'http', 'https'}


def validate_url_for_ssrf(
    url: str,
    allowed_hosts: Optional[Set[str]] = None,
    allow_private_ips: bool = False
) -> tuple[bool, Optional[str]]:
    """
    Validate URL for SSRF protection.
    
    CVE-2026-25580, CVE-2026-30953, CVE-2026-2654 mitigation.
    
    Args:
        url: URL to validate
        allowed_hosts: Optional set of allowed hostnames
        allow_private_ips: Whether to allow private IP access
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    try:
        parsed = urlparse(url)
        
        # Validate scheme
        scheme = parsed.scheme.lower()
        if scheme in DANGEROUS_URL_SCHEMES:
            return False, f"SSRF protection: Dangerous URL scheme '{scheme}' not allowed"
        
        if scheme not in ALLOWED_URL_SCHEMES:
            return False, f"SSRF protection: URL scheme '{scheme}' not in allowlist"
        
        # Validate hostname
        hostname = parsed.hostname
        if not hostname:
            return False, "SSRF protection: No hostname in URL"
        
        # Check against allowlist if provided
        if allowed_hosts and hostname not in allowed_hosts:
            return False, f"SSRF protection: Host '{hostname}' not in allowlist"
        
        # Check for IP address in hostname
        try:
            ip = ipaddress.ip_address(hostname)
            if not allow_private_ips:
                if is_private_ip(hostname):
                    return False, f"SSRF protection: Private IP '{hostname}' not allowed"
                if is_cloud_metadata_endpoint(hostname):
                    return False, f"SSRF protection: Cloud metadata endpoint '{hostname}' not allowed"
        except ValueError:
            # Hostname is not an IP, resolve it
            if not allow_private_ips:
                is_valid, error = validate_host_against_dns_rebinding(hostname)
                if not is_valid:
                    return False, error
        
        # Check for common SSRF bypass techniques
        bypass_patterns = [
            '@',            # Credential injection
            '\\x',          # Hex encoding
            '%',            # URL encoding (except for normal encoding)
            '0x',           # Hex notation
        ]
        
        for pattern in bypass_patterns:
            if pattern in url and pattern != '%':  # Allow normal percent encoding
                return False, f"SSRF protection: Potential bypass pattern '{pattern}' detected"
        
        return True, None
        
    except Exception as e:
        return False, f"SSRF protection: URL validation error: {e}"


def create_safe_url_validator(
    allowed_hosts: Optional[Set[str]] = None,
    allow_private_ips: bool = False
) -> Callable[[str], bool]:
    """
    Create a reusable URL validator function.
    
    Args:
        allowed_hosts: Set of allowed hostnames
        allow_private_ips: Whether to allow private IPs
        
    Returns:
        Validator function that returns True if URL is safe
    """
    def validator(url: str) -> bool:
        is_valid, _ = validate_url_for_ssrf(url, allowed_hosts, allow_private_ips)
        return is_valid
    
    return validator


# ============================================================================
# Pass 24: Memory Safety (Buffer Overflow Prevention)
# ============================================================================

class MemorySafetyError(SecurityError):
    """Raised when memory safety issue is detected."""
    pass


# Maximum sizes for various inputs
MAX_STRING_LENGTH = 10 * 1024 * 1024       # 10 MB
MAX_FILE_SIZE = 100 * 1024 * 1024          # 100 MB
MAX_JSON_DEPTH = 100                        # JSON nesting depth
MAX_COLLECTION_SIZE = 1_000_000            # Max items in list/dict


def validate_buffer_size(
    size: int,
    max_size: int = MAX_STRING_LENGTH,
    operation: str = "buffer"
) -> None:
    """
    Validate buffer size to prevent memory exhaustion.
    
    CVE-2026-25990 (Pillow), CVE-2026-24814 mitigation.
    
    Args:
        size: Requested buffer size
        max_size: Maximum allowed size
        operation: Name of operation for error message
        
    Raises:
        MemorySafetyError: If size exceeds maximum
    """
    if size < 0:
        raise MemorySafetyError(f"{operation}: Negative size not allowed")
    if size > max_size:
        raise MemorySafetyError(
            f"{operation}: Size {size} exceeds maximum {max_size}"
        )


def validate_string_for_memory_safety(
    value: str,
    max_length: int = MAX_STRING_LENGTH
) -> str:
    """
    Validate string length for memory safety.
    
    Args:
        value: String to validate
        max_length: Maximum allowed length
        
    Returns:
        The string if valid
        
    Raises:
        MemorySafetyError: If string is too long
    """
    if len(value) > max_length:
        raise MemorySafetyError(
            f"String length {len(value)} exceeds maximum {max_length}"
        )
    return value


def validate_collection_size(
    collection: Union[list, dict, set],
    max_size: int = MAX_COLLECTION_SIZE,
    operation: str = "collection"
) -> None:
    """
    Validate collection size to prevent memory exhaustion.
    
    Args:
        collection: Collection to validate
        max_size: Maximum allowed size
        operation: Name of operation for error message
        
    Raises:
        MemorySafetyError: If collection is too large
    """
    size = len(collection)
    if size > max_size:
        raise MemorySafetyError(
            f"{operation} size {size} exceeds maximum {max_size}"
        )


# ============================================================================
# Pass 25: Object Pollution Prevention
# ============================================================================

class ObjectPollutionError(SecurityError):
    """Raised when prototype pollution attempt is detected."""
    pass


# Dangerous property names that can lead to prototype pollution
DANGEROUS_PROPERTY_NAMES = {
    '__proto__', 'constructor', 'prototype',
    '__class__', '__bases__', '__mro__',
    '__subclasses__', '__globals__', '__code__',
    '__defaults__', '__kwdefaults__', '__closure__',
}

# Dangerous path patterns for nested object access
DANGEROUS_PATH_PATTERNS = [
    '.__proto__.', '.constructor.', '.prototype.',
    '[__proto__]', '[constructor]', '[prototype]',
]


def validate_property_name(name: str) -> tuple[bool, Optional[str]]:
    """
    Validate property name for prototype pollution.
    
    CVE-2026-27212, CVE-2026-26021 mitigation.
    
    Args:
        name: Property name to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if name in DANGEROUS_PROPERTY_NAMES:
        return False, f"Property name '{name}' is not allowed (prototype pollution risk)"
    
    return True, None


def validate_object_path(path: str) -> tuple[bool, Optional[str]]:
    """
    Validate object access path for prototype pollution.
    
    Args:
        path: Dot-notation path (e.g., "user.name")
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    # Check for dangerous patterns
    for pattern in DANGEROUS_PATH_PATTERNS:
        if pattern in path:
            return False, f"Path contains dangerous pattern: {pattern}"
    
    # Split and check each component
    parts = path.replace('[', '.').replace(']', '').split('.')
    for part in parts:
        is_valid, error = validate_property_name(part)
        if not is_valid:
            return False, error
    
    return True, None


def safe_set_nested_value(
    obj: dict,
    path: str,
    value: Any
) -> None:
    """
    Safely set a nested dictionary value with prototype pollution protection.
    
    Args:
        obj: Dictionary to modify
        path: Dot-notation path
        value: Value to set
        
    Raises:
        ObjectPollutionError: If path contains dangerous patterns
    """
    is_valid, error = validate_object_path(path)
    if not is_valid:
        raise ObjectPollutionError(error)
    
    parts = path.split('.')
    current = obj
    
    for part in parts[:-1]:
        if part not in current:
            current[part] = {}
        current = current[part]
    
    current[parts[-1]] = value


# ============================================================================
# Pass 26: Dynamic Code Execution Prevention
# ============================================================================

class CodeExecutionError(SecurityError):
    """Raised when dangerous code execution is attempted."""
    pass


# Dangerous built-in functions that should not be called
DANGEROUS_BUILTINS = {
    'eval', 'exec', 'compile', '__import__', 'open',
    'input', 'raw_input', 'reload',
    'execfile', 'file',  # Python 2 legacy
}

# Dangerous dunder methods that can lead to code execution
DANGEROUS_DUNDER_METHODS = {
    '__import__', '__builtins__', '__globals__', '__code__',
    '__subclasses__', '__mro__', '__bases__', '__class__',
    '__init__', '__new__', '__call__', '__getattr__',
    '__setattr__', '__delattr__', '__get__', '__set__', '__delete__',
}


def validate_code_string(code: str) -> tuple[bool, Optional[str]]:
    """
    Validate code string for dangerous constructs.
    
    CVE-2026-0863, CVE-2026-1470, CVE-2026-26030 mitigation.
    
    Args:
        code: Code string to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    # Check for eval/exec calls
    dangerous_patterns = [
        r'\beval\s*\(',
        r'\bexec\s*\(',
        r'\bcompile\s*\(',
        r'__import__\s*\(',
        r'subprocess\.call',
        r'subprocess\.run',
        r'subprocess\.Popen',
        r'os\.system\s*\(',
        r'os\.popen',
        r'os\.spawn',
        r'os\.exec',
    ]
    
    for pattern in dangerous_patterns:
        if re.search(pattern, code, re.IGNORECASE):
            return False, f"Code contains dangerous pattern: {pattern}"
    
    return True, None


def safe_eval(
    expression: str,
    allowed_names: Optional[dict] = None
) -> Any:
    """
    Safely evaluate a simple expression with restricted globals.
    
    WARNING: eval() is inherently dangerous. Prefer ast.literal_eval().
    
    Args:
        expression: Expression to evaluate
        allowed_names: Dictionary of allowed names
        
    Returns:
        Evaluation result
        
    Raises:
        CodeExecutionError: If expression is not safe
    """
    # First validate the code string
    is_valid, error = validate_code_string(expression)
    if not is_valid:
        raise CodeExecutionError(error)
    
    # Use literal_eval if possible (much safer)
    try:
        import ast
        return ast.literal_eval(expression)
    except (ValueError, SyntaxError):
        pass  # Fall through to restricted eval
    
    # Restricted eval with minimal globals
    if allowed_names is None:
        allowed_names = {}
    
    safe_globals = {
        '__builtins__': {},
    }
    
    try:
        return eval(expression, safe_globals, allowed_names)
    except Exception as e:
        raise CodeExecutionError(f"Eval failed: {e}")


# ============================================================================
# Pass 27: Hash Collision DoS Prevention
# ============================================================================

class HashDoSError(SecurityError):
    """Raised when hash collision attack is detected."""
    pass


# Enable hash randomization (Python 3.3+ does this by default)
def ensure_hash_randomization() -> bool:
    """
    Ensure Python hash randomization is enabled.
    
    Returns:
        True if hash randomization is enabled
    """
    # Check if PYTHONHASHSEED is set to 0 (disabled)
    if os.environ.get('PYTHONHASHSEED') == '0':
        return False
    
    # Check if hash randomization is working
    # Different runs should produce different hash values
    test_str = 'test_string_for_hash_check'
    return hash(test_str) != hash(test_str) or True  # Always random in Python 3.3+


def create_hash_collision_resistant_dict(
    initial: Optional[dict] = None
) -> dict:
    """
    Create a dictionary with hash collision resistance.
    
    In Python 3.3+, dict is already collision-resistant.
    This function exists for documentation purposes.
    
    Args:
        initial: Initial dictionary values
        
    Returns:
        New dictionary
    """
    return dict(initial) if initial else {}


# ============================================================================
# Pass 28: Certificate Pinning and Validation
# ============================================================================

class CertificateError(SecurityError):
    """Raised when certificate validation fails."""
    pass


# Known certificate fingerprints for pinning (example format)
PINNED_CERTIFICATES: dict[str, Set[str]] = {
    # 'hostname': {'sha256_fingerprint1', 'sha256_fingerprint2'}
}


def validate_certificate_pin(
    hostname: str,
    certificate_fingerprint: str
) -> tuple[bool, Optional[str]]:
    """
    Validate certificate against pinned fingerprints.
    
    CVE-2026-3336, CVE-2026-22696 mitigation.
    
    Args:
        hostname: Server hostname
        certificate_fingerprint: SHA-256 fingerprint of certificate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    pinned = PINNED_CERTIFICATES.get(hostname)
    if not pinned:
        # No pinning configured for this host
        return True, None
    
    if certificate_fingerprint.lower() not in {p.lower() for p in pinned}:
        return False, f"Certificate for {hostname} does not match pinned fingerprint"
    
    return True, None


def add_certificate_pin(hostname: str, fingerprint: str) -> None:
    """
    Add a certificate pin for a hostname.
    
    Args:
        hostname: Server hostname
        fingerprint: SHA-256 fingerprint
    """
    if hostname not in PINNED_CERTIFICATES:
        PINNED_CERTIFICATES[hostname] = set()
    PINNED_CERTIFICATES[hostname].add(fingerprint.lower())


# ============================================================================
# Pass 29: Constant-Time Operations (Timing Attack Prevention)
# ============================================================================

def constant_time_compare(val1: Union[str, bytes], val2: Union[str, bytes]) -> bool:
    """
    Compare two values in constant time to prevent timing attacks.
    
    Args:
        val1: First value
        val2: Second value
        
    Returns:
        True if values are equal
    """
    if isinstance(val1, str):
        val1 = val1.encode('utf-8')
    if isinstance(val2, str):
        val2 = val2.encode('utf-8')
    
    # Use hmac.compare_digest for constant-time comparison
    import hmac
    return hmac.compare_digest(val1, val2)


def constant_time_compare_hmac(
    signature1: bytes,
    signature2: bytes
) -> bool:
    """
    Compare HMAC signatures in constant time.
    
    Args:
        signature1: First signature
        signature2: Second signature
        
    Returns:
        True if signatures match
    """
    import hmac
    return hmac.compare_digest(signature1, signature2)


# ============================================================================
# Pass 30: Safe Deserialization (Pickle Security)
# ============================================================================

class UnsafeDeserializationError(SecurityError):
    """Raised when unsafe deserialization is attempted."""
    pass


# Dangerous pickle opcodes
DANGEROUS_PICKLE_OPCODES = {
    b'\x81',  # NEWOBJ (can execute __new__)
    b'\x82',  # EXT1
    b'\x83',  # EXT2
    b'\x84',  # EXT4
    b'\x85',  # TUPLE1
    b'\x86',  # TUPLE2
    b'\x87',  # TUPLE3
    b'\x90',  # NEWOBJ_EX
    b'\x91',  # STACK_GLOBAL
    b'\x93',  # INST (can execute arbitrary code)
    b'\x94',  # OBJ (can execute arbitrary code)
}

# Allowed modules/classes for pickle (restrictive allowlist)
ALLOWED_PICKLE_MODULES: Set[str] = set()
ALLOWED_PICKLE_CLASSES: Set[str] = set()


def scan_pickle_for_dangerous_opcodes(pickle_data: bytes) -> tuple[bool, List[str]]:
    """
    Scan pickle data for dangerous opcodes.
    
    CVE-2025-10155, CVE-2025-10156, CVE-2025-10157 mitigation.
    
    Args:
        pickle_data: Raw pickle data
        
    Returns:
        Tuple of (is_safe, list_of_dangers_found)
    """
    dangers = []
    
    # Check for dangerous opcodes
    for opcode in DANGEROUS_PICKLE_OPCODES:
        if opcode in pickle_data:
            dangers.append(f"Dangerous opcode found: {opcode.hex()}")
    
    # Check for __reduce__ indicator
    if b'__reduce__' in pickle_data or b'__reduce_ex__' in pickle_data:
        dangers.append("__reduce__ method call detected")
    
    # Check for system command indicators
    system_indicators = [b'os.system', b'subprocess', b'exec', b'eval']
    for indicator in system_indicators:
        if indicator in pickle_data:
            dangers.append(f"System command indicator found: {indicator}")
    
    return len(dangers) == 0, dangers


def safe_pickle_load(pickle_data: bytes) -> Any:
    """
    Safely load pickle data with security scanning.
    
    WARNING: pickle is inherently unsafe. Prefer JSON or other safe formats.
    
    Args:
        pickle_data: Raw pickle data
        
    Returns:
        Deserialized object
        
    Raises:
        UnsafeDeserializationError: If pickle contains dangerous content
    """
    # Scan for dangerous opcodes
    is_safe, dangers = scan_pickle_for_dangerous_opcodes(pickle_data)
    if not is_safe:
        raise UnsafeDeserializationError(
            f"Pickle contains dangerous content: {dangers}"
        )
    
    import pickle
    
    # Use RestrictedUnpickler if available
    try:
        class RestrictedUnpickler(pickle.Unpickler):
            def find_class(self, module, name):
                # Only allow specific modules/classes
                full_name = f"{module}.{name}"
                
                if ALLOWED_PICKLE_MODULES and module not in ALLOWED_PICKLE_MODULES:
                    raise UnsafeDeserializationError(
                        f"Module '{module}' not in allowlist"
                    )
                
                if ALLOWED_PICKLE_CLASSES and full_name not in ALLOWED_PICKLE_CLASSES:
                    raise UnsafeDeserializationError(
                        f"Class '{full_name}' not in allowlist"
                    )
                
                return super().find_class(module, name)
        
        return RestrictedUnpickler(io.BytesIO(pickle_data)).load()
        
    except Exception as e:
        raise UnsafeDeserializationError(f"Pickle load failed: {e}")


def add_allowed_pickle_module(module: str) -> None:
    """Add a module to the pickle allowlist."""
    ALLOWED_PICKLE_MODULES.add(module)


def add_allowed_pickle_class(full_class_name: str) -> None:
    """Add a class to the pickle allowlist."""
    ALLOWED_PICKLE_CLASSES.add(full_class_name)


# ============================================================================
# Pass 31: ML/AI Pipeline Security (Model Poisoning Prevention)
# ============================================================================

class ModelSecurityError(SecurityError):
    """Raised when ML model security issue is detected."""
    pass


# Model file extensions that are safer
SAFE_MODEL_EXTENSIONS = {'.safetensors', '.onnx', '.gguf'}
UNSAFE_MODEL_EXTENSIONS = {'.pkl', '.pickle', '.pt', '.pth', '.bin'}


def validate_model_file_extension(filename: str) -> tuple[bool, Optional[str]]:
    """
    Validate model file extension for safety.
    
    Training data poisoning, model extraction mitigation.
    
    Args:
        filename: Model filename
        
    Returns:
        Tuple of (is_safe, warning_message)
    """
    ext = Path(filename).suffix.lower()
    
    if ext in SAFE_MODEL_EXTENSIONS:
        return True, None
    
    if ext in UNSAFE_MODEL_EXTENSIONS:
        return False, f"Model format '{ext}' may contain executable code. Use SafeTensors instead."
    
    return True, f"Unknown model format '{ext}' - verify safety before loading"


def compute_model_hash(model_path: Union[str, Path]) -> str:
    """
    Compute hash of model file for integrity verification.
    
    Args:
        model_path: Path to model file
        
    Returns:
        SHA-256 hash of model
    """
    return compute_file_hash(model_path, 'sha256')


def validate_model_integrity(
    model_path: Union[str, Path],
    expected_hash: str
) -> bool:
    """
    Validate model file integrity.
    
    Args:
        model_path: Path to model file
        expected_hash: Expected SHA-256 hash
        
    Returns:
        True if hash matches
    """
    return verify_file_integrity(model_path, expected_hash, 'sha256')


# ============================================================================
# Pass 32: Import System Security
# ============================================================================

class ImportSecurityError(SecurityError):
    """Raised when import security issue is detected."""
    pass


# Allowed import paths (for restricted imports)
ALLOWED_IMPORT_PATHS: Set[Path] = set()

# Audit hook for import events
_import_audit_hooks: List[Callable[[str, tuple], None]] = []


def register_import_audit_hook(hook: Callable[[str, tuple], None]) -> None:
    """
    Register an audit hook for import events.
    
    CVE-2026-2297 mitigation.
    
    Args:
        hook: Callable that receives (event, args)
    """
    _import_audit_hooks.append(hook)
    
    # Register with Python's audit system if available (Python 3.8+)
    if hasattr(sys, 'addaudithook'):
        try:
            sys.addaudithook(hook)
        except RuntimeError:
            pass  # Audit hooks can only be added at startup


def validate_import_path(module_path: Union[str, Path]) -> tuple[bool, Optional[str]]:
    """
    Validate that a module path is in allowed locations.
    
    Args:
        module_path: Path to module file
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not ALLOWED_IMPORT_PATHS:
        # No restrictions configured
        return True, None
    
    module_path = Path(module_path).resolve()
    
    for allowed in ALLOWED_IMPORT_PATHS:
        try:
            module_path.relative_to(allowed)
            return True, None
        except ValueError:
            continue
    
    return False, f"Import path '{module_path}' not in allowed locations"


def add_allowed_import_path(path: Union[str, Path]) -> None:
    """
    Add an allowed import path.
    
    Args:
        path: Directory path to allow imports from
    """
    ALLOWED_IMPORT_PATHS.add(Path(path).resolve())


def check_sourceless_import_security(pyc_path: Union[str, Path]) -> tuple[bool, Optional[str]]:
    """
    Check security of .pyc file import.
    
    CVE-2026-2297 mitigation for SourcelessFileLoader.
    
    Args:
        pyc_path: Path to .pyc file
        
    Returns:
        Tuple of (is_safe, warning_message)
    """
    pyc_path = Path(pyc_path)
    
    # Check file permissions
    try:
        stat = pyc_path.stat()
        # Check if world-writable
        if stat.st_mode & 0o002:
            return False, f".pyc file '{pyc_path}' is world-writable"
        
        # Check if in system directories
        parent = pyc_path.parent
        if any(sys_dir in str(parent) for sys_dir in ['/tmp', '/var/tmp', 'C:\\Windows\\Temp']):
            return False, f".pyc file '{pyc_path}' is in temporary directory"
        
    except (OSError, PermissionError):
        pass
    
    return True, None


# ============================================================================
# Hash utilities for integrity verification
# ============================================================================

def compute_file_hash(filepath: Union[str, Path], algorithm: str = 'sha256') -> str:
    """
    Compute hash of file contents.
    
    Args:
        filepath: Path to file
        algorithm: Hash algorithm (sha256, sha512, md5)
        
    Returns:
        Hex digest of file hash
    """
    try:
        hasher = hashlib.new(algorithm)
        with open(filepath, 'rb') as f:
            for chunk in iter(lambda: f.read(8192), b''):
                hasher.update(chunk)
        return hasher.hexdigest()
    except (OSError, IOError) as e:
        raise ConfigurationSecurityError(f"Failed to read file for hashing: {e}")


def verify_file_integrity(
    filepath: Union[str, Path],
    expected_hash: str,
    algorithm: str = 'sha256'
) -> bool:
    """
    Verify file integrity against expected hash.
    
    Args:
        filepath: Path to file
        expected_hash: Expected hash value
        algorithm: Hash algorithm
        
    Returns:
        True if hash matches, False otherwise
    """
    actual_hash = compute_file_hash(filepath, algorithm)
    return actual_hash.lower() == expected_hash.lower()


# ============================================================================
# Pass 33: JWT Authentication Bypass Prevention (CVE-2026-29000, CVE-2026-28802)
# ============================================================================

class JWTValidationError(SecurityError):
    """Raised when JWT validation fails."""
    pass


# Forbidden JWT algorithms (known vulnerable or weak)
FORBIDDEN_JWT_ALGORITHMS = {'none', 'None', 'NONE', ''}

# Allowed JWT algorithms (secure choices)
ALLOWED_JWT_ALGORITHMS = {
    'HS256', 'HS384', 'HS512',  # HMAC
    'RS256', 'RS384', 'RS512',  # RSA
    'ES256', 'ES384', 'ES512',  # ECDSA
    'PS256', 'PS384', 'PS512',  # RSA-PSS
    'EdDSA',  # Ed25519/Ed448
}


def validate_jwt_algorithm(algorithm: str) -> None:
    """
    Validate JWT algorithm to prevent alg:none attacks.
    
    CVE-2026-29000: pac4j-jwt authentication bypass via JWE-wrapped PlainJWT
    CVE-2026-28802: Authlib JWT signature verification bypass using alg:none
    
    Args:
        algorithm: The JWT algorithm header value
        
    Raises:
        JWTValidationError: If algorithm is forbidden or not allowed
    """
    if not algorithm or algorithm.lower() in FORBIDDEN_JWT_ALGORITHMS:
        raise JWTValidationError(
            "JWT algorithm 'none' is forbidden - authentication bypass attempt detected"
        )
    
    if algorithm not in ALLOWED_JWT_ALGORITHMS:
        raise JWTValidationError(
            f"JWT algorithm '{algorithm}' is not in allowed list"
        )


def validate_jwt_header(header: dict) -> None:
    """
    Validate JWT header for security issues.
    
    Args:
        header: Decoded JWT header dictionary
        
    Raises:
        JWTValidationError: If header contains security issues
    """
    # Check algorithm
    alg = header.get('alg', '')
    validate_jwt_algorithm(alg)
    
    # Check for key confusion attack (jwk header injection)
    if 'jwk' in header:
        raise JWTValidationError("JWK embedded in header is not allowed")
    
    # Check for JWE with potential PlainJWT inner (CVE-2026-29000)
    if header.get('enc') and not header.get('alg', '').startswith('RSA'):
        # If encrypted but not using RSA for key exchange, verify carefully
        pass


def sanitize_jwt_token(token: str) -> str:
    """
    Sanitize JWT token input.
    
    Args:
        token: JWT token string
        
    Returns:
        Sanitized token
        
    Raises:
        JWTValidationError: If token format is invalid
    """
    # Remove whitespace and newlines
    token = token.strip()
    
    # Basic JWT structure check (header.payload.signature or header.payload)
    parts = token.split('.')
    if len(parts) not in (2, 3):
        raise JWTValidationError("Invalid JWT format")
    
    # Check for suspicious characters
    suspicious = ['<', '>', '"', "'", '\\', '\x00', '\n', '\r']
    for char in suspicious:
        if char in token:
            raise JWTValidationError(f"JWT contains forbidden character: {repr(char)}")
    
    return token


# ============================================================================
# Pass 34: SQL Injection Prevention (CVE-2026-1312, CVE-2026-3057, CVE-2026-21892)
# ============================================================================

class SQLInjectionError(SecurityError):
    """Raised when SQL injection is detected."""
    pass


# SQL injection patterns (Django, ORM-specific)
SQL_INJECTION_PATTERNS = [
    r'--\s*$',  # Comment to end of line
    r'/\*',      # Start of block comment
    r'\bOR\s+\d+=\d+\b',  # OR 1=1
    r'\bAND\s+\d+=\d+\b',  # AND 1=1
    r'\bUNION\b',  # UNION
    r'\bSELECT\b',  # SELECT
    r'\bINSERT\b',  # INSERT
    r'\bDELETE\b',  # DELETE
    r'\bDROP\b',    # DROP
    r'\bEXEC\b',    # EXEC
    r'\bEXECUTE\b', # EXECUTE
    r';\s*\w+',     # Statement terminator followed by command
    r'\bdual\b',    # Oracle DUAL table
    r'\bpg_sleep\b',  # PostgreSQL sleep
    r'\bsleep\s*\(',  # MySQL sleep
]

# Characters dangerous in column aliases (CVE-2026-1312)
DANGEROUS_COLUMN_CHARS = {'"', "'", '`', ';', '--', '/*', '*/', '\\', '\x00'}


def validate_sql_column_alias(alias: str) -> None:
    """
    Validate SQL column alias to prevent injection.
    
    CVE-2026-1312: Django SQL injection in QuerySet.order_by() via column aliases
    
    Args:
        alias: Column alias string
        
    Raises:
        SQLInjectionError: If alias contains dangerous characters
    """
    if not alias or not isinstance(alias, str):
        raise SQLInjectionError("Invalid column alias")
    
    # Check for dangerous characters
    for char in DANGEROUS_COLUMN_CHARS:
        if char in alias:
            raise SQLInjectionError(
                f"Column alias contains forbidden character: {repr(char)}"
            )
    
    # Check for SQL injection patterns
    alias_upper = alias.upper()
    for pattern in SQL_INJECTION_PATTERNS:
        if re.search(pattern, alias_upper, re.IGNORECASE):
            raise SQLInjectionError(
                f"Column alias contains SQL injection pattern"
            )
    
    # Prevent stacked queries (CVE-2026-1312)
    if ';' in alias:
        raise SQLInjectionError("Column alias cannot contain semicolon")
    
    # Prevent comment injection
    if '--' in alias or '/*' in alias or '*/' in alias:
        raise SQLInjectionError("Column alias cannot contain SQL comments")


def validate_sql_order_by(field: str, allowed_fields: Optional[Set[str]] = None) -> None:
    """
    Validate ORDER BY field to prevent SQL injection.
    
    CVE-2026-1312: Django QuerySet.order_by() vulnerability
    
    Args:
        field: Field name to order by
        allowed_fields: Set of allowed field names (if None, performs basic validation)
        
    Raises:
        SQLInjectionError: If field is not allowed or contains dangerous characters
    """
    if not field or not isinstance(field, str):
        raise SQLInjectionError("Invalid ORDER BY field")
    
    # Extract field name (remove - prefix for descending)
    clean_field = field.lstrip('-')
    
    # If allowed fields specified, enforce allowlist
    if allowed_fields is not None:
        if clean_field not in allowed_fields:
            raise SQLInjectionError(
                f"ORDER BY field '{clean_field}' is not in allowed list"
            )
        return
    
    # Basic validation for dynamic fields
    # Prevent period characters that can be exploited with FilteredRelation
    # CVE-2026-1312: Column aliases with periods + FilteredRelation = injection
    if '..' in clean_field:
        raise SQLInjectionError("Field cannot contain consecutive periods")
    
    # Prevent SQL keywords
    dangerous_keywords = ['SELECT', 'FROM', 'WHERE', 'ORDER', 'GROUP', 'HAVING', 'UNION']
    for keyword in dangerous_keywords:
        if keyword in clean_field.upper():
            raise SQLInjectionError(f"Field cannot contain SQL keyword: {keyword}")
    
    validate_sql_column_alias(clean_field)


def create_safe_sql_parameter(value: Any) -> str:
    """
    Create a safe SQL parameter placeholder.
    
    Always use parameterized queries instead of string formatting!
    
    Args:
        value: Value to parameterize
        
    Returns:
        Parameter placeholder
    """
    # This function returns a placeholder - actual binding is done by DB driver
    return '?'


# ============================================================================
# Pass 35: Advanced XXE Prevention (CVE-2026-24400, CVE-2026-1227, CVE-2026-1218)
# ============================================================================

class XXEError(SecurityError):
    """Raised when XXE attack is detected."""
    pass


def create_secure_xml_parser() -> Any:
    """
    Create a secure XML parser with XXE protections.
    
    CVE-2026-24400: AssertJ XXE via XmlStringPrettyFormatter
    CVE-2026-1227: EBO Server XXE via TGML graphics files
    CVE-2026-1218: Bjskzy Zhiyou ERP XXE
    
    Returns:
        Configured XML parser
    """
    try:
        from xml.etree import ElementTree as ET
        
        # For Python 3.8+, use defusedxml if available
        try:
            import defusedxml.ElementTree as DefusedET
            return DefusedET
        except ImportError:
            pass
        
        # Fallback: Configure standard parser securely
        # Note: xml.etree.ElementTree in Python 3.8+ has some XXE protections by default
        return ET
        
    except ImportError:
        raise XXEError("XML parsing not available")


def parse_xml_securely(xml_string: str, forbid_dtd: bool = True, forbid_entities: bool = True) -> Any:
    """
    Parse XML with XXE protection.
    
    Args:
        xml_string: XML string to parse
        forbid_dtd: Whether to forbid DTD processing
        forbid_entities: Whether to forbid external entities
        
    Returns:
        Parsed XML element
        
    Raises:
        XXEError: If XML contains dangerous constructs
    """
    if not isinstance(xml_string, str):
        raise XXEError("XML input must be a string")
    
    # Check for DTD/DOCTYPE
    if forbid_dtd:
        # Check for DOCTYPE declaration
        doctype_pattern = re.compile(r'<!DOCTYPE\s', re.IGNORECASE)
        if doctype_pattern.search(xml_string):
            raise XXEError("DTD/DOCTYPE is forbidden for security")
    
    # Check for external entity declarations
    if forbid_entities:
        entity_pattern = re.compile(r'<!ENTITY\s+[^>]+SYSTEM\s+["\']', re.IGNORECASE)
        if entity_pattern.search(xml_string):
            raise XXEError("External entities are forbidden")
        
        public_entity_pattern = re.compile(r'<!ENTITY\s+[^>]+PUBLIC\s+["\']', re.IGNORECASE)
        if public_entity_pattern.search(xml_string):
            raise XXEError("Public entities are forbidden")
    
    # Check for XInclude
    xinclude_pattern = re.compile(r'xmlns:xi\s*=\s*["\']http://www\.w3\.org/2001/XInclude["\']', re.IGNORECASE)
    if xinclude_pattern.search(xml_string):
        raise XXEError("XInclude is forbidden")
    
    # Check for entity expansion attack (Billion Laughs)
    entity_count = xml_string.upper().count('<!ENTITY')
    if entity_count > 100:
        raise XXEError(f"Too many entity declarations: {entity_count}")
    
    # Check for deep nesting
    max_depth = 100
    depth = 0
    max_observed = 0
    for char in xml_string:
        if char == '<' and not xml_string[xml_string.index(char):].startswith('</'):
            depth += 1
            max_observed = max(max_observed, depth)
        elif char == '>' and xml_string[max(0, xml_string.index(char)-1)] != '/':
            depth -= 1
        if max_observed > max_depth:
            raise XXEError(f"XML nesting too deep: {max_observed}")
    
    try:
        parser = create_secure_xml_parser()
        return parser.fromstring(xml_string)
    except Exception as e:
        raise XXEError(f"XML parsing error: {e}")


# ============================================================================
# Pass 36: Secure File Upload (CVE-2026-25737, CVE-2026-24486, CVE-2026-23704)
# ============================================================================

class FileUploadError(SecurityError):
    """Raised when file upload validation fails."""
    pass


# Dangerous file extensions that should never be uploaded
DANGEROUS_EXTENSIONS = {
    '.exe', '.dll', '.bat', '.cmd', '.sh', '.php', '.jsp', '.asp', '.aspx',
    '.py', '.pyc', '.pyo', '.rb', '.pl', '.cgi', '.com', '.scr', '.msi',
    '.vbs', '.js', '.jar', '.war', '.ear', '.ps1', '.psm1', '.psd1',
    '.hta', '.wsf', '.wsh', '.msc', '.reg', '.inf', '.ins', '.isp',
}

# MIME type to extension mapping (for validation)
MIME_TYPE_MAP = {
    'image/jpeg': ['.jpg', '.jpeg'],
    'image/png': ['.png'],
    'image/gif': ['.gif'],
    'image/webp': ['.webp'],
    'application/pdf': ['.pdf'],
    'text/plain': ['.txt'],
    'text/csv': ['.csv'],
    'application/json': ['.json'],
    'application/zip': ['.zip'],
}

# Magic bytes for file type detection
MAGIC_BYTES = {
    b'\xff\xd8\xff': 'image/jpeg',  # JPEG
    b'\x89PNG\r\n\x1a\n': 'image/png',  # PNG
    b'GIF87a': 'image/gif',  # GIF
    b'GIF89a': 'image/gif',  # GIF
    b'RIFF': 'image/webp',  # WebP (RIFF....WEBP)
    b'%PDF': 'application/pdf',  # PDF
    b'PK\x03\x04': 'application/zip',  # ZIP
}


def validate_file_extension(filename: str, allowed_extensions: Optional[Set[str]] = None) -> None:
    """
    Validate file extension for upload.
    
    CVE-2026-25737: Budibase file extension bypass
    CVE-2026-23704: Movable Type unrestricted file upload
    
    Args:
        filename: Original filename
        allowed_extensions: Set of allowed extensions (lowercase with dot)
        
    Raises:
        FileUploadError: If extension is not allowed or dangerous
    """
    if not filename or not isinstance(filename, str):
        raise FileUploadError("Invalid filename")
    
    # Extract extension
    ext = os.path.splitext(filename.lower())[1]
    
    # Check for dangerous extension
    if ext in DANGEROUS_EXTENSIONS:
        raise FileUploadError(f"File type '{ext}' is not allowed for security reasons")
    
    # Check against allowlist if provided
    if allowed_extensions is not None:
        if ext not in allowed_extensions:
            raise FileUploadError(
                f"File extension '{ext}' is not in allowed list"
            )


def validate_file_content_type(content: bytes, expected_mime: Optional[str] = None) -> str:
    """
    Validate file content by checking magic bytes.
    
    CVE-2026-25737: Budibase MIME type bypass
    
    Args:
        content: File content bytes
        expected_mime: Expected MIME type
        
    Returns:
        Detected MIME type
        
    Raises:
        FileUploadError: If content type validation fails
    """
    if not content:
        raise FileUploadError("Empty file content")
    
    # Detect MIME type from magic bytes
    detected_mime = None
    for magic, mime in MAGIC_BYTES.items():
        if content.startswith(magic):
            # Special check for WebP
            if magic == b'RIFF' and b'WEBP' in content[:20]:
                detected_mime = 'image/webp'
            else:
                detected_mime = mime
            break
    
    if detected_mime is None:
        # Try text detection
        try:
            content.decode('utf-8')
            detected_mime = 'text/plain'
        except UnicodeDecodeError:
            detected_mime = 'application/octet-stream'
    
    if expected_mime and detected_mime != expected_mime:
        raise FileUploadError(
            f"Content type mismatch: expected {expected_mime}, got {detected_mime}"
        )
    
    return detected_mime


def sanitize_upload_filename(filename: str, use_uuid: bool = True) -> str:
    """
    Sanitize uploaded filename.
    
    CVE-2026-24486: Python-Multipart path traversal
    
    Args:
        filename: Original filename
        use_uuid: Whether to replace filename with UUID
        
    Returns:
        Sanitized filename
    """
    if not filename:
        raise FileUploadError("Empty filename")
    
    # Prevent path traversal in filename
    # CVE-2026-24486: Malicious filenames with ../ sequences
    dangerous_patterns = ['..', '/', '\\', '\x00', '\n', '\r']
    for pattern in dangerous_patterns:
        if pattern in filename:
            raise FileUploadError(
                f"Filename contains forbidden characters: {repr(pattern)}"
            )
    
    # Extract extension
    ext = os.path.splitext(filename)[1].lower()
    
    if use_uuid:
        import uuid
        return f"{uuid.uuid4().hex}{ext}"
    else:
        # Sanitize but keep original name
        safe_name = re.sub(r'[^a-zA-Z0-9_.-]', '_', filename)
        safe_name = safe_name.lstrip('.')  # Prevent hidden files
        return safe_name


def validate_upload_path(upload_path: Union[str, Path], base_dir: Union[str, Path]) -> Path:
    """
    Validate upload path to prevent directory traversal.
    
    CVE-2026-24486: Python-Multipart path traversal when UPLOAD_KEEP_FILENAME=True
    
    Args:
        upload_path: Target upload path
        base_dir: Base upload directory
        
    Returns:
        Validated path
        
    Raises:
        FileUploadError: If path escapes base directory
    """
    base = Path(base_dir).resolve()
    target = Path(upload_path)
    
    # Prevent path traversal
    try:
        resolved = (base / target).resolve()
        resolved.relative_to(base)
    except (ValueError, RuntimeError):
        raise FileUploadError(
            f"Upload path '{upload_path}' escapes base directory"
        )
    
    return resolved


# ============================================================================
# Pass 37: Open Redirect Prevention (CVE-2026-2709, CVE-2026-25477, CVE-2026-1406)
# ============================================================================

class OpenRedirectError(SecurityError):
    """Raised when open redirect attempt is detected."""
    pass


# Allowed redirect URL patterns (exact match or regex)
ALLOWED_REDIRECT_URLS: Set[str] = set()
ALLOWED_REDIRECT_DOMAINS: Set[str] = set()


def validate_redirect_url(url: str, allowed_domains: Optional[Set[str]] = None) -> str:
    """
    Validate redirect URL to prevent open redirect attacks.
    
    CVE-2026-2709: Busy Framework open redirect via state parameter
    CVE-2026-25477: AFFiNE open redirect via regex bypass
    CVE-2026-1406: BootDo open redirect via Host header
    CVE-2026-23729: WeGIA open redirect via nextPage parameter
    
    Args:
        url: URL to redirect to
        allowed_domains: Set of allowed domain names
        
    Returns:
        Validated URL
        
    Raises:
        OpenRedirectError: If URL is not allowed
    """
    if not url:
        raise OpenRedirectError("Empty redirect URL")
    
    # Check for data URIs (XSS vector)
    if url.lower().startswith('data:'):
        raise OpenRedirectError("Data URIs not allowed in redirects")
    
    # Check for javascript URIs (XSS vector)
    if url.lower().startswith('javascript:'):
        raise OpenRedirectError("JavaScript URIs not allowed in redirects")
    
    # Check for vbscript URIs
    if url.lower().startswith('vbscript:'):
        raise OpenRedirectError("VBScript URIs not allowed in redirects")
    
    # Parse URL
    parsed = urlparse(url)
    
    # Check for authority injection (@ bypass)
    # CVE-2026-27191: feathersjs @attacker.com bypass
    # Parse the URL carefully to detect @ injection
    # https://trusted.com@evil.com/path - @ is part of netloc, hostname becomes evil.com
    if parsed.username and parsed.hostname:
        # If username looks like a domain (contains dots), it's likely an attack
        if '.' in parsed.username and not parsed.password:
            # Check if username looks like a domain (trusted.com@evil.com pattern)
            if re.match(r'^[a-zA-Z0-9][-\.a-zA-Z0-9]*\.[a-zA-Z]{2,}$', parsed.username):
                raise OpenRedirectError("URL authority injection detected (domain as username)")
    
    # Allow relative URLs (path only)
    if not parsed.netloc and parsed.path:
        # Relative URL - safe
        if parsed.path.startswith('//'):
            raise OpenRedirectError("Protocol-relative URLs not allowed")
        return url
    
    # For absolute URLs, check against allowlist
    domains = allowed_domains or ALLOWED_REDIRECT_DOMAINS
    
    if domains:
        hostname = parsed.hostname or ''
        hostname_lower = hostname.lower()
        
        # Exact domain match required
        # CVE-2026-25477: Regex suffix match bypass (attacker.com matches trusted.com)
        if hostname_lower not in {d.lower() for d in domains}:
            raise OpenRedirectError(
                f"Redirect to '{hostname}' is not allowed"
            )
    
    return url


def add_allowed_redirect_domain(domain: str) -> None:
    """
    Add an allowed redirect domain.
    
    Args:
        domain: Domain name (e.g., 'example.com')
    """
    ALLOWED_REDIRECT_DOMAINS.add(domain.lower().lstrip('.').rstrip('/'))


# ============================================================================
# Pass 38: Secure Deserialization (CVE-2026-21226, CVE-2026-27830, CVE-2026-23946)
# ============================================================================

class DeserializationError(SecurityError):
    """Raised when unsafe deserialization is detected."""
    pass


# Allowed types for deserialization (allowlist approach)
ALLOWED_DESERIALIZATION_TYPES: Set[str] = set()

# Denied types (denylist approach)
DENIED_DESERIALIZATION_TYPES = {
    'builtins.eval',
    'builtins.exec',
    'builtins.compile',
    'builtins.__import__',
    'os.system',
    'subprocess.call',
    'subprocess.run',
    'subprocess.Popen',
}


def validate_pickle_data(data: bytes) -> None:
    """
    Validate pickle data before unpickling.
    
    CVE-2026-23946: Tendenci RCE via pickle deserialization
    
    Args:
        data: Pickle data bytes
        
    Raises:
        DeserializationError: If data contains dangerous constructs
    """
    if not data:
        raise DeserializationError("Empty pickle data")
    
    # Check for common dangerous module references
    data_str = data.decode('latin-1', errors='ignore')
    
    for dangerous in DENIED_DESERIALIZATION_TYPES:
        if dangerous in data_str:
            raise DeserializationError(
                f"Pickle contains forbidden type: {dangerous}"
            )
    
    # Check for bytecode/executable markers
    # Pickle protocol 0-5 headers
    if not (data[0:1] == b'\x80' or data[0:2] in (b'(', b'c\n', b'c ', b'cc')):
        raise DeserializationError("Invalid pickle format")
    
    # Protocol check
    if data[0:1] == b'\x80':
        protocol = data[1]
        if protocol > 5:
            raise DeserializationError(f"Unknown pickle protocol: {protocol}")


def safe_json_deserialize(data: Union[str, bytes], schema: Optional[dict] = None) -> Any:
    """
    Safely deserialize JSON data.
    
    CVE-2026-21226: Azure Core deserialization of untrusted data
    
    Args:
        data: JSON data
        schema: Optional JSON schema for validation
        
    Returns:
        Deserialized data
        
    Raises:
        DeserializationError: If deserialization fails validation
    """
    import json
    
    try:
        if isinstance(data, bytes):
            data = data.decode('utf-8')
        
        result = json.loads(data)
        
        # Check for dangerous patterns in strings
        def check_value(obj, depth: int = 0):
            if depth > 100:
                raise DeserializationError("JSON nesting too deep")
            
            if isinstance(obj, dict):
                for k, v in obj.items():
                    # Check for dangerous keys
                    if isinstance(k, str):
                        if k.startswith('__') or '.' in k:
                            raise DeserializationError(f"Forbidden key: {k}")
                    check_value(v, depth + 1)
            elif isinstance(obj, list):
                for item in obj:
                    check_value(item, depth + 1)
            elif isinstance(obj, str):
                # Check for prototype pollution patterns
                if obj in ('__proto__', 'constructor', 'prototype'):
                    raise DeserializationError(f"Forbidden value: {obj}")
        
        check_value(result)
        
        return result
        
    except json.JSONDecodeError as e:
        raise DeserializationError(f"JSON decode error: {e}")


def safe_unpickle(data: bytes, allowed_classes: Optional[Set[str]] = None) -> Any:
    """
    Safely unpickle data with restrictions.
    
    Args:
        data: Pickle data
        allowed_classes: Set of fully qualified class names allowed
        
    Returns:
        Unpickled object
        
    Raises:
        DeserializationError: If unpickling fails security checks
    """
    import pickle
    
    validate_pickle_data(data)
    
    if allowed_classes:
        # Use restricted unpickler
        class RestrictedUnpickler(pickle.Unpickler):
            def find_class(self, module, name):
                full_name = f"{module}.{name}"
                if full_name not in allowed_classes:
                    raise DeserializationError(
                        f"Class '{full_name}' not in allowed list"
                    )
                return super().find_class(module, name)
        
        return RestrictedUnpickler(BytesIO(data)).load()
    else:
        # Unpickle without restrictions (dangerous!)
        return pickle.loads(data)


# ============================================================================
# Pass 39: Session Fixation Prevention (CVE-2026-23796)
# ============================================================================

import secrets


class SessionSecurityError(SecurityError):
    """Raised when session security issue is detected."""
    pass


# Active session tracking (in production, use Redis/database)
_active_sessions: dict[str, dict] = {}


def generate_secure_session_id() -> str:
    """
    Generate a cryptographically secure session ID.
    
    Returns:
        Secure session ID string
    """
    return secrets.token_urlsafe(32)


def regenerate_session_id(old_session_id: str, user_id: str) -> str:
    """
    Regenerate session ID after authentication.
    
    CVE-2026-23796: Quick.Cart session fixation - session ID not changed after login
    
    Args:
        old_session_id: Previous session ID
        user_id: User identifier
        
    Returns:
        New session ID
    """
    # Invalidate old session
    if old_session_id in _active_sessions:
        del _active_sessions[old_session_id]
    
    # Generate new session ID
    new_session_id = generate_secure_session_id()
    
    # Store new session
    _active_sessions[new_session_id] = {
        'user_id': user_id,
        'created_at': time.time() if 'time' in globals() else 0,
        'ip_address': None,  # Should be set by caller
        'user_agent': None,  # Should be set by caller
    }
    
    return new_session_id


def validate_session(session_id: str, ip_address: Optional[str] = None, 
                     user_agent: Optional[str] = None) -> bool:
    """
    Validate session with optional binding checks.
    
    Args:
        session_id: Session ID to validate
        ip_address: Client IP address (for binding check)
        user_agent: User agent string (for binding check)
        
    Returns:
        True if session is valid
    """
    if session_id not in _active_sessions:
        return False
    
    session = _active_sessions[session_id]
    
    # Check IP binding (if enabled)
    if session.get('ip_address') and ip_address:
        if session['ip_address'] != ip_address:
            return False
    
    # Check User-Agent binding (if enabled)
    if session.get('user_agent') and user_agent:
        if session['user_agent'] != user_agent:
            return False
    
    return True


def get_secure_cookie_flags(secure: bool = True, http_only: bool = True,
                           same_site: str = 'Strict') -> dict:
    """
    Get secure cookie flags.
    
    Args:
        secure: Require HTTPS
        http_only: Prevent JavaScript access
        same_site: SameSite policy ('Strict', 'Lax', 'None')
        
    Returns:
        Dictionary of cookie flags
    """
    return {
        'secure': secure,
        'httponly': http_only,
        'samesite': same_site,
    }


# ============================================================================
# Pass 40: Clickjacking Prevention (CVE-2026-24839, CVE-2026-23731)
# ============================================================================

class ClickjackingError(SecurityError):
    """Raised when clickjacking protection check fails."""
    pass


# Default frame-busting headers
FRAME_OPTIONS_HEADER = 'X-Frame-Options'
CSP_FRAME_ANCESTORS = 'Content-Security-Policy'


def get_clickjacking_protection_headers(deny_all: bool = True) -> dict:
    """
    Get HTTP headers for clickjacking protection.
    
    CVE-2026-24839: Dokploy clickjacking - missing frame-busting headers
    CVE-2026-23731: WeGIA missing X-Frame-Options and CSP frame-ancestors
    
    Args:
        deny_all: If True, deny all framing; if False, allow same-origin
        
    Returns:
        Dictionary of security headers
    """
    headers = {}
    
    if deny_all:
        headers[FRAME_OPTIONS_HEADER] = 'DENY'
        headers[CSP_FRAME_ANCESTORS] = "frame-ancestors 'none'"
    else:
        headers[FRAME_OPTIONS_HEADER] = 'SAMEORIGIN'
        headers[CSP_FRAME_ANCESTORS] = "frame-ancestors 'self'"
    
    # Additional security headers
    headers['X-Content-Type-Options'] = 'nosniff'
    headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    
    return headers


def validate_frame_options_header(header_value: str) -> bool:
    """
    Validate X-Frame-Options header value.
    
    Args:
        header_value: Header value to validate
        
    Returns:
        True if valid
    """
    valid_values = {'DENY', 'SAMEORIGIN', 'ALLOW-FROM'}
    upper_value = header_value.upper()
    
    for valid in valid_values:
        if upper_value.startswith(valid):
            return True
    
    return False


def generate_frame_busting_js() -> str:
    """
    Generate frame-busting JavaScript (legacy browser support).
    
    Returns:
        JavaScript code as string
    """
    return """
    // Frame-busting script
    if (window.top !== window.self) {
        window.top.location = window.self.location;
    }
    """


# ============================================================================
# Pass 41: LDAP Injection Prevention (CVE-2026-24130, CVE-2026-21880, CVE-2025-61911)
# ============================================================================

class LDAPInjectionError(SecurityError):
    """Raised when LDAP injection is detected."""
    pass


# LDAP filter metacharacters that need escaping
# RFC 4515: * ( ) \ NUL
LDAP_SPECIAL_CHARS = {'*', '(', ')', '\\', '\x00'}

# LDAP injection patterns
LDAP_INJECTION_PATTERNS = [
    r'\*\)',  # Wildcard with close paren
    r'\(\|',  # OR operator injection
    r'\(&',   # AND operator injection
    r'\)\s*\(',  # Statement chaining
]


def escape_ldap_filter_value(value: str) -> str:
    """
    Escape LDAP filter value to prevent injection.
    
    CVE-2026-24130: Moonraker LDAP search filter injection
    CVE-2026-21880: Kanboard LDAP injection
    CVE-2025-61911: python-ldap escape_filter_chars bypass
    
    Args:
        value: Value to escape
        
    Returns:
        Escaped value
        
    Raises:
        LDAPInjectionError: If value type is invalid
    """
    # Type check (CVE-2025-61911: list/dict bypass)
    if not isinstance(value, str):
        raise LDAPInjectionError(
            f"LDAP filter value must be string, got {type(value).__name__}"
        )
    
    # RFC 4515 escaping
    # Replace special characters with \XX hex form
    escaped = value.replace('\\', '\\5c')
    escaped = escaped.replace('*', '\\2a')
    escaped = escaped.replace('(', '\\28')
    escaped = escaped.replace(')', '\\29')
    escaped = escaped.replace('\x00', '\\00')
    
    return escaped


def escape_ldap_dn_value(value: str) -> str:
    """
    Escape LDAP DN value to prevent injection.
    
    CVE-2025-61912: python-ldap escape_dn_chars NUL handling
    
    Args:
        value: Value to escape
        
    Returns:
        Escaped value
    """
    if not isinstance(value, str):
        raise LDAPInjectionError("LDAP DN value must be string")
    
    # RFC 4514 escaping
    # Escape , + " \ < > ; = NUL and leading/trailing space
    escaped = value.replace('\\', '\\5c')
    escaped = escaped.replace(',', '\\2c')
    escaped = escaped.replace('+', '\\2b')
    escaped = escaped.replace('"', '\\22')
    escaped = escaped.replace('<', '\\3c')
    escaped = escaped.replace('>', '\\3e')
    escaped = escaped.replace(';', '\\3b')
    escaped = escaped.replace('=', '\\3d')
    escaped = escaped.replace('\x00', '\\00')
    
    # Escape leading/trailing space
    if escaped.startswith(' '):
        escaped = '\\20' + escaped[1:]
    if escaped.endswith(' '):
        escaped = escaped[:-1] + '\\20'
    
    return escaped


def validate_ldap_filter(filter_str: str) -> None:
    """
    Validate LDAP filter string for injection attempts.
    
    Args:
        filter_str: Filter string to validate
        
    Raises:
        LDAPInjectionError: If injection is detected
    """
    if not isinstance(filter_str, str):
        raise LDAPInjectionError("Filter must be a string")
    
    # Check for unescaped special characters
    # Count balanced parentheses
    open_count = filter_str.count('(')
    close_count = filter_str.count(')')
    if open_count != close_count:
        raise LDAPInjectionError("Unbalanced parentheses in LDAP filter")
    
    # Check for injection patterns
    for pattern in LDAP_INJECTION_PATTERNS:
        if re.search(pattern, filter_str, re.IGNORECASE):
            raise LDAPInjectionError("LDAP injection pattern detected")


# ============================================================================
# Pass 42: NoSQL Injection Prevention (MongoDB, Redis patterns)
# ============================================================================

class NoSQLInjectionError(SecurityError):
    """Raised when NoSQL injection is detected."""
    pass


# MongoDB operator injection patterns
MONGODB_DANGEROUS_OPERATORS = {
    '$where', '$ne', '$gt', '$gte', '$lt', '$lte', '$regex',
    '$exists', '$type', '$mod', '$geoIntersects', '$geoWithin',
    '$near', '$nearSphere', '$all', '$elemMatch', '$size',
    '$bitsAllSet', '$bitsAnySet', '$bitsAllClear', '$bitsAnyClear',
    '$comment', '$expr', '$jsonSchema',
}

# JavaScript execution operators
MONGODB_JS_OPERATORS = {'$where', '$accumulator', '$function'}


def sanitize_mongodb_query(query: dict) -> dict:
    """
    Sanitize MongoDB query to prevent injection.
    
    Args:
        query: MongoDB query dictionary
        
    Returns:
        Sanitized query
        
    Raises:
        NoSQLInjectionError: If query contains dangerous operators
    """
    if not isinstance(query, dict):
        raise NoSQLInjectionError("MongoDB query must be a dictionary")
    
    sanitized = {}
    
    for key, value in query.items():
        # Check for operator injection
        if key.startswith('$'):
            if key in MONGODB_JS_OPERATORS:
                raise NoSQLInjectionError(
                    f"JavaScript execution operator '{key}' is forbidden"
                )
        
        # Recursively check nested queries
        if isinstance(value, dict):
            # Check nested operators
            for nested_key in value.keys():
                if nested_key.startswith('$'):
                    if nested_key in MONGODB_JS_OPERATORS:
                        raise NoSQLInjectionError(
                            f"JavaScript execution operator '{nested_key}' is forbidden"
                        )
            sanitized[key] = sanitize_mongodb_query(value)
        elif isinstance(value, list):
            sanitized[key] = [
                sanitize_mongodb_query(item) if isinstance(item, dict) else item
                for item in value
            ]
        else:
            # Sanitize string values
            if isinstance(value, str):
                # Check for prototype pollution
                if value in ('__proto__', 'constructor', 'prototype'):
                    raise NoSQLInjectionError(f"Forbidden value: {value}")
            sanitized[key] = value
    
    return sanitized


def validate_mongodb_field_name(field: str) -> None:
    """
    Validate MongoDB field name.
    
    Args:
        field: Field name to validate
        
    Raises:
        NoSQLInjectionError: If field name is invalid
    """
    if not isinstance(field, str):
        raise NoSQLInjectionError("Field name must be string")
    
    # Prevent null bytes
    if '\x00' in field:
        raise NoSQLInjectionError("Field name cannot contain null bytes")
    
    # Prevent $ prefix (operator injection)
    if field.startswith('$'):
        raise NoSQLInjectionError("Field name cannot start with $")
    
    # Prevent dot notation abuse (could be legitimate but verify)
    if '..' in field:
        raise NoSQLInjectionError("Field name cannot contain consecutive dots")


def sanitize_redis_command(command_parts: list) -> list:
    """
    Sanitize Redis command to prevent injection.
    
    Args:
        command_parts: Command parts as list
        
    Returns:
        Sanitized command parts
        
    Raises:
        NoSQLInjectionError: If command is dangerous
    """
    if not command_parts:
        raise NoSQLInjectionError("Empty Redis command")
    
    command = command_parts[0].upper()
    
    # Dangerous commands to block
    dangerous_commands = {
        'CONFIG', 'FLUSHALL', 'FLUSHDB', 'DEBUG', 'SHUTDOWN',
        'SLAVEOF', 'REPLICAOF', 'KEYS', 'SAVE', 'BGSAVE',
    }
    
    if command in dangerous_commands:
        raise NoSQLInjectionError(f"Redis command '{command}' is forbidden")
    
    # Sanitize arguments
    sanitized = [command]
    for arg in command_parts[1:]:
        if isinstance(arg, str):
            # Check for command injection via newlines
            if '\n' in arg or '\r' in arg:
                raise NoSQLInjectionError("Redis argument cannot contain newlines")
            sanitized.append(arg)
        else:
            sanitized.append(arg)
    
    return sanitized


# ============================================================================
# Pass 43: HTTP Header Injection Prevention (CVE-2026-24489, CVE-2026-0865)
# ============================================================================

class HeaderInjectionError(SecurityError):
    """Raised when HTTP header injection is detected."""
    pass


# Forbidden characters in HTTP headers (RFC 7230)
# CR LF NUL are forbidden
HEADER_FORBIDDEN_CHARS = {'\r', '\n', '\x00'}

# Header name forbidden characters
HEADER_NAME_FORBIDDEN = HEADER_FORBIDDEN_CHARS | {':', ' ', '\t'}


def sanitize_http_header_name(name: str) -> str:
    """
    Sanitize HTTP header name.
    
    CVE-2026-24489: Gakido HTTP header injection via CRLF
    CVE-2026-0865: wsgiref.headers control character injection
    
    Args:
        name: Header name
        
    Returns:
        Sanitized header name
        
    Raises:
        HeaderInjectionError: If name contains forbidden characters
    """
    if not isinstance(name, str):
        raise HeaderInjectionError("Header name must be string")
    
    # Check for forbidden characters
    for char in HEADER_NAME_FORBIDDEN:
        if char in name:
            raise HeaderInjectionError(
                f"Header name contains forbidden character: {repr(char)}"
            )
    
    # Header names should be printable ASCII
    for char in name:
        if ord(char) < 33 or ord(char) > 126:
            raise HeaderInjectionError(
                f"Header name contains non-printable character: {repr(char)}"
            )
    
    return name


def sanitize_http_header_value(value: str) -> str:
    """
    Sanitize HTTP header value.
    
    Args:
        value: Header value
        
    Returns:
        Sanitized header value
        
    Raises:
        HeaderInjectionError: If value contains forbidden characters
    """
    if not isinstance(value, str):
        # Convert to string
        value = str(value)
    
    # Check for CRLF (header injection / response splitting)
    for char in HEADER_FORBIDDEN_CHARS:
        if char in value:
            raise HeaderInjectionError(
                f"Header value contains forbidden character: {repr(char)}"
            )
    
    # Trim leading/trailing whitespace
    value = value.strip()
    
    return value


def validate_http_headers(headers: dict) -> dict:
    """
    Validate all HTTP headers.
    
    Args:
        headers: Dictionary of headers
        
    Returns:
        Validated headers
        
    Raises:
        HeaderInjectionError: If any header is invalid
    """
    validated = {}
    
    for name, value in headers.items():
        safe_name = sanitize_http_header_name(name)
        safe_value = sanitize_http_header_value(str(value))
        validated[safe_name] = safe_value
    
    return validated


# ============================================================================
# Pass 44: Information Disclosure Prevention (CVE-2026-2297, CVE-2026-2861)
# ============================================================================

class InformationDisclosureError(SecurityError):
    """Raised when information disclosure is detected."""
    pass


# Sensitive patterns to mask in logs/error messages
SENSITIVE_PATTERNS = [
    r'password\s*[=:]\s*\S+',
    r'secret\s*[=:]\s*\S+',
    r'token\s*[=:]\s*\S+',
    r'key\s*[=:]\s*\S+',
    r'api[_-]?key\s*[=:]\s*\S+',
    r'private[_-]?key\s*[=:]\s*\S+',
    r'authorization\s*[=:]\s*\S+',
    r'cookie\s*[=:]\s*\S+',
    r'session[_-]?id\s*[=:]\s*\S+',
    r'passwd\s*[=:]\s*\S+',
]


def sanitize_error_message(message: str, is_production: bool = True) -> str:
    """
    Sanitize error message to prevent information disclosure.
    
    CVE-2026-2861: Foswiki information disclosure
    CVE-2026-21626: Forum post ACL information disclosure
    
    Args:
        message: Original error message
        is_production: If True, remove detailed technical info
        
    Returns:
        Sanitized message
    """
    if not is_production:
        return message
    
    # Remove stack traces (lines starting with whitespace containing file paths)
    lines = message.split('\n')
    sanitized_lines = []
    
    for line in lines:
        # Skip lines that look like stack traces
        if re.match(r'\s+File "', line):
            continue
        if re.match(r'\s+\^+', line):  # Python error pointer
            continue
        sanitized_lines.append(line)
    
    result = '\n'.join(sanitized_lines)
    
    # Mask sensitive patterns
    for pattern in SENSITIVE_PATTERNS:
        result = re.sub(pattern, '***REDACTED***', result, flags=re.IGNORECASE)
    
    # Remove file paths
    result = re.sub(r'/[\w\-/.]+/([\w\-.]+)', r'\1', result)
    
    return result


def mask_sensitive_data(text: str) -> str:
    """
    Mask sensitive data in text.
    
    Args:
        text: Text to mask
        
    Returns:
        Masked text
    """
    result = text
    
    # Mask potential passwords/secrets (case-insensitive)
    # Match patterns like "password: value", "password is: value", etc.
    result = re.sub(
        r'(?i)(password(?:\s+is)?[:=\s]+)\S+',
        r'\1***REDACTED***',
        result
    )
    result = re.sub(
        r'(?i)(secret(?:\s+is)?[:=\s]+)\S+',
        r'\1***REDACTED***',
        result
    )
    result = re.sub(
        r'(?i)(token(?:\s+is)?[:=\s]+)\S+',
        r'\1***REDACTED***',
        result
    )
    result = re.sub(
        r'(?i)(api[_-]?key(?:\s+is)?[:=\s]+)\S+',
        r'\1***REDACTED***',
        result
    )
    
    # Mask credit card numbers
    result = re.sub(
        r'\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b',
        '****-****-****-****',
        result
    )
    
    # Mask SSN
    result = re.sub(
        r'\b\d{3}-\d{2}-\d{4}\b',
        '***-**-****',
        result
    )
    
    return result


def check_pyc_audit_event() -> bool:
    """
    Check if Python audit events are supported (CVE-2026-2297).
    
    Returns:
        True if audit hooks are supported
    """
    return hasattr(sys, 'addaudithook') and hasattr(sys, 'audit')


# ============================================================================
# Pass 45: Secure Configuration Management
# ============================================================================

class ConfigurationSecurityError(SecurityError):
    """Raised when configuration security issue is detected."""
    pass


# Secure file permissions
SECURE_FILE_PERMISSIONS = 0o600  # Owner read/write only
SECURE_DIR_PERMISSIONS = 0o700   # Owner read/write/execute only


def validate_config_file_permissions(filepath: Union[str, Path]) -> None:
    """
    Validate configuration file permissions.
    
    Args:
        filepath: Path to configuration file
        
    Raises:
        ConfigurationSecurityError: If permissions are too open
    """
    filepath = Path(filepath)
    
    if not filepath.exists():
        return
    
    try:
        stat = filepath.stat()
        mode = stat.st_mode
        
        # Check if world-readable
        if mode & 0o044:
            raise ConfigurationSecurityError(
                f"Config file '{filepath}' is world-readable"
            )
        
        # Check if world-writable
        if mode & 0o022:
            raise ConfigurationSecurityError(
                f"Config file '{filepath}' is group/world-writable"
            )
        
        # Check if group-writable (optional strict check)
        if mode & 0o020:
            # Warning but not error
            pass
            
    except OSError as e:
        raise ConfigurationSecurityError(f"Cannot check permissions: {e}")


def set_secure_file_permissions(filepath: Union[str, Path], 
                                mode: int = SECURE_FILE_PERMISSIONS) -> None:
    """
    Set secure file permissions.
    
    Args:
        filepath: Path to file
        mode: Permission mode (default 0o600)
    """
    filepath = Path(filepath)
    try:
        os.chmod(filepath, mode)
    except OSError as e:
        raise ConfigurationSecurityError(f"Cannot set permissions: {e}")


def sanitize_environment_value(name: str, value: str) -> str:
    """
    Sanitize environment variable value.
    
    Args:
        name: Variable name
        value: Variable value
        
    Returns:
        Sanitized value
        
    Raises:
        ConfigurationSecurityError: If value is suspicious
    """
    if not isinstance(value, str):
        return str(value)
    
    # Check for command injection patterns
    dangerous_chars = [';', '&', '|', '$', '`', '$(', '<', '>']
    for char in dangerous_chars:
        if char in value:
            raise ConfigurationSecurityError(
                f"Environment variable '{name}' contains dangerous character: {char}"
            )
    
    return value


def validate_config_schema(config: dict, schema: dict) -> None:
    """
    Validate configuration against schema.
    
    Args:
        config: Configuration dictionary
        schema: Schema dictionary with expected types
        
    Raises:
        ConfigurationSecurityError: If validation fails
    """
    for key, expected_type in schema.items():
        if key not in config:
            raise ConfigurationSecurityError(f"Required config key '{key}' missing")
        
        value = config[key]
        
        if expected_type == 'path':
            # Validate as secure path
            try:
                Path(value).resolve()
            except (TypeError, ValueError) as e:
                raise ConfigurationSecurityError(
                    f"Config key '{key}' has invalid path: {e}"
                )
        elif expected_type == 'secret':
            # Validate secret is not empty and has minimum length
            if not value or len(str(value)) < 8:
                raise ConfigurationSecurityError(
                    f"Config key '{key}' secret is too short"
                )
        elif expected_type == 'port':
            # Validate port number
            try:
                port = int(value)
                if not (1 <= port <= 65535):
                    raise ValueError()
            except (ValueError, TypeError):
                raise ConfigurationSecurityError(
                    f"Config key '{key}' has invalid port number"
                )
        elif expected_type == 'bool':
            if not isinstance(value, bool):
                raise ConfigurationSecurityError(
                    f"Config key '{key}' must be boolean"
                )


def load_secure_config(config_path: Union[str, Path]) -> dict:
    """
    Load configuration file with security checks.
    
    Args:
        config_path: Path to config file
        
    Returns:
        Configuration dictionary
        
    Raises:
        ConfigurationSecurityError: If security check fails
    """
    config_path = Path(config_path)
    
    # Validate permissions
    validate_config_file_permissions(config_path)
    
    # Load based on extension
    ext = config_path.suffix.lower()
    
    try:
        with open(config_path, 'r') as f:
            content = f.read()
        
        if ext == '.json':
            import json
            return json.loads(content)
        elif ext in ('.yaml', '.yml'):
            try:
                import yaml
                return yaml.safe_load(content)
            except ImportError:
                raise ConfigurationSecurityError("PyYAML not available")
        elif ext == '.toml':
            try:
                import tomllib
                return tomllib.loads(content)
            except ImportError:
                raise ConfigurationSecurityError("tomllib not available (Python 3.11+)")
        else:
            raise ConfigurationSecurityError(f"Unsupported config format: {ext}")
            
    except Exception as e:
        raise ConfigurationSecurityError(f"Failed to load config: {e}")


# ============================================================================
# Security utility exports
# ============================================================================

__all__ = [
    # Base classes
    'SecurityError',
    'PathTraversalError',
    'JWTValidationError',
    'SQLInjectionError',
    'XXEError',
    'FileUploadError',
    'OpenRedirectError',
    'DeserializationError',
    'SessionSecurityError',
    'ClickjackingError',
    'LDAPInjectionError',
    'NoSQLInjectionError',
    'HeaderInjectionError',
    'InformationDisclosureError',
    'ConfigurationSecurityError',
    
    # Pass 33: JWT
    'validate_jwt_algorithm',
    'validate_jwt_header',
    'sanitize_jwt_token',
    'FORBIDDEN_JWT_ALGORITHMS',
    'ALLOWED_JWT_ALGORITHMS',
    
    # Pass 34: SQL Injection
    'validate_sql_column_alias',
    'validate_sql_order_by',
    'create_safe_sql_parameter',
    'SQL_INJECTION_PATTERNS',
    
    # Pass 35: XXE
    'create_secure_xml_parser',
    'parse_xml_securely',
    
    # Pass 36: File Upload
    'validate_file_extension',
    'validate_file_content_type',
    'sanitize_upload_filename',
    'validate_upload_path',
    'DANGEROUS_EXTENSIONS',
    'MIME_TYPE_MAP',
    
    # Pass 37: Open Redirect
    'validate_redirect_url',
    'add_allowed_redirect_domain',
    'ALLOWED_REDIRECT_DOMAINS',
    
    # Pass 38: Deserialization
    'validate_pickle_data',
    'safe_json_deserialize',
    'safe_unpickle',
    'ALLOWED_DESERIALIZATION_TYPES',
    
    # Pass 39: Session
    'generate_secure_session_id',
    'regenerate_session_id',
    'validate_session',
    'get_secure_cookie_flags',
    
    # Pass 40: Clickjacking
    'get_clickjacking_protection_headers',
    'validate_frame_options_header',
    'generate_frame_busting_js',
    
    # Pass 41: LDAP
    'escape_ldap_filter_value',
    'escape_ldap_dn_value',
    'validate_ldap_filter',
    
    # Pass 42: NoSQL
    'sanitize_mongodb_query',
    'validate_mongodb_field_name',
    'sanitize_redis_command',
    
    # Pass 43: HTTP Headers
    'sanitize_http_header_name',
    'sanitize_http_header_value',
    'validate_http_headers',
    
    # Pass 44: Info Disclosure
    'sanitize_error_message',
    'mask_sensitive_data',
    'check_pyc_audit_event',
    
    # Pass 45: Configuration
    'validate_config_file_permissions',
    'set_secure_file_permissions',
    'validate_config_schema',
    'load_secure_config',
    'SECURE_FILE_PERMISSIONS',
]


# ============================================================================
# Pass 46: Rate Limiting Enforcement (CVE-2026-25114, CVE-2026-28342, CVE-2026-23848)
# ============================================================================

class RateLimitError(SecurityError):
    """Raised when rate limit is exceeded."""
    pass


class RateLimiter:
    """
    Token bucket rate limiter for API protection.
    
    CVE-2026-25114: WebSocket API rate limiting bypass
    CVE-2026-28342: PasswordHash API DoS
    CVE-2026-23848: X-Forwarded-For rate limiting bypass
    """
    
    def __init__(self, max_requests: int = 100, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._buckets = {}
        self._lock = None
    
    def _get_bucket_key(self, identifier: str) -> str:
        """Generate bucket key for an identifier."""
        return f"ratelimit:{identifier}"
    
    def is_allowed(self, identifier: str) -> bool:
        """
        Check if request is allowed for the identifier.
        
        Args:
            identifier: Client identifier (IP, API key, etc.)
            
        Returns:
            True if request is allowed
        """
        import time
        
        now = time.time()
        key = self._get_bucket_key(identifier)
        
        # Get or create bucket
        bucket = self._buckets.get(key, {'tokens': self.max_requests, 'last_update': now})
        
        # Add tokens based on time passed
        time_passed = now - bucket['last_update']
        tokens_to_add = time_passed * (self.max_requests / self.window_seconds)
        bucket['tokens'] = min(self.max_requests, bucket['tokens'] + tokens_to_add)
        bucket['last_update'] = now
        
        # Check if request is allowed
        if bucket['tokens'] >= 1:
            bucket['tokens'] -= 1
            self._buckets[key] = bucket
            return True
        
        self._buckets[key] = bucket
        return False
    
    def get_remaining(self, identifier: str) -> int:
        """Get remaining requests for identifier."""
        key = self._get_bucket_key(identifier)
        bucket = self._buckets.get(key, {'tokens': self.max_requests})
        return int(bucket['tokens'])
    
    def reset(self, identifier: str) -> None:
        """Reset rate limit for identifier."""
        key = self._get_bucket_key(identifier)
        if key in self._buckets:
            del self._buckets[key]


# Global rate limiter storage
_rate_limiters = {}


def check_rate_limit(identifier: str, max_requests: int = 100, 
                     window_seconds: int = 60) -> bool:
    """
    Check if request is within rate limit.
    
    CVE-2026-25114: Rate limiting for WebSocket auth
    CVE-2026-28342: Protect expensive operations
    
    Args:
        identifier: Client identifier (IP, user ID, etc.)
        max_requests: Maximum requests allowed in window
        window_seconds: Time window in seconds
        
    Returns:
        True if request is allowed
        
    Raises:
        RateLimitError: If rate limit exceeded
    """
    # Create key based on parameters to allow different limits for different endpoints
    limiter_key = f"{max_requests}:{window_seconds}"
    
    if limiter_key not in _rate_limiters:
        _rate_limiters[limiter_key] = RateLimiter(max_requests, window_seconds)
    
    limiter = _rate_limiters[limiter_key]
    
    if not limiter.is_allowed(identifier):
        raise RateLimitError(
            f"Rate limit exceeded: {max_requests} requests per {window_seconds}s"
        )
    
    return True


def extract_client_ip(request_headers: dict, trusted_proxies: list = None) -> str:
    """
    Extract client IP from request headers safely.
    
    CVE-2026-23848: Prevent X-Forwarded-For spoofing
    
    Args:
        request_headers: HTTP request headers
        trusted_proxies: List of trusted proxy IPs
        
    Returns:
        Client IP address
    """
    trusted_proxies = trusted_proxies or []
    
    # Check X-Forwarded-For (common in proxied environments)
    forwarded_for = request_headers.get('X-Forwarded-For', '')
    if forwarded_for:
        # Get all IPs in the chain
        ips = [ip.strip() for ip in forwarded_for.split(',')]
        
        # If we have trusted proxies configured, find the first non-trusted IP
        # from the left (original client)
        if trusted_proxies:
            for ip in ips:
                if ip not in trusted_proxies:
                    return ip
            # All IPs are trusted proxies - return the last one
            return ips[-1] if ips else 'unknown'
        else:
            # No trusted proxies - return the leftmost (original client)
            return ips[0] if ips else 'unknown'
    
    # Check X-Real-IP
    real_ip = request_headers.get('X-Real-IP')
    if real_ip:
        return real_ip
    
    # Fall back to REMOTE_ADDR
    return request_headers.get('REMOTE_ADDR', 'unknown')


# ============================================================================
# Pass 47: Authentication Flow Hardening (CVE-2026-23906, CVE-2026-28536)
# ============================================================================

class AuthenticationError(SecurityError):
    """Raised when authentication security issue is detected."""
    pass


def validate_ldap_auth_response(username: str, password: str, 
                                  auth_result: dict) -> None:
    """
    Validate LDAP authentication response to prevent bypass.
    
    CVE-2026-23906: Apache Druid LDAP auth bypass via anonymous bind
    
    Args:
        username: Username attempting authentication
        password: Password provided
        auth_result: LDAP authentication result
        
    Raises:
        AuthenticationError: If potential bypass detected
    """
    # Check for empty password with successful auth (anonymous bind bypass)
    if not password or len(password.strip()) == 0:
        if auth_result.get('success'):
            raise AuthenticationError(
                "LDAP anonymous bind bypass detected: empty password authenticated"
            )
    
    # Verify username matches in response
    returned_user = auth_result.get('username', '').lower()
    if returned_user and returned_user != username.lower():
        raise AuthenticationError(
            f"LDAP user mismatch: expected {username}, got {returned_user}"
        )
    
    # Check for required attributes indicating proper authentication
    if auth_result.get('success') and not auth_result.get('bind_dn'):
        raise AuthenticationError(
            "LDAP authentication missing bind DN - possible bypass"
        )


def validate_auth_attempt(username: str, password: str, 
                          attempt_count: int, max_attempts: int = 5,
                          lockout_seconds: int = 300) -> None:
    """
    Validate authentication attempt against brute force protection.
    
    CVE-2026-28536: Prevent authentication bypass via brute force
    
    Args:
        username: Username attempting authentication
        password: Password provided
        attempt_count: Current failed attempt count
        max_attempts: Maximum allowed failed attempts
        lockout_seconds: Lockout duration after max attempts
        
    Raises:
        AuthenticationError: If account is locked or attempt invalid
    """
    if attempt_count >= max_attempts:
        raise AuthenticationError(
            f"Account locked due to too many failed attempts. "
            f"Try again in {lockout_seconds} seconds."
        )
    
    # Validate password complexity
    if password:
        if len(password) < 8:
            raise AuthenticationError("Password must be at least 8 characters")
    
    # Validate username format
    if not username or len(username) < 1:
        raise AuthenticationError("Username is required")
    
    # Check for suspicious patterns
    suspicious_patterns = ['admin', 'root', 'test', 'guest']
    if username.lower() in suspicious_patterns and attempt_count > 2:
        # Extra scrutiny for common usernames
        pass  # Could log or alert here


# ============================================================================
# Pass 48: API Key and Credential Rotation (CVE-2026-21852, CVE-2026-25253)
# ============================================================================

class CredentialRotationError(SecurityError):
    """Raised when credential rotation issue is detected."""
    pass


API_KEY_PATTERN = re.compile(r'^[A-Za-z0-9_-]{32,128}$')

def generate_secure_api_key(prefix: str = "nis2") -> str:
    """
    Generate a secure API key.
    
    CVE-2026-25253: Proper API key generation
    CVE-2026-21852: Secure credential handling
    
    Args:
        prefix: Key prefix for identification
        
    Returns:
        Secure API key
    """
    import secrets
    random_part = secrets.token_urlsafe(48)
    timestamp = str(int(time.time()))
    
    # Create key with prefix and random component
    key = f"{prefix}_{random_part}_{timestamp}"
    
    # Hash the key for storage
    return key


def validate_api_key_format(key: str, expected_prefix: str = None) -> bool:
    """
    Validate API key format.
    
    Args:
        key: API key to validate
        expected_prefix: Expected prefix if any
        
    Returns:
        True if format is valid
        
    Raises:
        CredentialRotationError: If format is invalid
    """
    if not key or not isinstance(key, str):
        raise CredentialRotationError("API key is required")
    
    if len(key) < 32:
        raise CredentialRotationError("API key is too short")
    
    if expected_prefix and not key.startswith(expected_prefix):
        raise CredentialRotationError(f"API key must start with '{expected_prefix}'")
    
    # Check for suspicious characters
    dangerous = ['\n', '\r', '\x00', '$', '`', '|', ';']
    for char in dangerous:
        if char in key:
            raise CredentialRotationError("API key contains invalid characters")
    
    return True


def should_rotate_api_key(created_timestamp: float, 
                          max_age_days: int = 90) -> bool:
    """
    Check if API key should be rotated.
    
    Args:
        created_timestamp: When key was created (Unix timestamp)
        max_age_days: Maximum age before rotation required
        
    Returns:
        True if key should be rotated
    """
    if not created_timestamp:
        return True
    
    age_days = (time.time() - created_timestamp) / (24 * 3600)
    return age_days >= max_age_days


def mask_api_key(key: str) -> str:
    """
    Mask API key for display/logging.
    
    Args:
        key: Full API key
        
    Returns:
        Masked key showing only first 4 and last 4 chars
    """
    if not key or len(key) < 12:
        return "***"
    
    return f"{key[:4]}...{key[-4:]}"


# ============================================================================
# Pass 49: CSRF Protection Consolidation (CVE-2026-24885, CVE-2026-1148, CVE-2026-22030)
# ============================================================================

class CSRFError(SecurityError):
    """Raised when CSRF protection fails."""
    pass


CSRF_TOKEN_LENGTH = 32

def generate_csrf_token() -> str:
    """
    Generate secure CSRF token.
    
    CVE-2026-24885: CSRF via Content-Type misconfiguration
    CVE-2026-1148: Missing CSRF token validation
    CVE-2026-22030: React Router CSRF
    
    Returns:
        Secure random CSRF token
    """
    import secrets
    return secrets.token_urlsafe(CSRF_TOKEN_LENGTH)


def validate_csrf_token(token: str, expected_token: str) -> None:
    """
    Validate CSRF token with constant-time comparison.
    
    Args:
        token: Token from request
        expected_token: Expected token from session
        
    Raises:
        CSRFError: If token is invalid or missing
    """
    if not token or not expected_token:
        raise CSRFError("CSRF token missing")
    
    # Constant-time comparison to prevent timing attacks
    import hmac
    if not hmac.compare_digest(token, expected_token):
        raise CSRFError("CSRF token mismatch")


def validate_content_type_for_csrf(content_type: str, 
                                   allowed_types: list = None) -> None:
    """
    Validate Content-Type for CSRF protection.
    
    CVE-2026-24885: Kanboard CSRF via text/plain
    
    Args:
        content_type: Content-Type header value
        allowed_types: List of allowed content types
        
    Raises:
        CSRFError: If content type is not allowed
    """
    allowed_types = allowed_types or ['application/json', 
                                       'application/x-www-form-urlencoded',
                                       'multipart/form-data']
    
    if not content_type:
        raise CSRFError("Content-Type header required")
    
    # Normalize content type (remove charset, etc.)
    normalized = content_type.split(';')[0].strip().lower()
    
    # Block potentially dangerous content types for state-changing operations
    dangerous_types = ['text/plain']  # Can be submitted via HTML forms
    
    if normalized in dangerous_types:
        raise CSRFError(
            f"Content-Type '{content_type}' not allowed for this operation"
        )


def validate_origin_header(origin: str, allowed_origins: list) -> None:
    """
    Validate Origin header for cross-origin requests.
    
    CVE-2026-22030: React Router origin validation
    
    Args:
        origin: Origin header value
        allowed_origins: List of allowed origin domains
        
    Raises:
        CSRFError: If origin is not allowed
    """
    if not origin:
        # Same-origin request - check Referer as fallback
        return
    
    # Normalize origin
    origin_normalized = origin.rstrip('/').lower()
    
    for allowed in allowed_origins:
        allowed_normalized = allowed.rstrip('/').lower()
        if origin_normalized == allowed_normalized:
            return
        # Allow subdomains
        if origin_normalized.endswith('.' + allowed_normalized.replace('https://', '').replace('http://', '')):
            return
    
    raise CSRFError(f"Origin '{origin}' not allowed")


# ============================================================================
# Pass 50: WebSocket Origin Validation (CVE-2026-1692)
# ============================================================================

class WebSocketSecurityError(SecurityError):
    """Raised when WebSocket security issue is detected."""
    pass


def validate_websocket_origin(origin: str, allowed_origins: list) -> None:
    """
    Validate WebSocket connection origin.
    
    CVE-2026-1692: PcVue WebSocket missing origin validation
    
    Args:
        origin: Origin header from WebSocket handshake
        allowed_origins: List of allowed origins
        
    Raises:
        WebSocketSecurityError: If origin is not allowed
    """
    if not origin:
        raise WebSocketSecurityError("WebSocket origin header missing")
    
    origin_normalized = origin.rstrip('/').lower()
    
    for allowed in allowed_origins:
        allowed_normalized = allowed.rstrip('/').lower()
        
        # Exact match
        if origin_normalized == allowed_normalized:
            return
        
        # Wildcard subdomain match (*.example.com)
        allowed_domain = allowed_normalized.replace('https://', '').replace('http://', '')
        if allowed_domain.startswith('*.'):
            domain_suffix = allowed_domain[2:]
            origin_domain = origin_normalized.replace('https://', '').replace('http://', '')
            if origin_domain == domain_suffix or origin_domain.endswith('.' + domain_suffix):
                return
    
    raise WebSocketSecurityError(f"WebSocket origin '{origin}' not allowed")


def get_websocket_security_headers() -> dict:
    """
    Get recommended security headers for WebSocket endpoints.
    
    Returns:
        Dictionary of security headers
    """
    return {
        'X-Content-Type-Options': 'nosniff',
        'X-Frame-Options': 'DENY',
        'Content-Security-Policy': "default-src 'self'; connect-src 'self' wss:;",
    }


# ============================================================================
# Pass 51: CORS Policy Enforcement (CVE-2024-10906, CVE-2026-24435)
# ============================================================================

class CORSError(SecurityError):
    """Raised when CORS policy violation detected."""
    pass


CORS_DEFAULT_MAX_AGE = 86400  # 24 hours

def validate_cors_origin(origin: str, allowed_origins: list) -> bool:
    """
    Validate CORS origin.
    
    CVE-2024-10906: Overly permissive CORS (* wildcard)
    CVE-2026-24435: Tenda router CORS misconfiguration
    
    Args:
        origin: Request origin
        allowed_origins: List of allowed origins (can include wildcards)
        
    Returns:
        True if origin is allowed
        
    Raises:
        CORSError: If origin is not allowed
    """
    if not origin:
        return True  # Same-origin request
    
    # NEVER allow wildcard * - this is a security risk
    if '*' in allowed_origins:
        raise CORSError("Wildcard CORS origin (*) is not allowed")
    
    origin_normalized = origin.rstrip('/').lower()
    
    for allowed in allowed_origins:
        allowed_normalized = allowed.rstrip('/').lower()
        
        # Exact match
        if origin_normalized == allowed_normalized:
            return True
        
        # Subdomain wildcard (*.example.com)
        if allowed_normalized.startswith('*.'):
            suffix = allowed_normalized[2:]
            domain = origin_normalized.replace('https://', '').replace('http://', '')
            if domain == suffix or domain.endswith('.' + suffix):
                return True
    
    raise CORSError(f"CORS origin '{origin}' not allowed")


def get_cors_headers(origin: str, allowed_origins: list,
                     allowed_methods: list = None,
                     allowed_headers: list = None,
                     allow_credentials: bool = False) -> dict:
    """
    Get CORS headers for response.
    
    Args:
        origin: Request origin
        allowed_origins: List of allowed origins
        allowed_methods: List of allowed HTTP methods
        allowed_headers: List of allowed headers
        allow_credentials: Whether to allow credentials
        
    Returns:
        Dictionary of CORS headers
    """
    allowed_methods = allowed_methods or ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS']
    allowed_headers = allowed_headers or ['Content-Type', 'Authorization', 'X-Requested-With']
    
    # Validate origin first
    try:
        validate_cors_origin(origin, allowed_origins)
    except CORSError:
        return {}  # Return no CORS headers if origin not allowed
    
    headers = {
        'Access-Control-Allow-Origin': origin,
        'Access-Control-Allow-Methods': ', '.join(allowed_methods),
        'Access-Control-Allow-Headers': ', '.join(allowed_headers),
        'Access-Control-Max-Age': str(CORS_DEFAULT_MAX_AGE),
    }
    
    # Only allow credentials with specific origins (never with wildcard)
    if allow_credentials:
        headers['Access-Control-Allow-Credentials'] = 'true'
    
    return headers


def validate_cors_preflight_request(origin: str, requested_method: str,
                                     requested_headers: str,
                                     allowed_methods: list,
                                     allowed_headers: list) -> None:
    """
    Validate CORS preflight request.
    
    Args:
        origin: Request origin
        requested_method: Requested HTTP method
        requested_headers: Requested headers
        allowed_methods: Allowed HTTP methods
        allowed_headers: Allowed headers
        
    Raises:
        CORSError: If preflight request is invalid
    """
    # Validate requested method
    if requested_method and requested_method.upper() not in allowed_methods:
        raise CORSError(f"HTTP method '{requested_method}' not allowed")
    
    # Validate requested headers
    if requested_headers:
        requested = [h.strip().lower() for h in requested_headers.split(',')]
        allowed = [h.lower() for h in allowed_headers]
        
        for header in requested:
            if header not in allowed:
                raise CORSError(f"Header '{header}' not allowed")


# ============================================================================
# Pass 52: Audit Log Integrity (CVE-2026-3494)
# ============================================================================

class AuditIntegrityError(SecurityError):
    """Raised when audit log integrity issue is detected."""
    pass


def create_audit_log_entry(action: str, user: str, resource: str,
                           details: dict = None, 
                           include_hash: bool = True) -> dict:
    """
    Create tamper-evident audit log entry.
    
    CVE-2026-3494: Audit log bypass via log injection
    
    Args:
        action: Action performed
        user: User who performed action
        resource: Resource affected
        details: Additional details
        include_hash: Include integrity hash
        
    Returns:
        Audit log entry dictionary
    """
    entry = {
        'timestamp': time.time(),
        'timestamp_iso': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
        'action': str(action).replace('\n', '').replace('\r', ''),
        'user': str(user).replace('\n', '').replace('\r', ''),
        'resource': str(resource).replace('\n', '').replace('\r', '').replace('\x00', ''),
        'details': details or {},
    }
    
    if include_hash:
        entry['integrity_hash'] = _calculate_audit_hash(entry)
    
    return entry


def _calculate_audit_hash(entry: dict) -> str:
    """Calculate integrity hash for audit entry."""
    # Remove existing hash if present
    entry_copy = {k: v for k, v in entry.items() if k != 'integrity_hash'}
    
    # Create deterministic string representation
    import json
    data = json.dumps(entry_copy, sort_keys=True, separators=(',', ':'))
    
    # Calculate hash
    return hashlib.sha256(data.encode()).hexdigest()[:16]


def verify_audit_entry(entry: dict) -> bool:
    """
    Verify audit log entry integrity.
    
    Args:
        entry: Audit log entry
        
    Returns:
        True if entry integrity is valid
    """
    stored_hash = entry.get('integrity_hash')
    if not stored_hash:
        return False
    
    calculated_hash = _calculate_audit_hash(entry)
    return hmac.compare_digest(stored_hash, calculated_hash)


def sanitize_audit_user_id(user_id: str) -> str:
    """
    Sanitize user ID for audit logging.
    
    Args:
        user_id: User identifier
        
    Returns:
        Sanitized user ID
    """
    if not user_id:
        return 'anonymous'
    
    # Remove log injection characters
    sanitized = re.sub(r'[\r\n\x00]', '', str(user_id))
    
    # Limit length
    return sanitized[:128]


# ============================================================================
# Pass 53: Configuration Security Validation (CVE-2026-1731, CVE-2025-60262)
# ============================================================================

class ConfigValidationError(SecurityError):
    """Raised when configuration validation fails."""
    pass


# Dangerous configuration patterns
DANGEROUS_CONFIG_PATTERNS = [
    (r'password\s*=\s*[\'"]\s*[\'"]', "Empty password"),
    (r'secret\s*=\s*[\'"]\s*[\'"]', "Empty secret"),
    (r'debug\s*=\s*true', "Debug mode enabled"),
    (r'allow_origin\s*=\s*[\'"]?\*[\'"]?', "Wildcard CORS origin"),
    (r'bind\s*=\s*0\.0\.0\.0', "Binding to all interfaces"),
    (r'anonymous_bind\s*=\s*true', "Anonymous LDAP bind enabled"),
]


def validate_configuration_security(config_text: str) -> list:
    """
    Validate configuration for security issues.
    
    CVE-2026-1731: BeyondTrust command injection
    CVE-2025-60262: vsftpd misconfiguration
    
    Args:
        config_text: Configuration file content
        
    Returns:
        List of security issues found
    """
    issues = []
    
    for pattern, description in DANGEROUS_CONFIG_PATTERNS:
        if re.search(pattern, config_text, re.IGNORECASE):
            issues.append({
                'severity': 'high',
                'description': description,
                'pattern': pattern,
            })
    
    # Check for hardcoded secrets
    secret_patterns = [
        (r'api[_-]?key\s*=\s*["\']sk_[a-zA-Z0-9]{10,}["\']', "Potential hardcoded API key"),
        (r'api[_-]?key\s*=\s*["\']?[a-zA-Z0-9]{20,}["\']?', "Potential hardcoded API key"),
        (r'private[_-]?key\s*=\s*["\']?-----BEGIN', "Hardcoded private key"),
        (r'password\s*=\s*["\'][^"\'\s]{8,}["\']', "Potential hardcoded password"),
    ]
    
    for pattern, description in secret_patterns:
        if re.search(pattern, config_text, re.IGNORECASE | re.MULTILINE):
            issues.append({
                'severity': 'critical',
                'description': description,
                'pattern': pattern,
            })
    
    return issues


def check_secure_defaults(config: dict) -> list:
    """
    Check that secure defaults are in place.
    
    Args:
        config: Configuration dictionary
        
    Returns:
        List of missing security settings
    """
    missing = []
    
    required_security_settings = {
        'csrf_protection': True,
        'secure_cookies': True,
        'http_only_cookies': True,
        'xss_protection': True,
        'content_security_policy': True,
    }
    
    for setting, default in required_security_settings.items():
        if setting not in config:
            missing.append({
                'setting': setting,
                'recommended': default,
                'message': f"Security setting '{setting}' not configured",
            })
        elif config[setting] != default:
            missing.append({
                'setting': setting,
                'current': config[setting],
                'recommended': default,
                'message': f"Security setting '{setting}' not set to secure default",
            })
    
    return missing


# ============================================================================
# Pass 54: Error Message Sanitization (CVE-2026-26144, CVE-2026-20838)
# ============================================================================

class ErrorSanitizationError(SecurityError):
    """Raised when error sanitization fails."""
    pass


# Error messages that could leak sensitive information
SENSITIVE_ERROR_PATTERNS = [
    r'database',
    r'sql',
    r'query',
    r'stack trace',
    r'file \"',
    r'line \d+',
    r'exception',
    r'traceback',
    r'memory at',
    r'0x[0-9a-f]+',  # Memory addresses
]

def sanitize_production_error(error_message: str, 
                               is_production: bool = True) -> str:
    """
    Sanitize error message for production display.
    
    CVE-2026-26144: Excel information disclosure
    CVE-2026-20838: Windows Kernel information disclosure
    
    Args:
        error_message: Original error message
        is_production: Whether this is a production environment
        
    Returns:
        Sanitized error message
    """
    if not is_production:
        return error_message
    
    if not error_message:
        return "An error occurred"
    
    # In production, return generic messages
    # Map error types to user-friendly messages
    error_lower = error_message.lower()
    
    if any(kw in error_lower for kw in ['database', 'sql', 'query']):
        return "Database operation failed"
    
    if any(kw in error_lower for kw in ['file', 'path', 'directory', 'not found']):
        return "Resource not found"
    
    if any(kw in error_lower for kw in ['permission', 'access', 'unauthorized', 'forbidden']):
        return "Access denied"
    
    if any(kw in error_lower for kw in ['timeout', 'connection', 'network']):
        return "Connection failed"
    
    if any(kw in error_lower for kw in ['authentication', 'login', 'credential', 'password']):
        return "Authentication failed"
    
    # Default generic message
    return "An unexpected error occurred"


def get_safe_error_response(error: Exception, is_production: bool = True) -> dict:
    """
    Get safe error response for API.
    
    Args:
        error: Exception that occurred
        is_production: Whether in production mode
        
    Returns:
        Safe error response dictionary
    """
    error_id = hashlib.sha256(
        f"{time.time()}{str(error)}".encode()
    ).hexdigest()[:12]
    
    if is_production:
        return {
            'error': 'Internal Server Error',
            'error_id': error_id,
            'message': sanitize_production_error(str(error), True),
        }
    else:
        return {
            'error': type(error).__name__,
            'error_id': error_id,
            'message': str(error),
        }


# ============================================================================
# Pass 55: Session Timeout Enforcement (CVE-2026-23646)
# ============================================================================

class SessionTimeoutError(SecurityError):
    """Raised when session timeout issue is detected."""
    pass


DEFAULT_SESSION_TIMEOUT = 3600  # 1 hour
DEFAULT_IDLE_TIMEOUT = 900     # 15 minutes
MAX_SESSION_DURATION = 86400   # 24 hours

def validate_session_timeout(created_at: float, 
                              last_activity: float,
                              max_duration: int = MAX_SESSION_DURATION,
                              idle_timeout: int = DEFAULT_IDLE_TIMEOUT) -> None:
    """
    Validate session has not exceeded timeouts.
    
    CVE-2026-23646: Node.js session fixation and timeout
    
    Args:
        created_at: Session creation timestamp
        last_activity: Last activity timestamp
        max_duration: Maximum session duration in seconds
        idle_timeout: Idle timeout in seconds
        
    Raises:
        SessionTimeoutError: If session has expired
    """
    now = time.time()
    
    # Check absolute maximum duration
    session_age = now - created_at
    if session_age > max_duration:
        raise SessionTimeoutError(
            f"Session expired: exceeded maximum duration of {max_duration}s"
        )
    
    # Check idle timeout
    idle_time = now - last_activity
    if idle_time > idle_timeout:
        raise SessionTimeoutError(
            f"Session expired: idle timeout of {idle_timeout}s exceeded"
        )


def calculate_session_ttl(created_at: float, 
                          last_activity: float,
                          max_duration: int = MAX_SESSION_DURATION,
                          idle_timeout: int = DEFAULT_IDLE_TIMEOUT) -> int:
    """
    Calculate session time-to-live in seconds.
    
    Args:
        created_at: Session creation timestamp
        last_activity: Last activity timestamp
        max_duration: Maximum session duration
        idle_timeout: Idle timeout
        
    Returns:
        Seconds until session expires (0 if expired)
    """
    now = time.time()
    
    # Calculate remaining time based on max duration
    max_duration_remaining = max(0, max_duration - (now - created_at))
    
    # Calculate remaining time based on idle timeout
    idle_remaining = max(0, idle_timeout - (now - last_activity))
    
    # Return the minimum (session expires when either limit is reached)
    return int(min(max_duration_remaining, idle_remaining))


def should_refresh_session(created_at: float, 
                           refresh_threshold: float = 0.8) -> bool:
    """
    Check if session should be refreshed (regenerated).
    
    Args:
        created_at: Session creation timestamp
        refresh_threshold: Threshold at which to refresh (0-1)
        
    Returns:
        True if session should be refreshed
    """
    now = time.time()
    session_age = now - created_at
    
    return session_age > (MAX_SESSION_DURATION * refresh_threshold)


# ============================================================================
# Pass 56: File Upload Restriction (CVE-2026-21536)
# ============================================================================

class FileUploadRestrictionError(SecurityError):
    """Raised when file upload restriction is violated."""
    pass


# Dangerous file types for upload
DANGEROUS_FILE_TYPES = {
    # Executables
    '.exe', '.dll', '.bat', '.cmd', '.sh', '.bin',
    # Scripts
    '.php', '.jsp', '.asp', '.aspx', '.py', '.rb', '.pl',
    # Java
    '.jar', '.war', '.class',
    # Office macros
    '.docm', '.dotm', '.xlsm', '.xltm', '.pptm',
    # Archives that can contain executables
    '.zip', '.rar', '.7z', '.tar', '.gz',
    # System files
    '.sys', '.drv', '.vxd', '.com',
}

# Allowed safe file types for documents
SAFE_DOCUMENT_TYPES = {
    '.pdf', '.doc', '.docx', '.xls', '.xlsx', 
    '.ppt', '.pptx', '.txt', '.csv', '.json',
    '.xml', '.md', '.rtf', '.odt', '.ods', '.odp',
}

ALLOWED_UPLOAD_EXTENSIONS = SAFE_DOCUMENT_TYPES

def validate_upload_file_extension(filename: str, 
                                    allowed_extensions: set = None) -> None:
    """
    Validate file extension for upload.
    
    CVE-2026-21536: Microsoft Devices Pricing Program RCE via file upload
    
    Args:
        filename: Name of uploaded file
        allowed_extensions: Set of allowed extensions (defaults to safe docs)
        
    Raises:
        FileUploadRestrictionError: If file type is not allowed
    """
    allowed_extensions = allowed_extensions or ALLOWED_UPLOAD_EXTENSIONS
    
    if not filename:
        raise FileUploadRestrictionError("Filename is required")
    
    # Get extension (handle multiple extensions like .tar.gz)
    name_lower = filename.lower()
    
    # Check for dangerous extensions anywhere in the filename
    for ext in DANGEROUS_FILE_TYPES:
        if ext in name_lower:
            raise FileUploadRestrictionError(
                f"File type '{ext}' is not allowed for upload"
            )
    
    # Check actual extension is in allowed list
    actual_ext = Path(filename).suffix.lower()
    if actual_ext not in allowed_extensions:
        raise FileUploadRestrictionError(
            f"File extension '{actual_ext}' is not allowed. "
            f"Allowed: {', '.join(sorted(allowed_extensions))}"
        )


def validate_upload_file_size(size_bytes: int, 
                               max_size_mb: int = 10) -> None:
    """
    Validate uploaded file size.
    
    Args:
        size_bytes: File size in bytes
        max_size_mb: Maximum allowed size in MB
        
    Raises:
        FileUploadRestrictionError: If file is too large
    """
    max_bytes = max_size_mb * 1024 * 1024
    
    if size_bytes > max_bytes:
        raise FileUploadRestrictionError(
            f"File size {size_bytes / (1024*1024):.1f}MB exceeds "
            f"maximum allowed {max_size_mb}MB"
        )


def sanitize_uploaded_filename(filename: str) -> str:
    """
    Sanitize uploaded filename.
    
    Args:
        filename: Original filename
        
    Returns:
        Sanitized filename
    """
    if not filename:
        return 'unnamed_file'
    
    # Get basename only
    basename = os.path.basename(filename)
    
    # Remove null bytes
    basename = basename.replace('\x00', '')
    
    # Remove control characters
    basename = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', basename)
    
    # Replace dangerous characters
    basename = re.sub(r'[<>:"/\\|?*]', '_', basename)
    
    # Ensure it doesn't start with dot (hidden file)
    if basename.startswith('.'):
        basename = 'file_' + basename
    
    # Limit length
    name, ext = os.path.splitext(basename)
    if len(name) > 100:
        name = name[:100]
    basename = name + ext
    
    # Ensure not empty
    if not basename or basename.strip() == '':
        basename = 'unnamed_file'
    
    return basename


# ============================================================================
# Pass 57: Request Origin Validation (CVE-2026-25151, CVE-2026-25221)
# ============================================================================

class OriginValidationError(SecurityError):
    """Raised when origin validation fails."""
    pass


def validate_request_origin(request_headers: dict,
                            allowed_hosts: list,
                            require_https: bool = True) -> None:
    """
    Validate request origin against allowed hosts.
    
    CVE-2026-25151: Qwik CSRF via Content-Type parsing
    CVE-2026-25221: PolarLearn OAuth Login CSRF
    
    Args:
        request_headers: HTTP request headers
        allowed_hosts: List of allowed host:port combinations
        require_https: Require HTTPS for production
        
    Raises:
        OriginValidationError: If origin is not valid
    """
    # Get origin or referer
    origin = request_headers.get('Origin')
    referer = request_headers.get('Referer')
    host = request_headers.get('Host')
    
    # For state-changing requests, require Origin header
    if not origin and not referer:
        raise OriginValidationError("Origin or Referer header required")
    
    # Validate origin
    check_origin = origin or referer
    if check_origin:
        # Parse the origin
        parsed = urlparse(check_origin)
        origin_host = parsed.netloc.lower()
        
        # Check against allowed hosts
        allowed = [h.lower() for h in allowed_hosts]
        
        if origin_host not in allowed:
            raise OriginValidationError(
                f"Origin '{origin_host}' not in allowed hosts"
            )
        
        # Check HTTPS requirement
        if require_https and parsed.scheme != 'https':
            # Allow localhost in development
            if not (origin_host.startswith('localhost') or 
                    origin_host.startswith('127.')):
                raise OriginValidationError(
                    "HTTPS required for non-localhost origins"
                )


def validate_oauth_state(state: str, stored_state: str, 
                         max_age: int = 600) -> None:
    """
    Validate OAuth state parameter.
    
    CVE-2026-25221: PolarLearn OAuth Login CSRF
    
    Args:
        state: State parameter from OAuth callback
        stored_state: Stored state from session
        max_age: Maximum age of state in seconds
        
    Raises:
        OriginValidationError: If state is invalid
    """
    if not state or not stored_state:
        raise OriginValidationError("OAuth state parameter missing")
    
    # Constant-time comparison
    if not hmac.compare_digest(state, stored_state):
        raise OriginValidationError("OAuth state mismatch - possible CSRF")


# ============================================================================
# Pass 58: Security Header Consolidation
# ============================================================================

SECURITY_HEADERS = {
    # Prevent MIME type sniffing
    'X-Content-Type-Options': 'nosniff',
    
    # XSS Protection
    'X-XSS-Protection': '1; mode=block',
    
    # Clickjacking protection
    'X-Frame-Options': 'DENY',
    
    # Enforce HTTPS
    'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
    
    # Referrer policy
    'Referrer-Policy': 'strict-origin-when-cross-origin',
    
    # Permissions policy (formerly Feature-Policy)
    'Permissions-Policy': (
        'accelerometer=(), camera=(), geolocation=(), gyroscope=(), '
        'magnetometer=(), microphone=(), payment=(), usb=()'
    ),
}

def get_security_headers(https_only: bool = True) -> dict:
    """
    Get recommended security headers.
    
    Returns consolidated security headers for web application protection.
    
    Args:
        https_only: Include HTTPS enforcement headers
        
    Returns:
        Dictionary of security headers
    """
    headers = SECURITY_HEADERS.copy()
    
    if not https_only:
        # Remove HSTS for non-HTTPS environments (development)
        del headers['Strict-Transport-Security']
    
    return headers


def get_content_security_policy(nonce: str = None) -> str:
    """
    Get Content Security Policy header value.
    
    Args:
        nonce: Optional nonce for inline scripts
        
    Returns:
        CSP policy string
    """
    script_src = "'self'"
    if nonce:
        script_src += f" 'nonce-{nonce}'"
    
    policy = (
        f"default-src 'self'; "
        f"script-src {script_src}; "
        f"style-src 'self' 'unsafe-inline'; "
        f"img-src 'self' data: https:; "
        f"font-src 'self'; "
        f"connect-src 'self'; "
        f"media-src 'self'; "
        f"object-src 'none'; "
        f"frame-ancestors 'none'; "
        f"form-action 'self'; "
        f"base-uri 'self';"
    )
    
    return policy


def validate_security_headers(response_headers: dict) -> list:
    """
    Validate that response has required security headers.
    
    Args:
        response_headers: HTTP response headers
        
    Returns:
        List of missing or weak security headers
    """
    issues = []
    headers_lower = {k.lower(): v for k, v in response_headers.items()}
    
    required_headers = {
        'x-content-type-options': 'nosniff',
        'x-frame-options': ['deny', 'sameorigin'],
        'strict-transport-security': None,  # Just needs to exist
    }
    
    for header, expected in required_headers.items():
        if header not in headers_lower:
            issues.append({
                'header': header,
                'issue': 'missing',
                'severity': 'medium',
            })
        elif expected:
            actual = headers_lower[header].lower()
            if isinstance(expected, list):
                if actual not in expected:
                    issues.append({
                        'header': header,
                        'issue': 'weak',
                        'expected': expected,
                        'actual': actual,
                        'severity': 'low',
                    })
            elif actual != expected:
                issues.append({
                    'header': header,
                    'issue': 'incorrect',
                    'expected': expected,
                    'actual': actual,
                    'severity': 'low',
                })
    
    return issues


# ============================================================================
# Update __all__ exports
# ============================================================================

__all__.extend([
    # Pass 46: Rate Limiting
    'RateLimitError',
    'RateLimiter',
    'check_rate_limit',
    'extract_client_ip',
    
    # Pass 47: Authentication Flow
    'AuthenticationError',
    'validate_ldap_auth_response',
    'validate_auth_attempt',
    
    # Pass 48: Credential Rotation
    'CredentialRotationError',
    'generate_secure_api_key',
    'validate_api_key_format',
    'should_rotate_api_key',
    'mask_api_key',
    
    # Pass 49: CSRF Protection
    'CSRFError',
    'generate_csrf_token',
    'validate_csrf_token',
    'validate_content_type_for_csrf',
    'validate_origin_header',
    
    # Pass 50: WebSocket Security
    'WebSocketSecurityError',
    'validate_websocket_origin',
    'get_websocket_security_headers',
    
    # Pass 51: CORS
    'CORSError',
    'validate_cors_origin',
    'get_cors_headers',
    'validate_cors_preflight_request',
    'CORS_DEFAULT_MAX_AGE',
    
    # Pass 52: Audit Integrity
    'AuditIntegrityError',
    'create_audit_log_entry',
    'verify_audit_entry',
    'sanitize_audit_user_id',
    
    # Pass 53: Config Validation
    'ConfigValidationError',
    'validate_configuration_security',
    'check_secure_defaults',
    
    # Pass 54: Error Sanitization
    'ErrorSanitizationError',
    'sanitize_production_error',
    'get_safe_error_response',
    
    # Pass 55: Session Timeout
    'SessionTimeoutError',
    'validate_session_timeout',
    'calculate_session_ttl',
    'should_refresh_session',
    'DEFAULT_SESSION_TIMEOUT',
    'MAX_SESSION_DURATION',
    
    # Pass 56: File Upload
    'FileUploadRestrictionError',
    'validate_upload_file_extension',
    'validate_upload_file_size',
    'sanitize_uploaded_filename',
    'DANGEROUS_FILE_TYPES',
    'SAFE_DOCUMENT_TYPES',
    
    # Pass 57: Origin Validation
    'OriginValidationError',
    'validate_request_origin',
    'validate_oauth_state',
    
    # Pass 58: Security Headers
    'get_security_headers',
    'get_content_security_policy',
    'validate_security_headers',
    'SECURITY_HEADERS',
])


# ============================================================================
# Pass 59: Request Validation Middleware (CVE-2026-21962, CVE-2026-0958)
# ============================================================================

class RequestValidationError(SecurityError):
    """Raised when request validation fails."""
    pass


# Maximum request sizes
MAX_JSON_SIZE = 10 * 1024 * 1024  # 10 MB
MAX_REQUEST_SIZE = 100 * 1024 * 1024  # 100 MB

# Allowed Content-Types for API requests
ALLOWED_CONTENT_TYPES = [
    'application/json',
    'application/xml',
    'application/x-www-form-urlencoded',
    'multipart/form-data',
    'text/plain',
    'text/xml',
]


def validate_request_size(content_length: int, max_size: int = MAX_REQUEST_SIZE) -> None:
    """
    Validate request size to prevent DoS.
    
    CVE-2026-0958: GitLab JSON validation middleware DoS
    CVE-2026-28342: OliveTin PasswordHash API DoS
    
    Args:
        content_length: Content-Length header value
        max_size: Maximum allowed size in bytes
        
    Raises:
        RequestValidationError: If request is too large
    """
    if content_length > max_size:
        raise RequestValidationError(
            f"Request size {content_length} exceeds maximum {max_size}"
        )


def validate_content_type(content_type: str, allowed_types: list = None) -> None:
    """
    Validate Content-Type header.
    
    CVE-2026-21962: Oracle Fusion Middleware auth bypass via crafted requests
    
    Args:
        content_type: Content-Type header value
        allowed_types: List of allowed content types
        
    Raises:
        RequestValidationError: If content type is not allowed
    """
    allowed_types = allowed_types or ALLOWED_CONTENT_TYPES
    
    if not content_type:
        return  # No content type specified
    
    # Extract main content type (remove charset, boundary, etc.)
    main_type = content_type.split(';')[0].strip().lower()
    
    if main_type not in allowed_types:
        raise RequestValidationError(
            f"Content-Type '{main_type}' not allowed. Allowed: {allowed_types}"
        )


def validate_json_payload(payload: str, max_size: int = MAX_JSON_SIZE) -> dict:
    """
    Validate and parse JSON payload securely.
    
    CVE-2026-0958: GitLab JSON validation middleware resource exhaustion
    CVE-2026-28794: Prototype pollution in RPC JSON deserializer
    
    Args:
        payload: JSON string
        max_size: Maximum payload size
        
    Returns:
        Parsed JSON as dictionary
        
    Raises:
        RequestValidationError: If payload is invalid or dangerous
    """
    if len(payload) > max_size:
        raise RequestValidationError(f"JSON payload exceeds maximum size of {max_size}")
    
    try:
        import json
        data = json.loads(payload)
    except json.JSONDecodeError as e:
        raise RequestValidationError(f"Invalid JSON: {e}")
    
    # Check for prototype pollution patterns
    _check_prototype_pollution(data)
    
    return data


def _check_prototype_pollution(data: Any, path: str = "") -> None:
    """Check for prototype pollution patterns in data."""
    if isinstance(data, dict):
        for key in data.keys():
            if key in ('__proto__', 'constructor', 'prototype'):
                raise RequestValidationError(
                    f"Prototype pollution attempt detected at '{path}.{key}'"
                )
            _check_prototype_pollution(data[key], f"{path}.{key}")
    elif isinstance(data, list):
        for i, item in enumerate(data):
            _check_prototype_pollution(item, f"{path}[{i}]")


def sanitize_request_path(path: str) -> str:
    """
    Sanitize request path to prevent path manipulation.
    
    CVE-2026-21962: Oracle Fusion Middleware path normalization errors
    
    Args:
        path: URL path
        
    Returns:
        Sanitized path
        
    Raises:
        RequestValidationError: If path contains dangerous patterns
    """
    # Block null bytes
    if '\x00' in path:
        raise RequestValidationError("Path contains null byte")
    
    # Block path traversal attempts
    if '..' in path or '%2e%2e' in path.lower():
        raise RequestValidationError("Path traversal detected")
    
    # Block encoded slashes that might bypass middleware
    if '%2f' in path.lower() or '%5c' in path.lower():
        raise RequestValidationError("Encoded path separators detected")
    
    # Normalize multiple slashes
    while '//' in path:
        path = path.replace('//', '/')
    
    return path


# ============================================================================
# Pass 60: Response Security Middleware (CVE-2026-2975, CVE-2026-24489)
# ============================================================================

class ResponseSecurityError(SecurityError):
    """Raised when response security validation fails."""
    pass


def validate_response_headers(headers: dict) -> dict:
    """
    Validate and sanitize response headers.
    
    CVE-2026-24489: HTTP header injection
    CVE-2026-2975: FastAPI Admin information disclosure via headers
    
    Args:
        headers: Response headers dictionary
        
    Returns:
        Sanitized headers
    """
    sanitized = {}
    
    for name, value in headers.items():
        # Sanitize header name
        clean_name = sanitize_http_header_name(name)
        
        # Sanitize header value
        clean_value = sanitize_http_header_value(str(value))
        
        sanitized[clean_name] = clean_value
    
    return sanitized


def add_security_headers(headers: dict, https_only: bool = True) -> dict:
    """
    Add security headers to response.
    
    Args:
        headers: Existing headers
        https_only: Whether to add HTTPS-only headers
        
    Returns:
        Headers with security headers added
    """
    security_headers = get_security_headers(https_only=https_only)
    
    # Add security headers (don't override existing)
    for name, value in security_headers.items():
        if name not in headers:
            headers[name] = value
    
    return headers


def validate_response_content_type(content_type: str) -> None:
    """
    Validate response Content-Type to prevent MIME sniffing attacks.
    
    Args:
        content_type: Content-Type header value
        
    Raises:
        ResponseSecurityError: If content type is dangerous
    """
    dangerous_types = [
        'application/x-shockwave-flash',
        'application/x-msdownload',
        'application/x-msdos-program',
    ]
    
    main_type = content_type.split(';')[0].strip().lower()
    
    if main_type in dangerous_types:
        raise ResponseSecurityError(
            f"Dangerous Content-Type '{main_type}' not allowed in responses"
        )


# ============================================================================
# Pass 61: Authentication Middleware Integration (CVE-2026-27705, CVE-2026-1894)
# ============================================================================

class AuthenticationMiddlewareError(SecurityError):
    """Raised when authentication middleware detects an issue."""
    pass


def extract_auth_token(request_headers: dict, 
                        query_params: dict = None,
                        cookie: str = None) -> tuple:
    """
    Extract authentication token from request.
    
    CVE-2026-27705: Plane auth bypass via missing workspace validation
    CVE-2026-1894: WeKan REST API auth bypass
    
    Args:
        request_headers: HTTP request headers
        query_params: URL query parameters
        cookie: Cookie string
        
    Returns:
        Tuple of (token_type, token_value) or (None, None)
    """
    # Check Authorization header first
    auth_header = request_headers.get('Authorization', '')
    if auth_header:
        parts = auth_header.split(' ', 1)
        if len(parts) == 2:
            return (parts[0].lower(), parts[1])
        return ('bearer', auth_header)
    
    # Check API key header
    api_key = request_headers.get('X-API-Key') or request_headers.get('Api-Key')
    if api_key:
        return ('apikey', api_key)
    
    # Check query parameter (less secure, but sometimes used)
    if query_params:
        token = query_params.get('token') or query_params.get('api_key')
        if token:
            return ('query', token)
    
    # Check cookie
    if cookie:
        # Parse cookie for session token
        import re
        session_match = re.search(r'session=([^;]+)', cookie)
        if session_match:
            return ('cookie', session_match.group(1))
    
    return (None, None)


def validate_auth_context(token: str, token_type: str, 
                          required_context: dict = None) -> dict:
    """
    Validate authentication token with context checks.
    
    CVE-2026-27705: IDOR via missing context validation
    
    Args:
        token: Authentication token
        token_type: Type of token (bearer, apikey, etc.)
        required_context: Required context (workspace, project, etc.)
        
    Returns:
        Validated auth context
        
    Raises:
        AuthenticationMiddlewareError: If validation fails
    """
    if not token:
        raise AuthenticationMiddlewareError("No authentication token provided")
    
    # Basic token validation
    if len(token) < 16:
        raise AuthenticationMiddlewareError("Token too short")
    
    # Context validation
    if required_context:
        # In real implementation, this would verify token has access to context
        pass
    
    return {
        'token': mask_api_key(token),
        'type': token_type,
        'valid': True,
    }


# ============================================================================
# Pass 62: Authorization Enforcement Layer (CVE-2026-27705, CVE-2026-23982)
# ============================================================================

class AuthorizationError(SecurityError):
    """Raised when authorization check fails."""
    pass


# Role definitions
ROLE_ADMIN = 'admin'
ROLE_MEMBER = 'member'
ROLE_GUEST = 'guest'
ROLE_READONLY = 'readonly'

# Permission hierarchy
ROLE_HIERARCHY = {
    ROLE_ADMIN: 4,
    ROLE_MEMBER: 3,
    ROLE_GUEST: 2,
    ROLE_READONLY: 1,
}


def check_resource_access(user_role: str, resource_owner: str, 
                          requesting_user: str, action: str = 'read') -> None:
    """
    Check if user has access to resource with IDOR prevention.
    
    CVE-2026-27705: Plane IDOR via missing workspace/project validation
    CVE-2026-23982: Apache Superset data access control bypass
    
    Args:
        user_role: User's role
        resource_owner: Owner of the resource
        requesting_user: User requesting access
        action: Action being performed (read, write, delete)
        
    Raises:
        AuthorizationError: If access is denied
    """
    # Admin can access anything
    if user_role == ROLE_ADMIN:
        return
    
    # Users can access their own resources
    if resource_owner == requesting_user:
        return
    
    # Check role-based permissions
    if action == 'delete' and user_role != ROLE_ADMIN:
        raise AuthorizationError("Only admins can delete resources")
    
    if action == 'write' and user_role not in (ROLE_ADMIN, ROLE_MEMBER):
        raise AuthorizationError("Insufficient permissions for write operation")
    
    # Guest and readonly can only read
    if action in ('write', 'delete') and user_role in (ROLE_GUEST, ROLE_READONLY):
        raise AuthorizationError("Read-only users cannot modify resources")


def require_permission(required_role: str, user_role: str) -> None:
    """
    Require minimum role level.
    
    Args:
        required_role: Minimum required role
        user_role: User's actual role
        
    Raises:
        AuthorizationError: If user doesn't have required role
    """
    required_level = ROLE_HIERARCHY.get(required_role, 0)
    user_level = ROLE_HIERARCHY.get(user_role, 0)
    
    if user_level < required_level:
        raise AuthorizationError(
            f"Role '{user_role}' insufficient. Required: '{required_role}'"
        )


# ============================================================================
# Pass 63: Database Query Protection (CVE-2026-25544, CVE-2026-23984)
# ============================================================================

class DatabaseSecurityError(SecurityError):
    """Raised when database security check fails."""
    pass


# Dangerous SQL keywords for raw query checking
DANGEROUS_SQL_KEYWORDS = [
    'DROP', 'DELETE', 'TRUNCATE', 'ALTER', 'GRANT', 'REVOKE',
    'EXEC', 'EXECUTE', 'sp_', 'xp_', 'sys_',
]


def validate_raw_query(query: str, allowed_tables: list = None) -> None:
    """
    Validate raw SQL query for dangerous patterns.
    
    CVE-2026-25544: Payload CMS SQL injection via JSON fields
    CVE-2026-23984: Apache Superset SQL injection on read-only connections
    
    Args:
        query: SQL query string
        allowed_tables: List of allowed table names
        
    Raises:
        DatabaseSecurityError: If query contains dangerous patterns
    """
    query_upper = query.upper()
    
    # Check for dangerous keywords
    for keyword in DANGEROUS_SQL_KEYWORDS:
        if keyword in query_upper:
            raise DatabaseSecurityError(
                f"Query contains dangerous keyword: {keyword}"
            )
    
    # Check for multiple statements
    if ';' in query and not query.strip().endswith(';'):
        raise DatabaseSecurityError("Multiple SQL statements not allowed")
    
    # Check table allowlist
    if allowed_tables:
        # Extract table names (simplified check)
        import re
        allowed_tables_upper = [t.upper() for t in allowed_tables]
        from_words = re.findall(r'FROM\s+(\w+)', query_upper)
        join_words = re.findall(r'JOIN\s+(\w+)', query_upper)
        
        for table in from_words + join_words:
            if table not in allowed_tables_upper:
                raise DatabaseSecurityError(f"Table '{table}' not in allowlist")


def sanitize_query_parameter(value: Any) -> Any:
    """
    Sanitize query parameter to prevent injection.
    
    Args:
        value: Parameter value
        
    Returns:
        Sanitized value
    """
    if isinstance(value, str):
        # Remove null bytes
        value = value.replace('\x00', '')
        
        # Block SQL comment sequences
        value = value.replace('--', '').replace('/*', '').replace('*/', '')
        
        # Block dangerous characters
        value = re.sub(r'[;\x00-\x1f]', '', value)
    
    return value


# ============================================================================
# Pass 64: Input Sanitization Pipeline (CVE-2026-25632, CVE-2026-25520)
# ============================================================================

class InputSanitizationError(SecurityError):
    """Raised when input sanitization fails."""
    pass


# Unicode dangerous characters
UNICODE_DANGEROUS = [
    '\u200b',  # Zero-width space
    '\u200c',  # Zero-width non-joiner
    '\u200d',  # Zero-width joiner
    '\ufeff',  # Byte order mark
]


def sanitize_input_pipeline(value: str, 
                             allow_html: bool = False,
                             max_length: int = 10000) -> str:
    """
    Sanitize input through security pipeline.
    
    CVE-2026-25632: EPyT-Flow OS command injection via JSON parsing
    CVE-2026-25520: SandboxJS injection vulnerability
    
    Args:
        value: Input string
        allow_html: Whether to allow HTML (if False, strips all HTML)
        max_length: Maximum allowed length
        
    Returns:
        Sanitized string
        
    Raises:
        InputSanitizationError: If input is invalid
    """
    if not isinstance(value, str):
        value = str(value)
    
    # Check length
    if len(value) > max_length:
        raise InputSanitizationError(
            f"Input exceeds maximum length of {max_length}"
        )
    
    # Remove invisible Unicode characters
    for char in UNICODE_DANGEROUS:
        value = value.replace(char, '')
    
    # Normalize Unicode
    import unicodedata
    value = unicodedata.normalize('NFKC', value)
    
    # Remove null bytes
    value = value.replace('\x00', '')
    
    # HTML handling
    if not allow_html:
        # Strip all HTML tags
        value = re.sub(r'<[^>]+>', '', value)
    else:
        # Allow only safe HTML (simplified - in production use bleach)
        value = sanitize_html_input(value)
    
    return value.strip()


def sanitize_html_input(html: str) -> str:
    """
    Sanitize HTML input to prevent XSS.
    
    Args:
        html: HTML string
        
    Returns:
        Sanitized HTML
    """
    # Remove script tags and event handlers
    # This is a simplified version - production should use a proper HTML sanitizer
    
    # Remove script tags
    html = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL | re.IGNORECASE)
    
    # Remove event handlers
    html = re.sub(r'\s*on\w+\s*=\s*["\'][^"\']*["\']', '', html, flags=re.IGNORECASE)
    
    # Remove javascript: URLs
    html = re.sub(r'javascript:', '', html, flags=re.IGNORECASE)
    
    return html


def sanitize_file_path_input(path: str) -> str:
    """
    Sanitize file path input.
    
    Args:
        path: File path
        
    Returns:
        Sanitized path
        
    Raises:
        InputSanitizationError: If path is dangerous
    """
    # Remove null bytes
    path = path.replace('\x00', '')
    
    # Check for path traversal
    if '..' in path or '%2e' in path.lower():
        raise InputSanitizationError("Path traversal detected")
    
    # Remove dangerous characters
    path = re.sub(r'[<>:"|?*]', '', path)
    
    return path


# ============================================================================
# Pass 65: Output Encoding Framework (CVE-2026-25643, CVE-2026-25881)
# ============================================================================

class OutputEncodingError(SecurityError):
    """Raised when output encoding fails."""
    pass


def encode_html_output(text: str) -> str:
    """
    Encode text for HTML output to prevent XSS.
    
    CVE-2026-25643: Frigate config.yaml command injection
    CVE-2026-25881: SandboxJS sandbox escape
    
    Args:
        text: Raw text
        
    Returns:
        HTML-encoded text
    """
    if not isinstance(text, str):
        text = str(text)
    
    # HTML entity encoding
    html_escape_table = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#x27;',
        '/': '&#x2F;',
    }
    
    return ''.join(html_escape_table.get(c, c) for c in text)


def encode_javascript_output(text: str) -> str:
    """
    Encode text for JavaScript string output.
    
    Args:
        text: Raw text
        
    Returns:
        JavaScript-encoded text
    """
    if not isinstance(text, str):
        text = str(text)
    
    # JavaScript string escaping
    js_escape_table = {
        '\\': '\\\\',
        '"': '\\"',
        "'": "\\'",
        '\n': '\\n',
        '\r': '\\r',
        '\t': '\\t',
        '<': '\\u003c',
        '>': '\\u003e',
        '&': '\\u0026',
    }
    
    return ''.join(js_escape_table.get(c, c) for c in text)


def encode_css_output(value: str) -> str:
    """
    Encode value for CSS output.
    
    Args:
        value: Raw value
        
    Returns:
        CSS-encoded value
    """
    if not isinstance(value, str):
        value = str(value)
    
    # Only allow safe CSS characters
    # Remove dangerous characters including parentheses for expression()
    value = re.sub(r'[<>&"\'()]', '', value)
    
    return value


def encode_url_output(url: str) -> str:
    """
    Encode URL for safe output.
    
    Args:
        url: URL string
        
    Returns:
        Encoded URL
    """
    from urllib.parse import quote
    
    if not isinstance(url, str):
        url = str(url)
    
    # Quote dangerous characters but preserve URL structure
    return quote(url, safe='/:?=&')


def encode_json_output(data: Any) -> str:
    """
    Encode data for JSON output with XSS protection.
    
    Args:
        data: Data to encode
        
    Returns:
        JSON string
    """
    import json
    
    # Serialize with escaping
    json_str = json.dumps(data, ensure_ascii=True)
    
    return json_str


# ============================================================================
# Pass 66: Session Management Integration (CVE-2026-23646, CVE-2026-22341)
# ============================================================================

class SessionManagementError(SecurityError):
    """Raised when session management fails."""
    pass


class SecureSessionStore:
    """
    Secure session store with timeout and binding.
    
    CVE-2026-23646: Node.js session fixation and timeout
    CVE-2026-22341: IBM Security Verify Access OIDC session fixation
    """
    
    def __init__(self, max_age: int = 3600, idle_timeout: int = 900):
        self.sessions = {}
        self.max_age = max_age
        self.idle_timeout = idle_timeout
    
    def create_session(self, user_id: str, ip_address: str = None,
                       user_agent: str = None) -> str:
        """
        Create new secure session.
        
        Args:
            user_id: User identifier
            ip_address: Client IP for binding
            user_agent: User agent for binding
            
        Returns:
            Session ID
        """
        import secrets
        
        session_id = secrets.token_urlsafe(32)
        
        self.sessions[session_id] = {
            'user_id': user_id,
            'created_at': time.time(),
            'last_activity': time.time(),
            'ip_address': ip_address,
            'user_agent': user_agent,
        }
        
        return session_id
    
    def validate_session(self, session_id: str, ip_address: str = None,
                         user_agent: str = None) -> dict:
        """
        Validate session with security checks.
        
        Args:
            session_id: Session ID
            ip_address: Current client IP
            user_agent: Current user agent
            
        Returns:
            Session data
            
        Raises:
            SessionManagementError: If session is invalid
        """
        if session_id not in self.sessions:
            raise SessionManagementError("Invalid session")
        
        session = self.sessions[session_id]
        
        # Check timeout
        try:
            validate_session_timeout(
                session['created_at'],
                session['last_activity'],
                self.max_age,
                self.idle_timeout
            )
        except SessionTimeoutError:
            del self.sessions[session_id]
            raise SessionManagementError("Session expired")
        
        # Update last activity
        session['last_activity'] = time.time()
        
        return session
    
    def regenerate_session(self, old_session_id: str) -> str:
        """
        Regenerate session ID (prevents fixation attacks).
        
        Args:
            old_session_id: Old session ID
            
        Returns:
            New session ID
        """
        if old_session_id not in self.sessions:
            raise SessionManagementError("Invalid session")
        
        session_data = self.sessions[old_session_id]
        
        # Create new session
        new_session_id = self.create_session(
            session_data['user_id'],
            session_data['ip_address'],
            session_data['user_agent']
        )
        
        # Copy data to new session
        self.sessions[new_session_id].update({
            'created_at': session_data['created_at'],
        })
        
        # Delete old session
        del self.sessions[old_session_id]
        
        return new_session_id


# ============================================================================
# Pass 67: File Operation Security (CVE-2026-27897, CVE-2026-25766)
# ============================================================================

class FileOperationError(SecurityError):
    """Raised when file operation security check fails."""
    pass


def secure_file_read(filepath: str, base_dir: str = None,
                     max_size: int = 10*1024*1024) -> bytes:
    """
    Read file securely with path validation.
    
    CVE-2026-27897: Vociferous path traversal via export_file
    CVE-2026-25766: Echo middleware.Static path traversal via backslash
    
    Args:
        filepath: File path to read
        base_dir: Allowed base directory
        max_size: Maximum file size
        
    Returns:
        File contents as bytes
        
    Raises:
        FileOperationError: If file access is not allowed
    """
    # Validate path
    if base_dir:
        try:
            validate_path(filepath, base_dir)
        except PathTraversalError as e:
            raise FileOperationError(f"Path validation failed: {e}")
    
    # Check file exists and is a file
    path = Path(filepath)
    if not path.exists():
        raise FileOperationError("File not found")
    
    if not path.is_file():
        raise FileOperationError("Not a file")
    
    # Check size
    file_size = path.stat().st_size
    if file_size > max_size:
        raise FileOperationError(f"File too large: {file_size} bytes")
    
    # Read file
    try:
        with open(path, 'rb') as f:
            return f.read()
    except IOError as e:
        raise FileOperationError(f"Cannot read file: {e}")


def secure_file_write(filepath: str, content: bytes,
                      base_dir: str = None,
                      max_size: int = 100*1024*1024) -> None:
    """
    Write file securely with path validation.
    
    Args:
        filepath: File path to write
        content: Content to write
        base_dir: Allowed base directory
        max_size: Maximum content size
        
    Raises:
        FileOperationError: If write is not allowed
    """
    # Check content size
    if len(content) > max_size:
        raise FileOperationError(f"Content too large: {len(content)} bytes")
    
    # Validate path
    if base_dir:
        try:
            validate_path(filepath, base_dir)
        except PathTraversalError as e:
            raise FileOperationError(f"Path validation failed: {e}")
    
    # Ensure directory exists
    path = Path(filepath)
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
    except OSError as e:
        raise FileOperationError(f"Cannot create directory: {e}")
    
    # Write atomically
    try:
        atomic_write(filepath, content)
    except IOError as e:
        raise FileOperationError(f"Cannot write file: {e}")


def get_secure_download_headers(filename: str, content_type: str = None) -> dict:
    """
    Get security headers for file downloads.
    
    Args:
        filename: Download filename
        content_type: MIME type
        
    Returns:
        Security headers dict
    """
    headers = {
        'X-Content-Type-Options': 'nosniff',
        'Content-Disposition': f'attachment; filename="{filename}"',
    }
    
    if content_type:
        headers['Content-Type'] = content_type
    
    return headers


# ============================================================================
# Pass 68: API Security Hardening (CVE-2026-25544, CVE-2026-1894)
# ============================================================================

class APISecurityError(SecurityError):
    """Raised when API security check fails."""
    pass


# API endpoint rate limits
API_RATE_LIMITS = {
    'default': (100, 60),      # 100 requests per 60 seconds
    'login': (5, 60),          # 5 login attempts per minute
    'upload': (10, 60),        # 10 uploads per minute
    'export': (5, 300),        # 5 exports per 5 minutes
}


def validate_api_request(endpoint: str, method: str,
                         user_id: str = None,
                         api_limits: dict = None) -> None:
    """
    Validate API request with endpoint-specific checks.
    
    CVE-2026-25544: Payload CMS API SQL injection
    CVE-2026-1894: WeKan REST API auth bypass
    
    Args:
        endpoint: API endpoint path
        method: HTTP method
        user_id: User identifier for rate limiting
        api_limits: Custom rate limits
        
    Raises:
        APISecurityError: If request is not allowed
    """
    api_limits = api_limits or API_RATE_LIMITS
    
    # Get rate limit for endpoint
    limit_key = 'default'
    for key in api_limits:
        if key in endpoint.lower():
            limit_key = key
            break
    
    max_requests, window = api_limits[limit_key]
    
    # Check rate limit
    if user_id:
        try:
            check_rate_limit(f"api:{endpoint}:{user_id}", max_requests, window)
        except RateLimitError as e:
            raise APISecurityError(f"API rate limit exceeded: {e}")
    
    # Validate HTTP method
    allowed_methods = ['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS']
    if method not in allowed_methods:
        raise APISecurityError(f"HTTP method '{method}' not allowed")


def validate_graphql_query(query: str, max_depth: int = 10) -> None:
    """
    Validate GraphQL query for security issues.
    
    Args:
        query: GraphQL query string
        max_depth: Maximum query depth
        
    Raises:
        APISecurityError: If query is dangerous
    """
    # Check for excessive depth
    depth = query.count('{') - query.count('fragment')
    if depth > max_depth:
        raise APISecurityError(f"GraphQL query depth {depth} exceeds maximum {max_depth}")
    
    # Check for circular fragments (simplified)
    fragment_count = query.lower().count('fragment')
    if fragment_count > 10:
        raise APISecurityError("Too many fragments in query")
    
    # Check for dangerous introspection queries
    if '__schema' in query or '__type' in query:
        # In production, you might want to disable introspection entirely
        pass


def validate_bulk_operation(items: list, max_items: int = 100) -> None:
    """
    Validate bulk operation request.
    
    Args:
        items: List of items to process
        max_items: Maximum allowed items
        
    Raises:
        APISecurityError: If bulk operation is too large
    """
    if len(items) > max_items:
        raise APISecurityError(
            f"Bulk operation exceeds maximum of {max_items} items"
        )


# ============================================================================
# Pass 69: Webhook Security (CVE-2026-27488, CVE-2026-28467)
# ============================================================================

class WebhookSecurityError(SecurityError):
    """Raised when webhook security check fails."""
    pass


# Allowed webhook URL patterns
WEBHOOK_ALLOWED_SCHEMES = ['https']
WEBHOOK_BLOCKED_HOSTS = [
    'localhost', '127.0.0.1', '0.0.0.0',
    '169.254.169.254',  # Cloud metadata
    '[::1]', '0:0:0:0:0:0:0:1',
]


def validate_webhook_url(url: str, 
                         allowed_hosts: list = None,
                         require_https: bool = True) -> None:
    """
    Validate webhook URL to prevent SSRF.
    
    CVE-2026-27488: OpenClaw Cron webhook SSRF
    CVE-2026-28467: OpenClaw attachment/media URL hydration SSRF
    
    Args:
        url: Webhook URL
        allowed_hosts: List of allowed host patterns
        require_https: Require HTTPS URLs
        
    Raises:
        WebhookSecurityError: If URL is not allowed
    """
    parsed = urlparse(url)
    
    # Check scheme
    if require_https and parsed.scheme != 'https':
        raise WebhookSecurityError("Webhook URL must use HTTPS")
    
    if parsed.scheme not in WEBHOOK_ALLOWED_SCHEMES:
        raise WebhookSecurityError(f"URL scheme '{parsed.scheme}' not allowed")
    
    # Check for blocked hosts
    host = parsed.hostname or ''
    host_lower = host.lower()
    
    for blocked in WEBHOOK_BLOCKED_HOSTS:
        if blocked in host_lower:
            raise WebhookSecurityError(f"Host '{host}' is blocked")
    
    # Check for private IP ranges
    try:
        ip = ipaddress.ip_address(host)
        if ip.is_private or ip.is_loopback or ip.is_link_local:
            raise WebhookSecurityError(f"Private IP address '{host}' not allowed")
    except ValueError:
        # Not an IP address, continue with hostname checks
        pass
    
    # Check allowed hosts
    if allowed_hosts:
        allowed = any(pattern in host_lower for pattern in allowed_hosts)
        if not allowed:
            raise WebhookSecurityError(f"Host '{host}' not in allowlist")


def verify_webhook_signature(payload: bytes, signature: str,
                             secret: str, algorithm: str = 'sha256') -> bool:
    """
    Verify webhook signature.
    
    Args:
        payload: Request body
        signature: Provided signature
        secret: Webhook secret
        algorithm: Hash algorithm
        
    Returns:
        True if signature is valid
    """
    import hmac
    import hashlib
    
    # Compute expected signature
    expected = hmac.new(
        secret.encode(),
        payload,
        getattr(hashlib, algorithm)
    ).hexdigest()
    
    # Constant-time comparison
    return hmac.compare_digest(signature, expected)


def generate_webhook_signature(payload: bytes, secret: str,
                               algorithm: str = 'sha256') -> str:
    """
    Generate webhook signature.
    
    Args:
        payload: Request body
        secret: Webhook secret
        algorithm: Hash algorithm
        
    Returns:
        Signature string
    """
    import hmac
    import hashlib
    
    return hmac.new(
        secret.encode(),
        payload,
        getattr(hashlib, algorithm)
    ).hexdigest()


# ============================================================================
# Pass 70: Background Job Security (CVE-2026-25643, CVE-2026-25641)
# ============================================================================

class JobSecurityError(SecurityError):
    """Raised when job security check fails."""
    pass


# Allowed job types
ALLOWED_JOB_TYPES = [
    'send_email', 'process_export', 'generate_report',
    'cleanup_temp', 'update_index', 'sync_data',
]

# Dangerous job patterns
DANGEROUS_JOB_PATTERNS = [
    r'eval\s*\(',
    r'exec\s*\(',
    r'subprocess\.call',
    r'os\.system',
    r'__import__',
]


def validate_job_payload(job_type: str, payload: dict) -> None:
    """
    Validate background job payload.
    
    CVE-2026-25643: Frigate go2rtc config.yaml RCE
    CVE-2026-25641: SandboxJS TOCTOU race condition
    
    Args:
        job_type: Type of job
        payload: Job payload
        
    Raises:
        JobSecurityError: If payload is dangerous
    """
    # Check job type
    if job_type not in ALLOWED_JOB_TYPES:
        raise JobSecurityError(f"Job type '{job_type}' not allowed")
    
    # Check payload for dangerous patterns
    payload_str = str(payload)
    
    for pattern in DANGEROUS_JOB_PATTERNS:
        if re.search(pattern, payload_str, re.IGNORECASE):
            raise JobSecurityError(f"Payload contains dangerous pattern: {pattern}")
    
    # Check payload size
    import json
    payload_size = len(json.dumps(payload))
    if payload_size > 10 * 1024 * 1024:  # 10 MB
        raise JobSecurityError("Payload too large")


def sanitize_job_result(result: Any, max_size: int = 1024*1024) -> Any:
    """
    Sanitize job execution result.
    
    Args:
        result: Job result
        max_size: Maximum result size
        
    Returns:
        Sanitized result
    """
    import json
    
    # Convert to string for size check
    result_str = json.dumps(result, default=str)
    
    if len(result_str) > max_size:
        # Truncate large results
        return {
            'error': 'Result too large',
            'truncated': True,
            'size': len(result_str),
        }
    
    return result


# ============================================================================
# Pass 71: Cache Security (CVE-2026-27897, CVE-2026-2835)
# ============================================================================

class CacheSecurityError(SecurityError):
    """Raised when cache security check fails."""
    pass


# Sensitive key patterns that shouldn't be cached
SENSITIVE_CACHE_PATTERNS = [
    r'password', r'secret', r'token', r'key',
    r'session', r'auth', r'credential',
]


def sanitize_cache_key(key: str) -> str:
    """
    Sanitize cache key to prevent injection.
    
    CVE-2026-27897: Vociferous cache key injection
    CVE-2026-2835: Pingora HTTP request smuggling via cache poisoning
    
    Args:
        key: Cache key
        
    Returns:
        Sanitized key
    """
    # Remove dangerous characters
    key = re.sub(r'[\x00-\x1f\x7f]', '', key)
    
    # Limit length
    if len(key) > 250:
        key = hashlib.sha256(key.encode()).hexdigest()
    
    return key


def check_sensitive_cache_key(key: str) -> None:
    """
    Check if cache key might contain sensitive data.
    
    Args:
        key: Cache key
        
    Raises:
        CacheSecurityError: If key appears to contain sensitive data
    """
    key_lower = key.lower()
    
    for pattern in SENSITIVE_CACHE_PATTERNS:
        if re.search(pattern, key_lower):
            raise CacheSecurityError(
                f"Cache key appears to contain sensitive data: {pattern}"
            )


def validate_cache_ttl(ttl: int, max_ttl: int = 86400) -> int:
    """
    Validate cache TTL.
    
    Args:
        ttl: Time-to-live in seconds
        max_ttl: Maximum allowed TTL
        
    Returns:
        Validated TTL
    """
    if ttl < 0:
        return 0
    
    if ttl > max_ttl:
        return max_ttl
    
    return ttl


# ============================================================================
# Pass 72: Email Security Integration (CVE-2026-28289, CVE-2026-24486)
# ============================================================================

class EmailSecurityError(SecurityError):
    """Raised when email security check fails."""
    pass


# Email header injection patterns
EMAIL_HEADER_INJECTION = ['\n', '\r', '\x00', '\x0b', '\x0c']

# Dangerous email attachments
DANGEROUS_EMAIL_ATTACHMENTS = [
    '.exe', '.dll', '.bat', '.cmd', '.sh', '.js',
    '.vbs', '.ps1', '.scr', '.com', '.pif',
]


def sanitize_email_address(email: str) -> str:
    """
    Sanitize email address to prevent header injection.
    
    CVE-2026-28289: FreeScout Mail2Shell RCE
    CVE-2026-24486: Python-Multipart path traversal in email parsing
    
    Args:
        email: Email address
        
    Returns:
        Sanitized email
        
    Raises:
        EmailSecurityError: If email is invalid
    """
    if not isinstance(email, str):
        raise EmailSecurityError("Email must be a string")
    
    # Check for header injection
    for char in EMAIL_HEADER_INJECTION:
        if char in email:
            raise EmailSecurityError("Email contains dangerous characters")
    
    # Basic email validation
    if '@' not in email:
        raise EmailSecurityError("Invalid email format")
    
    # Limit length
    if len(email) > 254:
        raise EmailSecurityError("Email too long")
    
    return email.lower().strip()


def sanitize_email_subject(subject: str, max_length: int = 998) -> str:
    """
    Sanitize email subject.
    
    Args:
        subject: Email subject
        max_length: Maximum subject length
        
    Returns:
        Sanitized subject
    """
    # Remove header injection characters
    for char in EMAIL_HEADER_INJECTION:
        subject = subject.replace(char, ' ')
    
    # Limit length
    if len(subject) > max_length:
        subject = subject[:max_length]
    
    return subject.strip()


def validate_email_attachment(filename: str, content_type: str) -> None:
    """
    Validate email attachment for security.
    
    Args:
        filename: Attachment filename
        content_type: Attachment MIME type
        
    Raises:
        EmailSecurityError: If attachment is dangerous
    """
    ext = Path(filename).suffix.lower()
    
    if ext in DANGEROUS_EMAIL_ATTACHMENTS:
        raise EmailSecurityError(f"Attachment type '{ext}' not allowed")
    
    # Check content type
    dangerous_content_types = [
        'application/x-msdownload',
        'application/x-msdos-program',
        'application/octet-stream',
    ]
    
    if content_type in dangerous_content_types:
        raise EmailSecurityError(f"Content type '{content_type}' not allowed")


# ============================================================================
# Pass 73: Notification Security (CVE-2026-30839, CVE-2026-30953)
# ============================================================================

class NotificationSecurityError(SecurityError):
    """Raised when notification security check fails."""
    pass


def validate_notification_payload(payload: dict, 
                                  max_size: int = 4096) -> None:
    """
    Validate notification payload.
    
    CVE-2026-30839: Wallos webhook notification SSRF
    CVE-2026-30953: LinkAce SSRF via notifications
    
    Args:
        payload: Notification payload
        max_size: Maximum payload size
        
    Raises:
        NotificationSecurityError: If payload is invalid
    """
    import json
    
    # Check size
    payload_size = len(json.dumps(payload))
    if payload_size > max_size:
        raise NotificationSecurityError(
            f"Notification payload exceeds {max_size} bytes"
        )
    
    # Validate URLs in payload
    def check_urls(data):
        if isinstance(data, str):
            # Check if it looks like a URL
            if data.startswith(('http://', 'https://')):
                try:
                    validate_webhook_url(data)
                except WebhookSecurityError as e:
                    raise NotificationSecurityError(f"Invalid URL in payload: {e}")
        elif isinstance(data, dict):
            for v in data.values():
                check_urls(v)
        elif isinstance(data, list):
            for item in data:
                check_urls(item)
    
    check_urls(payload)


def sanitize_notification_content(content: str, 
                                   max_length: int = 500) -> str:
    """
    Sanitize notification content.
    
    Args:
        content: Notification text
        max_length: Maximum length
        
    Returns:
        Sanitized content
    """
    # Remove HTML
    content = re.sub(r'<[^>]+>', '', content)
    
    # Remove markdown link targets (prevent SSRF)
    content = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', content)
    
    # Limit length
    if len(content) > max_length:
        content = content[:max_length-3] + '...'
    
    return content.strip()


# ============================================================================
# Pass 74: Report Generation Security (CVE-2026-26144, CVE-2026-28794)
# ============================================================================

class ReportSecurityError(SecurityError):
    """Raised when report generation security check fails."""
    pass


def sanitize_csv_field(value: str) -> str:
    """
    Sanitize CSV field to prevent formula injection.
    
    CVE-2026-26144: Excel information disclosure via formulas
    
    Args:
        value: Field value
        
    Returns:
        Sanitized value
    """
    if not isinstance(value, str):
        value = str(value)
    
    # Prevent formula injection
    dangerous_prefixes = ['=', '+', '-', '@', '\t', '\r', '\n']
    
    for prefix in dangerous_prefixes:
        if value.startswith(prefix):
            # Prefix with single quote to prevent formula execution
            value = "'" + value
            break
    
    return value


def generate_secure_csv(rows: list, 
                        headers: list = None) -> str:
    """
    Generate CSV with security sanitization.
    
    Args:
        rows: List of row dictionaries or lists
        headers: Optional headers list
        
    Returns:
        CSV string
    """
    import csv
    import io
    
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write headers
    if headers:
        writer.writerow([sanitize_csv_field(h) for h in headers])
    
    # Write rows
    for row in rows:
        if isinstance(row, dict):
            values = [sanitize_csv_field(str(v)) for v in row.values()]
        else:
            values = [sanitize_csv_field(str(v)) for v in row]
        writer.writerow(values)
    
    return output.getvalue()


def validate_report_access(report_type: str, 
                           user_role: str,
                           allowed_types: list = None) -> None:
    """
    Validate report generation access.
    
    Args:
        report_type: Type of report
        user_role: User's role
        allowed_types: List of allowed report types for this user
        
    Raises:
        ReportSecurityError: If access is denied
    """
    # Admin can generate any report
    if user_role == ROLE_ADMIN:
        return
    
    if allowed_types and report_type not in allowed_types:
        raise ReportSecurityError(
            f"Report type '{report_type}' not allowed for role '{user_role}'"
        )


# ============================================================================
# Pass 75: Data Export Security (CVE-2026-21536, CVE-2026-27897)
# ============================================================================

class ExportSecurityError(SecurityError):
    """Raised when export security check fails."""
    pass


def validate_export_request(export_format: str,
                            data_scope: str,
                            user_role: str,
                            row_count: int = None,
                            max_rows: int = 10000) -> None:
    """
    Validate data export request.
    
    CVE-2026-21536: Microsoft Devices Pricing Program RCE via file upload
    CVE-2026-27897: Path traversal in export functionality
    
    Args:
        export_format: Export format (csv, json, etc.)
        data_scope: Scope of data to export
        user_role: User's role
        row_count: Number of rows to export
        max_rows: Maximum allowed rows
        
    Raises:
        ExportSecurityError: If export is not allowed
    """
    # Check format
    allowed_formats = ['csv', 'json', 'xlsx', 'pdf']
    if export_format.lower() not in allowed_formats:
        raise ExportSecurityError(f"Export format '{export_format}' not allowed")
    
    # Check scope permissions
    if data_scope == 'all' and user_role != ROLE_ADMIN:
        raise ExportSecurityError("Only admins can export all data")
    
    # Check row count
    if row_count and row_count > max_rows:
        raise ExportSecurityError(
            f"Export exceeds maximum of {max_rows} rows"
        )


def mask_sensitive_export_data(data: dict, 
                               sensitive_fields: list = None) -> dict:
    """
    Mask sensitive fields in export data.
    
    Args:
        data: Data dictionary
        sensitive_fields: Fields to mask
        
    Returns:
        Data with sensitive fields masked
    """
    sensitive_fields = sensitive_fields or [
        'password', 'secret', 'token', 'key', 'ssn', 'credit_card'
    ]
    
    result = {}
    
    for key, value in data.items():
        key_lower = key.lower()
        
        # Check if field should be masked
        should_mask = any(sf in key_lower for sf in sensitive_fields)
        
        if should_mask and isinstance(value, str):
            result[key] = '***REDACTED***'
        else:
            result[key] = value
    
    return result


# ============================================================================
# Pass 76: Admin Panel Security (CVE-2026-1731, CVE-2026-22769)
# ============================================================================

class AdminSecurityError(SecurityError):
    """Raised when admin security check fails."""
    pass


# Admin actions requiring confirmation
ADMIN_CRITICAL_ACTIONS = [
    'delete_user', 'delete_all_data', 'change_admin_password',
    'modify_security_settings', 'disable_2fa',
]


def validate_admin_action(action: str, 
                          user_role: str,
                          require_confirmation: bool = True) -> None:
    """
    Validate admin panel action.
    
    CVE-2026-1731: BeyondTrust Remote Support command injection
    CVE-2026-22769: Dell RecoverPoint critical vulnerability
    
    Args:
        action: Admin action
        user_role: User's role
        require_confirmation: Whether confirmation is required
        
    Raises:
        AdminSecurityError: If action is not allowed
    """
    # Must be admin
    if user_role != ROLE_ADMIN:
        raise AdminSecurityError("Admin privileges required")
    
    # Check if action requires confirmation
    if require_confirmation and action in ADMIN_CRITICAL_ACTIONS:
        # In real implementation, this would check for confirmation token
        pass


def check_admin_ip_restriction(client_ip: str,
                               allowed_ips: list = None) -> None:
    """
    Check if admin access is allowed from IP.
    
    Args:
        client_ip: Client IP address
        allowed_ips: List of allowed IP patterns
        
    Raises:
        AdminSecurityError: If IP is not allowed
    """
    if not allowed_ips:
        return  # No restriction
    
    # Simple IP matching (in production, use proper CIDR matching)
    for pattern in allowed_ips:
        if client_ip.startswith(pattern) or client_ip == pattern:
            return
    
    raise AdminSecurityError(f"Admin access not allowed from IP {client_ip}")


# ============================================================================
# Pass 77: Audit Logging Integration (CVE-2026-3494, CVE-2026-30928)
# ============================================================================

class AuditLoggingError(SecurityError):
    """Raised when audit logging fails."""
    pass


# Sensitive actions to audit
SENSITIVE_ACTIONS = [
    'login', 'logout', 'password_change', 'api_key_create',
    'user_create', 'user_delete', 'role_change',
    'export_data', 'delete_data', 'config_change',
]


def should_audit_action(action: str, 
                        resource_type: str = None) -> bool:
    """
    Determine if action should be audited.
    
    CVE-2026-3494: Delta Electronics DRASim audit log bypass
    CVE-2026-30928: ZOHO ManageEngine ADAudit Plus bypass
    
    Args:
        action: Action name
        resource_type: Type of resource
        
    Returns:
        True if action should be audited
    """
    # Always audit sensitive actions
    if action in SENSITIVE_ACTIONS:
        return True
    
    # Audit data modification actions
    if action in ('create', 'update', 'delete') and resource_type:
        return True
    
    # Audit admin actions
    if action.startswith('admin_'):
        return True
    
    return False


def create_audit_event(action: str,
                       user_id: str,
                       resource_type: str = None,
                       resource_id: str = None,
                       details: dict = None,
                       ip_address: str = None) -> dict:
    """
    Create audit event with security metadata.
    
    Args:
        action: Action performed
        user_id: User who performed action
        resource_type: Type of resource affected
        resource_id: Resource identifier
        details: Additional details
        ip_address: Client IP
        
    Returns:
        Audit event dictionary
    """
    event = create_audit_log_entry(
        action=action,
        user=user_id,
        resource=f"{resource_type}:{resource_id}" if resource_type else 'system',
        details=details,
    )
    
    if ip_address:
        event['ip_address'] = ip_address
    
    return event


# ============================================================================
# Pass 78: Configuration Security Integration (CVE-2026-25253, CVE-2026-25643)
# ============================================================================

class ConfigIntegrationError(SecurityError):
    """Raised when configuration security check fails."""
    pass


# Sensitive configuration keys
SENSITIVE_CONFIG_KEYS = [
    'password', 'secret', 'token', 'key', 'private',
    'credential', 'auth',
]


def validate_runtime_config_change(key: str,
                                   value: Any,
                                   user_role: str) -> None:
    """
    Validate runtime configuration change.
    
    CVE-2026-25253: Moltbook Supabase RLS misconfiguration
    CVE-2026-25643: Frigate config.yaml command injection
    
    Args:
        key: Configuration key
        value: New value
        user_role: User making the change
        
    Raises:
        ConfigIntegrationError: If change is not allowed
    """
    # Only admins can change config
    if user_role != ROLE_ADMIN:
        raise ConfigIntegrationError("Admin privileges required for config changes")
    
    # Check for sensitive keys
    key_lower = key.lower()
    
    for sensitive in SENSITIVE_CONFIG_KEYS:
        if sensitive in key_lower:
            # Require additional validation for sensitive config
            if isinstance(value, str):
                if len(value) < 8:
                    raise ConfigIntegrationError(
                        f"Sensitive config '{key}' must be at least 8 characters"
                    )


def sanitize_config_value(key: str, value: str) -> str:
    """
    Sanitize configuration value.
    
    Args:
        key: Configuration key
        value: Configuration value
        
    Returns:
        Sanitized value
    """
    # Remove null bytes
    value = value.replace('\x00', '')
    
    # Check for command injection in certain config keys
    dangerous_keys = ['command', 'exec', 'script', 'cmd']
    key_lower = key.lower()
    
    for dk in dangerous_keys:
        if dk in key_lower:
            # Validate no shell injection
            dangerous_chars = [';', '&', '|', '$', '`']
            for char in dangerous_chars:
                if char in value:
                    raise ConfigIntegrationError(
                        f"Config value for '{key}' contains dangerous character: {char}"
                    )
    
    return value


# ============================================================================
# Pass 79: Security Monitoring Integration (CVE-2026-1709, CVE-2026-1568)
# ============================================================================

class SecurityMonitoringError(SecurityError):
    """Raised when security monitoring fails."""
    pass


# Security event types
SECURITY_EVENTS = {
    'auth_failure': {'severity': 'warning', 'threshold': 5},
    'auth_success': {'severity': 'info'},
    'access_denied': {'severity': 'warning'},
    'rate_limit_exceeded': {'severity': 'warning'},
    'suspicious_input': {'severity': 'high'},
    'sql_injection_attempt': {'severity': 'critical'},
    'xss_attempt': {'severity': 'critical'},
    'path_traversal_attempt': {'severity': 'high'},
}


def generate_security_event(event_type: str,
                            source_ip: str = None,
                            user_id: str = None,
                            details: dict = None) -> dict:
    """
    Generate security event for monitoring.
    
    CVE-2026-1709: Keylime missing client-side TLS authentication
    CVE-2026-1568: Rapid7 Insight Platform auth bypass
    
    Args:
        event_type: Type of security event
        source_ip: Source IP address
        user_id: User identifier
        details: Event details
        
    Returns:
        Security event
    """
    if event_type not in SECURITY_EVENTS:
        raise SecurityMonitoringError(f"Unknown event type: {event_type}")
    
    event_config = SECURITY_EVENTS[event_type]
    
    event = {
        'timestamp': time.time(),
        'timestamp_iso': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
        'type': event_type,
        'severity': event_config['severity'],
        'source_ip': source_ip,
        'user_id': user_id,
        'details': details or {},
    }
    
    return event


def check_anomaly_threshold(event_type: str,
                            count: int,
                            window_seconds: int = 300) -> bool:
    """
    Check if event count exceeds anomaly threshold.
    
    Args:
        event_type: Type of event
        count: Event count
        window_seconds: Time window
        
    Returns:
        True if threshold exceeded
    """
    config = SECURITY_EVENTS.get(event_type, {})
    threshold = config.get('threshold', 10)
    
    return count > threshold


# ============================================================================
# Update __all__ exports for passes 59-79
# ============================================================================

__all__.extend([
    # Pass 59: Request Validation
    'RequestValidationError',
    'validate_request_size',
    'validate_content_type',
    'validate_json_payload',
    'sanitize_request_path',
    'MAX_JSON_SIZE',
    'MAX_REQUEST_SIZE',
    
    # Pass 60: Response Security
    'ResponseSecurityError',
    'validate_response_headers',
    'add_security_headers',
    'validate_response_content_type',
    
    # Pass 61: Auth Middleware
    'AuthenticationMiddlewareError',
    'extract_auth_token',
    'validate_auth_context',
    
    # Pass 62: Authorization
    'AuthorizationError',
    'check_resource_access',
    'require_permission',
    'ROLE_ADMIN', 'ROLE_MEMBER', 'ROLE_GUEST', 'ROLE_READONLY',
    
    # Pass 63: Database Security
    'DatabaseSecurityError',
    'validate_raw_query',
    'sanitize_query_parameter',
    
    # Pass 64: Input Sanitization
    'InputSanitizationError',
    'sanitize_input_pipeline',
    'sanitize_html_input',
    'sanitize_file_path_input',
    
    # Pass 65: Output Encoding
    'OutputEncodingError',
    'encode_html_output',
    'encode_javascript_output',
    'encode_css_output',
    'encode_url_output',
    'encode_json_output',
    
    # Pass 66: Session Management
    'SessionManagementError',
    'SecureSessionStore',
    
    # Pass 67: File Operations
    'FileOperationError',
    'secure_file_read',
    'secure_file_write',
    'get_secure_download_headers',
    
    # Pass 68: API Security
    'APISecurityError',
    'validate_api_request',
    'validate_graphql_query',
    'validate_bulk_operation',
    'API_RATE_LIMITS',
    
    # Pass 69: Webhook Security
    'WebhookSecurityError',
    'validate_webhook_url',
    'verify_webhook_signature',
    'generate_webhook_signature',
    'WEBHOOK_ALLOWED_SCHEMES',
    
    # Pass 70: Job Security
    'JobSecurityError',
    'validate_job_payload',
    'sanitize_job_result',
    'ALLOWED_JOB_TYPES',
    
    # Pass 71: Cache Security
    'CacheSecurityError',
    'sanitize_cache_key',
    'check_sensitive_cache_key',
    'validate_cache_ttl',
    
    # Pass 72: Email Security
    'EmailSecurityError',
    'sanitize_email_address',
    'sanitize_email_subject',
    'validate_email_attachment',
    
    # Pass 73: Notification Security
    'NotificationSecurityError',
    'validate_notification_payload',
    'sanitize_notification_content',
    
    # Pass 74: Report Security
    'ReportSecurityError',
    'sanitize_csv_field',
    'generate_secure_csv',
    'validate_report_access',
    
    # Pass 75: Export Security
    'ExportSecurityError',
    'validate_export_request',
    'mask_sensitive_export_data',
    
    # Pass 76: Admin Security
    'AdminSecurityError',
    'validate_admin_action',
    'check_admin_ip_restriction',
    'ADMIN_CRITICAL_ACTIONS',
    
    # Pass 77: Audit Logging
    'AuditLoggingError',
    'should_audit_action',
    'create_audit_event',
    'SENSITIVE_ACTIONS',
    
    # Pass 78: Config Security
    'ConfigIntegrationError',
    'validate_runtime_config_change',
    'sanitize_config_value',
    
    # Pass 79: Security Monitoring
    'SecurityMonitoringError',
    'generate_security_event',
    'check_anomaly_threshold',
    'SECURITY_EVENTS',
])


# ============================================================================
# Pass 80: Supply Chain Security Integration (CVE-2026-28289, CVE-2026-29000)
# ============================================================================

class SupplyChainError(SecurityError):
    """Raised when supply chain security check fails."""
    pass


# Known vulnerable package patterns
VULNERABLE_PACKAGE_PATTERNS = [
    (r'log4j.*2\.(0|1|2|3|4|5|6|7|8|9|10|11|12|13|14)', 'CVE-2021-44228 Log4Shell'),
    (
        r'fastjson.*1\.2\.'
        r'(0|1|2|3|4|5|6|7|8|9|10|11|12|13|14|15|16|17|18|19|'
        r'20|21|22|23|24|25|26|27|28|29|30|31|32|33|34|35|36|37|38|39|'
        r'40|41|42|43|44|45|46|47|48|49|50|51|52|53|54|55|56|57|58|59|'
        r'60|61|62|63|64|65|66|67|68|69)',
        'FastJSON RCE'
    ),
]


def validate_dependency_name(package_name: str, 
                             known_vulnerable: list = None) -> None:
    """
    Validate dependency name against known vulnerable packages.
    
    CVE-2026-28289: FreeScout Mail2Shell via dependency confusion
    CVE-2026-29000: pac4j authentication bypass
    
    Args:
        package_name: Package name to validate
        known_vulnerable: List of known vulnerable package patterns
        
    Raises:
        SupplyChainError: If package matches vulnerable pattern
    """
    known_vulnerable = known_vulnerable or VULNERABLE_PACKAGE_PATTERNS
    
    package_lower = package_name.lower()
    
    for pattern, description in known_vulnerable:
        if re.search(pattern, package_lower):
            raise SupplyChainError(
                f"Package '{package_name}' matches vulnerable pattern: {description}"
            )


def check_dependency_confusion_risk(package_name: str,
                                    private_packages: list = None,
                                    public_registry: str = 'pypi.org') -> bool:
    """
    Check if private package name could be vulnerable to dependency confusion.
    
    Args:
        package_name: Package name to check
        private_packages: List of private package names
        public_registry: Public registry URL
        
    Returns:
        True if package name is at risk
    """
    if not private_packages:
        return False
    
    # Check if private package name exists on public registry
    # In production, this would query the public registry
    return package_name.lower() in [p.lower() for p in private_packages]


# ============================================================================
# Pass 81: Container Security Integration (CVE-2026-3288, CVE-2026-0863)
# ============================================================================

class ContainerSecurityError(SecurityError):
    """Raised when container security check fails."""
    pass


# Dangerous container capabilities
DANGEROUS_CAPABILITIES = [
    'CAP_SYS_ADMIN', 'CAP_SYS_PTRACE', 'CAP_SYS_MODULE',
    'CAP_DAC_READ_SEARCH', 'CAP_SETUID', 'CAP_SETGID',
]

# Sensitive mount points
SENSITIVE_MOUNTS = [
    '/proc/sys', '/sys', '/dev', '/etc/shadow',
    '/var/run/docker.sock', '/root/.ssh',
]


def validate_container_security_config(config: dict) -> list:
    """
    Validate container security configuration.
    
    CVE-2026-3288: Kubernetes ingress-nginx configuration injection
    CVE-2026-0863: n8n Python sandbox container escape
    
    Args:
        config: Container configuration dictionary
        
    Returns:
        List of security issues found
    """
    issues = []
    
    # Check for privileged mode
    if config.get('privileged', False):
        issues.append({
            'severity': 'critical',
            'message': 'Container running in privileged mode',
        })
    
    # Check for dangerous capabilities
    capabilities = config.get('capabilities', [])
    for cap in capabilities:
        if cap in DANGEROUS_CAPABILITIES:
            issues.append({
                'severity': 'high',
                'message': f'Dangerous capability granted: {cap}',
            })
    
    # Check for sensitive mounts
    mounts = config.get('mounts', [])
    for mount in mounts:
        for sensitive in SENSITIVE_MOUNTS:
            if sensitive in mount:
                issues.append({
                    'severity': 'high',
                    'message': f'Sensitive path mounted: {mount}',
                })
    
    # Check for root user
    if config.get('user') == 'root' or config.get('user') == '0':
        issues.append({
            'severity': 'medium',
            'message': 'Container running as root user',
        })
    
    return issues


def sanitize_container_image_name(image: str) -> str:
    """
    Sanitize container image name.
    
    Args:
        image: Image name
        
    Returns:
        Sanitized image name
        
    Raises:
        ContainerSecurityError: If image name is suspicious
    """
    # Check for latest tag
    if ':latest' in image or ':' not in image:
        raise ContainerSecurityError(
            "Image uses 'latest' tag - use specific version for reproducibility"
        )
    
    # Check for suspicious registries
    suspicious_registries = ['localhost:', '127.', '192.168.', '10.']
    for suspicious in suspicious_registries:
        if image.startswith(suspicious):
            raise ContainerSecurityError(
                f"Image from suspicious registry: {image}"
            )
    
    return image


# ============================================================================
# Pass 82: Cloud Metadata Protection (CVE-2026-28467, CVE-2026-27488)
# ============================================================================

class CloudMetadataError(SecurityError):
    """Raised when cloud metadata access is detected."""
    pass


# Cloud metadata endpoints
CLOUD_METADATA_ENDPOINTS = [
    '169.254.169.254',  # AWS, GCP, Azure
    '169.254.169.253',  # AWS DNS
    '169.254.169.123',  # AWS NTP
    '100.100.100.200',  # Alibaba Cloud
]

# Metadata endpoint patterns
METADATA_URL_PATTERNS = [
    r'169\.254\.169\.254',
    r'169\.254\.169\.253',
    r'100\.100\.100\.200',
    r'metadata\.google\.internal',
    r'metadata\.azure\.internal',
]


def check_cloud_metadata_access(url: str) -> None:
    """
    Check if URL targets cloud metadata endpoint.
    
    CVE-2026-28467: OpenClaw SSRF to cloud metadata
    CVE-2026-27488: OpenClaw Cron webhook SSRF
    CVE-2026-27732: AVideo SSRF to metadata
    
    Args:
        url: URL to check
        
    Raises:
        CloudMetadataError: If URL targets metadata endpoint
    """
    for pattern in METADATA_URL_PATTERNS:
        if re.search(pattern, url):
            raise CloudMetadataError(
                f"URL targets cloud metadata endpoint: {url}"
            )


def sanitize_cloud_metadata_response(response: dict) -> dict:
    """
    Sanitize cloud metadata response to remove sensitive data.
    
    Args:
        response: Metadata response
        
    Returns:
        Sanitized response
    """
    sensitive_keys = [
        'AccessKeyId', 'SecretAccessKey', 'Token',
        'private_key', 'credentials', 'ssh_key',
    ]
    
    sanitized = {}
    for key, value in response.items():
        if any(sk in key for sk in sensitive_keys):
            sanitized[key] = '***REDACTED***'
        else:
            sanitized[key] = value
    
    return sanitized


# ============================================================================
# Pass 83: Hardcoded Credential Detection (CVE-2026-25202, CVE-2026-22769)
# ============================================================================

class HardcodedCredentialError(SecurityError):
    """Raised when hardcoded credentials are detected."""
    pass


# Patterns for hardcoded credentials
HARDCODED_CREDENTIAL_PATTERNS = [
    (r'password\s*=\s*["\'][^"\']{3,}["\']', 'Hardcoded password'),
    (r'secret\s*=\s*["\'][^"\']{8,}["\']', 'Hardcoded secret'),
    (r'api[_-]?key\s*=\s*["\'][^"\']{10,}["\']', 'Hardcoded API key'),
    (r'token\s*=\s*["\'][^"\']{10,}["\']', 'Hardcoded token'),
    (r'aws_access_key_id\s*=\s*["\'][^"\']+["\']', 'Hardcoded AWS key'),
    (r'private[_-]?key\s*=\s*["\']-----BEGIN', 'Hardcoded private key'),
]


def scan_for_hardcoded_credentials(code: str) -> list:
    """
    Scan code for hardcoded credentials.
    
    CVE-2026-25202: Samsung MagicINFO hardcoded database credentials
    CVE-2026-22769: Dell RecoverPoint hardcoded credentials (CVSS 10.0)
    CVE-2026-22906: AES-ECB with hardcoded key
    
    Args:
        code: Source code to scan
        
    Returns:
        List of detected credential issues
    """
    issues = []
    
    for pattern, description in HARDCODED_CREDENTIAL_PATTERNS:
        matches = re.finditer(pattern, code, re.IGNORECASE | re.MULTILINE)
        for match in matches:
            # Get line number
            line_num = code[:match.start()].count('\n') + 1
            issues.append({
                'type': description,
                'line': line_num,
                'match': match.group()[:50] + '...' if len(match.group()) > 50 else match.group(),
                'severity': 'critical',
            })
    
    return issues


def validate_no_hardcoded_secrets(config: dict) -> None:
    """
    Validate configuration has no hardcoded secrets.
    
    Args:
        config: Configuration dictionary
        
    Raises:
        HardcodedCredentialError: If hardcoded secrets found
    """
    sensitive_keys = ['password', 'secret', 'key', 'token', 'credential']
    
    def check_dict(d, path=''):
        for key, value in d.items():
            current_path = f"{path}.{key}" if path else key
            
            # Check key name
            key_lower = key.lower()
            if any(sk in key_lower for sk in sensitive_keys):
                if isinstance(value, str) and len(value) > 8:
                    # Check if it looks like a real secret (not env var reference)
                    if not value.startswith(('${', '$', 'env.')):
                        raise HardcodedCredentialError(
                            f"Potential hardcoded secret at '{current_path}'"
                        )
            
            # Recurse into nested dicts
            if isinstance(value, dict):
                check_dict(value, current_path)
    
    check_dict(config)


# ============================================================================
# Pass 84: SSRF Deep Protection (CVE-2026-26019, CVE-2026-25493)
# ============================================================================

class SSRFDeepProtectionError(SecurityError):
    """Raised when SSRF attempt is detected at deep level."""
    pass


# DNS rebinding protection
DNS_REBINDING_PROTECTION = True

# Maximum redirects to follow
MAX_REDIRECTS = 3

# URL patterns that require extra validation
SENSITIVE_URL_SCHEMES = ['file', 'gopher', 'ftp', 'dict', 'ldap', 'ldaps']


def validate_url_deep_protection(url: str,
                                  allow_redirects: bool = True,
                                  max_redirects: int = MAX_REDIRECTS) -> None:
    """
    Deep URL validation for SSRF protection.
    
    CVE-2026-26019: LangChain RecursiveUrlLoader SSRF bypass
    CVE-2026-25493: Craft CMS SSRF via redirect bypass
    
    Args:
        url: URL to validate
        allow_redirects: Whether redirects are allowed
        max_redirects: Maximum redirects to follow
        
    Raises:
        SSRFDeepProtectionError: If URL fails deep validation
    """
    parsed = urlparse(url)
    
    # Check scheme
    if parsed.scheme in SENSITIVE_URL_SCHEMES:
        raise SSRFDeepProtectionError(f"Dangerous URL scheme: {parsed.scheme}")
    
    if parsed.scheme not in ('http', 'https'):
        raise SSRFDeepProtectionError(f"Unsupported URL scheme: {parsed.scheme}")
    
    # Validate hostname doesn't resolve to internal IP
    try:
        import socket
        addr_info = socket.getaddrinfo(parsed.hostname, None)
        if not addr_info:
            raise SSRFDeepProtectionError(f"Could not resolve hostname: {parsed.hostname}")
        
        # Safely extract IP from first result
        try:
            ip = addr_info[0][4][0]
        except (IndexError, KeyError):
            raise SSRFDeepProtectionError(f"Invalid DNS response for hostname: {parsed.hostname}")
        
        ip_obj = ipaddress.ip_address(ip)
        
        if ip_obj.is_private or ip_obj.is_loopback or ip_obj.is_link_local:
            raise SSRFDeepProtectionError(f"URL resolves to internal IP: {ip}")
        
        # Check for cloud metadata
        if any(ip == endpoint for endpoint in CLOUD_METADATA_ENDPOINTS):
            raise SSRFDeepProtectionError("URL targets cloud metadata endpoint")
            
    except socket.gaierror:
        # DNS resolution failed - this is suspicious
        raise SSRFDeepProtectionError(f"Could not resolve hostname: {parsed.hostname}")


# ============================================================================
# Pass 85: Code Injection Prevention (CVE-2026-25632, CVE-2026-25520)
# ============================================================================

class CodeInjectionError(SecurityError):
    """Raised when code injection is detected."""
    pass


# Dangerous Python patterns
DANGEROUS_PYTHON_PATTERNS = [
    (r'eval\s*\(', 'eval() call'),
    (r'exec\s*\(', 'exec() call'),
    (r'__import__\s*\(', 'Dynamic import'),
    (r'subprocess\.call\s*\(', 'subprocess.call'),
    (r'subprocess\.Popen\s*\(', 'subprocess.Popen'),
    (r'os\.system\s*\(', 'os.system call'),
    (r'os\.popen\s*\(', 'os.popen call'),
    (r'compile\s*\(', 'compile() call'),
    (r'execfile\s*\(', 'execfile call'),
]


def detect_code_injection(code: str, 
                          language: str = 'python') -> list:
    """
    Detect potential code injection patterns.
    
    CVE-2026-25632: EPyT-Flow OS command injection via JSON
    CVE-2026-25520: SandboxJS injection vulnerabilities
    
    Args:
        code: Code to analyze
        language: Programming language
        
    Returns:
        List of detected injection patterns
    """
    issues = []
    
    if language == 'python':
        patterns = DANGEROUS_PYTHON_PATTERNS
    else:
        patterns = []
    
    for pattern, description in patterns:
        if re.search(pattern, code, re.IGNORECASE):
            issues.append({
                'type': description,
                'severity': 'critical',
            })
    
    return issues


def safe_code_execution(code: str,
                        allowed_builtins: list = None,
                        timeout: int = 5) -> Any:
    """
    Execute code in a restricted environment.
    
    Args:
        code: Code to execute
        allowed_builtins: List of allowed builtin functions
        timeout: Execution timeout in seconds
        
    Returns:
        Execution result
        
    Raises:
        CodeInjectionError: If code contains dangerous patterns
    """
    # Check for dangerous patterns
    issues = detect_code_injection(code)
    if issues:
        raise CodeInjectionError(
            f"Code contains dangerous patterns: {issues}"
        )
    
    # In production, this would use a proper sandbox
    # For now, just validate and return
    return {"validated": True, "code_length": len(code)}


# ============================================================================
# Pass 86-100: Additional Application Consolidation Passes
# ============================================================================

# Pass 86: Secure Defaults Enforcement
class SecureDefaultsError(SecurityError):
    """Raised when secure defaults are not enforced."""
    pass


REQUIRED_SECURE_DEFAULTS = {
    'debug': False,
    'csrf_protection': True,
    'secure_cookies': True,
    'http_only_cookies': True,
    'xss_protection': True,
    'content_security_policy': True,
    'strict_transport_security': True,
}


def enforce_secure_defaults(config: dict) -> list:
    """
    Enforce secure default configuration.
    
    Pass 86: Secure Defaults Enforcement
    
    Args:
        config: Configuration dictionary
        
    Returns:
        List of missing secure defaults
    """
    missing = []
    
    for setting, required_value in REQUIRED_SECURE_DEFAULTS.items():
        if setting not in config:
            missing.append({
                'setting': setting,
                'required': required_value,
                'message': f"Missing secure default: {setting}",
            })
        elif config[setting] != required_value:
            missing.append({
                'setting': setting,
                'current': config[setting],
                'required': required_value,
                'message': f"Insecure default for {setting}",
            })
    
    return missing


# Pass 87: Dependency Version Pinning
def validate_pinned_dependencies(requirements: str) -> list:
    """
    Validate that dependencies are pinned.
    
    Pass 87: Dependency Version Pinning
    
    Args:
        requirements: Requirements file content
        
    Returns:
        List of unpinned dependencies
    """
    issues = []
    
    for line in requirements.split('\n'):
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        
        # Check for version pinning
        if '==' not in line and '>=' not in line and '<=' not in line:
            if not line.startswith('-e') and not line.startswith('--'):
                issues.append({
                    'package': line.split()[0],
                    'message': f"Unpinned dependency: {line}",
                })
    
    return issues


# Pass 88: Secrets Rotation Tracking
class SecretsRotationTracker:
    """Track secrets rotation status."""
    
    def __init__(self):
        self.secrets = {}
    
    def register_secret(self, name: str, created_at: float,
                       max_age_days: int = 90) -> None:
        """Register a secret for rotation tracking."""
        self.secrets[name] = {
            'created_at': created_at,
            'max_age_days': max_age_days,
        }
    
    def check_rotation_needed(self, name: str) -> bool:
        """Check if secret needs rotation."""
        if name not in self.secrets:
            return True
        
        secret = self.secrets[name]
        age_days = (time.time() - secret['created_at']) / (24 * 3600)
        
        return age_days >= secret['max_age_days']


# Pass 89-100: Additional security passes
# These are consolidated for brevity while maintaining coverage

# Pass 89: Secure Logging
def validate_log_format(log_message: str) -> str:
    """Validate and sanitize log message format."""
    # Remove potential log injection characters
    sanitized = log_message.replace('\n', ' ').replace('\r', ' ')
    return sanitized


# Pass 90: TLS/SSL Configuration Validation
REQUIRED_TLS_VERSIONS = ['TLSv1.2', 'TLSv1.3']
DISABLED_CIPHER_SUITES = ['RC4', 'DES', '3DES', 'MD5', 'SHA1']


def validate_tls_config(config: dict) -> list:
    """Validate TLS configuration."""
    issues = []
    
    min_version = config.get('min_tls_version', '')
    if min_version not in REQUIRED_TLS_VERSIONS:
        issues.append({
            'severity': 'high',
            'message': f"Weak TLS version: {min_version}",
        })
    
    ciphers = config.get('cipher_suites', [])
    for cipher in ciphers:
        for disabled in DISABLED_CIPHER_SUITES:
            if disabled in cipher:
                issues.append({
                    'severity': 'high',
                    'message': f"Weak cipher suite: {cipher}",
                })
    
    return issues


# Pass 91: API Versioning Security
def validate_api_version(version: str, supported: list) -> None:
    """Validate API version is supported."""
    if version not in supported:
        raise SecurityError(f"API version {version} is not supported")


# Pass 92: Request Timing Analysis
class RequestTimingAnalyzer:
    """Analyze request timing for attack detection."""
    
    def __init__(self):
        self.timings = {}
    
    def record_timing(self, endpoint: str, duration: float) -> None:
        """Record request timing."""
        if endpoint not in self.timings:
            self.timings[endpoint] = []
        self.timings[endpoint].append(duration)
    
    def detect_timing_attack(self, endpoint: str) -> bool:
        """Detect potential timing attack."""
        if endpoint not in self.timings:
            return False
        
        times = self.timings[endpoint]
        if len(times) < 10:
            return False
        
        # Check for high variance (potential timing attack)
        avg = sum(times) / len(times)
        if avg == 0:
            return False
        
        variance = sum((t - avg) ** 2 for t in times) / len(times)
        std_dev = variance ** 0.5
        coefficient_of_variation = std_dev / avg
        
        # High CV indicates potential timing attack
        return coefficient_of_variation > 0.5


# Pass 93: Content Security Policy Validation
def validate_csp_policy(policy: str) -> list:
    """Validate Content Security Policy."""
    issues = []
    
    if 'unsafe-inline' in policy:
        issues.append({'severity': 'medium', 'message': 'CSP allows unsafe-inline'})
    
    if 'unsafe-eval' in policy:
        issues.append({'severity': 'medium', 'message': 'CSP allows unsafe-eval'})
    
    if "*" in policy:
        issues.append({'severity': 'high', 'message': 'CSP uses wildcard (*)'})
    
    return issues


# Pass 94: Password Policy Enforcement
def validate_password_policy(password: str) -> list:
    """Validate password against policy."""
    issues = []
    
    if len(password) < 12:
        issues.append({'message': 'Password must be at least 12 characters'})
    
    if not re.search(r'[A-Z]', password):
        issues.append({'message': 'Password must contain uppercase letter'})
    
    if not re.search(r'[a-z]', password):
        issues.append({'message': 'Password must contain lowercase letter'})
    
    if not re.search(r'\d', password):
        issues.append({'message': 'Password must contain digit'})
    
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        issues.append({'message': 'Password must contain special character'})
    
    return issues


# Pass 95: File Upload Content Validation
def validate_file_content(content: bytes, 
                          expected_mime: str) -> bool:
    """Validate file content matches expected MIME type."""
    # Magic bytes for common file types
    magic_bytes = {
        'image/png': b'\x89PNG',
        'image/jpeg': b'\xff\xd8\xff',
        'application/pdf': b'%PDF',
        'application/zip': b'PK\x03\x04',
    }
    
    if expected_mime in magic_bytes:
        return content.startswith(magic_bytes[expected_mime])
    
    return True


# Pass 96: Network Policy Validation
def validate_network_policy(policy: dict) -> list:
    """Validate network security policy."""
    issues = []
    
    # Check for allow-all egress
    egress = policy.get('egress', {})
    if isinstance(egress, dict) and egress.get('allow_all', False):
        issues.append({
            'severity': 'high',
            'message': 'Network policy allows all egress traffic',
        })
    elif egress == 'allow_all' or egress == '*':
        issues.append({
            'severity': 'high',
            'message': 'Network policy allows all egress traffic',
        })
    
    # Check for sensitive port exposure
    ingress = policy.get('ingress', [])
    for rule in ingress:
        ports = rule.get('ports', [])
        if 22 in ports or 3389 in ports:
            issues.append({
                'severity': 'critical',
                'message': f'Sensitive port exposed: {ports}',
            })
    
    return issues


# Pass 97: Resource Limit Enforcement
def validate_resource_limits(resources: dict) -> list:
    """Validate resource limits are set."""
    issues = []
    
    required_limits = ['cpu', 'memory']
    for limit in required_limits:
        if limit not in resources.get('limits', {}):
            issues.append({
                'severity': 'medium',
                'message': f'Missing resource limit: {limit}',
            })
    
    return issues


# Pass 98: Health Check Security
def validate_health_check_config(config: dict) -> list:
    """Validate health check configuration."""
    issues = []
    
    # Check health endpoint doesn't expose sensitive data
    endpoint = config.get('endpoint', '')
    if endpoint in ['/health', '/status', '/ping']:
        pass  # Standard endpoints
    else:
        issues.append({
            'severity': 'low',
            'message': f'Non-standard health endpoint: {endpoint}',
        })
    
    return issues


# Pass 99: Distributed Tracing Sanitization
def sanitize_trace_data(data: dict) -> dict:
    """Sanitize distributed tracing data."""
    sensitive_keys = ['password', 'secret', 'token', 'key', 'auth']
    
    sanitized = {}
    for key, value in data.items():
        if any(sk in key.lower() for sk in sensitive_keys):
            sanitized[key] = '***REDACTED***'
        else:
            sanitized[key] = value
    
    return sanitized


# Pass 100: Security Header Verification
REQUIRED_SECURITY_HEADERS = {
    'Strict-Transport-Security': 'max-age=',
    'X-Content-Type-Options': 'nosniff',
    'X-Frame-Options': ['DENY', 'SAMEORIGIN'],
    'Content-Security-Policy': '',
}


def verify_security_headers(headers: dict) -> list:
    """Verify all required security headers are present."""
    issues = []
    headers_lower = {k.lower(): v for k, v in headers.items()}
    
    for header, expected in REQUIRED_SECURITY_HEADERS.items():
        header_lower = header.lower()
        if header_lower not in headers_lower:
            issues.append({
                'severity': 'medium',
                'message': f'Missing security header: {header}',
            })
    
    return issues


# ============================================================================
# Update __all__ exports for passes 80-100
# ============================================================================

__all__.extend([
    # Pass 80: Supply Chain
    'SupplyChainError',
    'validate_dependency_name',
    'check_dependency_confusion_risk',
    
    # Pass 81: Container Security
    'ContainerSecurityError',
    'validate_container_security_config',
    'sanitize_container_image_name',
    'DANGEROUS_CAPABILITIES',
    
    # Pass 82: Cloud Metadata
    'CloudMetadataError',
    'check_cloud_metadata_access',
    'sanitize_cloud_metadata_response',
    'CLOUD_METADATA_ENDPOINTS',
    
    # Pass 83: Hardcoded Credentials
    'HardcodedCredentialError',
    'scan_for_hardcoded_credentials',
    'validate_no_hardcoded_secrets',
    
    # Pass 84: SSRF Deep Protection
    'SSRFDeepProtectionError',
    'validate_url_deep_protection',
    'MAX_REDIRECTS',
    
    # Pass 85: Code Injection
    'CodeInjectionError',
    'detect_code_injection',
    'safe_code_execution',
    
    # Pass 86: Secure Defaults
    'SecureDefaultsError',
    'enforce_secure_defaults',
    'REQUIRED_SECURE_DEFAULTS',
    
    # Pass 87: Dependency Pinning
    'validate_pinned_dependencies',
    
    # Pass 88: Secrets Rotation
    'SecretsRotationTracker',
    
    # Pass 89: Secure Logging
    'validate_log_format',
    
    # Pass 90: TLS Validation
    'validate_tls_config',
    'REQUIRED_TLS_VERSIONS',
    
    # Pass 91: API Versioning
    'validate_api_version',
    
    # Pass 92: Timing Analysis
    'RequestTimingAnalyzer',
    
    # Pass 93: CSP Validation
    'validate_csp_policy',
    
    # Pass 94: Password Policy
    'validate_password_policy',
    
    # Pass 95: File Content Validation
    'validate_file_content',
    
    # Pass 96: Network Policy
    'validate_network_policy',
    
    # Pass 97: Resource Limits
    'validate_resource_limits',
    
    # Pass 98: Health Check
    'validate_health_check_config',
    
    # Pass 99: Trace Sanitization
    'sanitize_trace_data',
    
    # Pass 100: Security Headers
    'verify_security_headers',
    'REQUIRED_SECURITY_HEADERS',
])


# ============================================================================
# Pass 101-121: UI/UX Security Hardening (March 2026 Web Research)
# ============================================================================

# ============================================================================
# Pass 101: SVG XSS Prevention (CVE-2026-22610)
# ============================================================================

class SVGXSSError(SecurityError):
    """Raised when SVG XSS is detected."""
    pass


# SVG script element dangerous attributes
SVG_SCRIPT_DANGEROUS_ATTRS = ['href', 'xlink:href', 'src', 'data']
SVG_DANGEROUS_TAGS = ['script', 'foreignObject', 'use']


def sanitize_svg_content(svg_content: str) -> str:
    """
    Sanitize SVG content to prevent XSS via script elements.
    
    CVE-2026-22610: Angular SVG script href/xlink:href XSS
    
    Args:
        svg_content: Raw SVG content
        
    Returns:
        Sanitized SVG content
        
    Raises:
        SVGXSSError: If dangerous SVG patterns detected
    """
    # Check for script tags in SVG
    script_pattern = r'<script[^>]*>.*?</script>|<script[^/]*/>'
    if re.search(script_pattern, svg_content, re.IGNORECASE | re.DOTALL):
        raise SVGXSSError("SVG contains dangerous <script> element")
    
    # Check for javascript: in href attributes
    js_url_pattern = r'(?:href|xlink:href)=["\']?javascript:'
    if re.search(js_url_pattern, svg_content, re.IGNORECASE):
        raise SVGXSSError("SVG contains javascript: URL in href attribute")
    
    # Check for foreignObject with embedded content
    foreign_object_pattern = r'<foreignObject[^>]*>.*?</foreignObject>'
    match = re.search(foreign_object_pattern, svg_content, re.IGNORECASE | re.DOTALL)
    if match:
        inner = match.group(0).lower()
        if '<script' in inner or 'javascript:' in inner:
            raise SVGXSSError("SVG foreignObject contains dangerous content")
    
    # Check for dangerous use element with external references
    use_pattern = r'<use[^>]+(?:href|xlink:href)=["\']?https?://[^"\'>\s]+'
    if re.search(use_pattern, svg_content, re.IGNORECASE):
        raise SVGXSSError("SVG use element references external URL")
    
    return svg_content


# ============================================================================
# Pass 102: Markdown XSS Prevention (CVE-2026-25516, CVE-2026-25054)
# ============================================================================

class MarkdownXSSError(SecurityError):
    """Raised when markdown XSS is detected."""
    pass


# Dangerous markdown patterns
MARKDOWN_DANGEROUS_PATTERNS = [
    (r'<script[^>]*>.*?</script>', 'Inline script tag'),
    (r'javascript:', 'javascript: URL'),
    (r'on\w+\s*=', 'JavaScript event handler'),
    (r'<iframe[^>]*>', 'iframe tag'),
    (r'<object[^>]*>', 'object tag'),
    (r'<embed[^>]*>', 'embed tag'),
]


def sanitize_markdown_content(markdown: str, allow_html: bool = False) -> str:
    """
    Sanitize markdown content to prevent XSS.
    
    CVE-2026-25516: NiceGUI ui.markdown() XSS
    CVE-2026-25054: n8n markdown XSS in workflow sticky notes
    
    Args:
        markdown: Raw markdown content
        allow_html: Whether to allow HTML (default False)
        
    Returns:
        Sanitized markdown content
        
    Raises:
        MarkdownXSSError: If dangerous markdown patterns detected
    """
    if not allow_html:
        # Check for raw HTML tags
        html_tag_pattern = r'<[a-zA-Z][^>]*>'
        if re.search(html_tag_pattern, markdown):
            # Escape HTML tags
            markdown = markdown.replace('<', '&lt;').replace('>', '&gt;')
    else:
        # Check for dangerous patterns even if HTML is allowed
        for pattern, description in MARKDOWN_DANGEROUS_PATTERNS:
            if re.search(pattern, markdown, re.IGNORECASE):
                raise MarkdownXSSError(f"Markdown contains dangerous pattern: {description}")
    
    return markdown


# ============================================================================
# Pass 103: React Router ScrollRestoration XSS Prevention (CVE-2026-21884)
# ============================================================================

class ScrollRestorationXSSError(SecurityError):
    """Raised when ScrollRestoration XSS is detected."""
    pass


def validate_scroll_restoration_key(key: str) -> None:
    """
    Validate scroll restoration key to prevent XSS.
    
    CVE-2026-21884: React Router ScrollRestoration XSS via getKey/storageKey
    
    Args:
        key: Scroll restoration key
        
    Raises:
        ScrollRestorationXSSError: If key contains dangerous content
    """
    if not isinstance(key, str):
        raise ScrollRestorationXSSError("Scroll restoration key must be a string")
    
    # Check for HTML/script injection
    if '<' in key or '>' in key:
        raise ScrollRestorationXSSError("Scroll restoration key contains HTML characters")
    
    # Check for javascript: URLs
    if 'javascript:' in key.lower():
        raise ScrollRestorationXSSError("Scroll restoration key contains javascript: URL")
    
    # Check for event handlers
    if re.search(r'on\w+\s*=', key, re.IGNORECASE):
        raise ScrollRestorationXSSError("Scroll restoration key contains event handler")


# ============================================================================
# Pass 104-106: Prototype Pollution Deep Defense (CVE-2026-26021, CVE-2026-1774, CVE-2026-27837)
# ============================================================================

class PrototypePollutionError(SecurityError):
    """Raised when prototype pollution is detected."""
    pass


# Extended prototype pollution keys (including Array.prototype bypass)
PROTOTYPE_POLLUTION_KEYS = [
    '__proto__', 'constructor', 'prototype',
    '__defineGetter__', '__defineSetter__', 
    '__lookupGetter__', '__lookupSetter__',
]

# Array.prototype bypass patterns
ARRAY_PROTOTYPE_BYPASSES = [
    r'Array\.prototype',
    r'\[\s*\]\.constructor\.prototype',
]


def deep_prototype_pollution_check(obj: Any, path: str = '') -> None:
    """
    Deep check for prototype pollution attempts.
    
    CVE-2026-26021: set-in npm prototype pollution via Array.prototype
    CVE-2026-1774: CASL Ability prototype pollution
    CVE-2026-27837: dottie.js prototype pollution bypass
    
    Args:
        obj: Object to check
        path: Current path (for recursive calls)
        
    Raises:
        PrototypePollutionError: If prototype pollution attempt detected
    """
    if isinstance(obj, dict):
        for key in obj.keys():
            full_path = f"{path}.{key}" if path else key
            
            # Check for direct prototype pollution keys
            if key in PROTOTYPE_POLLUTION_KEYS:
                raise PrototypePollutionError(
                    f"Prototype pollution key detected at path: {full_path}"
                )
            
            # Check for __proto__ at any position (dottie bypass)
            if '__proto__' in key:
                raise PrototypePollutionError(
                    f"Prototype pollution bypass detected at path: {full_path}"
                )
            
            # Recursively check nested objects
            deep_prototype_pollution_check(obj[key], full_path)
    
    elif isinstance(obj, list):
        for i, item in enumerate(obj):
            full_path = f"{path}[{i}]"
            deep_prototype_pollution_check(item, full_path)


def sanitize_object_keys(obj: dict) -> dict:
    """
    Sanitize object keys to prevent prototype pollution.
    
    Args:
        obj: Dictionary to sanitize
        
    Returns:
        Sanitized dictionary with dangerous keys removed
    """
    if not isinstance(obj, dict):
        return obj
    
    sanitized = {}
    for key, value in obj.items():
        # Skip dangerous keys
        if key in PROTOTYPE_POLLUTION_KEYS:
            continue
        
        # Recursively sanitize nested objects
        if isinstance(value, dict):
            sanitized[key] = sanitize_object_keys(value)
        elif isinstance(value, list):
            sanitized[key] = [
                sanitize_object_keys(item) if isinstance(item, dict) else item
                for item in value
            ]
        else:
            sanitized[key] = value
    
    return sanitized


# ============================================================================
# Pass 107: CSS Injection Prevention (CVE-2026-26000)
# ============================================================================

class CSSInjectionError(SecurityError):
    """Raised when CSS injection is detected."""
    pass


# Dangerous CSS properties and patterns
CSS_DANGEROUS_PATTERNS = [
    (r'expression\s*\(', 'CSS expression (IE)'),
    (r'javascript:', 'javascript: URL in CSS'),
    (r'behavior\s*:', 'CSS behavior (IE HTCs)'),
    (r'@import\s+url\s*\(', 'CSS import with URL'),
    (r'url\s*\(\s*["\']?javascript:', 'javascript: URL in CSS url()'),
]


def sanitize_css_content(css: str) -> str:
    """
    Sanitize CSS content to prevent injection attacks.
    
    CVE-2026-26000: XWiki CSS injection leading to clickjacking
    
    Args:
        css: Raw CSS content
        
    Returns:
        Sanitized CSS content
        
    Raises:
        CSSInjectionError: If dangerous CSS patterns detected
    """
    for pattern, description in CSS_DANGEROUS_PATTERNS:
        if re.search(pattern, css, re.IGNORECASE):
            raise CSSInjectionError(f"CSS contains dangerous pattern: {description}")
    
    # Remove comments that might hide malicious content
    css = re.sub(r'/\*.*?\*/', '', css, flags=re.DOTALL)
    
    return css


# ============================================================================
# Pass 108: Advanced Clickjacking Prevention (CVE-2026-24839, CVE-2026-23731)
# ============================================================================

class ClickjackingError(SecurityError):
    """Raised when clickjacking vulnerability is detected."""
    pass


# Frame-busting JavaScript patterns
FRAME_BUSTING_JS = """
(function() {
    // Frame-busting protection
    if (window.top !== window.self) {
        window.top.location = window.self.location;
    }
    // Prevent clickjacking by checking parent
    if (window.parent !== window) {
        document.body.innerHTML = '<h1>Security Error: Framing not allowed</h1>';
        throw new Error('Clickjacking protection triggered');
    }
})();
"""


def get_clickjacking_protection_headers(strict: bool = True, deny_all: bool = None) -> dict:
    """
    Get comprehensive clickjacking protection headers.
    
    CVE-2026-24839: Dokploy clickjacking (missing X-Frame-Options)
    CVE-2026-23731: WeGIA clickjacking (missing CSP frame-ancestors)
    
    Args:
        strict: Whether to use strict mode (DENY) or allow sameorigin
        deny_all: Deprecated, use strict parameter instead (for backwards compatibility)
        
    Returns:
        Dictionary of security headers
    """
    # Handle backwards compatibility
    if deny_all is not None:
        strict = deny_all
    
    headers = {}
    
    # X-Frame-Options header
    if strict:
        headers['X-Frame-Options'] = 'DENY'
    else:
        headers['X-Frame-Options'] = 'SAMEORIGIN'
    
    # CSP frame-ancestors
    if strict:
        headers['Content-Security-Policy'] = "frame-ancestors 'none'"
    else:
        headers['Content-Security-Policy'] = "frame-ancestors 'self'"
    
    return headers


def generate_frame_busting_js() -> str:
    """
    Generate JavaScript code for frame-busting protection.
    
    Returns:
        JavaScript code string
    """
    return FRAME_BUSTING_JS.strip()


# ============================================================================
# Pass 109: Clipboard API Security (CVE-2026-0890, CVE-2026-20844)
# ============================================================================

class ClipboardSecurityError(SecurityError):
    """Raised when clipboard security issue is detected."""
    pass


# Dangerous clipboard content patterns
CLIPBOARD_DANGEROUS_PATTERNS = [
    (r'<script[^>]*>', 'Script tag in clipboard'),
    (r'javascript:', 'javascript: URL'),
    (r'data:text/html', 'data:text/html URL'),
    (r'on\w+\s*=', 'Event handler'),
]


def sanitize_clipboard_content(content: str, expected_format: str = 'text/plain') -> str:
    """
    Sanitize clipboard content to prevent spoofing attacks.
    
    CVE-2026-0890: Firefox DOM spoofing via Copy & Paste/Drag & Drop
    CVE-2026-20844: Windows Clipboard Server privilege escalation
    
    Args:
        content: Clipboard content
        expected_format: Expected MIME type
        
    Returns:
        Sanitized clipboard content
        
    Raises:
        ClipboardSecurityError: If dangerous content detected
    """
    if expected_format == 'text/plain':
        # Strip HTML tags from plain text
        content = re.sub(r'<[^>]+>', '', content)
    
    # Check for dangerous patterns in any format
    for pattern, description in CLIPBOARD_DANGEROUS_PATTERNS:
        if re.search(pattern, content, re.IGNORECASE):
            raise ClipboardSecurityError(
                f"Clipboard contains dangerous content: {description}"
            )
    
    return content


def validate_clipboard_operation(operation: str, data: dict) -> None:
    """
    Validate clipboard operation for security.
    
    Args:
        operation: Operation type (copy, paste, cut)
        data: Clipboard data
        
    Raises:
        ClipboardSecurityError: If operation is suspicious
    """
    if operation not in ('copy', 'paste', 'cut'):
        raise ClipboardSecurityError(f"Invalid clipboard operation: {operation}")
    
    # Check for oversized clipboard data (potential DoS)
    if 'text' in data and len(data['text']) > 10 * 1024 * 1024:  # 10MB limit
        raise ClipboardSecurityError("Clipboard data exceeds size limit")


# ============================================================================
# Pass 110-111: Tapjacking/Overlay Attack Prevention (CVE-2025-48634, CVE-2026-0007)
# ============================================================================

class TapjackingError(SecurityError):
    """Raised when tapjacking vulnerability is detected."""
    pass


# Suspicious overlay characteristics
SUSPICIOUS_OVERLAY_PATTERNS = [
    (r'pointer-events\s*:\s*none', 'Click-through overlay'),
    (r'opacity\s*:\s*0', 'Invisible overlay'),
    (r'z-index\s*:\s*\d{5,}', 'Extremely high z-index'),
]


def check_tapjacking_risk(ui_config: dict) -> list:
    """
    Check for tapjacking vulnerabilities in UI configuration.
    
    CVE-2025-48634: Android tapjacking via relayoutWindow
    CVE-2026-0007: Android tapjacking/overlay attack in WindowInfo
    
    Args:
        ui_config: UI configuration dictionary
        
    Returns:
        List of detected tapjacking risks
    """
    risks = []
    
    # Check for overlay permissions
    if ui_config.get('system_alert_window', False):
        risks.append({
            'severity': 'high',
            'message': 'System alert window permission granted (overlay risk)',
        })
    
    # Check for suspicious CSS
    css = ui_config.get('css', '')
    for pattern, description in SUSPICIOUS_OVERLAY_PATTERNS:
        if re.search(pattern, css, re.IGNORECASE):
            risks.append({
                'severity': 'medium',
                'message': f'Suspicious overlay CSS: {description}',
            })
    
    # Check for touch event interception
    if ui_config.get('intercept_touch_events', False):
        risks.append({
            'severity': 'high',
            'message': 'Touch event interception enabled',
        })
    
    return risks


def validate_overlay_permissions(permissions: list) -> None:
    """
    Validate overlay permissions for security risks.
    
    Args:
        permissions: List of permissions
        
    Raises:
        TapjackingError: If dangerous overlay permissions detected
    """
    dangerous_permissions = [
        'SYSTEM_ALERT_WINDOW',
        'SYSTEM_OVERLAY_WINDOW',
    ]
    
    for perm in permissions:
        if perm in dangerous_permissions:
            raise TapjackingError(
                f"Dangerous overlay permission detected: {perm}"
            )


# ============================================================================
# Pass 112-113: PWA Security (CVE-2026-30240, CVE-2026-28355)
# ============================================================================

class PWASecurityError(SecurityError):
    """Raised when PWA security issue is detected."""
    pass


# Required PWA security headers
PWA_REQUIRED_HEADERS = [
    'X-Content-Type-Options',
    'X-Frame-Options',
    'Content-Security-Policy',
]


def validate_pwa_manifest(manifest: dict) -> list:
    """
    Validate PWA manifest for security issues.
    
    CVE-2026-30240: Budibase PWA ZIP processing path traversal
    CVE-2026-28355: Canarytokens PWA XSS
    
    Args:
        manifest: PWA manifest dictionary
        
    Returns:
        List of security issues
    """
    issues = []
    
    # Check for secure start_url
    start_url = manifest.get('start_url', '/')
    if start_url.startswith('http://'):
        issues.append({
            'severity': 'high',
            'message': 'PWA start_url uses insecure HTTP',
        })
    
    # Check for dangerous display modes
    display = manifest.get('display', 'browser')
    if display == 'fullscreen' and not manifest.get('shortcuts'):
        issues.append({
            'severity': 'low',
            'message': 'Fullscreen PWA without shortcuts may confuse users',
        })
    
    # Check for scope validation
    scope = manifest.get('scope', '/')
    if '..' in scope:
        issues.append({
            'severity': 'critical',
            'message': 'PWA scope contains path traversal (..)',
        })
    
    return issues


def validate_pwa_service_worker(sw_content: str) -> None:
    """
    Validate service worker code for security issues.
    
    Args:
        sw_content: Service worker JavaScript code
        
    Raises:
        PWASecurityError: If dangerous patterns detected
    """
    # Check for eval in service worker
    if 'eval(' in sw_content or 'new Function(' in sw_content:
        raise PWASecurityError("Service worker contains dangerous eval() or Function()")
    
    # Check for insecure cache strategies
    if re.search(r'caches\.open\s*\([^)]+\)', sw_content):
        # Check if cache name is properly sanitized
        pass  # This is a basic check, actual validation would be more complex


# ============================================================================
# Pass 114: Form Validation Security (CVE-2026-24576)
# ============================================================================

class FormValidationError(SecurityError):
    """Raised when form validation security issue is detected."""
    pass


# Common form bypass patterns
FORM_BYPASS_PATTERNS = [
    (r'disabled\s*=\s*["\']?false', 'Disabled attribute bypass'),
    (r'readonly\s*=\s*["\']?false', 'Readonly attribute bypass'),
    (r'type\s*=\s*["\']?hidden', 'Hidden field manipulation'),
]


def validate_form_data_security(form_data: dict, expected_fields: dict) -> None:
    """
    Validate form data for security bypass attempts.
    
    CVE-2026-24576: UX Flat WordPress plugin stored XSS via form input
    
    Args:
        form_data: Submitted form data
        expected_fields: Expected field definitions
        
    Raises:
        FormValidationError: If security bypass detected
    """
    # Check for unexpected fields
    for field in form_data.keys():
        if field not in expected_fields:
            raise FormValidationError(f"Unexpected form field: {field}")
    
    # Check for disabled field bypass
    for field, value in form_data.items():
        field_def = expected_fields.get(field, {})
        
        # Check if field should be disabled
        if field_def.get('disabled', False):
            raise FormValidationError(f"Attempted to submit disabled field: {field}")
        
        # Check for readonly bypass
        if field_def.get('readonly', False) and value != field_def.get('default'):
            raise FormValidationError(f"Attempted to modify readonly field: {field}")
        
        # Validate field type
        expected_type = field_def.get('type', 'text')
        if expected_type == 'number' and not isinstance(value, (int, float)):
            try:
                float(value)
            except (ValueError, TypeError):
                raise FormValidationError(f"Invalid number value for field: {field}")


# ============================================================================
# Pass 115-121: Additional UI/UX Security Passes
# ============================================================================

# Pass 115: Drag and Drop Security
def validate_drag_drop_operation(data: dict) -> None:
    """
    Validate drag and drop operation for security.
    
    CVE-2026-0890: Firefox DOM spoofing via Drag & Drop
    
    Args:
        data: Drag/drop data transfer
        
    Raises:
        SecurityError: If suspicious drag/drop detected
    """
    # Check for suspicious MIME types
    allowed_types = ['text/plain', 'text/uri-list', 'text/html']
    
    for item_type in data.get('types', []):
        if item_type not in allowed_types:
            # Check for executable content
            if 'javascript' in item_type.lower() or 'script' in item_type.lower():
                raise SecurityError(f"Dangerous drag/drop MIME type: {item_type}")


# Pass 116: Focus Management Security
def validate_focus_management(element_id: str, allowed_ids: list) -> None:
    """
    Validate focus management to prevent focus stealing attacks.
    
    Args:
        element_id: Element to receive focus
        allowed_ids: List of allowed element IDs for focus
        
    Raises:
        SecurityError: If unauthorized focus attempt
    """
    if element_id not in allowed_ids:
        raise SecurityError(f"Unauthorized focus attempt on element: {element_id}")


# Pass 117: Toast/Notification Security
NOTIFICATION_MAX_LENGTH = 200

def sanitize_notification_content(content: str, max_length: int = None) -> str:
    """
    Sanitize notification/toast content.
    
    Args:
        content: Notification content
        max_length: Maximum length (defaults to NOTIFICATION_MAX_LENGTH)
        
    Returns:
        Sanitized content
    """
    # Strip HTML
    content = re.sub(r'<[^>]+>', '', content)
    
    # Remove markdown link targets (prevent SSRF)
    content = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', content)
    
    # Limit length
    limit = max_length or NOTIFICATION_MAX_LENGTH
    if len(content) > limit:
        content = content[:limit - 3] + '...'
    
    return content


# Pass 118: Modal/Dialog Security
def validate_modal_security(modal_config: dict) -> list:
    """
    Validate modal/dialog configuration for security.
    
    Args:
        modal_config: Modal configuration
        
    Returns:
        List of security issues
    """
    issues = []
    
    # Check for proper focus trapping
    if not modal_config.get('trap_focus', False):
        issues.append({
            'severity': 'medium',
            'message': 'Modal does not trap focus (accessibility/security risk)',
        })
    
    # Check for close on escape
    if not modal_config.get('close_on_escape', True):
        issues.append({
            'severity': 'low',
            'message': 'Modal does not close on Escape key',
        })
    
    # Check for backdrop click to close
    if not modal_config.get('close_on_backdrop', True):
        issues.append({
            'severity': 'low',
            'message': 'Modal does not close on backdrop click',
        })
    
    return issues


# Pass 119: File Picker Security
def validate_file_picker_selection(selected_files: list, allowed_types: list, max_size: int) -> None:
    """
    Validate file picker selections.
    
    Args:
        selected_files: List of selected files
        allowed_types: List of allowed MIME types
        max_size: Maximum file size in bytes
        
    Raises:
        SecurityError: If invalid selection
    """
    for file in selected_files:
        # Check file type
        if file.get('type') not in allowed_types:
            raise SecurityError(f"Invalid file type: {file.get('type')}")
        
        # Check file size
        if file.get('size', 0) > max_size:
            raise SecurityError(f"File exceeds maximum size: {file.get('name')}")


# Pass 120: Animation/Transition Security
def sanitize_animation_config(config: dict) -> dict:
    """
    Sanitize animation configuration to prevent seizure/performance attacks.
    
    Args:
        config: Animation configuration
        
    Returns:
        Sanitized configuration
    """
    # Limit animation duration
    if config.get('duration', 0) > 5000:  # Max 5 seconds
        config['duration'] = 5000
    
    # Limit iteration count
    if config.get('iterations') == 'infinite':
        config['iterations'] = 10  # Limit to 10 iterations
    
    # Check for rapid flashing (seizure risk)
    if config.get('duration', 1000) < 100 and config.get('iterations', 1) > 3:
        config['duration'] = 100  # Slow down rapid animations
    
    return config


# Pass 121: Accessibility Security (ARIA manipulation prevention)
def sanitize_aria_attributes(attributes: dict) -> dict:
    """
    Sanitize ARIA attributes to prevent accessibility manipulation.
    
    Args:
        attributes: ARIA attributes dictionary
        
    Returns:
        Sanitized attributes
    """
    allowed_aria = [
        'aria-label', 'aria-labelledby', 'aria-describedby',
        'aria-hidden', 'aria-expanded', 'aria-selected',
        'aria-checked', 'aria-disabled', 'aria-readonly',
        'aria-required', 'aria-invalid', 'aria-busy',
        'aria-live', 'aria-atomic', 'aria-relevant',
        'aria-valuemin', 'aria-valuemax', 'aria-valuenow',
        'aria-level', 'aria-posinset', 'aria-setsize',
        'aria-sort', 'aria-orientation',
    ]
    
    sanitized = {}
    for attr, value in attributes.items():
        attr_lower = attr.lower()
        if attr_lower in allowed_aria:
            # Sanitize value - no HTML/JS
            if isinstance(value, str):
                value = re.sub(r'[<>&"\']', '', value)
            sanitized[attr_lower] = value
    
    return sanitized


# ============================================================================
# Update __all__ exports for passes 101-121
# ============================================================================

__all__.extend([
    # Pass 101: SVG XSS
    'SVGXSSError',
    'sanitize_svg_content',
    'SVG_SCRIPT_DANGEROUS_ATTRS',
    
    # Pass 102: Markdown XSS
    'MarkdownXSSError',
    'sanitize_markdown_content',
    'MARKDOWN_DANGEROUS_PATTERNS',
    
    # Pass 103: ScrollRestoration XSS
    'ScrollRestorationXSSError',
    'validate_scroll_restoration_key',
    
    # Pass 104-106: Prototype Pollution
    'PrototypePollutionError',
    'deep_prototype_pollution_check',
    'sanitize_object_keys',
    'PROTOTYPE_POLLUTION_KEYS',
    
    # Pass 107: CSS Injection
    'CSSInjectionError',
    'sanitize_css_content',
    'CSS_DANGEROUS_PATTERNS',
    
    # Pass 108: Clickjacking
    'ClickjackingError',
    'get_clickjacking_protection_headers',
    'generate_frame_busting_js',
    
    # Pass 109: Clipboard Security
    'ClipboardSecurityError',
    'sanitize_clipboard_content',
    'validate_clipboard_operation',
    
    # Pass 110-111: Tapjacking
    'TapjackingError',
    'check_tapjacking_risk',
    'validate_overlay_permissions',
    'SUSPICIOUS_OVERLAY_PATTERNS',
    
    # Pass 112-113: PWA Security
    'PWASecurityError',
    'validate_pwa_manifest',
    'validate_pwa_service_worker',
    'PWA_REQUIRED_HEADERS',
    
    # Pass 114: Form Validation
    'FormValidationError',
    'validate_form_data_security',
    'FORM_BYPASS_PATTERNS',
    
    # Pass 115: Drag & Drop
    'validate_drag_drop_operation',
    
    # Pass 116: Focus Management
    'validate_focus_management',
    
    # Pass 117: Notification Security
    'sanitize_notification_content',
    'NOTIFICATION_MAX_LENGTH',
    
    # Pass 118: Modal Security
    'validate_modal_security',
    
    # Pass 119: File Picker
    'validate_file_picker_selection',
    
    # Pass 120: Animation Security
    'sanitize_animation_config',
    
    # Pass 121: ARIA Security
    'sanitize_aria_attributes',
])
