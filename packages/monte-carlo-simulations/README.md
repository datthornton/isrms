# IRMS Monte Carlo Simulations

Comprehensive Monte Carlo simulation models for security risk analysis in the Integrated Risk Management System (IRMS).

## Modules

### ALE (Annual Loss Estimation)

- Dashboard for threat analysis and ROI calculation
- Threat explorer with deep-dive capabilities
- Mitigation ROI modeling

### Black Swan Simulations

- Rare event modeling using PERT distributions
- Blast injury calculations
- Control effectiveness analysis

### Domestic Terror Simulations

- Monte Carlo simulations for domestic terrorism incident modeling
- Frequency and severity distribution analysis
- Scenario-based risk estimation

### Laffer Security Models

- Security investment optimization
- Diminishing returns analysis

### MCS Version 2

- Advanced Monte Carlo optimization engine
- Genetic algorithm-based bundle optimization
- Multi-objective frontier analysis

### Security Strategy

- Security measure effectiveness modeling
- Functional coverage analysis

## Installation

From the repository root:

```bash
pip install -e packages/monte-carlo-simulations/python
```

## Usage

```python
# ALE calculations
from isrms_mcs.ale.models.ale_equation import calculate_ale, calculate_sle, calculate_aro

# Black Swan simulation
from isrms_mcs.black_swan.simulation import run_black_swan_simulation

# Laffer security model
from isrms_mcs.laffer.security_laffer_model import calculate_optimal_investment

# MCS V2
from isrms_mcs.v2.config import SimulationConfig
from isrms_mcs.v2.optimize import run_optimization

# Security Strategy
from isrms_mcs.security_strategy.streamlit_module import build_strategy_dashboard
```

See individual module READMEs for detailed usage instructions.

## Data Files

Data files (`.xlsx`) are not included in this package. Configure paths via environment variables:

- `ISRMS_ALE_WORKBOOK` – Path to `ALE_workbook.xlsx`
- `ISRMS_MCS_DATA_DIR` – Directory containing MCS input files

## Package Structure

```
packages/monte-carlo-simulations/
├── README.md
└── python/
    ├── setup.py
    ├── pyproject.toml
    ├── requirements.txt
    └── isrms_mcs/
        ├── __init__.py
        ├── ale/
        │   ├── __init__.py
        │   ├── dashboard/
        │   │   ├── __init__.py
        │   │   ├── irms_ui.py
        │   │   └── pages/
        │   │       ├── __init__.py
        │   │       ├── threat_explorer.py
        │   │       └── mitigation_roi.py
        │   ├── models/
        │   │   ├── __init__.py
        │   │   └── ale_equation.py
        │   └── modules/
        │       ├── __init__.py
        │       └── load_ale_scenarios.py
        ├── black_swan/
        │   ├── __init__.py
        │   └── simulation.py
        ├── domestic_terror/
        │   ├── __init__.py
        │   └── simulation.py
        ├── laffer/
        │   ├── __init__.py
        │   └── security_laffer_model.py
        ├── v2/
        │   ├── __init__.py
        │   ├── config.py
        │   ├── optimize.py
        │   ├── dashboard.py
        │   ├── clean.py
        │   └── run_profile.py
        └── security_strategy/
            ├── __init__.py
            └── streamlit_module.py
```
