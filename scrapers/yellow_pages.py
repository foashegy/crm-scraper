import requests
from bs4 import BeautifulSoup
from db.models import Lead
from .base import BaseScraper
from .utils import RateLimiter, BROWSER_HEADERS, extract_emails


class YellowPagesScraper(BaseScraper):
    source_name = "Yellow Pages"

    BASE_URL = "https://www.yellowpages.com/search"

    def __init__(self, max_pages: int = 3):
        self.max_pages = max_pages
        self.rate_limiter = RateLimiter(min_delay=2.0, max_delay=5.0)

    def scrape(self, query: str, location: str, category: str = "", **kwargs) -> list[Lead]:
        leads: list[Lead] = []

        for page in range(1, self.max_pages + 1):
            self.rate_limiter.wait()
            params = {"search_terms": query, "geo_location_terms": location}
            if page > 1:
                params["page"] = page

            try:
                resp = requests.get(
                    self.BASE_URL, params=params,
                    headers=BROWSER_HEADERS, timeout=15,
                )
                if resp.status_code != 200:
                    break
            except requests.RequestException:
                break

            soup = BeautifulSoup(resp.text, "html.parser")
            cards = soup.select("div.result")
            if not cards:
                cards = soup.select("div.v-card")
            if not cards:
                break

            for card in cards:
                biz_name = ""
                name_el = card.select_one("a.business-name") or card.select_one("h2 a")
                if name_el:
                    biz_name = name_el.get_text(strip=True)

                phone = ""
                phone_el = card.select_one("div.phones") or card.select_one("div.phone")
                if phone_el:
                    phone = phone_el.get_text(strip=True)

                address = ""
                addr_el = card.select_one("div.adr") or card.select_one("p.adr") or card.select_one("div.street-address")
                if addr_el:
                    address = addr_el.get_text(" ", strip=True)

                website = ""
                web_el = card.select_one("a.track-visit-website")
                if web_el and web_el.get("href"):
                    website = web_el["href"]

                source_url = ""
                if name_el and name_el.get("href"):
                    href = name_el["href"]
                    source_url = f"https://www.yellowpages.com{href}" if href.startswith("/") else href

                if biz_name or phone:
                    leads.append(self._make_lead(
                        business_name=biz_name,
                        name=biz_name,
                        phone=phone,
                        address=address,
                        website=website,
                        category=category,
                        location=location,
                        source_url=source_url,
                    ))

        return leads
