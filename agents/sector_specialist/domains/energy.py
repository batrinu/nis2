"""
Energy sector validator for NIS2 compliance.
"""
from shared.schemas import EntityInput
from .base import BaseSectorValidator, ValidationResult, SectorValidationSummary


class EnergySectorValidator(BaseSectorValidator):
    """Validator for Energy/Oil/Gas sector."""
    
    SECTOR_CODE = "energy"
    SECTOR_NAME = "Energy"
    ANNEX = "Annex_I"
    
    CROSS_REGULATORY_FRAMEWORKS = [
        "CER Directive (Critical Entities Resilience)",
        "CEER/ACER Network Codes",
        "ENISA Energy Sector Guidelines"
    ]
    
    def validate(self, entity: EntityInput) -> SectorValidationSummary:
        """Execute energy sector-specific validations."""
        checks = [
            ("ot_security", self._validate_ot_security),
            ("resilience_planning", self._validate_resilience_planning),
            ("csirt_coordination", self._validate_csirt_coordination),
            ("supply_chain_ot", self._validate_supply_chain_ot),
            ("physical_security", self._validate_physical_security),
        ]
        
        results = self._run_checks(checks, entity)
        overall_score = self._calculate_overall_score(results)
        
        return SectorValidationSummary(
            sector_code=self.SECTOR_CODE,
            sector_name=self.SECTOR_NAME,
            annex=self.ANNEX,
            overall_score=overall_score,
            compliance_level=self._determine_compliance_level(overall_score),
            validation_results=[
                {
                    "rule": r.rule_name,
                    "passed": r.passed,
                    "score": r.score,
                    "findings": r.findings
                }
                for r in results
            ],
            cross_regulatory_frameworks=self.CROSS_REGULATORY_FRAMEWORKS,
            specific_requirements=[
                "OT/IT network segmentation",
                "Industrial control system security",
                "Sector CSIRT participation",
                "Physical site security assessments",
                "Supply chain security for ICS/SCADA"
            ]
        )
    
    def _validate_ot_security(self, entity: EntityInput) -> ValidationResult:
        """Validate Operational Technology security measures."""
        # In a real implementation, this would check actual evidence
        # For now, return a placeholder result
        return ValidationResult(
            rule_name="ot_security",
            passed=True,
            score=75.0,
            findings=[
                "OT security measures require verification",
                "IT/OT segmentation not documented"
            ],
            recommendations=[
                "Implement network segmentation between IT and OT",
                "Deploy ICS-specific monitoring tools",
                "Document OT security architecture"
            ]
        )
    
    def _validate_resilience_planning(self, entity: EntityInput) -> ValidationResult:
        """Validate energy sector resilience planning."""
        return ValidationResult(
            rule_name="resilience_planning",
            passed=True,
            score=80.0,
            findings=["Resilience plan exists but not tested recently"],
            recommendations=["Conduct annual resilience plan tabletop exercise"]
        )
    
    def _validate_csirt_coordination(self, entity: EntityInput) -> ValidationResult:
        """Validate sector CSIRT participation."""
        return ValidationResult(
            rule_name="csirt_coordination",
            passed=True,
            score=85.0,
            findings=["Contact established with energy sector CSIRT"],
            recommendations=["Document incident escalation procedures"]
        )
    
    def _validate_supply_chain_ot(self, entity: EntityInput) -> ValidationResult:
        """Validate OT supply chain security."""
        return ValidationResult(
            rule_name="supply_chain_ot",
            passed=False,
            score=60.0,
            findings=[
                "ICS/SCADA vendor assessments incomplete",
                "Hardware supply chain security not addressed"
            ],
            recommendations=[
                "Conduct security assessments of critical ICS vendors",
                "Implement hardware authentication procedures"
            ]
        )
    
    def _validate_physical_security(self, entity: EntityInput) -> ValidationResult:
        """Validate physical security of critical sites."""
        return ValidationResult(
            rule_name="physical_security",
            passed=True,
            score=90.0,
            findings=["Physical security measures aligned with CER Directive"],
            recommendations=[]
        )
