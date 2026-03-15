"""
ENIRE@RO Risk Assessment Engine
Calculates risk levels according to Ordinul Directorului DNSC nr. 2/2025.
"""
from typing import Optional, Dict, Any, List
from dataclasses import dataclass

from shared.knowledge_base_ro import RomanianNIS2KnowledgeBase


@dataclass
class ENIREResult:
    """ENIRE risk assessment result."""
    risk_score: float
    cyfun_level: str  # BASIC, IMPORTANT, ESENTIAL
    level_description: str
    sector: str
    size: str
    inputs: Dict[str, str]
    values: Dict[str, float]
    risk_factors: List[str]
    justification_required: bool
    recommendations: List[str]


class ENIREAssessor:
    """
    ENIRE@RO Risk Level Assessor.
    
    Implements the methodology from Ordinul Directorului DNSC nr. 2/2025:
    Nivel_Risc = Actor × Atac × Impact × Probabilitate × Dimensiune × Natură
    """
    
    def __init__(self, kb: Optional[RomanianNIS2KnowledgeBase] = None):
        """Initialize with Romanian knowledge base."""
        self.kb = kb or RomanianNIS2KnowledgeBase()
    
    def assess(
        self,
        sector_code: str,
        size: str,
        actor: Optional[str] = None,
        attack: Optional[str] = None,
        impact: Optional[str] = None,
        probability: Optional[str] = None,
        nature: str = "Targeted",
        justification: str = ""
    ) -> ENIREResult:
        """
        Perform ENIRE risk assessment.
        
        Args:
            sector_code: Romanian sector code (e.g., '101', '105.1')
            size: Entity size (micro, small, medium, large)
            actor: Threat actor type (uses sector default if not provided)
            attack: Attack type (uses sector default if not provided)
            impact: Impact level (uses sector default if not provided)
            probability: Probability level (uses sector default if not provided)
            nature: Attack nature (Global or Targeted)
            justification: Justification for any deviation from defaults
            
        Returns:
            ENIREResult with calculated risk score and CyFunRO level
        """
        # Get sector configuration
        main_sector = sector_code.split(".")[0]
        sector_config = self.kb._enire["sectors"].get(main_sector)
        
        if not sector_config:
            raise ValueError(f"Unknown sector code: {sector_code}")
        
        defaults = sector_config["default_matrix"]
        
        # Use provided values or defaults
        final_actor = actor or defaults["actor"]
        final_attack = attack or defaults["attack"]
        final_impact = impact or defaults["impact"]
        final_probability = probability or defaults["probability"]
        
        # Calculate score
        calc = self.kb._enire["methodology"]["calculation"]
        
        actor_val = calc["actor_values"].get(final_actor, 3)
        attack_val = calc["attack_values"].get(final_attack, 5)
        impact_val = calc["impact_values"].get(final_impact, 5)
        prob_val = calc["probability_values"].get(final_probability, 0.5)
        size_mult = calc["size_multipliers"].get(size.capitalize(), 1)
        nature_mult = calc["nature_multipliers"].get(nature, 2)
        
        risk_score = (
            actor_val * attack_val * impact_val * 
            prob_val * size_mult * nature_mult
        )
        
        # Determine CyFunRO level
        thresholds = self.kb._enire["methodology"]["risk_thresholds"]
        
        if risk_score >= thresholds["essential"]["min"]:
            cyfun_level = "ESENTIAL"
            level_desc = thresholds["essential"]["description"]
        elif risk_score >= thresholds["important"]["min"]:
            cyfun_level = "IMPORTANT"
            level_desc = thresholds["important"]["description"]
        else:
            cyfun_level = "BASIC"
            level_desc = thresholds["basic"]["description"]
        
        # Check if justification required
        justification_required = bool(
            (actor and actor != defaults["actor"]) or
            (attack and attack != defaults["attack"]) or
            (impact and impact != defaults["impact"]) or
            (probability and probability != defaults["probability"])
        )
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            cyfun_level, risk_score, sector_config.get("risk_factors", [])
        )
        
        return ENIREResult(
            risk_score=round(risk_score, 2),
            cyfun_level=cyfun_level,
            level_description=level_desc,
            sector=sector_config["name"],
            size=size,
            inputs={
                "actor": final_actor,
                "attack": final_attack,
                "impact": final_impact,
                "probability": final_probability,
                "nature": nature
            },
            values={
                "actor": actor_val,
                "attack": attack_val,
                "impact": impact_val,
                "probability": prob_val,
                "size_multiplier": size_mult,
                "nature_multiplier": nature_mult
            },
            risk_factors=sector_config.get("risk_factors", []),
            justification_required=justification_required,
            recommendations=recommendations
        )
    
    def _generate_recommendations(
        self,
        cyfun_level: str,
        risk_score: float,
        risk_factors: List[str]
    ) -> List[str]:
        """Generate recommendations based on risk level."""
        recommendations = []
        
        if cyfun_level == "ESENTIAL":
            recommendations.append("Implementați toate măsurile din CyFunRO nivel ESENȚIAL")
            recommendations.append("Desemnați un Ofițer de Securitate Cibernetică")
            recommendations.append("Efectuați evaluări de risc detaliate trimestrial")
        elif cyfun_level == "IMPORTANT":
            recommendations.append("Implementați măsurile din CyFunRO nivel IMPORTANT")
            recommendations.append("Evaluați necesitatea unui Ofițer de Securitate Cibernetică")
            recommendations.append("Efectuați evaluări de risc semestrial")
        else:
            recommendations.append("Implementați măsurile de bază CyFunRO")
            recommendations.append("Considerați implementarea măsurilor nivel IMPORTANT")
            recommendations.append("Efectuați evaluări de risc anual")
        
        # Add sector-specific recommendations
        for factor in risk_factors[:3]:  # Top 3 risk factors
            recommendations.append(f"Abordați factorul de risc: {factor}")
        
        return recommendations
    
    def get_report_template(self, result: ENIREResult) -> Dict[str, Any]:
        """
        Generate report template for ENIRE assessment.
        
        Returns:
            Report structure for submission to DNSC
        """
        return {
            "title": "Raportul evaluării nivelului de risc al entității",
            "sections": [
                {
                    "name": "Identificare entitate",
                    "fields": ["Denumire", "CUI", "Cod sector", "Dimensiune"]
                },
                {
                    "name": "Evaluare risc",
                    "fields": [
                        "Scor risc calculat",
                        "Nivel CyFunRO",
                        "Actori de amenințare evaluați",
                        "Tipuri de atac evaluate",
                        "Justificare modificări (dacă aplicabil)"
                    ]
                },
                {
                    "name": "Concluzii și recomandări",
                    "fields": ["Nivel risc determinat", "Măsuri recomandate"]
                }
            ],
            "submission": {
                "platform": "NIS2@RO",
                "deadline": "60 zile de la comunicarea deciziei DNSC",
                "format": "PDF + XML pentru platformă"
            },
            "data": {
                "sector": result.sector,
                "size": result.size,
                "risk_score": result.risk_score,
                "cyfun_level": result.cyfun_level,
                "inputs": result.inputs
            }
        }
    
    def compare_with_defaults(
        self,
        sector_code: str,
        actor: str,
        attack: str,
        impact: str,
        probability: str
    ) -> Dict[str, Any]:
        """Compare provided values with sector defaults."""
        main_sector = sector_code.split(".")[0]
        sector_config = self.kb._enire["sectors"].get(main_sector)
        
        if not sector_config:
            return {"error": "Unknown sector"}
        
        defaults = sector_config["default_matrix"]
        
        differences = {}
        
        if actor != defaults["actor"]:
            differences["actor"] = {
                "provided": actor,
                "default": defaults["actor"],
                "justification_required": True
            }
        
        if attack != defaults["attack"]:
            differences["attack"] = {
                "provided": attack,
                "default": defaults["attack"],
                "justification_required": True
            }
        
        if impact != defaults["impact"]:
            differences["impact"] = {
                "provided": impact,
                "default": defaults["impact"],
                "justification_required": True
            }
        
        if probability != defaults["probability"]:
            differences["probability"] = {
                "provided": probability,
                "default": defaults["probability"],
                "justification_required": True
            }
        
        return {
            "has_differences": len(differences) > 0,
            "differences": differences,
            "note": "Modificările valorilor implicite necesită justificare documentată"
        }
