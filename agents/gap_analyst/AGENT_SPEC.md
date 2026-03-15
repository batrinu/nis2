# Gap Analyst Agent Specification

## Purpose

Conduct pre-audit readiness evaluation and consulting preparation, identifying compliance gaps before formal audit and providing prioritized remediation guidance.

## Assessment Modes

### Mode 1: Quick Scan

**Purpose:** High-level maturity assessment for initial readiness evaluation

**Duration:** 30-60 minutes

**Scope:**
- Executive-level questionnaire (10-15 questions)
- Document existence checks
- Policy framework overview
- High-risk area identification

**Output:**
- Maturity score (1-5 scale)
- Risk heat map
- Priority areas for deep dive
- Estimated audit readiness timeline

### Mode 2: Deep Dive

**Purpose:** Article-by-article compliance gap analysis

**Duration:** 2-4 hours

**Scope:**
- Comprehensive questionnaire (50+ questions)
- Detailed evidence review
- Technical control validation
- Process maturity assessment
- Staff competency evaluation

**Output:**
- Detailed gap analysis report
- Compliance percentage by Article
- Prioritized remediation roadmap
- Resource estimates
- Timeline to compliance

---

## Compliance Domains

### Domain 1: Article 21 - Governance and Security Measures

**Assessment Areas:**

| Requirement | Quick Scan | Deep Dive |
|-------------|------------|-----------|
| Risk analysis (21(2)(a)) | Policy existence | Methodology, coverage, review cycle |
| Security policies (21(2)(a)) | Framework presence | Detailed policy review |
| Incident handling (21(2)(b)) | Plan existence | Capabilities, testing, metrics |
| Business continuity (21(2)(c)) | BCP existence | RTO/RPO, testing, dependencies |
| Supply chain security (21(2)(d)) | Awareness | Contracts, assessments, monitoring |
| Acquisition/development (21(2)(e)) | Awareness | SDLC, security requirements |
| Vulnerability handling (21(2)(f)) | Process existence | Disclosure, patch management |
| Effectiveness assessment (21(2)(g)) | Metrics existence | KPIs, review cycles |
| Basic cyber hygiene (21(2)(h)) | Training existence | Program details, coverage |
| Cryptography (21(2)(i)) | Policy existence | Implementation, key management |
| HR security (21(2)(j)) | Policy existence | Background checks, exit procedures |
| MFA (21(2)(k)) | Implementation | Coverage, exceptions |
| Communications security (21(2)(l)) | Policy existence | Implementation details |
| Emergency plans (21(2)(m)) | Plan existence | Testing, coordination |
| Environmental control (21(2)(n)) | Awareness | Physical security, redundancy |

### Domain 2: Article 23 - Incident Reporting

**Assessment Areas:**

| Aspect | Evaluation Criteria |
|--------|---------------------|
| Significant incident definition | Entity understands thresholds |
| Detection capabilities | SIEM, monitoring, alerting |
| Early warning (24h) | Process for immediate assessment |
| Intermediate report (72h) | Template, information sources |
| Final report (1 month) | Root cause, remediation |
| CSIRT cooperation | Contact procedures, coordination |
| Cross-border notification | Multi-authority processes |

**Significant Incident Thresholds:**
- Economic impact: €1,000,000+ loss
- User impact: 100,000+ users affected
- Duration: 12+ hours of service unavailability
- Data impact: Personal data of 100,000+ individuals
- National security implications

### Domain 3: Article 22 - Supply Chain Security

**Assessment Areas:**

| Control | Maturity Levels |
|---------|-----------------|
| Supplier inventory | 1: Ad-hoc → 5: Automated, comprehensive |
| Risk assessment | 1: No assessment → 5: Continuous monitoring |
| Contractual security | 1: Generic clauses → 5: Tailored, enforced |
| Security verification | 1: Self-attestation → 5: Third-party audit |
| Incident coordination | 1: No plan → 5: Joint exercises |

### Domain 4: Articles 24-26 - Registration

**Assessment Areas:**

- Entity classification accuracy
- Registration with competent authority
- Information currency
- Cross-border coordination (if applicable)
- Lead authority identification

---

## Sample Questions Bank

### Governance Questions (Q1-Q5)

**Q1: Board Accountability**
> "Is there a board member or senior executive with explicit accountability for cybersecurity risk?"

- Score 5: Named C-suite owner, board reporting quarterly+
- Score 3: Named owner, reports annually
- Score 1: No clear ownership

