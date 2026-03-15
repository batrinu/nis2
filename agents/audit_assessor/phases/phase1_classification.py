"""
Phase 1: Entity Classification for Audit Assessment.
Delegates to Entity Classifier Agent.
"""
from typing import Optional
from shared.schemas import EntityInput, EntityClassification
from agents.entity_classifier import EntityClassifier


class Phase1Classification:
    """Phase 1: Entity Classification."""
    
    def __init__(self, classifier: Optional[EntityClassifier] = None):
        """Initialize with entity classifier."""
        self.classifier = classifier or EntityClassifier()
    
    def execute(self, entity_data: EntityInput) -> dict:
        """
        Execute entity classification phase.
        
        Args:
            entity_data: Raw entity data
            
        Returns:
            Phase result with classification or early exit
        """
        # Perform classification
        classification = self.classifier.classify(entity_data)
        
        # Check for early exit conditions
        if classification.classification == "Non-Qualifying":
            return {
                "phase": "classification",
                "status": "early_exit",
                "reason": "Non-qualifying entity - audit not required",
                "classification": classification,
                "recommendation": "General cybersecurity advisory available upon request"
            }
        
        if classification.confidence_score < 0.70:
            return {
                "phase": "classification",
                "status": "escalation_required",
                "reason": "Classification confidence below threshold",
                "classification": classification,
                "edge_cases": classification.edge_cases,
                "recommendation": "Manual review required before proceeding with audit"
            }
        
        # Successful classification
        return {
            "phase": "classification",
            "status": "complete",
            "classification": classification,
            "entity_type": classification.classification,
            "legal_basis": classification.legal_basis,
            "confidence": classification.confidence_score,
            "lead_authority": classification.lead_authority
        }
