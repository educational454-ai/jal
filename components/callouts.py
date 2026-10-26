"""Reusable informational, warning, and methodology callout components."""
import streamlit as st


def render_depth_tier_note() -> None:
    """Render notice distinguishing project-defined physical tiers from official CGWB classifications."""
    st.markdown(
        """
        <div class="info-callout">
            <b>Depth Reference Tier Classification Note</b>: Tiers displayed above (&lt;4.0 m, 4.0–8.0 m, &gt;8.0 m) represent project-defined physical reference bands for instantaneous telemetry visualization. They do not constitute official Central Ground Water Board (CGWB) groundwater exploitation categories. Official CGWB administrative categorizations (Safe, Semi-Critical, Critical, Over-Exploited) are assessed at the entire taluka level based on annual groundwater extraction versus annual replenishable recharge budgets, not single-well point measurements.
        </div>
        """,
        unsafe_allow_html=True
    )


def render_forecast_mbgl_info() -> None:
    """Render educational context on MBGL water depth and statistical nature of predictions."""
    st.markdown(
        """
        <div class="info-callout" style="border-left-color: var(--blue-accent);">
            <b>Understanding Groundwater Measurements (MBGL)</b>: Water levels are measured in <b>Meters Below Ground Level (MBGL)</b>. A lower value (e.g., 2.5 m) means water is close to the surface, while a higher value (e.g., 10.5 m) indicates a deeper water table.<br>
            <span style="color: var(--callout-text-secondary); font-size: 0.83rem;">
            <b>Note</b>: Forecasts displayed here are statistical machine-learning estimates based on antecedent rainfall and prior water levels, not actual future physical measurements.
            </span>
        </div>
        """,
        unsafe_allow_html=True
    )


def render_horizon_callout(test_h: dict, overall_h: dict) -> None:
    """Render explicit forecast horizon reconciliation callout."""
    st.markdown(
        f"""
        <div class="info-callout" style="border-left-color: var(--blue-accent);">
            <b>Evaluation Population Forecast Horizon</b> (Held-out test set, 2018–2023, <i>n</i> = 124):<br>
            • <b>Median:</b> {test_h['median_days']:.1f} days &nbsp;|&nbsp; 
            • <b>Mean:</b> {test_h['mean_days']:.1f} days &nbsp;|&nbsp; 
            • <b>Min:</b> {test_h['min_days']:.1f} days &nbsp;|&nbsp; 
            • <b>Max:</b> {test_h['max_days']:.1f} days<br>
            <span style="color: var(--callout-text-secondary); font-size: 0.81rem;">
            *Predicts the next recorded CGWB observation date, not groundwater exactly 90 days in the future. For comparison, full historical population (1996–2023, n=658): Median = {overall_h['median_days']:.1f}d, Mean = {overall_h['mean_days']:.1f}d, Min = {overall_h['min_days']:.1f}d, Max = {overall_h['max_days']:.1f}d.*
            </span>
        </div>
        """,
        unsafe_allow_html=True
    )


def render_spatial_model_status_expander() -> None:
    """Render research findings on spatial interpolation and LOSO-CV."""
    with st.expander("🔬 **Spatial Prediction Layer Status (Why continuous heatmap interpolation is withheld)**"):
        st.markdown("""
        **Investigation Findings on `rf_mapping_model.joblib`:**
        - **Evaluation Deflation via Spatial Leave-One-Station-Out Validation**: While standard temporal evaluation on known station locations indicated $R^2 = 0.59$, rigorous **Leave-One-Station-Out Cross-Validation (LOSO-CV)** revealed an overall $R^2 = 0.022$ and severely negative $R^2$ values for individual stations (e.g., Pimpri: $R^2 = -8.79$, Saswad: $R^2 = -3.14$, Kamatwadi-Walha: $R^2 = -1.13$).
        - **Data Density Limitation**: With only 11 monitoring stations across $\\sim 1,105\\text{ km}^2$ (~1 well per $100\\text{ km}^2$), decision tree ensembles with raw latitude and longitude memorize coordinates rather than learning transferable spatial physical relationships.
        - **Basaltic Hydrogeology**: Groundwater in Deccan basalt flows is compartmentalized by fractured zones, compact massive basalt layers, weathered vesicular horizons, and lineaments that cannot be reliably interpolated without fine-scale digital elevation models (DEM), lithological logs, and geomorphic slope covariates.
        - **Integrity Decision**: To prevent presenting unvalidated or misleading spatial heatmaps as scientific predictions, the map displays verified station observations only until adequate spatial covariates and denser sensor networks are integrated.
        """)


def render_cqr_calibration_expander() -> None:
    """Render findings on prediction intervals and conformal prediction trade-offs."""
    with st.expander("📐 **Prediction Interval Calibration & Conformal Prediction Analysis**"):
        st.markdown("""
        **Uncalibrated Quantile Model Status:**
        - The current `q10` and `q90` Gradient Boosting models target nominal 80% coverage (10th to 90th percentiles).
        - On held-out test data (2018–2023, $n=124$), empirical coverage is **57.26%** (a **42.74% miss rate**), confirming significant out-of-sample undercoverage.
        - Measured average prediction interval width is **4.36 m**.
        
        **Conformalized Quantile Regression (CQR) Calibration Investigation:**
        - Investigated using an independent chronological calibration period (2014–2017) without tuning against the 2018–2023 test set:
          - A nonconformity score adjustment $Q = 1.543\\text{ m}$ was calculated on 97 calibration events.
          - Applying this adjustment achieved **85.5% empirical coverage** on the 2018–2023 test set, widening the average prediction interval from $4.04\\text{ m}$ to $7.13\\text{ m}$.
          
        **Assumptions & Limitations of Conformal Prediction in Hydrogeology:**
        1. **Exchangeability Violation**: Standard conformal prediction assumes exchangeable (i.i.d.) data. Time-series groundwater levels exhibit strong autocorrelation and non-stationary distribution shifts (e.g. changing multi-year rainfall regimes, expanding borewell extraction). Conformal prediction does not guarantee $\\ge 80\\%$ coverage on every future dataset when distribution shifts occur.
        2. **Interval Width Trade-off**: Achieving empirical coverage above $80\\%$ required widening the average interval to $\\sim 7.1\\text{ m}$, which spans most of the typical dynamic range of local shallow dugwells, limiting actionable decision utility.
        3. **Academic Baseline**: We retain the uncalibrated `q10`–`q90` model, clearly report its 57.3% measured test coverage and 4.36 m width, and explicitly state that calibration remains an unresolved research topic.
        """)


def render_decision_support_advisory_notice() -> None:
    """Render decision-support advisory notice."""
    st.markdown(
        """
        <div class="info-callout">
            <b>Decision-Support Advisory Notice</b>: Interventions presented below are rule-based hydrogeological guidelines synthesized from standard Central Ground Water Board (CGWB) and Groundwater Surveys and Development Agency (GSDA) watershed conservation handbooks. They represent preliminary decision-support heuristics, <b>not validated site-specific engineering designs</b>. All structural interventions require detailed on-site hydrogeological, geophysical, and civil surveys prior to construction.
        </div>
        """,
        unsafe_allow_html=True
    )
