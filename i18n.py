"""Bilingual (English / Arabic) support for the CRM Scraper app."""

import streamlit as st
import pandas as pd


# ---------------------------------------------------------------------------
# Core helpers
# ---------------------------------------------------------------------------

def get_lang() -> str:
    return st.session_state.get("lang", "en")


def t(key: str, **kwargs) -> str:
    """Return the translated string for *key* in the current language.

    Supports ``{placeholder}`` interpolation via **kwargs.
    Falls back to English if the key or language is missing.
    """
    lang = get_lang()
    entry = TRANSLATIONS.get(key, {})
    text = entry.get(lang, entry.get("en", key))
    if kwargs:
        text = text.format(**kwargs)
    return text


# ---------------------------------------------------------------------------
# Status round-trip helpers
# ---------------------------------------------------------------------------

STATUS_VALUES = ["New", "Contacted", "Interested", "Not Interested", "Converted"]

_STATUS_AR = {
    "New": "جديد",
    "Contacted": "تم التواصل",
    "Interested": "مهتم",
    "Not Interested": "غير مهتم",
    "Converted": "تم التحويل",
}

_STATUS_AR_TO_EN = {v: k for k, v in _STATUS_AR.items()}


def translated_statuses() -> list[str]:
    if get_lang() == "ar":
        return [_STATUS_AR[s] for s in STATUS_VALUES]
    return list(STATUS_VALUES)


def status_display_to_db(display: str) -> str:
    """Convert a (possibly translated) status label back to English for DB."""
    if display in STATUS_VALUES:
        return display
    return _STATUS_AR_TO_EN.get(display, display)


def status_db_to_display(db_val: str) -> str:
    """Convert an English DB status to the current-language display label."""
    if get_lang() == "ar":
        return _STATUS_AR.get(db_val, db_val)
    return db_val


# ---------------------------------------------------------------------------
# Column translation
# ---------------------------------------------------------------------------

COLUMN_TRANSLATIONS: dict[str, dict[str, str]] = {
    "id": {"en": "ID", "ar": "المعرف"},
    "business_name": {"en": "Business", "ar": "النشاط التجاري"},
    "name": {"en": "Name", "ar": "الاسم"},
    "phone": {"en": "Phone", "ar": "الهاتف"},
    "email": {"en": "Email", "ar": "البريد الإلكتروني"},
    "address": {"en": "Address", "ar": "العنوان"},
    "website": {"en": "Website", "ar": "الموقع الإلكتروني"},
    "category": {"en": "Category", "ar": "الفئة"},
    "source": {"en": "Source", "ar": "المصدر"},
    "location": {"en": "Location", "ar": "الموقع"},
    "status": {"en": "Status", "ar": "الحالة"},
    "notes": {"en": "Notes", "ar": "ملاحظات"},
    "created_at": {"en": "Created At", "ar": "تاريخ الإنشاء"},
    "query": {"en": "Query", "ar": "استعلام"},
    "leads_found": {"en": "Leads Found", "ar": "عملاء محتملون"},
    "leads_new": {"en": "New Leads", "ar": "عملاء جدد"},
    "leads_duplicate": {"en": "Duplicates", "ar": "مكرر"},
    "started_at": {"en": "Started At", "ar": "وقت البدء"},
    "finished_at": {"en": "Finished At", "ar": "وقت الانتهاء"},
    "error_message": {"en": "Error", "ar": "خطأ"},
}


def translate_columns(df: pd.DataFrame, cols: list[str] | None = None) -> pd.DataFrame:
    """Return a copy of *df* with column headers translated to the current language."""
    lang = get_lang()
    rename_map = {}
    target_cols = cols if cols is not None else list(df.columns)
    for c in target_cols:
        if c in COLUMN_TRANSLATIONS:
            rename_map[c] = COLUMN_TRANSLATIONS[c].get(lang, c)
    return df.rename(columns=rename_map)


# ---------------------------------------------------------------------------
# RTL CSS injection
# ---------------------------------------------------------------------------

RTL_CSS = """
<style>
    /* Global RTL */
    .main .block-container, .stSidebar {
        direction: rtl;
        text-align: right;
    }
    /* Keep dataframes LTR for readability */
    .stDataFrame, .stDataFrame * {
        direction: ltr !important;
        text-align: left !important;
    }
    /* Metric cards */
    [data-testid="stMetricValue"], [data-testid="stMetricLabel"] {
        direction: rtl;
        text-align: right;
    }
</style>
"""


