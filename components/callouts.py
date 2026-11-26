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
    with st.expander("🔬 **Spatial Prediction Layer Status (Why continuous heatmap interpolation is withheld)**", expanded=False):
        st.markdown("""
        **Investigation Findings on `rf_mapping_model.joblib`:**
        - **Evaluation Deflation via Spatial Leave-One-Station-Out Validation**: While standard temporal evaluation on known station locations indicated $R^2 = 0.59$, rigorous **Leave-One-Station-Out Cross-Validation (LOSO-CV)** revealed an overall $R^2 = 0.022$ and severely negative $R^2$ values for individual stations (e.g., Pimpri: $R^2 = -8.79$, Saswad: $R^2 = -3.14$, Kamatwadi-Walha: $R^2 = -1.13$).
        - **Data Density Limitation**: With only 11 monitoring stations across an approximate study area of $\\sim 2,936\\text{ km}^2$ (a rough spatial average of approximately 1 monitoring station per $267\\text{ km}^2$), decision tree ensembles with raw latitude and longitude memorize coordinates rather than learning transferable spatial physical relationships.
        - **Spatial Heterogeneity in Hard-Rock Terrain**: Groundwater distribution in regional hard-rock terrain can be highly heterogeneous across short distances due to localized sub-surface variations. Water levels cannot be reliably interpolated between sparse stations without site-specific lithological logs, digital elevation models (DEM), and fine-scale geomorphic covariates.
        - **Integrity Decision**: To prevent presenting unvalidated or misleading spatial heatmaps as scientific predictions, the map displays verified station observations only until adequate spatial covariates and denser sensor networks are integrated.
        """)


def render_cqr_calibration_expander() -> None:
    """Render findings on prediction intervals and conformal prediction trade-offs."""
    with st.expander("📐 **Prediction Interval Calibration & Conformal Prediction Analysis**", expanded=False):
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


def render_forecast_methodology_expander() -> None:
    """Render comprehensive scientific and methodological explanation covering next-observation targets,
    irregular intervals, MBGL interpretation, uncertainty undercoverage, and sensitivity simulation limitations.
    """
    with st.expander("🔬 **Scientific & Methodological Notes (Prediction Design & Scope)**", expanded=False):
        st.markdown("""
        ### 1. Next-Recorded-Observation Prediction Target
        - **Target Specification**: The Random Forest forecasting model predicts the water level at the **next recorded CGWB monitoring event** for a given station, rather than predicting a fixed temporal horizon (such as exactly 30, 60, or 90 calendar days into the future).
        - **Target Variable**: Formulated as $y_t = \\text{gw\\_level\\_next}$, which pairs each historical observation with the depth measured during the subsequent scheduled monitoring round at that specific well.

        ### 2. Irregular Historical Observation Intervals
        - **Survey Cadence**: Central Ground Water Board (CGWB) monitoring rounds in Maharashtra historically targeted quarterly seasonal soundings (roughly May pre-monsoon, August mid-monsoon, November post-monsoon, and January rabi-season). However, physical field surveys occur on irregular calendar dates.
        - **Held-Out Test Horizon (2018–2023, $n=124$)**: Survey intervals range between **41 days and 233 days**, with a **median of 92.0 days** and a **mean of 109.4 days**.
        - **Full Historical Range (1996–2023, $n=658$)**: Across the full multi-decadal record, intervals range from **41 days to 2,206 days** (e.g., Zendewadi's 6.0-year observation gap between 2016 and 2022), with an overall median of **102.0 days** and mean of **106.9 days**.

        ### 3. Meters Below Ground Level (MBGL) Physical Interpretation
        - **Depth Convention**: All groundwater depths are recorded in **Meters Below Ground Level (MBGL)**, where 0.0 m denotes the ground surface.
        - **Directionality**: 
          - **Higher MBGL value** indicates a **deeper water table** (water level has fallen; aquifer depletion/drawdown).
          - **Lower MBGL value** indicates a **shallower water table** (water level has risen closer to the surface; aquifer replenishment/recharge).
          - A **negative difference** ($\\text{Next} - \\text{Current} < 0$) signifies a **water-table rise (shallower)**.

        ### 4. Experimental Uncertainty Intervals & Empirical Undercoverage
        - **Model Architecture**: Prediction intervals are generated by Gradient Boosting quantile regressors trained on the 10th percentile (`q10`) and 90th percentile (`q90`), targeting a **nominal 80% coverage interval**.
        - **Observed Undercoverage**: Evaluated on the held-out test split (2018–2023), empirical test coverage is **57.26%**, representing an out-of-sample miss rate of **42.74%**. The measured average prediction interval width is **4.36 m**.
        - **Scientific Honesty**: We do **not** claim this to be a calibrated 80% confidence interval. It is presented strictly as an uncalibrated experimental uncertainty estimate reflecting the substantial residual variance in hard-rock basaltic hydrogeology.

        ### 5. Hypothetical Antecedent Rainfall Scaling
        - **Simulation Nature**: The rainfall sensitivity slider applies uniform proportional adjustments ($-50\\%$ to $+50\\%$) to antecedent cumulative rainfall features (`rain_30d`, `rain_90d`, `rain_180d`, `rain_365d`).
        - **Exploratory Purpose**: This simulation serves to probe model feature responsiveness under synthetic drought or above-average monsoon conditions.
        - **Important Limitation**: This is a **hypothetical sensitivity experiment**, not an operational weather forecast. It does not account for rainfall intensity, runoff thresholds, soil-moisture retention curves, or nonlinear fractured-basalt infiltration physics.

        ### 6. Research Prototype Scope & Operational Boundaries
        - **Non-Operational Status**: BhujalDrishti is a research decision-support prototype developed for Purandar Taluka, Maharashtra.
        - **Manual vs Live Telemetry**: Outputs are statistical machine learning estimates derived from historical manual tape soundings and gridded IMD rainfall data, **not real-time automated telemetry**.
        - **Field Validation**: Model outputs should not be used as sole justifications for engineering civil works or water-allocation mandates without on-site hydrogeological verification and local pump test data.
        """)


def render_decision_support_advisory_notice() -> None:
    """Render decision-support advisory notice with explicit physical reference tier and historical context."""
    st.markdown(
        """
        <div class="info-callout">
            <b>Decision-Support Advisory Notice</b>: Interventions presented below are project-defined hydrogeological heuristics based on standard watershed conservation practices, not official Central Ground Water Board (CGWB) or Ground Water Surveys and Development Agency (GSDA) statutory directives. Depth tiers (&lt; 4.0 m, 4.0–8.0 m, &gt; 8.0 m MBGL) are <b>project-defined physical depth categories, not official CGWB vulnerability or groundwater safety classifications</b>. Furthermore, advisories are formulated from each station's <b>latest available historical observation</b> recorded in the dataset, not current real-time groundwater conditions. They represent preliminary decision-support heuristics, <b>not validated site-specific engineering designs</b>. All structural interventions require detailed on-site hydrogeological, geophysical, and civil surveys prior to construction.
        </div>
        """,
        unsafe_allow_html=True
    )
