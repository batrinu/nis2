# Enforcement Officer Agent Specification

## Purpose

Calculate sanctions, generate legal notices, and determine enforcement actions for NIS2 non-compliance. Implements proportionality principles and maintains regulatory enforcement standards.

**⚠️ DISCLAIMER:** This agent identifies requirements and potential enforcement actions but does NOT provide legal advice. All enforcement decisions require human review by qualified legal professionals.

---

## Red Flag Detection

### Automatic Escalation Triggers

These conditions automatically trigger highest-priority enforcement review:

| Red Flag | Severity | Legal Basis |
|----------|----------|-------------|
| No incident response capability | Critical | Article 21(2)(b), Article 23 |
| Unencrypted sensitive data | Critical | Article 21(2)(i) |
| Missing business continuity plan | High | Article 21(2)(c) |
| Unregistered qualifying entity | High | Article 24/25 (Registration) |
| No risk assessment conducted | High | Article 21(2)(a) |
| Supply chain security absent | High | Article 21(2)(d), Article 22 |
| Significant incident unreported | Critical | Article 23(3) |
| Repeated non-compliance | Critical | Article 34 (Administrative Sanctions) |
| Obstruction of audit | Critical | Article 33(4) |
| False compliance declarations | Critical | Article 33(5) |

### Red Flag Assessment Logic

```python
class RedFlagDetector:
    FLAGS = {
        "NO_INCIDENT_RESPONSE": {
            "severity": "CRITICAL",
            "articles": ["21(2)(b)", "23"],
            "immediate_action": True,
            "base_fine_multiplier": 1.5
        },
        "UNENCRYPTED_SENSITIVE_DATA": {
            "severity": "CRITICAL", 
            "articles": ["21(2)(i)"],
            "immediate_action": True,
            "base_fine_multiplier": 1.3
        },
        "MISSING_BCP": {
            "severity": "HIGH",
            "articles": ["21(2)(c)"],
            "immediate_action": False,
            "base_fine_multiplier": 1.2
        },
        "UNREGISTERED_ENTITY": {
            "severity": "HIGH",
            "articles": ["24", "25"],
            "immediate_action": False,
            "base_fine_multiplier": 1.0
        }
    }
```

---

## Sanction Matrix

### Sanction Types

#### 1. Verbal Warning + 30-Day Window

**Applicability:**
- First-time minor non-compliance
- No immediate security risk
- Entity demonstrating cooperation

**Requirements:**
- Written record of verbal warning
- Specific remediation items
- 30-day response deadline
- Follow-up verification scheduled

#### 2. Formal Non-Compliance Notice

**Applicability:**
- Confirmed non-compliance
- Remediation possible without immediate penalty

**Content Requirements:**
- Legal basis citation
- Specific violations
- Required remediation actions
- Deadline for compliance
- Consequences of non-compliance

#### 3. Administrative Fines

**Fine Structure (Article 34):**

| Entity Type | Maximum Fine | Percentage Alternative |
|-------------|--------------|------------------------|
| Essential Entity | €10,000,000 | 2% of global turnover |
| Important Entity | €7,000,000 | 1.4% of global turnover |

**Fine Calculation Formula:**

```python
def calculate_fine(
    entity_type: str,           # "EE" or "IE"
    turnover: float,            # Global annual turnover
    severity_score: float,      # 0.0-1.0
    history_multiplier: float,  # 1.0 (first) to 3.0 (repeat)
    cooperation_factor: float,  # 0.7-1.0 (reduction for cooperation)
    cross_border_multiplier: float,  # 1.0-1.5 based on impact
    red_flag_multipliers: list[float]  # Additional multipliers
) -> dict:
    
    # Base maximum
    if entity_type == "EE":
        base_max = min(10_000_000, turnover * 0.02)
    else:
        base_max = min(7_000_000, turnover * 0.014)
    
    # Severity adjustment
    severity_multiplier = 0.3 + (severity_score * 0.7)  # 0.3-1.0
    
    # Combined multipliers
    combined_multiplier = (
        history_multiplier * 
        cooperation_factor * 
        cross_border_multiplier *
        max(red_flag_multipliers, default=1.0)
    )
    
    # Proposed fine
    proposed_fine = base_max * severity_multiplier * combined_multiplier
    
    # Cap at maximum
    final_fine = min(proposed_fine, base_max)
    
    return {
        "proposed_fine_eur": round(final_fine, 2),
        "maximum_possible": round(base_max, 2),
        "percentage_of_max": round((final_fine / base_max) * 100, 1),
        "calculation_breakdown": {...}
    }
```

