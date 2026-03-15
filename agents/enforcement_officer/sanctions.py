"""
Enforcement Officer Agent for NIS2 compliance assessment.
Calculates sanctions and generates legal notices.
"""
from typing import Optional
from datetime import datetime, timezone, timedelta
from dataclasses import dataclass
from shared.schemas import (
    EntityInput, EntityClassification, AuditAssessment,
    Violation, Sanction, SanctionPackage, FineCalculation,
    ProportionalityFactors, ProportionalityAssessment,
    RemediationPlan, AppealRights, SanctionNotice
)
from shared.knowledge_base import NIS2KnowledgeBase


@dataclass
class ComplianceHistory:
    """Compliance history for proportionality calculations."""
    previous_violations: int = 0
    cooperation_level: str = "satisfactory"  # excellent, good, satisfactory, poor
    remediation_timeliness: float = 100.0  # percentage


class RedFlagDetector:
    """Detects red flags requiring immediate enforcement action."""
    
    FLAGS = {
        "NO_INCIDENT_RESPONSE": {
            "severity": "CRITICAL",
            "articles": ["21(2)(b)", "23"],
            "immediate_action": True,
            "base_fine_multiplier": 1.5,
            "description": "No incident response capability"
        },
        "UNENCRYPTED_SENSITIVE_DATA": {
            "severity": "CRITICAL",
            "articles": ["21(2)(i)"],
            "immediate_action": True,
            "base_fine_multiplier": 1.3,
            "description": "Unencrypted sensitive data"
        },
        "MISSING_BCP": {
            "severity": "HIGH",
            "articles": ["21(2)(c)"],
            "immediate_action": False,
            "base_fine_multiplier": 1.2,
            "description": "Missing business continuity plan"
        },
        "UNREGISTERED_ENTITY": {
            "severity": "HIGH",
            "articles": ["24", "25"],
            "immediate_action": False,
            "base_fine_multiplier": 1.0,
            "description": "Unregistered qualifying entity"
        },
        "NO_RISK_ASSESSMENT": {
            "severity": "HIGH",
            "articles": ["21(2)(a)"],
            "immediate_action": False,
            "base_fine_multiplier": 1.1,
            "description": "No risk assessment conducted"
        },
        "SIGNIFICANT_INCIDENT_UNREPORTED": {
            "severity": "CRITICAL",
            "articles": ["23(3)"],
            "immediate_action": True,
            "base_fine_multiplier": 1.4,
            "description": "Significant incident unreported"
        },
        "REPEATED_NON_COMPLIANCE": {
            "severity": "CRITICAL",
            "articles": ["34"],
            "immediate_action": True,
            "base_fine_multiplier": 2.0,
            "description": "Repeated non-compliance"
        }
    }
    
    def detect(self, audit_result: AuditAssessment) -> list[dict]:
        """Detect red flags from audit results."""
        flags = []
        
        for finding in audit_result.findings:
            flag = self._check_finding(finding)
            if flag:
                flags.append(flag)
        
        return flags
    
    def _check_finding(self, finding: dict) -> Optional[dict]:
        """Check if finding matches a red flag."""
        # Map findings to red flags
        if finding.get("severity") == "Critical":
            if "incident response" in finding.get("description", "").lower():
                return self.FLAGS["NO_INCIDENT_RESPONSE"]
            if "encryption" in finding.get("description", "").lower():
                return self.FLAGS["UNENCRYPTED_SENSITIVE_DATA"]
        
        return None


