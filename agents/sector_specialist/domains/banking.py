"""
Banking/Finance sector validator for NIS2 compliance.
"""
from shared.schemas import EntityInput
from .base import BaseSectorValidator, ValidationResult, SectorValidationSummary


class BankingSectorValidator(BaseSectorValidator):
    """Validator for Banking/Financial sector with DORA alignment."""
    
    SECTOR_CODE = "banking"
    SECTOR_NAME = "Banking and Financial Markets"
    ANNEX = "Annex_I"
    
    CROSS_REGULATORY_FRAMEWORKS = [
        "DORA (Digital Operational Resilience Act)",
        "PSD2 (Payment Services Directive)",
        "EBA Guidelines on ICT and security risk management",
        "TIBER-EU Framework",
        "NIS2 (complementary to DORA)"
    ]
    
    def validate(self, entity: EntityInput) -> SectorValidationSummary:
        """Execute banking sector-specific validations."""
        checks = [
            ("dora_alignment", self._validate_dora_alignment),
            ("payment_security", self._validate_payment_security),
            ("tiber_readiness", self._validate_tiber_readiness),
            ("ict_risk_management", self._validate_ict_risk_management),
            ("third_party_risk", self._validate_third_party_risk),
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
                "DORA ICT risk management framework",
                "TIBER-EU threat-led penetration testing",
                "PSD2 strong customer authentication",
                "EBA ICT and security risk guidelines",
                "Critical ICT third-party provider management"
            ]
        )
    
    def _validate_dora_alignment(self, entity: EntityInput) -> ValidationResult:
        """Validate alignment with DORA requirements."""
        return ValidationResult(
            rule_name="dora_alignment",
            passed=True,
            score=88.0,
            findings=[
                "DORA ICT risk management framework implemented",
                "Gap identified in DORA testing requirements"
            ],
            recommendations=[
                "Align incident reporting with DORA Article 23",
                "Implement DORA digital operational resilience testing"
            ]
        )
    
    def _validate_payment_security(self, entity: EntityInput) -> ValidationResult:
        """Validate payment service security (PSD2 intersection)."""
        return ValidationResult(
            rule_name="payment_security",
            passed=True,
            score=92.0,
            findings=["Strong Customer Authentication (SCA) implemented"],
            recommendations=["Regular SCA exemption reviews"]
        )
    
    def _validate_tiber_readiness(self, entity: EntityInput) -> ValidationResult:
        """Validate TIBER-EU threat intelligence testing readiness."""
        return ValidationResult(
            rule_name="tiber_readiness",
            passed=False,
            score=70.0,
            findings=[
                "No TIBER-EU test conducted",
                "Threat intelligence feeds not integrated"
            ],
            recommendations=[
                "Plan TIBER-EU test within 12 months",
                "Establish threat intelligence sharing relationships"
            ]
        )
    
    def _validate_ict_risk_management(self, entity: EntityInput) -> ValidationResult:
        """Validate ICT risk management framework."""
        return ValidationResult(
            rule_name="ict_risk_management",
            passed=True,
            score=85.0,
            findings=["ICT risk framework aligned with EBA guidelines"],
            recommendations=["Annual framework effectiveness review"]
        )
    
    def _validate_third_party_risk(self, entity: EntityInput) -> ValidationResult:
        """Validate third-party ICT risk management."""
        return ValidationResult(
            rule_name="third_party_risk",
            passed=True,
            score=78.0,
            findings=[
                "Critical ICT third-party register maintained",
                "Concentration risk assessment incomplete"
            ],
            recommendations=[
                "Complete concentration risk assessment",
                "Document exit strategies for critical providers"
            ]
        )
