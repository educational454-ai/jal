"""Reusable KPI and metric card components for BhujalDrishti."""
import streamlit as st


def render_kpi_card(label: str, value: str, caption: str) -> None:
    """Render a single premium KPI card."""
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-top">
                <div class="kpi-label">{label}</div>
                <div class="kpi-value">{value}</div>
            </div>
            <div class="kpi-caption">{caption}</div>
        </div>
        """,
        unsafe_allow_html=True
    )


def render_overview_kpis(avg_mbgl: float, station_count: int, total_records: int, rf_mae: float) -> None:
    """Render the primary 4-column overview KPI grid."""
    k1, k2, k3, k4 = st.columns(4)
    with k1:
        render_kpi_card(
            label="Mean Water Table Depth",
            value=f"{avg_mbgl:.2f} m",
            caption=f"Meters Below Ground Level (MBGL) across {station_count} stations at latest record."
        )
    with k2:
        render_kpi_card(
            label="Monitoring Network",
            value=f"{station_count} Wells",
            caption="Active CGWB in-situ manual monitoring stations (~1 well per 100 km²)."
        )
    with k3:
        render_kpi_card(
            label="Historical Time Series",
            value=f"{total_records} Records",
            caption="Quality-verified quarterly observations spanning 1996 through 2023."
        )
    with k4:
        render_kpi_card(
            label="Held-Out Model MAE",
            value=f"{rf_mae:.3f} m",
            caption="Random Forest next-observation forecast error on 2018–2023 test set (n=124)."
        )


def render_depth_distribution_bar(shallow_count: int, moderate_count: int, deep_count: int, total_count: int) -> None:
    """Render horizontal pill bar summarizing depth reference stratification."""
    st.markdown(
        f"""
        <div class="distribution-pill-bar">
            <span class="distribution-pill-label">Latest Observation Depth Distribution:</span>
            <div style="display: flex; gap: 10px; align-items: center; flex-wrap: wrap;">
                <span class="badge-shallow">Shallow (&lt; 4m): {shallow_count} / {total_count} wells</span>
                <span class="badge-moderate">Moderate (4–8m): {moderate_count} / {total_count} wells</span>
                <span class="badge-deep">Deep (&gt; 8m): {deep_count} / {total_count} wells</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


def render_evaluation_result_cards(rf_mae: float, rf_rmse: float, rf_r2: float,
                                  pers_mae: float, pers_rmse: float,
                                  emp_cov: float, avg_width: float) -> None:
    """Render the 3-column held-out evaluation summary cards."""
    err_reduction = ((pers_mae - rf_mae) / pers_mae) * 100.0 if pers_mae else 0.0
    m1, m2, m3 = st.columns(3)
    with m1:
        st.markdown(
            f"""
            <div class='metric-card'>
                <div class='metric-card-content'>
                    <div class='metric-card-title'>Random Forest Model</div>
                    <div class='metric-card-body'>
                        • MAE: <b>{rf_mae:.3f} m</b><br>
                        • RMSE: <b>{rf_rmse:.3f} m</b><br>
                        • R²: <b>{rf_r2:.3f}</b>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with m2:
        st.markdown(
            f"""
            <div class='metric-card'>
                <div class='metric-card-content'>
                    <div class='metric-card-title'>Persistence Baseline</div>
                    <div class='metric-card-body'>
                        • MAE: <b>{pers_mae:.3f} m</b><br>
                        • RMSE: <b>{pers_rmse:.3f} m</b><br>
                        • Error Reduction: <b>{err_reduction:.1f}%</b> lower MAE
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with m3:
        st.markdown(
            f"""
            <div class='metric-card'>
                <div class='metric-card-content'>
                    <div class='metric-card-title'>Uncalibrated q10–q90 Prediction Band</div>
                    <div class='metric-card-body'>
                        • Empirical Test Coverage: <b>{emp_cov:.2f}%</b><br>
                        • Nominal Target: 80.0% (Undercoverage)<br>
                        • Measured Average Width: <b>{avg_width:.2f} m</b>
                    </div>
                </div>
                <div class='metric-card-caveat' style='margin-top: 6px;'>
                    <span style='color: var(--badge-deep-text); font-size: 0.78rem;'>*Does not guarantee future coverage*</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
