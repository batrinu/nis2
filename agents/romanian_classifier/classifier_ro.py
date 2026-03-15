"""
Romanian Entity Classifier Agent
Implements the priority-based classification algorithm per OUG 155/2024.
"""
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from datetime import datetime, timezone

from shared.schemas import EntityInput, EntityClassification, CrossBorderInfo, SizeDetails
from shared.knowledge_base_ro import RomanianNIS2KnowledgeBase


@dataclass
class RomanianClassificationResult:
    """Extended classification result for Romanian NIS2."""
    entity_id: str
    classification: str  # 'essential', 'important', 'out_of_scope', 'art9_analysis_required'
    eu_classification: str  # What EU NIS2 would classify
    priority_level: int
    rule_applied: str
    sector_code: str
    sector_name: str
    size_category: str
    annex: int
    art9_required: bool
    art9_analysis: Optional[Dict[str, Any]] = None
    cyfun_level: Optional[str] = None  # BASIC, IMPORTANT, ESENTIAL
    legal_basis: str = ""
    dnsc_registration_required: bool = False
    confidence_score: float = 1.0
    reasoning: List[str] = None
    edge_cases: List[str] = None
    
    def __post_init__(self):
        if self.reasoning is None:
            self.reasoning = []
        if self.edge_cases is None:
            self.edge_cases = []


