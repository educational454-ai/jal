import pandas as pd
import numpy as np
import json
import joblib
import os
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor, HistGradientBoostingRegressor
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

def evaluate_models():
    print("--- 1. Loading Processed Dataset ---")
    data_path = "data/processed/purandar_groundwater_features.csv"
    df = pd.read_csv(data_path)
    
    # Sort chronologically
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values(by='date').reset_index(drop=True)
    
    print(f"Total samples: {len(df)}")
    print(f"Date range: {df['date'].min().date()} to {df['date'].max().date()}")
    
    # -------------------------------------------------------------
    # TASK 1: Current Groundwater Level Estimation (Mapping Engine)
    # Features: lat, lon, month, quarter, season_code, rain_30d, rain_60d, rain_90d, rain_180d, rain_365d, rain_dry_days_30d, rain_max_1d_30d
    # -------------------------------------------------------------
    print("\n" + "="*50)
    print("TASK 1: SPATIO-TEMPORAL GROUNDWATER ESTIMATION (SCREEN 2)")
    print("="*50)
    
    feature_cols_map = [
        'latitude', 'longitude', 'month', 'quarter', 'season_code',
        'rain_30d', 'rain_60d', 'rain_90d', 'rain_180d', 'rain_365d',
        'rain_dry_days_30d', 'rain_max_1d_30d'
    ]
    
    # Train / Test Split by Time: Train <= 2017, Test >= 2018
    split_year = 2018
    train_mask = df['year'] < split_year
    test_mask = df['year'] >= split_year
    
    X_train_map = df.loc[train_mask, feature_cols_map]
    y_train_map = df.loc[train_mask, 'gw_level_mbgl']
    X_test_map = df.loc[test_mask, feature_cols_map]
    y_test_map = df.loc[test_mask, 'gw_level_mbgl']
    
    print(f"Train samples (1996 - {split_year-1}): {len(X_train_map)}")
    print(f"Test samples ({split_year} - 2023): {len(X_test_map)}")
    
    # Baseline: Station Seasonal Mean
    seasonal_station_mean = df.loc[train_mask].groupby(['station', 'season_code'])['gw_level_mbgl'].mean()
    def predict_baseline_map(row):
        val = seasonal_station_mean.get((row['station'], row['season_code']), np.nan)
        if np.isnan(val):
            val = y_train_map.mean()
        return val
        
    y_pred_baseline_map = df.loc[test_mask].apply(predict_baseline_map, axis=1)
    
    models_map = {
        'Baseline (Seasonal-Station Mean)': None,
        'Ridge Regression': Ridge(alpha=1.0),
        'Random Forest': RandomForestRegressor(n_estimators=150, max_depth=10, random_state=42),
        'Gradient Boosting': HistGradientBoostingRegressor(max_iter=150, max_depth=6, random_state=42)
    }
    
    results_map = {}
    fitted_models_map = {}
    
    for name, model in models_map.items():
        if model is None:
            preds = y_pred_baseline_map
        else:
            model.fit(X_train_map, y_train_map)
            preds = model.predict(X_test_map)
            fitted_models_map[name] = model
            
        mae = mean_absolute_error(y_test_map, preds)
        rmse = np.sqrt(mean_squared_error(y_test_map, preds))
        r2 = r2_score(y_test_map, preds)
        results_map[name] = {'MAE': round(mae, 3), 'RMSE': round(rmse, 3), 'R2': round(r2, 3)}
        print(f"  {name:32s} -> MAE: {mae:.3f} m | RMSE: {rmse:.3f} m | R2: {r2:.3f}")

    # -------------------------------------------------------------
    # TASK 2: Next Recorded Observation Groundwater Forecasting (SCREEN 3)
    # Target: gw_level_next (Next recorded monitoring event, irregular horizon)
    # -------------------------------------------------------------
    print("\n" + "="*50)
    print("TASK 2: NEXT RECORDED OBSERVATION FORECASTING (SCREEN 3)")
    print("="*50)
    
    # Filter rows that have next observation and previous lag
    df_fc = df.dropna(subset=['gw_level_next', 'gw_level_lag1']).copy()
    
    # Feature columns: only features known at or prior to the observation time
    # 'days_to_next_obs' is intentionally EXCLUDED because future interval is not known at forecast time
    feature_cols_fc = [
        'latitude', 'longitude', 'month', 'quarter', 'season_code',
        'gw_level_mbgl', 'gw_level_lag1', 'days_since_prev_obs',
        'rain_30d', 'rain_60d', 'rain_90d', 'rain_180d', 'rain_365d',
        'rain_dry_days_30d', 'rain_max_1d_30d'
    ]
    
    # Zero-Target-Leakage Chronological Split:
    # A sample is in Train ONLY if both observation date AND forward target date are strictly before split_date.
    # Test set observations start strictly at split_date.
    df_fc['date_dt'] = pd.to_datetime(df_fc['date'])
    df_fc['target_date_dt'] = pd.to_datetime(df_fc['target_date'])
    split_date = pd.to_datetime(f"{split_year}-01-01")
    
    train_mask_fc = (df_fc['date_dt'] < split_date) & (df_fc['target_date_dt'] < split_date)
    test_mask_fc = df_fc['date_dt'] >= split_date
    
    # Assert zero boundary leakage
    assert df_fc.loc[train_mask_fc, 'target_date_dt'].max() < split_date, (
        f"Target leakage error: training set target dates exceed split boundary ({split_date})"
    )
    assert df_fc.loc[test_mask_fc, 'date_dt'].min() >= split_date, (
        f"Split integrity error: test set contains observation date before split boundary ({split_date})"
    )
    
    X_train_fc = df_fc.loc[train_mask_fc, feature_cols_fc]
    y_train_fc = df_fc.loc[train_mask_fc, 'gw_level_next']
    X_test_fc = df_fc.loc[test_mask_fc, feature_cols_fc]
    y_test_fc = df_fc.loc[test_mask_fc, 'gw_level_next']
    
    print(f"Train samples ({df_fc.loc[train_mask_fc, 'date_dt'].min().date()} to {df_fc.loc[train_mask_fc, 'date_dt'].max().date()}): {len(X_train_fc)}")
    print(f"  (Train forward target range: {df_fc.loc[train_mask_fc, 'target_date_dt'].min().date()} to {df_fc.loc[train_mask_fc, 'target_date_dt'].max().date()})")
    print(f"Test samples ({df_fc.loc[test_mask_fc, 'date_dt'].min().date()} to {df_fc.loc[test_mask_fc, 'date_dt'].max().date()}): {len(X_test_fc)}")
    
    # Baseline: Persistence (forecast = current gw_level_mbgl)
    y_pred_persist = df_fc.loc[test_mask_fc, 'gw_level_mbgl']
    
    # Models for forecasting
    models_fc = {
        'Baseline (Persistence: gw_now)': None,
        'Random Forest Regressor': RandomForestRegressor(n_estimators=200, max_depth=8, random_state=42),
        'HistGradientBoosting': HistGradientBoostingRegressor(max_iter=150, max_depth=5, random_state=42)
    }
    
    # Quantile models for Uncertainty Intervals (nominal 10th and 90th percentile bounds)
    q10_model = GradientBoostingRegressor(loss='quantile', alpha=0.10, n_estimators=100, max_depth=4, random_state=42)
    q90_model = GradientBoostingRegressor(loss='quantile', alpha=0.90, n_estimators=100, max_depth=4, random_state=42)
    
    q10_model.fit(X_train_fc, y_train_fc)
    q90_model.fit(X_train_fc, y_train_fc)
    
    results_fc = {}
    fitted_models_fc = {}
    
    for name, model in models_fc.items():
        if model is None:
            preds = y_pred_persist
        else:
            model.fit(X_train_fc, y_train_fc)
            preds = model.predict(X_test_fc)
            fitted_models_fc[name] = model
            
        mae = mean_absolute_error(y_test_fc, preds)
        rmse = np.sqrt(mean_squared_error(y_test_fc, preds))
        r2 = r2_score(y_test_fc, preds)
        results_fc[name] = {'MAE': round(mae, 3), 'RMSE': round(rmse, 3), 'R2': round(r2, 3)}
        print(f"  {name:32s} -> MAE: {mae:.3f} m | RMSE: {rmse:.3f} m | R2: {r2:.3f}")
        
    # Empirical uncertainty interval coverage on held-out test set
    preds_q10 = q10_model.predict(X_test_fc)
    preds_q90 = q90_model.predict(X_test_fc)
    coverage = float(np.mean((y_test_fc >= preds_q10) & (y_test_fc <= preds_q90)) * 100.0)
    avg_width = float(np.mean(preds_q90 - preds_q10))
    print(f"\nUncertainty Band (q10–q90) Empirical Coverage on Held-Out Test Set: {coverage:.2f}% (Average width: {avg_width:.2f} m)")
    print(f"  Note: Nominal 80% coverage is uncalibrated out-of-sample (miss rate: {100.0 - coverage:.2f}%).")
    
    # -------------------------------------------------------------
    # 3. Save Best Models & Metadata
    # -------------------------------------------------------------
    os.makedirs("models", exist_ok=True)
    joblib.dump(fitted_models_map['Random Forest'], "models/rf_mapping_model.joblib")
    joblib.dump(fitted_models_fc['Random Forest Regressor'], "models/rf_forecast_model.joblib")
    joblib.dump(q10_model, "models/forecast_q10.joblib")
    joblib.dump(q90_model, "models/forecast_q90.joblib")
    
    # Save feature columns and audit metadata
    test_horizons = df_fc.loc[test_mask_fc, 'days_to_next_obs']
    all_horizons = df_fc['days_to_next_obs']
    
    metadata = {
        'split_year': split_year,
        'split_date': f"{split_year}-01-01",
        'task_description': 'Next recorded monitoring observation forecasting (irregular event horizon)',
        'evaluation_period': {
            'train_obs_range': [str(df_fc.loc[train_mask_fc, 'date_dt'].min().date()), str(df_fc.loc[train_mask_fc, 'date_dt'].max().date())],
            'train_target_range': [str(df_fc.loc[train_mask_fc, 'target_date_dt'].min().date()), str(df_fc.loc[train_mask_fc, 'target_date_dt'].max().date())],
            'test_obs_range': [str(df_fc.loc[test_mask_fc, 'date_dt'].min().date()), str(df_fc.loc[test_mask_fc, 'date_dt'].max().date())],
            'train_sample_count': int(len(X_train_fc)),
            'test_sample_count': int(len(X_test_fc))
        },
        'horizon_statistics': {
            'test_population': {
                'description': 'Held-out test set observations (2018–2023, n=124)',
                'mean_days': float(round(test_horizons.mean(), 1)),
                'median_days': float(round(test_horizons.median(), 1)),
                'min_days': float(round(test_horizons.min(), 1)),
                'max_days': float(round(test_horizons.max(), 1))
            },
            'overall_population': {
                'description': 'All eligible consecutive monitoring pairs (1996–2023, n=658)',
                'mean_days': float(round(all_horizons.mean(), 1)),
                'median_days': float(round(all_horizons.median(), 1)),
                'min_days': float(round(all_horizons.min(), 1)),
                'max_days': float(round(all_horizons.max(), 1))
            }
        },
        'feature_cols_map': feature_cols_map,
        'feature_cols_fc': feature_cols_fc,
        'results_map': results_map,
        'results_fc': results_fc,
        'uncertainty_intervals': {
            'nominal_coverage_pct': 80.0,
            'empirical_test_coverage_pct': round(coverage, 2),
            'average_interval_width_meters': round(avg_width, 2),
            'calibration_status': 'uncalibrated_undercoverage' if coverage < 75.0 else 'calibrated'
        },
        'uncertainty_80pct_coverage': round(coverage, 2)
    }
    with open("reports/model_evaluation.json", "w") as f:
        json.dump(metadata, f, indent=2)
        
    print("\nSuccessfully saved models to models/ and report to reports/model_evaluation.json!")

if __name__ == '__main__':
    evaluate_models()
