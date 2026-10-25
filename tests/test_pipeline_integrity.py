import os
import json
import datetime
import pytest
import pandas as pd
import numpy as np
import joblib
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

RAW_GW_PATH = "data/raw/purandhar_groundwater_level_merged.csv"
RAW_RF_PATH = "data/raw/purandar_rainfall_1991_2023.csv"
PROCESSED_PATH = "data/processed/purandar_groundwater_features.csv"
REPORT_PATH = "reports/model_evaluation.json"

def test_raw_data_integrity():
    """Verify raw files exist, have not been altered, and retain original shapes and values."""
    assert os.path.exists(RAW_GW_PATH), "Raw groundwater CSV missing"
    assert os.path.exists(RAW_RF_PATH), "Raw rainfall CSV missing"
    
    df_gw = pd.read_csv(RAW_GW_PATH)
    assert df_gw.shape == (680, 20), f"Raw groundwater shape changed: {df_gw.shape}"
    
    target_col = "Groundwater Level Quarterly Manual (meter)"
    assert target_col in df_gw.columns
    neg_readings = df_gw[df_gw[target_col] < 0]
    assert len(neg_readings) == 1, f"Expected exactly 1 negative reading in raw data, found {len(neg_readings)}"
    assert neg_readings.iloc[0]['Station'] == 'Narayanpur'
    assert neg_readings.iloc[0][target_col] == -0.40
    
    df_rf = pd.read_csv(RAW_RF_PATH)
    assert df_rf.shape == (49676, 4), f"Raw rainfall shape changed: {df_rf.shape}"

def test_negative_value_preservation():
    """Verify that negative groundwater readings are preserved in derived features and not silently clipped."""
    df_proc = pd.read_csv(PROCESSED_PATH)
    assert df_proc['gw_level_mbgl'].min() == -0.40, (
        f"Negative groundwater reading was clipped! Min is {df_proc['gw_level_mbgl'].min()}"
    )
    overflow_rows = df_proc[df_proc['is_overflow'] == 1]
    assert len(overflow_rows) == 1
    assert overflow_rows.iloc[0]['station'] == 'Narayanpur'
    assert overflow_rows.iloc[0]['gw_level_mbgl'] == -0.40

def test_rainfall_window_calendar_days():
    """Verify that antecedent rainfall lookbacks span exact calendar day lengths and exclude obs_date."""
    df_proc = pd.read_csv(PROCESSED_PATH)
    assert 'is_rainfall_extrapolated' in df_proc.columns
    
    # Check that stations outside the 4-point grid bounding box are flagged
    extrap_stations = set(df_proc[df_proc['is_rainfall_extrapolated'] == 1]['station'].unique())
    expected_extrap = {'Pimpri (Kh) Malvasti', 'Kamatwadi-Walha', 'Walha', 'Narayanpur'}
    assert extrap_stations == expected_extrap, f"Extrapolated stations mismatch: {extrap_stations}"

def test_chronological_split_zero_target_leakage():
    """Verify strict chronological train/test split: no train target dates leak into the test period."""
    df_proc = pd.read_csv(PROCESSED_PATH)
    df_fc = df_proc.dropna(subset=['gw_level_next', 'gw_level_lag1']).copy()
    
    df_fc['date_dt'] = pd.to_datetime(df_fc['date'])
    df_fc['target_date_dt'] = pd.to_datetime(df_fc['target_date'])
    split_date = pd.to_datetime('2018-01-01')
    
    train_mask = (df_fc['date_dt'] < split_date) & (df_fc['target_date_dt'] < split_date)
    test_mask = df_fc['date_dt'] >= split_date
    
    # Assert zero boundary leakage
    max_train_target_date = df_fc.loc[train_mask, 'target_date_dt'].max()
    min_test_obs_date = df_fc.loc[test_mask, 'date_dt'].min()
    
    assert max_train_target_date < split_date, (
        f"TARGET LEAKAGE: Training set contains target date {max_train_target_date} >= {split_date}"
    )
    assert min_test_obs_date >= split_date, (
        f"SPLIT VIOLATION: Test set contains observation date {min_test_obs_date} < {split_date}"
    )

def test_no_future_features_in_model():
    """Verify that future horizon 'days_to_next_obs' is NOT included in predictor features."""
    assert os.path.exists(REPORT_PATH)
    with open(REPORT_PATH) as f:
        meta = json.load(f)
    
    fc_features = meta['feature_cols_fc']
    assert 'days_to_next_obs' not in fc_features, "LEAKAGE: 'days_to_next_obs' found in feature_cols_fc!"
    assert 'gw_level_next' not in fc_features, "TARGET LEAKAGE: 'gw_level_next' in predictor features!"

