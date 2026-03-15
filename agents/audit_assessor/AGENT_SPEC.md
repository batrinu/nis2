# Audit Assessor Agent Specification

## Purpose

Execute comprehensive 5-phase audit methodology for NIS2 compliance assessment, evaluating entities against Article 21 security requirements and related provisions.

## Audit Phases Overview

```
Phase 1: Entity Classification → delegates to Entity Classifier Agent
Phase 2: Documentation Review
Phase 3: Technical Assessment
Phase 4: Interview Simulation
Phase 5: Compliance Scoring
```

---

## Phase 1: Entity Classification

### Delegation Contract

**Input:** Raw entity data (sector, size, operations)
**Output:** `EntityClassification` object
**Action:** Store classification in audit context, proceed only if qualifying entity

**Early Exit Conditions:**
- Non-qualifying entity: Audit not required, generate advisory report
- Classification confidence < 0.70: Escalate to manual review before proceeding

---

## Phase 2: Documentation Review

### Scope

Evaluate documentation against Article 21 and sector-specific requirements.

### Review Categories

#### 2.1 Information Security Management System (ISMS)

**ISO 27001 Alignment Check:**
| Control Area | Required Evidence | NIS2 Mapping |
|--------------|-------------------|--------------|
| Risk Assessment | Risk register, methodology document | Article 21(2)(a) |
| Security Policy | Approved policy document | Article 21(2)(b) |
| Access Control | IAM policies, privilege matrix | Article 21(2)(d) |
| Cryptography | Encryption standards, key management | Article 21(2)(e) |
| Physical Security | Facility security procedures | Article 21(2)(f) |
| Operations Security | Change management, logging | Article 21(2)(g) |
| Incident Management | Response procedures, playbooks | Article 21(2)(h) |
| Business Continuity | BCP/DR plans, RTO/RPO definitions | Article 21(2)(i) |

**Scoring:**
- Document present and approved: +10 points per area
- Document present but outdated: +5 points
- Document missing: 0 points
- Evidence of implementation: +5 bonus points

#### 2.2 Risk Management Documentation

**Required Artifacts:**
1. Cybersecurity risk assessment (last 12 months)
2. Risk treatment plan with owners and deadlines
3. Residual risk acceptance records
4. Supply chain risk register
5. Third-party risk assessment methodology

**Evaluation Criteria:**
```python
RISK_REGISTER_SCORE = min(100, sum([
    assessment_completeness * 25,      # 0-25 points
    risk_coverage_breadth * 25,        # 0-25 points
    treatment_plan_quality * 25,       # 0-25 points
    review_frequency_compliance * 25   # 0-25 points
]))
```

#### 2.3 Policy Framework

**Mandatory Policies (Article 21):**
- Information Security Policy
- Access Control Policy
- Cryptographic Controls Policy
- Asset Management Policy
- Incident Response Policy
- Business Continuity/Disaster Recovery Policy
- Supply Chain Security Policy
- Human Resources Security Policy

**Policy Quality Metrics:**
- Executive approval and date
- Review cycle defined (annual minimum)
- Distribution and acknowledgment records
- Version control and change history

---

## Phase 3: Technical Assessment

### 3.1 Vulnerability Management

**Assessment Areas:**

| Control | Validation Method | Pass Criteria |
|---------|-------------------|---------------|
| Asset inventory | Tool output review | 95%+ coverage |
| Vulnerability scanning | Scan configuration review | Weekly minimum |
| Patch management | Patch cycle documentation | Critical: 7 days, High: 30 days |
| Penetration testing | Test reports review | Annual minimum |
| Threat intelligence | Integration evidence | Active feeds |

**Evidence Collection:**
- Last 3 vulnerability scan reports
- Asset inventory export (sanitized)
- Patch management metrics (MTTR by severity)
- Penetration test findings and remediation status

### 3.2 Encryption Verification

**Data Classification Required:**
- Personal data (GDPR intersection)
- Financial data
- Authentication credentials
- Sensitive business data
- System configuration data

**Encryption Standards:**
| Data State | Minimum Standard | Validation |
|------------|------------------|------------|
| At rest | AES-256 | Configuration audit |
| In transit | TLS 1.2+ | Protocol scan |
| In use | Confidential computing | Architecture review |

**Key Management Verification:**
- HSM or equivalent key protection
- Key rotation procedures
- Access segregation (encrypt vs decrypt)
- Key escrow/backup procedures

### 3.3 Network Segmentation

**Architecture Review:**
```
Perimeter → DMZ → Internal Zones → Critical Assets
    ↓           ↓           ↓             ↓
  Firewall   WAF/IPS    Micro-seg      Zero Trust
```

