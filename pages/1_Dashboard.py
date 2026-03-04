import streamlit as st
import pandas as pd
from db.database import init_db
from db.queries import (
    get_lead_stats, get_leads_by_category_stats,
    get_leads_by_source_stats, get_leads_by_status_stats,
    get_recent_scrape_jobs,
)
from i18n import t, inject_rtl_css, status_db_to_display, translate_columns

init_db()
inject_rtl_css()

st.header(t("dashboard"))

# --- Metric cards ---
stats = get_lead_stats()
total = stats.pop("total", 0)

cols = st.columns(5)
cols[0].metric(t("total_leads"), total)
for i, status in enumerate(["New", "Contacted", "Interested", "Not Interested"], start=1):
    cols[i].metric(status_db_to_display(status), stats.get(status, 0))

st.divider()

# --- Charts ---
col_left, col_right = st.columns(2)

with col_left:
    st.subheader(t("leads_by_category"))
    cat_data = get_leads_by_category_stats()
    if cat_data:
        df = pd.DataFrame(cat_data)
        st.bar_chart(df, x="category", y="count")
    else:
        st.caption(t("no_data_yet"))

with col_right:
    st.subheader(t("leads_by_source"))
    src_data = get_leads_by_source_stats()
    if src_data:
        df = pd.DataFrame(src_data)
        st.bar_chart(df, x="source", y="count")
    else:
        st.caption(t("no_data_yet"))

st.subheader(t("leads_by_status"))
status_data = get_leads_by_status_stats()
if status_data:
    df = pd.DataFrame(status_data)
    st.bar_chart(df, x="status", y="count")

# --- Recent scrape jobs ---
st.divider()
st.subheader(t("recent_scrape_jobs"))
jobs = get_recent_scrape_jobs(limit=10)
if jobs:
    df = pd.DataFrame(jobs)
    display_cols = ["id", "source", "category", "query", "location", "status",
                    "leads_found", "leads_new", "leads_duplicate", "started_at", "finished_at"]
    display_cols = [c for c in display_cols if c in df.columns]
    df = translate_columns(df, display_cols)
    st.dataframe(df, use_container_width=True, hide_index=True)
else:
    st.caption(t("no_scrape_jobs_yet"))