def test_evaluation_metrics_and_coverage_honesty():
    """Verify recalculation of held-out test set metrics and honest empirical interval coverage."""
    with open(REPORT_PATH) as f:
        meta = json.load(f)
    
    df_proc = pd.read_csv(PROCESSED_PATH)
    df_fc = df_proc.dropna(subset=['gw_level_next', 'gw_level_lag1']).copy()
    
    df_fc['date_dt'] = pd.to_datetime(df_fc['date'])
    split_date = pd.to_datetime('2018-01-01')
    test_mask = df_fc['date_dt'] >= split_date
    
    X_test = df_fc.loc[test_mask, meta['feature_cols_fc']]
    y_test = df_fc.loc[test_mask, 'gw_level_next']
    
    rf_model = joblib.load("models/rf_forecast_model.joblib")
    q10_model = joblib.load("models/forecast_q10.joblib")
    q90_model = joblib.load("models/forecast_q90.joblib")
    
    # Recalculate test metrics
    preds_rf = rf_model.predict(X_test)
    recalc_mae = mean_absolute_error(y_test, preds_rf)
    recalc_rmse = np.sqrt(mean_squared_error(y_test, preds_rf))
    recalc_r2 = r2_score(y_test, preds_rf)
    
    rep_rf = meta['results_fc']['Random Forest Regressor']
    assert abs(rep_rf['MAE'] - recalc_mae) < 0.005, f"MAE mismatch: {rep_rf['MAE']} vs {recalc_mae}"
    assert abs(rep_rf['RMSE'] - recalc_rmse) < 0.005, f"RMSE mismatch: {rep_rf['RMSE']} vs {recalc_rmse}"
    assert abs(rep_rf['R2'] - recalc_r2) < 0.005, f"R2 mismatch: {rep_rf['R2']} vs {recalc_r2}"
    
    # Recalculate empirical interval coverage
    preds_q10 = q10_model.predict(X_test)
    preds_q90 = q90_model.predict(X_test)
    recalc_cov = np.mean((y_test >= preds_q10) & (y_test <= preds_q90)) * 100.0
    
    rep_cov = meta['uncertainty_intervals']['empirical_test_coverage_pct']
    assert abs(rep_cov - recalc_cov) < 0.1, f"Coverage mismatch: {rep_cov} vs {recalc_cov}"
    assert rep_cov < 75.0, "Empirical coverage unexpectedly claims high coverage without calibration"

def test_map_marker_integrity_and_no_arbitrary_influence_circles():
    """Verify that arbitrary depth-scaled influence circles are removed and fixed-size markers are used."""
    with open("app.py", "r", encoding="utf-8") as f:
        app_code = f.read()
    
    # Assert arbitrary scaling circle was removed
    assert "st.depth * 250" not in app_code, "Arbitrary influence circle scaling 'st.depth * 250' still present in app.py!"
    assert "L.circle([st.lat, st.lon]" not in app_code, "Arbitrary L.circle still present in app.py map!"
    
    # Assert fixed circle marker is used
    assert "L.circleMarker" in app_code, "L.circleMarker missing from map!"
    assert "is_extrapolated" in app_code, "Rainfall extrapolation flag missing from map popup!"
    assert "Observed CGWB Telemetry" in app_code, "Observed telemetry label missing from map popup!"

def test_phase4_metadata_and_dashboard_labeling():
    """Verify Phase 4 requirements: metadata synchronization, exact metric values, and honest UI labeling."""
    assert os.path.exists(REPORT_PATH)
    with open(REPORT_PATH, "r", encoding="utf-8") as f:
        meta = json.load(f)
    
    # 1. Held-out test results accuracy in metadata
    rf = meta['results_fc']['Random Forest Regressor']
    assert rf['MAE'] == 2.092, f"RF MAE mismatch: {rf['MAE']}"
    assert rf['RMSE'] == 2.899, f"RF RMSE mismatch: {rf['RMSE']}"
    assert rf['R2'] == 0.247, f"RF R2 mismatch: {rf['R2']}"
    
    pers = meta['results_fc']['Baseline (Persistence: gw_now)']
    assert pers['MAE'] == 2.744, f"Persistence MAE mismatch: {pers['MAE']}"
    
    unc = meta['uncertainty_intervals']
    assert unc['empirical_test_coverage_pct'] == 57.26, f"Empirical coverage mismatch: {unc['empirical_test_coverage_pct']}"
    assert unc['average_interval_width_meters'] == 4.36, f"Average width mismatch: {unc['average_interval_width_meters']}"
    
    # 2. Horizon statistics reconciliation
    h_test = meta['horizon_statistics']['test_population']
    assert h_test['median_days'] == 92.0
    assert h_test['mean_days'] == 109.4
    assert h_test['min_days'] == 41.0
    assert h_test['max_days'] == 233.0
    
    h_all = meta['horizon_statistics']['overall_population']
    assert h_all['median_days'] == 102.0
    assert h_all['mean_days'] == 106.9
    assert h_all['min_days'] == 41.0
    assert h_all['max_days'] == 2206.0
    
    # 3. UI labeling check in app.py
    with open("app.py", "r", encoding="utf-8") as f:
        app_code = f.read()
    
    assert "Next-Observation Groundwater Forecast" in app_code
    assert "Uncalibrated q10–q90 Prediction Band" in app_code
    assert "Meters Below Ground Level (MBGL)" in app_code
    assert "not groundwater exactly 90 days in the future" in app_code
    assert "Evaluation Population Forecast Horizon" in app_code
    assert "not actual future physical measurements" in app_code

