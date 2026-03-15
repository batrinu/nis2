# Report Generator Agent Specification

## Purpose

Compile audit findings, gap analyses, and enforcement actions into regulatory documentation. Generate multiple output formats suitable for different audiences and use cases.

## Report Templates

### Template 1: Executive Summary

**Audience:** C-Suite, Board of Directors

**Content:**
- Compliance percentage at a glance
- Criticality rating with traffic light indicator
- Key findings (max 5 bullet points)
- Required actions with business impact
- Timeline overview

**Structure:**
```yaml
executive_summary:
  report_metadata:
    title: "NIS2 Compliance Assessment Summary"
    entity_name: str
    assessment_date: date
    report_version: str
    classification: str  # "Essential" or "Important"
    
  compliance_overview:
    overall_percentage: float  # 0-100
    rating: str  # "Compliant", "Substantially", "Partially", "Non-Compliant"
    trend: str  # "Improving", "Stable", "Declining" (if previous assessment)
    
  domain_summary:
    governance: {score: float, status: str}
    technical_controls: {score: float, status: str}
    incident_response: {score: float, status: str}
    supply_chain: {score: float, status: str}
    documentation: {score: float, status: str}
    management_oversight: {score: float, status: str}
    
  key_findings:
    - severity: str  # "Critical", "High", "Medium", "Low"
      description: str
      business_impact: str
      
  required_actions:
    immediate: list[str]  # 0-30 days
    short_term: list[str]  # 1-3 months
    medium_term: list[str]  # 3-6 months
    
  resource_implications:
    estimated_budget: str
    staffing_requirements: str
    external_support: str
```

### Template 2: Legal Basis Citation

**Audience:** Legal counsel, regulatory authorities

**Content:**
- Specific Articles violated
- Legal reasoning for each finding
- Case law references (if applicable)
- National transposition references
- Jurisdictional considerations

**Structure:**
```yaml
legal_basis_citation:
  report_metadata:
    title: "Legal Basis Analysis"
    legal_framework: "Directive (EU) 2022/2555 (NIS2)"
    national_law: str  # e.g., "[Country] NIS2 Transposition Act"
    
  violations:
    - violation_id: str
      article: str  # e.g., "Article 21(2)(a)"
      paragraph: str
      requirement: str  # Full text of requirement
      finding: str
      evidence_summary: str
      legal_reasoning: str
      recommended_citation: str  # For enforcement notice
      
  cross_references:
    gdpr_intersections: list[str]
    dora_intersections: list[str]  # For financial entities
    sector_regulations: list[str]
    
  jurisdictional_analysis:
    lead_authority: str
    cross_border_implications: str
    coordination_requirements: str
```

### Template 3: Evidence Appendix

**Audience:** Auditors, investigators, legal review

**Content:**
- Evidence inventory with references
- Screenshot placeholders
- Log file references
- Interview summaries
- Technical tool outputs
- Chain of custody documentation

**Structure:**
```yaml
evidence_appendix:
  report_metadata:
    title: "Evidence Appendix"
    evidence_custodian: str
    retention_period: str
    
  evidence_inventory:
    - evidence_id: str
      type: str  # "document", "screenshot", "log", "interview", "technical"
      description: str
      source: str
      date_collected: datetime
      collector: str
      hash_verification: str  # For digital evidence
      location: str  # Storage reference
      
  document_evidence:
    - doc_id: str
      title: str
      version: str
      approval_date: date
      review_status: str
      
  technical_evidence:
    - scan_id: str
      tool: str
      scan_date: datetime
      scope: str
      findings_summary: str
      raw_results_location: str
      
  interview_summaries:
    - interview_id: str
      role: str
      date: datetime
      topics_covered: list[str]
      key_responses: dict
      assessment: str
```

### Template 4: Remediation Roadmap

**Audience:** Project managers, compliance officers

**Content:**
- SMART criteria for each remediation item
- Gantt-style timeline
- Resource allocation
- Milestone definitions
- Success criteria
- Verification methods

**Structure:**
```yaml
remediation_roadmap:
  report_metadata:
    title: "Remediation Roadmap"
    baseline_date: date
    target_compliance_date: date
    
  phases:
    - phase_id: str
      name: str
      duration_weeks: int
      objectives: list[str]
      items: list[RemediationItem]
      dependencies: list[str]
      milestones: list[Milestone]
      
  remediation_items:
    - item_id: str
      violation_reference: str
      description: str
      specific: str
      measurable: str
      achievable: bool
      relevant: str
      time_bound: date
      owner: str
      resources_required: dict
      verification_method: str
      estimated_cost: float
      
  timeline:
    format: "gantt"  # Or "kanban", "calendar"
    phases: list[PhaseTimeline]
    critical_path: list[str]
    buffer_time: int  # Days
```

