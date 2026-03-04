import streamlit as st
from dotenv import load_dotenv
from db.database import init_db
from i18n import t, inject_rtl_css

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

st.title(t("app_title"))
st.markdown(t("app_description"))
st.info(t("app_get_started"))
