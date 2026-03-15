"""
CyFun (CyberFundamentals) Maturity Assessment Engine
Implements the DNSC CyberFundamentals Framework 2025.
"""
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field
from datetime import datetime, timezone

from shared.knowledge_base_ro import RomanianNIS2KnowledgeBase


@dataclass
class CyFunCategoryResult:
    """Result for a CyFun category."""
    code: str
    name: str
    documentation_score: float
    implementation_score: float
    overall_score: float
    key_measures: Dict[str, Any]
    gaps: List[str]


@dataclass
class CyFunResult:
    """Complete CyFun maturity assessment result."""
    entity_id: str
    entity_type: str  # essential, important, basic
    assessment_date: datetime
    overall_maturity: float
    categories: Dict[str, CyFunCategoryResult]
    key_measures_status: Dict[str, Any]
    is_compliant: bool
    gaps: List[str]
    recommendations: List[str]
    remediation_plan_required: bool
    next_assessment_due: str
    target_maturity: float = 0.0  # 3.5 for essential, 3.0 for important


class CyFunAssessor:
    """
    CyberFundamentals Maturity Assessor.
    
    Assesses entities against the 6 categories and 98 controls
    of the DNSC CyberFundamentals Framework 2025.
    """
    
    CATEGORIES = {
        "GV": "Guvernanță",
        "ID": "Identificare",
        "PR": "Protecție",
        "DE": "Detectare",
        "RS": "Răspuns",
        "RC": "Recuperare"
    }
    
    def __init__(self, kb: Optional[RomanianNIS2KnowledgeBase] = None):
        """Initialize with Romanian knowledge base."""
        self.kb = kb or RomanianNIS2KnowledgeBase()
        self.framework = self.kb._cyfun
    
    def assess(
        self,
        entity_id: str,
        entity_type: str,
        category_scores: Optional[Dict[str, Dict[str, float]]] = None
    ) -> CyFunResult:
        """
        Perform CyFun maturity assessment.
        
        Args:
            entity_id: Entity identifier
            entity_type: 'essential', 'important', or 'basic'
            category_scores: Optional scores per category/subcategory
                            Format: {"GV": {"OC": {"doc": 4, "imp": 3}}, ...}
                            
        Returns:
            CyFunResult with maturity assessment
        """
        # Use default scores if not provided
        if not category_scores:
            category_scores = self._generate_default_scores(entity_type)
        
        # Calculate per-category scores
        categories = {}
        all_gaps = []
        
        for cat_code, cat_name in self.CATEGORIES.items():
            cat_result = self._assess_category(
                cat_code, cat_name, category_scores.get(cat_code, {}), entity_type
            )
            categories[cat_code] = cat_result
            all_gaps.extend(cat_result.gaps)
        
        # Calculate overall maturity
        overall = sum(c.overall_score for c in categories.values()) / len(categories)
        
        # Assess key measures
        key_measures_status = self._assess_key_measures(category_scores)
        
        # Check compliance
        is_compliant, compliance_gaps = self._check_compliance(
            entity_type, overall, categories, key_measures_status
        )
        all_gaps.extend(compliance_gaps)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            entity_type, categories, key_measures_status, all_gaps
        )
        
        # Determine remediation plan requirement
        remediation_required = (
            entity_type == "essential" and (not is_compliant or overall < 3.5)
        ) or (
            entity_type == "important" and not is_compliant
        )
        
        # Set target maturity based on entity type
        target_maturity = 3.5 if entity_type == "essential" else (
            3.0 if entity_type == "important" else 2.5
        )
        
        return CyFunResult(
            entity_id=entity_id,
            entity_type=entity_type,
            assessment_date=datetime.now(timezone.utc),
            overall_maturity=round(overall, 2),
            categories=categories,
            key_measures_status=key_measures_status,
            is_compliant=is_compliant,
            gaps=list(set(all_gaps)),  # Remove duplicates
            recommendations=recommendations,
            remediation_plan_required=remediation_required,
            next_assessment_due="Anual",  # All entities need annual assessment
            target_maturity=target_maturity
        )
    
    def _assess_category(
        self,
        code: str,
        name: str,
        scores: Dict[str, Any],
        entity_type: str
    ) -> CyFunCategoryResult:
        """Assess a single category."""
        # Get category configuration
        cat_config = self.framework["categories"].get(code, {})
        subcategories = cat_config.get("subcategories", {})
        
        # Calculate scores
        doc_scores = []
        imp_scores = []
        key_measures = {}
        gaps = []
        
        for sub_code, sub_data in subcategories.items():
            sub_scores = scores.get(sub_code, {})
            
            # Get documentation and implementation scores
            doc = sub_scores.get("doc", sub_scores.get("documentation", 3))
            imp = sub_scores.get("imp", sub_scores.get("implementation", 3))
            
            doc_scores.append(doc)
            imp_scores.append(imp)
            
            # Check key measures
            controls = sub_data.get("controls", [])
            for ctrl in controls:
                if self.kb.is_key_measure(ctrl):
                    key_measures[ctrl] = {
                        "doc": doc,
                        "imp": imp,
                        "overall": (doc + imp) / 2,
                        "compliant": (doc >= 3 and imp >= 3)
                    }
                    
                    # Check if key measure is below threshold
                    if entity_type == "essential":
                        if doc < 3 or imp < 3:
                            gaps.append(
                                f"Măsură-cheie {ctrl} sub pragul minim (doc: {doc}, imp: {imp})"
                            )
        
        # Calculate averages
        avg_doc = sum(doc_scores) / len(doc_scores) if doc_scores else 0
        avg_imp = sum(imp_scores) / len(imp_scores) if imp_scores else 0
        overall = (avg_doc + avg_imp) / 2
        
        return CyFunCategoryResult(
            code=code,
            name=name,
            documentation_score=round(avg_doc, 2),
            implementation_score=round(avg_imp, 2),
            overall_score=round(overall, 2),
            key_measures=key_measures,
            gaps=gaps
        )
    
    def _assess_key_measures(
        self,
        category_scores: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Assess all key measures."""
        key_measures_list = self.kb.get_key_measures()
        
        status = {
            "total": len(key_measures_list),
            "compliant": 0,
            "non_compliant": 0,
            "measures": {}
        }
        
        for measure_code, measure_info in key_measures_list.items():
            # Extract category and subcategory from measure code
            # e.g., "ID.AM-08" -> category "ID", subcategory "AM"
            parts = measure_code.split("-")
            if len(parts) >= 2:
                cat_sub = parts[0].split(".")
                if len(cat_sub) >= 2:
                    cat = cat_sub[0]
                    sub = cat_sub[1]
                    
                    # Get scores
                    cat_data = category_scores.get(cat, {})
                    sub_data = cat_data.get(sub, {}) if isinstance(cat_data, dict) else {}
                    
                    doc = sub_data.get("doc", sub_data.get("documentation", 3))
                    imp = sub_data.get("imp", sub_data.get("implementation", 3))
                    overall = (doc + imp) / 2
                    
                    is_compliant = overall >= 3
                    
                    status["measures"][measure_code] = {
                        "name": measure_info.get("name", ""),
                        "documentation": doc,
                        "implementation": imp,
                        "overall": overall,
                        "compliant": is_compliant,
                        "target": measure_info.get("target", ">= 3")
                    }
                    
                    if is_compliant:
                        status["compliant"] += 1
                    else:
                        status["non_compliant"] += 1
        
        return status
    
    def _check_compliance(
        self,
        entity_type: str,
        overall: float,
        categories: Dict[str, CyFunCategoryResult],
        key_measures: Dict[str, Any]
    ) -> tuple[bool, List[str]]:
        """Check if entity meets compliance thresholds."""
        gaps = []
        is_compliant = True
        
        if entity_type == "essential":
            # Overall maturity >= 3.5
            if overall < 3.5:
                is_compliant = False
                gaps.append(f"Maturitate generală {overall:.2f} < 3.5 necesar pentru entități esențiale")
            
            # Each category >= 3
            for cat in categories.values():
                if cat.overall_score < 3:
                    is_compliant = False
                    gaps.append(f"Categoria {cat.code} ({cat.name}): {cat.overall_score:.2f} < 3")
            
            # Each key measure >= 3
            for measure_code, measure in key_measures.get("measures", {}).items():
                if measure["overall"] < 3:
                    is_compliant = False
                    gaps.append(f"Măsură-cheie {measure_code}: {measure['overall']:.2f} < 3")
        
        elif entity_type == "important":
            # Overall maturity >= 3
            if overall < 3:
                is_compliant = False
                gaps.append(f"Maturitate generală {overall:.2f} < 3 necesar pentru entități importante")
            
            # Each category >= 3
            for cat in categories.values():
                if cat.overall_score < 3:
                    is_compliant = False
                    gaps.append(f"Categoria {cat.code} ({cat.name}): {cat.overall_score:.2f} < 3")
        
        # Basic entities have no specific thresholds
        
        return is_compliant, gaps
    
    def _generate_recommendations(
        self,
        entity_type: str,
        categories: Dict[str, CyFunCategoryResult],
        key_measures: Dict[str, Any],
        gaps: List[str]
    ) -> List[str]:
        """Generate improvement recommendations."""
        recommendations = []
        
        # Overall recommendations based on entity type
        if entity_type == "essential":
            recommendations.append("Mențineți maturitatea generală peste 3.5")
            recommendations.append("Asigurați implementarea tuturor măsurilor-cheie")
        elif entity_type == "important":
            recommendations.append("Mențineți maturitatea generală peste 3.0")
            recommendations.append("Considerați implementarea măsurilor nivel ESENȚIAL")
        else:
            recommendations.append("Continuați îmbunătățirea măsurilor de securitate")
        
        # Category-specific recommendations
        weakest_categories = sorted(
            categories.values(),
            key=lambda c: c.overall_score
        )[:2]  # Bottom 2
        
        for cat in weakest_categories:
            if cat.overall_score < 3:
                recommendations.append(
                    f"Prioritizați îmbunătățirea categoriei {cat.code} ({cat.name}): {cat.overall_score:.2f}"
                )
        
        # Key measures recommendations
        non_compliant_key = [
            code for code, m in key_measures.get("measures", {}).items()
            if not m.get("compliant", True)
        ]
        
        if non_compliant_key:
            recommendations.append(
                f"Remediați {len(non_compliant_key)} măsuri-cheie neconforme"
            )
        
        return recommendations
    
    def _generate_default_scores(self, entity_type: str) -> Dict[str, Any]:
        """Generate default scores for demo purposes."""
        # Higher scores for demonstration
        base_score = 3.5 if entity_type == "essential" else 3.0 if entity_type == "important" else 2.5
        
        return {
            "GV": {
                "OC": {"doc": base_score, "imp": base_score - 0.2},
                "RM": {"doc": base_score + 0.2, "imp": base_score},
                "RR": {"doc": base_score, "imp": base_score + 0.1},
                "PO": {"doc": base_score - 0.1, "imp": base_score},
                "OV": {"doc": base_score, "imp": base_score - 0.2},
                "SC": {"doc": base_score - 0.3, "imp": base_score - 0.4}
            },
            "ID": {
                "AM": {"doc": base_score, "imp": base_score},
                "RA": {"doc": base_score + 0.1, "imp": base_score - 0.1},
                "IM": {"doc": base_score, "imp": base_score}
            },
            "PR": {
                "AA": {"doc": base_score, "imp": base_score + 0.2},
                "AT": {"doc": base_score - 0.2, "imp": base_score - 0.1},
                "DS": {"doc": base_score, "imp": base_score},
                "PS": {"doc": base_score + 0.1, "imp": base_score},
                "IR": {"doc": base_score - 0.1, "imp": base_score - 0.2}
            },
            "DE": {
                "CM": {"doc": base_score, "imp": base_score + 0.1},
                "AE": {"doc": base_score - 0.1, "imp": base_score}
            },
            "RS": {
                "RP": {"doc": base_score, "imp": base_score},
                "AN": {"doc": base_score - 0.2, "imp": base_score - 0.1},
                "CO": {"doc": base_score, "imp": base_score + 0.1},
                "MI": {"doc": base_score, "imp": base_score}
            },
            "RC": {
                "RP": {"doc": base_score - 0.3, "imp": base_score - 0.2},
                "CO": {"doc": base_score, "imp": base_score}
            }
        }
    
    def generate_remediation_plan(
        self,
        result: CyFunResult,
        deadline_days: int = 30
    ) -> Dict[str, Any]:
        """Generate remediation plan for non-compliant items."""
        plan = {
            "title": "Plan de remediere deficiențe CyFun",
            "entity_id": result.entity_id,
            "assessment_date": result.assessment_date.isoformat(),
            "deadline": f"{deadline_days} zile",
            "overall_maturity_target": 3.5 if result.entity_type == "essential" else 3.0,
            "actions": []
        }
        
        # Priority 1: Key measures below threshold
        for measure_code, measure in result.key_measures_status.get("measures", {}).items():
            if not measure.get("compliant", True):
                plan["actions"].append({
                    "priority": 1,
                    "category": "Măsură-cheie",
                    "item": measure_code,
                    "current": measure["overall"],
                    "target": 3.0,
                    "action": f"Implementare {measure.get('name', measure_code)}",
                    "estimated_effort": "2-4 săptămâni"
                })
        
        # Priority 2: Categories below threshold
        for cat in result.categories.values():
            if cat.overall_score < 3:
                plan["actions"].append({
                    "priority": 2,
                    "category": f"Categoria {cat.code}",
                    "item": cat.name,
                    "current": cat.overall_score,
                    "target": 3.0,
                    "action": f"Îmbunătățire controale {cat.code}",
                    "estimated_effort": "4-8 săptămâni"
                })
        
        # Priority 3: Overall maturity if needed
        if result.overall_maturity < plan["overall_maturity_target"]:
            plan["actions"].append({
                "priority": 3,
                "category": "Maturitate generală",
                "item": "Toate categoriile",
                "current": result.overall_maturity,
                "target": plan["overall_maturity_target"],
                "action": "Program continu de îmbunătățire",
                "estimated_effort": "Continuu"
            })
        
        return plan
