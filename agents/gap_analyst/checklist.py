"""
Gap Analyst Agent for NIS2 compliance assessment.
Pre-audit readiness evaluation and consulting preparation.
"""
from typing import Optional, Literal
from datetime import datetime, timezone
from shared.schemas import (
    EntityInput, EntityClassification, GapAnalysisReport,
    DomainScore, RemediationItem
)
from shared.knowledge_base import NIS2KnowledgeBase


class QuestionBank:
    """Pre-loaded question bank for gap analysis."""
    
    QUESTIONS = {
        "governance": [
            {
                "id": "Q1",
                "question": "Is there a board member or senior executive with explicit accountability for cybersecurity risk?",
                "scoring": {"5": "Named C-suite owner, board reporting quarterly+",
                           "3": "Named owner, reports annually",
                           "1": "No clear ownership"}
            },
            {
                "id": "Q2",
                "question": "When was your last comprehensive cybersecurity risk assessment conducted?",
                "scoring": {"5": "Within 6 months, methodology documented",
                           "3": "Within 12 months",
                           "1": "Over 12 months or no assessment"}
            },
            {
                "id": "Q3",
                "question": "How many of the required policies do you have documented and approved?",
                "scoring": {"5": "All 6 current and approved",
                           "3": "4-5 policies",
                           "1": "<4 policies"}
            }
        ],
        "technical": [
            {
                "id": "Q6",
                "question": "Provide your vulnerability scanning frequency and average time to remediate critical vulnerabilities.",
                "scoring": {"5": "Continuous scanning, <7 days MTTR",
                           "3": "Weekly scanning, <30 days MTTR",
                           "1": "Monthly or less, >30 days MTTR"}
            },
            {
                "id": "Q7",
                "question": "Show evidence of your last penetration test and remediation status.",
                "scoring": {"5": "Annual external test, all criticals remediated",
                           "3": "Annual test, some open findings",
                           "1": "No recent test"}
            },
            {
                "id": "Q8",
                "question": "What encryption standards are applied to sensitive data at rest and in transit?",
                "scoring": {"5": "AES-256 at rest, TLS 1.3 in transit, HSM for keys",
                           "3": "Industry standard encryption",
                           "1": "Weak or no encryption"}
            },
            {
                "id": "Q9",
                "question": "What percentage of users and administrative accounts have MFA enforced?",
                "scoring": {"5": "100% admin, >95% users",
                           "3": "100% admin, <95% users",
                           "1": "Partial or no MFA"}
            }
        ],
        "incident_response": [
            {
                "id": "Q11",
                "question": "Provide documentation of your last three incident response tabletop exercises.",
                "scoring": {"5": "Quarterly exercises, documented, improved",
                           "3": "Annual exercises",
                           "1": "No exercises"}
            },
            {
                "id": "Q12",
                "question": "Show your incident response plan including escalation procedures.",
                "scoring": {"5": "Detailed plan, tested, includes NIS2 reporting",
                           "3": "Plan exists, not recently tested",
                           "1": "No formal plan"}
            },
            {
                "id": "Q15",
                "question": "What are the NIS2 reporting timelines for significant incidents?",
                "scoring": {"5": "24h/72h/1 month",
                           "3": "General awareness of timelines",
                           "1": "Unaware"}
            }
        ],
        "supply_chain": [
            {
                "id": "Q16",
                "question": "Show your inventory of critical ICT suppliers.",
                "scoring": {"5": "Comprehensive inventory, risk-rated",
                           "3": "Basic inventory",
                           "1": "No inventory"}
            },
            {
                "id": "Q17",
                "question": "Provide evidence of security assessments for top 3 critical suppliers.",
                "scoring": {"5": "Recent assessments, documented controls",
                           "3": "Some assessments",
                           "1": "No assessments"}
            },
            {
                "id": "Q18",
                "question": "Show security requirements in a recent critical supplier contract.",
                "scoring": {"5": "Detailed security clauses, audit rights",
                           "3": "Generic security mention",
                           "1": "No security requirements"}
            }
        ]
    }
    
    @classmethod
    def get_questions(cls, domain: Optional[str] = None) -> list[dict]:
        """Get questions, optionally filtered by domain."""
        if domain:
            return cls.QUESTIONS.get(domain, [])
        
        all_questions = []
        for domain_questions in cls.QUESTIONS.values():
            all_questions.extend(domain_questions)
        return all_questions


