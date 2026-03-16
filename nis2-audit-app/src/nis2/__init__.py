"""
NIS2 Compliance Assessment - Simplified Package
"""
from .models import (
    EntityInput,
    EntityClassification,
    AuditResult,
    GapAnalysis,
    Finding,
    CrossBorderInfo
)
from .classifier import classify_entity, check_national_designation
from .audit import run_audit, run_gap_analysis, generate_remediation_plan
from .report import generate_markdown_report, generate_json_report

__version__ = "2.0.0"
__all__ = [
    "EntityInput",
    "EntityClassification", 
    "AuditResult",
    "GapAnalysis",
    "Finding",
    "CrossBorderInfo",
    "classify_entity",
    "check_national_designation",
    "run_audit",
    "run_gap_analysis",
    "generate_remediation_plan",
    "generate_markdown_report",
    "generate_json_report",
]
