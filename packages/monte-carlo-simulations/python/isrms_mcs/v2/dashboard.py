"""MCS Version 2 – Dashboard

Streamlit dashboard for the MCS v2 optimization engine. Displays:
- Bundle configuration inputs
- Optimization run results
- Pareto front visualisation
- Fitness convergence chart

Migrated from: MCS Simulation Version 2/mcs_v2_dashboard.py
Changes from original:
- Removed hardcoded Windows paths
- Uses isrms_mcs package imports
- Refactored into callable render function
"""

from __future__ import annotations

import logging

import plotly.graph_objects as go
import streamlit as st

from isrms_mcs.v2.config import SimulationConfig, BundleConfig, default_config
from isrms_mcs.v2.optimize import run_optimization

logger = logging.getLogger(__name__)


def render_mcs_v2_dashboard() -> None:
    """Render the MCS v2 Streamlit dashboard."""
    st.set_page_config(
        page_title="IRMS MCS v2 – Optimization",
        page_icon="⚙️",
        layout="wide",
    )

    st.title("IRMS Monte Carlo Simulation v2 – Bundle Optimization")
    st.markdown(
        "Configure mitigation bundles and run the genetic algorithm optimizer "
        "to find the best risk-reduction package within your budget."
    )

    # -----------------------------------------------------------------------
    # Sidebar: simulation parameters
    # -----------------------------------------------------------------------
    st.sidebar.header("Simulation Parameters")

    run_id = st.sidebar.text_input("Run ID", value="mcs_v2_run_1")
    budget = st.sidebar.number_input(
        "Budget Constraint ($)", min_value=0.0, value=500_000.0, step=10_000.0
    )
    risk_target = st.sidebar.slider(
        "Risk Reduction Target", min_value=0.0, max_value=1.0, value=0.40, step=0.05
    )
    n_gen = st.sidebar.number_input("GA Generations", min_value=10, value=50, step=10)
    pop_size = st.sidebar.number_input(
        "Population Size", min_value=10, value=30, step=5
    )
    seed = st.sidebar.number_input("Random Seed", min_value=0, value=42)

    # -----------------------------------------------------------------------
    # Bundle configuration
    # -----------------------------------------------------------------------
    st.subheader("Bundle Configuration")
    st.markdown("Define mitigation bundles to evaluate in the optimizer.")

    n_bundles = st.number_input("Number of Bundles", min_value=1, max_value=20, value=3)

    bundles: list[BundleConfig] = []
    for i in range(int(n_bundles)):
        with st.expander(f"Bundle {i + 1}", expanded=(i == 0)):
            col1, col2, col3 = st.columns(3)
            b_id = col1.text_input(f"Bundle ID", value=f"BUNDLE_{i + 1:02d}", key=f"bid_{i}")
            b_name = col2.text_input(f"Name", value=f"Mitigation Bundle {i + 1}", key=f"bname_{i}")
            b_cost = col3.number_input(
                "Annual Cost ($)", min_value=0.0, value=50_000.0 * (i + 1), key=f"bcost_{i}"
            )
            b_rr = st.slider(
                "Expected Risk Reduction",
                min_value=0.0,
                max_value=1.0,
                value=min(0.10 * (i + 1), 0.50),
                step=0.01,
                key=f"brr_{i}",
            )
            bundles.append(
                BundleConfig(
                    bundle_id=b_id,
                    name=b_name,
                    measures=[],
                    estimated_cost=b_cost,
                    expected_risk_reduction=b_rr,
                )
            )

    # -----------------------------------------------------------------------
    # Run optimization
    # -----------------------------------------------------------------------
    if st.button("▶ Run Optimization", type="primary"):
        config = SimulationConfig(
            run_id=run_id,
            budget_constraint=budget,
            risk_target=risk_target,
            n_generations=int(n_gen),
            population_size=int(pop_size),
            seed=int(seed),
            bundles=bundles,
        )

        with st.spinner("Running genetic algorithm…"):
            result = run_optimization(config)

        st.success(
            f"Optimization complete! Best solution: "
            f"{len(result.best_bundle_ids)} bundles selected, "
            f"cost=${result.best_cost:,.0f}, "
            f"risk reduction={result.best_risk_reduction:.1%}"
        )

        # Metrics
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Bundles Selected", len(result.best_bundle_ids))
        col2.metric("Total Cost", f"${result.best_cost:,.0f}")
        col3.metric("Risk Reduction", f"{result.best_risk_reduction:.1%}")
        col4.metric("Feasible", "✅ Yes" if result.feasible else "❌ No")

        # Fitness convergence
        if result.fitness_history:
            fig_fitness = go.Figure(
                data=[
                    go.Scatter(
                        y=result.fitness_history,
                        mode="lines",
                        name="Best Fitness",
                        line={"color": "royalblue"},
                    )
                ]
            )
            fig_fitness.update_layout(
                title="GA Fitness Convergence",
                xaxis_title="Generation",
                yaxis_title="Best Fitness",
                template="plotly_white",
            )
            st.plotly_chart(fig_fitness, use_container_width=True)

        # Pareto front
        if result.pareto_front:
            costs = [p["cost"] for p in result.pareto_front]
            reductions = [p["risk_reduction"] for p in result.pareto_front]
            fig_pareto = go.Figure(
                data=[
                    go.Scatter(
                        x=costs,
                        y=reductions,
                        mode="markers+lines",
                        name="Pareto Front",
                        marker={"size": 8, "color": "tomato"},
                    )
                ]
            )
            fig_pareto.update_layout(
                title="Cost–Risk Reduction Pareto Front",
                xaxis_title="Total Cost ($)",
                yaxis_title="Risk Reduction",
                template="plotly_white",
            )
            st.plotly_chart(fig_pareto, use_container_width=True)


if __name__ == "__main__":
    render_mcs_v2_dashboard()