### Template 5: Enforcement Action Notice

**Audience:** Entity leadership, legal counsel, public record

**Content:**
- Violation details
- Legal basis
- Sanctions imposed
- Remediation requirements
- Appeal procedures
- Timeline for compliance

**Structure:**
```yaml
enforcement_action_notice:
  report_metadata:
    title: "Notice of Enforcement Action"
    notice_id: str
    issue_date: date
    effective_date: date
    competent_authority: str
    
  recipient:
    entity_name: str
    entity_classification: str
    legal_address: str
    registered_address: str
    
  violations:
    - violation_id: str
      article_violated: str
      description: str
      severity: str
      evidence_reference: str
      
  legal_basis:
    primary_articles: list[str]
    national_law: str
    case_precedents: list[str]
    
  sanctions:
    - sanction_type: str  # "fine", "warning", "restriction", "disclosure"
      amount: float | None
      payment_terms: str | None
      conditions: list[str]
      
  remediation_requirements:
    mandatory_actions: list[RemediationItem]
    deadline: date
    verification_requirements: str
    
  appeal_rights:
    appeal_deadline: date
    appeal_procedure: str
    appeal_authority: str
    stay_of_execution: bool
    
  disclosure:
    public_notification_required: bool
    notification_date: date | None
    disclosure_scope: str
```

---

## Output Formats

### Format 1: Markdown

**Use Case:** Human-readable documents, version control

**Features:**
- Standard Markdown syntax
- Tables for structured data
- Code blocks for technical details
- Footnotes for citations
- TOC generation

**Example Output:**
```markdown
# NIS2 Compliance Assessment Report

**Entity:** Example Energy Ltd  
**Date:** 2024-03-15  
**Classification:** Essential Entity

## Executive Summary

| Domain | Score | Status |
|--------|-------|--------|
| Governance | 85% | ✓ Substantially Compliant |
| Technical Controls | 72% | ⚠ Partially Compliant |
| ... | ... | ... |

**Overall: 78% - Substantially Compliant**

## Legal Basis

### Finding F-001: Insufficient Risk Assessment

**Article Violated:** Article 21(2)(a)  
**Requirement:** "Based on an all-hazards approach, appropriate and proportionate technical and organisational measures to manage the risks..."

[... detailed findings ...]
```

### Format 2: PDF-Ready HTML

**Use Case:** Formal regulatory submissions, printing

**Features:**
- Print-friendly CSS
- Page breaks
- Headers/footers with page numbers
- Official letterhead placeholders
- Signature blocks
- Annex/Appendix formatting

**Structure:**
```html
<!DOCTYPE html>
<html>
<head>
  <title>NIS2 Compliance Report</title>
  <style>
    @media print {
      .page-break { page-break-before: always; }
      .no-print { display: none; }
    }
    .header { ... }
    .footer { ... }
    table.regulatory { ... }
  </style>
</head>
<body>
  <div class="cover-page">...</div>
  <div class="page-break"></div>
  <div class="executive-summary">...</div>
  ...
</body>
</html>
```

### Format 3: JSON (Machine Processing)

**Use Case:** API responses, data exchange, automated processing

**Schema:**
```json
{
  "schema_version": "1.0.0",
  "report_type": "compliance_assessment",
  "report_id": "REP-2024-001",
  "entity": {
    "name": "Example Energy Ltd",
    "classification": "essential",
    "sector": "energy"
  },
  "assessment": {
    "date": "2024-03-15",
    "overall_score": 0.78,
    "rating": "substantially_compliant",
    "domains": {
      "governance": {"score": 0.85, "weight": 0.20},
      "technical_controls": {"score": 0.72, "weight": 0.25},
      ...
    }
  },
  "findings": [...],
  "remediation": {...}
}
```

---

## Scoring Visualization

### Chart Types

1. **Compliance Radar Chart**
   - 6 axes for compliance domains
   - Target circle at 100%
   - Actual score overlay
   - Industry benchmark comparison

2. **Gap Analysis Bar Chart**
   - X-axis: Requirements
   - Y-axis: Maturity level (1-5)
   - Color coding by domain
   - Target line at level 3

