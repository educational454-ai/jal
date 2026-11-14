"""Unit tests for Rainfall-Groundwater relationship calculations and data structures."""
import pandas as pd
import numpy as np
import pytest
from services.data_loader import load_data, get_rainfall_groundwater_correlations


def test_rainfall_groundwater_correlations_real_data():
    """Verify dynamic correlation metrics on the real Purandar dataset."""
    df = load_data()
    res = get_rainfall_groundwater_correlations(df)
    
    assert res["has_data"] is True
    assert res["n_obs"] == 680
    assert res["n_years"] == 28  # 1996 through 2023
    
    windows = res["windows"]
    for w in ['rain_90d', 'rain_180d', 'rain_365d']:
        assert w in windows
        assert 'pearson' in windows[w]
        assert 'spearman' in windows[w]
        assert 'mean_mm' in windows[w]
        assert 'median_mm' in windows[w]
        # In MBGL, more rainfall produces lower depth (shallower water table), so correlation is negative
        assert windows[w]['pearson'] < 0
        assert windows[w]['spearman'] < 0

    # Numerical precision checks
    assert pytest.approx(windows['rain_90d']['pearson'], 0.02) == -0.30
    assert pytest.approx(windows['rain_90d']['spearman'], 0.02) == -0.53
    assert pytest.approx(windows['rain_180d']['pearson'], 0.02) == -0.29
    assert pytest.approx(windows['rain_180d']['spearman'], 0.02) == -0.53
    assert pytest.approx(windows['rain_365d']['pearson'], 0.02) == -0.13
    assert pytest.approx(windows['rain_365d']['spearman'], 0.02) == -0.35


def test_annual_correlations_consistency():
    """Verify aggregated annual correlations."""
    df = load_data()
    res = get_rainfall_groundwater_correlations(df)
    annual = res["annual_windows"]
    
    for w in ['rain_90d', 'rain_180d', 'rain_365d']:
        assert w in annual
        assert annual[w]['pearson'] < 0
        assert annual[w]['spearman'] < 0
        
    assert pytest.approx(annual['rain_365d']['pearson'], 0.02) == -0.41
    assert pytest.approx(annual['rain_365d']['spearman'], 0.02) == -0.58


def test_rainfall_correlations_edge_cases():
    """Verify that None, empty DataFrame, missing columns, or tiny datasets return has_data=False."""
    assert get_rainfall_groundwater_correlations(None)["has_data"] is False
    assert get_rainfall_groundwater_correlations(pd.DataFrame())["has_data"] is False
    
    # Missing gw_level_mbgl
    no_gw = pd.DataFrame({'rain_90d': [100, 200, 300]})
    assert get_rainfall_groundwater_correlations(no_gw)["has_data"] is False

    # Missing rain columns
    no_rain = pd.DataFrame({'gw_level_mbgl': [5.0, 6.0, 7.0]})
    assert get_rainfall_groundwater_correlations(no_rain)["has_data"] is False

    # Fewer than 5 observations
    tiny = pd.DataFrame({
        'gw_level_mbgl': [5.0, 6.0, 7.0],
        'rain_365d': [500.0, 600.0, 700.0]
    })
    assert get_rainfall_groundwater_correlations(tiny)["has_data"] is False


def test_rainfall_correlations_nan_handling():
    """Verify that NaNs in groundwater or rainfall are filtered safely."""
    df = pd.DataFrame({
        'gw_level_mbgl': [5.0, 6.0, np.nan, 7.0, 8.0, 9.0],
        'rain_90d': [100, np.nan, 150, 200, 250, 300],
        'rain_180d': [200, 250, 300, 400, 500, 600],
        'rain_365d': [400, 500, 600, 800, 1000, 1200],
        'year': [2000, 2001, 2002, 2003, 2004, 2005]
    })
    res = get_rainfall_groundwater_correlations(df)
    # Rows with NaN in gw_level_mbgl or available windows dropped -> 4 valid rows
    # With 4 valid rows, should be < 5 so has_data is False
    assert res["has_data"] is False

    # With 6 valid rows:
    df_valid = pd.DataFrame({
        'gw_level_mbgl': [5.0, 6.0, 7.0, 8.0, 9.0, 10.0],
        'rain_90d': [300, 250, 200, 150, 100, 50],
        'rain_180d': [600, 500, 400, 300, 200, 100],
        'rain_365d': [1200, 1000, 800, 600, 400, 200],
        'year': [2000, 2001, 2002, 2003, 2004, 2005]
    })
    res_valid = get_rainfall_groundwater_correlations(df_valid)
    assert res_valid["has_data"] is True
    assert res_valid["n_obs"] == 6
    # Perfectly inverted relationship -> Pearson == -1.0
    assert pytest.approx(res_valid["windows"]["rain_90d"]["pearson"], 1e-4) == -1.0