class GapAnalyst:
    """
    Conducts pre-audit readiness evaluation and consulting preparation.
    """
    
    def __init__(self, knowledge_base: Optional[NIS2KnowledgeBase] = None):
        """Initialize with knowledge base."""
        self.kb = knowledge_base or NIS2KnowledgeBase()
        self.question_bank = QuestionBank()
    
    def conduct_quick_scan(self, entity_data: EntityInput) -> dict:
        """
        Execute high-level maturity assessment.
        
        Args:
            entity_data: Entity input data
            
        Returns:
            Quick scan result
        """
        # Get key questions for quick scan
        questions = self._select_quick_scan_questions()
        
        # Simulate responses (in real scenario, would collect from user)
        responses = self._simulate_responses(questions)
        
        # Calculate maturity
        maturity = self._calculate_maturity(responses)
        
        # Identify priority areas
        priority_areas = self._identify_priority_areas(responses)
        
        return {
            "mode": "quick_scan",
            "entity_id": entity_data.entity_id,
            "overall_maturity": maturity,
            "compliance_readiness": maturity * 20,  # Convert 1-5 to %
            "priority_areas": priority_areas,
            "estimated_timeline": self._estimate_timeline(maturity),
            "question_responses": responses
        }
    
    def conduct_deep_dive(
        self,
        entity_data: EntityInput,
        evidence: Optional[dict] = None
    ) -> dict:
        """
        Execute comprehensive gap analysis.
        
        Args:
            entity_data: Entity input data
            evidence: Optional evidence bundle
            
        Returns:
            Deep dive gap analysis report
        """
        # Get all questions
        all_questions = self.question_bank.get_questions()
        
        # Simulate detailed responses
        responses = self._simulate_responses(all_questions, detailed=True)
        
        # Calculate domain scores
        domain_scores = self._calculate_domain_scores(responses)
        
        # Identify gaps
        gaps = self._identify_gaps(responses)
        
        # Generate roadmap
        roadmap = self._generate_roadmap(gaps)
        
        # Calculate overall
        overall_maturity = sum(domain_scores.values()) / len(domain_scores) if domain_scores else 1
        compliance_readiness = (overall_maturity / 5) * 100
        
        return {
            "mode": "deep_dive",
            "entity_id": entity_data.entity_id,
            "assessment_date": datetime.now(timezone.utc).isoformat(),
            "overall_maturity": round(overall_maturity, 1),
            "compliance_readiness": round(compliance_readiness, 1),
            "domain_scores": domain_scores,
            "gaps": gaps,
            "remediation_roadmap": roadmap,
            "estimated_timeline": self._estimate_timeline(overall_maturity),
            "total_effort_days": self._estimate_effort(gaps),
            "question_responses": responses
        }
    
    def get_question_bank(self, domain: str, mode: str) -> list[dict]:
        """Retrieve appropriate questions for assessment."""
        if mode == "quick_scan":
            # Return subset of questions
            return self.question_bank.get_questions(domain)[:3]
        return self.question_bank.get_questions(domain)
    
    def _select_quick_scan_questions(self) -> list[dict]:
        """Select questions for quick scan."""
        questions = []
        for domain in ["governance", "technical", "incident_response"]:
            domain_qs = self.question_bank.get_questions(domain)
            if domain_qs:
                questions.extend(domain_qs[:2])  # Top 2 per domain
        return questions
    
    def _simulate_responses(
        self,
        questions: list[dict],
        detailed: bool = False
    ) -> list[dict]:
        """Simulate responses (placeholder for actual data collection)."""
        import random
        responses = []
        for q in questions:
            score = random.randint(2, 5) if not detailed else random.randint(1, 5)
            responses.append({
                "question_id": q["id"],
                "question": q["question"],
                "score": score,
                "max_score": 5,
                "response": f"Simulated response with score {score}"
            })
        return responses
    
    def _calculate_maturity(self, responses: list[dict]) -> int:
        """Calculate maturity from responses."""
        if not responses:
            return 1
        avg_score = sum(r["score"] for r in responses) / len(responses)
        return round(avg_score)
    
    def _identify_priority_areas(self, responses: list[dict]) -> list[str]:
        """Identify priority areas from responses."""
        low_scores = [r for r in responses if r["score"] <= 2]
        return [f"Area requiring improvement: {r['question_id']}" for r in low_scores[:3]]
    
    def _calculate_domain_scores(self, responses: list[dict]) -> dict:
        """Calculate scores per domain."""
        # Group by domain
        domain_scores = {}
        for domain in ["governance", "technical", "incident_response", "supply_chain"]:
            domain_responses = [
                r for r in responses 
                if r["question_id"] in [q["id"] for q in self.question_bank.get_questions(domain)]
            ]
            if domain_responses:
                avg = sum(r["score"] for r in domain_responses) / len(domain_responses)
                domain_scores[domain] = round(avg, 1)
        return domain_scores
    
    def _identify_gaps(self, responses: list[dict]) -> list[dict]:
        """Identify compliance gaps from responses."""
        gaps = []
        for r in responses:
            if r["score"] < 3:
                gaps.append({
                    "gap_id": f"GAP-{r['question_id']}",
                    "description": f"Low score on: {r['question']}",
                    "current_score": r["score"],
                    "target_score": 4,
                    "domain": self._get_domain_for_question(r["question_id"]),
                    "priority": "high" if r["score"] == 1 else "medium"
                })
        return gaps
    
    def _generate_roadmap(self, gaps: list[dict]) -> dict:
        """Generate remediation roadmap."""
        quick_wins = [g for g in gaps if g["current_score"] >= 2]
        short_term = [g for g in gaps if g["current_score"] == 1 and g["priority"] == "medium"]
        medium_term = [g for g in gaps if g["priority"] == "high"]
        
        return {
            "quick_wins": [{"gap_id": g["gap_id"], "action": f"Address {g['description']}"} for g in quick_wins[:3]],
            "short_term": [{"gap_id": g["gap_id"], "action": f"Remediate {g['description']}"} for g in short_term[:3]],
            "medium_term": [{"gap_id": g["gap_id"], "action": f"Implement {g['description']}"} for g in medium_term[:3]],
            "total_items": len(gaps)
        }
    
    def _estimate_timeline(self, maturity: float) -> str:
        """Estimate timeline to compliance based on maturity."""
        if maturity >= 4:
            return "3-6 months"
        elif maturity >= 3:
            return "6-12 months"
        elif maturity >= 2:
            return "12-18 months"
        return "18-24 months"
    
    def _estimate_effort(self, gaps: list[dict]) -> int:
        """Estimate effort in days."""
        return len(gaps) * 5  # Rough estimate: 5 days per gap
    
    def _get_domain_for_question(self, question_id: str) -> str:
        """Get domain for a question ID."""
        for domain, questions in self.question_bank.QUESTIONS.items():
            if any(q["id"] == question_id for q in questions):
                return domain
        return "unknown"
    
    def estimate_effort(self, gap: dict) -> dict:
        """Calculate resource requirements for remediation."""
        return {
            "effort_days": 5 * (4 - gap["current_score"]),
            "internal_resources": 1,
            "external_resources": 0 if gap["current_score"] >= 3 else 1,
            "estimated_cost_range": (5000, 20000) if gap["priority"] == "high" else (2000, 10000)
        }
