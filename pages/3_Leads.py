import streamlit as st
import pandas as pd
from db.database import init_db
from db.queries import get_leads, get_categories, get_leads_by_status_stats, update_lead_status, update_lead_notes, delete_leads
from i18n import (
    t, inject_rtl_css, STATUS_VALUES, translated_statuses,
    status_display_to_db, status_db_to_display, translate_columns,
)
from styles import inject_custom_css, section_header, status_badge, mini_status_bar

init_db()
inject_rtl_css()
inject_custom_css()

st.markdown(section_header(t("leads"), "👥"), unsafe_allow_html=True)

display_statuses = translated_statuses()

# --- Pipeline mini-bar ---
status_data = get_leads_by_status_stats()
if status_data:
    status_counts = {row["status"]: row["count"] for row in status_data}
    total_pipeline = sum(status_counts.values())
    st.markdown(f"**{t('pipeline_overview')}**")
    st.markdown(mini_status_bar(status_counts, total_pipeline), unsafe_allow_html=True)
    # Legend
    legend_html = " ".join(
        f'{status_badge(status_db_to_display(s))} <span style="font-size:0.82rem;color:#64748b;">{c}</span>&nbsp;&nbsp;'
        for s, c in status_counts.items() if c > 0
    )
    st.markdown(legend_html, unsafe_allow_html=True)
    st.markdown("")

# --- Filters ---
col1, col2, col3, col4 = st.columns(4)
with col1:
    search = st.text_input(t("search"), placeholder=t("search_placeholder"))
with col2:
    cats = get_categories()
    cat_filter = st.selectbox(t("category"), [t("all")] + [c.name for c in cats])
with col3:
    status_filter = st.selectbox(t("status"), [t("all")] + display_statuses)
with col4:
    source_filter = st.selectbox(t("source"), [t("all"), "Google Places", "Yellow Pages", "Custom URL"])

# Convert translated filter values back to English for DB query
db_cat = cat_filter if cat_filter != t("all") else None
db_status = status_display_to_db(status_filter) if status_filter != t("all") else None
db_source = source_filter if source_filter != t("all") else None

leads = get_leads(search=search, category=db_cat, status=db_status, source=db_source)

st.caption(t("leads_found_count", count=len(leads)))

if not leads:
    st.info(t("no_leads_match"))
    st.stop()

df = pd.DataFrame(leads)
display_cols = ["id", "business_name", "name", "phone", "email", "address",
                "website", "category", "source", "location", "status", "notes", "created_at"]
display_cols = [c for c in display_cols if c in df.columns]

# --- Bulk actions ---
with st.expander(t("bulk_actions")):
    selected_ids = st.multiselect(t("select_lead_ids"), df["id"].tolist())
    bcol1, bcol2 = st.columns(2)
    with bcol1:
        bulk_status = st.selectbox(t("set_status_to"), display_statuses, key="bulk_status")
        if st.button(t("apply_status")) and selected_ids:
            db_bulk_status = status_display_to_db(bulk_status)
            for lid in selected_ids:
                update_lead_status(lid, db_bulk_status)
            st.success(t("updated_leads", count=len(selected_ids)))
            st.rerun()
    with bcol2:
        if st.button(t("delete_selected"), type="secondary") and selected_ids:
            delete_leads(selected_ids)
            st.success(t("deleted_leads", count=len(selected_ids)))
            st.rerun()

# --- Data table with status badges ---
df_display = df[display_cols].copy()
# Translate status for display
df_display["status"] = df_display["status"].apply(status_db_to_display)
df_display = translate_columns(df_display, display_cols)
st.dataframe(df_display, use_container_width=True, hide_index=True)

# --- Inline editor ---
st.markdown("")
st.markdown(section_header(t("edit_lead"), "✏️"), unsafe_allow_html=True)
lead_id = st.number_input(t("lead_id_to_edit"), min_value=1, step=1)

matching = [l for l in leads if l["id"] == lead_id]
if matching:
    lead = matching[0]
    st.text(t("lead_info", business=lead['business_name'], phone=lead['phone'], email=lead['email']))
    ecol1, ecol2 = st.columns(2)
    with ecol1:
        current_index = STATUS_VALUES.index(lead["status"]) if lead["status"] in STATUS_VALUES else 0
        new_status = st.selectbox(t("status"), display_statuses, index=current_index, key="edit_status")
        if st.button(t("update_status")):
            update_lead_status(lead_id, status_display_to_db(new_status))
            st.success(t("status_updated"))
            st.rerun()
    with ecol2:
        new_notes = st.text_area(t("notes"), value=lead.get("notes", ""), key="edit_notes")
        if st.button(t("save_notes")):
            update_lead_notes(lead_id, new_notes)
            st.success(t("notes_saved"))
            st.rerun()
