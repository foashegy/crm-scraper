import os
import streamlit as st
import pandas as pd
from dotenv import load_dotenv
from db.database import init_db
from db.models import ScrapeJob
from db.queries import get_categories, insert_lead, insert_scrape_job, update_scrape_job
from scrapers.google_places import GooglePlacesScraper
from scrapers.yellow_pages import YellowPagesScraper
from scrapers.custom_url import CustomURLScraper
from i18n import t, inject_rtl_css

load_dotenv()
init_db()
inject_rtl_css()

st.header(t("scraper"))

# --- Source selector ---
source_options = ["Google Places", "Yellow Pages", "Custom URL"]
source = st.selectbox(t("data_source"), source_options)

# --- Category & location ---
categories = get_categories()
cat_names = [c.name for c in categories]

if source == "Custom URL":
    url = st.text_input(t("url_to_scrape"), placeholder=t("url_placeholder"))
    category = st.selectbox(t("category_optional"), [""] + cat_names)
    location = st.text_input(t("location_optional"), placeholder=t("location_placeholder"))
    query_display = url
else:
    category = st.selectbox(t("category"), cat_names)
    selected_cat = next((c for c in categories if c.name == category), None)
    keyword_options = selected_cat.keywords if selected_cat else []
    if keyword_options:
        query = st.selectbox(t("search_keyword"), keyword_options + [t("custom_option")])
        if query == t("custom_option"):
            query = st.text_input(t("custom_search_query"))
    else:
        query = st.text_input(t("search_query"), placeholder=t("query_placeholder"))
    location = st.text_input(t("location"), placeholder=t("location_placeholder"))
    query_display = query

# --- Run scrape ---
if st.button(t("run_scrape"), type="primary"):
    if source == "Custom URL" and not url:
        st.error(t("enter_url"))
    elif source != "Custom URL" and not query:
        st.error(t("enter_search_query"))
    elif source != "Custom URL" and not location:
        st.error(t("enter_location"))
    else:
        job = ScrapeJob(source=source, category=category, query=query_display, location=location)
        job_id = insert_scrape_job(job)

        progress = st.progress(0, text=t("starting_scrape"))
        try:
            if source == "Google Places":
                api_key = os.getenv("GOOGLE_PLACES_API_KEY", "")
                if not api_key or api_key == "your_api_key_here":
                    st.error(t("set_api_key"))
                    update_scrape_job(job_id, status="Failed", error_message="Missing API key")
                    st.stop()
                scraper = GooglePlacesScraper(api_key)
                progress.progress(20, text=t("querying_google"))
                leads = scraper.scrape(query, location, category=category)

            elif source == "Yellow Pages":
                scraper = YellowPagesScraper(max_pages=3)
                progress.progress(20, text=t("scraping_yp"))
                leads = scraper.scrape(query, location, category=category)

            else:  # Custom URL
                scraper = CustomURLScraper()
                progress.progress(20, text=t("fetching_url", url=url))
                leads = scraper.scrape(url, location, category=category or "")

            progress.progress(70, text=t("found_results_processing", count=len(leads)))

            # Show preview
            if leads:
                preview_data = [
                    {
                        t("col_business"): l.business_name,
                        t("col_phone"): l.phone,
                        t("col_email"): l.email,
                        t("col_address"): l.address,
                        t("col_website"): l.website,
                    }
                    for l in leads
                ]
                st.session_state["scraped_leads"] = leads
                st.session_state["scrape_job_id"] = job_id
                progress.progress(100, text=t("done"))
                st.success(t("found_results", count=len(leads)))
                st.dataframe(pd.DataFrame(preview_data), use_container_width=True, hide_index=True)
            else:
                progress.progress(100, text=t("done"))
                st.warning(t("no_results"))
                update_scrape_job(job_id, status="Completed", leads_found=0, leads_new=0, leads_duplicate=0)

        except Exception as e:
            progress.progress(100, text=t("failed"))
            st.error(t("scrape_failed", error=e))
            update_scrape_job(job_id, status="Failed", error_message=str(e)[:500])

# --- Save to DB ---
if "scraped_leads" in st.session_state and st.session_state["scraped_leads"]:
    if st.button(t("save_leads_db"), type="primary"):
        leads = st.session_state["scraped_leads"]
        job_id = st.session_state.get("scrape_job_id")
        new_count, dup_count = 0, 0
        for lead in leads:
            is_new, _ = insert_lead(lead)
            if is_new:
                new_count += 1
            else:
                dup_count += 1
        if job_id:
            update_scrape_job(
                job_id, status="Completed",
                leads_found=len(leads), leads_new=new_count, leads_duplicate=dup_count,
            )
        st.success(t("saved_leads", new_count=new_count, dup_count=dup_count))
        del st.session_state["scraped_leads"]
        st.rerun()
