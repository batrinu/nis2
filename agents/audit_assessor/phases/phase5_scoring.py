"""
Phase 5: Compliance Scoring for Audit Assessment.
Calculates weighted compliance scores and generates findings.
"""
from typing import Optional
from datetime import datetime, timezone, timedelta
from shared.schemas import (
    EntityInput, EntityClassification, DomainScore, Finding,
    Recommendation, AuditAssessment
)
from shared.knowledge_base import NIS2KnowledgeBase


class Phase5Scoring:
    """Phase 5: Compliance Scoring."""
    
    # Domain weights as per specification
    DOMAIN_WEIGHTS = {
        "governance": 0.20,
        "technical_controls": 0.25,
        "incident_response": 0.20,
        "supply_chain": 0.15,
        "documentation": 0.10,
        "management_oversight": 0.10
    }
    
    # Rating scale
    RATING_THRESHOLDS = {
        "Compliant": (90, 100),
        "Substantially Compliant": (75, 89),
        "Partially Compliant": (50, 74),
        "Non-Compliant": (0, 49)
    }
    
    def __init__(self, knowledge_base: Optional[NIS2KnowledgeBase] = None):
        """Initialize with knowledge base."""
        self.kb = knowledge_base or NIS2KnowledgeBase()
    
    def execute(
        self,
        entity_data: EntityInput,
        classification: EntityClassification,
        phase_results: dict
    ) -> dict:
        """
        Execute compliance scoring phase.
        
        Args:
            entity_data: Entity input data
            classification: Entity classification result
            phase_results: Results from previous phases
            
        Returns:
            Phase result with final compliance assessment
        """
        # Calculate domain scores from phase results
        domain_scores = self._calculate_domain_scores(phase_results)
        
        # Calculate overall score
        overall_score = self._calculate_overall_score(domain_scores)
        
        # Determine rating
        rating = self._determine_rating(overall_score)
        
        # Generate findings
        findings = self._compile_findings(phase_results)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(findings)
        
        # Article 21 mapping
        article_21_mapping = self._map_to_articles(domain_scores)
        
        return {
            "phase": "compliance_scoring",
            "status": "complete",
            "entity_id": entity_data.entity_id,
            
            # Scores
            "overall_score": round(overall_score, 1),
            "rating": rating,
            "domain_scores": [
                {
                    "domain": name,
                    "weight": weight,
                    "score": score,
                    "rating": self._determine_rating(score)
                }
                for name, weight in self.DOMAIN_WEIGHTS.items()
                for score in [domain_scores.get(name, 0)]
            ],
            
            # Article mapping
            "article_21_mapping": article_21_mapping,
            
            # Findings and recommendations
            "findings": findings,
            "recommendations": recommendations,
            
            # Next steps
            "next_audit_date": self._calculate_next_audit(rating),
            "escalation_required": rating == "Non-Compliant"
        }
    
    def _calculate_domain_scores(self, phase_results: dict) -> dict[str, float]:
        """Calculate scores for each compliance domain."""
        scores = {}
        
        # Map phase results to domains
        # Phase 2: Documentation Review
        doc_score = phase_results.get("phase2", {}).get("documentation_score", 0)
        
        # Phase 3: Technical Assessment
        tech_score = phase_results.get("phase3", {}).get("technical_score", 0)
        
        # Phase 4: Interviews
        mgmt_score = phase_results.get("phase4", {}).get("management_score", 0)
        
        # Distribute scores across domains
        scores["governance"] = doc_score * 0.7 + mgmt_score * 0.3
        scores["technical_controls"] = tech_score
        scores["incident_response"] = phase_results.get("phase2", {}).get(
            "article_21_compliance", {}
        ).get("21(2)(b)", {}).get("score", 70)
        scores["supply_chain"] = phase_results.get("phase2", {}).get(
            "article_21_compliance", {}
        ).get("21(2)(d)", {}).get("score", 65)
        scores["documentation"] = doc_score
        scores["management_oversight"] = mgmt_score
        
        return scores
    
    def _calculate_overall_score(self, domain_scores: dict[str, float]) -> float:
        """Calculate weighted overall score."""
        total = 0.0
        for domain, weight in self.DOMAIN_WEIGHTS.items():
            score = domain_scores.get(domain, 0)
            total += score * weight
        return total
    
    def _determine_rating(self, score: float) -> str:
        """Determine compliance rating from score."""
        for rating, (min_score, max_score) in self.RATING_THRESHOLDS.items():
            if min_score <= score <= max_score:
                return rating
        return "Non-Compliant"
    
    def _compile_findings(self, phase_results: dict) -> list[dict]:
        """Compile findings from all phases."""
        findings = []
        
        # Collect from each phase
        for phase_name in ["phase2", "phase3", "phase4"]:
            phase = phase_results.get(phase_name, {})
            phase_findings = phase.get("findings", [])
            findings.extend(phase_findings)
        
        return findings
    
    def _generate_recommendations(self, findings: list[dict]) -> list[dict]:
        """Generate recommendations from findings."""
        recommendations = []
        
        for finding in findings:
            rec = {
                "recommendation_id": f"REC-{finding.get('id', '000').split('-')[1]}",
                "finding_id": finding.get("id"),
                "priority": self._severity_to_priority(finding.get("severity", "Medium")),
                "description": finding.get("recommendation", ""),
                "article_reference": finding.get("article", "21(2)(a)"),
                "deadline": self._calculate_deadline(finding.get("severity", "Medium"))
            }
            recommendations.append(rec)
        
        return recommendations
    
    def _map_to_articles(self, domain_scores: dict) -> dict:
        """Map domain scores to Article 21 requirements."""
        article_mapping = {
            "21(2)(a)": {
                "domain": "governance",
                "status": self._score_to_status(domain_scores.get("governance", 0)),
                "score": domain_scores.get("governance", 0)
            },
            "21(2)(b)": {
                "domain": "incident_response",
                "status": self._score_to_status(domain_scores.get("incident_response", 0)),
                "score": domain_scores.get("incident_response", 0)
            },
            "21(2)(c)": {
                "domain": "technical_controls",
                "status": self._score_to_status(domain_scores.get("technical_controls", 0)),
                "score": domain_scores.get("technical_controls", 0)
            },
            "21(2)(d)": {
                "domain": "supply_chain",
                "status": self._score_to_status(domain_scores.get("supply_chain", 0)),
                "score": domain_scores.get("supply_chain", 0)
            }
        }
        return article_mapping
    
    def _score_to_status(self, score: float) -> str:
        """Convert score to compliance status."""
        if score >= 90:
            return "compliant"
        elif score >= 75:
            return "substantially_compliant"
        elif score >= 50:
            return "partially_compliant"
        return "non_compliant"
    
    def _severity_to_priority(self, severity: str) -> str:
        """Convert severity to priority."""
        mapping = {
            "Critical": "immediate",
            "High": "high",
            "Medium": "medium",
            "Low": "low"
        }
        return mapping.get(severity, "medium")
    
    def _calculate_deadline(self, severity: str) -> str:
        """Calculate remediation deadline based on severity."""
        days = {
            "Critical": 30,
            "High": 90,
            "Medium": 180,
            "Low": 365
        }.get(severity, 180)
        
        deadline = datetime.now(timezone.utc) + timedelta(days=days)
        return deadline.strftime("%Y-%m-%d")
    
    def _calculate_next_audit(self, rating: str) -> str:
        """Calculate next audit date based on rating."""
        months = {
            "Compliant": 24,
            "Substantially Compliant": 18,
            "Partially Compliant": 12,
            "Non-Compliant": 6
        }.get(rating, 12)
        
        next_date = datetime.now(timezone.utc) + timedelta(days=30*months)
        return next_date.strftime("%Y-%m-%d")
