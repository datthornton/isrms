# Security Risk Analysis Module - Complete

## Status: Phase 1 Complete ✅

All 10 subcomponents have been implemented:

### Fully Functional (Migrated from Existing Code)
1. ✅ **ASHER Risk Calculator** - v3 with full TVC model
2. ✅ **NIBRS SVA** - Lei-Mackenzie threat model + TVC
3. ✅ **Risk Register** - Automated facility and system-level registers
4. ✅ **Risk Matrix** - Combined ASHER + NIBRS visualization
5. ✅ **Security Assessment** - Physical security indicator scoring

### Templates (Ready for Development)
6. 📋 **Blast Effects Calculator** - IED blast modeling (Kingery-Bulmash)
7. 📋 **SERA Dashboard** - Special event risk assessment
8. 📋 **FEMA 455** - Facility risk assessment methodology
9. 📋 **Mitigation Cost Simulation** - Monte Carlo optimization
10. 📋 **Security Strategy** - Strategic security planning

## Architecture

```
packages/security-risk-analysis/
├── python/
│   └── isrms_security/
│       ├── asher/              # ASHER v3
│       ├── nibrs/              # NIBRS SVA
│       ├── risk_register/      # Risk register generator
│       ├── risk_matrix/        # ASHER+NIBRS matrix
│       ├── security_assessment/# Security indicator assessment
│       ├── blast_calculator/   # Blast effects
│       ├── sera/               # Special events
│       ├── fema455/            # FEMA methodology
│       ├── mitigation_sim/     # Monte Carlo
│       └── security_strategy/  # Strategic planning
└── README.md
```

## Usage

### ASHER Risk Assessment
```python
from isrms_security.asher import calculate_asher_risk
from isrms_security.asher.data_loader import load_asher_data

data_path = Path("facility_profile.xlsx")
metadata, threat_ctx, vuln_ctx, fsl, lop, services, pop = load_asher_data(data_path)

result = calculate_asher_risk(
    facility_id="PH1A",
    incident_type="ASE",
    threat_context_df=threat_ctx,
    vulnerability_context_df=vuln_ctx,
    fsl_df=fsl,
    lop_df=lop,
    services_df=services,
)

print(f"Risk Score: {result.risk_score}")
print(f"Risk Level: {result.risk_level}")
```

### NIBRS SVA
```python
from isrms_security.nibrs import load_nibrs_data, calculate_nibrs_threat, compute_model_2_score

data_path = Path("facility_profile.xlsx")
facility_context, model_1_rows, model_2_rows = load_nibrs_data(data_path)

# Calculate threat scores
import pandas as pd
state_crime_df = pd.read_excel(data_path, sheet_name="State Crime")
state_nibrs_df = pd.read_excel(data_path, sheet_name="State_NIBRS")

threat_scores, debug = calculate_nibrs_threat(
    hospital_pop=5000,
    state_crime_df=state_crime_df,
    state_nibrs_df=state_nibrs_df,
)

# Calculate risk for specific facility/crime
row = model_2_rows[
    (model_2_rows["Hospital"] == "Memorial Hospital") &
    (model_2_rows["Crime"] == "Aggravated Assault")
].iloc[0]

risk = compute_model_2_score(row, threat_scores)
print(f"NIBRS Risk: {risk}")
```

### Risk Register
```python
from isrms_security.risk_register import generate_system_risk_register
from isrms_core.models import FacilityRiskAssessment

# Generate system-level register
register_df = generate_system_risk_register(
    facilities=facility_assessments,
    output_path=Path("system_risk_register.csv")
)
```

### Security Assessment
```python
from isrms_security.security_assessment import conduct_security_assessment
import pandas as pd

indicators_df = pd.read_excel("IRMS_Security_Indicators.xlsx")
scoring_bands_df = pd.read_excel("IRMS_Security_Indicators.xlsx", sheet_name="IRMS_Security_Scoring")

responses = {
    "SEC-001": "Y",
    "SEC-002": "N",
    "SEC-003": "Y",
    # ... more responses
}

assessment = conduct_security_assessment(
    facility_name="Memorial Hospital",
    indicator_responses=responses,
    indicators_df=indicators_df,
    scoring_bands_df=scoring_bands_df,
)

print(f"Total Risk: {assessment.total_risk_score}")
print(f"Adequacy: {assessment.adequacy_band}")
```

## Next Steps

### Phase 2: Intelligence Risk Analysis Module
- Scenario Analysis (Bayesian)
- CTIM (Mobilization Indicators)
- Posture Ops (Log Analysis + OCR)
- Red Team Simulation

### Phase 3: Operational Analysis Module
- Monthly KPI
- Quarterly KPI
- Forecast Generator

### Phase 4: Executive Dashboard
- System-level aggregation
- Intelligence projections
- Operational trends

## Data Requirements

### ASHER
- `facility_profile.xlsx` with sheets:
  - metadata
  - threat_context
  - vulnerability_context
  - FSL_factors
  - LOP_factors
  - services
  - population

### NIBRS SVA
- `facility_profile.xlsx` with sheets:
  - County - Pop
  - Jurisdiction - Pop
  - State Crime
  - County Crime
  - State_NIBRS
  - County_NIBRS

### Security Assessment
- `IRMS_Security_Indicators.xlsx` with sheets:
  - Security_Staff
  - Security_Management
  - General_HCF
  - Emergency_Department
  - Pediatric_&_Infant
  - Outpatient_Pharmacy
  - Office
  - IRMS_Security_Scoring

## Migration Notes

### From Existing Codebases
- ASHER: Migrated from `C:\IRMS\ASHER Risk Calculator V2`
- NIBRS: Migrated from `C:\IRMS\NIBRS_SVA_Dashboard`
- Risk Matrix: Migrated from `C:\IRMS\ASHER_NIBRS_Risk_Matrix`
- Security Assessment: Migrated from `C:\IRMS\Security Assessment`

### Standardization Applied
- All calculations now use `isrms_core` shared functions
- Crime labels normalized via `isrms_core.utils.normalization`
- Risk levels use standardized `RiskLevel` enum
- Data loading centralized and path-agnostic