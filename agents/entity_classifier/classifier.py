"""
Entity Classifier Agent for NIS2 compliance assessment.
Determines Essential Entity (EE) vs Important Entity (IE) status.
"""
from datetime import datetime, timezone
from typing import Optional
import re

from shared.schemas import EntityInput, EntityClassification, SizeDetails, CrossBorderInfo
from shared.knowledge_base import NIS2KnowledgeBase


class UnknownSectorError(Exception):
    """Raised when sector cannot be mapped to Annex I or II."""
    pass


class EntityClassifier:
    """
    Classifies entities as Essential Entity (EE) or Important Entity (IE)
    under NIS2 Directive (EU) 2022/2555.
    """
    
    def __init__(self, knowledge_base: Optional[NIS2KnowledgeBase] = None):
        """Initialize classifier with knowledge base."""
        self.kb = knowledge_base or NIS2KnowledgeBase()
    
    def classify(self, entity_data: EntityInput) -> EntityClassification:
        """
        Execute full classification workflow.
        
        Args:
            entity_data: Input data for entity classification
            
        Returns:
            EntityClassification with full details
        """
        reasoning = []
        
        # Step 1: Map sector
        try:
            sector_info = self._map_sector(entity_data.sector)
            reasoning.append(f"Sector '{entity_data.sector}' mapped to {sector_info['annex']}")
        except UnknownSectorError as e:
            return self._create_unknown_classification(entity_data, str(e))
        
        # Step 2: Check size threshold
        size_check = self._check_size_threshold(entity_data)
        reasoning.append(size_check["reasoning"])
        
        # Step 3: Check for size exceptions
        has_exception = sector_info.get("size_exception", False)
        is_public_admin = entity_data.is_public_admin
        is_dns_tld = entity_data.is_dns_provider or entity_data.is_tld_registry
        is_trust_service = entity_data.is_trust_service_provider
        
        # Step 4: Determine classification
        if sector_info["annex"] == "Annex I":
            if (size_check["qualifies"] or has_exception or 
                is_public_admin or is_dns_tld or is_trust_service):
                classification = "Essential Entity"
                legal_basis = self._get_ee_citation(sector_info, entity_data)
                reasoning.append("Classified as Essential Entity (Annex I)")
            else:
                classification = "Non-Qualifying"
                legal_basis = "Article 2(1) - Below medium enterprise threshold"
                reasoning.append("Annex I sector but below size threshold")
        else:  # Annex II
            if size_check["qualifies"]:
                classification = "Important Entity"
                legal_basis = self._get_ie_citation(sector_info)
                reasoning.append("Classified as Important Entity (Annex II)")
            else:
                classification = "Non-Qualifying"
                legal_basis = "Article 2(1) - Below medium enterprise threshold"
                reasoning.append("Annex II sector but below size threshold")
        
        # Step 5: Determine lead authority
        lead_authority = self._determine_lead_authority(entity_data)
        reasoning.append(f"Lead authority: {lead_authority}")
        
        # Step 6: Calculate confidence
        confidence, edge_cases = self._calculate_confidence(
            entity_data, sector_info, size_check
        )
        
        # Build size details
        size_details = SizeDetails(
            employee_count=entity_data.employee_count,
            annual_turnover_eur=entity_data.annual_turnover_eur,
            balance_sheet_total=entity_data.balance_sheet_total
        )
        
        return EntityClassification(
            entity_id=entity_data.entity_id or f"ENT-{datetime.now(timezone.utc).timestamp()}",
            classification=classification,
            legal_basis=legal_basis,
            annex=sector_info["annex"],
            sector_classification=sector_info.get("parent_sector", entity_data.sector),
            size_qualification=size_check["qualifies"],
            size_details=size_details,
            cross_border=entity_data.cross_border_operations,
            lead_authority=lead_authority,
            confidence_score=confidence,
            edge_cases=edge_cases,
            reasoning_chain=reasoning
        )
    
    def _map_sector(self, sector: str) -> dict:
        """
        Map input sector to Annex I or Annex II.
        
        Args:
            sector: Sector name to map
            
        Returns:
            Sector information dict
            
        Raises:
            UnknownSectorError: If sector cannot be mapped
        """
        info = self.kb.get_sector_info(sector)
        if info is None:
            raise UnknownSectorError(f"Sector '{sector}' not found in Annex I or Annex II")
        return info
    
    def _check_size_threshold(self, entity_data: EntityInput) -> dict:
        """
        Evaluate medium/large enterprise criteria.
        
        Returns:
            Dict with qualification status and reasoning
        """
        employees = entity_data.employee_count
        turnover = entity_data.annual_turnover_eur
        balance = entity_data.balance_sheet_total or 0  # Handle None
        
        # Medium enterprise criteria (EU Recommendation 2003/361)
        # Medium: 50-249 employees AND (€10M-€50M turnover OR €10M-€43M balance)
        # Large: 250+ employees AND (€50M+ turnover OR €43M+ balance)
        
        is_medium = bool(
            50 <= employees <= 249 and
            (turnover >= 10_000_000 or balance >= 10_000_000)
        )
        
        is_large = bool(
            employees >= 250 and
            (turnover >= 50_000_000 or balance >= 50_000_000)
        )
        
        qualifies = is_medium or is_large
        
        reasoning = (
            f"Size check: {employees} employees, €{turnover:,.0f} turnover, "
            f"{'qualifies' if qualifies else 'does not qualify'} as medium/large enterprise"
        )
        
        return {
            "qualifies": qualifies,
            "is_medium": is_medium,
            "is_large": is_large,
            "reasoning": reasoning
        }
    
    def _determine_lead_authority(self, entity_data: EntityInput) -> str:
        """
        Apply Article 26 rules for cross-border scenarios.
        
        Returns:
            Member State code for lead authority
        """
        cb = entity_data.cross_border_operations
        
        if not cb or not cb.operates_cross_border:
            # Single Member State - use provided main establishment or default
            return cb.main_establishment if cb and cb.main_establishment else "XX"
        
        # Cross-border - apply hierarchy from Article 26
        if cb.main_establishment:
            return cb.main_establishment
        elif cb.decision_location:
            return cb.decision_location
        elif cb.majority_employees_location:
            return cb.majority_employees_location
        elif cb.highest_turnover_location:
            return cb.highest_turnover_location
        elif cb.member_states:
            return cb.member_states[0]
        
        return "XX"  # Unknown
    
    def _calculate_confidence(
        self,
        entity_data: EntityInput,
        sector_info: dict,
        size_check: dict
    ) -> tuple[float, list[str]]:
        """
        Compute confidence score with edge case detection.
        
        Returns:
            Tuple of (confidence_score, edge_cases)
        """
        edge_cases = []
        confidence = 1.0
        
        # Sector clarity check
        if "matched_sub_sector" in sector_info:
            # Direct sub-sector match - high confidence
            confidence *= 0.95
        else:
            # Main sector match - good confidence
            confidence *= 0.90
        
        # Data completeness
        missing_fields = []
        if entity_data.annual_turnover_eur <= 0:
            missing_fields.append("annual_turnover")
        if entity_data.employee_count <= 0:
            missing_fields.append("employee_count")
        if not entity_data.cross_border_operations:
            missing_fields.append("cross_border_info")
        
        if missing_fields:
            confidence *= 0.85
            edge_cases.append(f"MISSING_DATA: {', '.join(missing_fields)}")
        
        # Borderline size check
        employees = entity_data.employee_count
        turnover = entity_data.annual_turnover_eur
        
        # Check if near threshold boundaries
        if 45 <= employees <= 55:  # Near 50 employee threshold
            confidence -= 0.15
            edge_cases.append(f"BORDERLINE_SIZE: Employee count ({employees}) near threshold")
        
        if 8_000_000 <= turnover <= 12_000_000:  # Near €10M threshold
            confidence -= 0.15
            edge_cases.append(f"BORDERLINE_SIZE: Turnover near threshold")
        
        # Cross-border complexity
        cb = entity_data.cross_border_operations
        if cb and cb.operates_cross_border:
            if not cb.main_establishment and not cb.decision_location:
                confidence -= 0.10
                edge_cases.append("CROSS_BORDER_UNCLEAR: Lead authority indicators missing")
        
        # Ambiguous indicators for lead authority
        if cb and cb.operates_cross_border:
            indicators = [
                cb.main_establishment,
                cb.decision_location,
                cb.majority_employees_location,
                cb.highest_turnover_location
            ]
            if len([i for i in indicators if i]) > 1:
                # Multiple indicators - potential conflict
                unique = set(i for i in indicators if i)
                if len(unique) > 1:
                    confidence -= 0.05
                    edge_cases.append("CROSS_BORDER_INDICATORS: Multiple jurisdiction indicators")
        
        return max(0.0, min(1.0, confidence)), edge_cases
    
    def _get_ee_citation(self, sector_info: dict, entity_data: EntityInput) -> str:
        """Generate legal citation for Essential Entity classification."""
        sector = sector_info.get("parent_sector", "unknown")
        
        if entity_data.is_public_admin:
            return "Directive (EU) 2022/2555, Article 24(2) - Public administration body classification"
        elif entity_data.is_dns_provider or entity_data.is_tld_registry:
            return "Directive (EU) 2022/2555, Article 24(2) - Critical digital infrastructure classification"
        elif entity_data.is_trust_service_provider:
            return "Directive (EU) 2022/2555, Article 24(2) - Trust service provider classification"
        elif sector_info.get("size_exception"):
            return f"Directive (EU) 2022/2555, Article 24(2) - {sector.title()} sector (size exception)"
        else:
            return f"Directive (EU) 2022/2555, Article 24(1) - Essential Entity classification based on Annex I ({sector})"
    
    def _get_ie_citation(self, sector_info: dict) -> str:
        """Generate legal citation for Important Entity classification."""
        sector = sector_info.get("parent_sector", "unknown")
        return f"Directive (EU) 2022/2555, Article 25(1) - Important Entity classification based on Annex II ({sector})"
    
    def _create_unknown_classification(
        self,
        entity_data: EntityInput,
        error_message: str
    ) -> EntityClassification:
        """Create classification for unknown sector."""
        size_details = SizeDetails(
            employee_count=entity_data.employee_count,
            annual_turnover_eur=entity_data.annual_turnover_eur,
            balance_sheet_total=entity_data.balance_sheet_total
        )
        
        return EntityClassification(
            entity_id=entity_data.entity_id or f"ENT-{datetime.now(timezone.utc).timestamp()}",
            classification="Non-Qualifying",
            legal_basis="Unable to determine - sector not recognized",
            annex=None,
            sector_classification="UNKNOWN",
            size_qualification=False,
            size_details=size_details,
            cross_border=entity_data.cross_border_operations,
            lead_authority="XX",
            confidence_score=0.0,
            edge_cases=["UNKNOWN_SECTOR", "MANUAL_REVIEW_REQUIRED"],
            reasoning_chain=[error_message]
        )
    
    def get_legal_citation(self, classification: str, annex: Optional[str]) -> str:
        """Return specific Article citation for legal basis."""
        if classification == "Essential Entity":
            return "Directive (EU) 2022/2555, Article 24"
        elif classification == "Important Entity":
            return "Directive (EU) 2022/2555, Article 25"
        elif classification == "Non-Qualifying":
            return "Directive (EU) 2022/2555, Article 2(1) - Below threshold"
        return "Unknown classification"
    
    def check_national_designation(
        self,
        entity_data: EntityInput,
        classification: EntityClassification
    ) -> dict:
        """
        Check if entity may be designated as essential/important under 
        national rules regardless of EU size thresholds.
        
        Args:
            entity_data: Entity input data
            classification: Current classification result
            
        Returns:
            Dict with designation assessment
        """
        # Get lead authority/member state
        member_state = classification.lead_authority
        if not member_state or member_state == "XX":
            return {"applicable": False}
        
        # Check if member state has designation override
        if not self.kb.can_designate_regardless_of_size(member_state, entity_data.sector):
            return {"applicable": False}
        
        national_rules = self.kb.get_national_rules(member_state)
        
        # Special handling for healthcare in Romania
        if (member_state == "RO" and 
            entity_data.sector.lower() in ["health", "healthcare", "hospital"]):
            
            return {
                "applicable": True,
                "member_state": member_state,
                "authority": national_rules.get("competent_authority"),
                "reason": (
                    f"Under {national_rules.get('legal_framework')}, DNSC may designate "
                    "healthcare providers as Essential Entities regardless of size thresholds "
                    "if they provide critical services to the community. "
                    "Contact DNSC for case-by-case assessment."
                ),
                "recommendation": (
                    "Even though this entity does not meet EU size thresholds, "
                    "it should register with DNSC for assessment under Romanian "
                    "NIS2 transposition (GEO 155/2024, Article 9)."
                ),
                "action_required": "Contact DNSC via NIS2@RO platform"
            }
        
        # Generic designation check
        return {
            "applicable": True,
            "member_state": member_state,
            "authority": national_rules.get("competent_authority"),
            "reason": (
                f"Under {national_rules.get('legal_framework')}, the competent authority "
                "may designate entities as essential/important regardless of size thresholds."
            ),
            "recommendation": "Contact competent authority for case-by-case assessment"
        }
