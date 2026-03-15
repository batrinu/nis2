"""
Base class for sector-specific validators.
"""
from abc import ABC, abstractmethod
from typing import Optional, Callable
from dataclasses import dataclass, field
from pydantic import BaseModel

from shared.schemas import EntityInput


@dataclass
class ValidationRule:
    """Definition of a validation rule."""
    name: str
    description: str
    validation_fn: Callable
    required: bool = True
    applies_to: Optional[list[str]] = None


@dataclass
class ValidationResult:
    """Result of a validation check."""
    rule_name: str
    passed: bool
    score: float  # 0.0-100.0
    findings: list[str] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)
    evidence: list[str] = field(default_factory=list)


class SectorValidationSummary(BaseModel):
    """Summary of sector-specific validation."""
    sector_code: str
    sector_name: str
    annex: str
    overall_score: float
    compliance_level: str  # "Compliant", "Substantially", "Partially", "Non-Compliant"
    validation_results: list[dict]
    cross_regulatory_frameworks: list[str]
    specific_requirements: list[str]


class BaseSectorValidator(ABC):
    """Base class for all sector validators."""
    
    SECTOR_CODE: str = ""
    SECTOR_NAME: str = ""
    ANNEX: str = ""  # "Annex_I" or "Annex_II"
    SIZE_EXCEPTION: bool = False  # True for DNS/TLD/etc
    
    # Cross-regulatory frameworks this sector overlaps with
    CROSS_REGULATORY_FRAMEWORKS: list[str] = []
    
    def __init__(self):
        """Initialize validator."""
        self.validation_results: list[ValidationResult] = []
    
    @abstractmethod
    def validate(self, entity: EntityInput) -> SectorValidationSummary:
        """Execute all sector-specific validations."""
        pass
    
    def get_legal_citations(self) -> list[str]:
        """Return applicable legal citations for sector."""
        citations = [f"NIS2 {self.ANNEX}", f"NIS2 Article 21"]
        if self.SIZE_EXCEPTION:
            citations.append("Article 24(2) - Size exception")
        return citations
    
    def get_cross_regulatory_frameworks(self) -> list[str]:
        """Return intersecting regulations."""
        return self.CROSS_REGULATORY_FRAMEWORKS
    
    def _run_checks(
        self,
        checks: list[tuple[str, Callable]],
        entity: EntityInput
    ) -> list[ValidationResult]:
        """Execute validation checks and compile results."""
        results = []
        for name, check_fn in checks:
            try:
                result = check_fn(entity)
                results.append(result)
            except Exception as e:
                results.append(ValidationResult(
                    rule_name=name,
                    passed=False,
                    score=0.0,
                    findings=[f"Validation error: {str(e)}"]
                ))
        return results
    
    def _calculate_overall_score(self, results: list[ValidationResult]) -> float:
        """Calculate overall score from individual results."""
        if not results:
            return 0.0
        total = sum(r.score for r in results)
        return round(total / len(results), 2)
    
    def _determine_compliance_level(self, score: float) -> str:
        """Determine compliance level from score."""
        if score >= 90:
            return "Compliant"
        elif score >= 75:
            return "Substantially Compliant"
        elif score >= 50:
            return "Partially Compliant"
        else:
            return "Non-Compliant"
