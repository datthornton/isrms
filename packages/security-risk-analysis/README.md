# Security Risk Analysis Module

Physical security risk assessment tools for facility and system-level analysis.

## Subcomponents

### 1. ASHER Risk Calculator
- **Status**: ✅ Functional (v3)
- **Description**: Active Shooter Hazard Exposure Rating using Lei-Mackenzie TVC model
- **Levels**: Facility and System
- **Path**: `asher/`

### 2. NIBRS SVA
- **Status**: ✅ Functional (v3)
- **Description**: NIBRS "A" Crime risk assessment
- **Path**: `nibrs-sva/`

### 3. ASHER/NIBRS Risk Matrix
- **Status**: 🔨 In Development
- **Description**: Combined risk matrix visualization
- **Path**: `risk-matrix/`

### 4. Blast Effects Calculator
- **Status**: 🔨 In Development
- **Description**: IED blast injury and damage range calculator
- **Path**: `blast-calculator/`

### 5. SERA Dashboard
- **Status**: 🔨 In Development
- **Description**: Special Event Risk Assessment
- **Path**: `sera/`

### 6. Security Assessment
- **Status**: 🔨 In Development
- **Description**: Physical security criteria assessment
- **Path**: `security-assessment/`

### 7. Risk Register
- **Status**: 🔨 In Development
- **Description**: Automated facility/system risk register generation
- **Path**: `risk-register/`

### 8. Facility Risk Assessment
- **Status**: 🔨 In Development
- **Description**: FEMA 455-based facility assessment
- **Path**: `fema-455/`

### 9. Mitigation Cost Simulation
- **Status**: 🔨 In Development
- **Description**: Monte Carlo simulation for optimal mitigation packages
- **Path**: `mitigation-sim/`

### 10. Security Strategy
- **Status**: 🔨 In Development
- **Description**: Security strategy development across domains
- **Path**: `security-strategy/`

## Installation

```bash
pip install -e packages/security-risk-analysis/python
```

## Usage

### ASHER Risk Assessment
```python
from isrms_security.asher import calculate_asher_risk

risk = calculate_asher_risk(
    facility_id="PH1A",
    incident_type="ASE",
    data_path="facility_profile.xlsx"
)
```

### NIBRS SVA
```python
from isrms_security.nibrs import calculate_nibrs_risk

risk = calculate_nibrs_risk(
    hospital_name="Memorial Hospital",
    crime_type="Aggravated Assault"
)
```