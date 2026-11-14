"""Unit tests for station-wise groundwater change calculations and recency handling."""
import pandas as pd
import pytest
from services.data_loader import load_data, get_latest_per_station


def test_station_wise_change_columns():
    """Verify that get_latest_per_station returns all required change and recency columns."""
    df = load_data()
    latest = get_latest_per_station(df)
    
    assert len(latest) == 11
    required_cols = [
        'station', 'date', 'gw_level_mbgl', 'prev_date', 
        'prev_gw_level_mbgl', 'depth_change_m', 'days_elapsed', 
        'total_station_records', 'season_tag', 'is_rainfall_extrapolated'
    ]
    for col in required_cols:
        assert col in latest.columns, f"Missing column: {col}"


def test_station_change_mathematical_consistency():
    """Verify that depth_change_m strictly equals latest MBGL minus previous MBGL."""
    df = load_data()
    latest = get_latest_per_station(df)
    
    for _, row in latest.iterrows():
        if pd.notnull(row['prev_gw_level_mbgl']):
            expected_diff = row['gw_level_mbgl'] - row['prev_gw_level_mbgl']
            assert pytest.approx(row['depth_change_m'], 1e-4) == expected_diff
            
            # Days elapsed must be strictly positive
            expected_days = (row['date'] - row['prev_date']).days
            assert row['days_elapsed'] == expected_days
            assert row['days_elapsed'] > 0


def test_zendewadi_gap_exactness():
    """Verify Zendewadi's 2,206-day gap between 15-May-2016 and 30-May-2022."""
    df = load_data()
    latest = get_latest_per_station(df)
    z_row = latest[latest['station'] == 'Zendewadi'].iloc[0]
    
    assert z_row['days_elapsed'] == 2206
    assert z_row['date'].strftime('%Y-%m-%d') == '2022-05-30'
    assert z_row['prev_date'].strftime('%Y-%m-%d') == '2016-05-15'
    assert pytest.approx(z_row['depth_change_m'], 0.01) == 0.67


def test_observation_recency_counts():
    """Verify exactly 7 stations were observed in 2023, and 4 stations have older observations."""
    df = load_data()
    latest = get_latest_per_station(df)
    
    obs_years = latest['date'].dt.year.value_counts().to_dict()
    assert obs_years.get(2023, 0) == 7, "Expected exactly 7 stations observed in 2023"
    assert obs_years.get(2022, 0) == 1, "Expected Zendewadi in 2022"
    assert obs_years.get(2006, 0) == 1, "Expected Saswad in 2006"
    assert obs_years.get(1997, 0) == 2, "Expected Waghapur & Walha in 1997"


def test_synthetic_insufficient_observation_handling():
    """Verify that a synthetic dataset with single-observation stations does not crash."""
    synth_df = pd.DataFrame([
        {
            'station': 'SingleObsWell',
            'date': pd.to_datetime('2023-05-10'),
            'gw_level_mbgl': 5.50,
            'season_tag': 'Pre-Monsoon (May)'
        }
    ])
    result = get_latest_per_station(synth_df)
    assert len(result) == 1
    assert pd.isna(result.iloc[0]['prev_date'])
    assert pd.isna(result.iloc[0]['prev_gw_level_mbgl'])
    assert pd.isna(result.iloc[0]['depth_change_m'])
    assert pd.isna(result.iloc[0]['days_elapsed'])
    assert result.iloc[0]['total_station_records'] == 1

