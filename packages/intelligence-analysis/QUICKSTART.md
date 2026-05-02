# Intelligence Analysis Module - Quickstart Examples

This guide provides quick examples for each tool in the Intelligence Analysis module.

## Installation

```bash
# From repository root
pip install -e packages/intelligence-analysis/python
```

## 1. Bayesian Scenario Analysis

Probabilistic threat scenario modeling:

```python
from isrms_intel.scenario_analysis import BayesianScenarioAnalyzer

# Initialize analyzer
analyzer = BayesianScenarioAnalyzer()

# Add threat scenarios
analyzer.add_scenario(
    name="insider_threat",
    description="Malicious insider with access to critical systems",
    factors=["access_level", "motivation", "capability", "opportunity"]
)

analyzer.add_scenario(
    name="external_attack",
    description="External adversary targeting infrastructure",
    factors=["vulnerability", "threat_actor", "attack_vector", "defense_posture"]
)

# Set probabilities (simplified example)
analyzer.set_probability("motivation", {}, 0.3)
analyzer.set_probability("capability", {"motivation": True}, 0.7)

# Add evidence
analyzer.add_evidence("access_level", True)
analyzer.add_evidence("motivation", True)

# Analyze scenarios
results = analyzer.analyze_scenarios()
print(results)

# Get detailed scenario information
details = analyzer.get_scenario_details("insider_threat")
print(f"Insider Threat Probability: {details['overall_probability']:.2%}")
```

## 2. Mobilization Indicator Tracking (CTIM)

Track threat actor mobilization and generate early warnings:

```python
from isrms_intel.ctim import MobilizationIndicatorTracker, IndicatorType

# Initialize tracker
tracker = MobilizationIndicatorTracker()

# Add indicators
tracker.add_indicator(
    indicator_type=IndicatorType.RECONNAISSANCE,
    description="Increased port scanning activity from known threat IPs",
    confidence=0.75,
    source="IDS"
)

tracker.add_indicator(
    indicator_type=IndicatorType.CAPABILITY_DEVELOPMENT,
    description="Malware sample analysis shows targeting of our infrastructure",
    confidence=0.85,
    source="Threat Intelligence Feed"
)

tracker.add_indicator(
    indicator_type=IndicatorType.POSITIONING,
    description="Suspicious account creation near critical systems",
    confidence=0.90,
    source="SIEM"
)

# Check current threat level
threat_level = tracker.get_threat_level()
print(f"Current Threat Level: {threat_level.name}")

# Get indicators summary
summary = tracker.get_indicators_summary()
print(summary)

# Get alerts
alerts = tracker.get_alerts()
for alert in alerts:
    print(f"[{alert['timestamp']}] {alert['message']} (confidence: {alert['confidence']:.0%})")

# Correlate indicators for patterns
correlation = tracker.correlate_indicators()
print(f"\nIdentified {len(correlation['patterns'])} patterns")
for pattern in correlation['patterns']:
    print(f"  - {pattern['type']}: {pattern['count']} indicators, {pattern['avg_confidence']:.0%} confidence")
```

## 3. Security Posture Monitoring (Posture Ops)

Analyze security logs for anomalies and trends:

```python
from isrms_intel.posture_ops import LogAnalyzer
from datetime import datetime, timedelta
import pandas as pd

# Initialize analyzer
analyzer = LogAnalyzer()

# Ingest logs (example)
for i in range(100):
    timestamp = datetime.now() - timedelta(hours=i)
    analyzer.ingest_log(
        timestamp=timestamp,
        event_type="authentication_failure" if i % 10 == 0 else "normal_access",
        severity="warning" if i % 10 == 0 else "info",
        source=f"system_{i % 5}",
        message=f"Event {i}"
    )

# Or ingest from DataFrame
# df = pd.read_csv("security_logs.csv")
# df['timestamp'] = pd.to_datetime(df['timestamp'])
# analyzer.ingest_logs_from_dataframe(df)

# Establish baseline
analyzer.establish_baseline(days=30)

# Detect anomalies
anomalies = analyzer.detect_anomalies(window_hours=24, threshold=2.0)
print(f"Detected {len(anomalies)} anomalies")
for anomaly in anomalies:
    print(f"  - {anomaly['event_type']}: {anomaly['deviation']:.1f}x deviation from baseline")

# Get security metrics
metrics = analyzer.get_security_metrics(window_hours=24)
print(f"\nSecurity Metrics (last 24h):")
print(f"  Total Events: {metrics['total_events']}")
print(f"  Critical: {metrics['critical_events']}")
print(f"  Errors: {metrics['error_events']}")
print(f"  Warnings: {metrics['warning_events']}")
print(f"  Events/Hour: {metrics['events_per_hour']:.1f}")

# Trend analysis
trends = analyzer.get_trend_analysis(days=7)
print(trends)

# Top events
top_events = analyzer.get_top_events(n=5, window_hours=24)
print("\nTop 5 Event Types:")
print(top_events)
```

## 4. Red Team Simulation

Simulate adversarial attacks to test defenses:

