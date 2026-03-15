"""
Finding generator for creating audit findings from gaps.
"""
from typing import Dict, List, Optional
from datetime import datetime

from ..models import AuditFinding, NetworkDevice
from .checklist import ChecklistQuestion, ComplianceStatus
from .gap_analyzer import DeviceGap


class FindingGenerator:
    """
    Generate audit findings from gaps and checklist responses.
    """
    
    # Severity mapping
    SEVERITY_MAP = {
        "critical": "critical",
        "high": "high",
        "medium": "medium",
        "low": "low",
    }
    
    # NIS2 domain to article mapping
    DOMAIN_ARTICLES = {
        "governance": "Article 21(2)(a)",
        "technical_controls": "Article 21(2)(e)",
        "incident_response": "Article 21(2)(b)",
        "supply_chain": "Article 21(2)(d)",
        "documentation": "Article 21(2)(g)",
        "management_oversight": "Article 21(2)(h)",
    }
    
    def generate_from_question(
        self,
        question: ChecklistQuestion,
        session_id: str
    ) -> Optional[AuditFinding]:
        """
        Generate finding from a checklist question if non-compliant.
        
        Args:
            question: Checklist question with response
            session_id: Audit session ID
        
        Returns:
            AuditFinding or None if compliant
        """
        # Skip if compliant or not started
        if question.status in [ComplianceStatus.COMPLIANT, ComplianceStatus.NOT_STARTED]:
            return None
        
        # Determine severity based on status
        if question.status == ComplianceStatus.NON_COMPLIANT:
            severity = "high"
        else:  # PARTIALLY_COMPLIANT
            severity = "medium"
        
        # Build description
        description = question.description or ""
        if question.notes:
            description += f"\n\nAuditor Notes: {question.notes}"
        
        evidence_parts = []
        if question.evidence_found:
            evidence_parts.append("Evidence Reviewed:")
            evidence_parts.extend(f"  - {e}" for e in question.evidence_found)
        
        if question.device_evidence:
            evidence_parts.append("\nDevice Configuration Evidence:")
            for device_id, snippet in question.device_evidence.items():
                evidence_parts.append(f"  Device {device_id}:")
                if snippet:
                    evidence_parts.append(f"    {snippet[:200]}...")
        
        evidence = "\n".join(evidence_parts) if evidence_parts else ""
        
        # Generate recommendation
        recommendation = self._generate_recommendation(question)
        
        # Generate remediation steps
        remediation_steps = self._generate_remediation_steps(question)
        
        return AuditFinding(
            session_id=session_id,
            title=f"[{question.domain.upper()}] {question.question}",
            description=description,
            severity=severity,  # type: ignore
            nis2_article=question.nis2_article,
            nis2_domain=question.domain,
            evidence=evidence,
            device_ids=list(question.device_evidence.keys()),
            config_snippets=[snippet for snippet in question.device_evidence.values() if snippet],
            recommendation=recommendation,
            remediation_steps=remediation_steps,
            estimated_effort=self._estimate_effort(question),
            created_by="audit_engine",
        )
    
    def generate_from_device_gap(
        self,
        gap: DeviceGap,
        session_id: str
    ) -> AuditFinding:
        """
        Generate finding from a device configuration gap.
        
        Args:
            gap: Device gap
            session_id: Audit session ID
        
        Returns:
            AuditFinding
        """
        severity = self.SEVERITY_MAP.get(gap.severity, "medium")
        
        return AuditFinding(
            session_id=session_id,
            title=f"[{gap.gap_type.upper()}] {gap.description[:60]}...",
            description=gap.description,
            severity=severity,  # type: ignore
            nis2_article=gap.nis2_article,
            evidence=f"Configuration issue detected:\n{gap.config_snippet or 'N/A'}",
            device_ids=[gap.device_id],
            config_snippets=[gap.config_snippet] if gap.config_snippet else [],
            recommendation=gap.remediation or "Review and remediate the identified configuration issue.",
            remediation_steps=[gap.remediation] if gap.remediation else ["Review configuration", "Apply remediation"],
            estimated_effort="1-2 days",
            created_by="gap_analyzer",
        )
    
    def generate_all_findings(
        self,
        checklist_questions: List[ChecklistQuestion],
        device_gaps: Dict[str, List[DeviceGap]],
        session_id: str
    ) -> List[AuditFinding]:
        """
        Generate all findings from questions and gaps.
        
        Args:
            checklist_questions: All checklist questions with responses
            device_gaps: Gaps identified from device analysis
            session_id: Session ID
        
        Returns:
            List of AuditFinding objects
        """
        findings = []
        findings_append = findings.append  # Local variable for faster lookup
        _generate_from_question = self.generate_from_question  # Local for faster lookup
        _generate_from_device_gap = self.generate_from_device_gap
        
        # Generate from checklist questions
        for question in checklist_questions:
            finding = _generate_from_question(question, session_id)
            if finding:
                findings_append(finding)
        
        # Generate from device gaps (if not already covered)
        for gaps in device_gaps.values():
            for gap in gaps:
                finding = _generate_from_device_gap(gap, session_id)
                findings_append(finding)
        
        return findings
    
    def _generate_recommendation(self, question: ChecklistQuestion) -> str:
        """Generate recommendation based on question."""
        recommendations = {
            "GOV-001": "Develop and formally approve cybersecurity policies. Ensure they cover risk management, access control, and incident response.",
            "GOV-002": "Establish a dedicated CISO or security officer role with clear authority and reporting lines to senior management.",
            "GOV-003": "Implement a regular risk assessment schedule (at least annually) with documented risk registers and treatment plans.",
            "GOV-004": "Create and maintain a comprehensive asset inventory including all critical network and information systems.",
            "GOV-005": "Include security requirements in all vendor contracts and conduct security assessments of critical suppliers.",
            "TECH-001": "Implement network segmentation with VLANs and DMZs to isolate critical systems from general network traffic.",
            "TECH-002": "Deploy multi-factor authentication for all privileged access accounts and administrative systems.",
            "TECH-003": "Establish a patch management program with defined SLAs for critical security updates (maximum 30 days).",
            "TECH-004": "Implement encryption for all sensitive data at rest (AES-256) and in transit (TLS 1.2+).",
            "TECH-005": "Review and harden firewall rules following least-privilege principles with default-deny policies.",
            "TECH-006": "Enable port security features including DHCP snooping and dynamic ARP inspection on all access switches.",
            "TECH-007": "Disable insecure protocols (Telnet, HTTP, SNMPv1) and enforce SSHv2 and HTTPS for all management access.",
            "IR-001": "Develop a comprehensive incident response plan with defined roles, escalation procedures, and communication protocols.",
            "IR-002": "Implement centralized logging with a SIEM solution and establish 24/7 monitoring capabilities.",
            "IR-003": "Create and test business continuity and disaster recovery plans with defined RPO and RTO targets.",
            "IR-004": "Implement automated backup solutions with regular restoration testing and secure offsite storage.",
            "IR-005": "Establish a vulnerability management program with regular scanning and defined remediation SLAs.",
            "SC-001": "Conduct security assessments of all critical vendors before onboarding and annually thereafter.",
            "SC-002": "Integrate security requirements into procurement processes and RFP documents.",
            "SC-003": "Maintain a software and hardware asset inventory with SBOMs for critical applications.",
            "DOC-001": "Document all security procedures and ensure they are regularly reviewed and updated.",
            "DOC-002": "Implement comprehensive audit logging for all security-relevant events with tamper protection.",
            "MGMT-001": "Implement regular cybersecurity awareness training for all employees with phishing simulations.",
            "MGMT-002": "Conduct background checks for all personnel in privileged roles with access to critical systems.",
            "MGMT-003": "Establish a quarterly access review process with documented attestation from data owners.",
        }
        
        return recommendations.get(
            question.id,
            f"Address the gap in {question.domain} related to {question.nis2_article}."
        )
    
    def _generate_remediation_steps(self, question: ChecklistQuestion) -> List[str]:
        """Generate remediation steps based on question."""
        steps_map = {
            "GOV-001": [
                "Draft cybersecurity policy covering risk management",
                "Obtain board/senior management approval",
                "Communicate policy to all relevant personnel",
                "Schedule annual policy review"
            ],
            "GOV-002": [
                "Define CISO role and responsibilities",
                "Establish reporting line to board/CEO",
                "Allocate budget and resources",
                "Publish role in organizational chart"
            ],
            "GOV-003": [
                "Select risk assessment methodology",
                "Identify critical assets and threats",
                "Document risks in risk register",
                "Define risk treatment plans"
            ],
            "TECH-001": [
                "Design network segmentation architecture",
                "Configure VLANs and subnetting",
                "Implement firewall rules between segments",
                "Document network topology"
            ],
            "TECH-002": [
                "Select MFA solution",
                "Deploy MFA for privileged accounts",
                "Enforce MFA for all admin access",
                "Document MFA procedures"
            ],
            "TECH-003": [
                "Implement patch management tool",
                "Define patch SLAs by severity",
                "Establish maintenance windows",
                "Track and report patch compliance"
            ],
            "IR-001": [
                "Define incident response team roles",
                "Create incident classification matrix",
                "Document response procedures",
                "Conduct tabletop exercises"
            ],
            "IR-002": [
                "Deploy centralized logging infrastructure",
                "Configure log forwarding from all systems",
                "Implement SIEM with alerting rules",
                "Establish SOC or monitoring service"
            ],
        }
        
        return steps_map.get(question.id, [
            "Assess current state vs. requirement",
            "Develop remediation plan with timeline",
            "Implement necessary controls",
            "Verify and document compliance"
        ])
    
    def _estimate_effort(self, question: ChecklistQuestion) -> str:
        """Estimate remediation effort."""
        effort_map = {
            "GOV-001": "1-2 weeks",
            "GOV-002": "2-4 weeks",
            "GOV-003": "2-3 weeks",
            "TECH-001": "2-4 weeks",
            "TECH-002": "1-2 weeks",
            "TECH-003": "2-4 weeks",
            "TECH-004": "2-6 weeks",
            "IR-001": "2-4 weeks",
            "IR-002": "4-8 weeks",
            "IR-003": "4-6 weeks",
        }
        
        return effort_map.get(question.id, "1-2 weeks")


