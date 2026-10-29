"""Conservation Decision Support screen implementation for BhujalDrishti."""
import pandas as pd
import streamlit as st

from services.data_loader import get_latest_per_station, get_intervention_plan
from components.callouts import render_decision_support_advisory_notice


def render_decision_support_screen(df: pd.DataFrame) -> None:
    """Render Screen 4: Conservation Decision Support."""
    st.markdown("""
    <div class="screen-header-block">
        <div class="main-header">🛡️ Conservation Decision Support System</div>
        <div class="sub-header">Actionable, evidence-backed watershed and farm-level groundwater conservation interventions</div>
    </div>
    """, unsafe_allow_html=True)
    
    render_decision_support_advisory_notice()
    
    latest_st = get_latest_per_station(df)
    
    st.markdown("### 📋 Station-wise Vulnerability & Prescribed Interventions")
    
    for _, st_row in latest_st.iterrows():
        st_name = st_row['station']
        depth = st_row['gw_level_mbgl']
        plan = get_intervention_plan(depth)
        
        icon = plan['icon']
        tier_label = plan['tier_label']
        priority = plan['priority']
        category = plan['category']
        
        depth_str = f"{depth:.2f} m MBGL" if (pd.notna(depth) and isinstance(depth, (int, float))) else "Unrecorded"
        
        with st.expander(f"{icon} **{st_name}** — Level: {depth_str} ({tier_label})"):
            c1, c2 = st.columns([1, 1.5])
            with c1:
                st.markdown(f"**Latest Reading Date:** {st_row['date'].strftime('%d %b %Y') if pd.notna(st_row.get('date')) else 'N/A'}")
                st.markdown(f"**Season:** {st_row['season_tag']}")
                st.markdown(f"**Past 90-Day Rain:** `{st_row['rain_90d']:.1f} mm`" if pd.notna(st_row.get('rain_90d')) else "**Past 90-Day Rain:** `N/A`")
                st.markdown(f"**Past 365-Day Rain:** `{st_row['rain_365d']:.1f} mm`" if pd.notna(st_row.get('rain_365d')) else "**Past 365-Day Rain:** `N/A`")
                if st_row.get('is_rainfall_extrapolated', 0):
                    st.caption("⚠️ *Station is outside the 4-point IMD rainfall grid; rainfall lookbacks are spatially extrapolated.*")
                
                st.markdown(
                    f"<div style='margin-top: 8px;'><span class='{plan['badge']}'>{tier_label}</span></div>",
                    unsafe_allow_html=True
                )
                
            with c2:
                st.markdown(f"**Recommended Conservation Actions:** *({priority})*")
                if category == "Deep":
                    st.error(f"🚨 **{priority}**")
                elif category == "Moderate":
                    st.warning(f"⚠️ **{priority}**")
                elif category == "Shallow":
                    st.success(f"✅ **{priority}**")
                else:
                    st.info(f"ℹ️ **{priority}**")
                    
                action_bullets = ""
                for title, desc in plan['actions']:
                    action_bullets += f"- **{title}**: {desc}\n"
                st.markdown(action_bullets)
                
    st.markdown("---")
    st.info("📌 **Disclaimer**: *BhujalDrishti provides rule-based decision-support advisories synthesized from CGWB/GSDA hydrogeological guidelines. Water table depth alone does not prove groundwater depletion, establish its localized causes (e.g. pumping vs recharge dynamics), or prove the necessity of a specific engineering intervention at a site. All structural interventions must be validated through localized geophysical surveys and hydrogeological field investigations prior to execution.*")
