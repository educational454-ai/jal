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
    """Calculate the latest observed telemetry snapshot per monitoring station,
    including immediately previous observation metrics, elapsed days, and depth change.
    
    All calculations are performed dynamically from the sorted observation series.
    """
    df_sorted = df.sort_values(['station', 'date']).copy()
    
    # Calculate previous observation date, depth, and total records dynamically per station
    df_sorted['prev_date'] = df_sorted.groupby('station')['date'].shift(1)
    df_sorted['prev_gw_level_mbgl'] = df_sorted.groupby('station')['gw_level_mbgl'].shift(1)
    df_sorted['total_station_records'] = df_sorted.groupby('station')['date'].transform('count')
    
    # Extract the latest record per station
    latest = df_sorted.groupby('station').last().reset_index()
    
    # Calculate depth change in metres (latest MBGL - previous MBGL)
    # Positive = deeper below ground (water level fell); Negative = shallower (water level rose)
    latest['depth_change_m'] = latest['gw_level_mbgl'] - latest['prev_gw_level_mbgl']
    
    # Calculate elapsed calendar days between observations
    latest['days_elapsed'] = (latest['date'] - latest['prev_date']).dt.days
    
    if 'is_rainfall_extrapolated' not in latest.columns:
        latest['is_rainfall_extrapolated'] = latest['station'].apply(
            lambda s: 1 if s in EXTRAPOLATED_STATIONS else 0
        )
    return latest


def get_seasonal_matched_comparison(df: pd.DataFrame) -> dict:
    """Compute seasonal groundwater comparison between May (pre-monsoon) and 
    November (post-monsoon) using strictly matched station-year pairs.
    
    A pair is valid if and only if observations exist for both May and November
    at the exact same monitoring station within the same calendar year.
    
    Returns a dictionary containing:
    - has_data: bool
    - count: int (number of matched pairs)
    - year_min: int | None (earliest observation year with matched pairs)
    - year_max: int | None (latest observation year with matched pairs)
    - mean_change_m: float | None (mean November MBGL - May MBGL)
    - median_rise_m: float | None (median May MBGL - November MBGL)
    - pairs_df: pd.DataFrame (all matched observation pairs)
    - yearly_summary: pd.DataFrame (annual aggregations of matched pairs)
    """
    empty_result = {
        "has_data": False,
        "count": 0,
        "year_min": None,
        "year_max": None,
        "mean_change_m": None,
        "median_rise_m": None,
        "pairs_df": pd.DataFrame(),
        "yearly_summary": pd.DataFrame()
    }
    
    if df is None or df.empty or 'date' not in df.columns or 'gw_level_mbgl' not in df.columns or 'station' not in df.columns:
        return empty_result
        
    clean_df = df.dropna(subset=['gw_level_mbgl', 'date', 'station']).copy()
    if clean_df.empty:
        return empty_result
        
    if not pd.api.types.is_datetime64_any_dtype(clean_df['date']):
        clean_df['date'] = pd.to_datetime(clean_df['date'])
        
    clean_df['year'] = clean_df['date'].dt.year
    clean_df['month'] = clean_df['date'].dt.month
    
    # Filter May (pre-monsoon) and November (post-monsoon) observations
    may_df = clean_df[clean_df['month'] == 5]
    nov_df = clean_df[clean_df['month'] == 11]
    
    if may_df.empty or nov_df.empty:
        return empty_result
        
    # Deduplicate in case of multiple observations per station-year-month (keep latest chronological)
    may_unique = may_df.sort_values('date').groupby(['station', 'year']).last().reset_index()
    nov_unique = nov_df.sort_values('date').groupby(['station', 'year']).last().reset_index()
    
    # Strictly matched station-year pairs
    pairs = pd.merge(
        may_unique[['station', 'year', 'gw_level_mbgl', 'date']].rename(
            columns={'gw_level_mbgl': 'may_mbgl', 'date': 'may_date'}
        ),
        nov_unique[['station', 'year', 'gw_level_mbgl', 'date']].rename(
            columns={'gw_level_mbgl': 'nov_mbgl', 'date': 'nov_date'}
        ),
        on=['station', 'year'],
        how='inner'
    )
    
    if len(pairs) == 0:
        return empty_result
        
    # Depth change: November MBGL - May MBGL
    # Negative indicates water table is closer to surface (shallower)
    pairs['depth_change_m'] = pairs['nov_mbgl'] - pairs['may_mbgl']
    
    # Water table rise: May MBGL - November MBGL (-depth_change_m)
    # Positive indicates water level ascended towards surface
    pairs['water_table_rise_m'] = pairs['may_mbgl'] - pairs['nov_mbgl']
    
    # Annual summary of matched pairs
    yearly = pairs.groupby('year').agg(
        n_pairs=('station', 'count'),
        may_mean=('may_mbgl', 'mean'),
        nov_mean=('nov_mbgl', 'mean'),
        mean_change=('depth_change_m', 'mean'),
        median_rise=('water_table_rise_m', 'median')
    ).reset_index().sort_values('year')
    
    return {
        "has_data": True,
        "count": int(len(pairs)),
        "year_min": int(pairs['year'].min()),
        "year_max": int(pairs['year'].max()),
        "mean_change_m": float(pairs['depth_change_m'].mean()),
        "median_rise_m": float(pairs['water_table_rise_m'].median()),
        "pairs_df": pairs,
        "yearly_summary": yearly
    }


