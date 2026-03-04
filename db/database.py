import sqlite3
import os
import json

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "crm.db")

SCHEMA = """
CREATE TABLE IF NOT EXISTS leads (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    phone TEXT,
    email TEXT,
    business_name TEXT,
    address TEXT,
    website TEXT,
    category TEXT,
    subcategory TEXT,
    source TEXT NOT NULL,
    source_url TEXT,
    location TEXT,
    status TEXT NOT NULL DEFAULT 'New',
    notes TEXT DEFAULT '',
    google_place_id TEXT,
    raw_data TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_leads_phone_source
    ON leads(phone, source) WHERE phone IS NOT NULL AND phone != '';

CREATE UNIQUE INDEX IF NOT EXISTS idx_leads_email_source
    ON leads(email, source) WHERE email IS NOT NULL AND email != '';

CREATE TABLE IF NOT EXISTS categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    keywords TEXT NOT NULL DEFAULT '[]',
    is_custom INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS scrape_jobs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source TEXT NOT NULL,
    category TEXT,
    query TEXT,
    location TEXT,
    status TEXT NOT NULL DEFAULT 'Running',
    leads_found INTEGER DEFAULT 0,
    leads_new INTEGER DEFAULT 0,
    leads_duplicate INTEGER DEFAULT 0,
    error_message TEXT,
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    finished_at TIMESTAMP
);

CREATE TABLE IF NOT EXISTS settings (
    key TEXT PRIMARY KEY,
    value TEXT
);
"""

SEED_CATEGORIES = [
    ("Medical", '["doctor", "dentist", "clinic", "hospital", "physician", "surgeon", "therapist", "pharmacy", "chiropractor", "optometrist"]', 0),
    ("Legal", '["lawyer", "attorney", "law firm", "legal services", "notary", "paralegal"]', 0),
    ("Finance", '["accountant", "financial advisor", "bank", "mortgage", "insurance", "tax", "CPA", "investment"]', 0),
]


def get_connection() -> sqlite3.Connection:
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_db():
    conn = get_connection()
    conn.executescript(SCHEMA)
    for name, keywords, is_custom in SEED_CATEGORIES:
        conn.execute(
            "INSERT OR IGNORE INTO categories (name, keywords, is_custom) VALUES (?, ?, ?)",
            (name, keywords, is_custom),
        )
    conn.commit()
    conn.close()