class ProportionalityEngine:
    """Calculates proportionality of sanctions."""
    
    FACTOR_WEIGHTS = {
        "gravity": 0.25,
        "duration": 0.10,
        "intentionality": 0.20,
        "harm_caused": 0.20,
        "cooperation": 0.15,
        "previous_compliance": 0.10
    }
    
    def calculate(
        self,
        violations: list[Violation],
        entity_context: dict,
        history: ComplianceHistory
    ) -> ProportionalityAssessment:
        """Calculate proportionality assessment."""
        
        factors = ProportionalityFactors(
            gravity=self._assess_gravity(violations),
            duration=self._assess_duration(violations),
            intentionality=self._assess_intentionality(violations),
            harm_caused=self._assess_harm(violations),
            cooperation=self._cooperation_score(history),
            previous_compliance=self._compliance_history_score(history),
            cross_border_impact=entity_context.get("cross_border_impact", 0.5),
            sector_criticality=entity_context.get("sector_criticality", 0.5),
            public_interest=entity_context.get("public_interest", 0.5)
        )
        
        severity = self._weighted_severity(factors)
        tier = self._determine_tier(severity, factors)
        
        return ProportionalityAssessment(
            severity_score=severity,
            sanction_tier=tier,
            factors=factors,
            reasoning=self._generate_reasoning(factors, tier)
        )
    
    def _assess_gravity(self, violations: list[Violation]) -> float:
        """Assess gravity of violations (0.0-1.0)."""
        if not violations:
            return 0.0
        
        severity_map = {"critical": 1.0, "high": 0.7, "medium": 0.4, "low": 0.2}
        scores = [severity_map.get(v.severity, 0.5) for v in violations]
        return sum(scores) / len(scores)
    
    def _assess_duration(self, violations: list[Violation]) -> float:
        """Assess duration of violations (0.0-1.0)."""
        # Default - assume moderate duration
        return 0.5
    
    def _assess_intentionality(self, violations: list[Violation]) -> float:
        """Assess intentionality (0.0-1.0)."""
        # Default - assume negligent rather than willful
        return 0.3
    
    def _assess_harm(self, violations: list[Violation]) -> float:
        """Assess harm caused (0.0-1.0)."""
        # Based on critical/high findings
        critical_count = sum(1 for v in violations if v.severity == "critical")
        if critical_count > 0:
            return 0.8
        high_count = sum(1 for v in violations if v.severity == "high")
        if high_count > 0:
            return 0.6
        return 0.3
    
    def _cooperation_score(self, history: ComplianceHistory) -> float:
        """Calculate cooperation score (0.0-1.0)."""
        mapping = {
            "excellent": 1.0,
            "good": 0.8,
            "satisfactory": 0.6,
            "poor": 0.3
        }
        return mapping.get(history.cooperation_level, 0.6)
    
    def _compliance_history_score(self, history: ComplianceHistory) -> float:
        """Calculate compliance history score (0.0-1.0)."""
        if history.previous_violations == 0:
            return 1.0
        elif history.previous_violations == 1:
            return 0.7
        elif history.previous_violations <= 3:
            return 0.4
        return 0.2
    
    def _weighted_severity(self, factors: ProportionalityFactors) -> float:
        """Calculate weighted severity score."""
        weighted = (
            factors.gravity * self.FACTOR_WEIGHTS["gravity"] +
            factors.duration * self.FACTOR_WEIGHTS["duration"] +
            factors.intentionality * self.FACTOR_WEIGHTS["intentionality"] +
            factors.harm_caused * self.FACTOR_WEIGHTS["harm_caused"] +
            factors.cooperation * self.FACTOR_WEIGHTS["cooperation"] +
            factors.previous_compliance * self.FACTOR_WEIGHTS["previous_compliance"]
        )
        return round(weighted, 2)
    
    def _determine_tier(
        self,
        severity: float,
        factors: ProportionalityFactors
    ) -> str:
        """Determine sanction tier from severity."""
        if severity < 0.3:
            return "warning"
        elif severity < 0.5:
            return "notice"
        elif severity < 0.7:
            return "moderate_fine"
        elif severity < 0.9:
            return "severe_fine"
        return "maximum"
    
    def _generate_reasoning(
        self,
        factors: ProportionalityFactors,
        tier: str
    ) -> str:
        """Generate proportionality reasoning text."""
        return (
            f"Sanction tier '{tier}' determined based on: "
            f"gravity={factors.gravity:.2f}, "
            f"intentionality={factors.intentionality:.2f}, "
            f"harm={factors.harm_caused:.2f}, "
            f"cooperation={factors.cooperation:.2f}, "
            f"history={factors.previous_compliance:.2f}. "
            f"Article 34(2) proportionality principles applied."
        )


