# @isrms/core

Shared utilities, types, and calculation engines used across all ISRMS modules.

This package contains both Python and TypeScript implementations to support:
- Python-based risk calculation engines (Lei-Mackenzie, TVC, Monte Carlo)
- TypeScript-based web interfaces and API contracts

## Structure

```
core/
├── python/              # Python calculation engines
│   ├── calculations/    # Risk calculation models
│   │   ├── lei_mackenzie.py
│   │   ├── tvc.py
│   │   └── monte_carlo.py
│   ├── models/          # Data models and schemas
│   ├── utils/           # Shared utilities
│   └── types/           # Type definitions
├── typescript/          # TypeScript types and utilities
│   ├── types/
│   ├── utils/
│   └── constants/
└── tests/               # Unified tests
```

## Installation

### Python
```bash
pip install -e packages/core/python
```

### TypeScript
```bash
pnpm install
```

## Usage

### Python
```python
from isrms_core.calculations.lei_mackenzie import calculate_threat_score
from isrms_core.models import FacilityRiskAssessment

threat_scores = calculate_threat_score(
    hospital_pop=5000,
    county_name="Ada",
    state_name="idaho"
)
```

### TypeScript
```typescript
import { RiskLevel, FacilityRiskAssessment } from '@isrms/core/types';
```