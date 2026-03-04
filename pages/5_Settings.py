import os
import streamlit as st
from dotenv import load_dotenv
from db.database import init_db
from db.queries import (
    get_categories, add_category, update_category, delete_category,
    get_setting, set_setting, purge_duplicates,
)
from i18n import t, inject_rtl_css
from styles import inject_custom_css, section_header

load_dotenv()
init_db()
inject_rtl_css()
inject_custom_css()

st.markdown(section_header(t("settings"), "⚙️"), unsafe_allow_html=True)

# --- API Key Status ---
st.markdown(section_header(t("api_keys"), "🔑"), unsafe_allow_html=True)
api_key = os.getenv("GOOGLE_PLACES_API_KEY", "")
if api_key and api_key != "your_api_key_here":
    st.markdown(f"""
    <div class="settings-status-card" style="--indicator:#22c55e;">
        <span class="ssc-icon">✅</span>
        <span class="ssc-text"><strong>Google Places API</strong> — {t("configured")} ({api_key[:8]}...)</span>
    </div>
    """, unsafe_allow_html=True)
else:
    st.markdown(f"""
    <div class="settings-status-card" style="--indicator:#ef4444;">
        <span class="ssc-icon">❌</span>
        <span class="ssc-text"><strong>Google Places API</strong> — {t("not_configured")}</span>
    </div>
    """, unsafe_allow_html=True)
    st.code("GOOGLE_PLACES_API_KEY=your_key_here", language="text")

st.markdown("")

# --- Category Management ---
st.markdown(section_header(t("categories"), "📁"), unsafe_allow_html=True)

categories = get_categories()
for cat in categories:
    with st.expander(f"{t('custom_prefix') if cat.is_custom else ''}{cat.name}"):
        # Show keywords as tags
        if cat.keywords:
            tags_html = " ".join(f'<span class="kw-tag">{kw}</span>' for kw in cat.keywords)
            st.markdown(tags_html, unsafe_allow_html=True)
            st.markdown("")

        new_name = st.text_input(t("name"), value=cat.name, key=f"cat_name_{cat.id}")
        new_kw = st.text_area(
            t("keywords_per_line"),
            value="\n".join(cat.keywords),
            key=f"cat_kw_{cat.id}",
        )
        col1, col2 = st.columns(2)
        with col1:
            if st.button(t("save"), key=f"cat_save_{cat.id}"):
                kw_list = [k.strip() for k in new_kw.split("\n") if k.strip()]
                update_category(cat.id, new_name, kw_list)
                st.success(t("updated"))
                st.rerun()
        with col2:
            if cat.is_custom:
                if st.button(t("delete"), key=f"cat_del_{cat.id}", type="secondary"):
                    delete_category(cat.id)
                    st.success(t("deleted"))
                    st.rerun()

st.markdown("")
st.markdown(section_header(t("add_custom_category"), "➕"), unsafe_allow_html=True)
with st.form("add_category"):
    new_cat_name = st.text_input(t("category_name"))
    new_cat_keywords = st.text_area(t("keywords_per_line"))
    if st.form_submit_button(t("add_category")):
        if new_cat_name:
            kw_list = [k.strip() for k in new_cat_keywords.split("\n") if k.strip()]
            try:
                add_category(new_cat_name, kw_list)
                st.success(t("added_category", name=new_cat_name))
                st.rerun()
            except Exception as e:
                st.error(t("failed_error", error=e))
        else:
            st.error(t("enter_category_name"))

st.markdown("")

# --- Maintenance ---
st.markdown(section_header(t("maintenance"), "🔧"), unsafe_allow_html=True)
if st.button(t("purge_duplicates")):
    removed = purge_duplicates()
    st.success(t("removed_duplicates", count=removed))