#### 4. Criminal Referral Criteria

**Conditions for Criminal Referral:**
- Intentional or grossly negligent conduct
- Significant harm to public safety or national security
- Repeated willful non-compliance after formal notice
- Fraudulent compliance declarations
- Obstruction of regulatory authority

**Process:**
1. Document evidence of criminal conduct
2. Legal review by competent authority
3. Referral to prosecutorial authorities
4. Preserve evidence chain
5. Coordinate with law enforcement

#### 5. Public Disclosure Protocols

**Disclosure Triggers:**
- Non-compliance confirmed after formal process
- Public interest in disclosure
- Deterrence value
- No undue prejudice to entity

**Disclosure Content:**
- Entity name (no personal data)
- Nature of violation
- Sanction imposed
- Remediation requirements
- Timeline for compliance

**Restrictions:**
- No disclosure of technical vulnerabilities
- No disclosure of investigation methods
- Protection of trade secrets
- Consideration of ongoing incidents

#### 6. Operational Restrictions

**Available Restrictions:**
- Suspension of specific services
- Mandatory third-party security audit
- Appointment of security monitor
- Restrictions on new service offerings
- Required notification to customers/partners

**Duration:**
- Temporary (up to 12 months)
- Extended with justification (additional 12 months)
- Lifts upon demonstrated compliance

---

## Proportionality Engine

### Proportionality Calculation

```python
class ProportionalityEngine:
    """
    Implements Article 34 proportionality requirements.
    """
    
    def calculate_proportionality(
        self,
        violation: Violation,
        entity_context: EntityContext,
        history: ComplianceHistory
    ) -> ProportionalityAssessment:
        
        factors = {
            # Severity factors (0.0-1.0 each)
            "gravity": self._assess_gravity(violation),
            "duration": self._assess_duration(violation),
            "intentionality": self._assess_intentionality(violation),
            "harm_caused": self._assess_harm(violation),
            
            # Entity factors
            "size_adjustment": self._size_adjustment(entity_context),
            "cooperation": self._cooperation_score(history),
            "previous_compliance": self._compliance_history(history),
            
            # Impact factors
            "cross_border": self._cross_border_impact(violation),
            "sector_criticality": self._sector_factor(entity_context),
            "public_interest": self._public_interest_score(violation)
        }
        
        # Calculate weighted severity
        severity = self._weighted_severity(factors)
        
        # Determine sanction tier
        tier = self._determine_tier(severity, factors)
        
        return ProportionalityAssessment(
            severity_score=severity,
            sanction_tier=tier,
            factors=factors,
            reasoning=self._generate_reasoning(factors),
            legal_basis="Article 34(2) - Proportionality principles"
        )
```

### Proportionality Factors

| Factor | Weight | Assessment Criteria |
|--------|--------|---------------------|
| Gravity of violation | 25% | Impact on security, systemic risk |
| Duration of violation | 10% | Time since requirement applied |
| Intentionality | 20% | Negligent vs willful |
| Harm caused | 20% | Actual/potential damage |
| Cooperation level | 15% | Response to regulatory engagement |
| Previous compliance | 10% | History of violations |

---

## Output Templates

### Non-Compliance Report Structure

