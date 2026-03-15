# NIS2 Compliance Assessment System

A comprehensive multi-agent system for assessing compliance with Directive (EU) 2022/2555 (NIS2) on cybersecurity risk management measures.

## Overview

This system provides specialized agents for:

1. **Entity Classifier** - Determines Essential Entity (EE) vs Important Entity (IE) status
2. **Audit Assessor** - Executes 5-phase audit methodology
3. **Enforcement Officer** - Calculates sanctions and generates legal notices
4. **Gap Analyst** - Pre-audit readiness evaluation
5. **Report Generator** - Compiles findings into regulatory documentation
6. **Sector Specialist** - Domain-specific validation for 18 NIS2 sectors

## Quick Start

### Installation

```bash
pip install -r requirements.txt
```

### Command Line Usage

```bash
# List available mock entities
python main.py list-mocks

# Classify an entity
python main.py classify --mock 1

# Run full audit
python main.py audit --mock EE-ENERGY-001 --output audit.json

# Run gap analysis
python main.py gap --mock 2 --mode deep_dive

# Interactive mode
python main.py interactive
```

### Programmatic Usage

```python
from core import Orchestrator
from shared.data.mock_entities import EE_ENERGY

# Create orchestrator
orch = Orchestrator()

# Start session
session_id = orch.start_session(EE_ENERGY)

# Classify entity
result = orch.classify_entity(session_id)
print(result)

# Run audit
audit = orch.run_audit(session_id)
print(audit["audit_result"]["overall_score"])
```

## Architecture

```
nis2-assessment/
├── agents/
│   ├── entity-classifier/     # Entity classification logic
│   ├── audit-assessor/        # 5-phase audit methodology
│   │   └── phases/
│   ├── enforcement-officer/   # Sanction calculations
│   ├── gap-analyst/          # Pre-audit assessment
│   ├── report-generator/     # Documentation generation
│   └── sector-specialist/    # Sector-specific validation
│       └── domains/
├── core/                     # Orchestrator and coordination
├── shared/
│   ├── schemas/             # Pydantic models
│   ├── knowledge-base/      # NIS2 framework reference
│   └── data/               # Mock entities
├── tests/                  # Test suite
└── main.py                # CLI entry point
```

## NIS2 Framework

The system implements:

- **Article 21** - Cybersecurity risk management measures
- **Article 22** - Supply chain security
- **Article 23** - Incident reporting obligations
- **Article 24** - Essential Entities (Annex I)
- **Article 25** - Important Entities (Annex II)
- **Article 26** - Registration and competent authorities
- **Article 34** - Administrative sanctions

## Mock Entities

The system includes 4 sample entities for testing:

1. **EE-ENERGY-001** - Nordic Power Grid Operator AS (Essential Entity)
2. **IE-MANUF-001** - MedTech Devices GmbH (Important Entity)
3. **IE-DIGITAL-001** - CloudScale Hosting Ltd (Essential Entity - Digital Infrastructure)
4. **NON-QUAL-001** - SmallTech Solutions SL (Non-Qualifying)

## Compliance Scoring

| Rating | Score Range |
|--------|-------------|
| Compliant | 90-100% |
| Substantially Compliant | 75-89% |
| Partially Compliant | 50-74% |
| Non-Compliant | <50% |

## Domain Weights

| Domain | Weight |
|--------|--------|
| Governance | 20% |
| Technical Controls | 25% |
| Incident Response | 20% |
| Supply Chain | 15% |
| Documentation | 10% |
| Management Oversight | 10% |

## Sanction Matrix

| Entity Type | Maximum Fine | Percentage Alternative |
|-------------|--------------|------------------------|
| Essential Entity | €10,000,000 | 2% of global turnover |
| Important Entity | €7,000,000 | 1.4% of global turnover |

## Testing

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_classifier.py -v

# Run with coverage
pytest --cov=agents --cov=core
```

## Security

This application implements **32 security hardening passes** with production-grade security measures based on 2026 vulnerability research.

### Cryptographic Security
- **CVE-2026-26007**: `cryptography>=46.0.5` - Fixes elliptic curve subgroup validation vulnerability
- **Terrapin Attack**: `paramiko>=3.4.0` - Patched against SSH prefix truncation attack
- **Timing Attack Prevention**: Constant-time comparison for secrets (Pass 29)

### Network Security
- **CVE-2026-3484 Pattern Prevention**: Character allowlist validation on all nmap targets
- **SSH Connection Flooding (CVE-2026-20080 Pattern)**: Per-IP rate limiting (5 connections/min/IP)
- **MITM Protection**: Strict host key verification with `ssh_strict=True`
- **SSRF Prevention**: URL scheme validation, private IP blocking (Pass 23, CVE-2026-25580, CVE-2026-30953)
- **DNS Rebinding Protection**: Host resolution validation (Pass 22, CVE-2025-66416)

### Data Protection
- Credentials **never** persisted to disk (memory-only during active sessions)
- SQLite database with WAL mode, secure_delete=ON, extension loading disabled
- Database file permissions set to 0o600
- 10MB JSON field size limits
- 900 parameter limit for SQLite queries (CVE-2026-21696 prevention)
- Memory safety limits: 10MB strings, 100MB files, 100 JSON nesting levels (Pass 24)

### Supply Chain Security (Pass 20-21)
- Package name validation against typosquatting patterns
- Wheel entry validation to prevent path traversal (CVE-2026-1703, CVE-2026-24049)
- Dependency version pinning with hash verification

### Code Execution Prevention (Pass 25-26)
- Prototype pollution protection (CVE-2026-27212, CVE-2026-26021)
- Dynamic code execution blocking: eval(), exec(), compile() (CVE-2026-0863, CVE-2026-26030)
- Object path sanitization

### Serialization Security (Pass 7-8, 12, 30)
- PyYAML SafeLoader enforcement (CVE-2026-24009)
- XML XXE prevention with defusedxml (CVE-2026-24400)
- JSON serialization preferred over pickle (CVE-2026-28277)
- Pickle opcode scanning for dangerous patterns (CVE-2025-10155, CVE-2025-10156, CVE-2025-10157)

### ML/AI Pipeline Security (Pass 31)
- Safe model format preference (SafeTensors)
- Model file extension validation
- Model hash verification for integrity

### Import System Security (Pass 32)
- Import audit hook registration (CVE-2026-2297)
- SourcelessFileLoader security checks
- Import path restrictions

### Certificate Security (Pass 28)
- Certificate pinning support (CVE-2026-3336, CVE-2026-22696)
- Chain validation enforcement

### Rate Limiting
| Operation | Limit |
|-----------|-------|
| Network scans | 10 per minute |
| SSH connections (global) | 20 per minute |
| SSH connections (per IP) | 5 per minute |

### Input Validation
- All text fields have maximum length constraints
- Path traversal protection on all file operations (CVE-2026-28518)
- CIDR validation to prevent /0 internet-wide scans
- Regex timeout protection (Pass 11, CVE-2026-26006)

### Security Documentation
See [SECURITY.md](SECURITY.md) for detailed information on all 32 security passes.

## Legal Disclaimer

This system is for regulatory compliance assessment purposes under Directive (EU) 2022/2555. It does not constitute legal advice. Entities should consult qualified legal counsel for interpretation of specific obligations.

## License

MIT License - See LICENSE file for details.

## References

- [Directive (EU) 2022/2555](https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32022L2555)
- [ENISA Guidelines](https://www.enisa.europa.eu/publications)
