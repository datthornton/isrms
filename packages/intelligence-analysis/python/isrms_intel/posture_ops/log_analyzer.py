"""
Log Analyzer

Security log analysis and anomaly detection for posture monitoring.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from collections import Counter


class LogAnalyzer:
    """
    Security log analyzer for posture monitoring.
    
    Analyzes security event logs to detect anomalies, identify trends,
    and generate security posture metrics.
    
    Attributes:
        logs: List of parsed log entries
        baselines: Baseline patterns for anomaly detection
        anomalies: Detected anomalies
    """
    
    def __init__(self):
        """Initialize the log analyzer."""
        self.logs = []
        self.baselines = {}
        self.anomalies = []
        
    def ingest_log(
        self,
        timestamp: datetime,
        event_type: str,
        severity: str,
        source: str,
        message: str,
        metadata: Optional[Dict] = None
    ) -> None:
        """
        Ingest a security log entry.
        
        Args:
            timestamp: Event timestamp
            event_type: Type of security event
            severity: Event severity (info, warning, error, critical)
            source: Log source system
            message: Event message
            metadata: Additional event metadata
        """
        log_entry = {
            "timestamp": timestamp,
            "event_type": event_type,
            "severity": severity,
            "source": source,
            "message": message,
            "metadata": metadata or {}
        }
        
        self.logs.append(log_entry)
        
    def ingest_logs_from_dataframe(self, df: pd.DataFrame) -> None:
        """
        Bulk ingest logs from a DataFrame.
        
        Args:
            df: DataFrame with columns: timestamp, event_type, severity, source, message
        """
        required_columns = ["timestamp", "event_type", "severity", "source", "message"]
        if not all(col in df.columns for col in required_columns):
            raise ValueError(f"DataFrame must contain columns: {required_columns}")
        
        for _, row in df.iterrows():
            self.ingest_log(
                timestamp=row["timestamp"],
                event_type=row["event_type"],
                severity=row["severity"],
                source=row["source"],
                message=row["message"],
                metadata=row.get("metadata", {})
            )
            
    def establish_baseline(self, days: int = 30) -> None:
        """
        Establish baseline patterns from historical logs.
        
        Args:
            days: Number of days of history to use for baseline
        """
        if not self.logs:
            raise ValueError("No logs available to establish baseline")
        
        # Get logs within baseline period
        cutoff = datetime.now() - timedelta(days=days)
        baseline_logs = [log for log in self.logs if log["timestamp"] >= cutoff]
        
        if not baseline_logs:
            raise ValueError(f"No logs found within last {days} days")
        
        # Calculate event type frequencies
        event_counts = Counter(log["event_type"] for log in baseline_logs)
        total_events = len(baseline_logs)
        
        self.baselines["event_frequencies"] = {
            event: count / total_events
            for event, count in event_counts.items()
        }
        
        # Calculate severity distributions
        severity_counts = Counter(log["severity"] for log in baseline_logs)
        self.baselines["severity_distribution"] = {
            severity: count / total_events
            for severity, count in severity_counts.items()
        }
        
        # Calculate hourly event rates
        hourly_counts = Counter(log["timestamp"].hour for log in baseline_logs)
        self.baselines["hourly_rates"] = {
            hour: hourly_counts.get(hour, 0) / days
            for hour in range(24)
        }
        
    def detect_anomalies(self, window_hours: int = 24, threshold: float = 2.0) -> List[Dict]:
        """
        Detect anomalies in recent logs compared to baseline.
        
        Args:
            window_hours: Time window to analyze
            threshold: Standard deviations from baseline to flag as anomaly
            
        Returns:
            List of detected anomalies
        """
        if not self.baselines:
            raise ValueError("Baseline not established. Call establish_baseline() first")
        
        # Get recent logs
        cutoff = datetime.now() - timedelta(hours=window_hours)
        recent_logs = [log for log in self.logs if log["timestamp"] >= cutoff]
        
        if not recent_logs:
            return []
        
        anomalies = []
        
        # Check event type frequencies
        recent_events = Counter(log["event_type"] for log in recent_logs)
        total_recent = len(recent_logs)
        
        for event_type, count in recent_events.items():
            observed_freq = count / total_recent
            baseline_freq = self.baselines["event_frequencies"].get(event_type, 0)
            
            if baseline_freq > 0:
                deviation = abs(observed_freq - baseline_freq) / baseline_freq
                
                if deviation > threshold:
                    anomalies.append({
                        "type": "frequency_anomaly",
                        "event_type": event_type,
                        "observed_frequency": observed_freq,
                        "baseline_frequency": baseline_freq,
                        "deviation": deviation,
                        "timestamp": datetime.now()
                    })
        
        self.anomalies.extend(anomalies)
        return anomalies
        
    def get_security_metrics(self, window_hours: int = 24) -> Dict:
        """
        Calculate security posture metrics.
        
        Args:
            window_hours: Time window for metrics calculation
            
        Returns:
            Dictionary of security metrics
        """
        cutoff = datetime.now() - timedelta(hours=window_hours)
        recent_logs = [log for log in self.logs if log["timestamp"] >= cutoff]
        
        if not recent_logs:
            return {
                "total_events": 0,
                "critical_events": 0,
                "error_events": 0,
                "warning_events": 0,
                "anomaly_count": 0
            }
        
        severity_counts = Counter(log["severity"] for log in recent_logs)
        
        return {
            "total_events": len(recent_logs),
            "critical_events": severity_counts.get("critical", 0),
            "error_events": severity_counts.get("error", 0),
            "warning_events": severity_counts.get("warning", 0),
            "info_events": severity_counts.get("info", 0),
            "anomaly_count": len([a for a in self.anomalies 
                                 if a["timestamp"] >= cutoff]),
            "events_per_hour": len(recent_logs) / window_hours,
            "unique_sources": len(set(log["source"] for log in recent_logs)),
            "unique_event_types": len(set(log["event_type"] for log in recent_logs))
        }
        
    def get_trend_analysis(self, days: int = 7) -> pd.DataFrame:
        """
        Analyze security event trends over time.
        
        Args:
            days: Number of days to analyze
            
        Returns:
            DataFrame with daily trend statistics
        """
        cutoff = datetime.now() - timedelta(days=days)
        recent_logs = [log for log in self.logs if log["timestamp"] >= cutoff]
        
        if not recent_logs:
            return pd.DataFrame()
        
        # Group by day
        daily_stats = []
        for day_offset in range(days):
            day_start = cutoff + timedelta(days=day_offset)
            day_end = day_start + timedelta(days=1)
            
            day_logs = [log for log in recent_logs 
                       if day_start <= log["timestamp"] < day_end]
            
            if day_logs:
                severity_counts = Counter(log["severity"] for log in day_logs)
                daily_stats.append({
                    "date": day_start.date(),
                    "total_events": len(day_logs),
                    "critical": severity_counts.get("critical", 0),
                    "error": severity_counts.get("error", 0),
                    "warning": severity_counts.get("warning", 0),
                    "info": severity_counts.get("info", 0)
                })
        
        return pd.DataFrame(daily_stats)
        
    def get_top_events(self, n: int = 10, window_hours: int = 24) -> pd.DataFrame:
        """
        Get most frequent events in recent logs.
        
        Args:
            n: Number of top events to return
            window_hours: Time window to analyze
            
        Returns:
            DataFrame with top events and their frequencies
        """
        cutoff = datetime.now() - timedelta(hours=window_hours)
        recent_logs = [log for log in self.logs if log["timestamp"] >= cutoff]
        
        if not recent_logs:
            return pd.DataFrame()
        
        event_counts = Counter(log["event_type"] for log in recent_logs)
        top_events = event_counts.most_common(n)
        
        return pd.DataFrame(top_events, columns=["event_type", "count"])
