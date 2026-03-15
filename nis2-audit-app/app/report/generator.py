"""
Report generator for NIS2 audit results.
"""
import json
import logging
import os
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timezone

from ..models import AuditSession, NetworkDevice, AuditFinding
from ..audit.checklist import ChecklistSection
from ..audit.scorer import ComplianceScore
from ..security_utils import validate_path

logger = logging.getLogger(__name__)


def check_disk_space(path: Path, required_bytes: int = 10 * 1024 * 1024) -> Tuple[bool, str]:
    """
    Check if there's enough disk space at the given path.
    
    Args:
        path: Path to check
        required_bytes: Required free space (default 10MB)
        
    Returns:
        Tuple of (has_space, message)
    """
    try:
        # Get free space
        usage = shutil.disk_usage(path)
        free_space = usage.free
        
        if free_space < required_bytes:
            return False, (
                f"Insufficient disk space. Need {required_bytes / (1024*1024):.1f} MB, "
                f"have {free_space / (1024*1024):.1f} MB free."
            )
        
        return True, f"Sufficient disk space: {free_space / (1024*1024):.1f} MB free"
        
    except Exception as e:
        logger.warning(f"Could not check disk space: {e}")
        return False, f"Could not check disk space: {e}"


def validate_report_path(file_path: str, allow_overwrite: bool = False, 
                         check_space: bool = True) -> Path:
    """
    Validate a report file path for security.
    
    Args:
        file_path: The requested file path
        allow_overwrite: Whether to allow overwriting existing files
        check_space: Whether to check available disk space
        
    Returns:
        Validated Path object
        
    Raises:
        ValueError: If path is invalid or unsafe
    """
    # Use security_utils.validate_path for comprehensive validation
    try:
        # Default to user's home directory as base
        base_dir = Path.home()
        path = validate_path(file_path, base_dir, allow_symlinks=False)
    except Exception as e:
        # Fallback to basic validation if security_utils fails
        path = Path(file_path).resolve()
        
        # Check for path traversal attacks
        home_dir = Path.home().resolve()
        allowed_roots = [home_dir, Path("/tmp").resolve()]
        
        is_allowed = any(str(path).startswith(str(root)) for root in allowed_roots)
        if not is_allowed:
            raise ValueError(f"Path must be within home directory or /tmp: {file_path}")
    
    # Check for suspicious characters
    suspicious = ['..', '~', '$', '`', '|', ';', '&', '<', '>', '\x00']
    for char in suspicious:
        if char in file_path:
            raise ValueError(f"Path contains invalid characters: {repr(char)}")
    
    # Ensure parent directory exists or can be created
    parent = path.parent
    if not parent.exists():
        try:
            parent.mkdir(parents=True, exist_ok=True)
        except (OSError, PermissionError) as e:
            raise ValueError(f"Cannot create directory {parent}: {e}")
    
    # Check if file already exists
    if path.exists() and not allow_overwrite:
        raise ValueError(f"File already exists: {path}")
    
    # Check if parent is writable
    if not parent.exists() or not os.access(parent, os.W_OK):
        raise ValueError(f"Directory is not writable: {parent}")
    
    # Check disk space
    if check_space:
        has_space, message = check_disk_space(parent)
        if not has_space:
            raise ValueError(message)
    
    return path


