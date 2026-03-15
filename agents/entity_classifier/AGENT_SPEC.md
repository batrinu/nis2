# Entity Classifier Agent Specification

## Purpose

Determine Essential Entity (EE) vs Important Entity (IE) status under Directive (EU) 2022/2555 (NIS2).

## Inputs

| Field | Type | Description |
|-------|------|-------------|
| `sector` | `string` | Primary economic sector (must map to Annex I or Annex II) |
| `annual_turnover_eur` | `float` | Annual turnover in EUR |
| `employee_count` | `int` | Full-time equivalent employees |
| `service_scope` | `string[]` | Critical services provided |
| `cross_border_operations` | `boolean` | Operations in multiple Member States |
| `member_states` | `string[]` | List of EU Member States where entity operates |
| `is_public_admin` | `boolean` | Whether entity is a public administration body |
| `is_trust_service_provider` | `boolean` | Whether entity provides trust services under eIDAS |
| `is_tld_registry` | `boolean` | Whether entity manages top-level domains |
| `is_dns_provider` | `boolean` | Whether entity operates DNS services |

## Classification Logic

### Step 1: Sector Mapping

Map input sector to NIS2 Annex classification:

**Annex I - Essential Entities (EE):**
- Energy: Electricity, oil, gas, hydrogen, district heating/cooling
- Transport: Air, rail, water, road
- Banking: Credit institutions
- Financial Markets: Trading venues, central counterparties
- Health: Healthcare providers, medical device manufacturers
- Drinking Water: Suppliers and distributors
- Waste Water: Collection and treatment
- Digital Infrastructure: IXPs, DNS, TLD registries, cloud, data centers, CDNs
- ICT Service Management: Managed services, security services
- Public Administration: Central government bodies (above threshold)
- Space: Operators of ground-based infrastructure

**Annex II - Important Entities (IE):**
- Postal/Courier Services
- Waste Management
- Chemicals: Manufacture/production/distribution
- Food: Production/processing/distribution
- Manufacturing: Medical devices, computers, electronics, machinery, vehicles
- Digital Providers: Online marketplaces, search engines, social networks
- Research: Organizations conducting R&D

### Step 2: Size Threshold Application

**Medium Enterprise Definition (EU Recommendation 2003/361):**
- Employees: 50-249
- AND Annual turnover: €10M-€50M OR Balance sheet: €10M-€43M

**Classification Rules:**

1. **Essential Entities (Article 24):**
   - All entities in Annex I sectors that are medium or large enterprises
   - Public administration bodies (regardless of size)
   - Trust service providers (regardless of size)
   - TLD name registries (regardless of size)
   - DNS service providers (regardless of size)
   - Entities designated by Member State due to specific importance

2. **Important Entities (Article 25):**
   - All entities in Annex II sectors that are medium or large enterprises
   - Entities designated by Member State due to specific importance

### Step 3: Cross-Border Lead Authority Determination

**Lead Supervisory Authority Rules (Article 26):**

1. **Single Member State:** The competent authority of that Member State
2. **Multiple Member States:**
   - The Member State where entity has its main establishment (place of central administration)
   - If no clear main establishment: Where decisions about cybersecurity measures are taken
   - If still undetermined: Where most employees are located
   - If still undetermined: Where highest turnover is generated

**One-Stop-Shop Mechanism:**
- Lead authority coordinates with concerned authorities
- Cross-border cooperation procedures apply

## Output Schema

```python
class EntityClassification(BaseModel):
    entity_id: str
    classification: Literal["Essential Entity", "Important Entity", "Non-Qualifying"]
    legal_basis: str  # Article 24, 25, or 26 citation
    annex: Literal["Annex I", "Annex II", None]
    sector_classification: str  # Specific sector name
    size_qualification: bool
    size_details: dict  # employee_count, turnover, threshold_met
    cross_border: CrossBorderInfo
    lead_authority: str  # Member State code
    confidence_score: float  # 0.0-1.0
    edge_cases: list[str]  # Flags for manual review
    reasoning_chain: list[str]  # Step-by-step logic
```

