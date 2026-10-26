"""Sidebar navigation and telemetry context component."""
import streamlit as st
from styles.theme import get_current_theme


def render_sidebar() -> str:
    """Render the application sidebar with branding, theme switcher, and navigation.
    
    Returns:
        The label of the currently selected screen.
    """
    with st.sidebar:
        st.markdown("""
        <div class="sidebar-brand">
            <div class="sidebar-brand-name">💧 BhujalDrishti</div>
            <div class="sidebar-brand-tagline">Environmental Intelligence System</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Working Light / Dark Theme Switcher
        current_theme = get_current_theme()
        theme_index = 0 if current_theme == "light" else 1
        selected_theme_label = st.radio(
            "Interface Theme",
            ["☀️ Light Theme", "🌙 Dark Theme (Aqua)"],
            index=theme_index,
            horizontal=True,
            key="theme_selector_radio"
        )
        new_theme = "light" if "Light" in selected_theme_label else "dark"
        if new_theme != current_theme:
            st.session_state["app_theme"] = new_theme
            st.rerun()
            
        st.markdown("---")
        
        # Screen Navigation
        screen = st.radio(
            "Navigation",
            [
                "📊 Screen 1: Overview Dashboard",
                "🗺️ Screen 2: Groundwater Map",
                "🔮 Screen 3: Next-Observation Forecast",
                "🛡️ Screen 4: Decision Support"
            ],
            index=0,
            label_visibility="collapsed"
        )
        
        st.markdown("---")
        st.markdown("##### **Telemetry Network Context**")
        st.markdown("""
        <div class="telemetry-box">
            • <b>Jurisdiction:</b> Purandar Taluka (Pune, MH)<br>
            • <b>Administrative Area:</b> ~1,105 km²<br>
            • <b>Aquifer Formation:</b> Deccan Basalt Flows<br>
            • <b>CGWB Monitoring:</b> 11 In-situ Observation Wells<br>
            • <b>Rainfall Grid:</b> 4 IMD Points (0.25° resolution)<br>
            • <b>Extrapolated Wells:</b> 4 Southern/Western Stations<br>
            • <b>Validation Split:</b> Zero-Target-Leakage Chronological Split (Train: 1996–2017, Test: 2018–2023)
        </div>
        """, unsafe_allow_html=True)
        
        st.caption("ℹ️ *Academic research decision-support prototype. Predictions are statistical estimates, not physical measurements.*")
        
    return screen
