"""
Gap analyzer for correlating device data with NIS2 requirements.
"""
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

from ..models import NetworkDevice, DeviceCommandResult
from .checklist import ChecklistQuestion, ComplianceStatus


@dataclass
class DeviceGap:
    """A gap identified from device configuration analysis."""
    gap_type: str
    severity: str  # critical, high, medium, low
    description: str
    nis2_article: str
    device_id: str
    config_snippet: Optional[str] = None
    remediation: Optional[str] = None


class DeviceConfigAnalyzer:
    """
    Analyze device configurations for NIS2 compliance gaps.
    """
    
    def analyze_device(self, device: NetworkDevice) -> List[DeviceGap]:
        """
        Analyze a device for compliance gaps.
        
        Args:
            device: NetworkDevice with command results
        
        Returns:
            List of identified gaps
        """
        gaps = []
        _analyze = self._analyze_command_result  # Local variable for faster lookup
        
        for result in device.command_results:
            if result.success:
                gaps.extend(_analyze(device, result))
        
        return gaps
    
    def _analyze_command_result(
        self,
        device: NetworkDevice,
        result: DeviceCommandResult
    ) -> List[DeviceGap]:
        """Analyze a single command result for gaps."""
        gaps = []
        command_lower = result.command.lower()
        output = result.raw_output
        
        # Use local variables for faster method lookup
        _check_version = self._check_version
        _check_ssh_config = self._check_ssh_config
        _check_snmp_config = self._check_snmp_config
        _check_firewall_rules = self._check_firewall_rules
        _check_port_security = self._check_port_security
        _check_logging = self._check_logging
        _check_ntp = self._check_ntp
        _check_user_accounts = self._check_user_accounts
        
        # Check based on command type - use tuple of checks for efficiency
        checks = (
            ("version", _check_version),
            ("ssh", _check_ssh_config),
            ("snmp", _check_snmp_config),
            ("access-list", _check_firewall_rules),
            ("iptables", _check_firewall_rules),
            ("port-security", _check_port_security),
            ("logging", _check_logging),
            ("rsyslog", _check_logging),
            ("ntp", _check_ntp),
            ("user", _check_user_accounts),
            ("passwd", _check_user_accounts),
        )
        
        checked = set()  # Avoid duplicate checks
        for keyword, check_func in checks:
            if keyword in command_lower and check_func not in checked:
                gaps.extend(check_func(device, output))
                checked.add(check_func)
        
        return gaps
    
    def _check_version(self, device: NetworkDevice, output: str) -> List[DeviceGap]:
        """Check for outdated firmware/software versions."""
        gaps = []
        
        # Check for EOL Cisco IOS versions
        if device.vendor == "Cisco":
            # Look for known EOL version patterns - use 'in' check first for performance
            output_upper = output.upper()
            
            if "VERSION 12." in output_upper:
                gaps.append(DeviceGap(
                    gap_type="outdated_firmware",
                    severity="high",
                    description="Device is running Cisco IOS 12.x is End-of-Life",
                    nis2_article="21(2)(e)",
                    device_id=device.device_id,
                    config_snippet=output[:500],
                    remediation="Upgrade to a supported software version"
                ))
            elif "VERSION 15.0." in output_upper:
                gaps.append(DeviceGap(
                    gap_type="outdated_firmware",
                    severity="high",
                    description="Device is running Cisco IOS 15.0 is End-of-Life",
                    nis2_article="21(2)(e)",
                    device_id=device.device_id,
                    config_snippet=output[:500],
                    remediation="Upgrade to a supported software version"
                ))
            elif "VERSION 15.1(1)" in output_upper:
                gaps.append(DeviceGap(
                    gap_type="outdated_firmware",
                    severity="high",
                    description="Device is running Known vulnerable version",
                    nis2_article="21(2)(e)",
                    device_id=device.device_id,
                    config_snippet=output[:500],
                    remediation="Upgrade to a supported software version"
                ))
        
        return gaps
    
    def _check_ssh_config(self, device: NetworkDevice, output: str) -> List[DeviceGap]:
        """Check SSH configuration for security issues."""
        gaps = []
        output_lower = output.lower()
        
        # Check for SSH version (should be v2)
        if "version 1" in output_lower and "version 2" not in output_lower:
            gaps.append(DeviceGap(
                gap_type="weak_ssh",
                severity="high",
                description="SSH version 1 is enabled (insecure)",
                nis2_article="21(2)(k)",
                device_id=device.device_id,
                config_snippet="SSH Version 1",
                remediation="Disable SSHv1: 'ip ssh version 2'"
            ))
        
        # Check for weak ciphers on Linux - use tuple for faster iteration
        if "ciphers" in output_lower:
            weak_ciphers = ("3des", "aes128-cbc", "blowfish")
            for cipher in weak_ciphers:
                if cipher in output_lower:
                    gaps.append(DeviceGap(
                        gap_type="weak_crypto",
                        severity="medium",
                        description=f"Weak cipher detected: {cipher}",
                        nis2_article="21(2)(i)",
                        device_id=device.device_id,
                        remediation="Remove weak ciphers from SSH config"
                    ))
        
        return gaps
    
    def _check_snmp_config(self, device: NetworkDevice, output: str) -> List[DeviceGap]:
        """Check SNMP configuration for security issues."""
        gaps = []
        output_lower = output.lower()
        
        # Check for default community strings - use tuple for faster iteration
        default_communities = ("public", "private", "community")
        
        for community in default_communities:
            if f'community {community}' in output_lower or f'community "{community}"' in output_lower:
                gaps.append(DeviceGap(
                    gap_type="default_snmp_community",
                    severity="critical",
                    description=f"Default SNMP community '{community}' in use",
                    nis2_article="21(2)(j)",
                    device_id=device.device_id,
                    config_snippet=f"snmp-server community {community}",
                    remediation="Change to complex community string or use SNMPv3"
                ))
        
        # Check for SNMPv1/v2c (should use v3)
        if "snmp-server community" in output_lower and "v3" not in output_lower:
            gaps.append(DeviceGap(
                gap_type="legacy_snmp",
                severity="medium",
                description="SNMPv1/v2c in use instead of SNMPv3",
                nis2_article="21(2)(j)",
                device_id=device.device_id,
                remediation="Migrate to SNMPv3 with authentication and encryption"
            ))
        
        return gaps
    
    def _check_firewall_rules(self, device: NetworkDevice, output: str) -> List[DeviceGap]:
        """Check firewall/ACL configuration."""
        gaps = []
        output_lower = output.lower()
        
        # Check for overly permissive rules
        if "permit any any" in output_lower or "allow any" in output_lower:
            gaps.append(DeviceGap(
                gap_type="permissive_acl",
                severity="high",
                description="Overly permissive firewall rule detected (permit any any)",
                nis2_article="21(2)(j)",
                device_id=device.device_id,
                config_snippet="permit any any",
                remediation="Implement least-privilege access rules"
            ))
        
        # Check for management access from any - use simple string search
        if "permit" in output_lower and "any" in output_lower:
            if ("ssh" in output_lower or "telnet" in output_lower or "snmp" in output_lower):
                gaps.append(DeviceGap(
                    gap_type="open_management",
                    severity="critical",
                    description="Management protocols accessible from any source",
                    nis2_article="21(2)(j)",
                    device_id=device.device_id,
                    remediation="Restrict management access to specific source addresses"
                ))
        
        return gaps
    
    def _check_port_security(self, device: NetworkDevice, output: str) -> List[DeviceGap]:
        """Check port security configuration."""
        gaps = []
        
        # Check if port security is disabled
        if "port security is disabled" in output.lower() or "port-security is disabled" in output.lower():
            gaps.append(DeviceGap(
                gap_type="no_port_security",
                severity="medium",
                description="Port security is disabled on access ports",
                nis2_article="21(2)(j)",
                device_id=device.device_id,
                remediation="Enable port security on all access ports"
            ))
        
        return gaps
    
    def _check_logging(self, device: NetworkDevice, output: str) -> List[DeviceGap]:
        """Check logging configuration."""
        gaps = []
        output_lower = output.lower()
        
        # Check if logging is disabled
        if "logging disabled" in output_lower or "no logging" in output_lower:
            gaps.append(DeviceGap(
                gap_type="no_logging",
                severity="high",
                description="System logging is disabled",
                nis2_article="21(2)(b)",
                device_id=device.device_id,
                remediation="Enable logging to central syslog server"
            ))
        
        # Check for console-only logging
        if "logging console" in output_lower and "logging host" not in output_lower:
            gaps.append(DeviceGap(
                gap_type="local_logging_only",
                severity="medium",
                description="Logging only to console (no remote syslog)",
                nis2_article="21(2)(b)",
                device_id=device.device_id,
                remediation="Configure remote syslog server for centralized logging"
            ))
        
        return gaps
    
    def _check_ntp(self, device: NetworkDevice, output: str) -> List[DeviceGap]:
        """Check NTP configuration."""
        gaps = []
        output_lower = output.lower()
        
        # Check if NTP is not configured
        if "no ntp server" in output_lower or "not configured" in output_lower:
            gaps.append(DeviceGap(
                gap_type="no_ntp",
                severity="medium",
                description="NTP not configured - time sync may drift",
                nis2_article="21(2)(b)",
                device_id=device.device_id,
                remediation="Configure NTP servers for accurate time synchronization"
            ))
        
        return gaps
    
    def _check_user_accounts(self, device: NetworkDevice, output: str) -> List[DeviceGap]:
        """Check user account configuration."""
        gaps = []
        output_lower = output.lower()
        
        # Check for default accounts - use tuple for faster iteration
        default_accounts = ("admin", "administrator", "root", "cisco")
        
        for account in default_accounts:
            if f"username {account}" in output_lower or f":{account}:" in output_lower:
                gaps.append(DeviceGap(
                    gap_type="default_account",
                    severity="medium",
                    description=f"Default account '{account}' exists",
                    nis2_article="21(2)(j)",
                    device_id=device.device_id,
                    remediation="Rename or disable default accounts"
                ))
        
        return gaps