def inject_rtl_css():
    """Inject RTL stylesheet when current language is Arabic."""
    if get_lang() == "ar":
        st.markdown(RTL_CSS, unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Translation strings (~105 keys)
# ---------------------------------------------------------------------------

TRANSLATIONS: dict[str, dict[str, str]] = {
    # -- app.py --
    "app_title": {
        "en": "CRM Lead Scraper",
        "ar": "نظام جمع بيانات العملاء المحتملين",
    },
    "app_description": {
        "en": "Collect professional contact info from multiple sources to generate real estate sales leads. Use the sidebar to navigate between pages.",
        "ar": "اجمع معلومات التواصل المهنية من مصادر متعددة لتوليد عملاء محتملين لمبيعات العقارات. استخدم الشريط الجانبي للتنقل بين الصفحات.",
    },
    "app_get_started": {
        "en": "Select a page from the sidebar to get started.",
        "ar": "اختر صفحة من الشريط الجانبي للبدء.",
    },
    "language_label": {
        "en": "Language / اللغة",
        "ar": "Language / اللغة",
    },

    # -- Dashboard --
    "dashboard": {"en": "Dashboard", "ar": "لوحة التحكم"},
    "total_leads": {"en": "Total Leads", "ar": "إجمالي العملاء"},
    "leads_by_category": {"en": "Leads by Category", "ar": "العملاء حسب الفئة"},
    "leads_by_source": {"en": "Leads by Source", "ar": "العملاء حسب المصدر"},
    "leads_by_status": {"en": "Leads by Status", "ar": "العملاء حسب الحالة"},
    "recent_scrape_jobs": {"en": "Recent Scrape Jobs", "ar": "عمليات الجمع الأخيرة"},
    "no_data_yet": {"en": "No data yet.", "ar": "لا توجد بيانات بعد."},
    "no_scrape_jobs_yet": {
        "en": "No scrape jobs yet. Go to the Scraper page to start one.",
        "ar": "لا توجد عمليات جمع بعد. انتقل إلى صفحة الجامع لبدء عملية.",
    },

    # -- Statuses (display labels) --
    "status_new": {"en": "New", "ar": "جديد"},
    "status_contacted": {"en": "Contacted", "ar": "تم التواصل"},
    "status_interested": {"en": "Interested", "ar": "مهتم"},
    "status_not_interested": {"en": "Not Interested", "ar": "غير مهتم"},
    "status_converted": {"en": "Converted", "ar": "تم التحويل"},

    # -- Scraper --
    "scraper": {"en": "Scraper", "ar": "الجامع"},
    "data_source": {"en": "Data Source", "ar": "مصدر البيانات"},
    "url_to_scrape": {"en": "URL to scrape", "ar": "رابط الجمع"},
    "url_placeholder": {"en": "https://example.com/directory", "ar": "https://example.com/directory"},
    "category_optional": {"en": "Category (optional)", "ar": "الفئة (اختياري)"},
    "location_optional": {"en": "Location tag (optional)", "ar": "الموقع (اختياري)"},
    "location_placeholder": {"en": "e.g., Miami, FL", "ar": "مثال: الرياض"},
    "category": {"en": "Category", "ar": "الفئة"},
    "search_keyword": {"en": "Search keyword", "ar": "كلمة البحث"},
    "custom_option": {"en": "Custom...", "ar": "مخصص..."},
    "custom_search_query": {"en": "Custom search query", "ar": "استعلام بحث مخصص"},
    "search_query": {"en": "Search query", "ar": "استعلام البحث"},
    "query_placeholder": {"en": "e.g., dentists", "ar": "مثال: أطباء أسنان"},
    "location": {"en": "Location", "ar": "الموقع"},
    "run_scrape": {"en": "Run Scrape", "ar": "بدء الجمع"},
    "enter_url": {"en": "Please enter a URL.", "ar": "يرجى إدخال رابط."},
    "enter_search_query": {"en": "Please enter a search query.", "ar": "يرجى إدخال استعلام بحث."},
    "enter_location": {"en": "Please enter a location.", "ar": "يرجى إدخال موقع."},
    "starting_scrape": {"en": "Starting scrape...", "ar": "جاري بدء الجمع..."},
    "set_api_key": {
        "en": "Set your Google Places API key in .env or on the Settings page.",
        "ar": "قم بتعيين مفتاح Google Places API في ملف .env أو في صفحة الإعدادات.",
    },
    "querying_google": {"en": "Querying Google Places API...", "ar": "جاري الاستعلام من Google Places API..."},
    "scraping_yp": {"en": "Scraping Yellow Pages...", "ar": "جاري جمع البيانات من Yellow Pages..."},
    "fetching_url": {"en": "Fetching {url}...", "ar": "جاري جلب {url}..."},
    "found_results_processing": {"en": "Found {count} results. Processing...", "ar": "تم العثور على {count} نتيجة. جاري المعالجة..."},
    "done": {"en": "Done!", "ar": "تم!"},
    "found_results": {"en": "Found {count} results.", "ar": "تم العثور على {count} نتيجة."},
    "no_results": {"en": "No results found.", "ar": "لم يتم العثور على نتائج."},
    "scrape_failed": {"en": "Scrape failed: {error}", "ar": "فشل الجمع: {error}"},
    "failed": {"en": "Failed.", "ar": "فشل."},
    "save_leads_db": {"en": "Save Leads to Database", "ar": "حفظ العملاء في قاعدة البيانات"},
    "saved_leads": {
        "en": "Saved! {new_count} new leads, {dup_count} duplicates skipped.",
        "ar": "تم الحفظ! {new_count} عميل جديد، تم تخطي {dup_count} مكرر.",
    },

    # -- Preview columns --
    "col_business": {"en": "Business", "ar": "النشاط التجاري"},
    "col_phone": {"en": "Phone", "ar": "الهاتف"},
    "col_email": {"en": "Email", "ar": "البريد الإلكتروني"},
    "col_address": {"en": "Address", "ar": "العنوان"},
    "col_website": {"en": "Website", "ar": "الموقع الإلكتروني"},

    # -- Leads page --
    "leads": {"en": "Leads", "ar": "العملاء المحتملون"},
    "search": {"en": "Search", "ar": "بحث"},
    "search_placeholder": {"en": "Name, phone, email...", "ar": "الاسم، الهاتف، البريد..."},
    "all": {"en": "All", "ar": "الكل"},
    "status": {"en": "Status", "ar": "الحالة"},
    "source": {"en": "Source", "ar": "المصدر"},
    "leads_found_count": {"en": "{count} leads found", "ar": "تم العثور على {count} عميل"},
    "no_leads_match": {
        "en": "No leads match your filters. Run a scrape first!",
        "ar": "لا يوجد عملاء يطابقون الفلاتر. قم بتشغيل عملية جمع أولاً!",
    },
    "bulk_actions": {"en": "Bulk Actions", "ar": "إجراءات جماعية"},
    "select_lead_ids": {"en": "Select lead IDs for bulk action", "ar": "اختر معرفات العملاء للإجراء الجماعي"},
    "set_status_to": {"en": "Set status to", "ar": "تعيين الحالة إلى"},
    "apply_status": {"en": "Apply Status", "ar": "تطبيق الحالة"},
    "updated_leads": {"en": "Updated {count} leads.", "ar": "تم تحديث {count} عميل."},
    "delete_selected": {"en": "Delete Selected", "ar": "حذف المحدد"},
    "deleted_leads": {"en": "Deleted {count} leads.", "ar": "تم حذف {count} عميل."},
    "edit_lead": {"en": "Edit Lead", "ar": "تعديل العميل"},
    "lead_id_to_edit": {"en": "Lead ID to edit", "ar": "معرف العميل للتعديل"},
    "lead_info": {
        "en": "Business: {business}  |  Phone: {phone}  |  Email: {email}",
        "ar": "النشاط: {business}  |  الهاتف: {phone}  |  البريد: {email}",
    },
    "update_status": {"en": "Update Status", "ar": "تحديث الحالة"},
    "status_updated": {"en": "Status updated.", "ar": "تم تحديث الحالة."},
    "notes": {"en": "Notes", "ar": "ملاحظات"},
    "save_notes": {"en": "Save Notes", "ar": "حفظ الملاحظات"},
    "notes_saved": {"en": "Notes saved.", "ar": "تم حفظ الملاحظات."},

    # -- Export page --
    "export_leads": {"en": "Export Leads", "ar": "تصدير العملاء"},
    "leads_to_export": {"en": "{count} leads to export", "ar": "{count} عميل للتصدير"},
    "no_leads_match_export": {"en": "No leads match your filters.", "ar": "لا يوجد عملاء يطابقون الفلاتر."},
    "download_csv": {"en": "Download CSV", "ar": "تحميل CSV"},
    "download_excel": {"en": "Download Excel", "ar": "تحميل Excel"},
    "showing_first": {
        "en": "Showing first 20 of {count} leads.",
        "ar": "عرض أول 20 من {count} عميل.",
    },

    # -- Settings page --
    "settings": {"en": "Settings", "ar": "الإعدادات"},
    "api_keys": {"en": "API Keys", "ar": "مفاتيح API"},
    "api_key_configured": {
        "en": "Google Places API key configured ({key}...)",
        "ar": "تم تكوين مفتاح Google Places API ({key}...)",
    },
    "api_key_not_set": {
        "en": "Google Places API key not set. Add it to the `.env` file.",
        "ar": "لم يتم تعيين مفتاح Google Places API. أضفه إلى ملف `.env`.",
    },
    "categories": {"en": "Categories", "ar": "الفئات"},
    "custom_prefix": {"en": "[Custom] ", "ar": "[مخصص] "},
    "name": {"en": "Name", "ar": "الاسم"},
    "keywords_per_line": {"en": "Keywords (one per line)", "ar": "الكلمات المفتاحية (واحدة في كل سطر)"},
    "save": {"en": "Save", "ar": "حفظ"},
    "updated": {"en": "Updated.", "ar": "تم التحديث."},
    "delete": {"en": "Delete", "ar": "حذف"},
    "deleted": {"en": "Deleted.", "ar": "تم الحذف."},
    "add_custom_category": {"en": "Add Custom Category", "ar": "إضافة فئة مخصصة"},
    "category_name": {"en": "Category name", "ar": "اسم الفئة"},
    "add_category": {"en": "Add Category", "ar": "إضافة فئة"},
    "added_category": {"en": "Added category: {name}", "ar": "تمت إضافة الفئة: {name}"},
    "failed_error": {"en": "Failed: {error}", "ar": "فشل: {error}"},
    "enter_category_name": {"en": "Enter a category name.", "ar": "أدخل اسم الفئة."},
    "maintenance": {"en": "Maintenance", "ar": "الصيانة"},
    "purge_duplicates": {"en": "Purge Duplicate Leads", "ar": "حذف العملاء المكررين"},
    "removed_duplicates": {
        "en": "Removed {count} duplicate leads.",
        "ar": "تم حذف {count} عميل مكرر.",
    },

    # -- Visual overhaul: Hero & Home --
    "hero_tagline": {
        "en": "Collect professional contact info from multiple sources to generate real estate sales leads.",
        "ar": "اجمع معلومات التواصل المهنية من مصادر متعددة لتوليد عملاء محتملين لمبيعات العقارات.",
    },
    "feature_scrape_title": {"en": "Scrape", "ar": "جمع البيانات"},
    "feature_scrape_desc": {
        "en": "Pull leads from Google Places, Yellow Pages, or any URL automatically.",
        "ar": "اجمع العملاء من Google Places وYellow Pages أو أي رابط تلقائيًا.",
    },
    "feature_manage_title": {"en": "Manage", "ar": "إدارة"},
    "feature_manage_desc": {
        "en": "Filter, search, and update lead statuses through the pipeline.",
        "ar": "فلتر وابحث وحدّث حالات العملاء عبر خط الأنابيب.",
    },
    "feature_export_title": {"en": "Export", "ar": "تصدير"},
    "feature_export_desc": {
        "en": "Download your data as CSV or Excel in one click.",
        "ar": "حمّل بياناتك كـ CSV أو Excel بنقرة واحدة.",
    },
    "go_to_scraper": {"en": "Start Scraping", "ar": "ابدأ الجمع"},
    "go_to_dashboard": {"en": "View Dashboard", "ar": "عرض لوحة التحكم"},

    # -- Visual overhaul: Dashboard --
    "lead_completeness": {"en": "Lead Completeness", "ar": "اكتمال البيانات"},
    "with_phone": {"en": "With Phone", "ar": "مع هاتف"},
    "with_email": {"en": "With Email", "ar": "مع بريد"},
    "with_website": {"en": "With Website", "ar": "مع موقع"},

    # -- Visual overhaul: Scraper --
    "source_google_desc": {
        "en": "Search the Google Places API for local businesses.",
        "ar": "ابحث في Google Places API عن الأنشطة التجارية المحلية.",
    },
    "source_yp_desc": {
        "en": "Scrape business listings from YellowPages.com.",
        "ar": "اجمع بيانات الأنشطة التجارية من YellowPages.com.",
    },
    "source_url_desc": {
        "en": "Extract contacts from any web page via URL.",
        "ar": "استخرج جهات الاتصال من أي صفحة ويب عبر الرابط.",
    },
    "results_summary": {"en": "Results Summary", "ar": "ملخص النتائج"},
    "new_leads": {"en": "New Leads", "ar": "عملاء جدد"},
    "duplicates": {"en": "Duplicates", "ar": "مكرر"},

    # -- Visual overhaul: Export --
    "csv_desc": {
        "en": "Comma-separated values, works everywhere.",
        "ar": "قيم مفصولة بفواصل، يعمل في كل مكان.",
    },
    "excel_desc": {
        "en": "Microsoft Excel spreadsheet format.",
        "ar": "تنسيق جداول بيانات Microsoft Excel.",
    },
    "export_summary": {"en": "Export Summary", "ar": "ملخص التصدير"},
    "total_available": {"en": "Total Available", "ar": "الإجمالي المتاح"},
    "filtered_count": {"en": "Filtered Count", "ar": "العدد المفلتر"},

    # -- Visual overhaul: Settings --
    "api_status": {"en": "API Status", "ar": "حالة API"},
    "configured": {"en": "Configured", "ar": "مكوّن"},
    "not_configured": {"en": "Not Configured", "ar": "غير مكوّن"},

    # -- Visual overhaul: Leads --
    "pipeline_overview": {"en": "Pipeline Overview", "ar": "نظرة عامة على خط الأنابيب"},
}
