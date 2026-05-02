"""
Adversary Simulator

Simulates adversarial attack scenarios for security testing.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple
from enum import Enum
from datetime import datetime


class AttackPhase(Enum):
    """Attack lifecycle phases (based on cyber kill chain)."""
    RECONNAISSANCE = "reconnaissance"
    WEAPONIZATION = "weaponization"
    DELIVERY = "delivery"
    EXPLOITATION = "exploitation"
    INSTALLATION = "installation"
    COMMAND_CONTROL = "command_and_control"
    ACTIONS_ON_OBJECTIVES = "actions_on_objectives"


class AttackVector(Enum):
    """Attack vector types."""
    PHISHING = "phishing"
    MALWARE = "malware"
    SOCIAL_ENGINEERING = "social_engineering"
    PHYSICAL_INTRUSION = "physical_intrusion"
    SUPPLY_CHAIN = "supply_chain"
    INSIDER_THREAT = "insider_threat"
    ZERO_DAY = "zero_day_exploit"


class AdversarySimulator:
    """
    Adversary simulation for red team exercises.
    
    Simulates attack scenarios to test security controls and
    identify vulnerabilities in defensive posture.
    
    Attributes:
        scenarios: List of attack scenarios
        success_probabilities: Success rates for each attack phase
        defensive_controls: Active defensive measures
        simulation_results: Results from simulation runs
    """
    
    def __init__(self):
        """Initialize the adversary simulator."""
        self.scenarios = []
        self.success_probabilities = {
            AttackPhase.RECONNAISSANCE: 0.95,
            AttackPhase.WEAPONIZATION: 0.85,
            AttackPhase.DELIVERY: 0.70,
            AttackPhase.EXPLOITATION: 0.60,
            AttackPhase.INSTALLATION: 0.50,
            AttackPhase.COMMAND_CONTROL: 0.45,
            AttackPhase.ACTIONS_ON_OBJECTIVES: 0.40,
        }
        self.defensive_controls = {}
        self.simulation_results = []
        
    def add_scenario(
        self,
        name: str,
        description: str,
        attack_vector: AttackVector,
        target: str,
        objectives: List[str]
    ) -> None:
        """
        Add an attack scenario to simulate.
        
        Args:
            name: Scenario identifier
            description: Scenario description
            attack_vector: Primary attack vector
            target: Target system/asset
            objectives: List of attack objectives
        """
        scenario = {
            "name": name,
            "description": description,
            "attack_vector": attack_vector,
            "target": target,
            "objectives": objectives,
            "created_at": datetime.now()
        }
        
        self.scenarios.append(scenario)
        
    def add_defensive_control(
        self,
        name: str,
        control_type: str,
        effectiveness: float,
        coverage_phases: List[AttackPhase]
    ) -> None:
        """
        Add a defensive control to the simulation.
        
        Args:
            name: Control identifier
            control_type: Type of control (preventive, detective, corrective)
            effectiveness: Control effectiveness (0-1)
            coverage_phases: Attack phases this control addresses
        """
        if not 0 <= effectiveness <= 1:
            raise ValueError("Effectiveness must be between 0 and 1")
        
        self.defensive_controls[name] = {
            "type": control_type,
            "effectiveness": effectiveness,
            "coverage_phases": coverage_phases
        }
        
    def calculate_phase_success(self, phase: AttackPhase) -> float:
        """
        Calculate probability of success for an attack phase.
        
        Considers base success probability and defensive controls.
        
        Args:
            phase: Attack phase to evaluate
            
        Returns:
            Success probability (0-1)
        """
        base_probability = self.success_probabilities[phase]
        
        # Apply defensive controls
        for control in self.defensive_controls.values():
            if phase in control["coverage_phases"]:
                # Reduce success probability based on control effectiveness
                base_probability *= (1 - control["effectiveness"])
        
        return base_probability
        
    def simulate_attack(
        self,
        scenario_name: str,
        iterations: int = 1000
    ) -> Dict:
        """
        Run Monte Carlo simulation of an attack scenario.
        
        Args:
            scenario_name: Name of scenario to simulate
            iterations: Number of simulation iterations
            
        Returns:
            Dictionary with simulation results
        """
        # Find scenario
        scenario = next((s for s in self.scenarios if s["name"] == scenario_name), None)
        if not scenario:
            raise ValueError(f"Scenario '{scenario_name}' not found")
        
        # Run simulations
        successes = 0
        phase_successes = {phase: 0 for phase in AttackPhase}
        
        for _ in range(iterations):
            attack_succeeded = True
            
            # Simulate each phase
            for phase in AttackPhase:
                success_prob = self.calculate_phase_success(phase)
                
                if np.random.random() < success_prob:
                    phase_successes[phase] += 1
                else:
                    # Attack stopped at this phase
                    attack_succeeded = False
                    break
            
            if attack_succeeded:
                successes += 1
        
        # Calculate results
        results = {
            "scenario": scenario_name,
            "iterations": iterations,
            "overall_success_rate": successes / iterations,
            "phase_success_rates": {
                phase.value: phase_successes[phase] / iterations
                for phase in AttackPhase
            },
            "estimated_risk": self._calculate_risk_score(successes / iterations),
            "timestamp": datetime.now()
        }
        
        self.simulation_results.append(results)
        return results
        
    def _calculate_risk_score(self, success_rate: float) -> str:
        """
        Convert success rate to risk score.
        
        Args:
            success_rate: Attack success rate
            
        Returns:
            Risk level (Low, Medium, High, Critical)
        """
        if success_rate >= 0.7:
            return "Critical"
        elif success_rate >= 0.5:
            return "High"
        elif success_rate >= 0.3:
            return "Medium"
        else:
            return "Low"
            
    def compare_scenarios(self) -> pd.DataFrame:
        """
        Compare all simulated scenarios.
        
        Returns:
            DataFrame with scenario comparison
        """
        if not self.simulation_results:
            return pd.DataFrame()
        
        comparison_data = []
        for result in self.simulation_results:
            comparison_data.append({
                "scenario": result["scenario"],
                "success_rate": result["overall_success_rate"],
                "risk_level": result["estimated_risk"],
                "timestamp": result["timestamp"]
            })
        
        df = pd.DataFrame(comparison_data)
        return df.sort_values("success_rate", ascending=False).reset_index(drop=True)
        
    def get_defensive_recommendations(self, scenario_name: str) -> List[Dict]:
        """
        Generate defensive recommendations based on simulation.
        
        Args:
            scenario_name: Scenario to analyze
            
        Returns:
            List of recommended defensive improvements
        """
        # Find simulation results
        result = next(
            (r for r in self.simulation_results if r["scenario"] == scenario_name),
            None
        )
        
        if not result:
            raise ValueError(f"No simulation results for scenario '{scenario_name}'")
        
        recommendations = []
        
        # Identify weak phases
        for phase, success_rate in result["phase_success_rates"].items():
            if success_rate > 0.7:  # High success rate indicates weakness
                recommendations.append({
                    "phase": phase,
                    "current_success_rate": success_rate,
                    "recommendation": f"Strengthen controls for {phase} phase",
                    "priority": "High" if success_rate > 0.85 else "Medium"
                })
        
        return sorted(recommendations, key=lambda x: x["current_success_rate"], reverse=True)
        
    def export_results(self) -> pd.DataFrame:
        """
        Export all simulation results to DataFrame.
        
        Returns:
            DataFrame with detailed simulation results
        """
        if not self.simulation_results:
            return pd.DataFrame()
        
        export_data = []
        for result in self.simulation_results:
            row = {
                "scenario": result["scenario"],
                "iterations": result["iterations"],
                "overall_success_rate": result["overall_success_rate"],
                "estimated_risk": result["estimated_risk"],
                "timestamp": result["timestamp"]
            }
            
            # Add phase success rates
            for phase, rate in result["phase_success_rates"].items():
                row[f"phase_{phase}"] = rate
            
            export_data.append(row)
        
        return pd.DataFrame(export_data)
