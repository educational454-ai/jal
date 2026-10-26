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
    st.markdown("""
    <div class="screen-header-block">
        <div class="main-header">🔮 Next-Observation Groundwater Forecast</div>
        <div class="sub-header">Predicting the next recorded CGWB groundwater monitoring event per station with uncalibrated q10–q90 prediction bands</div>
    </div>
    """, unsafe_allow_html=True)
    
    render_forecast_mbgl_info()
    
    # Station Selector
    valid_stations = [s for s in df['station'].unique() if (df['station'] == s).sum() >= 10]
    c_s1, c_s2 = st.columns([1.1, 1.9])
    
    with c_s1:
        station_sel = st.selectbox("Select Monitoring Station", sorted(valid_stations), index=0)
        station_df = df[df['station'] == station_sel].sort_values('date').copy()
        latest_record = station_df.iloc[-1]
        
        st.markdown("#### **Latest Known Conditions**")
        st.markdown(f"- **Station**: `{station_sel}`")
        st.markdown(f"- **Observation Date**: {latest_record['date'].strftime('%d %b %Y')}")
        st.markdown(f"- **Recorded Level**: `{latest_record['gw_level_mbgl']:.2f} m MBGL`")
        st.markdown(f"- **Preceding 90-Day Rain**: `{latest_record['rain_90d']:.1f} mm`")
        st.markdown(f"- **Preceding 365-Day Rain**: `{latest_record['rain_365d']:.1f} mm`")
        if latest_record.get('is_rainfall_extrapolated', 0):
            st.caption("⚠️ *Station is outside the 4-point IMD rainfall grid; rainfall is spatially extrapolated.*")
        
        st.markdown("---")
        st.markdown("#### **Hypothetical Rainfall Sensitivity Scenario**")
        rain_factor = st.slider(
            "Simulate Antecedent Rainfall Adjustment (Hypothetical)", -50, 50, 0, 5, format="%d%%",
            help="Hypothetical sensitivity adjustment: scales antecedent 30d–365d cumulative rainfall features to simulate drought (-30%) or wet (+30%) conditions. Note: this is a sensitivity simulation, not a weather forecast."
        )
        st.caption("*Applies proportional scaling to antecedent 30d–365d cumulative rainfall features as a sensitivity experiment, not a weather forecast.*")
        
    with c_s2:
        # Forecast computation via model service
        if 'forecast' in models and 'q10' in models and 'q90' in models and 'metadata' in models:
            meta = models['metadata']
            pred_results = predict_next_observation(models, latest_record, rain_factor=rain_factor)
            pred_val = pred_results['pred_val']
            lower_b = pred_results['lower_b']
            upper_b = pred_results['upper_b']
            
            # Retrieve exact evaluation metrics dynamically from metadata
            model_metrics = get_model_metrics(meta)
            unc_metrics = get_uncertainty_metrics(meta)
            horizon_stats = get_horizon_stats(meta)
            
            emp_cov = unc_metrics['coverage_pct']
            avg_width = unc_metrics['average_width_m']
            test_h = horizon_stats['test']
            overall_h = horizon_stats['overall']
            
            st.markdown("#### **🔮 Next-Observation Groundwater Forecast**")
            k1, k2, k3 = st.columns([0.9, 1.75, 0.95])
            with k1:
                st.metric(
                    "Projected Depth", f"{pred_val:.2f} m", 
                    delta=f"{pred_val - latest_record['gw_level_mbgl']:+.2f} m vs current",
                    delta_color="inverse"
                )
            with k2:
                st.metric(
                    "Uncalibrated q10–q90 Prediction Band", f"{lower_b:.2f} m – {upper_b:.2f} m", 
                    help=f"Nominal 80% interval. Measured empirical test coverage: {emp_cov:.1f}% (below nominal 80% target; miss rate: {100.0 - emp_cov:.1f}%). Average test width: {avg_width:.2f} m. Does not guarantee future coverage."
                )
            with k3:
                status, color, badge = get_status(pred_val)
                st.markdown(f"**Estimated Status:**<br><span class='{badge}'>{status}</span>", unsafe_allow_html=True)
                
            st.markdown("##### **⏱️ Forecast Horizon Context (Next-Observation Schedule)**")
            render_horizon_callout(test_h, overall_h)
            
            st.markdown("##### **📊 Held-Out Test Evaluation Results (2018–2023, n=124 events)**")
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
            
    # Historical Water Table Fluctuations Plot
    st.markdown("---")
    st.subheader(f"📈 Historical Water Table Fluctuations: {station_sel}")
    active_theme = get_current_theme()
    render_station_history_chart(station_df, station_sel, theme=active_theme)
    st.caption("ℹ️ *Note: Depth bands (<4.0m, 4.0–8.0m, >8.0m) represent project-defined physical reference bands, not official administrative exploitation categories. Observed water table changes reflect net dynamic balance (precipitation infiltration, baseflow, and seasonal agricultural pumping extraction) rather than direct measurements of natural recharge alone.*")

    # Uncertainty Quantification and Conformal Prediction Discussion
    render_cqr_calibration_expander()