```python
class NonComplianceReport(BaseModel):
    # Executive Summary
    report_id: str
    entity_name: str
    entity_classification: str
    report_date: datetime
    competent_authority: str
    
    executive_summary: str  # Plain language summary
    criticality_rating: Literal["Critical", "High", "Medium", "Low"]
    overall_compliance_score: float
    
    # Legal Basis
    violated_articles: list[ArticleViolation]
    legal_framework: str  # NIS2 Directive reference
    national_transposition: str  # Relevant national law
    
    # Findings
    findings: list[Finding]
    evidence_references: list[EvidenceReference]
    witness_statements: list[Statement] | None
    
    # Remediation
    remediation_plan: RemediationPlan
    timeline: ComplianceTimeline
    verification_method: str
    
    # Sanctions
    proposed_sanctions: list[Sanction]
    fine_calculation: FineCalculation | None
    
    # Appeal Process
    appeal_rights: str
    appeal_deadline: date
    appeal_procedure: str
    
    # Signatures
    investigating_officer: str
    legal_review: str
    authority_head: str
```

### Remediation SMART Criteria

All remediation requirements must be:

- **S**pecific: Exact control/requirement to address
- **M**easurable: Quantifiable compliance criteria
- **A**chievable: Realistic given entity capabilities
- **R**elevant: Directly addresses the violation
- **T**ime-bound: Clear deadline with milestones

**Example:**
```yaml
remediation_item:
  id: "REM-001"
  violation: "Missing encryption for customer PII"
  article: "21(2)(i)"
  specific_requirement: "Implement AES-256 encryption for all customer PII at rest"
  measurable_criteria: "100% of customer PII fields encrypted; encryption audit passed"
  deadline: "2024-06-30"
  milestones:
    - "2024-05-15: Encryption architecture approved"
    - "2024-06-01: Implementation complete"
    - "2024-06-15: Testing and validation complete"
  verification: "Technical audit and penetration test"
```

---

## Implementation Contract

```python
class EnforcementOfficer:
    def __init__(self, config: EnforcementConfig, knowledge_base: NIS2KnowledgeBase):
        """Initialize with sanction thresholds and legal references."""
        pass
    
    def detect_red_flags(self, audit_result: AuditAssessment) -> list[RedFlag]:
        """Identify critical compliance failures requiring immediate action."""
        pass
    
    def calculate_sanctions(
        self, 
        violations: list[Violation],
        entity: EntityClassification,
        history: ComplianceHistory
    ) -> SanctionPackage:
        """Calculate appropriate sanctions based on proportionality."""
        pass
    
    def generate_notice(
        self, 
        sanction_package: SanctionPackage,
        template_type: str
    ) -> NonComplianceReport:
        """Generate legal notice with proper citations."""
        pass
    
    def assess_proportionality(
        self,
        proposed_sanction: Sanction,
        context: EnforcementContext
    ) -> ProportionalityAssessment:
        """Validate sanction against proportionality requirements."""
        pass
    
    def track_compliance_timeline(
        self,
        entity_id: str,
        remediation_plan: RemediationPlan
    ) -> ComplianceTracker:
        """Monitor remediation progress."""
        pass
    
    def escalate_criminal(
        self,
        evidence: CriminalEvidence
    ) -> CriminalReferral:
        """Generate criminal referral documentation."""
        pass
```

---

## Legal Basis Citations

All enforcement outputs must cite:

| Output Element | Required Citations |
|----------------|-------------------|
| Violation notice | Specific Article 21(2) sub-paragraphs |
| Fine calculation | Article 34(1) and (2) |
| Proportionality | Article 34(2) - factors considered |
| Cross-border coordination | Article 26 - lead authority |
| Incident reporting violations | Article 23(3) - reporting timelines |
| Registration violations | Article 24/25 - entity classification |
| Appeal rights | National transposition of Article 34(5) |

---

## Testing Requirements

1. **Fine Calculation Tests:** Verify caps, thresholds, multipliers
2. **Proportionality Tests:** Validate factor weighting
3. **Red Flag Tests:** Confirm detection accuracy
4. **Template Tests:** Verify legal citations
5. **Sample Cases:**
   - First-time minor violation (warning)
   - Repeat technical failure (moderate fine)
   - Critical security failure (maximum fine)
   - Criminal conduct (referral)
