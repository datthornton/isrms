"""Security Strategy Effectiveness – Streamlit Module

Models and visualises the effectiveness of a security strategy across
functional coverage domains. Uses a Monte Carlo approach to quantify
uncertainty in strategy effectiveness estimates.

Key concepts:
- Security domains: Physical, Cyber, Personnel, Operational
- Coverage score: fraction of domain requirements met
- Effectiveness simulation: PERT-sampled coverage × domain weight

Migrated from: Security Strategy/streamlit_module.py
Changes from original:
- Removed hardcoded Windows paths
- Added type hints, dataclasses, and full docstrings
- Monte Carlo effectiveness simulation using PERT distributions
- Refactored Streamlit UI into callable render function
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Optional

import numpy as np

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Domain definitions
# ---------------------------------------------------------------------------

SECURITY_DOMAINS: dict[str, dict] = {
    "PHYSICAL": {
        "name": "Physical Security",
        "description": "Perimeter, access control, barriers, and surveillance.",
        "weight": 0.30,
        "sub_domains": [
            "Perimeter Protection",
            "Access Control Systems",
            "Video Surveillance",
            "Intrusion Detection",
            "Security Lighting",
            "Barriers & Bollards",
        ],
    },
    "PERSONNEL": {
        "name": "Personnel Security",
        "description": "Screening, training, and insider threat mitigation.",
        "weight": 0.25,
        "sub_domains": [
            "Background Screening",
            "Security Awareness Training",
            "Insider Threat Program",
            "Visitor Management",
            "Contractor Vetting",
        ],
    },
    "OPERATIONAL": {
        "name": "Operational Security",
        "description": "Policies, procedures, incident response, and drills.",
        "weight": 0.25,
        "sub_domains": [
            "Security Policies & Procedures",
            "Incident Response Plan",
            "Drills & Exercises",
            "Security Risk Assessments",
            "Intelligence Collection",
        ],
    },
    "INFORMATION": {
        "name": "Information Security",
        "description": "Cyber security, data protection, and information sharing.",
        "weight": 0.20,
        "sub_domains": [
            "Cyber Threat Detection",
            "Data Loss Prevention",
            "Network Segmentation",
            "Patch Management",
            "Security Information Sharing",
        ],
    },
}


# ---------------------------------------------------------------------------
# Data models
# ---------------------------------------------------------------------------

@dataclass
class SecurityMeasure:
    """A single security measure within a domain.

    Parameters
    ----------
    measure_id : str
        Unique identifier.
    domain_id : str
        Parent domain (key in :data:`SECURITY_DOMAINS`).
    sub_domain : str
        Sub-domain within the parent domain.
    name : str
        Human-readable name.
    implemented : bool
        Whether the measure is currently in place.
    effectiveness_min : float
        Minimum effectiveness fraction (0–1).
    effectiveness_mode : float
        Most-likely effectiveness fraction.
    effectiveness_max : float
        Maximum effectiveness fraction.
    annual_cost : float
        Annual cost of the measure ($).
    """

    measure_id: str
    domain_id: str
    sub_domain: str
    name: str
    implemented: bool = False
    effectiveness_min: float = 0.5
    effectiveness_mode: float = 0.7
    effectiveness_max: float = 0.9
    annual_cost: float = 0.0
    notes: str = ""


@dataclass
class DomainAssessment:
    """Assessment result for a single security domain."""

    domain_id: str
    domain_name: str
    coverage_score: float  # Fraction of sub-domains with measures
    effectiveness_mean: float
    effectiveness_p90: float
    n_measures_implemented: int
    n_sub_domains_covered: int
    total_sub_domains: int
    annual_cost: float


@dataclass
class StrategyAssessment:
    """Overall security strategy assessment.

    Attributes
    ----------
    facility_id : str
        Facility identifier.
    overall_score : float
        Weighted aggregate strategy effectiveness score (0–1).
    maturity_level : str
        Qualitative maturity label.
    domain_assessments : list[DomainAssessment]
        Per-domain results.
    total_annual_cost : float
        Total annual cost of implemented measures ($).
    gaps : list[str]
        Identified coverage gaps.
    """

    facility_id: str
    overall_score: float
    maturity_level: str
    domain_assessments: list[DomainAssessment]
    total_annual_cost: float
    gaps: list[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _pert_samples(
    minimum: float,
    mode: float,
    maximum: float,
    n: int,
    rng: np.random.Generator,
) -> np.ndarray:
    """Draw *n* PERT samples."""
    if minimum >= maximum:
        return np.full(n, mode)
    mean = (minimum + 4.0 * mode + maximum) / 6.0
    alpha = 6.0 * (mean - minimum) / (maximum - minimum)
    beta_ = 6.0 * (maximum - mean) / (maximum - minimum)
    alpha = max(alpha, 1e-6)
    beta_ = max(beta_, 1e-6)
    raw = rng.beta(alpha, beta_, size=n)
    return minimum + raw * (maximum - minimum)


def _maturity_label(score: float) -> str:
    """Convert a 0–1 score to a maturity label."""
    if score >= 0.85:
        return "Optimized"
    elif score >= 0.70:
        return "Defined"
    elif score >= 0.50:
        return "Managed"
    elif score >= 0.30:
        return "Developing"
    else:
        return "Initial"


# ---------------------------------------------------------------------------
# Public assessment function
# ---------------------------------------------------------------------------

def run_strategy_assessment(
    facility_id: str,
    measures: list[SecurityMeasure],
    n_simulations: int = 10_000,
    seed: Optional[int] = None,
) -> StrategyAssessment:
    """Run a Monte Carlo strategy effectiveness assessment.

    For each security domain:
    1. Identify implemented measures.
    2. Sample effectiveness from PERT distributions.
    3. Compute coverage and weighted effectiveness scores.

    Parameters
    ----------
    facility_id : str
        Facility identifier.
    measures : list[SecurityMeasure]
        Security measures to assess (all domains combined).
    n_simulations : int
        Monte Carlo iterations for effectiveness sampling.
    seed : int, optional
        Random seed for reproducibility.

    Returns
    -------
    StrategyAssessment
        Full strategy assessment result.
    """
    rng = np.random.default_rng(seed)
    domain_assessments: list[DomainAssessment] = []
    total_weighted_score = 0.0
    total_cost = sum(m.annual_cost for m in measures if m.implemented)
    gaps: list[str] = []

    for domain_id, domain_def in SECURITY_DOMAINS.items():
        domain_measures = [m for m in measures if m.domain_id == domain_id]
        implemented = [m for m in domain_measures if m.implemented]
        sub_domains_covered = {m.sub_domain for m in implemented}
        all_sub_domains = set(domain_def["sub_domains"])

        coverage = len(sub_domains_covered) / len(all_sub_domains) if all_sub_domains else 0.0

        if implemented:
            eff_samples = np.zeros(n_simulations)
            for m in implemented:
                s = _pert_samples(
                    m.effectiveness_min,
                    m.effectiveness_mode,
                    m.effectiveness_max,
                    n_simulations,
                    rng,
                )
                eff_samples += s / len(implemented)
            eff_mean = float(np.mean(eff_samples))
            eff_p90 = float(np.percentile(eff_samples, 90))
        else:
            eff_mean = 0.0
            eff_p90 = 0.0

        domain_cost = sum(m.annual_cost for m in implemented)
        domain_score = coverage * eff_mean * domain_def["weight"]
        total_weighted_score += domain_score

        uncovered = all_sub_domains - sub_domains_covered
        if uncovered:
            gaps.append(
                f"{domain_def['name']}: no measures for "
                + ", ".join(sorted(uncovered))
            )

        domain_assessments.append(
            DomainAssessment(
                domain_id=domain_id,
                domain_name=domain_def["name"],
                coverage_score=coverage,
                effectiveness_mean=eff_mean,
                effectiveness_p90=eff_p90,
                n_measures_implemented=len(implemented),
                n_sub_domains_covered=len(sub_domains_covered),
                total_sub_domains=len(all_sub_domains),
                annual_cost=domain_cost,
            )
        )

    overall_score = min(total_weighted_score, 1.0)

    return StrategyAssessment(
        facility_id=facility_id,
        overall_score=overall_score,
        maturity_level=_maturity_label(overall_score),
        domain_assessments=domain_assessments,
        total_annual_cost=total_cost,
        gaps=gaps,
    )


# ---------------------------------------------------------------------------
# Streamlit render function
# ---------------------------------------------------------------------------

def build_strategy_dashboard() -> None:
    """Render the Security Strategy Streamlit dashboard.

    Import and call this function from a Streamlit app entry-point.
    Requires ``streamlit`` to be installed.
    """
    try:
        import streamlit as st
        import plotly.graph_objects as go
        import pandas as pd
    except ImportError as exc:
        logger.error("Streamlit or Plotly not available: %s", exc)
        return

    st.set_page_config(
        page_title="IRMS Security Strategy",
        page_icon="🛡️",
        layout="wide",
    )

    st.title("Security Strategy Effectiveness Assessment")
    st.markdown(
        "Model the effectiveness of your security strategy across Physical, "
        "Personnel, Operational, and Information security domains."
    )

    facility_id = st.sidebar.text_input("Facility ID", value="FAC_001")
    n_sims = st.sidebar.number_input(
        "Monte Carlo Iterations", min_value=1_000, max_value=100_000, value=10_000, step=1_000
    )
    seed = st.sidebar.number_input("Random Seed", min_value=0, value=42)

    # -----------------------------------------------------------------------
    # Measure input
    # -----------------------------------------------------------------------
    st.subheader("Security Measures")

    measures: list[SecurityMeasure] = []
    for domain_id, domain_def in SECURITY_DOMAINS.items():
        with st.expander(f"📋 {domain_def['name']}", expanded=False):
            for sub in domain_def["sub_domains"]:
                col1, col2, col3 = st.columns([3, 1, 1])
                key_prefix = f"{domain_id}_{sub}".replace(" ", "_")
                implemented = col1.checkbox(sub, key=f"impl_{key_prefix}")
                eff_mode = col2.slider(
                    "Effectiveness",
                    0.0,
                    1.0,
                    0.70,
                    0.05,
                    key=f"eff_{key_prefix}",
                )
                cost = col3.number_input(
                    "Annual Cost ($)",
                    min_value=0.0,
                    value=5_000.0,
                    step=1_000.0,
                    key=f"cost_{key_prefix}",
                )
                measures.append(
                    SecurityMeasure(
                        measure_id=key_prefix,
                        domain_id=domain_id,
                        sub_domain=sub,
                        name=sub,
                        implemented=implemented,
                        effectiveness_min=max(0.0, eff_mode - 0.15),
                        effectiveness_mode=eff_mode,
                        effectiveness_max=min(1.0, eff_mode + 0.15),
                        annual_cost=cost if implemented else 0.0,
                    )
                )

    if st.button("▶ Run Assessment", type="primary"):
        with st.spinner("Running Monte Carlo assessment…"):
            result = run_strategy_assessment(
                facility_id=facility_id,
                measures=measures,
                n_simulations=int(n_sims),
                seed=int(seed),
            )

        # Metrics
        col1, col2, col3 = st.columns(3)
        col1.metric("Overall Score", f"{result.overall_score:.1%}")
        col2.metric("Maturity Level", result.maturity_level)
        col3.metric("Annual Cost", f"${result.total_annual_cost:,.0f}")

        # Domain radar chart
        domain_names = [da.domain_name for da in result.domain_assessments]
        coverage_scores = [da.coverage_score for da in result.domain_assessments]

        fig = go.Figure(
            data=go.Scatterpolar(
                r=coverage_scores + [coverage_scores[0]],
                theta=domain_names + [domain_names[0]],
                fill="toself",
                name="Coverage",
            )
        )
        fig.update_layout(
            polar={"radialaxis": {"visible": True, "range": [0, 1]}},
            title="Domain Coverage Radar",
            template="plotly_white",
        )
        st.plotly_chart(fig, use_container_width=True)

        # Gaps
        if result.gaps:
            st.subheader("⚠️ Coverage Gaps")
            for gap in result.gaps:
                st.warning(gap)
        else:
            st.success("No coverage gaps identified.")


if __name__ == "__main__":
    build_strategy_dashboard()
