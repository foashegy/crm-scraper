import json
import sqlite3
from typing import Optional
from .database import get_connection
from .models import Lead, ScrapeJob, Category


# --- Leads ---

def insert_lead(lead: Lead) -> tuple[bool, int]:
    """Insert a lead. Returns (is_new, lead_id). Skips duplicates."""
    conn = get_connection()
    try:
        cur = conn.execute(
            """INSERT INTO leads
               (name, phone, email, business_name, address, website,
                category, subcategory, source, source_url, location,
                status, notes, google_place_id, raw_data)
               VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (lead.name, lead.phone, lead.email, lead.business_name,
             lead.address, lead.website, lead.category, lead.subcategory,
             lead.source, lead.source_url, lead.location, lead.status,
             lead.notes, lead.google_place_id, lead.raw_data),
        )
        conn.commit()
        return True, cur.lastrowid
    except sqlite3.IntegrityError:
        conn.rollback()
        return False, 0
    finally:
        conn.close()


def get_leads(
    search: str = "",
    category: Optional[str] = None,
    status: Optional[str] = None,
    source: Optional[str] = None,
    location: Optional[str] = None,
    limit: int = 500,
    offset: int = 0,
) -> list[dict]:
    conn = get_connection()
    clauses, params = [], []
    if search:
        clauses.append("(name LIKE ? OR business_name LIKE ? OR phone LIKE ? OR email LIKE ?)")
        w = f"%{search}%"
        params.extend([w, w, w, w])
    if category:
        clauses.append("category = ?")
        params.append(category)
    if status:
        clauses.append("status = ?")
        params.append(status)
    if source:
        clauses.append("source = ?")
        params.append(source)
    if location:
        clauses.append("location LIKE ?")
        params.append(f"%{location}%")

    where = " WHERE " + " AND ".join(clauses) if clauses else ""
    rows = conn.execute(
        f"SELECT * FROM leads{where} ORDER BY created_at DESC LIMIT ? OFFSET ?",
        params + [limit, offset],
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def update_lead_status(lead_id: int, status: str):
    conn = get_connection()
    conn.execute(
        "UPDATE leads SET status=?, updated_at=CURRENT_TIMESTAMP WHERE id=?",
        (status, lead_id),
    )
    conn.commit()
    conn.close()


def update_lead_notes(lead_id: int, notes: str):
    conn = get_connection()
    conn.execute(
        "UPDATE leads SET notes=?, updated_at=CURRENT_TIMESTAMP WHERE id=?",
        (notes, lead_id),
    )
    conn.commit()
    conn.close()


def delete_leads(lead_ids: list[int]):
    conn = get_connection()
    placeholders = ",".join("?" for _ in lead_ids)
    conn.execute(f"DELETE FROM leads WHERE id IN ({placeholders})", lead_ids)
    conn.commit()
    conn.close()


# --- Stats ---

def get_lead_stats() -> dict:
    conn = get_connection()
    total = conn.execute("SELECT COUNT(*) FROM leads").fetchone()[0]
    by_status = {
        row["status"]: row["cnt"]
        for row in conn.execute("SELECT status, COUNT(*) as cnt FROM leads GROUP BY status")
    }
    conn.close()
    return {"total": total, **by_status}


def get_leads_by_category_stats() -> list[dict]:
    conn = get_connection()
    rows = conn.execute(
        "SELECT COALESCE(category,'Uncategorized') as category, COUNT(*) as count FROM leads GROUP BY category ORDER BY count DESC"
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_leads_by_source_stats() -> list[dict]:
    conn = get_connection()
    rows = conn.execute(
        "SELECT source, COUNT(*) as count FROM leads GROUP BY source ORDER BY count DESC"
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_leads_by_status_stats() -> list[dict]:
    conn = get_connection()
    rows = conn.execute(
        "SELECT status, COUNT(*) as count FROM leads GROUP BY status ORDER BY count DESC"
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


# --- Scrape Jobs ---

def insert_scrape_job(job: ScrapeJob) -> int:
    conn = get_connection()
    cur = conn.execute(
        "INSERT INTO scrape_jobs (source, category, query, location, status) VALUES (?,?,?,?,?)",
        (job.source, job.category, job.query, job.location, job.status),
    )
    conn.commit()
    job_id = cur.lastrowid
    conn.close()
    return job_id


def update_scrape_job(job_id: int, **kwargs):
    conn = get_connection()
    sets = ", ".join(f"{k}=?" for k in kwargs)
    vals = list(kwargs.values())
    conn.execute(
        f"UPDATE scrape_jobs SET {sets}, finished_at=CURRENT_TIMESTAMP WHERE id=?",
        vals + [job_id],
    )
    conn.commit()
    conn.close()


def get_recent_scrape_jobs(limit: int = 20) -> list[dict]:
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM scrape_jobs ORDER BY started_at DESC LIMIT ?", (limit,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


# --- Categories ---

def get_categories() -> list[Category]:
    conn = get_connection()
    rows = conn.execute("SELECT * FROM categories ORDER BY is_custom, name").fetchall()
    conn.close()
    return [
        Category(id=r["id"], name=r["name"], keywords=json.loads(r["keywords"]), is_custom=bool(r["is_custom"]))
        for r in rows
    ]


def add_category(name: str, keywords: list[str]) -> int:
    conn = get_connection()
    cur = conn.execute(
        "INSERT INTO categories (name, keywords, is_custom) VALUES (?, ?, 1)",
        (name, json.dumps(keywords)),
    )
    conn.commit()
    cat_id = cur.lastrowid
    conn.close()
    return cat_id


def update_category(cat_id: int, name: str, keywords: list[str]):
    conn = get_connection()
    conn.execute(
        "UPDATE categories SET name=?, keywords=? WHERE id=?",
        (name, json.dumps(keywords), cat_id),
    )
    conn.commit()
    conn.close()


def delete_category(cat_id: int):
    conn = get_connection()
    conn.execute("DELETE FROM categories WHERE id=? AND is_custom=1", (cat_id,))
    conn.commit()
    conn.close()


# --- Settings ---

def get_setting(key: str, default: str = "") -> str:
    conn = get_connection()
    row = conn.execute("SELECT value FROM settings WHERE key=?", (key,)).fetchone()
    conn.close()
    return row["value"] if row else default


def set_setting(key: str, value: str):
    conn = get_connection()
    conn.execute(
        "INSERT INTO settings (key, value) VALUES (?, ?) ON CONFLICT(key) DO UPDATE SET value=?",
        (key, value, value),
    )
    conn.commit()
    conn.close()


# --- Maintenance ---

def purge_duplicates() -> int:
    """Remove duplicate leads keeping the oldest entry. Returns count removed."""
    conn = get_connection()
    # Remove dupes by phone+source
    cur = conn.execute("""
        DELETE FROM leads WHERE id NOT IN (
            SELECT MIN(id) FROM leads
            WHERE phone IS NOT NULL AND phone != ''
            GROUP BY phone, source
        ) AND phone IS NOT NULL AND phone != ''
    """)
    removed = cur.rowcount
    # Remove dupes by email+source
    cur = conn.execute("""
        DELETE FROM leads WHERE id NOT IN (
            SELECT MIN(id) FROM leads
            WHERE email IS NOT NULL AND email != ''
            GROUP BY email, source
        ) AND email IS NOT NULL AND email != ''
    """)
    removed += cur.rowcount
    conn.commit()
    conn.close()
    return removed
