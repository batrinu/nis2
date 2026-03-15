"""
NIS2 Article 21 compliance checklist.
Implements the cybersecurity risk management measures checklist.
"""
import logging
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)
from enum import Enum
from dataclasses import dataclass, field


class ComplianceStatus(str, Enum):
    """Compliance status for a checklist item."""
    NOT_STARTED = "not_started"
    COMPLIANT = "compliant"
    PARTIALLY_COMPLIANT = "partially_compliant"
    NON_COMPLIANT = "non_compliant"
    NOT_APPLICABLE = "not_applicable"


@dataclass
class ChecklistOption:
    """A response option for a checklist question."""
    value: str
    label: str
    description: Optional[str] = None
    compliance_score: float = 0.0  # 0.0 to 1.0


@dataclass
class ChecklistQuestion:
    """A single question in the NIS2 checklist."""
    id: str
    question: str
    domain: str  # governance, technical_controls, incident_response, supply_chain, documentation, management_oversight
    nis2_article: str  # e.g., "21(2)(a)"
    description: Optional[str] = None
    guidance: Optional[str] = None  # Auditor guidance
    evidence_required: Optional[str] = None  # What evidence to look for
    options: List[ChecklistOption] = field(default_factory=list)
    device_correlation: Optional[str] = None  # What device config to check
    
    # Response
    status: ComplianceStatus = ComplianceStatus.NOT_STARTED
    selected_option: Optional[str] = None
    notes: str = ""
    evidence_found: List[str] = field(default_factory=list)
    device_evidence: Dict[str, str] = field(default_factory=dict)  # device_id -> config_snippet


@dataclass
class ChecklistSection:
    """A section of the NIS2 checklist (domain)."""
    domain: str
    title: str
    description: str
    weight: float  # Scoring weight
    questions: List[ChecklistQuestion] = field(default_factory=list)


