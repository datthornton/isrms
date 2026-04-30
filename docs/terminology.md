# ISRMS Terminology & Standards

## Purpose
This document defines standardized terminology across all ISRMS modules to ensure consistency.

## Risk Levels

### Standard Risk Scale
- **CRITICAL**: Immediate threat requiring emergency response
- **HIGH**: Significant risk requiring priority mitigation
- **MEDIUM**: Moderate risk requiring planned mitigation
- **LOW**: Minor risk, monitor and reassess periodically

### Risk Score Ranges
- **CRITICAL**: 80-100
- **HIGH**: 60-79
- **MEDIUM**: 40-59
- **LOW**: 0-39

## Assessment Levels

- **Facility-level**: Individual location/site assessment
- **PHA-level**: Public Housing Authority (multiple facilities)
- **System-level**: Entire organization (all PHAs)

## Key Terms

### ASHER
**Active Shooter Hazard Exposure Rating**
- Assessed using Lei-Mackenzie models
- Calculated at facility and system levels
- Output: Numeric risk score (0-100)

### NIBRS
**National Incident-Based Reporting System**
- Focuses on "A" crimes (serious offenses)
- Assessed using Lei-Mackenzie models
- Output: Numeric risk score (0-100)

### SERA
**Special Event Risk Assessment**
- Conducted for high-visibility or temporary events
- Produces risk registers and mitigation plans

### PIR
**Priority Intelligence Requirements**
- Generated from Posture Ops analysis
- 72-hour threat indicators

### KPI
**Key Performance Indicator**
- Monthly and quarterly security metrics
- Includes variance analysis and trends

## Data File Terminology

### Input Datasheets
Standardized input files:
- **Incident Data**: `.xlsx` format, standard columns
- **Watch Commander Logs**: `.pdf` or `.xlsx`
- **SAR (Suspicious Activity Reports)**: `.xlsx`
- **Intelligence Logs**: `.pdf` with embedded images

### Output Datasheets
Standardized output files:
- **Risk Registers**: Facility, PHA, or System level
- **Assessment Reports**: FEMA 455 format
- **KPI Reports**: Monthly/Quarterly
- **Intelligence Summaries**: 72hr, 3mo, 6mo projections

## Calculation Models

### Lei-Mackenzie Model
Standard risk calculation methodology for:
- ASHER risk assessment
- NIBRS risk assessment
- System-level aggregations

### Monte Carlo Simulation
Used for:
- Mitigation cost optimization
- Red Team incident simulations
- Uncertainty quantification

### Bayesian Analysis
Used for:
- Scenario/competing hypothesis analysis
- Probabilistic threat assessment

## Status Indicators

- **ID**: In Development (not functioning)
- **Functional**: Operational but may need refinement
- **Production**: Fully tested and deployed
- **Deprecated**: Being replaced or removed

## Naming Conventions

### Files
- Risk registers: `risk-register-{level}-{date}.xlsx`
- KPI reports: `kpi-{period}-{date}.pdf`
- Assessments: `{facility-id}-assessment-{date}.pdf`

### Functions
- Use camelCase: `calculateASHERRisk()`
- Prefix level: `facilityRiskScore()`, `systemRiskScore()`

### Variables
- Constants: `UPPER_SNAKE_CASE`
- Regular: `camelCase`
- Types/Interfaces: `PascalCase`
