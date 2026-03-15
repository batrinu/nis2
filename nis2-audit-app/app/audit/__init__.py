"""
NIS2 Audit Engine - Article 21 compliance assessment.
"""
from .checklist import (
    ChecklistSection,
    ChecklistQuestion,
    ChecklistOption,
    ComplianceStatus,
    get_checklist_sections,
    get_all_questions,
    get_question_by_id,
    calculate_domain_weight,
)
from .scorer import ComplianceScorer, format_score_report
from .gap_analyzer import GapAnalyzer, DeviceConfigAnalyzer, DeviceGap
from .finding_generator import FindingGenerator, prioritize_findings, get_findings_summary

__all__ = [
    # Checklist
    "ChecklistSection",
    "ChecklistQuestion",
    "ChecklistOption",
    "ComplianceStatus",
    "get_checklist_sections",
    "get_all_questions",
    "get_question_by_id",
    "calculate_domain_weight",
    # Scorer
    "ComplianceScorer",
    "format_score_report",
    # Gap Analyzer
    "GapAnalyzer",
    "DeviceConfigAnalyzer",
    "DeviceGap",
    # Finding Generator
    "FindingGenerator",
    "prioritize_findings",
    "get_findings_summary",
]
