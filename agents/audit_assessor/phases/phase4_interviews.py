"""
Phase 4: Interview Simulation for Audit Assessment.
Evaluates CISO competency and board accountability.
"""
from typing import Optional
from datetime import datetime
from shared.schemas import EntityInput, EntityClassification


class Phase4Interviews:
    """Phase 4: Interview Simulation."""
    
    def __init__(self):
        """Initialize interview simulator."""
        self.ciso_questions = self._get_ciso_questions()
        self.board_questions = self._get_board_questions()
    
    def execute(
        self,
        entity_data: EntityInput,
        classification: EntityClassification,
        interview_data: Optional[dict] = None
    ) -> dict:
        """
        Execute interview simulation phase.
        
        Args:
            entity_data: Entity input data
            classification: Entity classification result
            interview_data: Optional interview responses
            
        Returns:
            Phase result with interview assessment
        """
        data = interview_data or {}
        
        # CISO competency assessment
        ciso_results = self._assess_ciso(data.get("ciso_responses", {}))
        
        # Board accountability assessment
        board_results = self._assess_board(data.get("board_responses", {}))
        
        return {
            "phase": "interview_simulation",
            "status": "complete",
            "entity_id": entity_data.entity_id,
            
            # CISO competency
            "ciso_competency": {
                "overall_score": ciso_results["overall_score"],
                "rating": ciso_results["rating"],
                "assessment_areas": {
                    "strategic_knowledge": ciso_results.get("strategic", {}),
                    "operational_knowledge": ciso_results.get("operational", {}),
                    "regulatory_knowledge": ciso_results.get("regulatory", {})
                },
                "question_responses": ciso_results.get("responses", []),
                "strengths": ciso_results.get("strengths", []),
                "development_areas": ciso_results.get("development_areas", [])
            },
            
            # Board accountability
            "board_accountability": {
                "overall_score": board_results["overall_score"],
                "rating": board_results["rating"],
                "accountability_indicators": {
                    "named_cyber_owner": board_results.get("named_owner", False),
                    "board_reporting_frequency": board_results.get("reporting_freq", "quarterly"),
                    "risk_register_inclusion": board_results.get("risk_register", True),
                    "defined_risk_appetite": board_results.get("risk_appetite", True),
                    "incident_notification_defined": board_results.get("incident_notification", True)
                },
                "question_responses": board_results.get("responses", []),
                "governance_maturity": board_results.get("maturity", "developing")
            },
            
            # Combined score
            "management_score": self._calculate_management_score(
                ciso_results, board_results
            ),
            "findings": self._generate_findings(ciso_results, board_results)
        }
    
    def _get_ciso_questions(self) -> list[dict]:
        """Get CISO interview questions."""
        return [
            {
                "id": "CISO-001",
                "category": "strategic",
                "question": "Describe your cybersecurity strategy and how it aligns with NIS2 Article 21",
                "assessment_criteria": "Understanding of NIS2, strategic alignment, risk-based approach"
            },
            {
                "id": "CISO-002",
                "category": "strategic",
                "question": "What metrics do you report to the board and how frequently?",
                "assessment_criteria": "Appropriate metrics, regular reporting, business alignment"
            },
            {
                "id": "CISO-003",
                "category": "operational",
                "question": "Walk me through your last tabletop exercise",
                "assessment_criteria": "Exercise design, participation, lessons learned, improvements"
            },
            {
                "id": "CISO-004",
                "category": "operational",
                "question": "How do you validate the effectiveness of your security controls?",
                "assessment_criteria": "Testing methods, metrics, continuous improvement"
            },
            {
                "id": "CISO-005",
                "category": "regulatory",
                "question": "What constitutes a 'significant incident' under NIS2 Article 23?",
                "assessment_criteria": "Knowledge of thresholds, reporting timelines, procedures"
            },
            {
                "id": "CISO-006",
                "category": "regulatory",
                "question": "Explain your reporting timeline to the competent authority",
                "assessment_criteria": "24h/72h/1 month understanding, CSIRT coordination"
            }
        ]
    
    def _get_board_questions(self) -> list[dict]:
        """Get Board interview questions."""
        return [
            {
                "id": "BOARD-001",
                "question": "Who has ultimate accountability for cybersecurity risk?",
                "assessment_criteria": "Clear ownership at board/senior level"
            },
            {
                "id": "BOARD-002",
                "question": "How frequently does the board review cybersecurity matters?",
                "assessment_criteria": "Regular reviews (quarterly minimum), formal agenda items"
            },
            {
                "id": "BOARD-003",
                "question": "What is the board's understanding of NIS2 compliance obligations?",
                "assessment_criteria": "Awareness of requirements, potential sanctions"
            },
            {
                "id": "BOARD-004",
                "question": "Describe the budget approval process for security investments",
                "assessment_criteria": "Appropriate budget process, security prioritization"
            },
            {
                "id": "BOARD-005",
                "question": "How are cybersecurity risks integrated into enterprise risk management?",
                "assessment_criteria": "ERM integration, risk appetite, board reporting"
            }
        ]
    
    def _assess_ciso(self, responses: dict) -> dict:
        """Assess CISO competency from responses."""
        # Placeholder scoring
        scores = {
            "strategic": {"score": 8, "max": 10},
            "operational": {"score": 7, "max": 10},
            "regulatory": {"score": 9, "max": 10}
        }
        
        total_score = sum(s["score"] for s in scores.values())
        max_score = sum(s["max"] for s in scores.values())
        percentage = (total_score / max_score) * 100
        
        rating = "Expert" if percentage >= 90 else \
                 "Proficient" if percentage >= 70 else \
                 "Basic" if percentage >= 50 else "Inadequate"
        
        return {
            "overall_score": round(percentage, 1),
            "rating": rating,
            "strategic": scores["strategic"],
            "operational": scores["operational"],
            "regulatory": scores["regulatory"],
            "strengths": ["Regulatory knowledge", "Strategic thinking"],
            "development_areas": ["Operational metrics"]
        }
    
    def _assess_board(self, responses: dict) -> dict:
        """Assess board accountability from responses."""
        # Placeholder scoring
        indicators = {
            "named_owner": True,
            "reporting_freq": "quarterly",
            "risk_register": True,
            "risk_appetite": True,
            "incident_notification": True
        }
        
        score = sum([
            20 if indicators["named_owner"] else 0,
            20 if indicators["reporting_freq"] in ["monthly", "quarterly"] else 10,
            20 if indicators["risk_register"] else 0,
            20 if indicators["risk_appetite"] else 0,
            20 if indicators["incident_notification"] else 0
        ])
        
        rating = "Mature" if score >= 90 else \
                 "Developing" if score >= 70 else \
                 "Basic" if score >= 50 else "Immature"
        
        return {
            "overall_score": score,
            "rating": rating,
            **indicators,
            "maturity": rating.lower()
        }
    
    def _calculate_management_score(
        self,
        ciso_results: dict,
        board_results: dict
    ) -> float:
        """Calculate combined management score."""
        return round((ciso_results["overall_score"] + board_results["overall_score"]) / 2, 1)
    
    def _generate_findings(
        self,
        ciso_results: dict,
        board_results: dict
    ) -> list[dict]:
        """Generate findings from interview assessment."""
        findings = []
        
        if ciso_results["overall_score"] < 70:
            findings.append({
                "id": "MGMT-001",
                "severity": "High",
                "article": "21(2)(h)",
                "description": "CISO competency assessment indicates gaps in cybersecurity knowledge",
                "recommendation": "Provide NIS2-specific training and professional development"
            })
        
        if board_results["overall_score"] < 70:
            findings.append({
                "id": "MGMT-002",
                "severity": "Medium",
                "article": "21(2)(g)",
                "description": "Board accountability for cybersecurity requires strengthening",
                "recommendation": "Establish formal board cybersecurity committee"
            })
        
        return findings
