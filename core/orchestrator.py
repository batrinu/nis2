"""
Core Orchestrator for NIS2 compliance assessment system.
Manages agent routing, context sharing, and state management.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from typing import Optional, Literal, Any
from datetime import datetime, timezone
from dataclasses import dataclass, field
from enum import Enum
import json
import uuid

from shared.schemas import (
    EntityInput, EntityClassification, AuditAssessment,
    GapAnalysisReport, SanctionNotice
)
from shared.knowledge_base import NIS2KnowledgeBase
from shared.knowledge_base_ro import RomanianNIS2KnowledgeBase
from agents.entity_classifier import EntityClassifier
from agents.romanian_classifier import RomanianEntityClassifier
from agents.audit_assessor import AuditAssessor
from agents.enforcement_officer import EnforcementOfficer
from agents.gap_analyst import GapAnalyst
from agents.enire_assessor import ENIREAssessor
from agents.cyfun_assessor import CyFunAssessor
from agents.report_generator import ReportGenerator
from agents.sector_specialist import SectorSpecialist


class AuditState(Enum):
    """Audit lifecycle states."""
    INIT = "init"
    ENTITY_DATA_COLLECTED = "entity_data_collected"
    CLASSIFICATION_COMPLETE = "classification_complete"
    CLASSIFICATION_FAILED = "classification_failed"
    NON_QUALIFYING = "non_qualifying"
    PHASE_1_COMPLETE = "phase_1_complete"
    PHASE_2_COMPLETE = "phase_2_complete"
    PHASE_3_COMPLETE = "phase_3_complete"
    PHASE_4_COMPLETE = "phase_4_complete"
    PHASE_5_COMPLETE = "phase_5_complete"
    AUDIT_COMPLETE = "audit_complete"
    ENFORCEMENT_REQUIRED = "enforcement_required"
    REMEDIATION_NEGOTIATED = "remediation_negotiated"
    REPORT_COMPLETE = "report_complete"


@dataclass
class SessionContext:
    """Shared context for an audit session."""
    session_id: str
    entity_data: Optional[EntityInput] = None
    classification: Optional[EntityClassification] = None
    audit_result: Optional[dict] = None
    gap_analysis: Optional[dict] = None
    enforcement_result: Optional[dict] = None
    state: AuditState = field(default=AuditState.INIT)
    history: list[dict] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    # Romanian-specific fields
    is_romanian_entity: bool = False
    ro_classification: Optional[dict] = None  # RomanianClassificationResult
    ro_sector_code: Optional[str] = None
    
    def transition(self, new_state: AuditState, reason: str = ""):
        """Transition to new state with audit trail."""
        old_state = self.state
        self.state = new_state
        self.history.append({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "from": old_state.value,
            "to": new_state.value,
            "reason": reason
        })


class AgentRouter:
    """Routes queries to appropriate agents."""
    
    ROUTES = {
        "classify": {
            "agent": "entity_classifier",
            "required_context": [],
            "next_states": [AuditState.CLASSIFICATION_COMPLETE, AuditState.CLASSIFICATION_FAILED]
        },
        "audit": {
            "agent": "audit_assessor",
            "required_context": ["classification"],
            "next_states": [AuditState.AUDIT_COMPLETE, AuditState.ENFORCEMENT_REQUIRED]
        },
        "enforce": {
            "agent": "enforcement_officer",
            "required_context": ["audit_result"],
            "next_states": [AuditState.ENFORCEMENT_REQUIRED]
        },
        "gap_analysis": {
            "agent": "gap_analyst",
            "required_context": [],
            "next_states": [AuditState.REPORT_COMPLETE]
        },
        "sector_check": {
            "agent": "sector_specialist",
            "required_context": ["entity_data"],
            "next_states": []
        },
        "report": {
            "agent": "report_generator",
            "required_context": ["audit_result"],
            "next_states": [AuditState.REPORT_COMPLETE]
        }
    }
    
    def route(self, action: str, context: SessionContext) -> dict:
        """Determine routing for an action."""
        route = self.ROUTES.get(action)
        if not route:
            return {"error": f"Unknown action: {action}"}
        
        # Check required context
        missing = []
        for req in route["required_context"]:
            if getattr(context, req) is None:
                missing.append(req)
        
        if missing:
            return {
                "error": "Missing required context",
                "missing": missing,
                "action": action
            }
        
        return {
            "agent": route["agent"],
            "action": action,
            "can_proceed": True
        }


class EvidenceChain:
    """Immutable audit trail for regulatory traceability."""
    
    def __init__(self):
        self.chain: list[dict] = []
    
    def add(
        self,
        session_id: str,
        evidence_type: str,
        action: str,
        data: dict,
        agent: str
    ) -> str:
        """Add evidence to chain."""
        evidence_id = str(uuid.uuid4())
        
        record = {
            "evidence_id": evidence_id,
            "session_id": session_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "evidence_type": evidence_type,
            "action": action,
            "agent": agent,
            "data_hash": hash(json.dumps(data, sort_keys=True, default=str)) & 0xFFFFFFFF
        }
        
        self.chain.append(record)
        return evidence_id
    
    def get_for_session(self, session_id: str) -> list[dict]:
        """Get all evidence for a session."""
        return [e for e in self.chain if e["session_id"] == session_id]


class LegalBasisValidator:
    """Validates legal citations in outputs."""
    
    VALID_ARTICLES = [
        "21(2)(a)", "21(2)(b)", "21(2)(c)", "21(2)(d)", "21(2)(e)",
        "21(2)(f)", "21(2)(g)", "21(2)(h)", "21(2)(i)", "21(2)(j)",
        "21(2)(k)", "21(2)(l)", "21(2)(m)", "21(2)(n)",
        "22", "23", "24", "25", "26", "34"
    ]
    
    def validate_citation(self, citation: str) -> bool:
        """Validate a legal citation."""
        for article in self.VALID_ARTICLES:
            if article in citation:
                return True
        return False
    
    def get_required_citation(self, finding_type: str) -> str:
        """Get required citation for finding type."""
        citations = {
            "risk_management": "Article 21(2)(a)",
            "incident_response": "Article 21(2)(b)",
            "business_continuity": "Article 21(2)(c)",
            "supply_chain": "Article 21(2)(d)",
            "cryptography": "Article 21(2)(i)",
            "access_control": "Article 21(2)(k)"
        }
        return citations.get(finding_type, "Article 21")


class Orchestrator:
    """
    Central coordination hub for NIS2 compliance assessment.
    Supports both EU NIS2 and Romanian national transposition (OUG 155/2024).
    """
    
    def __init__(self):
        """Initialize orchestrator with all agents."""
        self.kb = NIS2KnowledgeBase()
        self.ro_kb = RomanianNIS2KnowledgeBase()
        self.router = AgentRouter()
        self.evidence_chain = EvidenceChain()
        self.legal_validator = LegalBasisValidator()
        
        # Initialize agents
        self.agents = {
            "entity_classifier": EntityClassifier(self.kb),
            "romanian_classifier": RomanianEntityClassifier(self.ro_kb),
            "audit_assessor": AuditAssessor(knowledge_base=self.kb),
            "enforcement_officer": EnforcementOfficer(self.kb),
            "gap_analyst": GapAnalyst(self.kb),
            "enire_assessor": ENIREAssessor(self.ro_kb),
            "cyfun_assessor": CyFunAssessor(self.ro_kb),
            "report_generator": ReportGenerator(),
            "sector_specialist": SectorSpecialist(self.kb)
        }
        
        # Session storage
        self.sessions: dict[str, SessionContext] = {}
    
    def _is_romanian_entity(self, entity_data: EntityInput) -> bool:
        """Check if entity is Romanian based on country code."""
        if entity_data.cross_border_operations:
            # Check main establishment or member states
            main = entity_data.cross_border_operations.main_establishment
            if main == "RO":
                return True
            members = entity_data.cross_border_operations.member_states
            if members and "RO" in members:
                return True
        return False
    
    def _get_ro_sector_code(self, sector: str) -> Optional[str]:
        """Map sector name to Romanian sector code."""
        sector_map = {
            "energy": "101",
            "transport": "102",
            "banking": "103",
            "financial_markets": "104",
            "health": "105",
            "healthcare": "105",
            "drinking_water": "106",
            "waste_water": "107",
            "digital_infrastructure": "108",
            "ict_services": "109",
            "public_administration": "110",
            "space": "111",
            "postal": "201",
            "waste_management": "202",
            "chemicals": "203",
            "food": "204",
            "manufacturing": "205",
            "digital_providers": "206",
            "research": "207"
        }
        
        sector_lower = sector.lower().replace(" ", "_")
        code = sector_map.get(sector_lower)
        
        # For health sector, default to 105.1 (medical providers)
        if code == "105":
            return "105.1"
        
        return code
    
    def start_session(self, entity_data: EntityInput) -> str:
        """Initialize new audit session."""
        session_id = str(uuid.uuid4())
        
        context = SessionContext(
            session_id=session_id,
            entity_data=entity_data
        )
        
        self.sessions[session_id] = context
        
        # Log session start
        self.evidence_chain.add(
            session_id=session_id,
            evidence_type="session",
            action="session_started",
            data={"entity_id": entity_data.entity_id},
            agent="orchestrator"
        )
        
        return session_id
    
    def classify_entity(self, session_id: str, use_romanian: bool = True) -> dict:
        """
        Classify entity for a session.
        
        Args:
            session_id: Session identifier
            use_romanian: Whether to use Romanian classifier for RO entities
            
        Returns:
            Classification result with both EU and Romanian (if applicable) results
        """
        context = self._get_context(session_id)
        
        if not context.entity_data:
            return {"error": "No entity data in session"}
        
        # Check if Romanian entity
        is_romanian = self._is_romanian_entity(context.entity_data)
        context.is_romanian_entity = is_romanian
        
        result = {
            "session_id": session_id,
            "is_romanian_entity": is_romanian
        }
        
        # Always perform EU classification first
        classifier = self.agents["entity_classifier"]
        eu_classification = classifier.classify(context.entity_data)
        context.classification = eu_classification
        
        result["eu_classification"] = eu_classification.model_dump()
        
        # If Romanian entity and requested, also perform Romanian classification
        if is_romanian and use_romanian:
            ro_classifier = self.agents["romanian_classifier"]
            ro_sector_code = self._get_ro_sector_code(context.entity_data.sector)
            
            if ro_sector_code:
                context.ro_sector_code = ro_sector_code
                ro_classification = ro_classifier.classify(
                    context.entity_data,
                    ro_sector_code
                )
                context.ro_classification = ro_classification.__dict__
                result["ro_classification"] = ro_classification.__dict__
                
                # Use Romanian classification for state determination
                ro_class = ro_classification.classification
                if ro_class == "essential":
                    context.transition(AuditState.CLASSIFICATION_COMPLETE, "Romanian Essential Entity")
                elif ro_class == "important":
                    context.transition(AuditState.CLASSIFICATION_COMPLETE, "Romanian Important Entity")
                elif ro_class == "out_of_scope":
                    if ro_classification.art9_required:
                        context.transition(AuditState.CLASSIFICATION_COMPLETE, "Romanian - Art 9 Analysis Required")
                    else:
                        context.transition(AuditState.NON_QUALIFYING, "Romanian - Out of Scope")
                else:
                    context.transition(AuditState.CLASSIFICATION_FAILED, "Romanian classification uncertain")
            else:
                # Fall back to EU classification
                self._update_state_from_eu_classification(context, eu_classification)
        else:
            # Use EU classification
            self._update_state_from_eu_classification(context, eu_classification)
        
        # Log evidence
        self.evidence_chain.add(
            session_id=session_id,
            evidence_type="classification",
            action="entity_classified",
            data=result,
            agent="romanian_classifier" if (is_romanian and use_romanian) else "entity_classifier"
        )
        
        result["state"] = context.state.value
        return result
    
    def _update_state_from_eu_classification(self, context: SessionContext, classification: EntityClassification):
        """Update session state based on EU classification."""
        if classification.classification == "Non-Qualifying":
            context.transition(AuditState.NON_QUALIFYING, "Entity below threshold")
        elif classification.confidence_score < 0.70:
            context.transition(AuditState.CLASSIFICATION_FAILED, "Low confidence")
        else:
            context.transition(AuditState.CLASSIFICATION_COMPLETE, "Classification successful")
    
    def run_audit(self, session_id: str, **kwargs) -> dict:
        """Run full audit for a session."""
        context = self._get_context(session_id)
        
        # Ensure classification exists
        if not context.classification:
            result = self.classify_entity(session_id)
            if result.get("state") in ["non_qualifying", "classification_failed"]:
                return result
        
        # Execute audit
        assessor = self.agents["audit_assessor"]
        audit_result = assessor.execute_audit(
            context.entity_data,
            **kwargs
        )
        
        # Update context
        context.audit_result = audit_result
        context.transition(AuditState.AUDIT_COMPLETE, "Audit completed")
        
        # Log evidence
        self.evidence_chain.add(
            session_id=session_id,
            evidence_type="audit",
            action="audit_completed",
            data=audit_result,
            agent="audit_assessor"
        )
        
        return {
            "session_id": session_id,
            "state": context.state.value,
            "audit_result": audit_result
        }
    
    def run_gap_analysis(self, session_id: str, mode: str = "deep_dive") -> dict:
        """Run gap analysis for a session."""
        context = self._get_context(session_id)
        
        if not context.entity_data:
            return {"error": "No entity data in session"}
        
        # Execute gap analysis
        analyst = self.agents["gap_analyst"]
        
        if mode == "quick_scan":
            result = analyst.conduct_quick_scan(context.entity_data)
        else:
            result = analyst.conduct_deep_dive(context.entity_data)
        
        # Update context
        context.gap_analysis = result
        context.transition(AuditState.REPORT_COMPLETE, "Gap analysis completed")
        
        # Log evidence
        self.evidence_chain.add(
            session_id=session_id,
            evidence_type="gap_analysis",
            action=f"gap_analysis_{mode}",
            data=result,
            agent="gap_analyst"
        )
        
        return {
            "session_id": session_id,
            "state": context.state.value,
            "gap_analysis": result
        }
    
    def calculate_enforcement(
        self,
        session_id: str,
        violations: list[dict]
    ) -> dict:
        """Calculate enforcement for a session."""
        context = self._get_context(session_id)
        
        if not context.audit_result:
            return {"error": "No audit result available"}
        
        if not context.classification:
            return {"error": "No classification available"}
        
        # Convert violations
        from shared.schemas import Violation
        violation_objs = [
            Violation(**v) for v in violations
        ]
        
        # Execute enforcement
        officer = self.agents["enforcement_officer"]
        
        from agents.enforcement_officer import ComplianceHistory
        history = ComplianceHistory()
        
        sanction_package = officer.calculate_sanctions(
            violation_objs,
            context.classification,
            history
        )
        
        # Generate notice
        notice = officer.generate_notice(
            sanction_package,
            context.classification
        )
        
        # Update context
        context.enforcement_result = {
            "package": sanction_package.model_dump(),
            "notice": notice.model_dump()
        }
        context.transition(AuditState.ENFORCEMENT_REQUIRED, "Enforcement calculated")
        
        return {
            "session_id": session_id,
            "state": context.state.value,
            "sanction_package": sanction_package.model_dump(),
            "notice": notice.model_dump()
        }
    
    def generate_report(
        self,
        session_id: str,
        report_type: str = "executive_summary",
        format: str = "markdown"
    ) -> dict:
        """Generate report for a session."""
        context = self._get_context(session_id)
        
        if not context.audit_result:
            return {"error": "No audit result available"}
        
        # Convert audit result to AuditAssessment
        # For now, use the raw result
        
        generator = self.agents["report_generator"]
        
        # Generate appropriate report
        if report_type == "executive_summary":
            # Convert audit_result to AuditAssessment
            from shared.schemas import AuditAssessment
            assessment = AuditAssessment(**context.audit_result)
            content = generator.generate_executive_summary(assessment, format)
        elif report_type == "full":
            from shared.schemas import AuditAssessment
            assessment = AuditAssessment(**context.audit_result)
            content = generator.generate_full_report(assessment, format)
        elif report_type == "gap":
            if not context.gap_analysis:
                return {"error": "No gap analysis available"}
            # Convert to GapAnalysisReport
            content = json.dumps(context.gap_analysis, indent=2)
        else:
            return {"error": f"Unknown report type: {report_type}"}
        
        context.transition(AuditState.REPORT_COMPLETE, f"Report generated: {report_type}")
        
        return {
            "session_id": session_id,
            "state": context.state.value,
            "report_type": report_type,
            "format": format,
            "content": content
        }
    
    def get_session_state(self, session_id: str) -> dict:
        """Get current state of audit session."""
        context = self._get_context(session_id)
        
        result = {
            "session_id": session_id,
            "state": context.state.value,
            "created_at": context.created_at.isoformat(),
            "history": context.history,
            "has_classification": context.classification is not None,
            "has_audit_result": context.audit_result is not None,
            "has_gap_analysis": context.gap_analysis is not None,
            "has_enforcement": context.enforcement_result is not None
        }
        
        # Add Romanian-specific info if applicable
        if context.is_romanian_entity:
            result["is_romanian_entity"] = True
            result["ro_sector_code"] = context.ro_sector_code
            if context.ro_classification:
                result["ro_classification"] = {
                    "classification": context.ro_classification.get("classification"),
                    "cyfun_level": context.ro_classification.get("cyfun_level"),
                    "dnsc_registration_required": context.ro_classification.get("dnsc_registration_required")
                }
        
        return result
    
    def get_evidence_chain(self, session_id: str) -> list[dict]:
        """Get evidence chain for a session."""
        return self.evidence_chain.get_for_session(session_id)
    
    # ===== Romanian-Specific Methods =====
    
    def run_enire_risk_assessment(
        self,
        session_id: str,
        actor: Optional[str] = None,
        attack: Optional[str] = None,
        impact: Optional[str] = None,
        probability: Optional[str] = None,
        nature: str = "Targeted"
    ) -> dict:
        """
        Run ENIRE@RO risk assessment for Romanian entities.
        
        Args:
            session_id: Session identifier
            actor: Threat actor type (default from sector)
            attack: Attack type (default from sector)
            impact: Impact level (default from sector)
            probability: Probability level (default from sector)
            nature: Attack nature (Global or Targeted)
            
        Returns:
            ENIRE risk assessment result with CyFunRO level
        """
        context = self._get_context(session_id)
        
        if not context.is_romanian_entity:
            return {"error": "ENIRE assessment only available for Romanian entities"}
        
        if not context.ro_sector_code:
            return {"error": "No Romanian sector code assigned"}
        
        # Get size from Romanian classification
        size = "medium"  # default
        if context.ro_classification:
            size = context.ro_classification.get("size_category", "medium")
        
        # Run ENIRE assessment using the dedicated assessor
        enire_assessor = self.agents["enire_assessor"]
        enire_result = enire_assessor.assess(
            sector_code=context.ro_sector_code,
            size=size,
            actor=actor,
            attack=attack,
            impact=impact,
            probability=probability,
            nature=nature
        )
        
        # Log evidence
        self.evidence_chain.add(
            session_id=session_id,
            evidence_type="enire_assessment",
            action="enire_risk_calculated",
            data=enire_result.__dict__,
            agent="enire_assessor"
        )
        
        return {
            "session_id": session_id,
            "enire_result": enire_result.__dict__,
            "deadline": "60 zile de la comunicarea deciziei DNSC",
            "submission_platform": "NIS2@RO"
        }
    
    def run_cyfun_maturity_assessment(
        self,
        session_id: str,
        scores: Optional[dict] = None
    ) -> dict:
        """
        Run CyberFundamentals (CyFun) maturity assessment.
        
        Args:
            session_id: Session identifier
            scores: Optional dict with maturity scores per category
            
        Returns:
            CyFun maturity assessment result
        """
        context = self._get_context(session_id)
        
        if not context.is_romanian_entity:
            return {"error": "CyFun assessment only available for Romanian entities"}
        
        # Get entity type from classification
        entity_type = "basic"  # default
        entity_id = context.entity_data.entity_id if context.entity_data else "unknown"
        if context.ro_classification:
            entity_type = context.ro_classification.get("classification", "basic")
        
        # Run CyFun assessment using the dedicated assessor
        cyfun_assessor = self.agents["cyfun_assessor"]
        cyfun_result = cyfun_assessor.assess(
            entity_id=entity_id,
            entity_type=entity_type,
            category_scores=scores
        )
        
        # Generate remediation plan if needed
        remediation_plan = None
        if cyfun_result.remediation_plan_required:
            remediation_plan = cyfun_assessor.generate_remediation_plan(cyfun_result)
        
        # Log evidence
        self.evidence_chain.add(
            session_id=session_id,
            evidence_type="cyfun_assessment",
            action="cyfun_maturity_calculated",
            data=cyfun_result.__dict__,
            agent="cyfun_assessor"
        )
        
        return {
            "session_id": session_id,
            "cyfun_result": cyfun_result.__dict__,
            "remediation_plan": remediation_plan,
            "is_compliant": cyfun_result.is_compliant,
            "overall_maturity": cyfun_result.overall_maturity,
            "next_assessment": cyfun_result.next_assessment_due
        }
    
    def get_dnsc_registration_info(self, session_id: str) -> dict:
        """
        Get DNSC registration information for Romanian entities.
        
        Returns:
            Registration requirements and deadlines
        """
        context = self._get_context(session_id)
        
        if not context.is_romanian_entity:
            return {"error": "DNSC registration only applicable to Romanian entities"}
        
        if not context.ro_classification:
            return {"error": "Entity not yet classified under Romanian NIS2"}
        
        classification = context.ro_classification.get("classification", "out_of_scope")
        ro_classifier = self.agents["romanian_classifier"]
        
        return ro_classifier.get_registration_requirements(classification)
    
    def _get_context(self, session_id: str) -> SessionContext:
        """Get session context or raise error."""
        if session_id not in self.sessions:
            raise ValueError(f"Session not found: {session_id}")
        return self.sessions[session_id]