**Validation Checklist:**
- [ ] Network diagrams current and accurate
- [ ] Segmentation between IT/OT (if applicable)
- [ ] Critical asset isolation verified
- [ ] Lateral movement prevention tested
- [ ] Default deny policies in place
- [ ] Inter-zone traffic logging enabled

### 3.4 Identity and Access Management

**Controls Assessment:**
| Control | Evidence Required | Compliance Threshold |
|---------|-------------------|----------------------|
| MFA enforcement | Policy + config | 100% admin, 95% user |
| Privileged access | PAM tool review | Vaulted, rotated |
| Least privilege | Access review logs | Quarterly review |
| Account lifecycle | HR/IT integration | Auto-provisioning |
| Service accounts | Inventory + rotation | 90-day max age |

---

## Phase 4: Interview Simulation

### 4.1 CISO Competency Assessment

**Interview Topics:**

**Strategic Knowledge:**
1. "Describe your cybersecurity strategy and how it aligns with NIS2 Article 21"
2. "What metrics do you report to the board and how frequently?"
3. "Explain your incident escalation procedures for significant incidents"

**Operational Knowledge:**
4. "Walk me through your last tabletop exercise"
5. "How do you validate the effectiveness of your security controls?"
6. "Describe your supply chain risk management approach"

**Regulatory Knowledge:**
7. "What constitutes a 'significant incident' under NIS2 Article 23?"
8. "Explain your reporting timeline to the competent authority"
9. "How do you handle cross-border incident coordination?"

**Scoring Rubric:**
| Response Level | Score | Criteria |
|----------------|-------|----------|
| Expert | 10 | Detailed, accurate, demonstrates practical experience |
| Proficient | 7 | Correct understanding, minor gaps |
| Basic | 4 | General awareness, lacks detail |
| Inadequate | 1 | Incorrect or unaware |

### 4.2 Board Accountability Check

**Interview Questions for Board/Executive:**

1. "Who has ultimate accountability for cybersecurity risk?"
2. "How frequently does the board review cybersecurity matters?"
3. "What is the board's understanding of NIS2 compliance obligations?"
4. "Describe the budget approval process for security investments"
5. "How are cybersecurity risks integrated into enterprise risk management?"

**Accountability Indicators:**
- Board-approved cybersecurity strategy: +10
- Defined risk appetite statement: +10
- Regular board reporting (quarterly+): +10
- Board-level risk register inclusion: +10
- Incident notification to board defined: +10

---

## Phase 5: Compliance Scoring

### Weighted Scoring Algorithm

```python
COMPLIANCE_DOMAINS = {
    "governance": {
        "weight": 0.20,
        "components": {
            "board_accountability": 0.30,
            "risk_management_framework": 0.25,
            "policy_framework": 0.25,
            "roles_responsibilities": 0.20
        }
    },
    "technical_controls": {
        "weight": 0.25,
        "components": {
            "access_control": 0.20,
            "cryptography": 0.20,
            "network_security": 0.20,
            "vulnerability_management": 0.20,
            "monitoring_logging": 0.20
        }
    },
    "incident_response": {
        "weight": 0.20,
        "components": {
            "detection_capability": 0.30,
            "response_procedures": 0.30,
            "reporting_mechanisms": 0.20,
            "lessons_learned": 0.20
        }
    },
    "supply_chain": {
        "weight": 0.15,
        "components": {
            "supplier_assessment": 0.30,
            "contractual_security": 0.25,
            "monitoring_auditing": 0.25,
            "incident_coordination": 0.20
        }
    },
    "documentation": {
        "weight": 0.10,
        "components": {
            "completeness": 0.40,
            "currency": 0.30,
            "approval_process": 0.30
        }
    },
    "management_oversight": {
        "weight": 0.10,
        "components": {
            "ciso_competency": 0.40,
            "resource_allocation": 0.30,
            "training_awareness": 0.30
        }
    }
}

def calculate_compliance_score(assessment_results: dict) -> dict:
    """
    Calculate weighted compliance score across all domains.
    Returns overall score and domain breakdown.
    """
    pass
```

### Rating Scale

| Rating | Score Range | Description |
|--------|-------------|-------------|
| **Compliant** | 90-100% | Fully meets Article 21 requirements, minor improvements optional |
| **Substantially Compliant** | 75-89% | Generally compliant, specific remediation required |
| **Partially Compliant** | 50-74% | Significant gaps, formal remediation plan required |
| **Non-Compliant** | <50% | Material failures, immediate action and potential enforcement |

### Article 21 Requirement Mapping

