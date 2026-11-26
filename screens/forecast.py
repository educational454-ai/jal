"""Next-Observation Forecasting screen implementation for BhujalDrishti."""
import pandas as pd
import streamlit as st

from services.data_loader import get_status
from services.model_service import predict_next_observation
from services.metrics_service import get_model_metrics, get_uncertainty_metrics, get_horizon_stats
from components.metric_cards import render_evaluation_result_cards
from components.charts import render_station_history_chart
from components.callouts import (
    render_forecast_mbgl_info,
    render_horizon_callout,
    render_forecast_methodology_expander,
    render_cqr_calibration_expander,
)
from styles.theme import get_current_theme


def render_forecast_screen(df: pd.DataFrame, models: dict) -> None:
    """Render Screen 3: Next-Observation Forecast."""
    active_theme = get_current_theme()

    # 1. Welcome & High-Level Introduction Card
    st.markdown("""
    <div class="forecast-welcome-card">
        <div class="forecast-welcome-eyebrow">Machine Learning Prediction · Purandar Taluka, Maharashtra</div>
        <div class="forecast-welcome-title">Next-Observation Groundwater Forecast</div>
        <div class="forecast-welcome-desc">
            This module forecasts the expected groundwater depth (m MBGL) at the <b>next recorded Central Ground Water Board (CGWB) monitoring survey</b> 
            for an eligible monitoring well. Predictions are generated using historical depth soundings, antecedent precipitation lookbacks, and seasonal indicators.
            <div style="margin-top: 10px; padding-top: 8px; border-top: 1px solid var(--border-color); font-size: 0.83rem; color: var(--callout-text-secondary, var(--text-secondary));">
                ⚠️ <b>Temporal Horizon Notice:</b> This model predicts the next discrete observation event when physical manual soundings occur. 
                It is <b>NOT necessarily a fixed 90-day forecast</b>, nor is it a live or continuous real-time groundwater prediction.
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 2. Prominent Station Selection Toolbar
    valid_stations = [s for s in df['station'].unique() if (df['station'] == s).sum() >= 10]
    station_sel = st.selectbox(
        "Select Monitoring Station for Forecast", 
        sorted(valid_stations), 
        index=0,
        key="forecast_station_select",
        help="Select an eligible CGWB monitoring station to view latest conditions, simulate rainfall scenarios, and inspect machine learning forecasts."
    )
    st.caption("ℹ️ *Station Eligibility: 9 of the 11 CGWB monitoring stations in Purandar Taluka are available for forecasting because the other 2 stations have fewer than 10 historical groundwater observations. These 2 stations remain fully included in the project's historical monitoring and geospatial map data; they are only excluded from this forecast selector.*")
    
    station_df = df[df['station'] == station_sel].sort_values('date').copy()
    latest_record = station_df.iloc[-1]

    # Read current hypothetical rainfall factor from session state
    if "forecast_rain_slider" not in st.session_state:
        st.session_state["forecast_rain_slider"] = 0
    rain_factor = int(st.session_state["forecast_rain_slider"])

    if 'forecast' in models and 'q10' in models and 'q90' in models and 'metadata' in models:
        meta = models['metadata']
        
        # A. Baseline point estimate and prediction interval (0% adjustment)
        base_results = predict_next_observation(models, latest_record, rain_factor=0)
        pred_val = float(base_results['pred_val'])
        lower_b = float(base_results['lower_b'])
        upper_b = float(base_results['upper_b'])
        unc_width = upper_b - lower_b
        
        # B. Simulated hypothetical scenario prediction (slider adjustment)
        scen_results = predict_next_observation(models, latest_record, rain_factor=rain_factor)
        scen_val = float(scen_results['pred_val'])
        
        # Exact evaluation metrics from metadata
        model_metrics = get_model_metrics(meta)
        unc_metrics = get_uncertainty_metrics(meta)
        horizon_stats = get_horizon_stats(meta)
        
        emp_cov = float(unc_metrics['coverage_pct'])
        avg_width = float(unc_metrics['average_width_m'])
        test_h = horizon_stats['test']
        overall_h = horizon_stats['overall']
        
        # Current station telemetry details
        current_mbgl = float(latest_record['gw_level_mbgl'])
        latest_date = pd.to_datetime(latest_record['date'])
        
        # Estimated forecast horizon based on held-out test median
        median_days = int(test_h['median_days'])
        est_pred_date = latest_date + pd.Timedelta(days=median_days)
        
        # Predicted direction of change vs current observation
        diff_val = pred_val - current_mbgl
        if diff_val > 0.05:
            direction_name = "Deeper (water table falls)"
            delta_pill = f'<span class="forecast-delta-pill forecast-delta-deeper">↑ +{diff_val:.2f} m (Deeper)</span>'
            narrative = (
                f"The model forecasts that at the next recorded survey, the water table at <b>{station_sel}</b> will be approximately "
                f"<b>{pred_val:.2f} m MBGL</b>. Compared to the last historical sounding of {current_mbgl:.2f} m MBGL recorded on {latest_date.strftime('%d-%b-%Y')}, "
                f"the water table is predicted to <b>deepen by +{diff_val:.2f} m</b> (water level falls)."
            )
        elif diff_val < -0.05:
            direction_name = "Shallower (water table rises)"
            delta_pill = f'<span class="forecast-delta-pill forecast-delta-shallower">↓ {diff_val:.2f} m (Shallower)</span>'
            narrative = (
                f"The model forecasts that at the next recorded survey, the water table at <b>{station_sel}</b> will be approximately "
                f"<b>{pred_val:.2f} m MBGL</b>. Compared to the last historical sounding of {current_mbgl:.2f} m MBGL recorded on {latest_date.strftime('%d-%b-%Y')}, "
                f"the water table is predicted to <b>rise closer to the surface by {abs(diff_val):.2f} m</b> (water level ascends)."
            )
        else:
            direction_name = "Approximately Stable (±0.05 m)"
            delta_pill = f'<span class="forecast-delta-pill" style="background-color: var(--bg-secondary); color: var(--text-secondary); border: 1px solid var(--border-color);">~ {diff_val:+.2f} m (Stable)</span>'
            narrative = (
                f"The model forecasts that at the next recorded survey, the water table at <b>{station_sel}</b> will be approximately "
                f"<b>{pred_val:.2f} m MBGL</b>, remaining approximately stable compared to the last historical sounding ({current_mbgl:.2f} m MBGL on {latest_date.strftime('%d-%b-%Y')})."
            )
            
        status, color, badge = get_status(pred_val)
        
        # 3. Visually Prominent Forecast Summary & Latest Known Conditions Card
        c_fc, c_cond = st.columns([1.6, 1.4])
        
        with c_fc:
            fc_html = f"""
            <div class="forecast-summary-card">
                <div>
                    <div class="forecast-card-eyebrow">Random Forest Point Estimate · Next CGWB Observation</div>
                    <div class="forecast-depth-display">
                        <span class="forecast-depth-val">{pred_val:.2f}</span>
                        <span class="forecast-depth-unit">m MBGL</span>
                        {delta_pill}
                    </div>
                    <div class="forecast-narrative">
                        {narrative}
                    </div>
                </div>
                <div class="forecast-meta-grid" style="margin-top: 14px;">
                    <div class="forecast-meta-item">
                        <span class="forecast-meta-label">Predicted Direction</span>
                        <span class="forecast-meta-value">{direction_name}</span>
                        <span class="forecast-meta-caption">Compared to {current_mbgl:.2f} m recorded on {latest_date.strftime('%d %b %Y')}</span>
                    </div>
                    <div class="forecast-meta-item">
                        <span class="forecast-meta-label">Estimated Depth Status</span>
                        <div><span class="{badge}" style="margin-top: 2px;">● {status}</span></div>
                        <span class="forecast-meta-caption">Project physical tier (Shallow: &lt; 4m, Moderate: 4–8m, Deep: &gt; 8m)</span>
                    </div>
                    <div class="forecast-meta-item">
                        <span class="forecast-meta-label">Forecast Horizon Context</span>
                        <span class="forecast-meta-value">~{median_days} days</span>
                        <span class="forecast-meta-caption">Illustrative date: ~{est_pred_date.strftime('%b %Y')} (calculated from test-set median observation interval of 92 days; not a station-specific survey schedule or model-predicted date)</span>
                    </div>
                    <div class="forecast-meta-item">
                        <span class="forecast-meta-label">Uncalibrated q10–q90 Band</span>
                        <span class="forecast-meta-value">{lower_b:.2f} m – {upper_b:.2f} m</span>
                        <span class="forecast-meta-caption">Nominal 80% interval · Test coverage: {emp_cov:.1f}%</span>
                    </div>
                </div>
            </div>
            """
            st.markdown(fc_html, unsafe_allow_html=True)
            
        with c_cond:
            is_extrap = bool(latest_record.get('is_rainfall_extrapolated', 0))
            extrap_pill = (
                '<div class="conditions-status-pill" style="background-color: rgba(245, 158, 11, 0.14); border: 1px solid var(--badge-moderate-border); color: var(--badge-moderate-text);">'
                '<span>⚠️</span><span>Outside 4-point IMD grid (lookback extrapolated)</span></div>'
            ) if is_extrap else (
                '<div class="conditions-status-pill" style="background-color: rgba(16, 185, 129, 0.14); border: 1px solid var(--badge-shallow-border); color: var(--badge-shallow-text);">'
                '<span>✓</span><span>Station within 4-point IMD grid coverage</span></div>'
            )
            
            cond_html = f"""
            <div class="conditions-card">
                <div>
                    <div class="conditions-card-title">Latest Recorded Station Telemetry</div>
                    <div class="conditions-card-sub">In-situ manual CGWB observation (Not live automated telemetry)</div>
                    <div class="conditions-row">
                        <span class="conditions-lbl">Station Name:</span>
                        <span class="conditions-val"><b>{station_sel}</b></span>
                    </div>
                    <div class="conditions-row">
                        <span class="conditions-lbl">Observation Date:</span>
                        <span class="conditions-val">{latest_date.strftime('%d %b %Y')}</span>
                    </div>
                    <div class="conditions-row">
                        <span class="conditions-lbl">Recorded Depth:</span>
                        <span class="conditions-val"><b>{current_mbgl:.2f} m</b> MBGL</span>
                    </div>
                    <div class="conditions-row">
                        <span class="conditions-lbl">Antecedent 90d Rain:</span>
                        <span class="conditions-val">{latest_record['rain_90d']:.1f} mm</span>
                    </div>
                    <div class="conditions-row">
                        <span class="conditions-lbl">Antecedent 365d Rain:</span>
                        <span class="conditions-val">{latest_record['rain_365d']:.1f} mm</span>
                    </div>
                </div>
                {extrap_pill}
            </div>
            """
            st.markdown(cond_html, unsafe_allow_html=True)

        st.markdown("<div style='height: 18px;'></div>", unsafe_allow_html=True)

        # 4. Organized Progressive Disclosure via Secondary Tabs
        tab_viz, tab_eval, tab_tech = st.tabs([
            "📈 Forecast Visualization & Scenarios",
            "📊 Model Evaluation & Baseline Comparison",
            "🔬 Research Methodology & Uncertainty Calibration"
        ])

        with tab_viz:
            # A. Historical Observations vs Predicted Chart
            st.subheader(f"Historical Observations & Next-Observation Forecast: {station_sel}")
            render_station_history_chart(
                station_df, 
                station_sel, 
                pred_val=pred_val, 
                lower_b=lower_b, 
                upper_b=upper_b, 
                pred_date=est_pred_date,
                scenario_val=scen_val,
                rain_factor=rain_factor,
                theme=active_theme
            )
            st.caption(
                f"ℹ️ *Inverted y-axis (top is shallower, bottom is deeper MBGL). Points depict discrete in-situ CGWB physical soundings. "
                f"The amber diamond denotes the model's next-observation point estimate ({pred_val:.2f} m MBGL) with its uncalibrated q10–q90 band "
                f"({lower_b:.2f} m to {upper_b:.2f} m). Note: The displayed approximate {est_pred_date.strftime('%B %Y')} event date is illustrative, "
                f"calculated using the overall held-out test-set median observation interval of 92 days; it is NOT a station-specific survey schedule "
                f"or a date predicted by the model. No continuous curve or monthly intermediate values are fabricated.*"
            )

            st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

            # B. Uncertainty Quantification Section
            st.subheader("Prediction Uncertainty: Uncalibrated q10–q90 Prediction Band")
            unc_html = f"""
            <div class="uncertainty-card">
                <div class="uncertainty-title">
                    <span>📐</span>
                    <span>Uncertainty Quantification for {station_sel} (Gradient Boosting Quantile Models)</span>
                </div>
                <div style="font-size: 0.84rem; color: var(--text-secondary); line-height: 1.5; margin-bottom: 12px;">
                    <b>Model Distinction & Uncertainty Range:</b> The Random Forest produces the point estimate, while separate Gradient Boosting Quantile Models (<tt>q10</tt> and <tt>q90</tt>) produce the q10–q90 prediction interval. 
                    Because groundwater fluctuates with localized weather and pumping, this interval represents the expected uncertainty envelope between the 10th and 90th percentiles.
                </div>
                <div class="uncertainty-grid">
                    <div>
                        <div class="uncertainty-item-lbl">Station Interval</div>
                        <div class="uncertainty-item-val" style="color: var(--earth-gold, #D99A45);">{lower_b:.2f} – {upper_b:.2f} m</div>
                        <div class="uncertainty-item-sub">Station range (q10 to q90)</div>
                    </div>
                    <div>
                        <div class="uncertainty-item-lbl">Station Interval Span</div>
                        <div class="uncertainty-item-val">{unc_width:.2f} m</div>
                        <div class="uncertainty-item-sub">Selected station width</div>
                    </div>
                    <div>
                        <div class="uncertainty-item-lbl">Empirical Test Coverage</div>
                        <div class="uncertainty-item-val" style="color: var(--badge-moderate-text);">{emp_cov:.2f}%</div>
                        <div class="uncertainty-item-sub">Target: 80% (Miss rate: {100.0 - emp_cov:.1f}%)</div>
                    </div>
                    <div>
                        <div class="uncertainty-item-lbl">Average Test Width</div>
                        <div class="uncertainty-item-val">{avg_width:.2f} m</div>
                        <div class="uncertainty-item-sub">Held-out test set mean</div>
                    </div>
                </div>
            </div>
            """
            st.markdown(unc_html, unsafe_allow_html=True)
            st.caption(
                "⚠️ *Important Scientific Clarification: The Random Forest produces the point estimate, while separate Gradient Boosting Quantile Models produce the q10–q90 interval. "
                "This interval is an experimental uncertainty estimate with observed undercoverage (57.26% test coverage vs 80.0% nominal target); "
                "it is NOT a calibrated 80% confidence interval. Actual model outputs are preserved without artificial widening.*"
            )

            st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

            # C. Rainfall What-If Sensitivity Simulator
            st.subheader("Rainfall What-If Analysis (Hypothetical Sensitivity Simulation)")
            st.markdown("""
            <div class="sensitivity-card">
                <div class="sensitivity-header">
                    <div class="sensitivity-title">Simulate Antecedent Rainfall Scenarios (-50% to +50%)</div>
                    <div class="sensitivity-sub">
                        Evaluate machine learning model responsiveness by applying uniform proportional scaling to antecedent cumulative rainfall features (30d, 90d, 180d, 365d). 
                        For example, setting the slider to -30% simulates a severe drought scenario, while +30% simulates a high-precipitation monsoon.
                    </div>
                    <div style="margin-top: 6px; font-size: 0.77rem; color: var(--callout-text-secondary, var(--text-secondary));">
                        ⚠️ <b>Sensitivity Experiment Distinction:</b> This is a mathematical what-if sensitivity experiment to inspect model behavior. It is <b>NOT an operational rainfall forecast or a weather forecast</b>, and does not provide a guarantee of physical aquifer recharge.
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            st.slider(
                "Hypothetical Rainfall Scaling Factor",
                min_value=-50,
                max_value=50,
                step=5,
                format="%d%%",
                key="forecast_rain_slider",
                help="Hypothetical sensitivity adjustment: scales antecedent 30d–365d cumulative rainfall features to simulate drought (-30%) or wet (+30%) conditions. Note: this is a sensitivity simulation, not a weather forecast."
            )

            # Side-by-side scenario comparison cards
            scen_delta = scen_val - pred_val
            if scen_delta > 0.05:
                scen_dir = f"+{scen_delta:.2f} m (Deeper)"
                scen_color = "var(--badge-deep-text)"
            elif scen_delta < -0.05:
                scen_dir = f"{scen_delta:.2f} m (Shallower)"
                scen_color = "var(--badge-shallow-text)"
            else:
                scen_dir = "0.00 m (No Change)"
                scen_color = "var(--text-secondary)"

            rain_label = f"{rain_factor:+d}%" if rain_factor != 0 else "0% (Baseline)"
            sim_html = f"""
            <div class="scenario-comparison-grid">
                <div class="scenario-card">
                    <div class="scenario-card-eyebrow">Baseline Prediction (0% Adjustment)</div>
                    <div class="scenario-card-val">{pred_val:.2f} <span style="font-size: 0.9rem; font-weight: 500;">m MBGL</span></div>
                    <div class="scenario-card-sub">Standard antecedent rainfall features as observed</div>
                </div>
                <div class="scenario-card">
                    <div class="scenario-card-eyebrow">Simulated Scenario ({rain_label})</div>
                    <div class="scenario-card-val" style="color: var(--teal-accent);">{scen_val:.2f} <span style="font-size: 0.9rem; font-weight: 500;">m MBGL</span></div>
                    <div class="scenario-card-sub">Depth under {rain_label} cumulative rainfall scaling</div>
                </div>
                <div class="scenario-card">
                    <div class="scenario-card-eyebrow">Net Scenario Impact vs Baseline</div>
                    <div class="scenario-card-val" style="color: {scen_color};">{scen_dir}</div>
                    <div class="scenario-card-sub">Model sensitivity delta for {station_sel}</div>
                </div>
            </div>
            """
            st.markdown(sim_html, unsafe_allow_html=True)
            st.caption("ℹ️ *Applies proportional scaling to antecedent 30d–365d cumulative rainfall features as a hypothetical sensitivity experiment, not a weather forecast or guarantee of physical aquifer recharge.*")

        with tab_eval:
            # A. Held-Out Evaluation Cards
            st.subheader("Held-Out Test Evaluation Results (2018–2023, n=124 events)")
            render_evaluation_result_cards(
                rf_mae=model_metrics['rf_mae'],
                rf_rmse=model_metrics['rf_rmse'],
                rf_r2=model_metrics['rf_r2'],
                pers_mae=model_metrics['pers_mae'],
                pers_rmse=model_metrics['pers_rmse'],
                emp_cov=emp_cov,
                avg_width=avg_width,
                pers_r2=model_metrics.get('pers_r2', -0.233)
            )

            # B. Performance Synthesis Box
            st.markdown(
                """
                <div class="perf-synthesis-box">
                    <b>Performance Synthesis & Practical Scope:</b> The temporal Random Forest model outperforms the persistence baseline (<tt>gw_now</tt>) on the held-out test split (2018–2023, <i>n</i>=124), achieving a <b>23.8% reduction in MAE</b> (2.092 m vs 2.744 m) and a <b>21.8% reduction in RMSE</b> (2.899 m vs 3.709 m). However, an <i>R</i>² of <b>0.247</b> and an MAE of <b>~2.09 m</b> indicate that predictive performance remains limited, reflecting the hydrogeological complexity of Deccan basalt aquifers and irregular sounding intervals. These metrics apply strictly to the temporal next-observation forecast and should not be conflated with the spatial mapping model (LOSO-CV <i>R</i>² = 0.022) or separate exploratory notebook experiments. The model is a research prototype and is <b>not suitable for unrestricted operational deployment</b> without on-site validation.
                </div>
                """,
                unsafe_allow_html=True
            )

            # C. Plain-English Metric Definitions Card
            st.markdown("""
            <div class="metric-def-grid">
                <div class="metric-def-card">
                    <div class="metric-def-header">
                        <span class="metric-def-title">MAE (Mean Absolute Error)</span>
                        <span class="metric-def-badge">Lower is better</span>
                    </div>
                    <div class="metric-def-body">
                        The average vertical difference in metres between the model's predicted water depth and the actual depth measured by surveyors.
                    </div>
                    <div class="metric-def-values">
                        • <b>Random Forest:</b> 2.092 m<br>
                        • <b>Persistence Baseline:</b> 2.744 m<br>
                        • <b>Improvement:</b> +23.8% error reduction
                    </div>
                </div>
                <div class="metric-def-card">
                    <div class="metric-def-header">
                        <span class="metric-def-title">RMSE (Root Mean Squared Error)</span>
                        <span class="metric-def-badge">Lower is better</span>
                    </div>
                    <div class="metric-def-body">
                        Similar to MAE, but squares errors before taking the root, penalizing large prediction mistakes more severely than small ones.
                    </div>
                    <div class="metric-def-values">
                        • <b>Random Forest:</b> 2.899 m<br>
                        • <b>Persistence Baseline:</b> 3.709 m<br>
                        • <b>Improvement:</b> +21.8% error reduction
                    </div>
                </div>
                <div class="metric-def-card">
                    <div class="metric-def-header">
                        <span class="metric-def-title">R² (Variance Explained)</span>
                        <span class="metric-def-badge">Higher is better (max 1.0)</span>
                    </div>
                    <div class="metric-def-body">
                        The proportion of groundwater fluctuations explained by the model compared to predicting a simple horizontal historical mean.
                    </div>
                    <div class="metric-def-values">
                        • <b>Random Forest:</b> 0.247<br>
                        • <b>Persistence Baseline:</b> -0.233<br>
                        • <b>Context:</b> ~75% of variance remains unexplained
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # D. Forecast Horizon Context
            st.subheader("Forecast Horizon Context (Next-Observation Schedule)")
            render_horizon_callout(test_h, overall_h)
            st.caption(
                "ℹ️ *Horizon Interpretation: The displayed approximate next-observation event date is illustrative, "
                "calculated using the overall held-out test-set median observation interval of 92 days. It is NOT a station-specific "
                "survey schedule or a date predicted by the model.*"
            )

        with tab_tech:
            # Educational MBGL Context
            render_forecast_mbgl_info()
            st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
            
            # Technical Methodology & CQR Expanders
            render_forecast_methodology_expander()
            render_cqr_calibration_expander()

    else:
        st.warning("Forecasting models and evaluation metadata are loading or unavailable.")