```python
from isrms_intel.red_team import AdversarySimulator, AttackVector, AttackPhase

# Initialize simulator
simulator = AdversarySimulator()

# Add attack scenarios
simulator.add_scenario(
    name="ransomware_attack",
    description="Ransomware deployment via phishing",
    attack_vector=AttackVector.PHISHING,
    target="corporate_network",
    objectives=["data_encryption", "ransom_demand", "data_exfiltration"]
)

simulator.add_scenario(
    name="insider_sabotage",
    description="Malicious insider disrupts operations",
    attack_vector=AttackVector.INSIDER_THREAT,
    target="production_systems",
    objectives=["service_disruption", "data_theft"]
)

# Add defensive controls
simulator.add_defensive_control(
    name="email_filtering",
    control_type="preventive",
    effectiveness=0.8,
    coverage_phases=[AttackPhase.DELIVERY]
)

simulator.add_defensive_control(
    name="endpoint_protection",
    control_type="preventive",
    effectiveness=0.7,
    coverage_phases=[AttackPhase.EXPLOITATION, AttackPhase.INSTALLATION]
)

simulator.add_defensive_control(
    name="network_segmentation",
    control_type="preventive",
    effectiveness=0.6,
    coverage_phases=[AttackPhase.COMMAND_CONTROL, AttackPhase.ACTIONS_ON_OBJECTIVES]
)

# Run simulation
results = simulator.simulate_attack("ransomware_attack", iterations=10000)
print(f"\nRansomware Attack Simulation Results:")
print(f"  Overall Success Rate: {results['overall_success_rate']:.1%}")
print(f"  Risk Level: {results['estimated_risk']}")
print(f"\nPhase Success Rates:")
for phase, rate in results['phase_success_rates'].items():
    print(f"  {phase}: {rate:.1%}")

# Simulate another scenario
results2 = simulator.simulate_attack("insider_sabotage", iterations=10000)

# Compare scenarios
comparison = simulator.compare_scenarios()
print("\nScenario Comparison:")
print(comparison)

# Get recommendations
recommendations = simulator.get_defensive_recommendations("ransomware_attack")
print(f"\nDefensive Recommendations for Ransomware Attack:")
for rec in recommendations:
    print(f"  [{rec['priority']}] {rec['recommendation']}")
    print(f"    Current success rate: {rec['current_success_rate']:.1%}")

# Export results
export_df = simulator.export_results()
export_df.to_csv("/tmp/red_team_results.csv", index=False)
print("\nResults exported to /tmp/red_team_results.csv")
```

## Combined Analysis Example

Integrate multiple tools for comprehensive intelligence analysis:

```python
from isrms_intel import (
    BayesianScenarioAnalyzer,
    MobilizationIndicatorTracker,
    LogAnalyzer,
    AdversarySimulator
)

# Scenario: Coordinated threat analysis
print("=== Integrated Threat Intelligence Analysis ===\n")

# 1. Mobilization indicators suggest increased activity
tracker = MobilizationIndicatorTracker()
tracker.add_indicator(IndicatorType.RECONNAISSANCE, "Port scanning", 0.8, "IDS")
tracker.add_indicator(IndicatorType.CAPABILITY_DEVELOPMENT, "Malware detected", 0.85, "AV")

threat_level = tracker.get_threat_level()
print(f"1. Current Threat Level: {threat_level.name}")

# 2. Log analysis shows anomalies
analyzer = LogAnalyzer()
# ... ingest logs ...
# anomalies = analyzer.detect_anomalies()
# print(f"2. Detected {len(anomalies)} log anomalies")

# 3. Bayesian analysis estimates scenario probabilities
bay_analyzer = BayesianScenarioAnalyzer()
bay_analyzer.add_scenario("apt_attack", "Advanced Persistent Threat", ["recon", "malware"])
bay_analyzer.add_evidence("recon", True)
bay_analyzer.add_evidence("malware", True)
scenarios = bay_analyzer.analyze_scenarios()
print(f"3. Most likely scenario: {scenarios.iloc[0]['scenario']}")

# 4. Red team simulation tests defenses
simulator = AdversarySimulator()
simulator.add_scenario("apt_simulation", "APT simulation", AttackVector.ZERO_DAY, "critical_systems", ["persistence"])
# ... add controls ...
# results = simulator.simulate_attack("apt_simulation")
# print(f"4. Simulated attack success rate: {results['overall_success_rate']:.1%}")

print("\n=== Analysis Complete ===")
```

## Next Steps

1. **Integrate with your data sources**: Configure data feeds, log collectors, and threat intelligence sources
2. **Customize scenarios**: Add your organization-specific threat scenarios and attack vectors
3. **Tune thresholds**: Adjust detection thresholds based on your security posture
4. **Build dashboards**: Use Streamlit or other frameworks to visualize results
5. **Automate workflows**: Set up automated analysis pipelines and alerting

## Documentation

- [Full API Reference](../docs/api-reference.md)
- [Architecture Overview](../docs/architecture.md)
- [Development Guide](../docs/development.md)

## Support

For issues or questions, please refer to the main project documentation or contact the development team.