class ReportGenerator:
    """
    Generate audit reports in various formats.
    """
    
    def __init__(self, template_dir: Optional[str] = None):
        """
        Initialize report generator.
        
        Args:
            template_dir: Directory containing Jinja2 templates
        """
        if template_dir:
            self.template_dir = Path(template_dir)
        else:
            self.template_dir = Path(__file__).parent / "templates"
    
    def generate_markdown_report(
        self,
        session: AuditSession,
        devices: List[NetworkDevice],
        findings: List[AuditFinding],
        checklist_sections: List[ChecklistSection],
        compliance_score: Optional[ComplianceScore] = None,
        sanction_exposure: Optional[Dict] = None,
    ) -> str:
        """
        Generate Markdown report using Jinja2 template.
        
        Args:
            session: Audit session
            devices: Discovered devices
            findings: Audit findings
            checklist_sections: Checklist with responses
            compliance_score: Calculated compliance score
            sanction_exposure: Sanction exposure calculation
        
        Returns:
            Markdown report as string
        """
        try:
            from jinja2 import Template
        except ImportError:
            # Fallback without Jinja2
            return self._generate_markdown_simple(
                session, devices, findings, checklist_sections,
                compliance_score, sanction_exposure
            )
        
        # Load template
        template_path = self.template_dir / "markdown_report.md"
        if template_path.exists():
            template = Template(template_path.read_text())
        else:
            # Use inline template
            template = Template(self._get_default_template())
        
        # Prepare context
        context = self._prepare_context(
            session, devices, findings, checklist_sections,
            compliance_score, sanction_exposure
        )
        
        return template.render(**context)
    
    def _prepare_context(
        self,
        session: AuditSession,
        devices: List[NetworkDevice],
        findings: List[AuditFinding],
        checklist_sections: List[ChecklistSection],
        compliance_score: Optional[ComplianceScore],
        sanction_exposure: Optional[Dict],
    ) -> Dict[str, Any]:
        """Prepare template context."""
        
        # Count device types - single pass for efficiency
        router_count = switch_count = firewall_count = server_count = unknown_count = 0
        for d in devices:
            dt = d.device_type
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
        
        device_summary = {
            "router_count": router_count,
            "switch_count": switch_count,
            "firewall_count": firewall_count,
            "server_count": server_count,
            "unknown_count": unknown_count,
        }
        
        # Findings by severity - use dict.get for cleaner code
        findings_by_severity: Dict[str, int] = {}
        fbs_local = findings_by_severity  # Local for faster lookup
        for finding in findings:
            severity = finding.severity
            fbs_local[severity] = fbs_local.get(severity, 0) + 1
        
        # Domain scores - use list comprehension for better performance
        domain_scores = []
        if compliance_score:
            score_items = (
                ("Governance", compliance_score.governance_score),
                ("Technical Controls", compliance_score.technical_controls_score),
                ("Incident Response", compliance_score.incident_response_score),
                ("Supply Chain", compliance_score.supply_chain_score),
                ("Documentation", compliance_score.documentation_score),
                ("Management Oversight", compliance_score.management_oversight_score),
            )
            domain_scores = [
                {
                    "name": name,
                    "score": score.score,
                    "weight": score.weight,
                    "weighted_score": score.weighted_score,
                }
                for name, score in score_items
            ]
        
        return {
            "entity_name": session.entity_input.legal_name,
            "entity_sector": session.entity_input.sector,
            "audit_date": session.created_at.strftime("%Y-%m-%d %H:%M"),
            "session_id": session.session_id,
            "auditor_name": session.auditor_name,
            "classification": session.classification,
            "compliance_score": compliance_score,
            "domain_scores": domain_scores,
            "devices": devices,
            "device_summary": device_summary,
            "findings": findings,
            "findings_by_severity": findings_by_severity,
            "checklist_sections": checklist_sections,
            "sanction_exposure": sanction_exposure,
        }
    
    def _generate_markdown_simple(
        self,
        session: AuditSession,
        devices: List[NetworkDevice],
        findings: List[AuditFinding],
        checklist_sections: List[ChecklistSection],
        compliance_score: Optional[ComplianceScore],
        sanction_exposure: Optional[Dict],
    ) -> str:
        """Generate simple Markdown without Jinja2."""
        lines = [
            "# NIS2 Compliance Audit Report",
            "",
            f"**Entity:** {session.entity_input.legal_name}",
            f"**Sector:** {session.entity_input.sector}",
            f"**Date:** {session.created_at.strftime('%Y-%m-%d %H:%M')}",
            f"**Session:** {session.session_id}",
            "",
            "## Executive Summary",
            "",
        ]
        
        if compliance_score:
            lines.extend([
                f"**Compliance Score:** {compliance_score.overall_score:.1f}% "
                f"- {compliance_score.rating}",
                "",
                "### Domain Scores",
                "",
            ])
            score_map = {
                "Governance": compliance_score.governance_score,
                "Technical": compliance_score.technical_controls_score,
                "Incident Response": compliance_score.incident_response_score,
                "Supply Chain": compliance_score.supply_chain_score,
                "Documentation": compliance_score.documentation_score,
                "Management": compliance_score.management_oversight_score,
            }
            for name, score in score_map.items():
                lines.append(f"- {name}: {score.score:.1f}% (weight: {score.weight:.0%})")
            lines.append("")
        
        # Devices
        lines.extend([
            "## Device Inventory",
            "",
            f"**Total Devices:** {len(devices)}",
            "",
            "| IP | Vendor | Type | Status |",
            "|----|--------|------|--------|",
        ])
        for d in devices:
            lines.append(f"| {d.ip_address} | {d.vendor or '-'} | {d.device_type or '-'} | {d.connection_status} |")
        lines.append("")
        
        # Findings
        lines.extend([
            "## Findings",
            "",
            f"**Total Findings:** {len(findings)}",
            "",
        ])
        for finding in findings:
            lines.extend([
                f"### {finding.title}",
                "",
                f"**Severity:** {finding.severity}",
                f"**Article:** {finding.nis2_article or 'N/A'}",
                "",
                f"{finding.description}",
                "",
            ])
        
        return "\n".join(lines)
    
    def _get_default_template(self) -> str:
        """Get default inline template."""
        return """# NIS2 Compliance Audit Report

**Entity:** {{ entity_name }}  
**Sector:** {{ entity_sector }}  
**Audit Date:** {{ audit_date }}  
**Session ID:** {{ session_id }}

## Executive Summary

{% if compliance_score %}
**Compliance Score:** {{ "%.1f" | format(compliance_score.overall_score) }}% - {{ compliance_score.rating }}
{% endif %}

## Device Inventory

**Total Devices:** {{ devices | length }}

{% for device in devices %}
- {{ device.ip_address }} ({{ device.vendor or 'Unknown' }} {{ device.device_type or 'Unknown' }})
{% endfor %}

## Findings

**Total Findings:** {{ findings | length }}

{% for finding in findings %}
### {{ finding.title }}

**Severity:** {{ finding.severity }}  
**Article:** {{ finding.nis2_article or 'N/A' }}

{{ finding.description }}

{% if finding.recommendation %}
**Recommendation:** {{ finding.recommendation }}
{% endif %}

---
{% endfor %}
"""
    
    def generate_json_report(
        self,
        session: AuditSession,
        devices: List[NetworkDevice],
        findings: List[AuditFinding],
        checklist_sections: List[ChecklistSection],
        compliance_score: Optional[ComplianceScore] = None,
        sanction_exposure: Optional[Dict] = None,
    ) -> str:
        """
        Generate JSON report for machine consumption.
        
        Args:
            session: Audit session
            devices: Discovered devices
            findings: Audit findings
            checklist_sections: Checklist with responses
            compliance_score: Calculated compliance score
            sanction_exposure: Sanction exposure calculation
        
        Returns:
            JSON report as string
        """
        report = {
            "report_metadata": {
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "version": "0.1.0",
                "tool": "NIS2 Field Audit App",
            },
            "entity": {
                "name": session.entity_input.legal_name,
                "sector": session.entity_input.sector,
                "classification": session.classification.model_dump() if session.classification else None,
            },
            "audit": {
                "session_id": session.session_id,
                "created_at": session.created_at.isoformat(),
                "auditor": session.auditor_name,
                "location": session.audit_location,
            },
            "devices": [self._device_to_dict(d) for d in devices],
            "compliance": {
                "overall_score": compliance_score.overall_score if compliance_score else None,
                "rating": compliance_score.rating if compliance_score else None,
                "domain_scores": self._domain_scores_to_dict(compliance_score) if compliance_score else {},
            },
            "findings": [self._finding_to_dict(f) for f in findings],
            "checklist": self._checklist_to_dict(checklist_sections),
            "sanction_exposure": sanction_exposure,
        }
        
        return json.dumps(report, indent=2, default=str)
    
    def _device_to_dict(self, device: NetworkDevice) -> Dict:
        """Convert device to dict for JSON export."""
        return {
            "device_id": device.device_id,
            "ip_address": device.ip_address,
            "hostname": device.hostname,
            "vendor": device.vendor,
            "device_type": device.device_type,
            "os_version": device.os_version,
            "connection_status": device.connection_status,
            "open_ports": device.open_ports,
            "command_count": len(device.command_results),
        }
    
    def _finding_to_dict(self, finding: AuditFinding) -> Dict:
        """Convert finding to dict for JSON export."""
        return {
            "finding_id": finding.finding_id,
            "title": finding.title,
            "description": finding.description,
            "severity": finding.severity,
            "nis2_article": finding.nis2_article,
            "nis2_domain": finding.nis2_domain,
            "evidence": finding.evidence,
            "device_ids": finding.device_ids,
            "recommendation": finding.recommendation,
            "remediation_steps": finding.remediation_steps,
            "estimated_effort": finding.estimated_effort,
            "status": finding.status,
            "created_at": finding.created_at.isoformat(),
        }
    
    def _domain_scores_to_dict(self, score: ComplianceScore) -> Dict:
        """Convert domain scores to dict."""
        return {
            "governance": self._gap_score_to_dict(score.governance_score),
            "technical_controls": self._gap_score_to_dict(score.technical_controls_score),
            "incident_response": self._gap_score_to_dict(score.incident_response_score),
            "supply_chain": self._gap_score_to_dict(score.supply_chain_score),
            "documentation": self._gap_score_to_dict(score.documentation_score),
            "management_oversight": self._gap_score_to_dict(score.management_oversight_score),
        }
    
    def _gap_score_to_dict(self, gap_score) -> Dict:
        """Convert a GapScore to dict."""
        return {"score": gap_score.score, "weight": gap_score.weight}
    
    def _checklist_to_dict(self, sections: List[ChecklistSection]) -> Dict:
        """Convert checklist to dict."""
        return {
            section.domain: {
                "title": section.title,
                "weight": section.weight,
                "questions": [
                    {
                        "id": q.id,
                        "question": q.question,
                        "status": q.status.value,
                        "nis2_article": q.nis2_article,
                        "notes": q.notes,
                    }
                    for q in section.questions
                ],
            }
            for section in sections
        }


