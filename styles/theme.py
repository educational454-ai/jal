"""Theme configuration and styling injection for BhujalDrishti."""
import os
import streamlit as st

THEME_PALETTES = {
    "dark": {
        "bg_primary": "#07141B",
        "bg_secondary": "#0B2029",
        "bg_surface": "#102A35",
        "bg_surface_hover": "#163745",
        "border": "#23414B",
        "text_primary": "#EAF6F7",
        "text_secondary": "#A5BEC5",
        "text_muted": "#7E9FA7",
        "teal_accent": "#35D0C1",
        "blue_accent": "#58B9E8",
        "callout_bg": "#0B2029",
        "callout_border": "#23414B",
        "callout_text": "#EAF6F7",
        "callout_text_secondary": "#A5BEC5",
        "sidebar_bg": "#0B2029",
        "sidebar_border": "#23414B",
        "chart_bg": "#102A35",
        "chart_grid": "#23414B",
    },
    "light": {
        "bg_primary": "#F4F8F8",
        "bg_secondary": "#EBF2F3",
        "bg_surface": "#FFFFFF",
        "bg_surface_hover": "#F8FAFA",
        "border": "#D9E5E7",
        "text_primary": "#17313B",
        "text_secondary": "#617780",
        "text_muted": "#82969E",
        "teal_accent": "#087F80",
        "blue_accent": "#247DA8",
        "callout_bg": "#F8FAFC",
        "callout_border": "#CBD5E1",
        "callout_text": "#1E293B",
        "callout_text_secondary": "#475569",
        "sidebar_bg": "#F8FAFC",
        "sidebar_border": "#E2E8F0",
        "chart_bg": "#FAFAFA",
        "chart_grid": "#E2E8F0",
    }
}


def init_theme(default_theme: str = "light") -> str:
    """Initialize theme in session state if not already present."""
    if "app_theme" not in st.session_state:
        st.session_state["app_theme"] = default_theme
    return st.session_state["app_theme"]


def get_current_theme() -> str:
    """Retrieve the currently active theme identifier ('dark' or 'light')."""
    return st.session_state.get("app_theme", "light")


def toggle_theme() -> str:
    """Toggle between light and dark themes and return new theme."""
    current = get_current_theme()
    new_theme = "dark" if current == "light" else "light"
    st.session_state["app_theme"] = new_theme
    return new_theme


def get_theme_palette(theme: str = None) -> dict:
    """Retrieve color palette dictionary for chart rendering."""
    if theme is None:
        theme = get_current_theme()
    return THEME_PALETTES.get(theme, THEME_PALETTES["light"])


def apply_theme(theme: str = None) -> None:
    """Inject centralized CSS and apply theme-specific tokens."""
    if theme is None:
        theme = get_current_theme()
    
    css_path = os.path.join(os.path.dirname(__file__), "styles.css")
    css_content = ""
    if os.path.exists(css_path):
        with open(css_path, "r", encoding="utf-8") as f:
            css_content = f.read()
            
    palette = get_theme_palette(theme)
    
    # Generate dynamic override styles for the active theme
    theme_css = f"""
    <style>
        {css_content}
        
        :root {{
            --bg-primary: {palette['bg_primary']};
            --bg-secondary: {palette['bg_secondary']};
            --bg-surface: {palette['bg_surface']};
            --border-color: {palette['border']};
            --text-primary: {palette['text_primary']};
            --text-secondary: {palette['text_secondary']};
            --text-muted: {palette['text_muted']};
            --teal-accent: {palette['teal_accent']};
            --blue-accent: {palette['blue_accent']};
            --callout-bg: {palette['callout_bg']};
            --callout-border: {palette['callout_border']};
            --callout-text: {palette['callout_text']};
            --callout-text-secondary: {palette['callout_text_secondary']};
            --sidebar-bg: {palette['sidebar_bg']};
            --sidebar-border: {palette['sidebar_border']};
        }}
        
        /* Direct container backgrounds based on active theme */
        .stApp {{
            background-color: {palette['bg_primary']} !important;
            color: {palette['text_primary']} !important;
        }}

        /* Sidebar Complete Theme Integration */
        section[data-testid="stSidebar"],
        section[data-testid="stSidebar"] > div,
        div[data-testid="stSidebarContent"],
        div[data-testid="stSidebarUserContent"] {{
            background-color: {palette['sidebar_bg']} !important;
            border-right: 1px solid {palette['sidebar_border']} !important;
        }}
        section[data-testid="stSidebar"] p,
        section[data-testid="stSidebar"] span,
        section[data-testid="stSidebar"] label,
        section[data-testid="stSidebar"] div[data-testid="stMarkdownContainer"] p,
        section[data-testid="stSidebar"] div[data-testid="stMarkdownContainer"] span {{
            color: {palette['text_primary']} !important;
        }}
        section[data-testid="stSidebar"] hr {{
            border-color: {palette['sidebar_border']} !important;
        }}
        section[data-testid="stSidebar"] .sidebar-brand-name {{
            color: {palette['text_primary']} !important;
        }}
        section[data-testid="stSidebar"] .sidebar-brand-tagline {{
            color: {palette['teal_accent']} !important;
        }}
        section[data-testid="stSidebar"] .telemetry-box {{
            background-color: {palette['bg_surface']} !important;
            border: 1px solid {palette['border']} !important;
            color: {palette['text_secondary']} !important;
        }}
        section[data-testid="stSidebar"] .telemetry-box b {{
            color: {palette['text_primary']} !important;
        }}

        /* Native Streamlit Metric Contrast & Overflow Fix */
        div[data-testid="stMetricLabel"] p,
        div[data-testid="stMetricLabel"] span,
        div[data-testid="stMetricLabel"] {{
            color: {palette['text_secondary']} !important;
        }}
        div[data-testid="stMetricValue"],
        div[data-testid="stMetricValue"] div,
        div[data-testid="stMetricValue"] span {{
            color: {palette['text_primary']} !important;
            white-space: nowrap !important;
            overflow: visible !important;
            font-size: 1.55rem !important;
        }}

        /* Dropdowns & Select Components */
        div[data-baseweb="select"] > div {{
            background-color: {palette['bg_surface']} !important;
            border-color: {palette['border']} !important;
            color: {palette['text_primary']} !important;
        }}

        /* Native Alert Theming */
        div[data-testid="stAlert"] {{
            background-color: {palette['callout_bg']} !important;
            border: 1px solid {palette['callout_border']} !important;
            color: {palette['callout_text']} !important;
        }}
        div[data-testid="stAlert"] p,
        div[data-testid="stAlert"] span {{
            color: {palette['callout_text']} !important;
        }}
    </style>
    """
    st.markdown(theme_css, unsafe_allow_html=True)
