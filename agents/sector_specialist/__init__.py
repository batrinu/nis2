"""
Sector Specialist Agent for NIS2 compliance assessment.
"""
from .validator import SectorSpecialist
from .domains import (
    BaseSectorValidator,
    ValidationResult,
    ValidationRule,
)

__all__ = [
    "SectorSpecialist",
    "BaseSectorValidator",
    "ValidationResult",
    "ValidationRule",
]
