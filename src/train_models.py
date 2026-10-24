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
    # TASK 2: Next-Quarter Groundwater Forecasting (SCREEN 3)
    # Target: gw_level_next
    # -------------------------------------------------------------
    print("\n" + "="*50)
    print("TASK 2: NEXT-QUARTER / 1-3 MONTH AHEAD FORECASTING (SCREEN 3)")
    print("="*50)
    
    # Filter rows that have next observation
    df_fc = df.dropna(subset=['gw_level_next', 'gw_level_lag1']).copy()
    
    feature_cols_fc = [
        'latitude', 'longitude', 'month', 'quarter', 'season_code',
        'gw_level_mbgl', 'gw_level_lag1', 'days_since_prev_obs',
        'rain_30d', 'rain_60d', 'rain_90d', 'rain_180d', 'rain_365d',
        'rain_dry_days_30d', 'rain_max_1d_30d'
    ]
    
    train_mask_fc = df_fc['year'] < split_year
    test_mask_fc = df_fc['year'] >= split_year
    
    X_train_fc = df_fc.loc[train_mask_fc, feature_cols_fc]
    y_train_fc = df_fc.loc[train_mask_fc, 'gw_level_next']
    X_test_fc = df_fc.loc[test_mask_fc, feature_cols_fc]
    y_test_fc = df_fc.loc[test_mask_fc, 'gw_level_next']
    
    print(f"Train samples (1996 - {split_year-1}): {len(X_train_fc)}")
    print(f"Test samples ({split_year} - 2023): {len(X_test_fc)}")
    
    # Baseline: Persistence (forecast = current gw_level_mbgl)
    y_pred_persist = df_fc.loc[test_mask_fc, 'gw_level_mbgl']
    
    # Models for forecasting
    models_fc = {
        'Baseline (Persistence: gw_now)': None,
        'Random Forest Regressor': RandomForestRegressor(n_estimators=200, max_depth=8, random_state=42),
        'HistGradientBoosting': HistGradientBoostingRegressor(max_iter=150, max_depth=5, random_state=42)
    }
    
    # Quantile models for Uncertainty Intervals (10th and 90th percentile bounds)
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
        
    # Uncertainty interval coverage on test set
    preds_q10 = q10_model.predict(X_test_fc)
    preds_q90 = q90_model.predict(X_test_fc)
    coverage = np.mean((y_test_fc >= preds_q10) & (y_test_fc <= preds_q90)) * 100.0
    print(f"\nUncertainty Band (10th - 90th Percentile) Empirical Coverage on Test Set: {coverage:.1f}%")
    
    # -------------------------------------------------------------
    # 3. Save Best Models & Metadata
    # -------------------------------------------------------------
    os.makedirs("models", exist_ok=True)
    joblib.dump(fitted_models_map['Random Forest'], "models/rf_mapping_model.joblib")
    joblib.dump(fitted_models_fc['Random Forest Regressor'], "models/rf_forecast_model.joblib")
    joblib.dump(q10_model, "models/forecast_q10.joblib")
    joblib.dump(q90_model, "models/forecast_q90.joblib")
    
    # Save feature columns metadata
    metadata = {
        'split_year': split_year,
        'feature_cols_map': feature_cols_map,
        'feature_cols_fc': feature_cols_fc,
        'results_map': results_map,
        'results_fc': results_fc,
        'uncertainty_80pct_coverage': round(coverage, 2)
    }
    with open("reports/model_evaluation.json", "w") as f:
        json.dump(metadata, f, indent=2)
        
    print("\nSuccessfully saved models to models/ and report to reports/model_evaluation.json!")

if __name__ == '__main__':
    evaluate_models()