class RomanianEntityClassifier:
    """
    Romanian NIS2 Entity Classifier.
    
    Implements the priority-based classification algorithm:
    1. Priority 0: Administrație Publică Centrală → Esențial
    2. Priority 1: Servicii de încredere calificate → Esențial
    3. Priority 2: DNS/TLD → Esențial
    4. Priority 3: Servicii de încredere necalificate → Important/Esențial
    5. Priority 4: Comunicații electronice publice → Important/Esențial
    6. Priority 5: MSSP (large only) → Esențial
    7. Priority 6: Annex 1 sectors → Esențial if medium/large, else Art 9
    8. Priority 7: Annex 2 sectors → Important if medium/large
    """
    
    def __init__(self, kb: Optional[RomanianNIS2KnowledgeBase] = None):
        """Initialize with Romanian knowledge base."""
        self.kb = kb or RomanianNIS2KnowledgeBase()
    
    def classify(
        self,
        entity_data: EntityInput,
        sector_code: str,
        perform_art9_analysis: bool = False,
        art9_data: Optional[Dict[str, Any]] = None
    ) -> RomanianClassificationResult:
        """
        Classify entity under Romanian NIS2.
        
        Args:
            entity_data: Entity input data
            sector_code: Romanian sector code (e.g., '101.1', '201.1')
            perform_art9_analysis: Whether to perform Art 9 analysis
            art9_data: Data for Art 9 analysis if performed
            
        Returns:
            RomanianClassificationResult with full classification details
        """
        reasoning = []
        edge_cases = []
        
        # Step 1: Calculate Romanian size category
        size = self.kb.calculate_size_ro(
            employees=entity_data.employee_count,
            turnover_eur=entity_data.annual_turnover_eur,
            balance_eur=entity_data.balance_sheet_total or 0
        )
        reasoning.append(f"Dimensiune calculată conform Legii 346/2004: {size}")
        
        # Step 2: Get sector info
        sector = self.kb.get_sector_info(sector_code.split(".")[0])
        subsector = self.kb.get_subsector_info(sector_code)
        
        if not subsector:
            return RomanianClassificationResult(
                entity_id=entity_data.entity_id or "",
                classification="unknown",
                eu_classification="unknown",
                priority_level=-1,
                rule_applied="Sector necunoscut",
                sector_code=sector_code,
                sector_name="Necunoscut",
                size_category=size,
                annex=0,
                art9_required=False,
                confidence_score=0.0,
                reasoning=[f"Cod sector necunoscut: {sector_code}"],
                edge_cases=["INVALID_SECTOR_CODE"]
            )
        
        reasoning.append(f"Sector identificat: {subsector['name']} ({sector_code})")
        
        # Step 3: Apply priority-based classification
        result = self.kb.classify_by_priority(sector_code, size)
        
        classification = result["classification"]
        priority = result["priority"]
        rule = result["rule"]
        art9_required = result["art9_required"]
        
        reasoning.append(f"Regulă aplicată: {rule}")
        
        # Step 4: Determine annex
        main_sector = sector_code.split(".")[0]
        is_annex_1 = main_sector in self.kb._sectors["annex_1"]["sectors"]
        annex = 1 if is_annex_1 else 2
        
        # Step 5: EU classification (for comparison)
        eu_classification = self._determine_eu_classification(size, is_annex_1, art9_required)
        
        # Step 6: Perform Art 9 analysis if required and requested
        art9_analysis = None
        if art9_required and perform_art9_analysis and art9_data:
            art9_analysis = self._perform_art9_analysis(art9_data)
            
            # Update classification based on Art 9 results
            if art9_analysis.get("art9_applies", False):
                classification = "essential"
                reasoning.append("Clasificare actualizată la Esențial în urma analizei Art 9")
        
        # Step 7: Determine CyFun level
        cyfun_level = self._estimate_cyfun_level(classification, size)
        
        # Step 8: Determine legal basis
        legal_basis = self._get_legal_basis(classification, priority)
        
        # Step 9: Determine if DNSC registration is required
        dnsc_registration = classification in ["essential", "important"]
        
        # Step 10: Calculate confidence
        confidence = self._calculate_confidence(entity_data, sector_code)
        
        # Build result
        return RomanianClassificationResult(
            entity_id=entity_data.entity_id or f"RO-{datetime.now(timezone.utc).timestamp()}",
            classification=classification,
            eu_classification=eu_classification,
            priority_level=priority,
            rule_applied=rule,
            sector_code=sector_code,
            sector_name=subsector["name"],
            size_category=size,
            annex=annex,
            art9_required=art9_required,
            art9_analysis=art9_analysis,
            cyfun_level=cyfun_level,
            legal_basis=legal_basis,
            dnsc_registration_required=dnsc_registration,
            confidence_score=confidence,
            reasoning=reasoning,
            edge_cases=edge_cases
        )
    
    def _determine_eu_classification(self, size: str, is_annex_1: bool, art9_required: bool) -> str:
        """Determine what EU NIS2 would classify."""
        if art9_required:
            return "out_of_scope_eu"  # Would need Art 9 analysis in RO
        
        if is_annex_1:
            if size in ["medium", "large"]:
                return "essential_eu"
            else:
                return "out_of_scope_eu"
        else:
            if size in ["medium", "large"]:
                return "important_eu"
            else:
                return "out_of_scope_eu"
    
    def _perform_art9_analysis(self, art9_data: Dict[str, Any]) -> Dict[str, Any]:
        """Perform Article 9 disruptive effect analysis."""
        analysis = {
            "art9_applies": False,
            "criteria_met": [],
            "criteria_not_met": [],
            "recommendation": ""
        }
        
        # Check lit a) - Sole provider
        if art9_data.get("is_sole_provider", False):
            analysis["criteria_met"].append("Art 9 lit a) - Furnizor unic de servicii esențiale")
            analysis["art9_applies"] = True
        
        # Check lit b) dimensions
        lit_b_dimensions = art9_data.get("lit_b", {})
        high_impact_count = 0
        
        for dim, value in lit_b_dimensions.items():
            if dim == "personal_data_affected" and value > 1000000:
                analysis["criteria_met"].append(f"Art 9 lit b) - {dim}: >1M persoane afectate")
                high_impact_count += 1
            elif dim == "public_service_users" and value >= 115000:
                analysis["criteria_met"].append(f"Art 9 lit b) - {dim}: ≥115k utilizatori")
                high_impact_count += 1
            elif dim == "pib_impact_percent" and value > 0.1:
                analysis["criteria_met"].append(f"Art 9 lit b) - {dim}: >0.1% PIB")
                high_impact_count += 1
            elif dim == "deaths" and value > 100:
                analysis["criteria_met"].append(f"Art 9 lit b) - {dim}: >100 decese")
                high_impact_count += 1
        
        if high_impact_count >= 1:
            analysis["art9_applies"] = True
        
        # Check lit d) - Critical infrastructure
        if art9_data.get("is_critical_infrastructure", False):
            analysis["criteria_met"].append("Art 9 lit d) - Infrastructură critică")
            analysis["art9_applies"] = True
        
        # Recommendation
        if analysis["art9_applies"]:
            analysis["recommendation"] = (
                "Contactați DNSC pentru desemnare ca Entitate Esențială conform Art 9 "
                "din OUG 155/2024. Pregătiți documentația justificativă."
            )
        else:
            analysis["recommendation"] = (
                "Entitatea nu îndeplinește criteriile Art 9. Monitorizați schimbările "
                "care ar putea duce la aplicarea acestui articol."
            )
        
        return analysis
    
    def _estimate_cyfun_level(self, classification: str, size: str) -> str:
        """Estimate CyFunRO level based on classification and size."""
        if classification == "essential":
            return "ESENTIAL"
        elif classification == "important":
            return "IMPORTANT"
        elif size == "large":
            return "BASIC"  # Large but out of scope
        else:
            return "BASIC"
    
    def _get_legal_basis(self, classification: str, priority: int) -> str:
        """Get legal basis for classification."""
        bases = {
            -1: "Necunoscut",
            0: "OUG 155/2024, Art 5(1)(a) - Administrație Publică Centrală",
            1: "OUG 155/2024, Art 5(1)(c) - Prestatori servicii de încredere calificate",
            2: "OUG 155/2024, Art 5(1)(d) - Furnizori DNS și Registre TLD",
            3: "OUG 155/2024, Art 5(2) și 6(2)(a) - Prestatori servicii de încredere necalificate",
            4: "OUG 155/2024, Art 5(2) și 6(2)(b) - Comunicații electronice publice",
            5: "OUG 155/2024, Art 5(3) - MSSP (doar mari)",
            6: "OUG 155/2024, Art 5(1) și Art 9 - Entități Esențiale (sau analiză Art 9)",
            7: "OUG 155/2024, Art 6(1) - Entități Importante"
        }
        return bases.get(priority, "OUG 155/2024")
    
    def _calculate_confidence(self, entity_data: EntityInput, sector_code: str) -> float:
        """Calculate confidence score for classification."""
        confidence = 1.0
        
        # Check data completeness
        if entity_data.employee_count <= 0:
            confidence -= 0.2
        if entity_data.annual_turnover_eur <= 0:
            confidence -= 0.2
        if not entity_data.balance_sheet_total:
            confidence -= 0.1
        
        # Check for borderline cases
        if 45 <= entity_data.employee_count <= 55:
            confidence -= 0.15
        
        return max(0.0, min(1.0, confidence))
    
    def validate_cui(self, cui: str) -> bool:
        """Validate Romanian CUI."""
        return self.kb.validate_cui(cui)
    
    def get_registration_requirements(self, classification: str) -> Dict[str, Any]:
        """Get DNSC registration requirements for classification."""
        if classification == "essential":
            return {
                "required": True,
                "deadline": "30 zile de la intrarea în vigoare a Ordinului 1/2025",
                "platform": "NIS2@RO",
                "risk_assessment": {"required": True, "deadline": "60 zile de la comunicarea deciziei DNSC"},
                "maturity_assessment": {"required": True, "deadline": "Anual"},
                "cybersecurity_officer": {"required": True, "appointment": "30 zile de la înregistrare"}
            }
        elif classification == "important":
            return {
                "required": True,
                "deadline": "30 zile de la intrarea în vigoare a Ordinului 1/2025",
                "platform": "NIS2@RO",
                "risk_assessment": {"required": True, "deadline": "60 zile de la comunicarea deciziei DNSC"},
                "maturity_assessment": {"required": True, "deadline": "Anual"},
                "cybersecurity_officer": {"required": True, "appointment": "30 zile de la înregistrare"}
            }
        else:
            return {
                "required": False,
                "note": "Înregistrare voluntară posibilă"
            }
