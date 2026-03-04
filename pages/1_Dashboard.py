import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from db.database import init_db
from db.queries import (
    get_lead_stats, get_leads_by_category_stats,
    get_leads_by_source_stats, get_leads_by_status_stats,
    get_recent_scrape_jobs, get_leads,
)
from i18n import t, inject_rtl_css, status_db_to_display, translate_columns
from styles import (
    inject_custom_css, metric_card, section_header, status_badge,
    STATUS_COLORS, PLOTLY_COLORS, _STATUS_AR_TO_EN,
)

init_db()
inject_rtl_css()
inject_custom_css()

st.markdown(section_header(t("dashboard"), "📊"), unsafe_allow_html=True)

# --- Metric cards ---
stats = get_lead_stats()
total = stats.pop("total", 0)

STATUS_ICONS = {
    "New": "🆕",
    "Contacted": "📞",
    "Interested": "⭐",
    "Not Interested": "❌",
    "Converted": "✅",
}

cols = st.columns(5)
with cols[0]:
    st.markdown(metric_card("📊", t("total_leads"), total, "#3b82f6"), unsafe_allow_html=True)
for i, status in enumerate(["New", "Contacted", "Interested", "Not Interested"], start=1):
    with cols[i]:
        st.markdown(
            metric_card(
                STATUS_ICONS[status],
                status_db_to_display(status),
                stats.get(status, 0),
                STATUS_COLORS[status],
            ),
            unsafe_allow_html=True,
        )

st.markdown("")

# --- Charts ---
col_left, col_right = st.columns(2)

with col_left:
    st.markdown(section_header(t("leads_by_category"), "📁"), unsafe_allow_html=True)
    cat_data = get_leads_by_category_stats()
    if cat_data:
        df = pd.DataFrame(cat_data).sort_values("count", ascending=True)
        fig = px.bar(
            df, x="count", y="category", orientation="h",
            color_discrete_sequence=["#3b82f6"],
        )
        fig.update_layout(
            margin=dict(l=0, r=0, t=10, b=0),
            xaxis_title="", yaxis_title="",
            height=300,
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
        )
        fig.update_traces(marker_cornerradius=6)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.caption(t("no_data_yet"))

with col_right:
    st.markdown(section_header(t("leads_by_source"), "🌐"), unsafe_allow_html=True)
    src_data = get_leads_by_source_stats()
    if src_data:
        df = pd.DataFrame(src_data)
        fig = px.pie(
            df, values="count", names="source", hole=0.45,
            color_discrete_sequence=PLOTLY_COLORS,
        )
        fig.update_layout(
            margin=dict(l=0, r=0, t=10, b=0),
            height=300,
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            legend=dict(orientation="h", yanchor="bottom", y=-0.2),
        )
        fig.update_traces(textposition="inside", textinfo="label+percent")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.caption(t("no_data_yet"))

# --- Status funnel ---
col_funnel, col_completeness = st.columns(2)

with col_funnel:
    st.markdown(section_header(t("leads_by_status"), "📈"), unsafe_allow_html=True)
    status_data = get_leads_by_status_stats()
    if status_data:
        df = pd.DataFrame(status_data)
        # Ensure pipeline order
        order = ["New", "Contacted", "Interested", "Not Interested", "Converted"]
        df["_sort"] = df["status"].map({s: i for i, s in enumerate(order)})
        df = df.sort_values("_sort").drop(columns=["_sort"])
        colors = [STATUS_COLORS.get(s, "#6b7280") for s in df["status"]]
        display_labels = [status_db_to_display(s) for s in df["status"]]
        fig = go.Figure(go.Funnel(
            y=display_labels,
            x=df["count"].tolist(),
            marker=dict(color=colors),
            textinfo="value+percent initial",
        ))
        fig.update_layout(
            margin=dict(l=0, r=0, t=10, b=0),
            height=300,
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
        )
        st.plotly_chart(fig, use_container_width=True)

with col_completeness:
    st.markdown(section_header(t("lead_completeness"), "📋"), unsafe_allow_html=True)
    all_leads = get_leads(limit=10000)
    if all_leads:
        total_count = len(all_leads)
        phone_pct = sum(1 for l in all_leads if l.get("phone")) / total_count
        email_pct = sum(1 for l in all_leads if l.get("email")) / total_count
        web_pct = sum(1 for l in all_leads if l.get("website")) / total_count

        for label_key, pct, color in [
            ("with_phone", phone_pct, "#22c55e"),
            ("with_email", email_pct, "#3b82f6"),
            ("with_website", web_pct, "#8b5cf6"),
        ]:
            st.markdown(f"**{t(label_key)}** — {pct:.0%}")
            st.progress(pct)
    else:
        st.caption(t("no_data_yet"))

# --- Recent scrape jobs ---
st.markdown("")
st.markdown(section_header(t("recent_scrape_jobs"), "🕐"), unsafe_allow_html=True)
jobs = get_recent_scrape_jobs(limit=10)
if jobs:
    df = pd.DataFrame(jobs)
    display_cols = ["id", "source", "category", "query", "location", "status",
                    "leads_found", "leads_new", "leads_duplicate", "started_at", "finished_at"]
    display_cols = [c for c in display_cols if c in df.columns]
    # Color the status column
    df["status"] = df["status"].apply(
        lambda s: s  # keep raw for dataframe
    )
    df = translate_columns(df, display_cols)
    st.dataframe(df, use_container_width=True, hide_index=True)
else:
    st.caption(t("no_scrape_jobs_yet"))
