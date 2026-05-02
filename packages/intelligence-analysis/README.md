# Intelligence Risk Analysis Module

Threat scenario analysis, mobilization indicators, and security posture monitoring tools for the Integrated Security Risk Management System (ISRMS).

## Overview

The Intelligence Risk Analysis module provides tools for:

1. **Scenario Analysis Dashboard** - Bayesian threat modeling and scenario analysis
2. **CTIM (Cyber Threat Intelligence & Mobilization)** - Mobilization indicator tracking and threat intelligence
3. **Posture Ops** - Security posture monitoring through log analysis
4. **Red Team Simulation** - Adversarial simulation and testing frameworks

## Modules

### Scenario Analysis Dashboard (Bayesian)

Bayesian network-based threat scenario modeling:
- Probabilistic threat assessment
- Multi-factor risk analysis
- Scenario comparison and ranking
- Decision support for security posture changes

### CTIM (Mobilization Indicators)

Threat mobilization and intelligence monitoring:
- Early warning indicator tracking
- Threat actor activity monitoring
- Intelligence fusion and correlation
- Alert generation and escalation

### Posture Ops (Log Analysis)

Security posture monitoring and log analysis:
- Security event correlation
- Anomaly detection
- Trend analysis
- Security metrics and KPIs

### Red Team Simulation

Adversarial simulation and security testing:
- Attack scenario modeling
- Defense effectiveness testing
- Vulnerability assessment
- Penetration testing support

## Installation

From the repository root:

```bash
pip install -e packages/intelligence-analysis/python
```

## Usage

```python
# Scenario Analysis
from isrms_intel.scenario_analysis import BayesianScenarioAnalyzer

# CTIM
from isrms_intel.ctim import MobilizationIndicatorTracker

# Posture Ops
from isrms_intel.posture_ops import LogAnalyzer

# Red Team Simulation
from isrms_intel.red_team import AdversarySimulator
```

See individual module READMEs for detailed usage instructions.

## Data Requirements

This module may require:
- Threat intelligence feeds
- Security event logs
- Historical incident data
- Environmental context data

Configure data sources via environment variables or configuration files.

## Package Structure

```
packages/intelligence-analysis/
├── README.md
└── python/
    ├── setup.py
    ├── pyproject.toml
    ├── requirements.txt
    └── isrms_intel/
        ├── __init__.py
        ├── scenario_analysis/
        │   ├── __init__.py
        │   └── bayesian_analyzer.py
        ├── ctim/
        │   ├── __init__.py
        │   └── mobilization_tracker.py
        ├── posture_ops/
        │   ├── __init__.py
        │   └── log_analyzer.py
        └── red_team/
            ├── __init__.py
            └── adversary_simulator.py
```

## Dependencies

- Python 3.10+
- pandas, numpy, scipy (data analysis)
- scikit-learn (machine learning)
- networkx (graph analysis for Bayesian networks)
- Additional dependencies listed in requirements.txt

## Development

```bash
# Install in development mode
pip install -e packages/intelligence-analysis/python[dev]

# Run tests
pytest packages/intelligence-analysis/python/tests

# Run linting
pylint isrms_intel
```

## License

Proprietary - All Rights Reserved
