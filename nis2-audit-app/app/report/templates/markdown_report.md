# NIS2 Compliance Audit Report

**Entity:** {{ entity_name }}  
**Sector:** {{ entity_sector }}  
**Audit Date:** {{ audit_date }}  
**Session ID:** {{ session_id }}  
**Auditor:** {{ auditor_name or "N/A" }}

---

## Executive Summary

{% if classification %}
### Entity Classification

| Field | Value |
|-------|-------|
| **Classification** | {{ classification.classification }} |
| **Legal Basis** | {{ classification.legal_basis }} |
| **Annex** | {{ classification.annex or "N/A" }} |
| **Lead Authority** | {{ classification.lead_authority }} |
| **Confidence** | {{ "%.0f" | format(classification.confidence_score * 100) }}% |
{% endif %}

### Overall Compliance Score

**{{ "%.1f" | format(compliance_score.overall_score) }}%** - {{ compliance_score.rating }}

| Domain | Score | Weight | Weighted Score |
|--------|-------|--------|----------------|
{% for domain in domain_scores %}
| {{ domain.name }} | {{ "%.1f" | format(domain.score) }}% | {{ "%.0f" | format(domain.weight * 100) }}% | {{ "%.1f" | format(domain.weighted_score) }} |
{% endfor %}

---

## Device Inventory

**Total Devices Discovered:** {{ devices | length }}

| IP Address | Hostname | Vendor | Type | Status |
|------------|----------|--------|------|--------|
{% for device in devices %}
| {{ device.ip_address }} | {{ device.hostname or "-" }} | {{ device.vendor or "Unknown" }} | {{ device.device_type or "Unknown" }} | {{ device.connection_status }} |
{% endfor %}

### Device Breakdown

{% if device_summary %}
- **Routers:** {{ device_summary.router_count }}
- **Switches:** {{ device_summary.switch_count }}
- **Firewalls:** {{ device_summary.firewall_count }}
- **Servers:** {{ device_summary.server_count }}
- **Unknown:** {{ device_summary.unknown_count }}
{% endif %}

---

## Audit Findings

**Total Findings:** {{ findings | length }}

{% if findings_by_severity %}
### Findings by Severity

| Severity | Count |
|----------|-------|
{% for sev, count in findings_by_severity.items() %}
| {{ sev | capitalize }} | {{ count }} |
{% endfor %}
{% endif %}

{% for finding in findings %}
### {{ finding.finding_id or loop.index }}: {{ finding.title }}

**Severity:** {{ finding.severity | upper }}  
**NIS2 Article:** {{ finding.nis2_article or "N/A" }}  
**Domain:** {{ finding.nis2_domain or "N/A" }}

#### Description

{{ finding.description }}

#### Evidence

{{ finding.evidence or "No evidence recorded" }}

{% if finding.device_ids %}
**Affected Devices:** {{ finding.device_ids | join(", ") }}
{% endif %}

#### Recommendation

{{ finding.recommendation or "No recommendation provided" }}

{% if finding.remediation_steps %}
#### Remediation Steps

{% for step in finding.remediation_steps %}
1. {{ step }}
{% endfor %}
{% endif %}

{% if finding.estimated_effort %}
**Estimated Effort:** {{ finding.estimated_effort }}
{% endif %}

---

{% endfor %}

## Compliance Checklist Results

{% for section in checklist_sections %}
### {{ section.title }} ({{ section.domain }})

**Weight:** {{ "%.0f" | format(section.weight * 100) }}%

| ID | Question | Status | Notes |
|----|----------|--------|-------|
{% for question in section.questions %}
| {{ question.id }} | {{ question.question[:60] }}... | {{ question.status.value }} | {{ question.notes[:30] }}... |
{% endfor %}

{% endfor %}

---

{% if sanction_exposure %}
## Sanction Exposure

Based on the entity classification and compliance gaps, the potential sanction exposure is:

| Metric | Value |
|--------|-------|
| **Maximum Fine (Fixed)** | €{{ sanction_exposure.max_amount_eur | format_number }} |
| **Maximum Fine (% of turnover)** | {{ "%.1f" | format(sanction_exposure.max_percentage * 100) }}% |
| **Potential Fine Amount** | €{{ sanction_exposure.potential_fine_eur | format_number }} |
| **Risk Level** | {{ sanction_exposure.risk_level }} |

**Note:** This is an estimate based on the NIS2 Directive sanction matrix. Actual sanctions are determined by competent authorities based on specific circumstances.
{% endif %}

---

## Appendix A: Device Configuration Snippets

{% for device in devices %}
{% if device.config and device.config.running_config %}
### {{ device.hostname or device.ip_address }}

```
{{ device.config.running_config[:1000] }}
{% if device.config.running_config | length > 1000 %}
... (truncated)
{% endif %}
```

{% endif %}
{% endfor %}

---

## Appendix B: Audit Methodology

This audit was conducted in accordance with the NIS2 Field Audit App methodology:

1. **Entity Classification** - Determined Essential/Important Entity status per NIS2 Articles 24-25
2. **Network Discovery** - Discovered devices via network scanning
3. **Device Interrogation** - Collected configuration data via SSH
4. **Gap Analysis** - Assessed configurations against NIS2 Article 21 requirements
5. **Compliance Scoring** - Weighted scoring across 6 domains
6. **Finding Generation** - Prioritized remediation recommendations

### Limitations

- This audit represents a point-in-time assessment
- Configuration data was collected from accessible devices only
- Some findings may require manual verification
- Sanction exposure is estimated based on generic criteria

---

## Signatures

**Auditor:** _________________________ Date: ___________

**Entity Representative:** _________________________ Date: ___________

---

*Report generated by NIS2 Field Audit App v0.1.0*  
*Directive (EU) 2022/2555 Compliance Assessment*