| Article 21(2) Requirement | Assessment Phase | Domain Weight |
|---------------------------|------------------|---------------|
| (a) Risk analysis and security policies | Phase 2, Phase 4 | Governance 20%, Documentation 10% |
| (b) Incident handling | Phase 2, Phase 3, Phase 4 | Incident Response 20% |
| (c) Business continuity | Phase 2 | Technical Controls 25% |
| (d) Supply chain security | Phase 2, Phase 4 | Supply Chain 15% |
| (e) Security in acquisition/development | Phase 3 | Technical Controls 25% |
| (f) Vulnerability handling and disclosure | Phase 3 | Technical Controls 25% |
| (g) Assessment of effectiveness | Phase 3, Phase 4 | Management Oversight 10% |
| (h) Basic cyber hygiene and training | Phase 4 | Management Oversight 10% |
| (i) Cryptography and encryption | Phase 3 | Technical Controls 25% |
| (j) Human resources security | Phase 2 | Governance 20% |
| (k) Multi-factor authentication | Phase 3 | Technical Controls 25% |
| (l) Secured communications | Phase 3 | Technical Controls 25% |
| (m) Emergency plans | Phase 2 | Incident Response 20% |
| (n) Environmental control | Phase 2 | Technical Controls 25% |

---

## Output Schema

```python
class AuditAssessment(BaseModel):
    audit_id: str
    entity_id: str
    timestamp: datetime
    auditor_reference: str
    
    phase_results: dict[str, PhaseResult]
    
    overall_score: float
    rating: Literal["Compliant", "Substantially Compliant", "Partially Compliant", "Non-Compliant"]
    
    domain_scores: dict[str, DomainScore]
    
    findings: list[Finding]
    recommendations: list[Recommendation]
    
    article_21_mapping: dict[str, ComplianceStatus]
    
    cross_border_coordination: CrossBorderInfo | None
    
    next_audit_date: date
    evidence_references: list[str]
```

---

## Implementation Contract

```python
class AuditAssessor:
    def __init__(self, classifier: EntityClassifier, config: AuditConfig):
        """Initialize with classifier agent and audit configuration."""
        pass
    
    def execute_audit(self, entity_data: EntityInput, mode: str) -> AuditAssessment:
        """
        Execute full 5-phase audit.
        Mode: 'full' | 'targeted' | 'follow-up'
        """
        pass
    
    def _phase_1_classification(self, entity_data: EntityInput) -> EntityClassification:
        """Delegate to Entity Classifier Agent."""
        pass
    
    def _phase_2_documentation_review(self, documents: DocumentBundle) -> Phase2Result:
        """Evaluate ISMS alignment and policy framework."""
        pass
    
    def _phase_3_technical_assessment(self, technical_evidence: TechnicalBundle) -> Phase3Result:
        """Assess technical controls and vulnerabilities."""
        pass
    
    def _phase_4_interview_simulation(self, interview_data: InterviewBundle) -> Phase4Result:
        """Evaluate CISO competency and board accountability."""
        pass
    
    def _phase_5_compliance_scoring(self, phase_results: list) -> AuditAssessment:
        """Calculate final scores and generate findings."""
        pass
    
    def generate_checklist(self, entity_type: str) -> list[str]:
        """Generate pre-audit checklist based on entity classification."""
        pass
```

---

## Phase Modules Structure

```
agents/audit-assessor/phases/
├── __init__.py
├── phase1_classification.py    # Entity classification delegation
├── phase2_documentation.py     # ISMS and policy review
├── phase3_technical.py         # Technical controls assessment
├── phase4_interviews.py        # Competency evaluation
├── phase5_scoring.py           # Compliance calculation
└── checklists.py               # Article 21 requirement checklists
```

---

## Legal Basis Citations

All findings must cite specific NIS2 Articles:

| Finding Category | Legal Citation |
|------------------|----------------|
| Risk management failure | "Article 21(2)(a) - Risk analysis and information system security policies" |
| Incident response gap | "Article 21(2)(b) - Incident handling" |
| Business continuity failure | "Article 21(2)(c) - Business continuity and crisis management" |
| Supply chain weakness | "Article 21(2)(d) - Supply chain security" |
| Cryptography failure | "Article 21(2)(i) - Use of cryptography and encryption" |
| Access control failure | "Article 21(2)(k) - Multi-factor authentication" |

---

## Testing Requirements

1. **Phase Tests:** Each phase independently testable
2. **Integration Tests:** Full audit workflow
3. **Scoring Validation:** Verify rating thresholds
4. **Sample Audits:**
   - Compliant entity (score 90+)
   - Substantially compliant (score 75-89)
   - Partially compliant (score 50-74)
   - Non-compliant (score <50)