def prioritize_findings(findings: List[AuditFinding]) -> List[AuditFinding]:
    """
    Sort findings by priority (severity and impact).
    
    Args:
        findings: List of findings
    
    Returns:
        Sorted list
    """
    severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3, "info": 4}
    
    return sorted(
        findings,
        key=lambda f: (severity_order.get(f.severity, 5), f.nis2_article or "")
    )


def get_findings_summary(findings: List[AuditFinding]) -> Dict:
    """
    Get summary statistics for findings.
    
    Args:
        findings: List of findings
    
    Returns:
        Summary dict
    """
    severity_counts = {"critical": 0, "high": 0, "medium": 0, "low": 0, "info": 0}
    domain_counts: Dict[str, int] = {}
    article_counts: Dict[str, int] = {}
    
    # Use local variables for faster attribute access
    severity_local = severity_counts
    domain_local = domain_counts
    article_local = article_counts
    
    for finding in findings:
        severity_local[finding.severity] = severity_local.get(finding.severity, 0) + 1
        domain = finding.nis2_domain
        domain_local[domain] = domain_local.get(domain, 0) + 1
        article = finding.nis2_article
        article_local[article] = article_local.get(article, 0) + 1
    
    return {
        "total": len(findings),
        "by_severity": severity_counts,
        "by_domain": domain_counts,
        "by_article": article_counts,
    }
