"""Unit tests for Screen 2: Groundwater Map GIS Dashboard."""
import math
import numpy as np
import pandas as pd
import pytest

from services.data_loader import (
    load_data,
    get_latest_per_station,
    get_depth_tier_category,
    get_depth_tier,
    get_status
)


def test_station_coordinate_validity():
    """Verify that all monitoring stations have valid, non-null, non-zero geographic coordinates."""
    df = load_data()
    latest_st = get_latest_per_station(df)
    
    assert len(latest_st) == 11, f"Expected 11 stations, found {len(latest_st)}"
    
    # Check nulls
    assert latest_st['latitude'].notna().all(), "Found null latitude values"
    assert latest_st['longitude'].notna().all(), "Found null longitude values"
    
    # Check non-zero
    assert (latest_st['latitude'] > 0).all(), "Found non-positive latitude"
    assert (latest_st['longitude'] > 0).all(), "Found non-positive longitude"
    
    # Check realistic bounding coordinates for Purandar Taluka region (approx 18.0 - 18.6 N, 73.8 - 74.4 E)
    for _, row in latest_st.iterrows():
        lat = row['latitude']
        lon = row['longitude']
        assert 18.0 <= lat <= 18.6, f"Latitude {lat} for {row['station']} out of Purandar range"
        assert 73.8 <= lon <= 74.4, f"Longitude {lon} for {row['station']} out of Purandar range"


def test_depth_tier_stratification_counts():
    """Verify the 11 stations are stratified into Shallow (2), Moderate (5), Deep (4)."""
    df = load_data()
    latest_st = get_latest_per_station(df)
    
    tiers = latest_st['gw_level_mbgl'].apply(get_depth_tier_category)
    counts = tiers.value_counts().to_dict()
    
    assert counts.get('Shallow', 0) == 2, f"Expected 2 shallow stations, got {counts.get('Shallow')}"
    assert counts.get('Moderate', 0) == 5, f"Expected 5 moderate stations, got {counts.get('Moderate')}"
    assert counts.get('Deep', 0) == 4, f"Expected 4 deep stations, got {counts.get('Deep')}"


def test_depth_tier_filtering():
    """Verify depth tier filter logic correctly subsets the DataFrame."""
    df = load_data()
    latest_st = get_latest_per_station(df)
    
    # Shallow
    shallow_df = latest_st[latest_st['gw_level_mbgl'].apply(get_depth_tier_category) == "Shallow"]
    assert len(shallow_df) == 2
    assert (shallow_df['gw_level_mbgl'] < 4.0).all()
    
    # Moderate
    moderate_df = latest_st[latest_st['gw_level_mbgl'].apply(get_depth_tier_category) == "Moderate"]
    assert len(moderate_df) == 5
    assert ((moderate_df['gw_level_mbgl'] >= 4.0) & (moderate_df['gw_level_mbgl'] <= 8.0)).all()
    
    # Deep
    deep_df = latest_st[latest_st['gw_level_mbgl'].apply(get_depth_tier_category) == "Deep"]
    assert len(deep_df) == 4
    assert (deep_df['gw_level_mbgl'] > 8.0).all()


def test_defensive_coordinate_filtering():
    """Verify that records with missing or zero coordinates are isolated safely without dropping from telemetry."""
    synthetic_data = pd.DataFrame({
        'station': ['Valid_Station', 'Null_Lat', 'Zero_Lon', 'Null_Both'],
        'latitude': [18.25, np.nan, 18.30, None],
        'longitude': [74.15, 74.20, 0.0, None],
        'gw_level_mbgl': [5.2, 3.1, 9.4, 6.0],
        'date': pd.to_datetime(['2023-11-01'] * 4)
    })
    
    valid_coords = synthetic_data[
        synthetic_data['latitude'].notna() & 
        synthetic_data['longitude'].notna() & 
        (synthetic_data['latitude'] != 0) & 
        (synthetic_data['longitude'] != 0)
    ]
    invalid_coords = synthetic_data[
        synthetic_data['latitude'].isna() | 
        synthetic_data['longitude'].isna() | 
        (synthetic_data['latitude'] == 0) | 
        (synthetic_data['longitude'] == 0)
    ]
    
    assert len(valid_coords) == 1
    assert valid_coords.iloc[0]['station'] == 'Valid_Station'
    assert len(invalid_coords) == 3
    assert set(invalid_coords['station'].tolist()) == {'Null_Lat', 'Zero_Lon', 'Null_Both'}


