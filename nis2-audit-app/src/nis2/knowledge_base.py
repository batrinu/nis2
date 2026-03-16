"""
NIS2 Directive knowledge base.
Contains regulatory data for classification and assessment.
"""

# Annex I sectors - Essential Entities
ANNEX_I_SECTORS = {
    "energy": {
        "sub_sectors": ["electricity", "oil", "gas", "hydrogen", "district_heating", "district_cooling"],
        "article": "24"
    },
    "transport": {
        "sub_sectors": ["air", "rail", "water", "road"],
        "article": "24"
    },
    "banking": {
        "sub_sectors": ["credit_institution"],
        "article": "24"
    },
    "financial_markets": {
        "sub_sectors": ["trading_venue", "central_counterparty"],
        "article": "24"
    },
    "health": {
        "sub_sectors": ["healthcare_provider", "medical_device_manufacturer"],
        "article": "24"
    },
    "drinking_water": {
        "sub_sectors": ["supplier", "distributor"],
        "article": "24"
    },
    "waste_water": {
        "sub_sectors": ["collector", "treatment_operator"],
        "article": "24"
    },
    "digital_infrastructure": {
        "sub_sectors": ["ixp", "dns_provider", "tld_registry", "cloud_provider", "data_center", "cdn"],
        "article": "24",
        "size_exception": True
    },
    "ict_services": {
        "sub_sectors": ["managed_service_provider", "managed_security_service_provider"],
        "article": "24"
    },
    "public_administration": {
        "sub_sectors": ["central_government"],
        "article": "24",
        "size_exception": True
    },
    "space": {
        "sub_sectors": ["ground_based_infrastructure"],
        "article": "24"
    }
}

# Annex II sectors - Important Entities
ANNEX_II_SECTORS = {
    "postal": {"sub_sectors": ["postal_service", "courier_service"], "article": "25"},
    "waste_management": {"sub_sectors": ["waste_operator"], "article": "25"},
    "chemicals": {"sub_sectors": ["manufacture", "production", "distribution"], "article": "25"},
    "food": {"sub_sectors": ["production", "processing", "distribution"], "article": "25"},
    "manufacturing": {
        "sub_sectors": ["medical_device", "computer_electronic", "electrical_equipment", 
                        "machinery", "motor_vehicles", "transport_equipment"],
        "article": "25"
    },
    "digital_providers": {
        "sub_sectors": ["online_marketplace", "search_engine", "social_network"],
        "article": "25"
    },
    "research": {"sub_sectors": ["research_organization"], "article": "25"}
}

# Article 21 requirements for audit
ARTICLE_21_REQUIREMENTS = {
    "21(2)(a)": {
        "title": "Risk analysis and security policies",
        "description": "Appropriate technical and organisational measures to manage risks",
        "domain": "governance"
    },
    "21(2)(b)": {
        "title": "Incident handling",
        "description": "Prevent, detect, respond to and recover from incidents",
        "domain": "incident_response"
    },
    "21(2)(c)": {
        "title": "Business continuity",
        "description": "Business continuity, crisis management and disaster recovery",
        "domain": "technical_controls"
    },
    "21(2)(d)": {
        "title": "Supply chain security",
        "description": "Security of supply chains and ICT products/services",
        "domain": "supply_chain"
    },
    "21(2)(e)": {
        "title": "Security in acquisition and development",
        "description": "Security in network and information systems acquisition, development and maintenance",
        "domain": "technical_controls"
    },
    "21(2)(f)": {
        "title": "Vulnerability handling",
        "description": "Policies and procedures to assess and treat vulnerabilities",
        "domain": "technical_controls"
    },
    "21(2)(g)": {
        "title": "Cryptography and encryption",
        "description": "Use of cryptography and encryption where appropriate",
        "domain": "technical_controls"
    },
    "21(2)(h)": {
        "title": "Human resources security",
        "description": "Security in human resources, including access control and training",
        "domain": "governance"
    },
    "21(2)(i)": {
        "title": "Multi-factor authentication",
        "description": "Use of multi-factor authentication and secured communication",
        "domain": "technical_controls"
    }
}

