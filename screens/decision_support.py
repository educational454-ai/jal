"""Conservation Decision Support screen implementation for BhujalDrishti.

Includes:
- Section 1: Page Heading & Clear Preliminary Planning Introduction
- Section 2: AI-Powered Station Advisory Workbench (Main Focus Near Top)
- Section 3: Taluka-Wide Planning, Prioritization & Station Cards
- Section 4: Scientific Assumptions, Limitations & Methodological Boundaries
"""
import pandas as pd
import streamlit as st

from services.data_loader import (
    get_latest_per_station,
    get_depth_tier_category,
    get_depth_tier,
    get_intervention_plan
)
from services.gemini_service import (
    generate_station_advisory,
    is_gemini_configured,
    get_configured_model_id,
    DEFAULT_GEMINI_MODEL,
    compute_station_cache_key,
    PROMPT_SCHEMA_VERSION,
)
from components.callouts import render_decision_support_advisory_notice


def render_ai_station_advisory_section(
    df: pd.DataFrame,
    models: dict | None = None,
    initial_station: str | None = None
) -> None:
    """Render the AI-Powered Station Advisory workbench with caching, explicit trigger, and deterministic fallback."""
    st.markdown('<div class="ai-advisory-container">', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="ai-advisory-section-header">
        <div class="ai-section-title">🤖 Station Advisory Workbench</div>
        <div class="ai-section-subtitle">Station-specific hydrogeological decision support synthesized via Gemini API with deterministic rule-based fallback</div>
    </div>
    """, unsafe_allow_html=True)

    # Station selection for AI Advisory
    all_stations = sorted(df['station'].dropna().unique().tolist())
    if not all_stations:
        st.info("No monitoring station data available for advisory synthesis.")
        st.markdown('</div>', unsafe_allow_html=True)
        return

    # Determine default station index
    if "ds_ai_station_selector" in st.session_state and st.session_state["ds_ai_station_selector"] in all_stations:
        default_idx = all_stations.index(st.session_state["ds_ai_station_selector"])
    elif initial_station and initial_station in all_stations:
        default_idx = all_stations.index(initial_station)
    else:
        default_idx = 0

    col_sel, col_status = st.columns([2.2, 1.3])
    with col_sel:
        selected_st = st.selectbox(
            "Select Monitoring Station for Advisory",
            options=all_stations,
            index=default_idx,
            key="ds_ai_station_selector",
            help="Select a monitoring station to view latest telemetry and synthesize an explainable hydrogeological advisory."
        )

    model_id = get_configured_model_id() or DEFAULT_GEMINI_MODEL
    gemini_configured = is_gemini_configured()

    with col_status:
        if gemini_configured:
            st.markdown(
                f'<div style="margin-top: 28px; padding: 7px 12px; background-color: var(--bg-secondary); border: 1px solid var(--border-color); border-radius: 6px; font-size: 0.78rem; color: var(--teal-accent);">'
                f'✨ <b>Gemini Ready:</b> <code>{model_id}</code>'
                f'</div>',
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                f'<div style="margin-top: 28px; padding: 7px 12px; background-color: var(--alert-warning-bg); border: 1px solid var(--alert-warning-border); border-radius: 6px; font-size: 0.78rem; color: var(--alert-warning-text);">'
                f'ℹ️ <b>Baseline Active:</b> Key Unconfigured'
                f'</div>',
                unsafe_allow_html=True
            )

    # Informational card explaining how the advisory works
    st.markdown("""
    <div class="ds-advisory-intro-card">
        <b>How Station Advisories Work:</b> Select an eligible monitoring station and click <b>Generate Advisory</b> below. 
        The system evaluates historical depth soundings, lookback precipitation, project reference tiers, and the Random Forest ML forecast to generate practical conservation actions.
        <div style="margin-top: 6px; font-size: 0.80rem; color: var(--text-secondary);">
            • <b>Deterministic Heuristic vs. Gemini AI:</b> If Gemini API is configured, it synthesizes clear natural-language explanations; if unconfigured or unreachable, the verified deterministic heuristic baseline is displayed.<br>
            • <b>Model Boundary:</b> Gemini provides narrative synthesis and explanations; it does <b>NOT</b> generate or replace the Random Forest machine learning forecast.
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Initialize session state cache
    if "ds_ai_advisory_cache" not in st.session_state:
        st.session_state["ds_ai_advisory_cache"] = {}

    cache_key = compute_station_cache_key(selected_st, df, models=models, model_id=model_id)
    is_cached = cache_key in st.session_state["ds_ai_advisory_cache"]

    # Action buttons
    col_btn1, col_btn2 = st.columns([1.6, 3])
    generate_clicked = False
    regenerate_clicked = False

    with col_btn1:
        if not is_cached:
            generate_clicked = st.button(
                f"✨ Generate Advisory for {selected_st}",
                key=f"ds_btn_gen_{selected_st}",
                type="primary",
                help=f"Synthesize an explainable advisory for {selected_st} using Gemini (or project heuristic fallback)."
            )
        else:
            regenerate_clicked = st.button(
                f"🔄 Refresh / Regenerate ({selected_st})",
                key=f"ds_btn_regen_{selected_st}",
                help="Invalidate current cached advisory and re-query Gemini API."
            )

    if generate_clicked or regenerate_clicked:
        with st.spinner(f"Synthesizing hydrogeological advisory for {selected_st}..."):
            advisory_data = generate_station_advisory(selected_st, df, models=models, model_id=model_id)
            st.session_state["ds_ai_advisory_cache"][cache_key] = advisory_data
            is_cached = True

    # Render Panel Content
    if not is_cached:
        # User has not clicked generate yet for this station
        st.markdown(
            f'<div class="ai-advisory-cta-card">'
            f'<div class="ai-cta-icon">💡</div>'
            f'<div class="ai-cta-body">'
            f'<div class="ai-cta-title">Synthesize Station-Specific Advisory for {selected_st}</div>'
            f'<div class="ai-cta-desc">'
            f'Click <b>Generate Advisory for {selected_st}</b> to evaluate historical depth soundings, '
            f'rainfall indicators, project reference tiers, and ML forecasts. '
            f'If Gemini is unconfigured or unreachable, the project heuristic baseline will be displayed.'
            f'</div>'
            f'</div>'
            f'</div>',
            unsafe_allow_html=True
        )
    else:
        advisory = st.session_state["ds_ai_advisory_cache"][cache_key]
        is_fallback = advisory.get("is_fallback", False)
        fallback_reason = advisory.get("fallback_reason")

        # Status Banner
        if is_fallback:
            st.markdown(
                f'<div class="ai-banner-fallback">'
                f'<div class="ai-banner-header">⚠️ Project-Defined Heuristic Baseline Active</div>'
                f'<div class="ai-banner-desc">AI generation was unavailable ({fallback_reason or "Unconfigured API key"}). '
                f'Displaying project-defined rule-based baseline advisory (not official government guidance).</div>'
                f'</div>',
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                f'<div class="ai-banner-success">'
                f'<div class="ai-banner-header">✨ AI-Generated Preliminary Advisory ({advisory.get("model_id", model_id)})</div>'
                f'<div class="ai-banner-desc">Synthesized from verified station telemetry, antecedent rainfall context, and ML forecasts.</div>'
                f'</div>',
                unsafe_allow_html=True
            )

        # Preliminary Planning Notice
        st.markdown(
            '<div class="ai-preliminary-notice">'
            '⚠️ <b>Preliminary Planning Notice:</b> This advisory is generated as preliminary decision-support exploration. '
            'It does not constitute official Central Ground Water Board (CGWB) or Ground Water Surveys and Development Agency (GSDA) '
            'statutory guidance, groundwater exploitation categorization, or certified civil engineering design.'
            '</div>',
            unsafe_allow_html=True
        )

        # Station Telemetry Header Card
        obs_depth = advisory.get('observed_depth_mbgl', 0.0)
        supp_ev = advisory.get('supporting_evidence', {})
        obs_date = supp_ev.get('observation_date', 'N/A')
        tier_label = advisory.get('physical_depth_tier', 'Unknown')
        
        tier_cat = get_depth_tier_category(obs_depth)
        badge_class = "badge-deep" if tier_cat == "Deep" else ("badge-moderate" if tier_cat == "Moderate" else "badge-shallow")

        summary_heading = "📋 Project-Defined Heuristic Baseline Summary" if is_fallback else "✨ AI-Synthesized Advisory Summary"
        summary_border_style = 'style="border-left-color: var(--alert-warning-border);"' if is_fallback else 'style="border-left-color: var(--teal-accent);"'

        st.markdown(
            f'<div class="ai-telemetry-header-card">'
            f'<div class="ai-telemetry-item">'
            f'<span class="ai-telemetry-label">Monitoring Station</span>'
            f'<span class="ai-telemetry-val">{selected_st}</span>'
            f'</div>'
            f'<div class="ai-telemetry-item">'
            f'<span class="ai-telemetry-label">Latest Measured Depth</span>'
            f'<span class="ai-telemetry-val">{obs_depth:.2f} m MBGL</span>'
            f'<span style="font-size: 0.70rem; color: var(--text-muted); font-weight: 500;">(Manual Tape Sounding)</span>'
            f'</div>'
            f'<div class="ai-telemetry-item">'
            f'<span class="ai-telemetry-label">Recorded Observation Date</span>'
            f'<span class="ai-telemetry-val">{obs_date}</span>'
            f'<span style="font-size: 0.70rem; color: var(--text-muted); font-weight: 500;">(Historical Survey · Not Live)</span>'
            f'</div>'
            f'<div class="ai-telemetry-item">'
            f'<span class="ai-telemetry-label">Project-Defined Tier</span>'
            f'<span class="{badge_class}">● {tier_label}</span>'
            f'</div>'
            f'</div>',
            unsafe_allow_html=True
        )

        # Advisory Summary
        st.markdown(
            f'<div class="ai-summary-card" {summary_border_style}>'
            f'<div class="ai-summary-label">{summary_heading}</div>'
            f'<div class="ai-summary-text">{advisory.get("advisory_summary", "")}</div>'
            f'</div>',
            unsafe_allow_html=True
        )

        # Recommended Actions
        st.markdown("#### Recommended Conservation & Stewardship Actions")
        actions = advisory.get("recommended_actions", [])
        if actions:
            for idx, action in enumerate(actions):
                act_title = action.get("title", f"Action {idx+1}")
                act_cat = action.get("action_category", "Conservation")
                act_desc = action.get("description", "")
                act_rationale = action.get("hydrogeological_rationale", "")
                act_precond = action.get("preconditions_and_feasibility", "")
                act_prio = action.get("priority", "Medium")

                if act_prio == "High":
                    prio_class = "ai-badge-prio-high"
                elif act_prio == "Medium":
                    prio_class = "ai-badge-prio-medium"
                else:
                    prio_class = "ai-badge-prio-low"

                st.markdown(
                    f'<div class="ai-action-card">'
                    f'<div class="ai-action-top">'
                    f'<div class="ai-action-title-group">'
                    f'<span class="ai-action-num">{idx + 1}</span>'
                    f'<span class="ai-action-title">{act_title}</span>'
                    f'</div>'
                    f'<div class="ai-action-badges">'
                    f'<span class="ai-badge-cat">{act_cat.replace("_", " ")}</span>'
                    f'<span class="{prio_class}">{act_prio} Priority</span>'
                    f'</div>'
                    f'</div>'
                    f'<div class="ai-action-desc">{act_desc}</div>'
                    f'<div class="ai-action-detail-grid">'
                    f'<div class="ai-detail-block">'
                    f'<div class="ai-detail-block-title">Hydrogeological Rationale</div>'
                    f'<div class="ai-detail-block-text">{act_rationale}</div>'
                    f'</div>'
                    f'<div class="ai-detail-block">'
                    f'<div class="ai-detail-block-title">Preconditions &amp; Feasibility</div>'
                    f'<div class="ai-detail-block-text">{act_precond}</div>'
                    f'</div>'
                    f'</div>'
                    f'</div>',
                    unsafe_allow_html=True
                )
        else:
            st.info("No specific actions listed for this station.")

        # Supporting Evidence Expander
        with st.expander("📊 Supporting Evidence & Telemetry Indicators", expanded=False):
            st.markdown(f"- **Measured Groundwater Depth**: `{obs_depth:.2f} m MBGL` observed on `{obs_date}` (*Historical in-situ manual sounding; not real-time automated telemetry*).")
            st.markdown(f"- **Project Physical Depth Tier**: `{tier_label}` (*Project-defined physical reference band: Shallow &lt; 4m, Moderate 4–8m, Deep &gt; 8m; not official CGWB classification*).")
            st.markdown(f"- **Historical Observation Context**: {supp_ev.get('historical_context', 'Historical records not available.')}")
            st.markdown(f"- **Antecedent Precipitation Context**: {supp_ev.get('rainfall_context', 'Antecedent rainfall indicators not recorded.')}")
            
            fc_ctx = supp_ev.get('forecast_context')
            if fc_ctx:
                st.markdown(f"- **Statistical ML Next-Observation Forecast**: {fc_ctx} (*Event-based prediction for the next recorded observation event; not a fixed 30/60/90-day calendar forecast*).")
            else:
                st.markdown("- **Statistical ML Next-Observation Forecast**: Ineligible (< 10 historical soundings) or forecast models unavailable (*Requires at least 10 soundings to prevent statistical overfitting*).")

        # Limitations & Uncertainty Expander
        with st.expander("⚖️ Scientific Limitations & Uncertainty", expanded=False):
            lims = advisory.get("limitations_and_uncertainty", [])
            for idx, lim in enumerate(lims, start=1):
                st.markdown(f"{idx}. {lim}")

        # Mandatory Field Verification Statement
        vf_statement = advisory.get("field_verification_statement", "")
        if vf_statement:
            st.markdown(
                f'<div class="ai-field-verification-box">'
                f'<div class="vf-icon">🛡️</div>'
                f'<div class="vf-text">'
                f'<div class="vf-title">Mandatory Field Verification Requirement</div>'
                f'<div class="vf-body">{vf_statement}</div>'
                f'</div>'
                f'</div>',
                unsafe_allow_html=True
            )

    st.markdown('</div>', unsafe_allow_html=True)


def render_decision_support_screen(df: pd.DataFrame, models: dict | None = None) -> None:
    """Render Screen 4: Conservation Decision Support Dashboard."""
    # Defensively ensure models dictionary is available for forecast lookups
    if models is None:
        try:
            from services.model_service import load_models
            models = load_models()
        except Exception:
            models = {}

    # 1. Welcome Card & High-Level Advisory Scope
    st.markdown("""
    <div class="ds-welcome-card">
        <div class="ds-welcome-eyebrow">Decision Support System · Purandar Taluka, Maharashtra</div>
        <div class="ds-welcome-title">Groundwater Conservation Decision Support</div>
        <div class="ds-welcome-desc">
            This module provides preliminary, data-driven planning insights and conservation options for Purandar Taluka based on available historical groundwater telemetry. 
            Recommendations combine deterministic hydrogeological rules with optional explainable AI synthesis to guide watershed conservation and agricultural water budgeting.
            <div style="margin-top: 10px; padding-top: 8px; border-top: 1px solid var(--border-color); font-size: 0.83rem; color: var(--callout-text-secondary, var(--text-secondary));">
                ⚠️ <b>Preliminary Advisory Notice:</b> Recommendations presented here are indicative planning heuristics synthesized for decision support. 
                They do <b>NOT</b> constitute official Central Ground Water Board (CGWB) or Ground Water Surveys and Development Agency (GSDA) statutory directives, 
                administrative exploitation categorizations, or certified civil engineering designs. 
                Site-specific geological, hydrogeological, and infiltration assessments are strictly required prior to implementing any structural recharge interventions.
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 2. Main Screen Layout Organized by Progressive Disclosure Tabs
    tab_advisory, tab_taluka, tab_limits = st.tabs([
        "🎯 Station Advisory Workbench",
        "🗺️ Taluka-Wide Planning & Prioritization",
        "⚖️ Scientific Assumptions & Limitations"
    ])

    latest_st = get_latest_per_station(df)
    total_wells = len(latest_st)

    # Calculate canonical categories dynamically
    categories = latest_st['gw_level_mbgl'].apply(get_depth_tier_category)
    deep_count = int((categories == "Deep").sum())
    moderate_count = int((categories == "Moderate").sum())
    shallow_count = int((categories == "Shallow").sum())
    unknown_count = int((categories == "Unknown").sum())

    with tab_advisory:
        # Station Advisory Workbench (Main focus near top)
        default_ai_station = latest_st.iloc[0]['station'] if not latest_st.empty else None
        render_ai_station_advisory_section(df, models=models, initial_station=default_ai_station)

    with tab_taluka:
        st.markdown("""
        <div class="ds-scope-distinction-banner">
            <b>Scope Distinction:</b> The <b>Station Advisory Workbench</b> (Tab 1) focuses on individualized telemetry and explainable conservation actions for a single selected station. 
            This section provides a <b>macro-level regional snapshot across all 11 monitoring stations</b> in Purandar Taluka to support watershed-scale planning and comparative prioritization.
        </div>
        """, unsafe_allow_html=True)

        # Taluka-Wide Summary KPI Cards
        st.subheader("Purandar Taluka Network Summary")
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.markdown(
                f'<div class="kpi-card kpi-card-total">'
                f'<div class="kpi-top">'
                f'<div class="kpi-label">Total Monitoring Stations</div>'
                f'<div class="kpi-value">{total_wells} Wells</div>'
                f'</div>'
                f'<div class="kpi-caption">CGWB monitoring stations represented in the historical dataset.</div>'
                f'</div>',
                unsafe_allow_html=True
            )
        with c2:
            st.markdown(
                f'<div class="kpi-card kpi-card-deep">'
                f'<div class="kpi-top">'
                f'<div class="kpi-label">Deep Reference Tier (> 8 m)</div>'
                f'<div class="kpi-value" style="color: var(--badge-deep-text);">{deep_count} Stations</div>'
                f'</div>'
                f'<div class="kpi-caption">Project physical tier (> 8.0 m MBGL); enhanced assessment &amp; conservation review.</div>'
                f'</div>',
                unsafe_allow_html=True
            )
        with c3:
            st.markdown(
                f'<div class="kpi-card kpi-card-moderate">'
                f'<div class="kpi-top">'
                f'<div class="kpi-label">Moderate Reference Tier (4–8 m)</div>'
                f'<div class="kpi-value" style="color: var(--badge-moderate-text);">{moderate_count} Stations</div>'
                f'</div>'
                f'<div class="kpi-caption">Project physical tier (4.0–8.0 m MBGL); soil moisture conservation &amp; micro-irrigation.</div>'
                f'</div>',
                unsafe_allow_html=True
            )
        with c4:
            st.markdown(
                f'<div class="kpi-card kpi-card-shallow">'
                f'<div class="kpi-top">'
                f'<div class="kpi-label">Shallow Reference Tier (< 4 m)</div>'
                f'<div class="kpi-value" style="color: var(--badge-shallow-text);">{shallow_count} Stations</div>'
                f'</div>'
                f'<div class="kpi-caption">Project physical tier (< 4.0 m MBGL); monitoring advisory &amp; participatory planning.</div>'
                f'</div>',
                unsafe_allow_html=True
            )

        if unknown_count > 0:
            st.warning(f"⚠️ **Incomplete Telemetry Alert**: {unknown_count} monitoring station(s) have unrecorded or missing depth measurements.")

        # Physical Depth Categories & Depth Interpretation Note
        st.markdown(
            '<div class="station-assessment-note" style="margin-top: 14px;">'
            'ℹ️ <b>Physical Depth Categories & Historical Baseline Note:</b> Depth reference categories '
            '(Shallow: &lt; 4.0 m, Moderate: 4.0–8.0 m, Deep: &gt; 8.0 m MBGL) are project-defined physical reference categories based on each station\'s latest available historical observation, '
            '<b>not current live groundwater conditions</b>. They do not constitute official Central Ground Water Board (CGWB) vulnerability, '
            'critical status, or groundwater safety classifications. '
            'Importantly, <b>water table depth alone does not prove aquifer depletion, extraction stress, recharge potential, or total aquifer storage</b>.'
            '</div>',
            unsafe_allow_html=True
        )

        st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
        st.subheader("Station Assessment & Prioritization")

        # Filters toolbar
        with st.container():
            f1, f2, f3 = st.columns([1.5, 1.3, 1.2])
            with f1:
                station_search = st.text_input(
                    "Search Station",
                    "",
                    placeholder="Search by name (e.g. Saswad, Jejuri, Walha)...",
                    key="ds_search_station",
                    help="Filter the displayed stations by name."
                )
            with f2:
                tier_options = ["All Tiers", "Deep (> 8.0 m)", "Moderate (4.0–8.0 m)", "Shallow (< 4.0 m)"]
                if unknown_count > 0:
                    tier_options.append("Unknown / Unclassified")
                tier_filter = st.selectbox(
                    "Filter by Depth Tier",
                    tier_options,
                    index=0,
                    key="ds_tier_filter",
                    help="Filter stations by their project-defined physical reference depth tier."
                )
            with f3:
                sort_option = st.selectbox(
                    "Sort Stations",
                    ["Deepest Observation First", "Shallowest Observation First", "Alphabetical (A–Z)"],
                    index=0,
                    key="ds_sort_option",
                    help="Order stations to prioritize deep water tables or organize alphabetically."
                )

        # Filter logic
        filtered_df = latest_st.copy()
        filtered_df['category'] = filtered_df['gw_level_mbgl'].apply(get_depth_tier_category)

        if "Deep" in tier_filter:
            filtered_df = filtered_df[filtered_df['category'] == "Deep"]
        elif "Moderate" in tier_filter:
            filtered_df = filtered_df[filtered_df['category'] == "Moderate"]
        elif "Shallow" in tier_filter:
            filtered_df = filtered_df[filtered_df['category'] == "Shallow"]
        elif "Unknown" in tier_filter:
            filtered_df = filtered_df[filtered_df['category'] == "Unknown"]

        if station_search.strip():
            query = station_search.strip()
            filtered_df = filtered_df[filtered_df['station'].str.contains(query, case=False, na=False)]

        # Sorting logic
        if "Deepest" in sort_option:
            filtered_df = filtered_df.sort_values(by="gw_level_mbgl", ascending=False, na_position="last")
        elif "Shallowest" in sort_option:
            filtered_df = filtered_df.sort_values(by="gw_level_mbgl", ascending=True, na_position="last")
        elif "Alphabetical" in sort_option:
            filtered_df = filtered_df.sort_values(by="station", ascending=True)

        st.markdown(
            f"<div class='results-count-bar'>Showing <b>{len(filtered_df)}</b> of <b>{total_wells}</b> monitoring stations</div>",
            unsafe_allow_html=True
        )

        # Station Details & Deterministic Recommendations
        if filtered_df.empty:
            st.info(f"No monitoring stations match your search query '{station_search}' in the selected tier ({tier_filter}).")
        else:
            is_single = len(filtered_df) == 1
            for _, st_row in filtered_df.iterrows():
                st_name = st_row['station']
                depth = st_row['gw_level_mbgl']
                plan = get_intervention_plan(depth)

                icon = plan['icon']
                tier_label = plan['tier_label']
                priority = plan['priority']
                category = plan['category']
                badge_class = plan['badge']

                obs_dt = st_row['date'] if pd.notna(st_row.get('date')) else None
                obs_year = obs_dt.year if obs_dt else None
                obs_date = obs_dt.strftime('%d %b %Y') if obs_dt else 'N/A'
                season_tag = st_row.get('season_tag', 'N/A')
                rain_90 = f"{st_row['rain_90d']:.1f} mm" if pd.notna(st_row.get('rain_90d')) else "N/A"
                rain_365 = f"{st_row['rain_365d']:.1f} mm" if pd.notna(st_row.get('rain_365d')) else "N/A"
                is_extrapolated = bool(st_row.get('is_rainfall_extrapolated', 0))

                is_older = (obs_year is not None and obs_year < 2023)
                recency_badge_html = f'<span class="station-historical-badge" style="background-color: rgba(245, 158, 11, 0.15); border: 1px solid var(--badge-moderate-border); color: var(--badge-moderate-text); padding: 2px 8px; border-radius: 4px; font-size: 0.72rem; font-weight: 600;">🗓️ Historical Survey: {obs_year}</span>' if is_older else ""

                if pd.notna(depth) and isinstance(depth, (int, float)):
                    depth_val_str = f"{depth:.2f}"
                    depth_unit_str = "m MBGL"
                else:
                    depth_val_str = "Unrecorded"
                    depth_unit_str = ""

                extrap_badge_html = f'<span class="station-extrap-badge">⚠️ Spatially Extrapolated Rain</span>' if is_extrapolated else ""
                extrap_warning_html = f'<div class="station-extrap-warning">⚠️ <i>Station lies outside the 4-point IMD precipitation grid; rainfall lookbacks are spatially extrapolated from the nearest grid coordinates.</i></div>' if is_extrapolated else ""

                card_html = (
                    f'<div class="decision-station-card tier-{category.lower()}">'
                    f'<div class="station-card-top">'
                    f'<div class="station-identity">'
                    f'<span class="station-name">{st_name}</span>'
                    f'<span class="{badge_class}">● {tier_label}</span>'
                    f'{recency_badge_html}'
                    f'{extrap_badge_html}'
                    f'</div>'
                    f'<div class="station-depth-hero hero-{category.lower()}">'
                    f'<span class="station-depth-val">{depth_val_str}</span>'
                    f'<span class="station-depth-unit">{depth_unit_str}</span>'
                    f'</div>'
                    f'</div>'
                    f'<div class="station-telemetry-grid">'
                    f'<div class="telemetry-item"><span class="telemetry-lbl">Latest Recorded Survey</span><span class="telemetry-val">{obs_date}</span></div>'
                    f'<div class="telemetry-item"><span class="telemetry-lbl">Season</span><span class="telemetry-val">{season_tag}</span></div>'
                    f'<div class="telemetry-item"><span class="telemetry-lbl">Past 90-Day Rain</span><span class="telemetry-val">{rain_90}</span></div>'
                    f'<div class="telemetry-item"><span class="telemetry-lbl">Past 365-Day Rain</span><span class="telemetry-val">{rain_365}</span></div>'
                    f'</div>'
                    f'{extrap_warning_html}'
                    f'</div>'
                )
                st.markdown(card_html, unsafe_allow_html=True)

                # Conservation Recommendations Expander
                with st.expander(f"📋 View Project-Defined Heuristic Plan — {st_name} ({priority})", expanded=is_single):
                    banner_html = (
                        f'<div class="decision-priority-banner priority-{category.lower()}">'
                        f'<span class="priority-banner-icon">{icon}</span>'
                        f'<div class="priority-banner-text">'
                        f'<div class="priority-banner-title">{priority}</div>'
                        f'<div class="priority-banner-sub">Assessment based on latest available historical observation ({obs_date}), not current groundwater conditions.</div>'
                        f'</div>'
                        f'</div>'
                    )
                    st.markdown(banner_html, unsafe_allow_html=True)

                    actions_rows = "".join([
                        f'<div class="decision-action-item">'
                        f'<div class="action-num-badge">{idx + 1}</div>'
                        f'<div class="action-body">'
                        f'<div class="action-title">{title}</div>'
                        f'<div class="action-desc">{desc}</div>'
                        f'</div>'
                        f'</div>'
                        for idx, (title, desc) in enumerate(plan['actions'])
                    ])
                    actions_html = f'<div class="decision-actions-list">{actions_rows}</div>'
                    st.markdown(actions_html, unsafe_allow_html=True)
                    st.caption(
                        f"ℹ️ *Project-Defined Heuristic Note for {st_name}: Assessment is based on latest historical sounding ({obs_date}) "
                        f"and project-defined physical depth tiers (< 4.0 m, 4.0–8.0 m, > 8.0 m MBGL). It does not represent current real-time "
                        f"groundwater conditions, nor does it represent official CGWB/GSDA guidance or statutory government directives.*"
                    )

    with tab_limits:
        # Educational Advisory Notice Component
        render_decision_support_advisory_notice()

        st.subheader("Core Scientific Assumptions & Methodological Boundaries")
        st.markdown("""
        <div class="ds-limitations-grid">
            <div class="ds-limitation-card">
                <div class="ds-limitation-header">
                    <span>🗓️</span>
                    <span>Historical Soundings vs. Live Measurements</span>
                </div>
                <div class="ds-limitation-body">
                    All station assessments are derived from historical in-situ tape soundings recorded between 1997 and 2023, not real-time automated telemetry. Groundwater depths represent conditions at the specific historical survey date.
                </div>
            </div>
            <div class="ds-limitation-card">
                <div class="ds-limitation-header">
                    <span>⏱️</span>
                    <span>Differing Station Observation Dates</span>
                </div>
                <div class="ds-limitation-body">
                    Monitoring campaigns occurred across different years and months (e.g. 7 stations observed in 2023, 4 stations in earlier years). These soundings cannot be averaged or interpreted as a single simultaneous regional water table.
                </div>
            </div>
            <div class="ds-limitation-card">
                <div class="ds-limitation-header">
                    <span>🚜</span>
                    <span>Unmetered Agricultural Groundwater Pumping</span>
                </div>
                <div class="ds-limitation-body">
                    Agricultural extraction across Purandar Taluka is largely unmetered in available records. Water table depth reflects the combined effect of extraction and recharge, but depth alone cannot prove depletion rates or volumetric stress.
                </div>
            </div>
            <div class="ds-limitation-card">
                <div class="ds-limitation-header">
                    <span>🪨</span>
                    <span>Hard-Rock Geological Heterogeneity</span>
                </div>
                <div class="ds-limitation-body">
                    Groundwater in Deccan basalt flows is localized and compartmentalized. All artificial recharge structures (check dams, percolation tanks) strictly require site-specific geological, geophysical, and infiltration surveys before implementation.
                </div>
            </div>
            <div class="ds-limitation-card">
                <div class="ds-limitation-header">
                    <span>📋</span>
                    <span>Preliminary Planning Heuristics</span>
                </div>
                <div class="ds-limitation-body">
                    Action recommendations are rule-based heuristics synthesized for preliminary planning support. They do not constitute certified civil engineering blueprints or guaranteed water conservation outcomes.
                </div>
            </div>
            <div class="ds-limitation-card">
                <div class="ds-limitation-header">
                    <span>🌧️</span>
                    <span>Rainfall Grid Spatial Extrapolation</span>
                </div>
                <div class="ds-limitation-body">
                    Four peripheral stations lie outside the 4-point 0.25° IMD precipitation grid; antecedent rainfall metrics at these stations are spatially interpolated and do not represent direct rain-gauge observations at the wellhead.
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
