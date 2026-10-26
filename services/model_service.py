"""Model loading and inference services for BhujalDrishti."""
import os
import json
import joblib
import pandas as pd
import streamlit as st


@st.cache_resource
def load_models() -> dict:
    """Load machine learning models and evaluation metadata artifacts."""
    models = {}
    if os.path.exists("models/rf_forecast_model.joblib"):
        models['forecast'] = joblib.load("models/rf_forecast_model.joblib")
    if os.path.exists("models/forecast_q10.joblib"):
        models['q10'] = joblib.load("models/forecast_q10.joblib")
    if os.path.exists("models/forecast_q90.joblib"):
        models['q90'] = joblib.load("models/forecast_q90.joblib")
    if os.path.exists("reports/model_evaluation.json"):
        with open("reports/model_evaluation.json", "r", encoding="utf-8") as f:
            models['metadata'] = json.load(f)
    return models


def predict_next_observation(models: dict, latest_record: pd.Series, rain_factor: float = 0.0) -> dict:
    """Perform next-observation forecast inference with scenario adjustment.
    
    Args:
        models: Dictionary containing trained model objects and metadata.
        latest_record: Single row Series of the station's latest observation.
        rain_factor: Percentage adjustment (-50% to +50%) for scenario simulation.
        
    Returns:
        dict with projected depth, lower bound, upper bound, and raw quantile predictions.
    """
    if 'forecast' not in models or 'q10' not in models or 'q90' not in models or 'metadata' not in models:
        raise ValueError("Forecasting models or evaluation metadata are not loaded.")
        
    meta = models['metadata']
    feature_cols = meta.get('feature_cols_fc', [])
    
    feat_dict = {}
    for col in feature_cols:
        feat_dict[col] = latest_record[col]
        
    # Apply what-if simulation multiplier to antecedent rain features
    multiplier = 1.0 + (rain_factor / 100.0)
    for rf_col in ['rain_30d', 'rain_60d', 'rain_90d', 'rain_180d', 'rain_365d']:
        if rf_col in feat_dict:
            feat_dict[rf_col] *= multiplier
            
    X_input = pd.DataFrame([feat_dict])
    pred_val = float(models['forecast'].predict(X_input)[0])
    pred_q10 = float(models['q10'].predict(X_input)[0])
    pred_q90 = float(models['q90'].predict(X_input)[0])
    
    # Non-truncating physical interval bounds
    lower_b = min(pred_q10, pred_val)
    upper_b = max(pred_val, pred_q90)
    
    return {
        "pred_val": pred_val,
        "lower_b": lower_b,
        "upper_b": upper_b,
        "pred_q10": pred_q10,
        "pred_q90": pred_q90,
    }
