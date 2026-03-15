"""
Shared knowledge base for NIS2 compliance assessment.
"""
from pathlib import Path
from typing import Optional
import yaml


class NIS2KnowledgeBase:
    """Knowledge base for NIS2 directive information."""
    
    # Annex I sectors - Essential Entities
    ANNEX_I_SECTORS = {
        "energy": {
            "sub_sectors": [
                "electricity", "oil", "gas", "hydrogen", 
                "district_heating", "district_cooling"
            ],
            "annex": "Annex I",
            "article": "24"
        },
        "transport": {
            "sub_sectors": ["air", "rail", "water", "road"],
            "annex": "Annex I",
            "article": "24"
        },
        "banking": {
            "sub_sectors": ["credit_institution"],
            "annex": "Annex I",
            "article": "24"
        },
        "financial_markets": {
            "sub_sectors": ["trading_venue", "central_counterparty"],
            "annex": "Annex I",
            "article": "24"
        },
        "health": {
            "sub_sectors": ["healthcare_provider", "medical_device_manufacturer"],
            "annex": "Annex I",
            "article": "24"
        },
        "drinking_water": {
            "sub_sectors": ["supplier", "distributor"],
            "annex": "Annex I",
            "article": "24"
        },
        "waste_water": {
            "sub_sectors": ["collector", "treatment_operator"],
            "annex": "Annex I",
            "article": "24"
        },
        "digital_infrastructure": {
            "sub_sectors": [
                "ixp", "dns_provider", "tld_registry", 
                "cloud_provider", "data_center", "cdn"
            ],
            "annex": "Annex I",
            "article": "24",
            "size_exception": True  # All entities regardless of size
        },
        "ict_services": {
            "sub_sectors": ["managed_service_provider", "managed_security_service_provider"],
            "annex": "Annex I",
            "article": "24"
        },
        "public_administration": {
            "sub_sectors": ["central_government"],
            "annex": "Annex I",
            "article": "24",
            "size_exception": True  # Regardless of size
        },
        "space": {
            "sub_sectors": ["ground_based_infrastructure"],
            "annex": "Annex I",
            "article": "24"
        }
    }
    
    # Annex II sectors - Important Entities
    ANNEX_II_SECTORS = {
        "postal": {
            "sub_sectors": ["postal_service", "courier_service"],
            "annex": "Annex II",
            "article": "25"
        },
        "waste_management": {
            "sub_sectors": ["waste_operator"],
            "annex": "Annex II",
            "article": "25"
        },
        "chemicals": {
            "sub_sectors": ["manufacture", "production", "distribution"],
            "annex": "Annex II",
            "article": "25"
        },
        "food": {
            "sub_sectors": ["production", "processing", "distribution"],
            "annex": "Annex II",
            "article": "25"
        },
        "manufacturing": {
            "sub_sectors": [
                "medical_device", "computer_electronic", "electrical_equipment",
                "machinery", "motor_vehicles", "transport_equipment"
            ],
            "annex": "Annex II",
            "article": "25"
        },
        "digital_providers": {
            "sub_sectors": [
                "online_marketplace", "search_engine", "social_network"
            ],
            "annex": "Annex II",
            "article": "25"
        },
        "research": {
            "sub_sectors": ["research_organization"],
            "annex": "Annex II",
            "article": "25"
        }
    }
    
    # Article 21 requirements
    ARTICLE_21_REQUIREMENTS = {
        "21(2)(a)": {
            "title": "Risk analysis and security policies",
            "description": "Based on an all-hazards approach, appropriate and proportionate technical and organisational measures to manage the risks posed to the security of network and information systems",
            "domain": "governance"
        },
        "21(2)(b)": {
            "title": "Incident handling",
            "description": "Measures to prevent, detect, respond to and recover from incidents",
            "domain": "incident_response"
        },
        "21(2)(c)": {
            "title": "Business continuity and crisis management",
            "description": "Measures for business continuity, crisis management and disaster recovery",
            "domain": "technical_controls"
        },
        "21(2)(d)": {
            "title": "Supply chain security",
            "description": "Measures concerning the security of supply chains and the security of their use of ICT products and services",
            "domain": "supply_chain"
        },
        "21(2)(e)": {
            "title": "Security in acquisition and development",
            "description": "Measures concerning the security of network and information systems acquisition, development and maintenance",
            "domain": "technical_controls"
        },
        "21(2)(f)": {
            "title": "Vulnerability handling",
            "description": "Measures for effectively handling vulnerabilities and disclosures",
            "domain": "technical_controls"
        },
        "21(2)(g)": {
            "title": "Effectiveness assessment",
            "description": "Measures for the assessment of the effectiveness of cybersecurity risk management",
            "domain": "governance"
        },
        "21(2)(h)": {
            "title": "Basic cyber hygiene and training",
            "description": "Basic cyber hygiene practices and cybersecurity training",
            "domain": "management_oversight"
        },
        "21(2)(i)": {
            "title": "Cryptography and encryption",
            "description": "Policies and procedures regarding the use of cryptography and, where appropriate, encryption",
            "domain": "technical_controls"
        },
        "21(2)(j)": {
            "title": "Human resources security and access control",
            "description": "Policies and procedures regarding human resources security, access control and asset management",
            "domain": "governance"
        },
        "21(2)(k)": {
            "title": "Multi-factor authentication",
            "description": "The use of multi-factor authentication and secured communications",
            "domain": "technical_controls"
        },
        "21(2)(l)": {
            "title": "Secured communications",
            "description": "Secured communications between systems and services",
            "domain": "technical_controls"
        },
        "21(2)(m)": {
            "title": "Emergency plans",
            "description": "Measures for emergency plans, backup management and disaster recovery",
            "domain": "incident_response"
        },
        "21(2)(n)": {
            "title": "Environmental control",
            "description": "Measures regarding the security of the physical environment and installations",
            "domain": "technical_controls"
        }
    }
    
    # Domain weights for scoring
    DOMAIN_WEIGHTS = {
        "governance": 0.20,
        "technical_controls": 0.25,
        "incident_response": 0.20,
        "supply_chain": 0.15,
        "documentation": 0.10,
        "management_oversight": 0.10
    }
    
    # Fine thresholds
    FINE_THRESHOLDS = {
        "Essential Entity": {
            "max_amount": 10_000_000,
            "max_percentage": 0.02  # 2% of turnover
        },
        "Important Entity": {
            "max_amount": 7_000_000,
            "max_percentage": 0.014  # 1.4% of turnover
        }
    }
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize knowledge base with optional custom config."""
        self.config_path = config_path
        self._custom_config = {}
        if config_path and Path(config_path).exists():
            with open(config_path) as f:
                self._custom_config = yaml.safe_load(f)
    
    def get_sector_info(self, sector: str) -> Optional[dict]:
        """Get sector information from Annex I or II."""
        sector_lower = sector.lower().replace(" ", "_")
        
        # Check Annex I
        if sector_lower in self.ANNEX_I_SECTORS:
            return self.ANNEX_I_SECTORS[sector_lower]
        
        # Check Annex II
        if sector_lower in self.ANNEX_II_SECTORS:
            return self.ANNEX_II_SECTORS[sector_lower]
        
        # Check sub-sectors
        for annex, sectors in [("Annex I", self.ANNEX_I_SECTORS), 
                               ("Annex II", self.ANNEX_II_SECTORS)]:
            for main_sector, info in sectors.items():
                if sector_lower in [s.lower() for s in info["sub_sectors"]]:
                    result = info.copy()
                    result["matched_sub_sector"] = sector_lower
                    result["parent_sector"] = main_sector
                    return result
        
        return None
    
    def is_essential_entity_sector(self, sector: str) -> bool:
        """Check if sector is in Annex I (Essential Entities)."""
        info = self.get_sector_info(sector)
        return info is not None and info.get("annex") == "Annex I"
    
    def is_important_entity_sector(self, sector: str) -> bool:
        """Check if sector is in Annex II (Important Entities)."""
        info = self.get_sector_info(sector)
        return info is not None and info.get("annex") == "Annex II"
    
    def get_article_21_requirements(self, domain: Optional[str] = None) -> dict:
        """Get Article 21 requirements, optionally filtered by domain."""
        if domain:
            return {
                k: v for k, v in self.ARTICLE_21_REQUIREMENTS.items()
                if v["domain"] == domain
            }
        return self.ARTICLE_21_REQUIREMENTS
    
    def get_domain_weight(self, domain: str) -> float:
        """Get scoring weight for a compliance domain."""
        return self.DOMAIN_WEIGHTS.get(domain, 0.0)
    
    def get_fine_thresholds(self, classification: str) -> dict:
        """Get fine thresholds for entity classification."""
        return self.FINE_THRESHOLDS.get(classification, {
            "max_amount": 0,
            "max_percentage": 0.0
        })
    
    def get_legal_citation(self, article: str, member_state: Optional[str] = None) -> str:
        """Get full legal citation for an article."""
        # Romanian citations
        if member_state == "RO":
            if article == "21":
                return "OUG 155/2024, Art 21 - Măsuri de management al riscului de securitate cibernetică"
            elif article == "23":
                return "OUG 155/2024, Art 23 - Obligații de raportare"
            elif article == "art_9":
                return "OUG 155/2024, Art 9 - Depășirea pragurilor de dimensiune"
            elif article in ["24", "25"]:
                entity_type = "esențiale" if article == "24" else "importante"
                return f"OUG 155/2024, Art {article} - Entități {entity_type}"
            elif article == "64":
                return "OUG 155/2024, Art 64 - Sancțiuni contravenționale"
        
        # EU citations
        base = "Directive (EU) 2022/2555"
        if article.startswith("21"):
            return f"{base}, Article {article} - Cybersecurity Risk Management Measures"
        elif article in ["23"]:
            return f"{base}, Article {article} - Reporting Obligations"
        elif article in ["24"]:
            return f"{base}, Article {article} - Essential Entities"
        elif article in ["25"]:
            return f"{base}, Article {article} - Important Entities"
        elif article in ["26"]:
            return f"{base}, Article {article} - Registration and Competent Authorities"
        elif article in ["34"]:
            return f"{base}, Article {article} - Administrative Sanctions"
        return f"{base}, Article {article}"
    
    # National transposition variations
    NATIONAL_VARIATIONS = {
        "RO": {  # Romania
            "name": "Romania",
            "legal_framework": "GEO 155/2024 + Law 124/2025",
            "competent_authority": "DNSC (National Cyber Security Directorate)",
            "special_rules": {
                "designation_override": True,  # DNSC can designate regardless of size
                "healthcare_always_essential": False,  # But can be designated based on criticality
                "public_admin_size_exception": True,
            },
            "notes": [
                "DNSC may designate entities as essential/important regardless of size thresholds",
                "If disruption would have significant societal/economic consequences",
                "Hospitals may be designated as essential based on critical role",
                "Registration via NIS2@RO platform within 30 days of Order 1/2025",
            ],
            "fines_local": {
                "Essential Entity": {"amount_ron": 500_000, "approx_eur": 100_000},
                "Important Entity": {"amount_ron": 300_000, "approx_eur": 60_000},
            }
        },
        "DE": {  # Germany
            "name": "Germany",
            "legal_framework": "NIS2UmsuCG",
            "competent_authority": "BSI (Federal Office for Information Security)",
        },
        "FR": {  # France
            "name": "France", 
            "legal_framework": "NIS2 Transposition Law",
            "competent_authority": "ANSSI",
        }
    }
    
    def get_national_rules(self, member_state: str) -> Optional[dict]:
        """Get national transposition rules for a member state.
        
        Args:
            member_state: Two-letter country code (e.g., 'RO', 'DE', 'FR')
            
        Returns:
            Dict with national rules or None if not found
        """
        return self.NATIONAL_VARIATIONS.get(member_state.upper())
    
    def can_designate_regardless_of_size(self, member_state: str, sector: str) -> bool:
        """Check if member state can designate entities regardless of size.
        
        Args:
            member_state: Two-letter country code
            sector: Entity sector
            
        Returns:
            True if designation authority exists for this sector
        """
        rules = self.NATIONAL_VARIATIONS.get(member_state.upper())
        if not rules:
            return False
        
        special = rules.get("special_rules", {})
        
        # Romania: DNSC can designate any entity regardless of size
        if special.get("designation_override", False):
            return True
            
        return False
    
    def get_competent_authority(self, member_state: str) -> str:
        """Get competent authority for a member state.
        
        Args:
            member_state: Two-letter country code
            
        Returns:
            Name of competent authority
        """
        rules = self.NATIONAL_VARIATIONS.get(member_state.upper())
        if rules:
            return rules.get("competent_authority", "Unknown")
        return "National Competent Authority"
