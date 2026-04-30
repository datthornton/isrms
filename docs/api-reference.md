# ISRMS API Reference

## Core Library (@isrms/core)

### Risk Calculations

#### `calculateASHER(params: ASHERParams): number`
Calculates ASHER (Active Shooter Hazard Exposure Rating) using Lei-Mackenzie model.

**Parameters:**
- `facilityId: string` - Unique facility identifier
- `historicalIncidents: number` - Count of historical incidents
- `population: number` - Facility population/occupancy
- `securityMeasures: SecurityMeasure[]` - Existing security controls

**Returns:** Risk score (0-100)

**Example:**
```typescript
import { calculateASHER } from '@isrms/core/calculations';

const score = calculateASHER({
  facilityId: 'FAC-001',
  historicalIncidents: 3,
  population: 500,
  securityMeasures: ['cameras', 'access_control']
});
```

---

#### `calculateNIBRS(params: NIBRSParams): number`
Calculates NIBRS "A" crime risk using Lei-Mackenzie model.

**Parameters:**
- `facilityId: string`
- `crimeData: CrimeIncident[]` - Historical NIBRS data
- `demographics: Demographics` - Population demographics

**Returns:** Risk score (0-100)

---

#### `aggregateSystemRisk(facilities: FacilityRisk[]): SystemRisk`
Aggregates facility-level risks to system-level.

**Parameters:**
- `facilities: FacilityRisk[]` - Array of facility risk assessments

**Returns:**
```typescript
interface SystemRisk {
  overallRiskLevel: RiskLevel;
  averageScore: number;
  highestRiskFacilities: string[];
  criticalCount: number;
  highCount: number;
  mediumCount: number;
  lowCount: number;
}
```

---

### Types

#### `RiskLevel`
```typescript
enum RiskLevel {
  CRITICAL = 'CRITICAL',
  HIGH = 'HIGH',
  MEDIUM = 'MEDIUM',
  LOW = 'LOW'
}
```

#### `FacilityRiskAssessment`
```typescript
interface FacilityRiskAssessment {
  facilityId: string;
  timestamp: Date;
  riskLevel: RiskLevel;
  asherScore: number;
  nibrsScore: number;
  compositeScore: number;
  recommendations: string[];
}
```

---

## Data Layer (@isrms/data-layer)

### Input Manager

#### `parseIncidentData(file: File): Promise<IncidentData[]>`
Parses incident data from .xlsx files.

#### `parseWatchCommanderLog(file: File): Promise<LogEntry[]>`
Parses watch commander logs with OCR support for embedded images.

#### `parseSAR(file: File): Promise<SAREntry[]>`
Parses Suspicious Activity Reports.

### Output Manager

#### `generateRiskRegister(level: 'facility' | 'system', data: RiskData): Promise<Report>`
Generates automated risk register.

#### `generateKPIReport(period: 'monthly' | 'quarterly', data: KPIData): Promise<Report>`
Generates KPI reports.

---

## Security Risk Analysis Module

### Blast Calculator

#### `calculateBlastEffects(charge: BlastParams): BlastEffects`
Calculates injury and damage ranges for IED charges.

**Parameters:**
```typescript
interface BlastParams {
  chargeWeight: number; // kg TNT equivalent
  standoffDistance: number; // meters
  buildingType: 'concrete' | 'steel' | 'wood';
}
```

**Returns:**
```typescript
interface BlastEffects {
  lethalRadius: number;
  severeInjuryRadius: number;
  minorInjuryRadius: number;
  structuralDamageRadius: number;
}
```

---

## Intelligence Analysis Module

### Scenario Analysis

#### `runBayesianAnalysis(hypotheses: Hypothesis[], evidence: Evidence[]): AnalysisResult`
Runs Bayesian competing hypothesis analysis.

### Posture Ops

#### `analyzeThreatPosture(logs: LogEntry[], sars: SAREntry[]): PostureRecommendation`
Analyzes logs and SARs to recommend security posture.

**Returns:**
```typescript
interface PostureRecommendation {
  posture: 'NORMAL' | 'ELEVATED' | 'HIGH' | 'SEVERE';
  pirs: string[]; // Priority Intelligence Requirements
  indicators: ThreatIndicator[];
  validFor: '72h' | '3mo' | '6mo';
}
```

---

## Operational Analysis Module

### Forecast Generator

#### `generateForecast(historicalData: MonthlyData[]): ForecastResult`
Generates incident forecasts using seasonal linear regression.

**Returns:**
```typescript
interface ForecastResult {
  predictions: MonthlyPrediction[];
  seasonalFactors: number[];
  trend: 'increasing' | 'decreasing' | 'stable';
  confidenceInterval: [number, number];
}
```

---

## REST API Endpoints

### Risk Assessment

```
POST /api/risk/facility
POST /api/risk/system
GET  /api/risk/facility/:id
GET  /api/risk/system
```

### Intelligence

```
POST /api/intelligence/scenario
GET  /api/intelligence/posture
GET  /api/intelligence/projections
```

### Operations

```
GET  /api/operations/kpi/monthly
GET  /api/operations/kpi/quarterly
GET  /api/operations/forecast
```

---

**Note:** Full API documentation with request/response examples will be generated using OpenAPI/Swagger once endpoints are implemented.
