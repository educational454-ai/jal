"""Unit tests for seasonal groundwater comparison and matched station-year pairing."""
import pandas as pd
import numpy as np
import pytest
from services.data_loader import load_data, get_seasonal_matched_comparison


def test_seasonal_matched_pairs_real_data():
    """Verify matched station-year pairs on the verified Purandar processed dataset."""
    df = load_data()
    res = get_seasonal_matched_comparison(df)
    
    assert res["has_data"] is True
    assert res["count"] == 137, f"Expected exactly 137 matched pairs, got {res['count']}"
    assert res["year_min"] == 1996
    assert res["year_max"] == 2022
    
    # Mathematical sanity
    assert pytest.approx(res["mean_change_m"], 0.01) == -3.61
    assert pytest.approx(res["median_rise_m"], 0.01) == 3.19
    
    # Negative Nov-May depth change implies water table rose
    assert res["mean_change_m"] < 0
    assert res["median_rise_m"] > 0


def test_seasonal_pairs_strict_matching():
    """Verify that every matched pair contains observations for the exact same station and year."""
    df = load_data()
    res = get_seasonal_matched_comparison(df)
    pairs = res["pairs_df"]
    
    assert len(pairs) == 137
    assert 'station' in pairs.columns
    assert 'year' in pairs.columns
    assert 'may_mbgl' in pairs.columns
    assert 'nov_mbgl' in pairs.columns
    assert 'depth_change_m' in pairs.columns
    assert 'water_table_rise_m' in pairs.columns
    
    for _, row in pairs.iterrows():
        # Check depth change definition: Nov - May
        expected_diff = row['nov_mbgl'] - row['may_mbgl']
        assert pytest.approx(row['depth_change_m'], 1e-4) == expected_diff
        # Water table rise definition: May - Nov
        expected_rise = row['may_mbgl'] - row['nov_mbgl']
        assert pytest.approx(row['water_table_rise_m'], 1e-4) == expected_rise
        assert pytest.approx(row['water_table_rise_m'], 1e-4) == -expected_diff


def test_seasonal_yearly_summary_structure():
    """Verify yearly summary table aggregation."""
    df = load_data()
    res = get_seasonal_matched_comparison(df)
    yearly = res["yearly_summary"]
    
    assert len(yearly) == 23  # 23 distinct historical years with matched pairs
    assert 'year' in yearly.columns
    assert 'n_pairs' in yearly.columns
    assert 'may_mean' in yearly.columns
    assert 'nov_mean' in yearly.columns
    assert 'mean_change' in yearly.columns
    assert 'median_rise' in yearly.columns
    
    # All years should be within the min-max span
    assert yearly['year'].min() == 1996
    assert yearly['year'].max() == 2022
    assert yearly['n_pairs'].sum() == 137


def test_seasonal_edge_cases_empty_and_none():
    """Verify that None, empty DataFrame, or missing columns fail gracefully without throwing."""
    res_none = get_seasonal_matched_comparison(None)
    assert res_none["has_data"] is False
    assert res_none["count"] == 0
    
    res_empty = get_seasonal_matched_comparison(pd.DataFrame())
    assert res_empty["has_data"] is False
    assert res_empty["count"] == 0

    res_missing_cols = get_seasonal_matched_comparison(pd.DataFrame({'a': [1, 2]}))
    assert res_missing_cols["has_data"] is False
    assert res_missing_cols["count"] == 0


def test_seasonal_edge_cases_unmatched_data():
    """Verify synthetic datasets with only May or only Nov observations return has_data=False."""
    only_may = pd.DataFrame([
        {'station': 'A', 'date': pd.to_datetime('2020-05-15'), 'gw_level_mbgl': 8.0},
        {'station': 'B', 'date': pd.to_datetime('2020-05-15'), 'gw_level_mbgl': 7.5}
    ])
    res_may = get_seasonal_matched_comparison(only_may)
    assert res_may["has_data"] is False
    assert res_may["count"] == 0
    
    only_nov = pd.DataFrame([
        {'station': 'A', 'date': pd.to_datetime('2020-11-15'), 'gw_level_mbgl': 3.0},
        {'station': 'B', 'date': pd.to_datetime('2020-11-15'), 'gw_level_mbgl': 2.5}
    ])
    res_nov = get_seasonal_matched_comparison(only_nov)
    assert res_nov["has_data"] is False
    assert res_nov["count"] == 0
    
    # Different years (unmatched)
    diff_years = pd.DataFrame([
        {'station': 'A', 'date': pd.to_datetime('2020-05-15'), 'gw_level_mbgl': 8.0},
        {'station': 'A', 'date': pd.to_datetime('2021-11-15'), 'gw_level_mbgl': 3.0}
    ])
    res_diff = get_seasonal_matched_comparison(diff_years)
    assert res_diff["has_data"] is False
    assert res_diff["count"] == 0


def test_seasonal_edge_cases_nan_handling():
    """Verify that rows with NaN in gw_level_mbgl are dropped safely."""
    nan_df = pd.DataFrame([
        {'station': 'A', 'date': pd.to_datetime('2020-05-15'), 'gw_level_mbgl': np.nan},
        {'station': 'A', 'date': pd.to_datetime('2020-11-15'), 'gw_level_mbgl': 3.0},
        {'station': 'B', 'date': pd.to_datetime('2020-05-15'), 'gw_level_mbgl': 8.0},
        {'station': 'B', 'date': pd.to_datetime('2020-11-15'), 'gw_level_mbgl': 4.0}
    ])
    res_nan = get_seasonal_matched_comparison(nan_df)
    assert res_nan["has_data"] is True
    assert res_nan["count"] == 1
    assert res_nan["pairs_df"].iloc[0]['station'] == 'B'
    assert pytest.approx(res_nan["mean_change_m"], 0.01) == -4.0
    assert pytest.approx(res_nan["median_rise_m"], 0.01) == 4.0

