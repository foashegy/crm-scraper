"""Shared CSS & styling utilities for the CRM Scraper app."""

import streamlit as st

# ---------------------------------------------------------------------------
# Status colors
# ---------------------------------------------------------------------------

STATUS_COLORS = {
    "New": "#22c55e",
    "Contacted": "#3b82f6",
    "Interested": "#f59e0b",
    "Not Interested": "#ef4444",
    "Converted": "#8b5cf6",
}

# Arabic status mapping for color lookup
_STATUS_AR_TO_EN = {
    "جديد": "New",
    "تم التواصل": "Contacted",
    "مهتم": "Interested",
    "غير مهتم": "Not Interested",
    "تم التحويل": "Converted",
}

PLOTLY_COLORS = ["#3b82f6", "#8b5cf6", "#f59e0b", "#ef4444", "#22c55e",
                 "#06b6d4", "#ec4899", "#14b8a6", "#f97316", "#6366f1"]


def _get_status_color(status: str) -> str:
    """Get color for a status value (works with both EN and AR)."""
    en_status = _STATUS_AR_TO_EN.get(status, status)
    return STATUS_COLORS.get(en_status, "#6b7280")


# ---------------------------------------------------------------------------
# inject_custom_css — call once per page
# ---------------------------------------------------------------------------

