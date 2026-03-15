# Sector Specialist Agent Specification

## Purpose

Provide domain-specific validation for the 18 NIS2 sectors, implementing sector-specific requirements, cross-regulatory alignment, and specialized validation rules.

## Sector Architecture

### Pluggable Sector Module System

```
agents/sector-specialist/domains/
├── __init__.py
├── base.py                    # Base sector class
├── energy.py                  # Energy/Oil/Gas
├── transport.py               # Transport (air, rail, water, road)
├── banking.py                 # Banking/Finance
├── financial_markets.py       # Financial market infrastructure
├── health.py                  # Healthcare
├── water.py                   # Drinking and waste water
├── digital_infrastructure.py  # IXPs, DNS, cloud, data centers
├── ict_services.py            # Managed security services
├── public_admin.py            # Public administration
├── space.py                   # Space infrastructure
├── postal.py                  # Postal/courier
├── waste.py                   # Waste management
├── chemicals.py               # Chemical industry
├── food.py                    # Food production
├── manufacturing.py           # Manufacturing
├── digital_providers.py       # Online platforms
└── research.py                # Research organizations
```

---

## Sub-Agent Specifications

### 1. Energy/Oil/Gas Sub-Agent

**Scope:** Electricity, oil, gas, hydrogen, district heating/cooling

**Sector-Specific Requirements:**

| Requirement | Source | Validation Rule |
|-------------|--------|-----------------|
| CEER/ACER guidelines | Sector regulation | Check alignment with network codes |
| Resilience standards | ENISA guidelines | Verify critical infrastructure protection |
| CSIRT participation | NIS2 + sector rules | Confirm sector CSIRT membership |
| Physical security | CER Directive intersection | Validate site security assessments |
| Supply chain (OT) | Sector specific | ICS/SCADA vendor assessments |

**Validation Rules:**

```python
class EnergySectorValidator(BaseSectorValidator):
    SECTOR_CODE = "energy"
    ANNEX = "Annex_I"
    
    SPECIFIC_VALIDATIONS = {
        "ot_security": {
            "description": "Operational Technology security measures",
            "required_for": ["electricity", "gas", "oil"],
            "validation": self._validate_ot_security,
            "citation": "Article 21(2) + CER Directive"
        },
        "resilience_plan": {
            "description": "Energy sector resilience plan",
            "required_for": ["electricity", "gas"],
            "validation": self._validate_resilience_plan,
            "citation": "Sector-specific implementing acts"
        },
        "csirt_coordination": {
            "description": "Sector CSIRT participation",
            "required": True,
            "validation": self._validate_csirt_membership,
            "citation": "Article 24 + sector guidelines"
        }
    }
    
    def _validate_ot_security(self, entity: Entity) -> ValidationResult:
        """Validate OT/ICS security measures."""
        checks = [
            ("it_ot_segmentation", self._check_segmentation),
            ("ics_monitoring", self._check_ics_monitoring),
            ("scada_security", self._check_scada_security),
            ("physical_security", self._check_physical_security)
        ]
        return self._run_checks(checks, entity)
```

### 2. Banking/Finance Sub-Agent

**Scope:** Credit institutions, payment service providers

**Cross-Regulatory Alignment:**

| NIS2 Requirement | DORA Correspondence | Validation Approach |
|------------------|---------------------|---------------------|
| Risk management | ICT Risk Management (DORA Art. 6) | Unified assessment |
| Incident reporting | Major ICT Incident Reporting (DORA Art. 18) | Harmonized timeline |
| Supply chain | ICT Third-Party Risk (DORA Art. 28) | Joint assessment |
| Testing | Digital Operational Resilience Testing (DORA Art. 25) | Leverage TIBER-EU |

**Validation Rules:**

```python
class BankingSectorValidator(BaseSectorValidator):
    SECTOR_CODE = "banking"
    ANNEX = "Annex_I"
    
    # DORA intersection flags
    DORA_OVERLAP = True
    
    SPECIFIC_VALIDATIONS = {
        "dora_alignment": {
            "description": "Alignment with DORA requirements",
            "validation": self._validate_dora_alignment,
            "citation": "NIS2 Article 21 + DORA"
        },
        "payment_security": {
            "description": "Payment service security (PSD2 intersection)",
            "validation": self._validate_payment_security,
            "citation": "PSD2 + NIS2 Article 21"
        },
        "tiber_readiness": {
            "description": "Threat intelligence-based ethical red teaming",
            "recommended": True,
            "validation": self._validate_tiber_readiness,
            "citation": "DORA Art. 25 / TIBER-EU"
        }
    }
    
    def get_applicable_frameworks(self) -> list[str]:
        return ["NIS2", "DORA", "PSD2", "EBA Guidelines"]
```

