# Integrated Security Risk Management System (ISRMS)

## Overview

ISRMS is a comprehensive security risk management platform that integrates three core modules:

1. **Security Risk Analysis** - Facility and system-level physical security risk assessment
2. **Intelligence Risk Analysis** - Threat scenario analysis and security posture recommendations
3. **Operational Analysis** - KPI tracking, incident forecasting, and trend analysis

## Architecture

This is a monorepo managed with pnpm workspaces, containing:

- **`packages/core`** - Shared utilities, types, and calculation engines
- **`packages/data-layer`** - Centralized input/output datasheet handling
- **`packages/security-risk-analysis`** - Module 1: Security Risk Analysis
- **`packages/intelligence-analysis`** - Module 2: Intelligence Risk Analysis
- **`packages/operational-analysis`** - Module 3: Operational Analysis
- **`apps/dashboard`** - Executive dashboard (Next.js)
- **`apps/api`** - Backend API service

## Getting Started

### Prerequisites

- Node.js 18+ or Python 3.10+
- pnpm 8+

### Installation

```bash
# Install pnpm globally
npm install -g pnpm

# Install all dependencies
pnpm install
```

### Development

```bash
# Run all packages in development mode
pnpm dev

# Run specific package
pnpm --filter @isrms/dashboard dev

# Run tests
pnpm test
```

## Module Status

### Security Risk Analysis
- [ ] SERA/SERA Dashboard
- [ ] Blast Effects Calculator
- [ ] ASHER Risk Calculator (Facility)
- [ ] ASHER Risk Calculator (System-level)
- [ ] ASHER/NIBRS Risk Matrix
- [ ] NIBRS Risk Calculator
- [ ] Security Assessment
- [ ] Risk Register (Automated)
- [ ] Facility Risk Assessment (FEMA 455)
- [ ] Mitigation Cost Simulation
- [ ] Security Strategy

### Intelligence Risk Analysis
- [ ] Scenario Analysis Dashboard (Bayesian)
- [ ] CTIM (Mobilization Indicators)
- [ ] Posture Ops (Log Analysis)
- [ ] Red Team Simulation

### Operational Analysis
- [ ] Monthly KPI Reports
- [ ] Quarterly KPI Reports
- [ ] Forecast Generator

## Documentation

- [Architecture Overview](./docs/architecture.md)
- [Terminology & Standards](./docs/terminology.md)
- [API Reference](./docs/api-reference.md)
- [Development Guide](./docs/development.md)

## License

Proprietary - All Rights Reserved
