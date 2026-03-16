"""Basic tests for NIS2 module."""
import pytest
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from nis2 import (
    classify_entity,
    run_audit,
    EntityInput,
    CrossBorderInfo
)


def test_essential_entity_classification():
    """Test Essential Entity classification."""
    entity = EntityInput(
        legal_name="Energy Corp",
        sector="energy",
        employee_count=150,
        annual_turnover_eur=25000000,
        cross_border_operations=CrossBorderInfo(
            operates_cross_border=False,
            main_establishment="RO"
        )
    )
    
    result = classify_entity(entity)
    
    assert result.classification == "Essential Entity"
    assert result.annex == "Annex I"
    assert result.lead_authority == "RO"
    assert result.confidence_score > 0.8


def test_important_entity_classification():
    """Test Important Entity classification."""
    entity = EntityInput(
        legal_name="Manufacturing Ltd",
        sector="manufacturing",
        employee_count=80,
        annual_turnover_eur=12000000,
        cross_border_operations=CrossBorderInfo(
            operates_cross_border=False,
            main_establishment="DE"
        )
    )
    
    result = classify_entity(entity)
    
    assert result.classification == "Important Entity"
    assert result.annex == "Annex II"


def test_non_qualifying_classification():
    """Test Non-Qualifying classification."""
    entity = EntityInput(
        legal_name="Small Business",
        sector="energy",
        employee_count=10,
        annual_turnover_eur=500000,
        cross_border_operations=CrossBorderInfo(
            operates_cross_border=False,
            main_establishment="FR"
        )
    )
    
    result = classify_entity(entity)
    
    assert result.classification == "Non-Qualifying"


def test_audit_generation():
    """Test audit report generation."""
    entity = EntityInput(
        legal_name="Test Corp",
        sector="energy",
        employee_count=100,
        annual_turnover_eur=20000000,
        cross_border_operations=CrossBorderInfo(
            operates_cross_border=False,
            main_establishment="RO"
        )
    )
    
    classification = classify_entity(entity)
    audit = run_audit(entity, classification)
    
    assert audit.entity_id is not None
    assert 0 <= audit.overall_score <= 100
    assert audit.rating in ["Compliant", "Substantially Compliant", "Partially Compliant", "Non-Compliant"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
