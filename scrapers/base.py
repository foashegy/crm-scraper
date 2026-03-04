from abc import ABC, abstractmethod
from db.models import Lead


class BaseScraper(ABC):
    """Abstract base class for all scrapers."""

    source_name: str = "Unknown"

    @abstractmethod
    def scrape(self, query: str, location: str, category: str = "", **kwargs) -> list[Lead]:
        """Run the scrape and return a list of Lead objects."""
        ...

    def _make_lead(self, **kwargs) -> Lead:
        kwargs.setdefault("source", self.source_name)
        return Lead(**kwargs)
