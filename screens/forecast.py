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
    render_cqr_calibration_expander,
)
from styles.theme import get_current_theme


def render_forecast_screen(df: pd.DataFrame, models: dict) -> None:
    """Render Screen 3: Next-Observation Forecast."""
    # 1. Page Heading & MBGL Notice
    st.markdown("""
    <div class="screen-header-block">
        <div class="main-header">Next-Observation Groundwater Forecast</div>
        <div class="sub-header">Predicting the next recorded CGWB groundwater monitoring event per station with uncalibrated q10–q90 prediction bands</div>
    </div>
    """, unsafe_allow_html=True)
    
    render_forecast_mbgl_info()
    
    # 2. Prominent Full-Width Station Selector
    valid_stations = [s for s in df['station'].unique() if (df['station'] == s).sum() >= 10]
    station_sel = st.selectbox(
        "Select Monitoring Station", 
        sorted(valid_stations), 
        index=0,
        key="forecast_station_select",
        help="Select a CGWB monitoring station to view latest conditions, simulate rainfall scenarios, and generate machine learning forecasts."
    )
    station_df = df[df['station'] == station_sel].sort_values('date').copy()
    latest_record = station_df.iloc[-1]
    active_theme = get_current_theme()

    # Read current hypothetical rainfall factor from session state
    if "forecast_rain_slider" not in st.session_state:
        st.session_state["forecast_rain_slider"] = 0
    rain_factor = int(st.session_state["forecast_rain_slider"])

    if 'forecast' in models and 'q10' in models and 'q90' in models and 'metadata' in models:
        meta = models['metadata']
        pred_results = predict_next_observation(models, latest_record, rain_factor=rain_factor)
        pred_val = float(pred_results['pred_val'])
        lower_b = float(pred_results['lower_b'])
        upper_b = float(pred_results['upper_b'])
        
        # Exact evaluation metrics from metadata
        model_metrics = get_model_metrics(meta)
        unc_metrics = get_uncertainty_metrics(meta)
        horizon_stats = get_horizon_stats(meta)
        
        emp_cov = float(unc_metrics['coverage_pct'])
        avg_width = float(unc_metrics['average_width_m'])
        test_h = horizon_stats['test']
        overall_h = horizon_stats['overall']
        
        current_mbgl = float(latest_record['gw_level_mbgl'])
        diff_val = pred_val - current_mbgl
        if diff_val > 0.005:
            delta_pill = f'<span class="forecast-delta-pill forecast-delta-deeper">↑ +{diff_val:.2f} m vs current</span>'
        elif diff_val < -0.005:
            delta_pill = f'<span class="forecast-delta-pill forecast-delta-shallower">↓ {diff_val:.2f} m vs current</span>'
        else:
            delta_pill = '<span class="forecast-delta-pill" style="background-color: var(--bg-secondary); color: var(--text-secondary); border: 1px solid var(--border-color);">0.00 m vs current</span>'
            
        status, color, badge = get_status(pred_val)
        
        # 3 & 4. Visually Prominent Forecast Summary & Latest Known Conditions Card
        c_fc, c_cond = st.columns([1.6, 1.4])
        
        with c_fc:
            sim_badge = f' · Simulated ({rain_factor:+d}% rain)' if rain_factor != 0 else ''
            fc_html = f"""
            <div class="forecast-summary-card">
                <div>
                    <div class="forecast-card-eyebrow">Random Forest Point Estimate · Next Observation{sim_badge}</div>
                    <div class="forecast-depth-display">
                        <span class="forecast-depth-val">{pred_val:.2f}</span>
                        <span class="forecast-depth-unit">m MBGL</span>
                        {delta_pill}
                    </div>
                </div>
                <div class="forecast-meta-grid">
                    <div class="forecast-meta-item">
                        <span class="forecast-meta-label">Uncalibrated q10–q90 Band</span>
                        <span class="forecast-meta-value">{lower_b:.2f} m – {upper_b:.2f} m</span>
                        <span class="forecast-meta-caption">Nominal 80% interval · Test coverage: {emp_cov:.1f}%</span>
                    </div>
                    <div class="forecast-meta-item">
                        <span class="forecast-meta-label">Estimated Depth Status</span>
                        <div><span class="{badge}" style="margin-top: 2px;">● {status}</span></div>
                        <span class="forecast-meta-caption">Project physical tier (&lt; 4m, 4–8m, &gt; 8m)</span>
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
                '<span>✓</span><span>Station within IMD grid bounding box</span></div>'
            )
            
            cond_html = f"""
            <div class="conditions-card">
                <div>
                    <div class="conditions-card-title">Latest Known Station Telemetry</div>
                    <div class="conditions-card-sub">In-situ CGWB physical observation</div>
                    <div class="conditions-row">
                        <span class="conditions-lbl">Station Name:</span>
                        <span class="conditions-val"><b>{station_sel}</b></span>
                    </div>
                    <div class="conditions-row">
                        <span class="conditions-lbl">Observation Date:</span>
                        <span class="conditions-val">{latest_record['date'].strftime('%d %b %Y')}</span>
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
            
        # 5. Hypothetical Rainfall Sensitivity Scenario
        st.markdown("""
        <div class="sensitivity-card">
            <div class="sensitivity-header">
                <div class="sensitivity-title">Hypothetical Rainfall Sensitivity Scenario</div>
                <div class="sensitivity-sub">Simulate proportional scaling of antecedent 30d–365d cumulative rainfall features (-50% to +50%) to evaluate model sensitivity under drought or surplus monsoon conditions. Note: this is a sensitivity simulation, not a weather forecast.</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.slider(
            "Simulate Antecedent Rainfall Adjustment (Hypothetical)",
            min_value=-50,
            max_value=50,
            step=5,
            format="%d%%",
            key="forecast_rain_slider",
            help="Hypothetical sensitivity adjustment: scales antecedent 30d–365d cumulative rainfall features to simulate drought (-30%) or wet (+30%) conditions. Note: this is a sensitivity simulation, not a weather forecast."
        )
        st.caption("ℹ️ *Applies proportional scaling to antecedent 30d–365d cumulative rainfall features as a sensitivity experiment, not a weather forecast.*")

        # 6. Forecast Horizon Context
        st.subheader("Forecast Horizon Context (Next-Observation Schedule)")
        render_horizon_callout(test_h, overall_h)

        # 7. Model Evaluation Results
        st.subheader("Held-Out Test Evaluation Results (2018–2023, n=124 events)")
        render_evaluation_result_cards(
            rf_mae=model_metrics['rf_mae'],
            rf_rmse=model_metrics['rf_rmse'],
            rf_r2=model_metrics['rf_r2'],
            pers_mae=model_metrics['pers_mae'],
            pers_rmse=model_metrics['pers_rmse'],
            emp_cov=emp_cov,
            avg_width=avg_width
        )

    else:
        st.warning("Forecasting models and evaluation metadata are loading or unavailable.")

    # 8. Historical Groundwater Chart (Full-Width)
    st.markdown("---")
    st.subheader(f"Historical Water Table Fluctuations: {station_sel}")
    render_station_history_chart(station_df, station_sel, theme=active_theme)
    st.caption("ℹ️ *Note: Depth bands (< 4.0 m, 4.0–8.0 m, > 8.0 m) represent project-defined physical reference bands, not official administrative exploitation categories. Observed water table changes reflect net dynamic balance (precipitation infiltration, baseflow, and seasonal agricultural pumping extraction) rather than direct measurements of natural recharge alone.*")

    # 9. Prediction Interval Calibration & Conformal Prediction Analysis
    render_cqr_calibration_expander()
