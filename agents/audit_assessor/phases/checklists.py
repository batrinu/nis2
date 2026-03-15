"""
Article 21 requirement checklists for audit assessment.
"""
# Using built-in dict and list types for Python 3.9+


class Article21Checklist:
    """Checklist for Article 21 cybersecurity risk management measures."""
    
    CHECKLIST = {
        "21(2)(a)": {
            "title": "Risk analysis and security policies",
            "domain": "governance",
            "weight": 0.08,
            "items": [
                {
                    "id": "21.2.a.1",
                    "description": "Comprehensive cybersecurity risk assessment conducted (last 12 months)",
                    "evidence_required": ["Risk assessment report", "Methodology document"],
                    "scoring": {"present": 10, "partial": 5, "missing": 0}
                },
                {
                    "id": "21.2.a.2",
                    "description": "Information security policy framework approved and current",
                    "evidence_required": ["Security policy document", "Approval record", "Review date"],
                    "scoring": {"present": 10, "partial": 5, "missing": 0}
                },
                {
                    "id": "21.2.a.3",
                    "description": "All-hazards approach documented",
                    "evidence_required": ["Risk methodology covering all hazard types"],
                    "scoring": {"present": 5, "partial": 2, "missing": 0}
                }
            ]
        },
        "21(2)(b)": {
            "title": "Incident handling",
            "domain": "incident_response",
            "weight": 0.10,
            "items": [
                {
                    "id": "21.2.b.1",
                    "description": "Incident response plan documented and approved",
                    "evidence_required": ["Incident response plan", "Approval record"],
                    "scoring": {"present": 10, "partial": 5, "missing": 0}
                },
                {
                    "id": "21.2.b.2",
                    "description": "Incident detection capabilities implemented",
                    "evidence_required": ["SIEM configuration", "Alert rules", "Monitoring coverage"],
                    "scoring": {"present": 10, "partial": 5, "missing": 0}
                },
                {
                    "id": "21.2.b.3",
                    "description": "Incident response team defined and trained",
                    "evidence_required": ["Team roster", "Training records", "Contact procedures"],
                    "scoring": {"present": 10, "partial": 5, "missing": 0}
                },
                {
                    "id": "21.2.b.4",
                    "description": "NIS2 reporting procedures integrated",
                    "evidence_required": ["Reporting procedures", "CSIRT contacts", "Timeline definitions"],
                    "scoring": {"present": 10, "partial": 5, "missing": 0}
                }
            ]
        },
        "21(2)(c)": {
            "title": "Business continuity and crisis management",
            "domain": "technical_controls",
            "weight": 0.05,
            "items": [
                {
                    "id": "21.2.c.1",
                    "description": "Business continuity plan documented",
                    "evidence_required": ["BCP document", "BIA (Business Impact Analysis)"],
                    "scoring": {"present": 10, "partial": 5, "missing": 0}
                },
                {
                    "id": "21.2.c.2",
                    "description": "RTO/RPO defined for critical systems",
                    "evidence_required": ["RTO/RPO definitions", "System criticality classification"],
                    "scoring": {"present": 5, "partial": 2, "missing": 0}
                },
                {
                    "id": "21.2.c.3",
                    "description": "Crisis management procedures established",
                    "evidence_required": ["Crisis management plan", "Escalation procedures"],
                    "scoring": {"present": 5, "partial": 2, "missing": 0}
                }
            ]
        },
        "21(2)(d)": {
            "title": "Supply chain security",
            "domain": "supply_chain",
            "weight": 0.08,
            "items": [
                {
                    "id": "21.2.d.1",
                    "description": "Supply chain risk assessment conducted",
                    "evidence_required": ["Supply chain risk register", "Assessment methodology"],
                    "scoring": {"present": 10, "partial": 5, "missing": 0}
                },
                {
                    "id": "21.2.d.2",
                    "description": "Security requirements in supplier contracts",
                    "evidence_required": ["Contract templates", "Security clauses", "Audit rights"],
                    "scoring": {"present": 10, "partial": 5, "missing": 0}
                },
                {
                    "id": "21.2.d.3",
                    "description": "Critical supplier inventory maintained",
                    "evidence_required": ["Supplier inventory", "Criticality ratings"],
                    "scoring": {"present": 5, "partial": 2, "missing": 0}
                }
            ]
        },
        "21(2)(e)": {
            "title": "Security in acquisition and development",
            "domain": "technical_controls",
            "weight": 0.04,
            "items": [
                {
                    "id": "21.2.e.1",
                    "description": "Secure development lifecycle documented",
                    "evidence_required": ["SDLC policy", "Security checkpoints"],
                    "scoring": {"present": 10, "partial": 5, "missing": 0}
                },
                {
                    "id": "21.2.e.2",
                    "description": "Security requirements in procurement",
                    "evidence_required": ["Procurement policy", "Security requirements template"],
                    "scoring": {"present": 5, "partial": 2, "missing": 0}
                }
            ]
        },
        "21(2)(f)": {
            "title": "Vulnerability handling and disclosure",
            "domain": "technical_controls",
            "weight": 0.06,
            "items": [
                {
                    "id": "21.2.f.1",
                    "description": "Vulnerability management program active",
                    "evidence_required": ["Vulnerability policy", "Scan results", "Patch metrics"],
                    "scoring": {"present": 10, "partial": 5, "missing": 0}
                },
                {
                    "id": "21.2.f.2",
                    "description": "Coordinated vulnerability disclosure process",
                    "evidence_required": ["Disclosure policy", "Security.txt"],
                    "scoring": {"present": 5, "partial": 2, "missing": 0}
                }
            ]
        },
        "21(2)(g)": {
            "title": "Effectiveness assessment",
            "domain": "governance",
            "weight": 0.04,
            "items": [
                {
                    "id": "21.2.g.1",
                    "description": "Security metrics and KPIs defined",
                    "evidence_required": ["Security metrics dashboard", "KPI definitions"],
                    "scoring": {"present": 10, "partial": 5, "missing": 0}
                },
                {
                    "id": "21.2.g.2",
                    "description": "Regular security assessments conducted",
                    "evidence_required": ["Assessment schedule", "Last assessment report"],
                    "scoring": {"present": 5, "partial": 2, "missing": 0}
                }
            ]
        },
        "21(2)(h)": {
            "title": "Basic cyber hygiene and training",
            "domain": "management_oversight",
            "weight": 0.06,
            "items": [
                {
                    "id": "21.2.h.1",
                    "description": "Security awareness training program",
                    "evidence_required": ["Training program", "Completion records", "Content review"],
                    "scoring": {"present": 10, "partial": 5, "missing": 0}
                },
                {
                    "id": "21.2.h.2",
                    "description": "Role-based security training",
                    "evidence_required": ["Role-based curriculum", "Training matrix"],
                    "scoring": {"present": 5, "partial": 2, "missing": 0}
                },
                {
                    "id": "21.2.h.3",
                    "description": "Basic cyber hygiene practices enforced",
                    "evidence_required": ["Password policy", "Device management", "Updates"],
                    "scoring": {"present": 5, "partial": 2, "missing": 0}
                }
            ]
        },
        "21(2)(i)": {
            "title": "Cryptography and encryption",
            "domain": "technical_controls",
            "weight": 0.08,
            "items": [
                {
                    "id": "21.2.i.1",
                    "description": "Cryptographic policy documented",
                    "evidence_required": ["Cryptography policy", "Standards reference"],
                    "scoring": {"present": 10, "partial": 5, "missing": 0}
                },
                {
                    "id": "21.2.i.2",
                    "description": "Encryption implemented for sensitive data at rest",
                    "evidence_required": ["Encryption configurations", "Data classification"],
                    "scoring": {"present": 10, "partial": 5, "missing": 0}
                },
                {
                    "id": "21.2.i.3",
                    "description": "TLS/encryption for data in transit",
                    "evidence_required": ["TLS configurations", "Protocol versions"],
                    "scoring": {"present": 10, "partial": 5, "missing": 0}
                },
                {
                    "id": "21.2.i.4",
                    "description": "Key management procedures established",
                    "evidence_required": ["Key management policy", "HSM usage", "Rotation procedures"],
                    "scoring": {"present": 5, "partial": 2, "missing": 0}
                }
            ]
        },
        "21(2)(j)": {
            "title": "Human resources security and access control",
            "domain": "governance",
            "weight": 0.06,
            "items": [
                {
                    "id": "21.2.j.1",
                    "description": "Access control policy documented",
                    "evidence_required": ["Access control policy", "Principle of least privilege"],
                    "scoring": {"present": 10, "partial": 5, "missing": 0}
                },
                {
                    "id": "21.2.j.2",
                    "description": "User access reviews conducted",
                    "evidence_required": ["Review schedule", "Last review records"],
                    "scoring": {"present": 10, "partial": 5, "missing": 0}
                },
                {
                    "id": "21.2.j.3",
                    "description": "HR security procedures (onboarding/offboarding)",
                    "evidence_required": ["Onboarding checklist", "Offboarding checklist"],
                    "scoring": {"present": 5, "partial": 2, "missing": 0}
                }
            ]
        },
        "21(2)(k)": {
            "title": "Multi-factor authentication",
            "domain": "technical_controls",
            "weight": 0.06,
            "items": [
                {
                    "id": "21.2.k.1",
                    "description": "MFA enforced for administrative access",
                    "evidence_required": ["MFA configuration", "Coverage report", "Exception list"],
                    "scoring": {"present": 10, "partial": 5, "missing": 0}
                },
                {
                    "id": "21.2.k.2",
                    "description": "MFA enforced for user access to sensitive systems",
                    "evidence_required": ["User MFA rollout status", "Coverage metrics"],
                    "scoring": {"present": 5, "partial": 2, "missing": 0}
                }
            ]
        },
        "21(2)(l)": {
            "title": "Secured communications",
            "domain": "technical_controls",
            "weight": 0.04,
            "items": [
                {
                    "id": "21.2.l.1",
                    "description": "Secure communication channels defined",
                    "evidence_required": ["Communication security policy", "Approved channels"],
                    "scoring": {"present": 10, "partial": 5, "missing": 0}
                }
            ]
        },
        "21(2)(m)": {
            "title": "Emergency plans",
            "domain": "incident_response",
            "weight": 0.04,
            "items": [
                {
                    "id": "21.2.m.1",
                    "description": "Backup and recovery procedures documented",
                    "evidence_required": ["Backup policy", "Recovery procedures", "Test records"],
                    "scoring": {"present": 10, "partial": 5, "missing": 0}
                },
                {
                    "id": "21.2.m.2",
                    "description": "Disaster recovery plan tested",
                    "evidence_required": ["DR plan", "Test results", "Lessons learned"],
                    "scoring": {"present": 5, "partial": 2, "missing": 0}
                }
            ]
        },
        "21(2)(n)": {
            "title": "Environmental control",
            "domain": "technical_controls",
            "weight": 0.03,
            "items": [
                {
                    "id": "21.2.n.1",
                    "description": "Physical security controls implemented",
                    "evidence_required": ["Physical security policy", "Access controls", "Monitoring"],
                    "scoring": {"present": 10, "partial": 5, "missing": 0}
                },
                {
                    "id": "21.2.n.2",
                    "description": "Environmental protections (fire, flood, climate)",
                    "evidence_required": ["Environmental controls", "Monitoring systems"],
                    "scoring": {"present": 5, "partial": 2, "missing": 0}
                }
            ]
        }
    }
    
    @classmethod
    def get_requirements_for_domain(cls, domain: str) -> dict:
        """Get all requirements for a specific domain."""
        return {
            article: data
            for article, data in cls.CHECKLIST.items()
            if data["domain"] == domain
        }
    
    @classmethod
    def get_all_items(cls) -> list[dict]:
        """Get all checklist items flattened."""
        items = []
        for article, data in cls.CHECKLIST.items():
            for item in data["items"]:
                item_copy = item.copy()
                item_copy["article"] = article
                item_copy["domain"] = data["domain"]
                item_copy["domain_weight"] = data["weight"]
                items.append(item_copy)
        return items
    
    @classmethod
    def calculate_domain_score(cls, domain: str, assessments: dict) -> float:
        """
        Calculate score for a domain.
        
        Args:
            domain: Domain name
            assessments: Dict mapping item_id to score (0-10)
        
        Returns:
            Domain score (0-100)
        """
        requirements = cls.get_requirements_for_domain(domain)
        if not requirements:
            return 0.0
        
        total_score = 0
        total_items = 0
        
        for article, data in requirements.items():
            for item in data["items"]:
                score = assessments.get(item["id"], 0)
                total_score += score
                total_items += 1
        
        return (total_score / (total_items * 10)) * 100 if total_items > 0 else 0.0
