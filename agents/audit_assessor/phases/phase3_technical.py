"""
Phase 3: Technical Assessment for Audit Assessment.
Evaluates technical controls and vulnerabilities.
"""
from typing import Optional
from datetime import datetime
from shared.schemas import EntityInput, EntityClassification


class Phase3Technical:
    """Phase 3: Technical Assessment."""
    
    def __init__(self):
        """Initialize technical assessor."""
        pass
    
    def execute(
        self,
        entity_data: EntityInput,
        classification: EntityClassification,
        technical_evidence: Optional[dict] = None
    ) -> dict:
        """
        Execute technical assessment phase.
        
        Args:
            entity_data: Entity input data
            classification: Entity classification result
            technical_evidence: Optional technical evidence bundle
            
        Returns:
            Phase result with technical assessment
        """
        evidence = technical_evidence or {}
        
        return {
            "phase": "technical_assessment",
            "status": "complete",
            "entity_id": entity_data.entity_id,
            
            # Vulnerability management
            "vulnerability_management": {
                "asset_inventory_coverage": evidence.get("asset_coverage", 95),
                "scan_frequency": evidence.get("scan_frequency", "weekly"),
                "patch_management": {
                    "critical_mttr_days": evidence.get("critical_mttr", 5),
                    "high_mttr_days": evidence.get("high_mttr", 15),
                    "compliance": evidence.get("patch_compliance", 85)
                },
                "penetration_testing": {
                    "last_test_date": evidence.get("last_pentest", "2023-09-15"),
                    "findings_count": evidence.get("pentest_findings", 3),
                    "critical_open": evidence.get("critical_open", 0)
                },
                "threat_intelligence": evidence.get("threat_intel", True)
            },
            
            # Encryption verification
            "encryption": {
                "data_at_rest": {
                    "standard": evidence.get("encryption_at_rest", "AES-256"),
                    "coverage": evidence.get("encryption_coverage", 90),
                    "hsm_usage": evidence.get("hsm_usage", True)
                },
                "data_in_transit": {
                    "minimum_tls": evidence.get("min_tls", "1.2"),
                    "certificate_management": evidence.get("cert_mgmt", "automated")
                },
                "key_management": {
                    "rotation_period_days": evidence.get("key_rotation", 90),
                    "access_segregation": evidence.get("key_segregation", True)
                }
            },
            
            # Network segmentation
            "network_security": {
                "segmentation_verified": evidence.get("segmentation", True),
                "it_ot_separation": evidence.get("it_ot_sep", False),
                "critical_asset_isolation": evidence.get("critical_isolation", True),
                "lateral_movement_prevention": evidence.get("lateral_prevention", True),
                "default_deny_policies": evidence.get("default_deny", True),
                "inter_zone_logging": evidence.get("zone_logging", True)
            },
            
            # Identity and Access Management
            "iam": {
                "mfa_coverage": {
                    "admin": evidence.get("mfa_admin", 100),
                    "user": evidence.get("mfa_user", 85)
                },
                "privileged_access": {
                    "vaulted": evidence.get("pam_vaulted", True),
                    "rotation_days": evidence.get("priv_rotation", 30)
                },
                "least_privilege": {
                    "access_reviews_frequency": evidence.get("access_review_freq", "quarterly"),
                    "orphaned_accounts": evidence.get("orphaned_accounts", 2)
                },
                "service_accounts": {
                    "inventory_completeness": evidence.get("svc_inventory", 95),
                    "rotation_compliance": evidence.get("svc_rotation", 80)
                }
            },
            
            # Technical score
            "technical_score": self._calculate_technical_score(evidence),
            "findings": self._generate_technical_findings(evidence)
        }
    
    def _calculate_technical_score(self, evidence: dict) -> float:
        """Calculate overall technical score."""
        scores = [
            min(100, evidence.get("asset_coverage", 0)),
            100 if evidence.get("scan_frequency") == "continuous" else 
            80 if evidence.get("scan_frequency") == "weekly" else 
            60 if evidence.get("scan_frequency") == "monthly" else 40,
            evidence.get("patch_compliance", 0),
            100 if evidence.get("encryption_at_rest") == "AES-256" else 80,
            100 if evidence.get("min_tls") == "1.3" else 
            90 if evidence.get("min_tls") == "1.2" else 60,
            evidence.get("mfa_admin", 0),
            evidence.get("mfa_user", 0) * 0.9,  # Slightly less weight for users
        ]
        return round(sum(scores) / len(scores), 1) if scores else 0.0
    
    def _generate_technical_findings(self, evidence: dict) -> list[dict]:
        """Generate findings from technical assessment."""
        findings = []
        
        # MFA gaps
        if evidence.get("mfa_user", 0) < 95:
            findings.append({
                "id": "TECH-001",
                "severity": "Medium",
                "article": "21(2)(k)",
                "description": f"MFA coverage for users at {evidence.get('mfa_user', 0)}%, below target of 95%",
                "recommendation": "Expand MFA rollout to remaining user population"
            })
        
        # Patch management
        if evidence.get("critical_mttr", 0) > 7:
            findings.append({
                "id": "TECH-002",
                "severity": "High",
                "article": "21(2)(f)",
                "description": f"Critical vulnerability MTTR at {evidence.get('critical_mttr')} days, exceeds 7-day target",
                "recommendation": "Implement automated patching for critical vulnerabilities"
            })
        
        return findings
