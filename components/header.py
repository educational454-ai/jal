"""Global research header banner component."""
import streamlit as st


def render_research_header(theme: str = "light") -> None:
    """Render the top research observatory banner with platform branding and jurisdiction context."""
    st.markdown("""
    <div class="research-header">
        <div class="header-left">
            <div class="header-icon-box">
                <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M12 2.69l5.66 5.66a8 8 0 1 1-11.31 0z"></path>
                </svg>
            </div>
            <div class="header-titles">
                <div class="header-main-title">BhujalDrishti &nbsp;<span style="font-weight: 400; font-size: 1.05rem; color: var(--text-secondary);">| JalRakshak AI</span></div>
                <div class="header-subtitle">Multimodal GIS & Hydrological Next-Observation Forecasting Decision Support</div>
            </div>
        </div>
        <div class="header-badges">
            <span class="badge-prototype">Research Prototype</span>
            <span class="badge-jurisdiction">Purandar Taluka (~1,105 km²)</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