class GapAnalyzer:
    """
    Analyze gaps between device configurations and NIS2 requirements.
    """
    
    def __init__(self):
        self.config_analyzer = DeviceConfigAnalyzer()
    
    def analyze_all_devices(self, devices: List[NetworkDevice]) -> Dict[str, List[DeviceGap]]:
        """
        Analyze all devices for gaps.
        
        Args:
            devices: List of NetworkDevice objects
        
        Returns:
            Dict mapping device_id to list of gaps
        """
        all_gaps = {}
        _analyze = self.config_analyzer.analyze_device  # Local variable for faster lookup
        
        for device in devices:
            gaps = _analyze(device)
            if gaps:
                all_gaps[device.device_id] = gaps
        
        return all_gaps
    
    def correlate_with_checklist(
        self,
        checklist_questions: List[ChecklistQuestion],
        device_gaps: Dict[str, List[DeviceGap]]
    ) -> List[ChecklistQuestion]:
        """
        Correlate device gaps with checklist questions.
        
        Args:
            checklist_questions: Questions to update
            device_gaps: Gaps found on devices
        
        Returns:
            Updated questions with device evidence
        """
        # Flatten all gaps using list comprehension (faster than extend loop)
        all_gaps = [gap for gaps in device_gaps.values() for gap in gaps]
        
        # Group gaps by article for O(1) lookup instead of O(n^2)
        gaps_by_article: Dict[str, List[DeviceGap]] = {}
        for gap in all_gaps:
            article = gap.nis2_article
            if article not in gaps_by_article:
                gaps_by_article[article] = []
            gaps_by_article[article].append(gap)
        
        # Map gaps to questions
        NOT_STARTED = ComplianceStatus.NOT_STARTED  # Local for faster lookup
        NON_COMPLIANT = ComplianceStatus.NON_COMPLIANT
        PARTIALLY_COMPLIANT = ComplianceStatus.PARTIALLY_COMPLIANT
        
        for question in checklist_questions:
            relevant_gaps = gaps_by_article.get(question.nis2_article)
            
            if relevant_gaps:
                device_evidence = question.device_evidence
                evidence_found_append = question.evidence_found.append
                
                # Add device evidence
                for gap in relevant_gaps:
                    device_evidence[gap.device_id] = gap.config_snippet or gap.description
                    evidence_found_append(gap.description)
                
                # Auto-update status based on gaps
                has_critical = any(g.severity == "critical" for g in relevant_gaps)
                if has_critical:
                    question.status = NON_COMPLIANT
                elif question.status == NOT_STARTED:
                    question.status = PARTIALLY_COMPLIANT
        
        return checklist_questions
    
    def generate_gap_summary(self, device_gaps: Dict[str, List[DeviceGap]]) -> Dict[str, Any]:
        """
        Generate summary of all gaps.
        
        Args:
            device_gaps: Gaps by device
        
        Returns:
            Summary dict
        """
        # Pre-allocate counters for performance
        severity_counts = {"critical": 0, "high": 0, "medium": 0, "low": 0}
        type_counts: Dict[str, int] = {}
        article_counts: Dict[str, int] = {}
        total_gaps = 0
        
        # Use local variables for faster lookup
        severity_local = severity_counts
        type_local = type_counts
        article_local = article_counts
        
        for gaps in device_gaps.values():
            total_gaps += len(gaps)
            for gap in gaps:
                severity_local[gap.severity] = severity_local.get(gap.severity, 0) + 1
                gap_type = gap.gap_type
                type_local[gap_type] = type_local.get(gap_type, 0) + 1
                article = gap.nis2_article
                article_local[article] = article_local.get(article, 0) + 1
        
        return {
            "total_gaps": total_gaps,
            "affected_devices": len(device_gaps),
            "severity_breakdown": severity_counts,
            "gap_types": type_counts,
            "nis2_articles": article_counts,
        }
