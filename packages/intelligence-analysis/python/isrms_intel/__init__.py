"""
ISRMS Intelligence Analysis Module

Comprehensive threat intelligence and risk analysis tools.
"""

__version__ = "0.1.0"

# Version info
VERSION = __version__

# Module metadata
__author__ = "ISRMS Development Team"
__description__ = "Intelligence Risk Analysis Module for ISRMS"

# Public API exports
from isrms_intel.scenario_analysis import BayesianScenarioAnalyzer
from isrms_intel.ctim import MobilizationIndicatorTracker
from isrms_intel.posture_ops import LogAnalyzer
from isrms_intel.red_team import AdversarySimulator

__all__ = [
    "BayesianScenarioAnalyzer",
    "MobilizationIndicatorTracker",
    "LogAnalyzer",
    "AdversarySimulator",
]