def inject_custom_css():
    st.markdown("""
<style>
/* Metric / KPI cards */
.metric-card {
    background: #ffffff;
    border-radius: 12px;
    padding: 1.2rem 1.4rem;
    border-left: 5px solid var(--accent, #3b82f6);
    box-shadow: 0 2px 8px rgba(0,0,0,0.06);
    margin-bottom: 0.8rem;
    transition: transform 0.15s, box-shadow 0.15s;
}
.metric-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 16px rgba(0,0,0,0.10);
}
.metric-card .metric-icon {
    font-size: 1.6rem;
    margin-bottom: 0.2rem;
}
.metric-card .metric-value {
    font-size: 2rem;
    font-weight: 700;
    color: #1e293b;
    line-height: 1.1;
}
.metric-card .metric-label {
    font-size: 0.85rem;
    color: #64748b;
    margin-top: 0.15rem;
}

/* Status badge pills */
.status-badge {
    display: inline-block;
    padding: 0.2rem 0.75rem;
    border-radius: 999px;
    font-size: 0.78rem;
    font-weight: 600;
    color: #fff;
    line-height: 1.5;
}

/* Card containers */
.styled-card {
    background: #ffffff;
    border-radius: 12px;
    padding: 1.5rem;
    box-shadow: 0 2px 8px rgba(0,0,0,0.06);
    margin-bottom: 1rem;
    border: 1px solid #f1f5f9;
}

/* Section headers with accent underline */
.section-header {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    font-size: 1.25rem;
    font-weight: 700;
    color: #1e293b;
    margin-bottom: 0.3rem;
    padding-bottom: 0.4rem;
    border-bottom: 3px solid #3b82f6;
}
.section-header .sh-icon {
    font-size: 1.3rem;
}

/* Hero section */
.hero-container {
    text-align: center;
    padding: 2.5rem 1rem 1.5rem;
}
.hero-container .hero-icon {
    font-size: 4rem;
    margin-bottom: 0.5rem;
}
.hero-container h1 {
    font-size: 2.4rem;
    font-weight: 800;
    color: #1e293b;
    margin: 0;
}
.hero-container .hero-tagline {
    font-size: 1.1rem;
    color: #64748b;
    margin-top: 0.3rem;
}

/* Feature cards */
.feature-card {
    background: #ffffff;
    border-radius: 14px;
    padding: 1.8rem 1.4rem;
    text-align: center;
    box-shadow: 0 2px 12px rgba(0,0,0,0.06);
    border: 1px solid #f1f5f9;
    transition: transform 0.15s, box-shadow 0.15s;
    height: 100%;
}
.feature-card:hover {
    transform: translateY(-3px);
    box-shadow: 0 8px 24px rgba(0,0,0,0.10);
}
.feature-card .fc-icon {
    font-size: 2.5rem;
    margin-bottom: 0.6rem;
}
.feature-card .fc-title {
    font-size: 1.15rem;
    font-weight: 700;
    color: #1e293b;
    margin-bottom: 0.3rem;
}
.feature-card .fc-desc {
    font-size: 0.88rem;
    color: #64748b;
    line-height: 1.5;
}

/* Download cards */
.download-card {
    background: #ffffff;
    border-radius: 12px;
    padding: 1.5rem;
    text-align: center;
    box-shadow: 0 2px 8px rgba(0,0,0,0.06);
    border: 1px solid #f1f5f9;
    margin-bottom: 0.5rem;
}
.download-card .dl-icon {
    font-size: 2rem;
    margin-bottom: 0.3rem;
}
.download-card .dl-title {
    font-size: 1rem;
    font-weight: 600;
    color: #1e293b;
}
.download-card .dl-desc {
    font-size: 0.8rem;
    color: #64748b;
}

/* Settings cards */
.settings-status-card {
    background: #ffffff;
    border-radius: 12px;
    padding: 1.2rem 1.4rem;
    box-shadow: 0 2px 8px rgba(0,0,0,0.06);
    border-left: 5px solid var(--indicator, #22c55e);
    display: flex;
    align-items: center;
    gap: 0.8rem;
    margin-bottom: 1rem;
}
.settings-status-card .ssc-icon {
    font-size: 1.8rem;
}
.settings-status-card .ssc-text {
    font-size: 0.95rem;
    color: #1e293b;
}

/* Keyword tags */
.kw-tag {
    display: inline-block;
    background: #eff6ff;
    color: #3b82f6;
    padding: 0.15rem 0.6rem;
    border-radius: 999px;
    font-size: 0.78rem;
    font-weight: 500;
    margin: 0.15rem 0.2rem;
}

/* Source description cards */
.source-info {
    display: flex;
    align-items: center;
    gap: 0.6rem;
    background: #f8fafc;
    border-radius: 10px;
    padding: 0.8rem 1rem;
    margin-bottom: 0.8rem;
    border: 1px solid #e2e8f0;
}
.source-info .si-icon { font-size: 1.5rem; }
.source-info .si-text { font-size: 0.88rem; color: #475569; }

/* Mini stacked bar */
.mini-bar-container {
    display: flex;
    height: 10px;
    border-radius: 999px;
    overflow: hidden;
    margin: 0.5rem 0 1rem;
}
.mini-bar-segment {
    height: 100%;
    transition: width 0.3s;
}

/* Button hover */
.stButton > button {
    border-radius: 8px !important;
    transition: transform 0.1s !important;
}
.stButton > button:hover {
    transform: translateY(-1px) !important;
}

/* Sidebar styling */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #f8fafc 0%, #ffffff 100%);
}

/* Dark mode support */
@media (prefers-color-scheme: dark) {
    .metric-card, .styled-card, .feature-card, .download-card, .settings-status-card {
        background: #1e293b;
        border-color: #334155;
    }
    .metric-card .metric-value, .feature-card .fc-title,
    .download-card .dl-title, .section-header,
    .settings-status-card .ssc-text {
        color: #f1f5f9;
    }
    .metric-card .metric-label, .feature-card .fc-desc,
    .download-card .dl-desc, .hero-container .hero-tagline,
    .source-info .si-text {
        color: #94a3b8;
    }
    .hero-container h1 { color: #f1f5f9; }
    .source-info { background: #1e293b; border-color: #334155; }
    .kw-tag { background: #1e3a5f; color: #93c5fd; }
}
</style>
""", unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Component helpers
# ---------------------------------------------------------------------------

def status_badge(status: str) -> str:
    """Return HTML for a colored pill badge."""
    color = _get_status_color(status)
    return f'<span class="status-badge" style="background:{color};">{status}</span>'


def metric_card(icon: str, label: str, value, color: str = "#3b82f6") -> str:
    """Return styled HTML for a metric card."""
    return f"""
<div class="metric-card" style="--accent:{color};">
    <div class="metric-icon">{icon}</div>
    <div class="metric-value">{value}</div>
    <div class="metric-label">{label}</div>
</div>
"""


def section_header(title: str, icon: str = "") -> str:
    """Return styled HTML section header with icon."""
    return f"""
<div class="section-header">
    <span class="sh-icon">{icon}</span> {title}
</div>
"""


def mini_status_bar(status_counts: dict, total: int) -> str:
    """Return HTML for a mini horizontal stacked bar showing status distribution."""
    if total == 0:
        return ""
    segments = ""
    for status, count in status_counts.items():
        if count > 0:
            pct = (count / total) * 100
            color = _get_status_color(status)
            segments += f'<div class="mini-bar-segment" style="width:{pct:.1f}%;background:{color};" title="{status}: {count}"></div>'
    return f'<div class="mini-bar-container">{segments}</div>'
