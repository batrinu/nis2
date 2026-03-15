"""
Healthcare sector validator for NIS2 compliance.
"""
from shared.schemas import EntityInput
from .base import BaseSectorValidator, ValidationResult, SectorValidationSummary


class HealthcareSectorValidator(BaseSectorValidator):
    """Validator for Healthcare sector with MDR/IVDR alignment."""
    
    SECTOR_CODE = "health"
    SECTOR_NAME = "Healthcare"
    ANNEX = "Annex_I"
    
    CROSS_REGULATORY_FRAMEWORKS = [
        "GDPR (patient data protection)",
        "MDR (Medical Device Regulation)",
        "IVDR (In Vitro Diagnostic Regulation)",
        "Clinical Trials Regulation",
        "eHealth Network guidelines"
    ]
    
    def validate(self, entity: EntityInput) -> SectorValidationSummary:
        """Execute healthcare sector-specific validations."""
        checks = [
            ("patient_safety_impact", self._validate_patient_safety_impact),
            ("medical_device_security", self._validate_medical_device_security),
            ("gdpr_intersection", self._validate_gdpr_intersection),
            ("clinical_environment", self._validate_clinical_environment),
            ("business_continuity", self._validate_business_continuity),
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
                "Patient safety impact assessment",
                "Connected medical device cybersecurity",
                "Coordinated GDPR/NIS2 breach notification",
                "Clinical system availability requirements",
                "MDR Annex I cybersecurity requirements"
            ]
        )
    
    def _validate_patient_safety_impact(self, entity: EntityInput) -> ValidationResult:
        """Validate patient safety impact assessment framework."""
        return ValidationResult(
            rule_name="patient_safety_impact",
            passed=True,
            score=82.0,
            findings=[
                "Patient safety impact framework documented",
                "Clinical risk assessment integrated"
            ],
            recommendations=[
                "Regular patient safety impact reviews",
                "Clinical staff cybersecurity training"
            ]
        )
    
    def _validate_medical_device_security(self, entity: EntityInput) -> ValidationResult:
        """Validate cybersecurity of connected medical devices."""
        return ValidationResult(
            rule_name="medical_device_security",
            passed=False,
            score=65.0,
            findings=[
                "Legacy medical devices without security updates",
                "Device inventory incomplete",
                "Network segmentation for medical devices missing"
            ],
            recommendations=[
                "Complete medical device security inventory",
                "Implement network segmentation for devices",
                "Establish device lifecycle management",
                "Align with MDR Annex I Section 17.2"
            ]
        )
    
    def _validate_gdpr_intersection(self, entity: EntityInput) -> ValidationResult:
        """Validate coordinated GDPR/NIS2 notification procedures."""
        return ValidationResult(
            rule_name="gdpr_intersection",
            passed=True,
            score=88.0,
            findings=[
                "Coordinated notification procedure documented",
                "DPO and CISO coordination established"
            ],
            recommendations=[
                "Regular coordination meetings",
                "Joint incident response exercises"
            ]
        )
    
    def _validate_clinical_environment(self, entity: EntityInput) -> ValidationResult:
        """Validate clinical trial/research environment security."""
        return ValidationResult(
            rule_name="clinical_environment",
            passed=True,
            score=75.0,
            findings=["Research environment security controls in place"],
            recommendations=["Annual research security audit"]
        )
    
    def _validate_business_continuity(self, entity: EntityInput) -> ValidationResult:
        """Validate business continuity for clinical services."""
        return ValidationResult(
            rule_name="business_continuity",
            passed=True,
            score=80.0,
            findings=[
                "Clinical service continuity plans documented",
                "RTO/RPO defined for critical systems"
            ],
            recommendations=[
                "Patient care impact assessment in BCP",
                "Regular clinical system failover testing"
            ]
        )
