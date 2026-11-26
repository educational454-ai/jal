"""Reusable KPI and metric card components for BhujalDrishti."""
import textwrap
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


def render_overview_kpis(
    station_count: int = 11,
    total_records: int = 680,
    coverage_km2: str = "~2,936 km²",
    avg_mbgl: float = None,
    rf_mae: float = None
) -> None:
    """Render the primary 3-column overview project snapshot KPI grid."""
    k1, k2, k3 = st.columns(3)
    with k1:
        render_kpi_card(
            label="Observation Stations",
            value=f"{station_count} Stations",
            caption=f"CGWB monitoring network in Purandar (1996–2023; 9 eligible for forecasting with ≥10 obs)."
        )
    with k2:
        render_kpi_card(
            label="Historical Observations",
            value=f"{total_records} Soundings",
            caption="Quality-verified manual tape depth soundings (1996–2023; discrete historical surveys)."
        )
    with k3:
        render_kpi_card(
            label="Study Area Coverage",
            value=f"{coverage_km2}",
            caption="Purandar Taluka, Maharashtra (~1 monitoring station per 267 km²; coarse network)."
        )


def render_depth_distribution_summary(shallow_count: int, moderate_count: int, deep_count: int, total_count: int) -> None:
    """Render a compact, elegant depth distribution breakdown card with segmented progress bar."""
    pct_shallow = (shallow_count / total_count * 100) if total_count else 0
    pct_moderate = (moderate_count / total_count * 100) if total_count else 0
    pct_deep = (deep_count / total_count * 100) if total_count else 0

    card_html = textwrap.dedent(f"""
    <div class="depth-dist-card">
        <div class="depth-dist-header">
            <span class="depth-dist-title">Current Depth Stratification</span>
            <span class="depth-dist-subtitle">Latest observation per station ({total_count} wells)</span>
        </div>
        <div class="depth-dist-bar-track">
            <div class="depth-dist-bar-seg seg-shallow" style="width: {pct_shallow:.1f}%;" title="Shallow: {shallow_count} ({pct_shallow:.1f}%)"></div>
            <div class="depth-dist-bar-seg seg-moderate" style="width: {pct_moderate:.1f}%;" title="Moderate: {moderate_count} ({pct_moderate:.1f}%)"></div>
            <div class="depth-dist-bar-seg seg-deep" style="width: {pct_deep:.1f}%;" title="Deep: {deep_count} ({pct_deep:.1f}%)"></div>
        </div>
        <div class="depth-dist-rows">
            <div class="depth-dist-row">
                <div class="depth-dist-cat">
                    <span class="depth-dist-dot dot-shallow"></span>
                    <span class="depth-dist-name">Shallow (&lt; 4.0 m MBGL)</span>
                </div>
                <div class="depth-dist-val">
                    <span class="depth-dist-count">{shallow_count} wells</span>
                    <span class="depth-dist-pct">({pct_shallow:.1f}%)</span>
                </div>
            </div>
            <div class="depth-dist-row">
                <div class="depth-dist-cat">
                    <span class="depth-dist-dot dot-moderate"></span>
                    <span class="depth-dist-name">Moderate (4.0–8.0 m MBGL)</span>
                </div>
                <div class="depth-dist-val">
                    <span class="depth-dist-count">{moderate_count} wells</span>
                    <span class="depth-dist-pct">({pct_moderate:.1f}%)</span>
                </div>
            </div>
            <div class="depth-dist-row">
                <div class="depth-dist-cat">
                    <span class="depth-dist-dot dot-deep"></span>
                    <span class="depth-dist-name">Deep (&gt; 8.0 m MBGL)</span>
                </div>
                <div class="depth-dist-val">
                    <span class="depth-dist-count">{deep_count} wells</span>
                    <span class="depth-dist-pct">({pct_deep:.1f}%)</span>
                </div>
            </div>
        </div>
        <div class="depth-dist-note">
            ℹ️ Depth bands are project-defined reference ranges, not official CGWB groundwater-status classifications.
        </div>
    </div>
    """).strip()

    st.markdown(card_html, unsafe_allow_html=True)


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
                                  emp_cov: float, avg_width: float,
                                  pers_r2: float = -0.233) -> None:
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
                        • R²: <b>{pers_r2:.3f}</b><br>
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
