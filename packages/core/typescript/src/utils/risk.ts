import { RiskLevel } from '../types';

/**
 * Convert numeric score to risk level
 */
export function getRiskLevel(score: number): RiskLevel {
  if (score >= 80) return RiskLevel.CRITICAL;
  if (score >= 60) return RiskLevel.HIGH;
  if (score >= 40) return RiskLevel.MEDIUM;
  return RiskLevel.LOW;
}

/**
 * Get color for risk level (for UI)
 */
export function getRiskColor(level: RiskLevel): string {
  switch (level) {
    case RiskLevel.CRITICAL:
      return '#dc2626'; // red-600
    case RiskLevel.HIGH:
      return '#ea580c'; // orange-600
    case RiskLevel.MEDIUM:
      return '#ca8a04'; // yellow-600
    case RiskLevel.LOW:
      return '#16a34a'; // green-600
  }
}

/**
 * Format risk score for display
 */
export function formatRiskScore(score: number, decimals: number = 2): string {
  return score.toFixed(decimals);
}