"""Sidebar navigation and branding component."""
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
            <div class="sidebar-brand-tagline">JalRakshak AI • Groundwater Intelligence</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Simplified Light / Dark Theme Switcher
        current_theme = get_current_theme()
        theme_index = 0 if current_theme == "light" else 1
        selected_theme_label = st.radio(
            "Theme",
            ["☀️ Light", "🌙 Dark"],
            index=theme_index,
            horizontal=True,
            key="theme_selector_radio",
            label_visibility="collapsed"
        )
        new_theme = "light" if "Light" in selected_theme_label else "dark"
        if new_theme != current_theme:
            st.session_state["app_theme"] = new_theme
            st.rerun()
            
        st.markdown('<div class="sidebar-divider"></div>', unsafe_allow_html=True)
        
        # Screen Navigation
        screen = st.radio(
            "Navigation",
            [
                "📊 Overview Dashboard",
                "🗺️ Groundwater Map",
                "🔮 Next-Observation Forecast",
                "🛡️ Decision Support"
            ],
            index=0,
            label_visibility="collapsed"
        )
        
        st.markdown('<div class="sidebar-divider"></div>', unsafe_allow_html=True)
        
        # Compact, non-intrusive research prototype footer
        st.markdown("""
        <div class="sidebar-footer">
            <span class="sidebar-footer-badge">Research Prototype</span>
            <div class="sidebar-footer-sub">Purandar Taluka CGWB Telemetry</div>
        </div>
        """, unsafe_allow_html=True)
        
    return screen