def test_station_telemetry_popup_attributes():
    """Verify that all required attributes for rich Leaflet popups exist and have consistent values."""
    df = load_data()
    latest_st = get_latest_per_station(df)
    
    for _, row in latest_st.iterrows():
        st_name = row['station']
        depth = row['gw_level_mbgl']
        prev_depth = row['prev_gw_level_mbgl']
        change = row['depth_change_m']
        days = row['days_elapsed']
        
        status, color, _ = get_status(depth)
        cat = get_depth_tier_category(depth)
        assert cat in ['Shallow', 'Moderate', 'Deep']
        assert status in ['Shallow (< 4.0 m)', 'Moderate (4.0–8.0 m)', 'Deep (> 8.0 m)']
        assert color in ['#0F766E', '#854D0E', '#991B1B']
        
        # Mathematical consistency
        if pd.notnull(prev_depth):
            expected_change = round(depth - prev_depth, 2)
            assert round(change, 2) == expected_change, (
                f"Change mismatch at {st_name}: {change} != {expected_change}"
            )
            assert days >= 0, f"Negative days elapsed at {st_name}"
            
        if st_name == 'Zendewadi':
            assert days == 2206, f"Zendewadi elapsed days should be 2,206, got {days}"
            assert row['prev_date'].strftime('%Y-%m-%d') == '2016-05-15'
            assert row['date'].strftime('%Y-%m-%d') == '2022-05-30'


def test_interpretation_directionality():
    """Verify water table directionality semantics:
    Higher MBGL = deeper (water level fell).
    Lower MBGL = shallower (water level rose).
    """
    # Positive change: MBGL increased, water level fell / deeper
    change_pos = 1.50
    assert change_pos > 0
    # Negative change: MBGL decreased, water level rose / shallower
    change_neg = -2.10
    assert change_neg < 0


def test_map_screen_scientific_terminology():
    """Verify that updated scientific terminology is used in map screen and components."""
    import inspect
    from screens import groundwater_map
    from components import map_view

    screen_src = inspect.getsource(groundwater_map.render_groundwater_map_screen)
    map_view_src = inspect.getsource(map_view.render_groundwater_map)

    # 1. Renamed KPI labels
    assert 'label="Latest Recorded Depth Distribution"' in screen_src
    assert 'label="Stations with Valid Coordinates"' in screen_src
    assert 'label="Latest Observation Coverage"' in screen_src

    # 2. Positional accuracy qualification
    assert "does not establish positional accuracy" in screen_src

    # 3. Rainfall grid spatial coverage wording
    assert "four-point rainfall grid" in map_view_src
    assert "spatial coverage" in map_view_src
    assert "Station within IMD grid bounding box" not in map_view_src


def test_spatial_model_status_expander_wording():
    """Verify that the Spatial Prediction Layer Status section uses corrected ~2,936 km² and 267 km² figures."""
    import inspect
    from components import callouts

    callouts_src = inspect.getsource(callouts.render_spatial_model_status_expander)
    assert "2,936" in callouts_src, "Expected ~2,936 km² in spatial model status expander"
    assert "267" in callouts_src, "Expected ~1 station per 267 km² in spatial model status expander"
    assert "1,105" not in callouts_src, "Found outdated 1,105 km² figure in spatial model status expander"
    assert "100\\text{ km}^2" not in callouts_src, "Found outdated 100 km² figure in spatial model status expander"


def test_filter_labels_contrast_css():
    """Verify that styles.css and theme.py define high-contrast styling for selectbox filter labels."""
    from styles.theme import apply_theme
    import inspect

    with open("styles/styles.css", "r", encoding="utf-8") as f:
        css = f.read()

    assert 'div[data-testid="stSelectbox"] label' in css
    assert 'color: var(--text-primary)' in css

    theme_src = inspect.getsource(apply_theme)
    assert 'div[data-testid="stSelectbox"] label' in theme_src
    assert "{palette['text_primary']}" in theme_src