3. **Timeline Gantt Chart**
   - Phases as swimlanes
   - Remediation items as bars
   - Dependencies as arrows
   - Milestones as diamonds

4. **Trend Line Chart** (for follow-up assessments)
   - X-axis: Assessment dates
   - Y-axis: Domain scores
   - Lines for each domain
   - Trend arrows

### Visualization Libraries

- **Static:** Matplotlib, Plotly (export to PNG/SVG)
- **Interactive:** Plotly, D3.js (for HTML reports)
- **Embedded:** Base64-encoded images in Markdown/HTML

---

## Cross-Border Coordination

### Multi-Authority Reporting

**When Required:**
- Entity operates in multiple Member States
- Significant incident affects multiple jurisdictions
- Enforcement action with cross-border implications

**Report Structure:**
```yaml
cross_border_report:
  lead_authority:
    member_state: str
    authority_name: str
    contact: str
    
  concerned_authorities:
    - member_state: str
      authority_name: str
      scope_of_concern: str
      
  coordination:
    information_shared: list[str]
    consultation_timeline: str
    disagreement_resolution: str
    
  language_provisions:
    original_language: str
    translations_provided: list[str]
```

---

## Implementation Contract

```python
class ReportGenerator:
    def __init__(self, template_dir: str, knowledge_base: NIS2KnowledgeBase):
        """Initialize with Jinja2 templates and legal references."""
        self.jinja_env = Environment(loader=FileSystemLoader(template_dir))
        pass
    
    def generate_executive_summary(
        self, 
        assessment: AuditAssessment,
        format: str = "markdown"
    ) -> str:
        """Generate executive summary in specified format."""
        pass
    
    def generate_full_report(
        self,
        assessment: AuditAssessment,
        format: str = "markdown"
    ) -> str:
        """Generate complete assessment report."""
        pass
    
    def generate_enforcement_notice(
        self,
        sanction_package: SanctionPackage,
        format: str = "html"
    ) -> str:
        """Generate formal enforcement notice."""
        pass
    
    def generate_gap_report(
        self,
        gap_analysis: GapAnalysisReport,
        format: str = "markdown"
    ) -> str:
        """Generate gap analysis report."""
        pass
    
    def generate_visualizations(
        self,
        assessment: AuditAssessment
    ) -> dict[str, bytes]:
        """Generate chart images as base64 or binary."""
        pass
    
    def export_json(
        self,
        assessment: AuditAssessment
    ) -> dict:
        """Export report data as structured JSON."""
        pass
    
    def compile_evidence_appendix(
        self,
        evidence: list[EvidenceItem]
    ) -> str:
        """Generate evidence appendix with proper referencing."""
        pass
```

---

## Template Directory Structure

```
agents/report-generator/templates/
├── base.html                 # Base HTML template
├── base.md                   # Base Markdown template
├── executive_summary/
│   ├── template.md
│   └── template.html
├── legal_basis/
│   ├── template.md
│   └── template.html
├── evidence_appendix/
│   ├── template.md
│   └── template.html
├── remediation_roadmap/
│   ├── template.md
│   ├── template.html
│   └── gantt_chart.html
├── enforcement_notice/
│   ├── template.html
│   └── template.md
├── styles/
│   ├── print.css
│   └── screen.css
└── partials/
    ├── header.html
    ├── footer.html
    ├── signature_block.html
    └── legal_disclaimer.html
```

---

## Legal Basis Citations

All reports must include:

| Report Section | Required Citations |
|----------------|-------------------|
| Cover page | Directive (EU) 2022/2555 reference |
| Scope | Applicable Articles (21, 22, 23, 24, 25, 26) |
| Findings | Specific Article sub-paragraphs |
| Remediation | Article 21(2) requirements |
| Enforcement | Article 34 sanctions |
| Cross-border | Article 26 coordination |

**Standard Disclaimer:**
> "This report is prepared for regulatory compliance assessment purposes under Directive (EU) 2022/2555. It does not constitute legal advice. Entities should consult qualified legal counsel for interpretation of specific obligations."

---

## Testing Requirements

1. **Template Tests:** All templates render without errors
2. **Format Tests:** Markdown, HTML, JSON outputs valid
3. **Citation Tests:** All findings include proper legal citations
4. **Sample Reports:**
   - Compliant entity full report
   - Non-compliant entity with enforcement
   - Cross-border entity report
