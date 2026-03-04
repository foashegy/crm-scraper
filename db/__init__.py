from .database import get_connection, init_db
from .models import Lead, ScrapeJob, Category
from .queries import (
    insert_lead, get_leads, update_lead_status, update_lead_notes,
    delete_leads, get_lead_stats, get_leads_by_category_stats,
    get_leads_by_source_stats, get_leads_by_status_stats,
    insert_scrape_job, update_scrape_job, get_recent_scrape_jobs,
    get_categories, add_category, update_category, delete_category,
    get_setting, set_setting, purge_duplicates,
)