# NIS2 Article 21 Checklist Data
NIS2_CHECKLIST_SECTIONS = [
    ChecklistSection(
        domain="governance",
        title="Governance & Risk Management",
        description="Risk analysis and information system security policies",
        weight=0.20,
        questions=[
            ChecklistQuestion(
                id="GOV-001",
                question="Does the entity have documented cybersecurity risk management policies?",
                domain="governance",
                nis2_article="21(2)(a)",
                description="Policies covering risk analysis and information system security",
                guidance="Look for formal policy documents, board approval, regular review dates",
                evidence_required="Policy documents, approval records, review logs",
                options=[
                    ChecklistOption("yes", "Yes - Formal policies in place", "Documented, approved, and regularly reviewed", 1.0),
                    ChecklistOption("partial", "Partial - Informal or outdated policies", "Some policies exist but not formalized or current", 0.5),
                    ChecklistOption("no", "No - No policies documented", "No formal cybersecurity policies", 0.0),
                ],
            ),
            ChecklistQuestion(
                id="GOV-002",
                question="Is there a designated security officer or CISO role?",
                domain="governance",
                nis2_article="21(2)(a)",
                description="Accountability for cybersecurity risk management",
                guidance="Check organizational chart, role description, reporting lines",
                evidence_required="Job description, org chart, responsibility matrix",
                options=[
                    ChecklistOption("yes", "Yes - Dedicated CISO or security officer", "Full-time role with clear authority", 1.0),
                    ChecklistOption("dual", "Dual-hat - Security is part-time role", "Security responsibilities assigned to another role", 0.5),
                    ChecklistOption("no", "No - No designated security role", "No clear ownership of security", 0.0),
                ],
            ),
            ChecklistQuestion(
                id="GOV-003",
                question="Are cybersecurity risks regularly assessed and documented?",
                domain="governance",
                nis2_article="21(2)(a)",
                description="Systematic risk assessment process",
                guidance="Look for risk registers, assessment reports, threat analysis",
                evidence_required="Risk assessment reports, risk register, threat intelligence",
                options=[
                    ChecklistOption("yes", "Yes - Regular formal assessments", "Annual or periodic risk assessments conducted", 1.0),
                    ChecklistOption("irregular", "Irregular assessments", "Assessments done but not on schedule", 0.5),
                    ChecklistOption("no", "No formal risk assessments", "No documented risk assessment process", 0.0),
                ],
            ),
            ChecklistQuestion(
                id="GOV-004",
                question="Is there a documented asset inventory?",
                domain="governance",
                nis2_article="21(2)(j)",
                description="Inventory of critical network and information systems",
                guidance="Check for CMDB, asset registers, network diagrams",
                evidence_required="Asset inventory, CMDB exports, network diagrams",
                device_correlation="device_inventory",
                options=[
                    ChecklistOption("yes", "Yes - Comprehensive asset inventory", "All critical assets documented and classified", 1.0),
                    ChecklistOption("partial", "Partial inventory", "Some assets documented but not complete", 0.5),
                    ChecklistOption("no", "No asset inventory", "No formal asset tracking", 0.0),
                ],
            ),
            ChecklistQuestion(
                id="GOV-005",
                question="Are security responsibilities defined for third parties?",
                domain="governance",
                nis2_article="21(2)(d)",
                description="Supply chain security governance",
                guidance="Check contracts, SLAs, security requirements for vendors",
                evidence_required="Vendor contracts, security addendums, SLA documents",
                options=[
                    ChecklistOption("yes", "Yes - Security clauses in contracts", "All vendor contracts include security requirements", 1.0),
                    ChecklistOption("some", "Some vendors covered", "Security clauses in some but not all contracts", 0.5),
                    ChecklistOption("no", "No security requirements", "No contractual security requirements", 0.0),
                ],
            ),
        ],
    ),
    
    ChecklistSection(
        domain="technical_controls",
        title="Technical & Security Controls",
        description="Technical and organizational security measures",
        weight=0.25,
        questions=[
            ChecklistQuestion(
                id="TECH-001",
                question="Are network segments properly isolated (VLANs, DMZs)?",
                domain="technical_controls",
                nis2_article="21(2)(j)",
                description="Network segmentation and access control",
                guidance="Review network diagrams, VLAN configs, firewall rules",
                evidence_required="Network diagrams, VLAN configs, firewall rules",
                device_correlation="show_vlan_brief,show_access-lists",
                options=[
                    ChecklistOption("yes", "Yes - Properly segmented", "Critical systems isolated in separate VLANs/DMZs", 1.0),
                    ChecklistOption("partial", "Partial segmentation", "Some segmentation but not comprehensive", 0.5),
                    ChecklistOption("no", "No segmentation", "Flat network with no isolation", 0.0),
                ],
            ),
            ChecklistQuestion(
                id="TECH-002",
                question="Is multi-factor authentication (MFA) enforced for privileged access?",
                domain="technical_controls",
                nis2_article="21(2)(k)",
                description="Strong authentication for administrative access",
                guidance="Check AAA config, MFA solutions, privileged access management",
                evidence_required="AAA configuration, MFA logs, PAM solution",
                device_correlation="show_aaa_sessions,show_users",
                options=[
                    ChecklistOption("yes", "Yes - MFA for all privileged access", "MFA enforced for admin accounts", 1.0),
                    ChecklistOption("partial", "MFA for some systems", "MFA on some but not all admin access", 0.5),
                    ChecklistOption("no", "No MFA", "Single-factor authentication only", 0.0),
                ],
            ),
            ChecklistQuestion(
                id="TECH-003",
                question="Are security patches applied in a timely manner?",
                domain="technical_controls",
                nis2_article="21(2)(e)",
                description="Patch management for vulnerabilities",
                guidance="Check patch levels, security advisories, change records",
                evidence_required="Patch management records, system versions, change logs",
                device_correlation="show_version",
                options=[
                    ChecklistOption("yes", "Yes - Regular patching within SLA", "Critical patches applied within 30 days", 1.0),
                    ChecklistOption("delayed", "Delayed patching", "Patches applied but with delays", 0.5),
                    ChecklistOption("no", "No patch management", "Systems significantly out of date", 0.0),
                ],
            ),
            ChecklistQuestion(
                id="TECH-004",
                question="Is encryption used for sensitive data at rest and in transit?",
                domain="technical_controls",
                nis2_article="21(2)(i)",
                description="Cryptographic protection measures",
                guidance="Check TLS versions, disk encryption, VPN configs",
                evidence_required="Crypto configurations, certificate inventory, encryption policies",
                device_correlation="show_crypto_isakmp_sa",
                options=[
                    ChecklistOption("yes", "Yes - Strong encryption everywhere", "TLS 1.2+, AES encryption, proper key management", 1.0),
                    ChecklistOption("partial", "Partial encryption", "Some encryption but gaps remain", 0.5),
                    ChecklistOption("no", "Weak or no encryption", "Legacy protocols, weak ciphers", 0.0),
                ],
            ),
            ChecklistQuestion(
                id="TECH-005",
                question="Are firewalls and ACLs properly configured?",
                domain="technical_controls",
                nis2_article="21(2)(j)",
                description="Network access control measures",
                guidance="Review firewall rules, ACLs, default-deny policies",
                evidence_required="Firewall configs, ACL documentation, rule review records",
                device_correlation="show_access-lists,iptables -L",
                options=[
                    ChecklistOption("yes", "Yes - Least privilege, default deny", "Well-configured rules, regular reviews", 1.0),
                    ChecklistOption("overpermissive", "Overly permissive rules", "Rules exist but allow excessive access", 0.5),
                    ChecklistOption("no", "No firewall/ACLs", "No network access controls", 0.0),
                ],
            ),
            ChecklistQuestion(
                id="TECH-006",
                question="Is port security enabled on access switches?",
                domain="technical_controls",
                nis2_article="21(2)(j)",
                description="Physical/edge port protection",
                guidance="Check port security, DHCP snooping, dynamic ARP inspection",
                evidence_required="Port security configs, DHCP snooping status",
                device_correlation="show_port-security,show_ip_dhcp_snooping",
                options=[
                    ChecklistOption("yes", "Yes - Port security enabled", "Port security, DHCP snooping, DAI active", 1.0),
                    ChecklistOption("partial", "Partial protection", "Some security features enabled", 0.5),
                    ChecklistOption("no", "No port security", "No layer 2 security controls", 0.0),
                ],
            ),
            ChecklistQuestion(
                id="TECH-007",
                question="Are secure protocols used for management access?",
                domain="technical_controls",
                nis2_article="21(2)(k)",
                description="SSH vs Telnet, HTTPS vs HTTP",
                guidance="Check management protocols, SSH versions, cipher suites",
                evidence_required="SSH config, management ACLs, protocol inventory",
                device_correlation="show_ip_ssh,cat /etc/ssh/sshd_config",
                options=[
                    ChecklistOption("yes", "Yes - SSHv2, HTTPS only", "No cleartext protocols, strong ciphers", 1.0),
                    ChecklistOption("mixed", "Mixed protocols", "Some secure, some legacy protocols", 0.5),
                    ChecklistOption("no", "Cleartext protocols", "Telnet, HTTP, SNMPv1 in use", 0.0),
                ],
            ),
        ],
    ),
    
    ChecklistSection(
        domain="incident_response",
        title="Incident Response & Business Continuity",
        description="Detection, response, and recovery capabilities",
        weight=0.20,
        questions=[
            ChecklistQuestion(
                id="IR-001",
                question="Is there a documented incident response plan?",
                domain="incident_response",
                nis2_article="21(2)(b)",
                description="Procedures for handling security incidents",
                guidance="Look for IRP, contact lists, escalation procedures",
                evidence_required="Incident response plan, contact lists, playbooks",
                options=[
                    ChecklistOption("yes", "Yes - Comprehensive IRP", "Documented plan with roles and procedures", 1.0),
                    ChecklistOption("basic", "Basic plan", "Simple plan but not comprehensive", 0.5),
                    ChecklistOption("no", "No incident response plan", "No documented incident procedures", 0.0),
                ],
            ),
            ChecklistQuestion(
                id="IR-002",
                question="Are security events logged and monitored?",
                domain="incident_response",
                nis2_article="21(2)(b)",
                description="Security monitoring and detection",
                guidance="Check SIEM, log aggregation, alerting thresholds",
                evidence_required="Logging configs, SIEM dashboards, alert rules",
                device_correlation="show_logging,cat /etc/rsyslog.conf",
                options=[
                    ChecklistOption("yes", "Yes - Centralized logging with monitoring", "SIEM in place with active monitoring", 1.0),
                    ChecklistOption("logging", "Logging only", "Logs collected but not actively monitored", 0.5),
                    ChecklistOption("no", "No centralized logging", "No security event logging", 0.0),
                ],
            ),
            ChecklistQuestion(
                id="IR-003",
                question="Is there a business continuity/disaster recovery plan?",
                domain="incident_response",
                nis2_article="21(2)(c)",
                description="Recovery procedures and backup strategy",
                guidance="Check BCP, DR plans, backup schedules, tested procedures",
                evidence_required="BCP/DR plans, backup logs, test results",
                options=[
                    ChecklistOption("yes", "Yes - Tested BCP/DR plans", "Regular testing, current documentation", 1.0),
                    ChecklistOption("documented", "Documented but not tested", "Plans exist but not regularly tested", 0.5),
                    ChecklistOption("no", "No BCP/DR plan", "No recovery procedures documented", 0.0),
                ],
            ),
            ChecklistQuestion(
                id="IR-004",
                question="Are backups performed regularly and tested?",
                domain="incident_response",
                nis2_article="21(2)(c)",
                description="Data backup and recovery testing",
                guidance="Check backup schedules, retention, restoration tests",
                evidence_required="Backup logs, restore test results, retention policy",
                options=[
                    ChecklistOption("yes", "Yes - Regular backups with testing", "Automated backups, periodic restore tests", 1.0),
                    ChecklistOption("backups", "Backups without testing", "Backups performed but not tested", 0.5),
                    ChecklistOption("no", "No backup strategy", "Irregular or no backups", 0.0),
                ],
            ),
            ChecklistQuestion(
                id="IR-005",
                question="Is there a vulnerability management process?",
                domain="incident_response",
                nis2_article="21(2)(f)",
                description="Vulnerability handling and disclosure",
                guidance="Check vulnerability scanning, remediation SLAs, bug bounty",
                evidence_required="Vulnerability reports, scan schedules, remediation records",
                options=[
                    ChecklistOption("yes", "Yes - Regular scanning and remediation", "Quarterly scans, defined SLAs", 1.0),
                    ChecklistOption("irregular", "Irregular scanning", "Scans done but not on schedule", 0.5),
                    ChecklistOption("no", "No vulnerability management", "No scanning program", 0.0),
                ],
            ),
        ],
    ),
    
    ChecklistSection(
        domain="supply_chain",
        title="Supply Chain Security",
        description="Third-party and supply chain risk management",
        weight=0.15,
        questions=[
            ChecklistQuestion(
                id="SC-001",
                question="Are critical vendors assessed for security risks?",
                domain="supply_chain",
                nis2_article="21(2)(d)",
                description="Vendor security assessments",
                guidance="Check vendor questionnaires, security assessments, audits",
                evidence_required="Vendor assessments, security questionnaires, audit reports",
                options=[
                    ChecklistOption("yes", "Yes - All critical vendors assessed", "Security assessments for key suppliers", 1.0),
                    ChecklistOption("some", "Some vendors assessed", "Assessments for some but not all", 0.5),
                    ChecklistOption("no", "No vendor assessments", "No security evaluation of suppliers", 0.0),
                ],
            ),
            ChecklistQuestion(
                id="SC-002",
                question="Are security requirements in procurement processes?",
                domain="supply_chain",
                nis2_article="21(2)(d)",
                description="Security in acquisition and development",
                guidance="Check procurement policies, security requirements in RFPs",
                evidence_required="Procurement policies, RFP templates, security requirements",
                options=[
                    ChecklistOption("yes", "Yes - Security in procurement", "Security requirements standard in RFPs", 1.0),
                    ChecklistOption("partial", "Partial integration", "Security considered for some purchases", 0.5),
                    ChecklistOption("no", "No security in procurement", "No security considerations in purchasing", 0.0),
                ],
            ),
            ChecklistQuestion(
                id="SC-003",
                question="Is there a software/hardware asset inventory?",
                domain="supply_chain",
                nis2_article="21(2)(d)",
                description="Tracking of ICT products and services",
                guidance="Check SBOMs, license management, end-of-life tracking",
                evidence_required="Software inventory, SBOMs, EOL tracking",
                options=[
                    ChecklistOption("yes", "Yes - Complete inventory with SBOMs", "Software bill of materials maintained", 1.0),
                    ChecklistOption("partial", "Basic inventory", "Asset list but no SBOMs", 0.5),
                    ChecklistOption("no", "No inventory", "Unknown software/hardware assets", 0.0),
                ],
            ),
        ],
    ),
    
    ChecklistSection(
        domain="documentation",
        title="Documentation & Audit",
        description="Security documentation and audit trails",
        weight=0.10,
        questions=[
            ChecklistQuestion(
                id="DOC-001",
                question="Are security procedures documented?",
                domain="documentation",
                nis2_article="21(2)(g)",
                description="Assessment of security measure effectiveness",
                guidance="Check procedure documents, work instructions, standards",
                evidence_required="Procedure documents, standards, guidelines",
                options=[
                    ChecklistOption("yes", "Yes - Comprehensive documentation", "Procedures documented and maintained", 1.0),
                    ChecklistOption("partial", "Partial documentation", "Some procedures documented", 0.5),
                    ChecklistOption("no", "No documentation", "No written security procedures", 0.0),
                ],
            ),
            ChecklistQuestion(
                id="DOC-002",
                question="Is there audit logging of security-relevant events?",
                domain="documentation",
                nis2_article="21(2)(g)",
                description="Audit trail for accountability",
                guidance="Check audit logs, log retention, tamper protection",
                evidence_required="Audit configurations, log samples, retention policies",
                device_correlation="auditctl -l",
                options=[
                    ChecklistOption("yes", "Yes - Comprehensive audit logging", "Security events logged, logs protected", 1.0),
                    ChecklistOption("basic", "Basic logging", "Some events logged but not comprehensive", 0.5),
                    ChecklistOption("no", "No audit logging", "No security audit trail", 0.0),
                ],
            ),
        ],
    ),
    
    ChecklistSection(
        domain="management_oversight",
        title="Management Oversight & Training",
        description="Human resources security and training",
        weight=0.10,
        questions=[
            ChecklistQuestion(
                id="MGMT-001",
                question="Is cybersecurity awareness training provided?",
                domain="management_oversight",
                nis2_article="21(2)(h)",
                description="Cyber hygiene and training programs",
                guidance="Check training records, phishing simulations, content",
                evidence_required="Training records, course content, completion rates",
                options=[
                    ChecklistOption("yes", "Yes - Regular training for all", "Annual training, phishing tests", 1.0),
                    ChecklistOption("partial", "Training for some roles", "IT staff trained, general staff not", 0.5),
                    ChecklistOption("no", "No security training", "No awareness program", 0.0),
                ],
            ),
            ChecklistQuestion(
                id="MGMT-002",
                question="Are background checks performed for privileged roles?",
                domain="management_oversight",
                nis2_article="21(2)(j)",
                description="HR security and access control",
                guidance="Check hiring procedures, background check policy",
                evidence_required="HR policies, background check records",
                options=[
                    ChecklistOption("yes", "Yes - For all privileged roles", "Background checks for admins, security staff", 1.0),
                    ChecklistOption("partial", "Some roles only", "Checks for some but not all sensitive roles", 0.5),
                    ChecklistOption("no", "No background checks", "No screening for privileged access", 0.0),
                ],
            ),
            ChecklistQuestion(
                id="MGMT-003",
                question="Is there an access review process?",
                domain="management_oversight",
                nis2_article="21(2)(j)",
                description="Regular review of access rights",
                guidance="Check access review schedules, attestation records",
                evidence_required="Access review records, attestation emails",
                options=[
                    ChecklistOption("yes", "Yes - Quarterly or better", "Regular access reviews with documentation", 1.0),
                    ChecklistOption("annual", "Annual reviews", "Yearly access review process", 0.5),
                    ChecklistOption("no", "No access reviews", "No review of user access rights", 0.0),
                ],
            ),
        ],
    ),
]


def get_checklist_sections() -> List[ChecklistSection]:
    """Get the full NIS2 checklist sections."""
    return NIS2_CHECKLIST_SECTIONS


def get_all_questions() -> List[ChecklistQuestion]:
    """Get all questions flattened into a single list."""
    return [q for section in NIS2_CHECKLIST_SECTIONS for q in section.questions]


def get_question_by_id(question_id: str) -> Optional[ChecklistQuestion]:
    """Get a specific question by ID."""
    return next(
        (q for section in NIS2_CHECKLIST_SECTIONS for q in section.questions if q.id == question_id),
        None
    )


def get_questions_by_domain(domain: str) -> List[ChecklistQuestion]:
    """Get all questions for a specific domain."""
    return [q for section in NIS2_CHECKLIST_SECTIONS if section.domain == domain for q in section.questions]


def calculate_domain_weight(domain: str) -> float:
    """Get the weight for a specific domain."""
    return next(
        (section.weight for section in NIS2_CHECKLIST_SECTIONS if section.domain == domain),
        0.0
    )