class SanctionCalculator:
    """
    Calculate potential sanction exposure under NIS2.
    """
    
    # Fine thresholds per NIS2 Article 34
    FINE_THRESHOLDS = {
        "Essential Entity": {
            "max_amount_eur": 10_000_000,
            "max_percentage": 0.02,  # 2% of global turnover
        },
        "Important Entity": {
            "max_amount_eur": 7_000_000,
            "max_percentage": 0.014,  # 1.4% of global turnover
        },
    }
    
    def calculate_exposure(
        self,
        classification: str,
        annual_turnover: float,
        compliance_score: float,
        critical_findings: int = 0,
        high_findings: int = 0,
    ) -> Dict:
        """
        Calculate potential sanction exposure.
        
        Args:
            classification: Entity classification
            annual_turnover: Annual turnover in EUR
            compliance_score: Overall compliance score
            critical_findings: Number of critical findings
            high_findings: Number of high findings
        
        Returns:
            Dict with exposure details
        """
        # Get thresholds
        thresholds = self.FINE_THRESHOLDS.get(classification, {
            "max_amount_eur": 0,
            "max_percentage": 0.0,
        })
        
        # Calculate percentage-based fine
        percentage_fine = annual_turnover * thresholds["max_percentage"]
        
        # Maximum fine is the higher of fixed or percentage
        max_fine = max(thresholds["max_amount_eur"], percentage_fine)
        
        # Adjust based on compliance score and findings
        # Non-compliant entities (<50%) at higher risk
        # Calculate risk multiplier based on findings
        risk_multiplier = 1.0
        
        if compliance_score < 50:
            risk_multiplier += 0.5  # Non-compliant
        elif compliance_score < 75:
            risk_multiplier += 0.25  # Partially compliant
        
        # Add risk for critical/high findings
        risk_multiplier += min(critical_findings * 0.2, 1.0)  # Max +100% for critical
        risk_multiplier += min(high_findings * 0.05, 0.5)  # Max +50% for high
        
        # Cap at maximum
        potential_fine = min(max_fine * risk_multiplier, max_fine)
        
        # Determine risk level
        if potential_fine >= max_fine * 0.8:
            risk_level = "Critical"
        elif potential_fine >= max_fine * 0.5:
            risk_level = "High"
        elif potential_fine >= max_fine * 0.2:
            risk_level = "Medium"
        else:
            risk_level = "Low"
        
        return {
            "classification": classification,
            "max_amount_eur": thresholds["max_amount_eur"],
            "max_percentage": thresholds["max_percentage"],
            "percentage_fine_eur": percentage_fine,
            "potential_fine_eur": potential_fine,
            "risk_multiplier": risk_multiplier,
            "risk_level": risk_level,
            "compliance_score": compliance_score,
            "max_possible_fine": max_fine,
        }


def format_number(value: float) -> str:
    """Format number with thousand separators."""
    return f"{value:,.0f}"


# Register custom filters for Jinja2
def register_filters(env):
    """Register custom Jinja2 filters."""
    env.filters["format_number"] = format_number
