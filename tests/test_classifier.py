"""
Tests for Entity Classifier Agent.
"""
import pytest
from agents.entity_classifier import EntityClassifier
from shared.data.mock_entities import EE_ENERGY, IE_MANUFACTURING, IE_DIGITAL, NON_QUALIFYING


class TestEntityClassifier:
    """Test cases for entity classification."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.classifier = EntityClassifier()
    
    def test_classify_essential_entity_energy(self):
        """Test classification of essential entity in energy sector."""
        result = self.classifier.classify(EE_ENERGY)
        
        assert result.classification == "Essential Entity"
        assert result.annex == "Annex I"
        assert result.sector_classification == "energy"
        assert result.size_qualification is True
        assert result.confidence_score > 0.7
    
    def test_classify_important_entity_manufacturing(self):
        """Test classification of important entity in manufacturing."""
        result = self.classifier.classify(IE_MANUFACTURING)
        
        assert result.classification == "Important Entity"
        assert result.annex == "Annex II"
        assert result.sector_classification == "manufacturing"
        assert result.size_qualification is True
    
    def test_classify_important_entity_digital(self):
        """Test classification of important entity (digital infrastructure is actually EE)."""
        result = self.classifier.classify(IE_DIGITAL)
        
        # Digital infrastructure is Annex I (Essential Entity)
        assert result.classification == "Essential Entity"
        assert result.annex == "Annex I"
    
    def test_classify_non_qualifying(self):
        """Test classification of non-qualifying entity."""
        result = self.classifier.classify(NON_QUALIFYING)
        
        assert result.classification == "Non-Qualifying"
        assert result.size_qualification is False
    
    def test_cross_border_lead_authority(self):
        """Test lead authority determination for cross-border entity."""
        result = self.classifier.classify(EE_ENERGY)
        
        # Nordic Power Grid operates in NO, SE, DK with main establishment in NO
        assert result.lead_authority == "NO"
        assert result.cross_border.operates_cross_border is True
    
    def test_legal_basis_citation(self):
        """Test that legal basis is properly cited."""
        result = self.classifier.classify(EE_ENERGY)
        
        assert "Directive (EU) 2022/2555" in result.legal_basis
        assert "Article 24" in result.legal_basis
    
    def test_confidence_calculation(self):
        """Test confidence score calculation."""
        result = self.classifier.classify(EE_ENERGY)
        
        assert 0.0 <= result.confidence_score <= 1.0
        assert len(result.reasoning_chain) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