# Audit checklists by domain
AUDIT_CHECKLIST = {
    "governance": [
        {"id": "GOV-01", "text": "Risk analysis and information system security policies implemented", "article": "21(2)(a)"},
        {"id": "GOV-02", "text": "Management approval of security policies documented", "article": "21(2)(a)"},
        {"id": "GOV-03", "text": "Regular review and update of security policies", "article": "21(2)(a)"},
        {"id": "GOV-04", "text": "Security roles and responsibilities defined", "article": "21(2)(h)"},
    ],
    "incident_response": [
        {"id": "INC-01", "text": "Incident response procedures documented", "article": "21(2)(b)"},
        {"id": "INC-02", "text": "Incident detection capabilities in place", "article": "21(2)(b)"},
        {"id": "INC-03", "text": "Incident reporting to authorities process defined", "article": "21(2)(b)"},
        {"id": "INC-04", "text": "Post-incident analysis conducted", "article": "21(2)(b)"},
    ],
    "technical_controls": [
        {"id": "TECH-01", "text": "Access control policies implemented", "article": "21(2)(i)"},
        {"id": "TECH-02", "text": "Multi-factor authentication for sensitive systems", "article": "21(2)(i)"},
        {"id": "TECH-03", "text": "Vulnerability management program in place", "article": "21(2)(f)"},
        {"id": "TECH-04", "text": "Encryption used for sensitive data", "article": "21(2)(g)"},
        {"id": "TECH-05", "text": "Network segmentation implemented", "article": "21(2)(a)"},
        {"id": "TECH-06", "text": "Logging and monitoring systems operational", "article": "21(2)(b)"},
    ],
    "business_continuity": [
        {"id": "BC-01", "text": "Business continuity plan documented", "article": "21(2)(c)"},
        {"id": "BC-02", "text": "Disaster recovery procedures defined", "article": "21(2)(c)"},
        {"id": "BC-03", "text": "Regular testing of continuity plans", "article": "21(2)(c)"},
        {"id": "BC-04", "text": "Backup and restoration procedures implemented", "article": "21(2)(c)"},
    ],
    "supply_chain": [
        {"id": "SUP-01", "text": "Supply chain security policies defined", "article": "21(2)(d)"},
        {"id": "SUP-02", "text": "Security requirements in vendor contracts", "article": "21(2)(d)"},
        {"id": "SUP-03", "text": "Vendor risk assessments conducted", "article": "21(2)(d)"},
    ]
}


def get_sector_info(sector: str) -> dict | None:
    """Get sector information from Annex I or II."""
    sector_lower = sector.lower().replace(" ", "_")
    
    if sector_lower in ANNEX_I_SECTORS:
        info = ANNEX_I_SECTORS[sector_lower].copy()
        info["annex"] = "Annex I"
        info["parent_sector"] = sector_lower
        return info
    
    if sector_lower in ANNEX_II_SECTORS:
        info = ANNEX_II_SECTORS[sector_lower].copy()
        info["annex"] = "Annex II"
        info["parent_sector"] = sector_lower
        return info
    
    # Try matching sub-sectors
    for parent, data in {**ANNEX_I_SECTORS, **ANNEX_II_SECTORS}.items():
        if sector_lower in [s.lower() for s in data["sub_sectors"]]:
            info = data.copy()
            info["annex"] = "Annex I" if parent in ANNEX_I_SECTORS else "Annex II"
            info["parent_sector"] = parent
            return info
    
    return None


def check_size_threshold(employees: int, turnover: float, balance: float = 0) -> dict:
    """
    Check if entity meets medium/large enterprise criteria.
    
    EU Recommendation 2003/361:
    - Medium: 50-249 employees AND (€10M+ turnover OR €10M+ balance)
    - Large: 250+ employees AND (€50M+ turnover OR €43M+ balance)
    """
    is_medium = 50 <= employees <= 249 and (turnover >= 10_000_000 or balance >= 10_000_000)
    is_large = employees >= 250 and (turnover >= 50_000_000 or balance >= 43_000_000)
    
    return {
        "is_medium": is_medium,
        "is_large": is_large,
        "qualifies": is_medium or is_large
    }


def determine_lead_authority(cross_border) -> str:
    """Determine lead supervisory authority based on NIS2 rules."""
    if not cross_border.operates_cross_border:
        return cross_border.main_establishment or "XX"
    
    # Main establishment principle
    if cross_border.main_establishment:
        return cross_border.main_establishment
    
    # Decision location
    if hasattr(cross_border, 'decision_location') and cross_border.decision_location:
        return cross_border.decision_location
    
    # Majority of employees
    if hasattr(cross_border, 'majority_employees_location') and cross_border.majority_employees_location:
        return cross_border.majority_employees_location
    
    # Highest turnover
    if hasattr(cross_border, 'highest_turnover_location') and cross_border.highest_turnover_location:
        return cross_border.highest_turnover_location
    
    return "XX"