def get_rainfall_groundwater_correlations(df: pd.DataFrame) -> dict:
    """Compute dynamic Pearson and Spearman rank correlations between antecedent
    rainfall accumulation lookback windows and observed groundwater levels (m MBGL).
    
    Returns structured metrics dict with defensive fallbacks.
    """
    default_result = {
        "has_data": False,
        "n_obs": 0,
        "n_years": 0,
        "windows": {},
        "annual_windows": {}
    }
    if df is None or df.empty or 'gw_level_mbgl' not in df.columns:
        return default_result

    target_windows = ['rain_90d', 'rain_180d', 'rain_365d']
    available_windows = [w for w in target_windows if w in df.columns]
    if not available_windows:
        return default_result

    clean_df = df.dropna(subset=['gw_level_mbgl'] + available_windows).copy()
    if len(clean_df) < 5:
        return default_result

    results = {
        "has_data": True,
        "n_obs": int(len(clean_df)),
        "n_years": 0,
        "windows": {},
        "annual_windows": {}
    }

    for w in available_windows:
        p_val = clean_df['gw_level_mbgl'].corr(clean_df[w], method='pearson')
        s_val = clean_df['gw_level_mbgl'].corr(clean_df[w], method='spearman')
        results["windows"][w] = {
            "pearson": float(p_val) if pd.notnull(p_val) else 0.0,
            "spearman": float(s_val) if pd.notnull(s_val) else 0.0,
            "mean_mm": float(clean_df[w].mean()),
            "median_mm": float(clean_df[w].median()),
        }

    # Annual level correlations if 'year' is present
    if 'year' in clean_df.columns:
        agg_dict = {'gw_level_mbgl': 'mean'}
        for w in available_windows:
            agg_dict[w] = 'mean'
        annual = clean_df.groupby('year').agg(agg_dict).reset_index()
        results["n_years"] = int(len(annual))
        for w in available_windows:
            p_val = annual['gw_level_mbgl'].corr(annual[w], method='pearson')
            s_val = annual['gw_level_mbgl'].corr(annual[w], method='spearman')
            results["annual_windows"][w] = {
                "pearson": float(p_val) if pd.notnull(p_val) else 0.0,
                "spearman": float(s_val) if pd.notnull(s_val) else 0.0,
            }

    return results


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
    """Return rule-based conservation advisories corresponding to project-defined physical depth tiers.
    
    Advisory notes:
    Recommendations are rule-based hydrogeological heuristics synthesized from standard
    CGWB and GSDA watershed guidelines for preliminary decision support. Depth categories
    (< 4.0 m, 4.0–8.0 m, > 8.0 m MBGL) are project-defined physical reference categories,
    not official CGWB vulnerability or groundwater safety classifications. Water table depth
    alone does not prove groundwater depletion, establish localized root causes, or prove
    the necessity of a specific engineering structure at a site.
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
            "priority": "Deep Reference Tier — Enhanced Assessment Advisory",
            "priority_level": "Deep Reference Tier (> 8.0 m MBGL)",
            "actions": [
                ("Artificial Recharge Feasibility Assessment", "Evaluate check dams and percolation structures as preliminary recharge options, strictly requiring site-specific geological, hydrogeological, and infiltration feasibility assessment."),
                ("Voluntary Extraction Monitoring & Pumping Review", "Maintain voluntary extraction monitoring and seasonal pumping reviews to assess local water table behavior during peak summer dry periods."),
                ("Crop Water Management Options", "Explore crop transitions toward drought-resilient varieties and high-efficiency drip irrigation as locally assessed agricultural options, rather than blanket prescriptions."),
                ("Farm Storage Pond Lining Assessment (Shet-Tale)", "Assess farm storage pond lining requirements based on site-specific soil and water-retention characteristics, avoiding unnecessary lining where native soils demonstrate low permeability.")
            ]
        }
    elif cat == "Moderate":
        return {
            "category": "Moderate",
            "tier_label": "Moderate (4.0–8.0 m)",
            "icon": "🟡",
            "color": "#854D0E",
            "badge": "badge-moderate",
            "priority": "Moderate Reference Tier — Conservation Advisory",
            "priority_level": "Moderate Reference Tier (4.0–8.0 m MBGL)",
            "actions": [
                ("Contour Bunding & Continuous Contour Trenches (CCT)", "Consider ridge-to-valley contour bunding and continuous contour trenches (CCT) as preliminary soil and water conservation options, subject to local terrain slope and soil depth suitability."),
                ("Micro-Irrigation Adoption", "Support drip and micro-sprinkler irrigation systems as water-efficiency options suited to local agricultural conditions."),
                ("Rooftop Rainwater Harvesting & Managed Recharge", "Promote direct rooftop rainwater collection for local storage. Distinguish rooftop collection from groundwater injection: any potential injection well recharge must require site-specific hydrogeological and water-quality assessment.")
            ]
        }
    elif cat == "Shallow":
        return {
            "category": "Shallow",
            "tier_label": "Shallow (< 4.0 m)",
            "icon": "🟢",
            "color": "#0F766E",
            "badge": "badge-shallow",
            "priority": "Shallow Reference Tier — Monitoring Advisory",
            "priority_level": "Shallow Reference Tier (< 4.0 m MBGL)",
            "actions": [
                ("Aquifer Monitoring & Surveillance", "Conduct systematic water level observations under a proposed quarterly monitoring schedule (noting that historical dataset soundings were irregular); avoid concentrated deep extraction that could induce localized drawdown cones."),
                ("Participatory Community Water Budgeting", "Encourage village participatory water budgeting at Gram Sabha meetings prior to the rabi cropping season as a suggested participatory planning measure for local water-resource planning.")
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
