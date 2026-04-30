# ISRMS Architecture

## System Overview

ISRMS is built as a monorepo using pnpm workspaces, enabling code sharing while maintaining module independence.

## Core Principles

### 1. Shared Core Library
All risk calculations, type definitions, and utilities are centralized in `@isrms/core` to ensure:
- Consistent terminology across modules
- Single source of truth for calculations (Lei-Mackenzie models, etc.)
- Reduced code duplication

### 2. Centralized Data Layer
All input/output datasheet handling is managed by `@isrms/data-layer`:
- Unified .xlsx, .pdf, and image parsing
- Standardized data validation
- Single location for input datasheets
- Single location for output datasheets

### 3. Module Independence
Each module (`security-risk-analysis`, `intelligence-analysis`, `operational-analysis`) can:
- Be developed independently
- Have its own release cycle
- Import from `@isrms/core` and `@isrms/data-layer`

### 4. Executive Dashboard Integration
The dashboard (`apps/dashboard`) provides:
- System-level risk aggregation
- Access to all submodules
- Operational trends and status
- Intelligence summaries (72hr, 3mo, 6mo projections)

## Technology Stack

### Frontend
- **Framework**: Next.js 14 (React 18)
- **Language**: TypeScript
- **UI Components**: Shadcn/ui, Tailwind CSS
- **Charts**: Recharts, D3.js
- **State Management**: Zustand, React Query

### Backend
- **API**: Node.js + Fastify OR Python FastAPI
- **Database**: PostgreSQL (relational data)
- **Cache**: Redis
- **File Processing**: xlsx, pdf-parse, tesseract.js (OCR)

### Calculations
- **Risk Models**: Python (scipy, numpy, pandas)
- **Monte Carlo**: Python (scipy.stats)
- **Bayesian Analysis**: Python (pymc3 or similar)

## Data Flow

```
Input Datasheets (.xlsx, .pdf)
    ↓
@isrms/data-layer (parsing, validation)
    ↓
Module-specific processing
    ↓
@isrms/core (risk calculations)
    ↓
Output Datasheets + Database
    ↓
Executive Dashboard (visualization)
```

## Module Architecture

### Security Risk Analysis
- **Facility-level**: Individual facility assessments
- **System-level**: Aggregated risk across all facilities
- **Shared calculations**: ASHER, NIBRS, blast effects

### Intelligence Analysis
- **Scenario Analysis**: Bayesian hypothesis testing
- **Posture Ops**: Log parsing (OCR for images)
- **Projections**: 72hr, 3mo, 6mo threat forecasts

### Operational Analysis
- **KPI Reports**: Monthly and quarterly
- **Forecasting**: Seasonal linear regression
- **Variance Analysis**: Actual vs. forecasted incidents

## Scalability Considerations

- **Horizontal scaling**: API can run multiple instances behind load balancer
- **Computation offloading**: Heavy calculations (Monte Carlo, Bayesian) run as async jobs
- **Caching strategy**: Redis for frequently accessed risk scores and reports
- **Database optimization**: Indexed queries for facility/system lookups
