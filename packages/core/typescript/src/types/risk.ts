/**
 * Risk assessment types - matches Python models
 */

export enum RiskLevel {
  CRITICAL = 'CRITICAL', // 80-100
  HIGH = 'HIGH',         // 60-79
  MEDIUM = 'MEDIUM',     // 40-59
  LOW = 'LOW',           // 0-39
}

export interface ThreatScore {
  crimeType: string;
  score: number; // 0.0 to 1.0
  lambdaValue: number;
  countyMultiplier: number;
  stateMultiplier: number;
  debugInfo: Record<string, any>;
}

export interface FacilityRiskAssessment {
  facilityId: string;
  facilityName: string;
  timestamp: string; // ISO 8601
  riskLevel: RiskLevel;
  
  // NIBRS Scores
  nibrsCompositeScore: number;
  nibrsCrimeScores: Record<string, number>; // {crime_type: score}
  
  // ASHER Scores (optional)
  asherCompositeScore?: number;
  asherEventScores?: Record<string, number>;
  
  // Context
  population?: number;
  squareFootage?: number;
  county?: string;
  state: string;
  
  // Recommendations
  recommendations?: string[];
}

export interface SystemRiskAssessment {
  timestamp: string; // ISO 8601
  overallRiskLevel: RiskLevel;
  averageScore: number;
  
  // Facility breakdown
  totalFacilities: number;
  criticalCount: number;
  highCount: number;
  mediumCount: number;
  lowCount: number;
  
  // Highest risk facilities
  highestRiskFacilities: string[];
  
  // Aggregated crime risks
  crimeRiskSummary: Record<string, number>;
  
  // Trend data
  trend: 'increasing' | 'decreasing' | 'stable';
  varianceFromForecast?: number;
}

export interface TVCComponents {
  threat: number;
  vulnerability: number;
  consequence: number;
  scaling?: number;
}