## Confidence Scoring

### Certainty Calculation

```
confidence = base_score × sector_clarity × data_completeness × edge_case_penalty
```

**Base Score (0.0-1.0):**
- Clear Annex I match: 0.95
- Clear Annex II match: 0.90
- Ambiguous sector: 0.60
- Unknown sector: 0.30

**Sector Clarity Multipliers:**
- Exact match: 1.0
- Related sector requiring interpretation: 0.85
- Multiple possible sectors: 0.70

**Data Completeness Multipliers:**
- All fields provided: 1.0
- Missing optional fields: 0.95
- Missing recommended fields: 0.85
- Missing critical fields: 0.50

**Edge Case Penalties:**
- Borderline size (±10% threshold): -0.15
- Complex corporate structure: -0.10
- Sector overlap: -0.10
- Recent regulatory changes: -0.05

### Edge Case Flagging

Auto-flag for manual review when:
1. Confidence < 0.70
2. Annual turnover within 10% of threshold
3. Employee count within 5 of threshold
4. Sector not clearly in Annex I or II
5. Multiple possible sector classifications
6. Cross-border with conflicting lead authority indicators
7. Special designation status unclear
8. Pending merger/acquisition affecting size qualification

## Implementation Contract

### Class Interface

```python
class EntityClassifier:
    def __init__(self, config_path: str = None):
        """Initialize with sector mappings and thresholds."""
        pass
    
    def classify(self, entity_data: EntityInput) -> EntityClassification:
        """Execute full classification workflow."""
        pass
    
    def _map_sector(self, sector: str) -> tuple[str, str]:
        """Return (annex, specific_sector) or raise UnknownSectorError."""
        pass
    
    def _check_size_threshold(self, entity_data: EntityInput) -> dict:
        """Evaluate medium/large enterprise criteria."""
        pass
    
    def _determine_lead_authority(self, entity_data: EntityInput) -> str:
        """Apply Article 26 rules for cross-border scenarios."""
        pass
    
    def _calculate_confidence(self, result: EntityClassification) -> float:
        """Compute confidence score with edge case detection."""
        pass
    
    def get_legal_citation(self, classification: str, annex: str) -> str:
        """Return specific Article citation for legal basis."""
        pass
```

### Dependencies

- `pydantic` for input/output validation
- `yaml` for sector configuration
- Shared knowledge base for NIS2 annex definitions

## Legal Basis Citations

| Scenario | Citation |
|----------|----------|
| Essential Entity - Annex I sector | "Directive (EU) 2022/2555, Article 24(1) - Essential Entity classification based on Annex I sector qualification" |
| Important Entity - Annex II sector | "Directive (EU) 2022/2555, Article 25(1) - Important Entity classification based on Annex II sector qualification" |
| Public administration EE | "Directive (EU) 2022/2555, Article 24(2) - Public administration body classification regardless of size" |
| DNS/TLD EE | "Directive (EU) 2022/2555, Article 24(2) - Critical digital infrastructure classification" |
| Cross-border lead authority | "Directive (EU) 2022/2555, Article 26 - Lead supervisory authority determination" |
| Non-qualifying (below threshold) | "Directive (EU) 2022/2555, Article 2(1) - Entity below medium enterprise threshold" |

## Error Handling

| Error | Response |
|-------|----------|
| Unknown sector | Classification with confidence=0.0, edge_case=["UNKNOWN_SECTOR"], request manual review |
| Missing critical data | Raise ValidationError with required fields list |
| Conflicting jurisdiction indicators | Return all possibilities with confidence adjustment |
| Ambiguous corporate structure | Flag for legal review with available indicators |

## Testing Requirements

1. **Unit Tests:** All sector mappings, threshold calculations
2. **Integration Tests:** Cross-border scenarios, edge cases
3. **Sample Data:**
   - EE-Energy: Large electricity distributor, 500 employees, €200M turnover
   - IE-Manufacturing: Medical device manufacturer, 150 employees, €30M turnover
   - IE-Digital: Cloud provider, 80 employees, €15M turnover
