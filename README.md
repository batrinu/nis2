# NIS2 Compliance Assessment Tool

A streamlined tool for assessing NIS2 (Directive EU 2022/2555) compliance.

## Features

- **Entity Classification**: Determine Essential vs Important Entity status
- **Compliance Audit**: Assess against Article 21 requirements
- **Gap Analysis**: Identify compliance gaps and remediation priorities
- **Report Generation**: Export to Markdown or JSON

## Quick Start

```bash
# Classify an entity
python -m nis2 classify --name "Example Corp" --sector energy --employees 150 --turnover 25000000

# Run full audit
python -m nis2 audit --entity-file entity.json

# Gap analysis
python -m nis2 gap --entity-file entity.json --mode quick_scan
```

## Installation

```bash
cd nis2-audit-app
pip install -r requirements.txt
```

## Usage

### Entity Classification

```bash
python -m nis2 classify \
  --name "Company Name" \
  --sector energy \
  --employees 150 \
  --turnover 25000000 \
  --country RO
```

### Running an Audit

Create an entity file `entity.json`:

```json
{
  "legal_name": "Example Corp",
  "sector": "energy",
  "employee_count": 150,
  "annual_turnover_eur": 25000000,
  "cross_border_operations": {
    "operates_cross_border": false,
    "main_establishment": "RO"
  }
}
```

Run the audit:

```bash
python -m nis2 audit --entity-file entity.json --output report.md
```

## Architecture

The tool has been simplified to a functional core:

```
nis2-audit-app/src/nis2/
├── __init__.py          # Package exports
├── __main__.py          # CLI entry point
├── models.py            # Pydantic models
├── knowledge_base.py    # NIS2 regulatory data
├── classifier.py        # Entity classification functions
├── audit.py             # Audit and gap analysis functions
├── report.py            # Report generation
└── cli.py               # Command-line interface
```

**Total: ~3,000 lines** (down from 100,000+)

## NIS2 Overview

The NIS2 Directive categorizes entities as:

- **Essential Entities (Annex I)**: Energy, transport, banking, health, etc.
- **Important Entities (Annex II)**: Postal, waste, chemicals, manufacturing, etc.

Size thresholds (EU Recommendation 2003/361):
- **Medium**: 50-249 employees AND (€10M+ turnover OR €10M+ balance)
- **Large**: 250+ employees AND (€50M+ turnover OR €43M+ balance)

## License

MIT License
