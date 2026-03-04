import io
import streamlit as st
import pandas as pd
from db.database import init_db
from db.queries import get_leads, get_categories
from i18n import (
    t, inject_rtl_css, translated_statuses,
    status_display_to_db, translate_columns,
)
from styles import inject_custom_css, section_header, metric_card

init_db()
inject_rtl_css()
inject_custom_css()

st.markdown(section_header(t("export_leads"), "📤"), unsafe_allow_html=True)

display_statuses = translated_statuses()

# --- Filters ---
col1, col2, col3 = st.columns(3)
with col1:
    cats = get_categories()
    cat_filter = st.selectbox(t("category"), [t("all")] + [c.name for c in cats])
with col2:
    status_filter = st.selectbox(t("status"), [t("all")] + display_statuses)
with col3:
    source_filter = st.selectbox(t("source"), [t("all"), "Google Places", "Yellow Pages", "Custom URL"])

db_cat = cat_filter if cat_filter != t("all") else None
db_status = status_display_to_db(status_filter) if status_filter != t("all") else None
db_source = source_filter if source_filter != t("all") else None

all_leads = get_leads(limit=10000)
leads = get_leads(category=db_cat, status=db_status, source=db_source, limit=10000)

# --- Export summary metrics ---
st.markdown(section_header(t("export_summary"), "📊"), unsafe_allow_html=True)
mc1, mc2 = st.columns(2)
with mc1:
    st.markdown(metric_card("📦", t("total_available"), len(all_leads), "#3b82f6"), unsafe_allow_html=True)
with mc2:
    st.markdown(metric_card("🔍", t("filtered_count"), len(leads), "#8b5cf6"), unsafe_allow_html=True)

st.markdown("")

if not leads:
    st.info(t("no_leads_match_export"))
    st.stop()

df = pd.DataFrame(leads)
export_cols = ["id", "business_name", "name", "phone", "email", "address",
               "website", "category", "source", "location", "status", "notes", "created_at"]
export_cols = [c for c in export_cols if c in df.columns]
df_export = df[export_cols]

df_display = translate_columns(df_export.head(20), export_cols)
st.dataframe(df_display, use_container_width=True, hide_index=True)
if len(leads) > 20:
    st.caption(t("showing_first", count=len(leads)))

# --- Styled download cards ---
st.markdown("")
col_csv, col_xlsx = st.columns(2)

with col_csv:
    st.markdown("""
    <div class="download-card">
        <div class="dl-icon">📄</div>
        <div class="dl-title">CSV</div>
        <div class="dl-desc">{desc}</div>
    </div>
    """.format(desc=t("csv_desc")), unsafe_allow_html=True)
    csv_data = df_export.to_csv(index=False).encode("utf-8")
    st.download_button(
        label=t("download_csv"),
        data=csv_data,
        file_name="crm_leads.csv",
        mime="text/csv",
        use_container_width=True,
    )

with col_xlsx:
    st.markdown("""
    <div class="download-card">
        <div class="dl-icon">📊</div>
        <div class="dl-title">Excel</div>
        <div class="dl-desc">{desc}</div>
    </div>
    """.format(desc=t("excel_desc")), unsafe_allow_html=True)
    buffer = io.BytesIO()
    df_export.to_excel(buffer, index=False, engine="openpyxl")
    st.download_button(
        label=t("download_excel"),
        data=buffer.getvalue(),
        file_name="crm_leads.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True,
    )
