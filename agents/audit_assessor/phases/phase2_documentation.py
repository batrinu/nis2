"""
Phase 2: Documentation Review for Audit Assessment.
Evaluates ISMS alignment and policy framework.
"""
from typing import Optional
from shared.schemas import EntityInput, EntityClassification
from shared.knowledge_base import NIS2KnowledgeBase
from .checklists import Article21Checklist


class Phase2Documentation:
    """Phase 2: Documentation Review."""
    
    def __init__(self, knowledge_base: Optional[NIS2KnowledgeBase] = None):
        """Initialize with knowledge base."""
        self.kb = knowledge_base or NIS2KnowledgeBase()
        self.checklist = Article21Checklist()
    
    def execute(
        self,
        entity_data: EntityInput,
        classification: EntityClassification,
        documents: Optional[dict] = None
    ) -> dict:
        """
        Execute documentation review phase.
        
        Args:
            entity_data: Entity input data
            classification: Entity classification result
            documents: Optional document bundle for review
            
        Returns:
            Phase result with documentation assessment
        """
        # In a real implementation, this would review actual documents
        # For now, return a structured assessment framework
        
        assessments = self._assess_documentation(documents or {})
        
        return {
            "phase": "documentation_review",
            "status": "complete",
            "entity_id": entity_data.entity_id,
            "classification": classification.classification,
            
            # ISMS alignment
            "isms_alignment": {
                "risk_assessment": assessments.get("risk_assessment", {}),
                "security_policy": assessments.get("security_policy", {}),
                "access_control": assessments.get("access_control", {}),
                "cryptography": assessments.get("cryptography", {}),
                "physical_security": assessments.get("physical_security", {}),
                "operations_security": assessments.get("operations_security", {}),
                "incident_management": assessments.get("incident_management", {}),
                "business_continuity": assessments.get("business_continuity", {}),
            },
            
            # Risk management documentation
            "risk_management": {
                "risk_register_completeness": assessments.get("risk_register", {}).get("score", 0),
                "risk_coverage": assessments.get("risk_coverage", {}).get("score", 0),
                "treatment_plan_quality": assessments.get("treatment_plan", {}).get("score", 0),
                "review_frequency": assessments.get("review_frequency", {}).get("score", 0)
            },
            
            # Policy framework
            "policy_framework": {
                "policies_present": assessments.get("policies_present", []),
                "policies_outdated": assessments.get("policies_outdated", []),
                "policies_missing": assessments.get("policies_missing", []),
                "approval_status": assessments.get("approval_status", {}),
                "review_cycle_compliance": assessments.get("review_cycles", {}).get("score", 0)
            },
            
            # Article 21 mapping
            "article_21_compliance": self._map_to_article21(assessments),
            
            # Score
            "documentation_score": self._calculate_score(assessments),
            "findings": self._generate_findings(assessments)
        }
    
    def _assess_documentation(self, documents: dict) -> dict:
        """Assess documentation against requirements."""
        # Placeholder implementation
        # In real scenario, would analyze actual documents
        return {
            "risk_assessment": {"present": True, "score": 75, "last_updated": "2023-06"},
            "security_policy": {"present": True, "score": 80, "approved": True},
            "access_control": {"present": True, "score": 85},
            "cryptography": {"present": True, "score": 70},
            "physical_security": {"present": True, "score": 75},
            "operations_security": {"present": True, "score": 80},
            "incident_management": {"present": True, "score": 78},
            "business_continuity": {"present": True, "score": 72},
            "risk_register": {"score": 75},
            "policies_present": [
                "Information Security Policy",
                "Access Control Policy",
                "Incident Response Policy",
                "Business Continuity Policy",
                "Cryptography Policy"
            ],
            "policies_missing": [
                "Supply Chain Security Policy"
            ]
        }
    
    def _map_to_article21(self, assessments: dict) -> dict:
        """Map documentation assessment to Article 21 requirements."""
        return {
            "21(2)(a)": {
                "status": "partially_compliant",
                "score": 75,
                "findings": ["Risk assessment present but methodology not fully documented"]
            },
            "21(2)(b)": {
                "status": "substantially_compliant",
                "score": 78,
                "findings": ["Incident response plan present, testing records incomplete"]
            },
            "21(2)(c)": {
                "status": "substantially_compliant",
                "score": 72,
                "findings": ["BCP present, RTO/RPO defined but not tested recently"]
            }
        }
    
    def _calculate_score(self, assessments: dict) -> float:
        """Calculate overall documentation score."""
        scores = [
            assessments.get("risk_assessment", {}).get("score", 0),
            assessments.get("security_policy", {}).get("score", 0),
            assessments.get("access_control", {}).get("score", 0),
            assessments.get("cryptography", {}).get("score", 0),
            assessments.get("physical_security", {}).get("score", 0),
            assessments.get("operations_security", {}).get("score", 0),
            assessments.get("incident_management", {}).get("score", 0),
            assessments.get("business_continuity", {}).get("score", 0),
        ]
        return sum(scores) / len(scores) if scores else 0.0
    
    def _generate_findings(self, assessments: dict) -> list[dict]:
        """Generate findings from documentation assessment."""
        findings = []
        
        if "Supply Chain Security Policy" in assessments.get("policies_missing", []):
            findings.append({
                "id": "DOC-001",
                "severity": "Medium",
                "article": "21(2)(d)",
                "description": "Supply Chain Security Policy not documented",
                "recommendation": "Develop and approve supply chain security policy"
            })
        
        return findings