class EnforcementOfficer:
    """
    Calculates sanctions and generates legal notices for NIS2 non-compliance.
    """
    
    def __init__(self, knowledge_base: Optional[NIS2KnowledgeBase] = None):
        """Initialize with knowledge base."""
        self.kb = knowledge_base or NIS2KnowledgeBase()
        self.red_flag_detector = RedFlagDetector()
        self.proportionality_engine = ProportionalityEngine()
    
    def detect_red_flags(self, audit_result: AuditAssessment) -> list[dict]:
        """Identify critical compliance failures requiring immediate action."""
        return self.red_flag_detector.detect(audit_result)
    
    def calculate_sanctions(
        self,
        violations: list[Violation],
        entity: EntityClassification,
        history: Optional[ComplianceHistory] = None
    ) -> SanctionPackage:
        """Calculate appropriate sanctions based on proportionality."""
        history = history or ComplianceHistory()
        
        # Calculate proportionality
        entity_context = {
            "cross_border_impact": 0.7 if entity.cross_border.operates_cross_border else 0.3,
            "sector_criticality": 0.8 if entity.classification == "Essential Entity" else 0.6,
            "public_interest": 0.7  # Default
        }
        
        proportionality = self.proportionality_engine.calculate(
            violations, entity_context, history
        )
        
        # Calculate fine if applicable
        fine_calc = None
        if proportionality.sanction_tier in ["moderate_fine", "severe_fine", "maximum"]:
            fine_calc = self._calculate_fine(
                entity, proportionality, violations, history
            )
        
        # Determine sanctions
        sanctions = self._determine_sanctions(proportionality, fine_calc)
        
        # Create remediation plan
        remediation = self._create_remediation_plan(violations)
        
        # Detect red flags
        red_flags = []
        for v in violations:
            if v.severity == "critical":
                red_flags.append(f"CRITICAL_VIOLATION: {v.violation_id}")
        
        return SanctionPackage(
            entity_id=entity.entity_id,
            violations=violations,
            sanctions=sanctions,
            proportionality=proportionality,
            remediation=remediation,
            fine_calculation=fine_calc,
            red_flags_detected=red_flags
        )
    
    def _calculate_fine(
        self,
        entity: EntityClassification,
        proportionality: ProportionalityAssessment,
        violations: list[Violation],
        history: ComplianceHistory
    ) -> FineCalculation:
        """Calculate administrative fine."""
        # Get thresholds
        thresholds = self.kb.get_fine_thresholds(entity.classification)
        
        turnover = entity.size_details.annual_turnover_eur
        base_max = min(
            thresholds["max_amount"],
            turnover * thresholds["max_percentage"]
        )
        
        # Severity adjustment
        severity_multiplier = 0.3 + (proportionality.severity_score * 0.7)
        
        # History multiplier
        history_multiplier = 1.0 + (history.previous_violations * 0.5)
        
        # Cooperation factor
        cooperation_map = {"excellent": 0.7, "good": 0.8, "satisfactory": 1.0, "poor": 1.2}
        cooperation_factor = cooperation_map.get(history.cooperation_level, 1.0)
        
        # Calculate proposed fine
        proposed = base_max * severity_multiplier * history_multiplier * cooperation_factor
        final_fine = min(proposed, base_max)
        
        return FineCalculation(
            proposed_fine_eur=round(final_fine, 2),
            maximum_possible=round(base_max, 2),
            percentage_of_max=round((final_fine / base_max) * 100, 1),
            calculation_breakdown={
                "base_maximum": base_max,
                "severity_multiplier": severity_multiplier,
                "history_multiplier": history_multiplier,
                "cooperation_factor": cooperation_factor
            }
        )
    
    def _determine_sanctions(
        self,
        proportionality: ProportionalityAssessment,
        fine_calc: Optional[FineCalculation]
    ) -> list[Sanction]:
        """Determine sanctions based on tier."""
        sanctions = []
        
        tier = proportionality.sanction_tier
        
        if tier == "warning":
            sanctions.append(Sanction(
                sanction_type="written_warning",
                description="Formal written warning with 30-day remediation window",
                conditions=["Remediate identified violations within 30 days"],
                deadline=(datetime.now(timezone.utc) + timedelta(days=30)).date()
            ))
        
        elif tier == "notice":
            sanctions.append(Sanction(
                sanction_type="formal_notice",
                description="Formal non-compliance notice issued",
                conditions=["Comply with specified requirements within 60 days"],
                deadline=(datetime.now(timezone.utc) + timedelta(days=60)).date()
            ))
        
        elif tier in ["moderate_fine", "severe_fine", "maximum"]:
            if fine_calc:
                sanctions.append(Sanction(
                    sanction_type="fine",
                    amount_eur=fine_calc.proposed_fine_eur,
                    description=f"Administrative fine of €{fine_calc.proposed_fine_eur:,.2f}",
                    conditions=["Payment within 30 days of notice", "Remediation of violations"]
                ))
        
        return sanctions
    
    def _create_remediation_plan(self, violations: list[Violation]) -> RemediationPlan:
        """Create remediation plan for violations."""
        actions = []
        
        for v in violations:
            actions.append({
                "violation_id": v.violation_id,
                "article": v.article_violated,
                "action": f"Remediate {v.description}",
                "deadline_days": 30 if v.severity == "critical" else 60
            })
        
        max_deadline = max(a["deadline_days"] for a in actions) if actions else 60
        
        return RemediationPlan(
            mandatory_actions=actions,
            deadline=(datetime.now(timezone.utc) + timedelta(days=max_deadline)).date(),
            verification_requirements="Independent audit verification required"
        )
    
    def generate_notice(
        self,
        sanction_package: SanctionPackage,
        entity: EntityClassification,
        competent_authority: str = "Competent Authority"
    ) -> SanctionNotice:
        """Generate formal enforcement notice."""
        
        appeal_deadline = (datetime.now(timezone.utc) + timedelta(days=30)).date()
        
        return SanctionNotice(
            notice_id=f"NOTICE-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')}",
            issue_date=datetime.now(timezone.utc),
            effective_date=datetime.now(timezone.utc),
            competent_authority=competent_authority,
            entity_name=entity.entity_id,  # Should be legal name
            entity_classification=entity.classification,
            entity_address="Address placeholder",
            violations=sanction_package.violations,
            legal_basis="Directive (EU) 2022/2555, Article 34",
            sanctions=sanction_package.sanctions,
            fine_calculation=sanction_package.fine_calculation,
            remediation_requirements=sanction_package.remediation,
            proportionality_assessment=sanction_package.proportionality,
            appeal_rights=AppealRights(
                appeal_deadline=appeal_deadline,
                appeal_procedure="Written appeal to competent authority within 30 days",
                appeal_authority="National Appeal Board",
                stay_of_execution=False
            ),
            public_notification_required=len(sanction_package.violations) > 2,
            disclosure_scope="Public register of sanctions" if len(sanction_package.violations) > 2 else None,
            investigating_officer="Investigating Officer",
            legal_review="Legal Review Team",
            authority_head="Authority Head"
        )
    
    def assess_proportionality(
        self,
        proposed_sanction: Sanction,
        context: dict
    ) -> ProportionalityAssessment:
        """Validate sanction against proportionality requirements."""
        # Simplified - would use full engine in practice
        return self.proportionality_engine.calculate(
            [], context, ComplianceHistory()
        )
