"""Unit tests for physical depth tier classification and intervention planning."""
import pytest
from services.data_loader import (
    get_depth_tier,
    get_depth_tier_category,
    get_status,
    get_intervention_plan,
    load_data,
    get_latest_per_station,
)


def test_depth_below_4m():
    """Verify depths below 4.0 m are classified as Shallow phreatic tier."""
    test_values = [-0.40, 0.0, 1.25, 2.50, 3.99]
    for d in test_values:
        tier_label, color, badge = get_depth_tier(d)
        assert tier_label == "Shallow (< 4.0 m)", f"Failed for depth {d}"
        assert color == "#0F766E"
        assert badge == "badge-shallow"
        assert get_depth_tier_category(d) == "Shallow"
        
        plan = get_intervention_plan(d)
        assert plan["category"] == "Shallow"
        assert plan["icon"] == "🟢"
        assert plan["priority"] == "Sustainable Level Maintained"
        assert len(plan["actions"]) > 0


def test_depth_exactly_4m():
    """Verify depth of exactly 4.0 m is classified as Moderate boundary tier."""
    d = 4.00
    tier_label, color, badge = get_depth_tier(d)
    assert tier_label == "Moderate (4.0–8.0 m)"
    assert color == "#854D0E"
    assert badge == "badge-moderate"
    assert get_depth_tier_category(d) == "Moderate"
    
    plan = get_intervention_plan(d)
    assert plan["category"] == "Moderate"
    assert plan["icon"] == "🟡"
    assert plan["priority"] == "Moderate Depletion Precaution"
    assert len(plan["actions"]) > 0


def test_depth_between_4m_and_8m():
    """Verify depths between 4.0 m and 8.0 m are classified as Moderate tier."""
    test_values = [4.01, 5.06, 6.20, 7.08, 7.99]
    for d in test_values:
        tier_label, color, badge = get_depth_tier(d)
        assert tier_label == "Moderate (4.0–8.0 m)", f"Failed for depth {d}"
        assert color == "#854D0E"
        assert badge == "badge-moderate"
        assert get_depth_tier_category(d) == "Moderate"
        
        plan = get_intervention_plan(d)
        assert plan["category"] == "Moderate"
        assert plan["icon"] == "🟡"
        assert plan["priority"] == "Moderate Depletion Precaution"
        assert len(plan["actions"]) > 0


def test_depth_exactly_8m():
    """Verify depth of exactly 8.0 m is classified as Moderate boundary tier."""
    d = 8.00
    tier_label, color, badge = get_depth_tier(d)
    assert tier_label == "Moderate (4.0–8.0 m)"
    assert color == "#854D0E"
    assert badge == "badge-moderate"
    assert get_depth_tier_category(d) == "Moderate"
    
    plan = get_intervention_plan(d)
    assert plan["category"] == "Moderate"
    assert plan["icon"] == "🟡"
    assert plan["priority"] == "Moderate Depletion Precaution"
    assert len(plan["actions"]) > 0


def test_depth_above_8m():
    """Verify depths above 8.0 m are classified as Deep stress tier."""
    test_values = [8.01, 8.34, 8.48, 10.50, 16.0]
    for d in test_values:
        tier_label, color, badge = get_depth_tier(d)
        assert tier_label == "Deep (> 8.0 m)", f"Failed for depth {d}"
        assert color == "#991B1B"
        assert badge == "badge-deep"
        assert get_depth_tier_category(d) == "Deep"
        
        plan = get_intervention_plan(d)
        assert plan["category"] == "Deep"
        assert plan["icon"] == "🔴"
        assert plan["priority"] == "High Priority Intervention Advisory"
        assert len(plan["actions"]) > 0


def test_station_telemetry_intervention_coverage():
    """Verify all 11 stations in Purandar Taluka produce valid plans across physical tiers."""
    df = load_data()
    latest_st = get_latest_per_station(df)
    assert len(latest_st) == 11
    
    categories_found = set()
    for _, row in latest_st.iterrows():
        plan = get_intervention_plan(row["gw_level_mbgl"])
        categories_found.add(plan["category"])
        assert plan["icon"] in ["🔴", "🟡", "🟢"]
        assert len(plan["actions"]) >= 2
        
    # Purandar has stations across all physical depth tiers
    assert "Deep" in categories_found, "Deep stations missing in telemetry"
    assert "Moderate" in categories_found, "Moderate stations missing in telemetry"
    assert "Shallow" in categories_found, "Shallow stations missing in telemetry"
