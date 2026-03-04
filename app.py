import streamlit as st
from dotenv import load_dotenv
from db.database import init_db
from i18n import t, inject_rtl_css
from styles import inject_custom_css

load_dotenv()
init_db()

# --- Language selector (must come before page_config uses it) ---
if "lang" not in st.session_state:
    st.session_state["lang"] = "en"

st.set_page_config(
    page_title="CRM Lead Scraper",
    page_icon="📇",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Sidebar language toggle
lang_options = {"English": "en", "العربية": "ar"}
lang_labels = list(lang_options.keys())
current_label = next(k for k, v in lang_options.items() if v == st.session_state["lang"])
selected_label = st.sidebar.selectbox(
    t("language_label"),
    lang_labels,
    index=lang_labels.index(current_label),
)
st.session_state["lang"] = lang_options[selected_label]

inject_rtl_css()
inject_custom_css()

# --- Hero Section ---
st.markdown("""
<div class="hero-container">
    <div class="hero-icon">📇</div>
    <h1>{title}</h1>
    <p class="hero-tagline">{tagline}</p>
</div>
""".format(title=t("app_title"), tagline=t("hero_tagline")), unsafe_allow_html=True)

st.markdown("")

# --- Feature Cards ---
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div class="feature-card">
        <div class="fc-icon">🔍</div>
        <div class="fc-title">{title}</div>
        <div class="fc-desc">{desc}</div>
    </div>
    """.format(title=t("feature_scrape_title"), desc=t("feature_scrape_desc")), unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="feature-card">
        <div class="fc-icon">📋</div>
        <div class="fc-title">{title}</div>
        <div class="fc-desc">{desc}</div>
    </div>
    """.format(title=t("feature_manage_title"), desc=t("feature_manage_desc")), unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="feature-card">
        <div class="fc-icon">📤</div>
        <div class="fc-title">{title}</div>
        <div class="fc-desc">{desc}</div>
    </div>
    """.format(title=t("feature_export_title"), desc=t("feature_export_desc")), unsafe_allow_html=True)

st.markdown("")

# --- Quick-start CTA ---
cta1, cta2, _ = st.columns([1, 1, 2])
with cta1:
    if st.button(t("go_to_scraper"), type="primary", use_container_width=True):
        st.switch_page("pages/2_Scraper.py")
with cta2:
    if st.button(t("go_to_dashboard"), use_container_width=True):
        st.switch_page("pages/1_Dashboard.py")
