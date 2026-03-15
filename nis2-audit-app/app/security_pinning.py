"""
Certificate and host key pinning for the NIS2 Field Audit Tool.

Provides protection against man-in-the-middle attacks by verifying
that remote hosts present expected cryptographic identities.
"""
import os
import json
import hashlib
import hmac
from pathlib import Path
from typing import Optional, Dict, Set, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timezone

from .security_utils import atomic_write, secure_file_permissions


@dataclass
class PinnedHost:
    """Represents a pinned host identity."""
    hostname: str
    port: int
    key_type: str  # ssh-rsa, ssh-ed25519, ecdsa-sha2-nistp256, etc.
    key_fingerprint: str  # SHA256:xxxxx or MD5:xxxxx format
    pinned_at: str  # ISO timestamp
    last_seen: str  # ISO timestamp
    pin_type: str = "first_seen"  # first_seen, manual, imported


class HostKeyPinningError(Exception):
    """Raised when host key verification fails."""
    pass


class HostKeyPinningManager:
    """
    Manages pinned host keys for SSH connections.
    
    SECURITY: This provides TOFU (Trust On First Use) style verification
    similar to SSH's known_hosts, with additional protections:
    - First-seen keys are automatically pinned
    - Key changes trigger warnings and require confirmation
    - Pins are stored securely with restricted permissions
    """
    
    def __init__(self, pins_file: Optional[Path] = None):
        """
        Initialize the pinning manager.
        
        Args:
            pins_file: Path to store pinned hosts. Uses default if None.
        """
        if pins_file is None:
            pins_file = self._get_default_pins_file()
        
        self._pins_file = Path(pins_file)
        self._pins: Dict[str, PinnedHost] = {}
        self._load_pins()
    
    def _get_default_pins_file(self) -> Path:
        """Get default location for pins file."""
        if os.name == 'nt':  # Windows
            base_dir = Path(os.environ.get('LOCALAPPDATA', Path.home() / 'AppData/Local'))
        elif os.sys.platform == 'darwin':  # macOS
            base_dir = Path.home() / 'Library/Application Support'
        else:  # Linux
            base_dir = Path(os.environ.get('XDG_DATA_HOME', Path.home() / '.local/share'))
        
        pins_dir = base_dir / 'nis2-audit'
        pins_dir.mkdir(parents=True, exist_ok=True)
        return pins_dir / 'pinned_hosts.json'
    
    def _load_pins(self) -> None:
        """Load pinned hosts from file."""
        if not self._pins_file.exists():
            return
        
        try:
            with open(self._pins_file, 'r') as f:
                data = json.load(f)
            
            for hostname, pin_data in data.items():
                self._pins[hostname] = PinnedHost(**pin_data)
        except (json.JSONDecodeError, TypeError, KeyError) as e:
            import logging
            logging.getLogger(__name__).error(f"Failed to load host pins: {e}")
            self._pins = {}
    
    def _save_pins(self) -> None:
        """Save pinned hosts to file."""
        data = {hostname: asdict(pin) for hostname, pin in self._pins.items()}
        
        # Atomic write with secure permissions
        with atomic_write(self._pins_file, mode='w') as f:
            json.dump(data, f, indent=2)
        
        secure_file_permissions(self._pins_file, 0o600)
    
    def _normalize_hostname(self, hostname: str, port: int = 22) -> str:
        """Create consistent key for hostname:port combinations."""
        hostname = hostname.lower().strip()
        if port != 22:
            return f"[{hostname}]:{port}"
        return hostname
    
    def compute_fingerprint(self, key_bytes: bytes, hash_algo: str = "sha256") -> str:
        """
        Compute SSH-style fingerprint of a host key.
        
        Args:
            key_bytes: Raw key bytes
            hash_algo: Hash algorithm (sha256 or md5)
            
        Returns:
            Fingerprint string (e.g., "SHA256:xxxxx" or "MD5:xx:xx:xx...")
        """
        if hash_algo.lower() == "sha256":
            hash_bytes = hashlib.sha256(key_bytes).digest()
            # Base64 encode, remove padding
            import base64
            b64 = base64.b64encode(hash_bytes).decode('ascii').rstrip('=')
            return f"SHA256:{b64}"
        else:
            hash_bytes = hashlib.md5(key_bytes).digest()
            # Hex with colons
            hex_str = hash_bytes.hex()
            return "MD5:" + ':'.join(hex_str[i:i+2] for i in range(0, 32, 2))
    
    def pin_host(self, hostname: str, port: int, key_type: str, 
                 key_fingerprint: str, pin_type: str = "manual") -> None:
        """
        Manually pin a host key.
        
        Args:
            hostname: Hostname or IP address
            port: SSH port
            key_type: Key algorithm (ssh-rsa, ssh-ed25519, etc.)
            key_fingerprint: Computed fingerprint
            pin_type: How this pin was created
        """
        key = self._normalize_hostname(hostname, port)
        now = datetime.now(timezone.utc).isoformat()
        
        self._pins[key] = PinnedHost(
            hostname=hostname,
            port=port,
            key_type=key_type,
            key_fingerprint=key_fingerprint,
            pinned_at=now,
            last_seen=now,
            pin_type=pin_type
        )
        
        self._save_pins()
    
    def verify_or_pin_host(self, hostname: str, port: int, 
                           key_type: str, key_fingerprint: str) -> Tuple[bool, str]:
        """
        Verify a host key against pinned value, or pin if first seen.
        
        Args:
            hostname: Hostname or IP address
            port: SSH port
            key_type: Key algorithm
            key_fingerprint: Computed fingerprint
            
        Returns:
            Tuple of (is_valid, message)
            - First seen: (True, "Pinned new host key")
            - Matches: (True, "Host key verified")
            - Mismatch: (False, "Host key changed!")
        """
        key = self._normalize_hostname(hostname, port)
        
        if key not in self._pins:
            # First time seeing this host - pin it
            self.pin_host(hostname, port, key_type, key_fingerprint, "first_seen")
            return True, f"Pinned new {key_type} key for {hostname}:{port}"
        
        pinned = self._pins[key]
        
        pinned.last_seen = datetime.now(timezone.utc).isoformat()
        self._save_pins()
        
        # Verify key type matches
        if pinned.key_type != key_type:
            return False, (
                f"Host key type changed for {hostname}! "
                f"Expected {pinned.key_type}, got {key_type}. "
                f"This may indicate a man-in-the-middle attack."
            )
        
        # Verify fingerprint matches (constant-time comparison)
        if not hmac.compare_digest(pinned.key_fingerprint, key_fingerprint):
            return False, (
                f"Host key changed for {hostname}! "
                f"This may indicate a man-in-the-middle attack. "
                f"Remove the pin if this was an authorized key change."
            )
        
        return True, f"Host key verified for {hostname}"
    
    def remove_pin(self, hostname: str, port: int = 22) -> bool:
        """
        Remove a pinned host.
        
        Args:
            hostname: Hostname or IP address
            port: SSH port
            
        Returns:
            True if removed, False if not found
        """
        key = self._normalize_hostname(hostname, port)
        
        if key in self._pins:
            del self._pins[key]
            self._save_pins()
            return True
        return False
    
    def is_pinned(self, hostname: str, port: int = 22) -> bool:
        """Check if a host has a pinned key."""
        key = self._normalize_hostname(hostname, port)
        return key in self._pins
    
    def get_pin_info(self, hostname: str, port: int = 22) -> Optional[PinnedHost]:
        """Get pinning information for a host."""
        key = self._normalize_hostname(hostname, port)
        return self._pins.get(key)
    
    def list_pinned_hosts(self) -> Dict[str, PinnedHost]:
        """Return all pinned hosts."""
        return dict(self._pins)
    
    def clear_all_pins(self) -> None:
        """Remove all pinned hosts (use with caution)."""
        self._pins.clear()
        if self._pins_file.exists():
            self._pins_file.unlink()


# Integration with SSH connections
class PinnedSSHVerifier:
    """
    SSH host key verifier that uses the pinning manager.
    
    This class can be used with paramiko or netmiko to verify host keys
    against pinned values.
    """
    
    def __init__(self, pinning_manager: Optional[HostKeyPinningManager] = None):
        if pinning_manager is None:
            pinning_manager = HostKeyPinningManager()
        self._pm = pinning_manager
    
    def verify_host_key(self, hostname: str, port: int, 
                        key_type: str, key_bytes: bytes) -> Tuple[bool, str]:
        """
        Verify a host key against pinned value.
        
        Args:
            hostname: Hostname or IP
            port: SSH port
            key_type: Key algorithm name
            key_bytes: Raw public key bytes
            
        Returns:
            Tuple of (is_valid, message)
        """
        fingerprint = self._pm.compute_fingerprint(key_bytes)
        return self._pm.verify_or_pin_host(hostname, port, key_type, fingerprint)


# Convenience functions
def get_pinning_manager() -> HostKeyPinningManager:
    """Get the global pinning manager instance."""
    return HostKeyPinningManager()
