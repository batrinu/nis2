"""
Sample mock entities for testing NIS2 compliance assessment.
"""
from shared.schemas import EntityInput, CrossBorderInfo, Address


# Mock Entity 1: Essential Entity - Energy Sector
EE_ENERGY = EntityInput(
    entity_id="EE-ENERGY-001",
    legal_name="Nordic Power Grid Operator AS",
    sector="energy",
    annual_turnover_eur=250_000_000,
    employee_count=500,
    balance_sheet_total=400_000_000,
    service_scope=["electricity_transmission", "grid_management"],
    cross_border_operations=CrossBorderInfo(
        operates_cross_border=True,
        member_states=["NO", "SE", "DK"],
        main_establishment="NO",
        decision_location="NO",
        majority_employees_location="NO",
        highest_turnover_location="NO"
    ),
    is_public_admin=False,
    is_trust_service_provider=False,
    is_tld_registry=False,
    is_dns_provider=False
)


# Mock Entity 2: Important Entity - Manufacturing Sector
IE_MANUFACTURING = EntityInput(
    entity_id="IE-MANUF-001",
    legal_name="MedTech Devices GmbH",
    sector="manufacturing",
    annual_turnover_eur=30_000_000,
    employee_count=150,
    balance_sheet_total=25_000_000,
    service_scope=["medical_device_manufacturing", "healthcare_equipment"],
    cross_border_operations=CrossBorderInfo(
        operates_cross_border=True,
        member_states=["DE", "AT", "CH"],
        main_establishment="DE",
        decision_location="DE",
        majority_employees_location="DE",
        highest_turnover_location="DE"
    ),
    is_public_admin=False,
    is_trust_service_provider=False,
    is_tld_registry=False,
    is_dns_provider=False
)


# Mock Entity 3: Important Entity - Digital Provider
IE_DIGITAL = EntityInput(
    entity_id="IE-DIGITAL-001",
    legal_name="CloudScale Hosting Ltd",
    sector="digital_infrastructure",
    annual_turnover_eur=15_000_000,
    employee_count=80,
    balance_sheet_total=12_000_000,
    service_scope=["cloud_computing", "data_center", "managed_services"],
    cross_border_operations=CrossBorderInfo(
        operates_cross_border=True,
        member_states=["IE", "NL", "DE", "FR"],
        main_establishment="IE",
        decision_location="IE",
        majority_employees_location="IE",
        highest_turnover_location="DE"
    ),
    is_public_admin=False,
    is_trust_service_provider=False,
    is_tld_registry=False,
    is_dns_provider=False
)


# Mock Entity 4: Non-Qualifying (Small Enterprise)
NON_QUALIFYING = EntityInput(
    entity_id="NON-QUAL-001",
    legal_name="SmallTech Solutions SL",
    sector="digital_providers",
    annual_turnover_eur=2_000_000,
    employee_count=15,
    balance_sheet_total=1_500_000,
    service_scope=["software_development", "it_consulting"],
    cross_border_operations=CrossBorderInfo(
        operates_cross_border=False,
        member_states=["ES"],
        main_establishment="ES"
    ),
    is_public_admin=False,
    is_trust_service_provider=False,
    is_tld_registry=False,
    is_dns_provider=False
)


# Mock Entity 5: Romanian Essential Entity - Healthcare
RO_HOSPITAL = EntityInput(
    entity_id="RO-HEALTH-001",
    legal_name="Spitalul Municipal Mangalia",
    sector="health",
    annual_turnover_eur=14_500_000,
    employee_count=433,
    balance_sheet_total=18_000_000,
    service_scope=["general_healthcare", "emergency_services"],
    cross_border_operations=CrossBorderInfo(
        operates_cross_border=False,
        member_states=["RO"],
        main_establishment="RO"
    ),
    is_public_admin=False,
    is_trust_service_provider=False,
    is_tld_registry=False,
    is_dns_provider=False
)


# All mock entities
ALL_MOCK_ENTITIES = [
    EE_ENERGY,
    IE_MANUFACTURING,
    IE_DIGITAL,
    NON_QUALIFYING,
    RO_HOSPITAL
]


def get_mock_entity(entity_id: str) -> EntityInput:
    """Get a mock entity by ID."""
    for entity in ALL_MOCK_ENTITIES:
        if entity.entity_id == entity_id:
            return entity
    raise ValueError(f"Mock entity not found: {entity_id}")


def list_mock_entities() -> list[dict]:
    """List all mock entities with summaries."""
    return [
        {
            "id": e.entity_id,
            "name": e.legal_name,
            "sector": e.sector,
            "employees": e.employee_count,
            "turnover": e.annual_turnover_eur
        }
        for e in ALL_MOCK_ENTITIES
    ]
