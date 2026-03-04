from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime


@dataclass
class Lead:
    name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    business_name: Optional[str] = None
    address: Optional[str] = None
    website: Optional[str] = None
    category: Optional[str] = None
    subcategory: Optional[str] = None
    source: str = ""
    source_url: Optional[str] = None
    location: Optional[str] = None
    status: str = "New"
    notes: str = ""
    google_place_id: Optional[str] = None
    raw_data: Optional[str] = None
    id: Optional[int] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


@dataclass
class ScrapeJob:
    source: str = ""
    category: Optional[str] = None
    query: Optional[str] = None
    location: Optional[str] = None
    status: str = "Running"
    leads_found: int = 0
    leads_new: int = 0
    leads_duplicate: int = 0
    error_message: Optional[str] = None
    id: Optional[int] = None
    started_at: Optional[str] = None
    finished_at: Optional[str] = None


@dataclass
class Category:
    name: str = ""
    keywords: list = field(default_factory=list)
    is_custom: bool = False
    id: Optional[int] = None