### 3. Healthcare Sub-Agent

**Scope:** Healthcare providers, medical device manufacturers

**Multi-Regulatory Intersection:**

| Regulation | Intersection with NIS2 | Key Considerations |
|------------|------------------------|-------------------|
| GDPR | Patient data protection | Joint breach notification |
| MDR/IVDR | Medical device cybersecurity | Pre-market requirements |
| Clinical Trials Regulation | Trial data security | Research environment protection |

**Validation Rules:**

```python
class HealthcareSectorValidator(BaseSectorValidator):
    SECTOR_CODE = "health"
    ANNEX = "Annex_I"
    
    SPECIFIC_VALIDATIONS = {
        "patient_safety_impact": {
            "description": "Assessment of patient safety impact from incidents",
            "required": True,
            "validation": self._validate_patient_safety_framework,
            "citation": "MDR Annex I + NIS2 Article 21"
        },
        "medical_device_security": {
            "description": "Cybersecurity of connected medical devices",
            "required": True,
            "validation": self._validate_medical_device_security,
            "citation": "MDR Annex I, 17.2 / MDCG guidance"
        },
        "gdpr_intersection": {
            "description": "Coordinated personal data breach notification",
            "required": True,
            "validation": self._validate_notification_coordination,
            "citation": "GDPR Article 33 + NIS2 Article 23"
        },
        "clinical_environment": {
            "description": "Research/clinical trial data protection",
            "applies_if": lambda e: e.has_clinical_trials,
            "validation": self._validate_clinical_security,
            "citation": "CTR + NIS2"
        }
    }
```

### 4. Transport Sub-Agent

**Scope:** Air, rail, water, road transport

**Cross-Border Coordination:**

| Transport Mode | Cross-Border Element | Special Requirements |
|----------------|---------------------|----------------------|
| Air | Eurocontrol, EASA | Aviation security integration |
| Rail | ERATV, ERA | Interoperability security |
| Water | EMSA, port authorities | Maritime cyber risk management |
| Road | International carriers | Fleet management security |

**Validation Rules:**

```python
class TransportSectorValidator(BaseSectorValidator):
    SECTOR_CODE = "transport"
    ANNEX = "Annex_I"
    
    SPECIFIC_VALIDATIONS = {
        "cross_border_coordination": {
            "description": "Protocols for cross-border incident coordination",
            "required": True,
            "validation": self._validate_coordination_protocols,
            "citation": "NIS2 Article 26 + sector regulations"
        },
        "safety_management_integration": {
            "description": "Integration with safety management systems",
            "required": True,
            "validation": self._validate_sms_integration,
            "citation": "Sector safety regulations + NIS2"
        }
    }
    
    def get_mode_specific_requirements(self, mode: str) -> list[ValidationRule]:
        """Return mode-specific validation rules."""
        modes = {
            "air": [self._easa_coordination, self._ Eurocontrol_procedures],
            "rail": [self._era_alignment, self._tsi_compliance],
            "water": [self._emsa_coordination, self._ism_code_alignment],
            "road": [self._fleet_security, self._cargo_security]
        }
        return modes.get(mode, [])
```

### 5. Digital Infrastructure Sub-Agent

**Scope:** IXPs, DNS, TLD registries, cloud, data centers, CDNs

**Specific Requirements:**

```python
class DigitalInfrastructureValidator(BaseSectorValidator):
    SECTOR_CODE = "digital_infrastructure"
    ANNEX = "Annex_I"
    
    # All entities in this sector are EE regardless of size
    SIZE_EXCEPTION = True
    
    SPECIFIC_VALIDATIONS = {
        "dns_security": {
            "description": "DNSSEC implementation and security",
            "applies_to": ["dns_operator", "tld_registry"],
            "validation": self._validate_dns_security,
            "citation": "ENISA DNS security guidelines"
        },
        "bgp_security": {
            "description": "BGP hijacking protection (RPKI, etc.)",
            "applies_to": ["ixp", "cloud_provider"],
            "validation": self._validate_bgp_security,
            "citation": "MANRS + NIS2"
        },
        "multi_tenant_isolation": {
            "description": "Customer isolation in multi-tenant environments",
            "applies_to": ["cloud_provider", "data_center", "cdn"],
            "validation": self._validate_isolation,
            "citation": "Article 21(2)(d) + ENISA cloud security"
        },
        "service_continuity": {
            "description": "High availability and failover capabilities",
            "required": True,
            "validation": self._validate_continuity,
            "citation": "Article 21(2)(c) + sector SLAs"
        }
    }
```

---

## Knowledge Base Integration

### ENISA Guidelines Integration

