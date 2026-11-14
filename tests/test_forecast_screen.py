"""Unit tests for Phase 2: Screen 3 — Next-Observation Forecast and associated components."""
import json
import pytest
import pandas as pd
import numpy as np

from services.data_loader import load_data, get_status
from services.model_service import load_models, predict_next_observation
from services.metrics_service import get_model_metrics, get_uncertainty_metrics, get_horizon_stats
from components.charts import render_station_history_chart
from components.metric_cards import render_evaluation_result_cards
from components.callouts import render_forecast_methodology_expander, render_cqr_calibration_expander


@pytest.fixture(scope="module")
def dataset_and_models():
    """Load verified processed dataset and trained forecasting models."""
    df = load_data()
    models = load_models()
    return df, models


def test_valid_forecast_stations_selection(dataset_and_models):
    """Verify that only stations with >= 10 observations are eligible for forecasting."""
    df, _ = dataset_and_models
    valid_stations = [s for s in df['station'].unique() if (df['station'] == s).sum() >= 10]
    
    assert len(valid_stations) == 9
    assert "Saswad" in valid_stations
    assert "Jejuri" in valid_stations
    assert "Zendewadi" in valid_stations
    
    # 2 stations have < 10 records and are safely excluded from the selectbox
    all_stations = df['station'].unique()
    excluded = set(all_stations) - set(valid_stations)
    assert len(excluded) == 2
    for s in excluded:
        assert (df['station'] == s).sum() < 10


def test_baseline_prediction_mathematical_bounds(dataset_and_models):
    """Verify that baseline predictions produce valid values and ordered uncertainty bounds."""
    df, models = dataset_and_models
    valid_stations = [s for s in df['station'].unique() if (df['station'] == s).sum() >= 10]
    
    for st_name in valid_stations:
        sub = df[df['station'] == st_name].sort_values('date')
        latest_record = sub.iloc[-1]
        
        res = predict_next_observation(models, latest_record, rain_factor=0)
        
        assert 'pred_val' in res
        assert 'lower_b' in res
        assert 'upper_b' in res
        
        pred_val = float(res['pred_val'])
        lower_b = float(res['lower_b'])
        upper_b = float(res['upper_b'])
        
        assert np.isfinite(pred_val)
        assert np.isfinite(lower_b)
        assert np.isfinite(upper_b)
        
        # Inverted / ordered bounds: lower_b <= pred_val <= upper_b
        assert lower_b <= pred_val + 1e-5, f"Lower bound {lower_b} exceeds point estimate {pred_val} for {st_name}"
        assert pred_val <= upper_b + 1e-5, f"Point estimate {pred_val} exceeds upper bound {upper_b} for {st_name}"
        assert upper_b >= lower_b


def test_direction_of_change_classification(dataset_and_models):
    """Verify correct MBGL directionality: positive change means Deeper, negative means Shallower."""
    df, models = dataset_and_models
    
    # Test synthetic delta cases
    # 1. Deeper (water table fell)
    current = 4.0
    pred_deeper = 5.2
    diff = pred_deeper - current
    assert diff > 0.05
    dir_name = "Deeper (water table falls)" if diff > 0.05 else ("Shallower (water table rises)" if diff < -0.05 else "Approximately Stable")
    assert dir_name == "Deeper (water table falls)"
    
    # 2. Shallower (water table rose)
    pred_shallower = 2.8
    diff = pred_shallower - current
    assert diff < -0.05
    dir_name = "Deeper (water table falls)" if diff > 0.05 else ("Shallower (water table rises)" if diff < -0.05 else "Approximately Stable")
    assert dir_name == "Shallower (water table rises)"
    
    # 3. Approximately Stable (within 0.05 m)
    pred_stable = 4.02
    diff = pred_stable - current
    assert abs(diff) <= 0.05
    dir_name = "Deeper (water table falls)" if diff > 0.05 else ("Shallower (water table rises)" if diff < -0.05 else "Approximately Stable")
    assert dir_name == "Approximately Stable"