**Q2: Risk Management**
> "When was your last comprehensive cybersecurity risk assessment conducted?"

- Score 5: Within 6 months, methodology documented
- Score 3: Within 12 months
- Score 1: Over 12 months or no assessment

**Q3: Policy Framework**
> "How many of the following policies do you have documented and approved?"
> (Security, Access Control, Incident Response, BCP, Cryptography, Supply Chain)

- Score 5: All 6 current and approved
- Score 3: 4-5 policies
- Score 1: <4 policies

**Q4: Budget**
> "What percentage of IT budget is allocated to cybersecurity?"

- Score 5: Industry benchmark (typically 10-15%)
- Score 3: Below benchmark but defined
- Score 1: No defined budget

**Q5: Training**
> "Describe your security awareness training program."

- Score 5: Mandatory, annual, role-based, tested
- Score 3: Annual general training
- Score 1: Ad-hoc or no training

### Technical Questions (Q6-Q10)

**Q6: Vulnerability Management**
> "Provide your vulnerability scanning frequency and average time to remediate critical vulnerabilities."

- Score 5: Continuous scanning, <7 days MTTR
- Score 3: Weekly scanning, <30 days MTTR
- Score 1: Monthly or less, >30 days MTTR

**Q7: Penetration Testing**
> "Show evidence of your last penetration test and remediation status."

- Score 5: Annual external test, all criticals remediated
- Score 3: Annual test, some open findings
- Score 1: No recent test

**Q8: Encryption**
> "What encryption standards are applied to sensitive data at rest and in transit?"

- Score 5: AES-256 at rest, TLS 1.3 in transit, HSM for keys
- Score 3: Industry standard encryption
- Score 1: Weak or no encryption

**Q9: MFA**
> "What percentage of users and administrative accounts have MFA enforced?"

- Score 5: 100% admin, >95% users
- Score 3: 100% admin, <95% users
- Score 1: Partial or no MFA

**Q10: Logging**
> "Describe your security logging and monitoring capabilities."

- Score 5: Centralized SIEM, 24/7 monitoring, correlation
- Score 3: Centralized logs, periodic review
- Score 1: Distributed logs, ad-hoc review

### Incident Response Questions (Q11-Q15)

**Q11: Tabletop Exercises**
> "Provide documentation of your last three incident response tabletop exercises."

- Score 5: Quarterly exercises, documented, improved
- Score 3: Annual exercises
- Score 1: No exercises

**Q12: Incident Response Plan**
> "Show your incident response plan including escalation procedures."

- Score 5: Detailed plan, tested, includes NIS2 reporting
- Score 3: Plan exists, not recently tested
- Score 1: No formal plan

**Q13: CSIRT Contact**
> "Do you have established contact procedures with your national CSIRT?"

- Score 5: Established relationship, tested contact
- Score 3: Contact information available
- Score 1: No contact established

**Q14: Significant Incident Knowledge**
> "What constitutes a 'significant incident' under NIS2 Article 23 for your entity?"

- Score 5: Detailed knowledge of all thresholds
- Score 3: General awareness
- Score 1: Unaware of requirements

**Q15: Reporting Timeline**
> "What are the NIS2 reporting timelines for significant incidents?"

- Score 5: 24h/72h/1 month
- Score 3: General awareness of timelines
- Score 1: Unaware

### Supply Chain Questions (Q16-Q20)

**Q16: Supplier Inventory**
> "Show your inventory of critical ICT suppliers."

- Score 5: Comprehensive inventory, risk-rated
- Score 3: Basic inventory
- Score 1: No inventory

**Q17: Supplier Assessments**
> "Provide evidence of security assessments for top 3 critical suppliers."

- Score 5: Recent assessments, documented controls
- Score 3: Some assessments
- Score 1: No assessments

**Q18: Contractual Security**
> "Show security requirements in a recent critical supplier contract."

- Score 5: Detailed security clauses, audit rights
- Score 3: Generic security mention
- Score 1: No security requirements

**Q19: Supply Chain Incidents**
> "Describe your process for responding to supplier security incidents."

- Score 5: Documented process, tested coordination
- Score 3: Informal process
- Score 1: No process

**Q20: Dependency Analysis**
> "Have you analyzed concentration risk (single points of failure) in your supply chain?"

- Score 5: Formal analysis, mitigation plans
- Score 3: Informal awareness
- Score 1: No analysis

---

## Deliverables

### Gap Analysis Report Structure

