"""
Knowledge base for NIS2 directive information.
Simplified version for the Field Audit App.
"""
from typing import Optional


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
            "sub_sectors": ["healthcare_provider", "medical_device_manufacturer", "hospital"],
            "annex": "Annex I",
            "article": "24"
        },
        "healthcare": {
            "sub_sectors": ["healthcare_provider", "medical_device_manufacturer", "hospital"],
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
    
    def get_sector_info(self, sector: str) -> Optional[dict]:
        """Get sector information from Annex I or II."""
        sector_lower = sector.lower().replace(" ", "_").replace("-", "_")
        
        # Check Annex I
        if sector_lower in self.ANNEX_I_SECTORS:
            result = self.ANNEX_I_SECTORS[sector_lower].copy()
            result["parent_sector"] = sector_lower
            return result
        
        # Check Annex II
        if sector_lower in self.ANNEX_II_SECTORS:
            result = self.ANNEX_II_SECTORS[sector_lower].copy()
            result["parent_sector"] = sector_lower
            return result
        
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
    
    def get_domain_weight(self, domain: str) -> float:
        """Get scoring weight for a compliance domain."""
        return self.DOMAIN_WEIGHTS.get(domain, 0.0)
    
    def get_fine_thresholds(self, classification: str) -> dict:
        """Get fine thresholds for entity classification."""
        return self.FINE_THRESHOLDS.get(classification, {
            "max_amount": 0,
            "max_percentage": 0.0
        })
