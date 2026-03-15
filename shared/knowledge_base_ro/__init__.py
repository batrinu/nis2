"""
Romanian NIS2 Knowledge Base
Implements OUG 155/2024, Law 124/2025, and DNSC Orders 1/2025 and 2/2025
"""
import json
from pathlib import Path
from typing import Optional, Dict, Any, List
from dataclasses import dataclass


@dataclass
class SizeClassificationRO:
    """Romanian size classification per Legea 346/2004."""
    category: str  # micro, small, medium, large
    employees: int
    turnover_eur: float
    balance_eur: float
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "category": self.category,
            "employees": self.employees,
            "turnover_eur": self.turnover_eur,
            "balance_eur": self.balance_eur
        }


@dataclass  
class EntityTypeRO:
    """Romanian entity type definition."""
    code: str
    name: str
    entity_types: List[str]
    caen_codes: List[str]
    priority: Optional[int] = None
    legal_ref: Optional[str] = None


class RomanianNIS2KnowledgeBase:
    """
    Knowledge base for Romanian NIS2 implementation.
    Loads and provides access to Romanian-specific regulations.
    """
    
    def __init__(self, data_path: Optional[str] = None):
        """Initialize with path to Romanian knowledge base files."""
        if data_path is None:
            data_path = Path(__file__).parent
        else:
            data_path = Path(data_path)
        
        self.data_path = data_path
        self._sectors = None
        self._article9 = None
        self._enire = None
        self._cyfun = None
        
        self._load_all()
    
    def _load_all(self):
        """Load all Romanian knowledge base files."""
        # Load sectors
        with open(self.data_path / "sectors_ro.json", "r", encoding="utf-8") as f:
            self._sectors = json.load(f)
        
        # Load Article 9 criteria
        with open(self.data_path / "article9_criteria.json", "r", encoding="utf-8") as f:
            self._article9 = json.load(f)
        
        # Load ENIRE scoring
        with open(self.data_path / "enire_scoring.json", "r", encoding="utf-8") as f:
            self._enire = json.load(f)
        
        # Load CyFun measures
        with open(self.data_path / "cyfun_measures.json", "r", encoding="utf-8") as f:
            self._cyfun = json.load(f)
    
    # ===== Size Classification =====
    
    def calculate_size_ro(self, employees: int, turnover_eur: float, balance_eur: float) -> str:
        """
        Calculate Romanian size category per Legea 346/2004.
        
        Returns:
            'micro', 'small', 'medium', or 'large'
        """
        thresholds = self._sectors["size_thresholds_ro"]
        
        # Check large first
        if (employees >= thresholds["large"]["employees_min"] or 
            turnover_eur >= thresholds["large"]["turnover_min_eur"] or
            balance_eur >= thresholds["large"]["balance_min_eur"]):
            return "large"
        
        # Check medium
        if (employees <= thresholds["medium"]["employees_max"] and 
            turnover_eur <= thresholds["medium"]["turnover_max_eur"] and
            balance_eur <= thresholds["medium"]["balance_max_eur"]):
            # Also check if above small
            if (employees > thresholds["small"]["employees_max"] or 
                turnover_eur > thresholds["small"]["turnover_max_eur"] or
                balance_eur > thresholds["small"]["balance_max_eur"]):
                return "medium"
        
        # Check small
        if (employees <= thresholds["small"]["employees_max"] and 
            turnover_eur <= thresholds["small"]["turnover_max_eur"] and
            balance_eur <= thresholds["small"]["balance_max_eur"]):
            # Also check if above micro
            if (employees > thresholds["micro"]["employees_max"] or 
                turnover_eur > thresholds["micro"]["turnover_max_eur"] or
                balance_eur > thresholds["micro"]["balance_max_eur"]):
                return "small"
        
        # Must be micro
        return "micro"
    
    # ===== Sector Classification =====
    
    def get_sector_info(self, sector_code: str) -> Optional[Dict[str, Any]]:
        """Get sector information by code (e.g., '101', '201')."""
        # Check Annex 1
        if sector_code in self._sectors["annex_1"]["sectors"]:
            return self._sectors["annex_1"]["sectors"][sector_code]
        
        # Check Annex 2
        if sector_code in self._sectors["annex_2"]["sectors"]:
            return self._sectors["annex_2"]["sectors"][sector_code]
        
        return None
    
    def get_subsector_info(self, subsector_code: str) -> Optional[Dict[str, Any]]:
        """Get subsector information by code (e.g., '101.1', '201.1')."""
        sector_code = subsector_code.split(".")[0]
        sector = self.get_sector_info(sector_code)
        
        if sector and "subsectors" in sector:
            for sub in sector["subsectors"]:
                if sub["code"] == subsector_code:
                    return sub
        
        return None
    
    def classify_by_priority(self, sector_code: str, size: str) -> Dict[str, Any]:
        """
        Classify entity based on priority rules.
        
        Returns dict with:
            - classification: 'essential', 'important', or 'out_of_scope'
            - priority: priority number (0-7)
            - rule: description of rule applied
            - art9_required: whether Art 9 analysis is needed
        """
        subsector = self.get_subsector_info(sector_code)
        sector = self.get_sector_info(sector_code.split(".")[0])
        
        if not subsector:
            return {"classification": "unknown", "priority": -1}
        
        priority = subsector.get("priority")
        
        # Priority 0: Administrație Publică Centrală
        if priority == 0:
            return {
                "classification": "essential",
                "priority": 0,
                "rule": "Administrație Publică Centrală - Esențial indiferent de dimensiune",
                "art9_required": False
            }
        
        # Priority 1: Servicii de încredere calificate
        if priority == 1:
            return {
                "classification": "essential",
                "priority": 1,
                "rule": "Prestatori servicii de încredere calificate - Esențial indiferent de dimensiune",
                "art9_required": False
            }
        
        # Priority 2: DNS și TLD
        if priority == 2:
            return {
                "classification": "essential",
                "priority": 2,
                "rule": "Furnizori DNS și Registre TLD - Esențial indiferent de dimensiune",
                "art9_required": False
            }
        
        # Priority 3: Servicii de încredere necalificate
        if priority == 3:
            if size in ["micro", "small"]:
                return {
                    "classification": "important",
                    "priority": 3,
                    "rule": "Prestatori servicii de încredere necalificate - Important (micro/small)",
                    "art9_required": False
                }
            else:
                return {
                    "classification": "essential",
                    "priority": 3,
                    "rule": "Prestatori servicii de încredere necalificate - Esențial (medium/large)",
                    "art9_required": False
                }
        
        # Priority 4: Comunicații electronice publice
        if priority == 4:
            if size in ["micro", "small"]:
                return {
                    "classification": "important",
                    "priority": 4,
                    "rule": "Comunicații electronice publice - Important (micro/small)",
                    "art9_required": False
                }
            else:
                return {
                    "classification": "essential",
                    "priority": 4,
                    "rule": "Comunicații electronice publice - Esențial (medium/large)",
                    "art9_required": False
                }
        
        # Priority 5: MSSP (only if large)
        if priority == 5:
            if size == "large":
                return {
                    "classification": "essential",
                    "priority": 5,
                    "rule": "MSSP - Esențial (large only)",
                    "art9_required": False
                }
            else:
                return {
                    "classification": "out_of_scope",
                    "priority": 5,
                    "rule": "MSSP - În afara domeniului de aplicare (non-large)",
                    "art9_required": False
                }
        
        # Determine annex
        main_sector_code = sector_code.split(".")[0]
        is_annex_1 = main_sector_code in self._sectors["annex_1"]["sectors"]
        is_annex_2 = main_sector_code in self._sectors["annex_2"]["sectors"]
        
        # Priority 6: Annex 1 sectors
        if is_annex_1:
            if size in ["medium", "large"]:
                return {
                    "classification": "essential",
                    "priority": 6,
                    "rule": f"{sector['name']} - Esențial (medium/large)",
                    "art9_required": False
                }
            else:
                return {
                    "classification": "out_of_scope",
                    "priority": 6,
                    "rule": f"{sector['name']} - În afara domeniului (micro/small), necesită analiză Art 9",
                    "art9_required": True
                }
        
        # Priority 7: Annex 2 sectors
        if is_annex_2:
            if size in ["medium", "large"]:
                return {
                    "classification": "important",
                    "priority": 7,
                    "rule": f"{sector['name']} - Important (medium/large)",
                    "art9_required": False
                }
            else:
                return {
                    "classification": "out_of_scope",
                    "priority": 7,
                    "rule": f"{sector['name']} - În afara domeniului (micro/small)",
                    "art9_required": False
                }
        
        return {"classification": "unknown", "priority": -1, "rule": "Sector necunoscut"}
    
    # ===== Article 9 Criteria =====
    
    def get_article9_criteria(self) -> Dict[str, Any]:
        """Get all Article 9 disruptive effect criteria."""
        return self._article9
    
    def evaluate_article9_lit_a(self, is_sole_provider: bool) -> Dict[str, Any]:
        """Evaluate Article 9 lit a) - Sole provider of essential service."""
        return {
            "criterion": "art_9_lit_a",
            "applies": is_sole_provider,
            "weight": "critical",
            "threshold_met": is_sole_provider
        }
    
    def evaluate_article9_lit_b(self, dimension: str, value: float) -> Dict[str, Any]:
        """
        Evaluate Article 9 lit b) - Impact assessment.
        
        Args:
            dimension: One of the lit b dimensions (e.g., 'b1_drepturi_fundamentale')
            value: The measured value
            
        Returns:
            Dict with evaluation result
        """
        dim_config = self._article9["criteria"]["art_9_lit_b"]["dimensions"].get(dimension)
        
        if not dim_config:
            return {"error": f"Unknown dimension: {dimension}"}
        
        # Determine level based on thresholds
        level = "scazut"
        # This would need specific logic per dimension type
        
        return {
            "criterion": "art_9_lit_b",
            "dimension": dimension,
            "value": value,
            "level": level,
            "weight": dim_config.get("weight", 1.0),
            "thresholds": dim_config.get("thresholds", {})
        }
    
    # ===== ENIRE Scoring =====
    
    def calculate_enire_score(
        self,
        sector_code: str,
        size: str,
        actor: Optional[str] = None,
        attack: Optional[str] = None,
        impact: Optional[str] = None,
        probability: Optional[str] = None,
        nature: str = "Targeted"
    ) -> Dict[str, Any]:
        """
        Calculate ENIRE risk score for an entity.
        
        Uses default values from sector if specific values not provided.
        """
        sector = self._enire["sectors"].get(sector_code)
        
        if not sector:
            return {"error": f"Unknown sector: {sector_code}"}
        
        defaults = sector["default_matrix"]
        
        # Use provided values or defaults
        actor = actor or defaults["actor"]
        attack = attack or defaults["attack"]
        impact = impact or defaults["impact"]
        probability = probability or defaults["probability"]
        
        # Get values from scoring methodology
        calc = self._enire["methodology"]["calculation"]
        
        actor_val = calc["actor_values"].get(actor, 3)
        attack_val = calc["attack_values"].get(attack, 5)
        impact_val = calc["impact_values"].get(impact, 5)
        prob_val = calc["probability_values"].get(probability, 0.5)
        size_mult = calc["size_multipliers"].get(size.capitalize(), 1)
        nature_mult = calc["nature_multipliers"].get(nature, 2)
        
        # Calculate risk score
        risk_score = actor_val * attack_val * impact_val * prob_val * size_mult * nature_mult
        
        # Determine CyFunRO level
        thresholds = self._enire["methodology"]["risk_thresholds"]
        
        if risk_score >= thresholds["essential"]["min"]:
            cyfun_level = "ESENTIAL"
            level_desc = thresholds["essential"]["description"]
        elif risk_score >= thresholds["important"]["min"]:
            cyfun_level = "IMPORTANT"
            level_desc = thresholds["important"]["description"]
        else:
            cyfun_level = "BASIC"
            level_desc = thresholds["basic"]["description"]
        
        return {
            "risk_score": risk_score,
            "cyfun_level": cyfun_level,
            "level_description": level_desc,
            "inputs": {
                "actor": actor,
                "attack": attack,
                "impact": impact,
                "probability": probability,
                "size": size,
                "nature": nature
            },
            "values": {
                "actor": actor_val,
                "attack": attack_val,
                "impact": impact_val,
                "probability": prob_val,
                "size_multiplier": size_mult,
                "nature_multiplier": nature_mult
            },
            "risk_factors": sector.get("risk_factors", [])
        }
    
    # ===== CyFun Measures =====
    
    def get_cyfun_framework(self) -> Dict[str, Any]:
        """Get complete CyFun framework."""
        return self._cyfun
    
    def get_category(self, code: str) -> Optional[Dict[str, Any]]:
        """Get CyFun category by code (e.g., 'GV', 'ID', 'PR')."""
        return self._cyfun["categories"].get(code)
    
    def get_key_measures(self) -> Dict[str, Any]:
        """Get all key measures (Măsuri-cheie)."""
        return self._cyfun["key_measures"]["list"]
    
    def is_key_measure(self, control_code: str) -> bool:
        """Check if a control is a key measure."""
        return control_code in self._cyfun["key_measures"]["list"]
    
    def get_compliance_threshold(self, entity_type: str) -> Dict[str, Any]:
        """
        Get compliance thresholds for entity type.
        
        Args:
            entity_type: 'essential', 'important', or 'basic'
        """
        return self._cyfun["framework"]["compliance_thresholds"].get(entity_type, {})
    
    # ===== Utilities =====
    
    @staticmethod
    def validate_cui(cui: str) -> bool:
        """
        Validate Romanian CUI (Cod Unic de Identificare) using the Romanian algorithm.
        
        Args:
            cui: CUI to validate (with or without 'RO' prefix)
            
        Returns:
            True if valid, False otherwise
        """
        # Remove RO prefix and any non-digit characters
        cui_clean = cui.upper().replace("RO", "").replace(" ", "").replace("-", "")
        
        if not cui_clean.isdigit():
            return False
        
        if len(cui_clean) < 2 or len(cui_clean) > 10:
            return False
        
        # Romanian CUI validation algorithm
        # Control digit is the last digit
        control_digit = int(cui_clean[-1])
        
        # Multipliers for validation
        multipliers = [7, 5, 3, 2, 1, 7, 5, 3, 2]
        
        # Get the number part (without control digit)
        number_part = cui_clean[:-1]
        
        # Pad with zeros to match multiplier length
        number_part = number_part.zfill(9)
        
        # Calculate sum
        total = 0
        for i, digit in enumerate(number_part):
            total += int(digit) * multipliers[i]
        
        # Calculate control digit
        calculated_control = (total * 10) % 11
        if calculated_control == 10:
            calculated_control = 0
        
        return calculated_control == control_digit
    
    def get_all_sectors(self) -> List[Dict[str, Any]]:
        """Get all sectors from both annexes."""
        sectors = []
        
        for code, sector in self._sectors["annex_1"]["sectors"].items():
            sectors.append({
                "code": code,
                "name": sector["name"],
                "annex": 1
            })
        
        for code, sector in self._sectors["annex_2"]["sectors"].items():
            sectors.append({
                "code": code,
                "name": sector["name"],
                "annex": 2
            })
        
        return sectors


# Convenience function
def get_ro_kb() -> RomanianNIS2KnowledgeBase:
    """Get default Romanian knowledge base instance."""
    return RomanianNIS2KnowledgeBase()
