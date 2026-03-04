import os
import streamlit as st
from dotenv import load_dotenv
from db.database import init_db
from db.queries import (
    get_categories, add_category, update_category, delete_category,
    get_setting, set_setting, purge_duplicates,
)
from i18n import t, inject_rtl_css

load_dotenv()
init_db()
inject_rtl_css()

st.header(t("settings"))

# --- API Key Status ---
st.subheader(t("api_keys"))
api_key = os.getenv("GOOGLE_PLACES_API_KEY", "")
if api_key and api_key != "your_api_key_here":
    st.success(t("api_key_configured", key=api_key[:8]))
else:
    st.warning(t("api_key_not_set"))
    st.code("GOOGLE_PLACES_API_KEY=your_key_here", language="text")

st.divider()

# --- Category Management ---
st.subheader(t("categories"))

categories = get_categories()
for cat in categories:
    with st.expander(f"{t('custom_prefix') if cat.is_custom else ''}{cat.name}"):
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

st.divider()
st.subheader(t("add_custom_category"))
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

st.divider()

# --- Maintenance ---
st.subheader(t("maintenance"))
if st.button(t("purge_duplicates")):
    removed = purge_duplicates()
    st.success(t("removed_duplicates", count=removed))
