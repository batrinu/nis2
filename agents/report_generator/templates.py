"""
Report Generator Agent for NIS2 compliance assessment.
Compiles audit findings into regulatory documentation.
"""
from typing import Optional, Literal
from datetime import datetime, timezone
import json
from shared.schemas import (
    EntityInput, AuditAssessment, GapAnalysisReport,
    SanctionPackage, SanctionNotice
)


class ReportGenerator:
    """
    Compiles audit findings into regulatory documentation.
    Generates multiple output formats.
    """
    
    def __init__(self, template_dir: Optional[str] = None):
        """Initialize with template directory."""
        self.template_dir = template_dir
    
    def generate_executive_summary(
        self,
        assessment: AuditAssessment,
        format: Literal["markdown", "html", "json"] = "markdown"
    ) -> str:
        """Generate executive summary in specified format."""
        
        if format == "markdown":
            return self._generate_exec_summary_md(assessment)
        elif format == "html":
            return self._generate_exec_summary_html(assessment)
        elif format == "json":
            return json.dumps(self._generate_exec_summary_data(assessment), indent=2)
        
        raise ValueError(f"Unknown format: {format}")
    
    def _generate_exec_summary_md(self, assessment: AuditAssessment) -> str:
        """Generate executive summary as Markdown."""
        rating_emoji = {
            "Compliant": "✅",
            "Substantially Compliant": "✓",
            "Partially Compliant": "⚠️",
            "Non-Compliant": "❌"
        }.get(assessment.rating, "❓")
        
        md = f"""# NIS2 Compliance Assessment - Executive Summary

**Entity:** {assessment.entity_id}  
**Assessment Date:** {assessment.assessment_date.strftime('%Y-%m-%d')}  
**Report Version:** {assessment.report_version}

## Compliance Overview

| Metric | Value |
|--------|-------|
| Overall Score | {assessment.overall_score:.1f}% |
| Rating | {rating_emoji} {assessment.rating} |
| Classification | {assessment.entity_classification} |

## Domain Performance

| Domain | Score | Status |
|--------|-------|--------|
"""
        
        for domain in assessment.domain_scores:
            status = "✓" if domain.score >= 75 else "⚠️" if domain.score >= 50 else "❌"
            md += f"| {domain.domain_name} | {domain.score:.1f}% | {status} |\n"
        
        md += f"""
## Key Findings

"""
        
        critical_findings = [f for f in assessment.findings if f.severity == "Critical"]
        high_findings = [f for f in assessment.findings if f.severity == "High"]
        
        if critical_findings:
            md += "### Critical Findings\n\n"
            for f in critical_findings[:3]:
                md += f"- **{f.finding_id}:** {f.title}\n"
        
        if high_findings:
            md += "\n### High Priority Findings\n\n"
            for f in high_findings[:3]:
                md += f"- **{f.finding_id}:** {f.title}\n"
        
        md += f"""
## Required Actions

**Immediate (0-30 days):**
{chr(10).join(f"- {r.description[:100]}..." for r in assessment.recommendations if r.priority == "immediate")}

**Short-term (1-3 months):**
{chr(10).join(f"- {r.description[:100]}..." for r in assessment.recommendations if r.priority == "high")}

---
*This summary is for executive review. See full report for detailed findings and evidence.*
"""
        
        return md
    
    def _generate_exec_summary_html(self, assessment: AuditAssessment) -> str:
        """Generate executive summary as HTML."""
        return f"""<!DOCTYPE html>
<html>
<head>
    <title>NIS2 Compliance Assessment - Executive Summary</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; }}
        h1 {{ color: #1a472a; }}
        table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
        th, td {{ border: 1px solid #ddd; padding: 12px; text-align: left; }}
        th {{ background-color: #1a472a; color: white; }}
        .compliant {{ color: green; }}
        .partial {{ color: orange; }}
        .non-compliant {{ color: red; }}
        .footer {{ margin-top: 40px; font-size: 0.9em; color: #666; }}
    </style>
</head>
<body>
    <h1>NIS2 Compliance Assessment - Executive Summary</h1>
    
    <p><strong>Entity:</strong> {assessment.entity_id}</p>
    <p><strong>Assessment Date:</strong> {assessment.assessment_date.strftime('%Y-%m-%d')}</p>
    <p><strong>Rating:</strong> <span class="{'compliant' if assessment.rating == 'Compliant' else 'partial' if assessment.rating == 'Substantially Compliant' else 'non-compliant'}">{assessment.rating}</span></p>
    
    <h2>Overall Score: {assessment.overall_score:.1f}%</h2>
    
    <table>
        <tr>
            <th>Domain</th>
            <th>Score</th>
            <th>Weight</th>
        </tr>
""" + "".join([f"""        <tr>
            <td>{d.domain_name}</td>
            <td>{d.score:.1f}%</td>
            <td>{d.weight * 100:.0f}%</td>
        </tr>
""" for d in assessment.domain_scores]) + """
    </table>
    
    <div class="footer">
        <p>This report was generated automatically. For questions, contact the competent authority.</p>
    </div>
</body>
</html>"""
    
    def _generate_exec_summary_data(self, assessment: AuditAssessment) -> dict:
        """Generate executive summary as data structure."""
        return {
            "report_type": "executive_summary",
            "entity_id": assessment.entity_id,
            "assessment_date": assessment.assessment_date.isoformat(),
            "overall_score": assessment.overall_score,
            "rating": assessment.rating,
            "classification": assessment.entity_classification,
            "domain_scores": [
                {
                    "name": d.domain_name,
                    "score": d.score,
                    "weight": d.weight
                }
                for d in assessment.domain_scores
            ],
            "key_findings_count": len(assessment.findings),
            "critical_findings": len([f for f in assessment.findings if f.severity == "Critical"]),
            "recommendations_count": len(assessment.recommendations)
        }
    
    def generate_full_report(
        self,
        assessment: AuditAssessment,
        format: Literal["markdown", "html", "json"] = "markdown"
    ) -> str:
        """Generate complete assessment report."""
        
        if format == "markdown":
            return self._generate_full_report_md(assessment)
        elif format == "json":
            return json.dumps(assessment.model_dump(), indent=2, default=str)
        
        raise ValueError(f"Unknown format: {format}")
    
    def _generate_full_report_md(self, assessment: AuditAssessment) -> str:
        """Generate full report as Markdown."""
        md = f"""# NIS2 Compliance Assessment Report

---

**Report ID:** {assessment.report_id}  
**Entity ID:** {assessment.entity_id}  
**Assessment Date:** {assessment.assessment_date.strftime('%Y-%m-%d')}  
**Assessor:** {assessment.assessor}  
**Report Version:** {assessment.report_version}

---

## 1. Executive Summary

This report presents the findings of a NIS2 compliance assessment conducted under Directive (EU) 2022/2555.

### 1.1 Overall Assessment

| Metric | Value |
|--------|-------|
| Overall Score | {assessment.overall_score:.1f}% |
| Rating | {assessment.rating} |
| Entity Classification | {assessment.entity_classification} |
| Next Assessment Due | {assessment.next_assessment_date or 'TBD'} |

### 1.2 Domain Scores

| Domain | Score | Weight | Weighted Contribution |
|--------|-------|--------|----------------------|
"""
        
        for d in assessment.domain_scores:
            contribution = d.score * d.weight
            md += f"| {d.domain_name} | {d.score:.1f}% | {d.weight * 100:.0f}% | {contribution:.1f}% |\n"
        
        md += f"""
## 2. Legal Basis

This assessment was conducted under **Directive (EU) 2022/2555** (NIS2 Directive).

### 2.1 Applicable Articles

"""
        
        for article, status in assessment.article_21_mapping.items():
            md += f"- **{article}:** {status.get('status', 'unknown')} (Score: {status.get('score', 'N/A')})\n"
        
        md += f"""
## 3. Findings

### 3.1 Summary by Severity

| Severity | Count |
|----------|-------|
| Critical | {len([f for f in assessment.findings if f.severity == 'Critical'])} |
| High | {len([f for f in assessment.findings if f.severity == 'High'])} |
| Medium | {len([f for f in assessment.findings if f.severity == 'Medium'])} |
| Low | {len([f for f in assessment.findings if f.severity == 'Low'])} |

### 3.2 Detailed Findings

"""
        
        for finding in assessment.findings:
            md += f"""#### {finding.finding_id}: {finding.title}

- **Severity:** {finding.severity}
- **Article Reference:** {finding.article_reference}
- **Description:** {finding.description}
- **Business Impact:** {finding.business_impact}
- **Recommendation:** {finding.recommendation}

"""
        
        md += f"""
## 4. Recommendations

| ID | Priority | Description | Article |
|----|----------|-------------|---------|
"""
        
        for rec in assessment.recommendations[:10]:  # Limit to top 10
            md += f"| {rec.recommendation_id} | {rec.priority} | {rec.description[:50]}... | {rec.article_reference} |\n"
        
        md += f"""
## 5. Remediation Roadmap

"""
        
        for item in assessment.remediation_roadmap[:5]:
            md += f"""### {item.item_id}

- **Description:** {item.description}
- **Deadline:** {item.time_bound}
- **Owner:** {item.owner or 'TBD'}
- **Verification:** {item.verification_method}

"""
        
        md += f"""
---

## Appendices

### Appendix A: Assessment Methodology

This assessment followed the 5-phase NIS2 audit methodology:
1. Entity Classification
2. Documentation Review
3. Technical Assessment
4. Interview Simulation
5. Compliance Scoring

### Appendix B: Legal Disclaimer

This report is prepared for regulatory compliance assessment purposes under Directive (EU) 2022/2555. It does not constitute legal advice. Entities should consult qualified legal counsel for interpretation of specific obligations.

---

*Report generated: {datetime.now(timezone.utc).isoformat()}*
"""
        
        return md
    
    def generate_enforcement_notice(
        self,
        sanction_package: SanctionPackage,
        notice: SanctionNotice,
        format: Literal["markdown", "html"] = "html"
    ) -> str:
        """Generate formal enforcement notice."""
        
        if format == "html":
            return self._generate_enforcement_notice_html(notice)
        return self._generate_enforcement_notice_md(notice)
    
    def _generate_enforcement_notice_html(self, notice: SanctionNotice) -> str:
        """Generate enforcement notice as HTML."""
        return f"""<!DOCTYPE html>
<html>
<head>
    <title>Notice of Enforcement Action</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; max-width: 800px; }}
        .header {{ border-bottom: 3px solid #1a472a; padding-bottom: 20px; margin-bottom: 30px; }}
        .notice-id {{ font-size: 0.9em; color: #666; }}
        h1 {{ color: #1a472a; }}
        h2 {{ color: #333; border-bottom: 1px solid #ccc; padding-bottom: 10px; }}
        .violation {{ background: #f5f5f5; padding: 15px; margin: 10px 0; border-left: 4px solid #d9534f; }}
        .sanction {{ background: #fff3cd; padding: 15px; margin: 10px 0; border-left: 4px solid #ffc107; }}
        .footer {{ margin-top: 50px; padding-top: 20px; border-top: 1px solid #ccc; font-size: 0.9em; }}
    </style>
</head>
<body>
    <div class="header">
        <p class="notice-id">Notice ID: {notice.notice_id}</p>
        <h1>Notice of Enforcement Action</h1>
        <p><strong>Competent Authority:</strong> {notice.competent_authority}</p>
        <p><strong>Issue Date:</strong> {notice.issue_date.strftime('%Y-%m-%d')}</p>
    </div>
    
    <h2>Recipient</h2>
    <p><strong>Entity:</strong> {notice.entity_name}</p>
    <p><strong>Classification:</strong> {notice.entity_classification}</p>
    
    <h2>Violations</h2>
""" + "".join([f"""    <div class="violation">
        <p><strong>Violation {v.violation_id}</strong></p>
        <p><strong>Article Violated:</strong> {v.article_violated}</p>
        <p>{v.description}</p>
        <p><strong>Severity:</strong> {v.severity}</p>
    </div>
""" for v in notice.violations]) + """
    <h2>Sanctions Imposed</h2>
""" + "".join([f"""    <div class="sanction">
        <p><strong>Type:</strong> {s.sanction_type}</p>
        {f'<p><strong>Amount:</strong> €{s.amount_eur:,.2f}</p>' if s.amount_eur else ''}
        <p>{s.description}</p>
    </div>
""" for s in notice.sanctions]) + f"""
    <h2>Remediation Requirements</h2>
    <p><strong>Deadline:</strong> {notice.remediation_requirements.deadline}</p>
    <p>{notice.remediation_requirements.verification_requirements}</p>
    
    <h2>Appeal Rights</h2>
    <p>You have the right to appeal this decision. Appeals must be submitted by <strong>{notice.appeal_rights.appeal_deadline}</strong>.</p>
    <p><strong>Appeal Procedure:</strong> {notice.appeal_rights.appeal_procedure}</p>
    
    <div class="footer">
        <p><strong>Legal Basis:</strong> {notice.legal_basis}</p>
        <p><strong>Investigating Officer:</strong> {notice.investigating_officer}</p>
        <p><strong>Authority Head:</strong> {notice.authority_head}</p>
    </div>
</body>
</html>"""
    
    def _generate_enforcement_notice_md(self, notice: SanctionNotice) -> str:
        """Generate enforcement notice as Markdown."""
        md = f"""# Notice of Enforcement Action

**Notice ID:** {notice.notice_id}  
**Competent Authority:** {notice.competent_authority}  
**Issue Date:** {notice.issue_date.strftime('%Y-%m-%d')}

---

## Recipient

**Entity:** {notice.entity_name}  
**Classification:** {notice.entity_classification}

---

## Violations

"""
        
        for v in notice.violations:
            md += f"""### {v.violation_id}

- **Article Violated:** {v.article_violated}
- **Severity:** {v.severity}
- **Description:** {v.description}

"""
        
        md += f"""---

## Sanctions

"""
        
        for s in notice.sanctions:
            md += f"""### {s.sanction_type}

{s.description}
{ f"**Amount:** €{s.amount_eur:,.2f}" if s.amount_eur else ""}

"""
        
        md += f"""---

## Remediation Requirements

**Deadline:** {notice.remediation_requirements.deadline}

{notice.remediation_requirements.verification_requirements}

---

## Appeal Rights

You have the right to appeal this decision.

**Appeal Deadline:** {notice.appeal_rights.appeal_deadline}  
**Appeal Procedure:** {notice.appeal_rights.appeal_procedure}

---

*Legal Basis: {notice.legal_basis}*
"""
        
        return md
    
    def generate_gap_report(
        self,
        gap_analysis: GapAnalysisReport,
        format: Literal["markdown", "html", "json"] = "markdown"
    ) -> str:
        """Generate gap analysis report."""
        
        if format == "markdown":
            return self._generate_gap_report_md(gap_analysis)
        elif format == "json":
            return json.dumps(gap_analysis.model_dump(), indent=2, default=str)
        
        raise ValueError(f"Unknown format: {format}")
    
    def _generate_gap_report_md(self, gap_analysis: GapAnalysisReport) -> str:
        """Generate gap report as Markdown."""
        md = f"""# NIS2 Gap Analysis Report

**Report ID:** {gap_analysis.report_id}  
**Entity:** {gap_analysis.entity_id}  
**Assessment Date:** {gap_analysis.assessment_date.strftime('%Y-%m-%d')}  
**Mode:** {gap_analysis.assessment_mode}

---

## Executive Summary

| Metric | Value |
|--------|-------|
| Overall Maturity | {gap_analysis.overall_maturity}/5 |
| Compliance Readiness | {gap_analysis.compliance_readiness:.1f}% |
| Rating | {gap_analysis.rating} |

## Domain Scores

"""
        
        for d in gap_analysis.domain_scores:
            md += f"- **{d.domain_name}:** {d.score:.1f}% (Weight: {d.weight * 100:.0f}%)\n"
        
        md += f"""
## Key Findings

Total Findings: {len(gap_analysis.findings)}

"""
        
        for finding in gap_analysis.findings[:10]:
            md += f"- **{finding.severity}:** {finding.title}\n"
        
        md += f"""
## Remediation Roadmap

"""
        
        for item in gap_analysis.remediation_roadmap[:5]:
            md += f"""### {item.item_id}

- **Description:** {item.description}
- **Deadline:** {item.time_bound}
- **Status:** {item.status}

"""
        
        return md
    
    def export_json(self, assessment: AuditAssessment) -> dict:
        """Export report data as structured JSON."""
        return assessment.model_dump()
