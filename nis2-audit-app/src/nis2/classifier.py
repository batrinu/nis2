"""
NIS2 Entity Classification functions.
"""
from datetime import datetime, timezone
from .models import EntityInput, EntityClassification, CrossBorderInfo
from .knowledge_base import get_sector_info, check_size_threshold, determine_lead_authority


def classify_entity(entity: EntityInput) -> EntityClassification:
    """
    Classify an entity under NIS2.
    
    Args:
        entity: Entity input data
        
    Returns:
        Classification result
    """
    reasoning = []
    
    # Step 1: Map sector
    sector_info = get_sector_info(entity.sector)
    if sector_info is None:
        return EntityClassification(
            entity_id=entity.entity_id or f"ENT-{datetime.now(timezone.utc).timestamp()}",
            classification="Non-Qualifying",
            legal_basis="Sector not found in Annex I or II",
            annex=None,
            sector_classification=entity.sector,
            size_qualification=False,
            lead_authority="XX",
            confidence_score=0.0,
            reasoning_chain=[f"Unknown sector: {entity.sector}"]
        )
    
    reasoning.append(f"Sector '{entity.sector}' mapped to {sector_info['annex']}")
    
    # Step 2: Check size
    size = check_size_threshold(
        entity.employee_count,
        entity.annual_turnover_eur,
        entity.balance_sheet_total or 0
    )
    reasoning.append(f"Size check: medium={size['is_medium']}, large={size['is_large']}")
    
    # Step 3: Check exceptions
    has_exception = sector_info.get("size_exception", False)
    
    # Step 4: Determine classification
    if sector_info["annex"] == "Annex I":
        if size["qualifies"] or has_exception or entity.is_public_admin or \
           entity.is_dns_provider or entity.is_tld_registry or entity.is_trust_service_provider:
            classification = "Essential Entity"
            legal_basis = f"Article {sector_info['article']} - Annex I sector"
            reasoning.append("Classified as Essential Entity")
        else:
            classification = "Non-Qualifying"
            legal_basis = "Below medium enterprise threshold"
            reasoning.append("Annex I but below size threshold")
    else:  # Annex II
        if size["qualifies"]:
            classification = "Important Entity"
            legal_basis = f"Article {sector_info['article']} - Annex II sector"
            reasoning.append("Classified as Important Entity")
        else:
            classification = "Non-Qualifying"
            legal_basis = "Below medium enterprise threshold"
            reasoning.append("Annex II but below size threshold")
    
    # Step 5: Determine lead authority
    lead = determine_lead_authority(entity.cross_border_operations)
    reasoning.append(f"Lead authority: {lead}")
    
    # Step 6: Calculate confidence
    confidence = 1.0
    if entity.employee_count <= 0 or entity.annual_turnover_eur <= 0:
        confidence -= 0.2
    if 45 <= entity.employee_count <= 55:  # Borderline
        confidence -= 0.15
    
    return EntityClassification(
        entity_id=entity.entity_id or f"ENT-{datetime.now(timezone.utc).timestamp()}",
        classification=classification,
        legal_basis=legal_basis,
        annex=sector_info["annex"],
        sector_classification=sector_info["parent_sector"],
        size_qualification=size["qualifies"],
        lead_authority=lead,
        confidence_score=max(0.0, min(1.0, confidence)),
        reasoning_chain=reasoning
    )


def check_national_designation(entity: EntityInput) -> dict:
    """
    Check if entity may qualify for national designation.
    Some countries can designate smaller entities as Essential under Article 9.
    
    Returns dict with applicable flag and action required.
    """
    sector_info = get_sector_info(entity.sector)
    if sector_info is None:
        return {"applicable": False}
    
    size = check_size_threshold(
        entity.employee_count,
        entity.annual_turnover_eur,
        entity.balance_sheet_total or 0
    )
    
    # If in Annex I but below size threshold, may be designated
    if sector_info["annex"] == "Annex I" and not size["qualifies"]:
        return {
            "applicable": True,
            "reason": "Annex I sector below size threshold - may be designated under Article 9",
            "action_required": "Check national transposition for designation rules",
            "consult_authority": True
        }
    
    return {"applicable": False}
