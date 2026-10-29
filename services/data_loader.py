"""Data loading, feature preparation, and physical depth classification services for BhujalDrishti."""
import pandas as pd
import streamlit as st

EXTRAPOLATED_STATIONS = {
    'Pimpri (Kh) Malvasti',
    'Kamatwadi-Walha',
    'Walha',
    'Narayanpur'
}


@st.cache_data
def load_data(filepath: str = "data/processed/purandar_groundwater_features.csv") -> pd.DataFrame:
    """Load processed groundwater dataset with calendar lookbacks and extrapolation flags."""
    df = pd.read_csv(filepath)
    df['date'] = pd.to_datetime(df['date'])
    
    # Defensive verification of rainfall extrapolation flag
    if 'is_rainfall_extrapolated' not in df.columns:
        df['is_rainfall_extrapolated'] = df['station'].apply(
            lambda s: 1 if s in EXTRAPOLATED_STATIONS else 0
        )
    return df


def get_latest_per_station(df: pd.DataFrame) -> pd.DataFrame:
    """Calculate the latest observed telemetry snapshot per monitoring station."""
    latest = df.sort_values('date').groupby('station').last().reset_index()
    if 'is_rainfall_extrapolated' not in latest.columns:
        latest['is_rainfall_extrapolated'] = latest['station'].apply(
            lambda s: 1 if s in EXTRAPOLATED_STATIONS else 0
        )
    return latest


def get_depth_tier_category(mbgl: float | None) -> str:
    """Return canonical tier category string: 'Shallow', 'Moderate', 'Deep', or 'Unknown'.
    
    Boundary definitions:
    - Shallow: mbgl < 4.0 m
    - Moderate: 4.0 <= mbgl <= 8.0 m (inclusive of boundary values 4.0 m and 8.0 m)
    - Deep: mbgl > 8.0 m
    - Unknown: missing, NaN, non-numeric, or invalid values
    
    Note: These tiers are project-defined physical reference bands for instantaneous
    telemetry visualization. They do not constitute official Central Ground Water Board
    (CGWB) or Groundwater Estimation Committee (GEC) administrative exploitation categories.
    """
    if mbgl is None:
        return "Unknown"
    try:
        val = float(mbgl)
        if pd.isna(val):
            return "Unknown"
    except (ValueError, TypeError):
        return "Unknown"
        
    if val < 4.0:
        return "Shallow"
    elif val <= 8.0:
        return "Moderate"
    else:
        return "Deep"


def get_depth_tier(mbgl: float | None) -> tuple[str, str, str]:
    """Classify water table depth into project-defined physical reference tiers.
    
    Returns:
        (tier_label, hex_color, badge_css_class)
    """
    cat = get_depth_tier_category(mbgl)
    if cat == "Shallow":
        return "Shallow (< 4.0 m)", "#0F766E", "badge-shallow"
    elif cat == "Moderate":
        return "Moderate (4.0–8.0 m)", "#854D0E", "badge-moderate"
    elif cat == "Deep":
        return "Deep (> 8.0 m)", "#991B1B", "badge-deep"
    else:
        return "Unknown / Unclassified", "#64748B", "badge-unknown"


def get_status(mbgl: float | None) -> tuple[str, str, str]:
    """Backward-compatible alias for get_depth_tier."""
    return get_depth_tier(mbgl)


def get_intervention_plan(mbgl: float | None) -> dict:
    """Return rule-based conservation advisories corresponding to physical depth tiers.
    
    Advisory notes:
    Recommendations are rule-based hydrogeological heuristics synthesized from standard
    CGWB and GSDA watershed guidelines for preliminary decision support. Water table depth
    alone does not prove groundwater depletion, establish its localized root causes (e.g.
    lithological variation, fracture connectivity, localized pumping, or recharge dynamics),
    or prove the necessity of a specific engineering structure at a site.
    All structural interventions require localized on-site hydrogeological, geophysical,
    and civil feasibility surveys prior to implementation.
    """
    cat = get_depth_tier_category(mbgl)
    if cat == "Deep":
        return {
            "category": "Deep",
            "tier_label": "Deep (> 8.0 m)",
            "icon": "🔴",
            "color": "#991B1B",
            "badge": "badge-deep",
            "priority": "High-Vulnerability Monitoring & Conservation Advisory",
            "priority_level": "Deep Reference Tier (> 8.0 m MBGL)",
            "actions": [
                ("Artificial Recharge Exploration", "Prioritize site feasibility surveys for percolation structures and check dams in regional drainage paths where local basalt fracturing supports infiltration."),
                ("Extraction Monitoring & Pumping Review", "Conduct voluntary monitoring of local extraction rates and recommend voluntary seasonal pumping moderation during peak summer dry periods."),
                ("Crop Water Management Advisory", "Promote transition of water-intensive summer crops toward drought-resilient pulses, millets, and drip-irrigated horticulture (custard apple, pomegranate)."),
                ("Lined Farm Storage (Shet-Tale)", "Encourage plastic lining for farm storage ponds where porous soil conditions lead to high percolation losses.")
            ]
        }
    elif cat == "Moderate":
        return {
            "category": "Moderate",
            "tier_label": "Moderate (4.0–8.0 m)",
            "icon": "🟡",
            "color": "#854D0E",
            "badge": "badge-moderate",
            "priority": "Precautionary Stewardship & Recharge Advisory",
            "priority_level": "Moderate Reference Tier (4.0–8.0 m MBGL)",
            "actions": [
                ("Contour Bunding & Soil Moisture Conservation", "Implement ridge-to-valley soil moisture conservation and continuous contour trenches (CCT) on upper slope lands to enhance infiltration lag time."),
                ("Micro-Irrigation Adoption", "Promote expanded drip and micro-sprinkler irrigation systems for fig, vegetable, and orchard farming to optimize irrigation water efficiency."),
                ("Rooftop Rainwater Harvesting", "Incentivize injection well recharge and direct rooftop harvesting for institutional, gram panchayat, and residential structures.")
            ]
        }
    elif cat == "Shallow":
        return {
            "category": "Shallow",
            "tier_label": "Shallow (< 4.0 m)",
            "icon": "🟢",
            "color": "#0F766E",
            "badge": "badge-shallow",
            "priority": "Equilibrium Maintenance & Monitoring Advisory",
            "priority_level": "Shallow Reference Tier (< 4.0 m MBGL)",
            "actions": [
                ("Aquifer Monitoring & Vigilance", "Continue systematic quarterly water level observation; avoid concentrated deep extraction that could induce localized drawdown cones."),
                ("Participatory Community Water Budgeting", "Conduct bi-annual village participatory water audits at Gram Sabha meetings prior to rabi cropping season to maintain safe yields.")
            ]
        }
    else:  # Unknown / Invalid / Missing depth
        return {
            "category": "Unknown",
            "tier_label": "Unknown / Unclassified",
            "icon": "⚪",
            "color": "#64748B",
            "badge": "badge-unknown",
            "priority": "Telemetry Unavailable / Unclassified",
            "priority_level": "Data Incomplete (Unrecorded MBGL)",
            "actions": [
                ("Verify Station Telemetry", "Observation depth is missing, invalid, or unrecorded. Confirm physical well monitoring records before assessing hydrogeological status."),
                ("Conduct In-Situ Measurement", "Perform in-situ manual sounder or acoustic probe measurement to establish current water table depth before formulating watershed interventions.")
            ]
        }