```python
class GapAnalysisReport(BaseModel):
    # Metadata
    report_id: str
    entity_id: str
    assessment_date: datetime
    assessor: str
    mode: Literal["quick_scan", "deep_dive"]
    
    # Executive Summary
    overall_maturity: int  # 1-5
    compliance_readiness: float  # 0-100%
    estimated_timeline_to_compliance: str
    
    # Domain Scores
    domain_scores: dict[str, DomainScore]
    # Article 21, Article 22, Article 23, Articles 24-26
    
    # Gap Details
    gaps: list[Gap]
    
    # Remediation Roadmap
    roadmap: RemediationRoadmap
    
    # Appendix
    question_responses: list[QuestionResponse]
    evidence_reviewed: list[str]
```

### Prioritized Remediation Roadmap

```python
class RemediationRoadmap(BaseModel):
    phases: list[RoadmapPhase]
    
    # Effort Estimates
    total_effort_days: int
    internal_resources_required: int
    external_resources_recommended: int
    estimated_cost_range: tuple[float, float]
    
    # Timeline
    quick_wins: list[RemediationItem]  # 0-30 days
    short_term: list[RemediationItem]   # 1-3 months
    medium_term: list[RemediationItem]  # 3-6 months
    long_term: list[RemediationItem]    # 6-12 months
    
    # Critical Path
    critical_path: list[str]  # Item IDs that block other items
    
    # Risk-Weighted Priority
    risk_based_priorities: list[PriorityItem]
```

---

## Implementation Contract

```python
class GapAnalyst:
    def __init__(self, knowledge_base: NIS2KnowledgeBase, config: GapConfig):
        """Initialize with question banks and assessment criteria."""
        pass
    
    def conduct_quick_scan(self, entity_data: EntityInput) -> QuickScanResult:
        """Execute high-level maturity assessment."""
        pass
    
    def conduct_deep_dive(self, entity_data: EntityInput, evidence: EvidenceBundle) -> GapAnalysisReport:
        """Execute comprehensive gap analysis."""
        pass
    
    def get_question_bank(self, domain: str, mode: str) -> list[Question]:
        """Retrieve appropriate questions for assessment."""
        pass
    
    def score_response(self, question: Question, response: Response) -> Score:
        """Evaluate response against maturity criteria."""
        pass
    
    def identify_gaps(self, scores: list[Score]) -> list[Gap]:
        """Map low scores to specific compliance gaps."""
        pass
    
    def generate_roadmap(
        self, 
        gaps: list[Gap],
        constraints: ResourceConstraints
    ) -> RemediationRoadmap:
        """Create prioritized remediation plan."""
        pass
    
    def estimate_effort(self, gap: Gap) -> EffortEstimate:
        """Calculate resource requirements for remediation."""
        pass
```

---

## Interactive Questionnaire Logic

```python
class InteractiveQuestionnaire:
    """
    Adaptive questionnaire that adjusts based on responses.
    """
    
    def __init__(self):
        self.questions = self._load_questions()
        self.responses = {}
        self.current_path = []
    
    def get_next_question(self) -> Question | None:
        """Determine next question based on previous responses."""
        # Skip irrelevant branches
        if self.responses.get("is_qualifying_entity") == False:
            return None  # Early exit
        
        # Deep dive based on risk areas
        if self._high_risk_area_detected():
            return self._get_deep_dive_question()
        
        return self._get_next_standard_question()
    
    def calculate_progress(self) -> float:
        """Return completion percentage."""
        pass
    
    def generate_interim_report(self) -> InterimResult:
        """Provide preliminary findings during assessment."""
        pass
```

---

## Legal Basis Citations

All recommendations must cite relevant Articles:

| Gap Category | Legal Citation |
|--------------|----------------|
| Risk management gap | "Article 21(2)(a) - Risk analysis and security policies" |
| Incident response gap | "Article 21(2)(b) and Article 23 - Incident handling and reporting" |
| Supply chain gap | "Article 21(2)(d) and Article 22 - Supply chain security" |
| Encryption gap | "Article 21(2)(i) - Cryptography and encryption" |
| MFA gap | "Article 21(2)(k) - Multi-factor authentication" |
| Registration gap | "Article 24/25/26 - Entity classification and registration" |

---

## Testing Requirements

1. **Question Bank Tests:** All questions have valid scoring criteria
2. **Adaptive Logic Tests:** Branching logic works correctly
3. **Roadmap Tests:** Effort estimates are reasonable
4. **Sample Assessments:**
   - Mature entity (maturity 4-5)
   - Developing entity (maturity 2-3)
   - Immature entity (maturity 1-2)
