"""
Sector Specialist Agent for NIS2 compliance assessment.
"""
from typing import Optional, Type
from shared.schemas import EntityInput
from shared.knowledge_base import NIS2KnowledgeBase
from .domains.base import BaseSectorValidator, SectorValidationSummary
from .domains import (
    EnergySectorValidator,
    BankingSectorValidator,
    HealthcareSectorValidator,
    TransportSectorValidator,
    DigitalInfrastructureValidator,
)


class SectorSpecialist:
    """
    Provides domain-specific validation for NIS2 sectors.
    Routes entities to appropriate sector validators.
    """
    
    def __init__(self, knowledge_base: Optional[NIS2KnowledgeBase] = None):
        """Initialize with sector validators."""
        self.kb = knowledge_base or NIS2KnowledgeBase()
        
        # Register sector validators
        self.validators: dict[str, Type[BaseSectorValidator]] = {
            "energy": EnergySectorValidator,
            "transport": TransportSectorValidator,
            "banking": BankingSectorValidator,
            "financial_markets": BankingSectorValidator,
            "health": HealthcareSectorValidator,
            "digital_infrastructure": DigitalInfrastructureValidator,
            "ict_services": DigitalInfrastructureValidator,
        }
    
    def get_validator(self, sector: str) -> Optional[BaseSectorValidator]:
        """
        Return appropriate validator for sector.
        
        Args:
            sector: Sector code or name
            
        Returns:
            Sector validator instance or None
        """
        # Normalize sector name
        sector_normalized = sector.lower().replace(" ", "_")
        
        # Direct match
        if sector_normalized in self.validators:
            return self.validators[sector_normalized]()
        
        # Check knowledge base for sector mapping
        sector_info = self.kb.get_sector_info(sector)
        if sector_info:
            parent = sector_info.get("parent_sector")
            if parent and parent in self.validators:
                return self.validators[parent]()
        
        return None
    
    def validate_entity(
        self,
        entity: EntityInput,
        sector: Optional[str] = None
    ) -> SectorValidationSummary:
        """
        Execute sector-specific validation.
        
        Args:
            entity: Entity to validate
            sector: Optional sector override (uses entity.sector if not provided)
            
        Returns:
            Sector validation summary
        """
        target_sector = sector or entity.sector
        
        validator = self.get_validator(target_sector)
        if validator:
            return validator.validate(entity)
        
        # No specific validator - return generic summary
        return SectorValidationSummary(
            sector_code="generic",
            sector_name=target_sector,
            annex=self._get_annex(target_sector),
            overall_score=0.0,
            compliance_level="Unknown",
            validation_results=[],
            cross_regulatory_frameworks=[],
            specific_requirements=["No sector-specific validator available"]
        )
    
    def get_sector_requirements(self, sector: str) -> list[str]:
        """Return all applicable requirements for sector."""
        validator = self.get_validator(sector)
        if validator:
            # Create instance and get requirements
            # This is a simplified version
            info = self.kb.get_sector_info(sector)
            if info:
                return [f"NIS2 {info.get('annex')} requirements"]
        return []
    
    def get_cross_regulatory_frameworks(self, sector: str) -> list[str]:
        """Return intersecting regulations."""
        validator = self.get_validator(sector)
        if validator:
            return validator.get_cross_regulatory_frameworks()
        return []
    
    def _get_annex(self, sector: str) -> str:
        """Get annex for sector."""
        info = self.kb.get_sector_info(sector)
        return info.get("annex", "Unknown") if info else "Unknown"
    
    def register_validator(
        self,
        sector_code: str,
        validator_class: Type[BaseSectorValidator]
    ) -> None:
        """
        Register a new sector validator.
        
        Args:
            sector_code: Code for the sector
            validator_class: Validator class to register
        """
        self.validators[sector_code] = validator_class