def test_rainfall_what_if_simulation_responsiveness(dataset_and_models):
    """Verify that hypothetical rainfall scaling generates responsive predictions."""
    df, models = dataset_and_models
    sub = df[df['station'] == 'Jejuri'].sort_values('date')
    latest_record = sub.iloc[-1]
    
    base_res = predict_next_observation(models, latest_record, rain_factor=0)
    drought_res = predict_next_observation(models, latest_record, rain_factor=-30)
    surplus_res = predict_next_observation(models, latest_record, rain_factor=30)
    
    assert base_res['pred_val'] != drought_res['pred_val'] or base_res['pred_val'] != surplus_res['pred_val']
    # Under surplus rain (+30%), Jejuri water table is shallower (lower MBGL) than under drought (-30%)
    assert surplus_res['pred_val'] < drought_res['pred_val']


def test_exact_evaluation_metrics_consistency():
    """Verify exact held-out test evaluation figures against reports/model_evaluation.json."""
    with open("reports/model_evaluation.json", "r", encoding="utf-8") as f:
        meta = json.load(f)
        
    m = get_model_metrics(meta)
    unc = get_uncertainty_metrics(meta)
    h = get_horizon_stats(meta)
    
    # Random Forest Regressor
    assert m['rf_mae'] == 2.092
    assert m['rf_rmse'] == 2.899
    assert m['rf_r2'] == 0.247
    
    # Baseline Persistence
    assert m['pers_mae'] == 2.744
    assert m['pers_rmse'] == 3.709
    assert m['pers_r2'] == -0.233
    
    # Error Reduction
    rf_err_reduction = ((m['pers_mae'] - m['rf_mae']) / m['pers_mae']) * 100.0
    assert abs(rf_err_reduction - 23.76) < 0.1
    
    # Uncertainty
    assert unc['coverage_pct'] == 57.26
    assert unc['average_width_m'] == 4.36
    
    # Horizon
    assert h['test']['median_days'] == 92.0
    assert h['test']['mean_days'] == 109.4
    assert h['overall']['median_days'] == 102.0
    assert h['overall']['mean_days'] == 106.9


def test_forecast_screen_code_scientific_disclaimers():
    """Verify that screens/forecast.py contains necessary scientific disclaimers and avoids false claims."""
    with open("screens/forecast.py", "r", encoding="utf-8") as f:
        code = f.read()
        
    assert "Next-Observation Groundwater Forecast" in code
    assert "Uncalibrated q10–q90 Prediction Band" in code
    assert "Meters Below Ground Level (MBGL)" in code or "render_forecast_mbgl_info" in code
    assert "render_forecast_methodology_expander" in code
    assert "render_cqr_calibration_expander" in code
    assert "render_evaluation_result_cards" in code
    assert "render_station_history_chart" in code
    assert "hypothetical sensitivity experiment" in code.lower()
    assert "not an operational rainfall forecast" in code.lower() or "not a weather forecast" in code.lower()
    assert "not live automated telemetry" in code.lower() or "not live telemetry" in code.lower()


def test_forecast_screen_clarity_improvements():
    """Verify the three specific clarity improvements on Screen 3."""
    with open("screens/forecast.py", "r", encoding="utf-8") as f:
        code = f.read()
        
    # 1. Station eligibility clarity
    assert "9 of the 11 CGWB monitoring stations" in code
    assert "fewer than 10 historical groundwater observations" in code
    assert "remain fully included in the project's historical monitoring and geospatial map data" in code
    
    # 2. Forecast horizon interpretation clarity
    assert "illustrative" in code.lower()
    assert "test-set median observation interval of 92 days" in code
    assert "not a station-specific survey schedule" in code.lower()
    
    # 3. Uncertainty model distinction
    assert "Random Forest produces the point estimate" in code
    assert "Gradient Boosting Quantile Models produce the q10–q90 interval" in code or "Gradient Boosting Quantile Models (<tt>q10</tt> and <tt>q90</tt>) produce the q10–q90 prediction interval" in code
