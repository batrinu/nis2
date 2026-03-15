"""
Audit Assessor Agent for NIS2 compliance assessment.
Executes comprehensive 5-phase audit methodology.
"""
from typing import Optional, Literal
from datetime import datetime, timezone
from shared.schemas import (
    EntityInput, EntityClassification, AuditAssessment, DomainScore, Finding
)
from shared.knowledge_base import NIS2KnowledgeBase
from agents.entity_classifier import EntityClassifier
from .phases import (
    Phase1Classification,
    Phase2Documentation,
    Phase3Technical,
    Phase4Interviews,
    Phase5Scoring,
)


class AuditAssessor:
    """
    Executes comprehensive 5-phase audit methodology for NIS2 compliance.
    """
    
    def __init__(
        self,
        classifier: Optional[EntityClassifier] = None,
        knowledge_base: Optional[NIS2KnowledgeBase] = None
    ):
        """Initialize with classifier and knowledge base."""
        self.kb = knowledge_base or NIS2KnowledgeBase()
        self.classifier = classifier or EntityClassifier(self.kb)
        
        # Initialize phases
        self.phase1 = Phase1Classification(self.classifier)
        self.phase2 = Phase2Documentation(self.kb)
        self.phase3 = Phase3Technical()
        self.phase4 = Phase4Interviews()
        self.phase5 = Phase5Scoring(self.kb)
    
    def execute_audit(
        self,
        entity_data: EntityInput,
        mode: Literal["full", "targeted", "follow-up"] = "full",
        documents: Optional[dict] = None,
        technical_evidence: Optional[dict] = None,
        interview_data: Optional[dict] = None
    ) -> dict:
        """
        Execute full 5-phase audit.
        
        Args:
            entity_data: Entity input data
            mode: Audit mode (full, targeted, follow-up)
            documents: Optional document bundle
            technical_evidence: Optional technical evidence
            interview_data: Optional interview responses
            
        Returns:
            Complete audit assessment
        """
        audit_id = f"AUD-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')}"
        
        # Phase 1: Entity Classification
        phase1_result = self.phase1.execute(entity_data)
        
        # Check for early exit
        if phase1_result["status"] == "early_exit":
            return {
                "audit_id": audit_id,
                "status": "not_required",
                "reason": phase1_result["reason"],
                "classification": phase1_result["classification"]
            }
        
        if phase1_result["status"] == "escalation_required":
            return {
                "audit_id": audit_id,
                "status": "escalation",
                "reason": phase1_result["reason"],
                "classification": phase1_result["classification"],
                "edge_cases": phase1_result["edge_cases"]
            }
        
        classification = phase1_result["classification"]
        
        # Phase 2: Documentation Review
        phase2_result = self.phase2.execute(entity_data, classification, documents)
        
        # Phase 3: Technical Assessment
        phase3_result = self.phase3.execute(entity_data, classification, technical_evidence)
        
        # Phase 4: Interview Simulation
        phase4_result = self.phase4.execute(entity_data, classification, interview_data)
        
        # Phase 5: Compliance Scoring
        phase_results = {
            "phase1": phase1_result,
            "phase2": phase2_result,
            "phase3": phase3_result,
            "phase4": phase4_result
        }
        phase5_result = self.phase5.execute(entity_data, classification, phase_results)
        
        # Compile final assessment
        return self._compile_assessment(
            audit_id=audit_id,
            entity_data=entity_data,
            classification=classification,
            phase_results=phase_results,
            phase5_result=phase5_result
        )
    
    def _compile_assessment(
        self,
        audit_id: str,
        entity_data: EntityInput,
        classification: EntityClassification,
        phase_results: dict,
        phase5_result: dict
    ) -> dict:
        """Compile final audit assessment."""
        return {
            "audit_id": audit_id,
            "entity_id": entity_data.entity_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "auditor_reference": "AUDITOR-001",
            
            # Phase results
            "phase_results": phase_results,
            
            # Overall results
            "overall_score": phase5_result["overall_score"],
            "rating": phase5_result["rating"],
            "domain_scores": phase5_result["domain_scores"],
            
            # Article mapping
            "article_21_mapping": phase5_result["article_21_mapping"],
            
            # Findings and recommendations
            "findings": phase5_result["findings"],
            "recommendations": phase5_result["recommendations"],
            
            # Next steps
            "next_audit_date": phase5_result["next_audit_date"],
            "escalation_required": phase5_result["escalation_required"],
            
            # Metadata
            "classification": classification.model_dump(),
            "cross_border_coordination": {
                "lead_authority": classification.lead_authority,
                "member_states": classification.cross_border.member_states if classification.cross_border else []
            }
        }
    
    def generate_checklist(self, entity_type: str) -> list[str]:
        """Generate pre-audit checklist based on entity classification."""
        base_checklist = [
            "Risk assessment report (last 12 months)",
            "Information security policy and supporting policies",
            "Incident response plan and procedures",
            "Business continuity and disaster recovery plans",
            "Asset inventory",
            "Access control policy and user access reviews",
            "Vulnerability management reports",
            "Penetration test reports (last 12 months)",
            "Cryptography/encryption policy",
            "Supply chain security documentation",
            "Staff security awareness training records",
            "Network architecture diagrams",
            "Previous audit reports (if applicable)"
        ]
        
        if entity_type == "Essential Entity":
            base_checklist.extend([
                "Sector-specific resilience plans",
                "Cross-border coordination procedures",
                "CSIRT coordination documentation"
            ])
        
        return base_checklist