```python
class ENISAKnowledgeBase:
    """Integration with ENISA sector-specific guidelines."""
    
    GUIDELINES = {
        "energy": "Guidelines on Sector-specific security requirements for energy",
        "health": "Cybersecurity for healthcare",
        "finance": "Cybersecurity for the financial sector",
        "transport": "Cybersecurity in the transport sector",
        "digital": "Cloud security guidance"
    }
    
    def get_sector_guidelines(self, sector: str) -> dict:
        """Retrieve applicable ENISA guidelines for sector."""
        pass
    
    def map_to_nis2(self, guideline_ref: str) -> str:
        """Map ENISA guideline to NIS2 Article."""
        pass
```

### Implementing Acts Reference

```python
class ImplementingActsDB:
    """Reference to delegated and implementing acts."""
    
    ACTS = {
        "technical_requirements": {
            "reference": "Commission Delegated Regulation...",
            "sectors": ["all"],
            "content": "..."
        },
        "incident_reporting_formats": {
            "reference": "Commission Implementing Regulation...",
            "applies_to": ["incident_reporting"],
            "templates": {...}
        }
    }
```

---

## Implementation Contract

```python
class SectorSpecialist:
    def __init__(self, knowledge_base: SectorKnowledgeBase):
        """Initialize with sector validators."""
        self.validators = self._load_validators()
        pass
    
    def get_validator(self, sector: str) -> BaseSectorValidator:
        """Return appropriate validator for sector."""
        pass
    
    def validate_entity(
        self, 
        entity: Entity,
        sector: str
    ) -> SectorValidationResult:
        """Execute sector-specific validation."""
        validator = self.get_validator(sector)
        return validator.validate(entity)
    
    def get_sector_requirements(self, sector: str) -> list[Requirement]:
        """Return all applicable requirements for sector."""
        pass
    
    def get_cross_regulatory_frameworks(
        self, 
        sector: str
    ) -> list[CrossRegulatoryFramework]:
        """Return intersecting regulations (DORA, GDPR, etc.)."""
        pass
    
    def check_cross_regulatory_alignment(
        self,
        entity: Entity,
        sector: str
    ) -> AlignmentReport:
        """Check alignment across applicable regulations."""
        pass
```

### Base Validator Class

```python
class BaseSectorValidator(ABC):
    """Base class for all sector validators."""
    
    SECTOR_CODE: str
    ANNEX: str  # "Annex_I" or "Annex_II"
    SIZE_EXCEPTION: bool = False  # True for DNS/TLD/etc
    
    SPECIFIC_VALIDATIONS: dict[str, ValidationConfig]
    
    @abstractmethod
    def validate(self, entity: Entity) -> SectorValidationResult:
        """Execute all sector-specific validations."""
        pass
    
    def get_legal_citations(self) -> list[str]:
        """Return applicable legal citations for sector."""
        citations = [f"NIS2 {self.ANNEX}"]
        if self.SIZE_EXCEPTION:
            citations.append("Article 24(2) - Size exception")
        return citations
    
    def _run_checks(
        self, 
        checks: list[tuple[str, Callable]],
        entity: Entity
    ) -> ValidationResult:
        """Execute validation checks and compile results."""
        pass
```

---

## Sector-Specific Legal Citations

| Sector | Primary Citation | Secondary Citations |
|--------|-----------------|---------------------|
| Energy | NIS2 Annex I, Section 1 | CER Directive; ACER/CEER guidelines |
| Banking | NIS2 Annex I, Section 3 | DORA; PSD2; EBA Guidelines |
| Finance Markets | NIS2 Annex I, Section 4 | DORA; MiFID II; EMIR |
| Health | NIS2 Annex I, Section 5 | MDR/IVDR; GDPR; Clinical Trials Regulation |
| Transport | NIS2 Annex I, Section 2 | Sector safety regulations (EASA, ERA, EMSA) |
| Digital Infra | NIS2 Annex I, Section 8 | ENISA technical guidelines; Internet standards |
| Cloud | NIS2 Annex I, Section 8 | ENISA cloud security; CSA STAR |
| Manufacturing | NIS2 Annex II, Section 6 | Sector-specific product safety |
| Digital Providers | NIS2 Annex II, Section 7 | DSA; DMA (where applicable) |

---

## Testing Requirements

1. **Sector Validator Tests:** Each sector's validation logic
2. **Cross-Regulatory Tests:** DORA, GDPR intersections
3. **Edge Case Tests:** Entities spanning multiple sectors
4. **Sample Validations:**
   - Energy: Power grid operator
   - Banking: Investment firm
   - Health: Hospital with medical devices
   - Digital: Cloud service provider
