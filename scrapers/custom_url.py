import requests
from bs4 import BeautifulSoup
from db.models import Lead
from .base import BaseScraper
from .utils import BROWSER_HEADERS, extract_phones, extract_emails


class CustomURLScraper(BaseScraper):
    source_name = "Custom URL"

    def scrape(self, query: str, location: str = "", category: str = "", **kwargs) -> list[Lead]:
        """query is the URL to scrape."""
        url = query
        try:
            resp = requests.get(url, headers=BROWSER_HEADERS, timeout=15)
            resp.raise_for_status()
        except requests.RequestException as e:
            raise RuntimeError(f"Failed to fetch {url}: {e}")

        soup = BeautifulSoup(resp.text, "html.parser")
        text = soup.get_text(" ", strip=True)

        phones = extract_phones(text)
        emails = extract_emails(text)

        # Try to get a page title as a name hint
        title = ""
        if soup.title:
            title = soup.title.get_text(strip=True)

        leads: list[Lead] = []

        # Create one lead per unique phone or email found
        seen: set[str] = set()
        for phone in phones:
            if phone not in seen:
                seen.add(phone)
                leads.append(self._make_lead(
                    business_name=title,
                    name=title,
                    phone=phone,
                    category=category,
                    location=location,
                    source_url=url,
                ))

        for email in emails:
            if email not in seen:
                seen.add(email)
                leads.append(self._make_lead(
                    business_name=title,
                    name=title,
                    email=email,
                    category=category,
                    location=location,
                    source_url=url,
                ))

        return leads
