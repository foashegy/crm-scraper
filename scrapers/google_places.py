import json
import requests
from db.models import Lead
from .base import BaseScraper


class GooglePlacesScraper(BaseScraper):
    source_name = "Google Places"

    API_URL = "https://places.googleapis.com/v1/places:searchText"
    FIELD_MASK = "places.displayName,places.formattedAddress,places.nationalPhoneNumber,places.websiteUri,places.id"

    def __init__(self, api_key: str):
        self.api_key = api_key

    def scrape(self, query: str, location: str, category: str = "", **kwargs) -> list[Lead]:
        text_query = f"{query} in {location}" if location else query
        leads: list[Lead] = []
        page_token = None

        for _ in range(3):  # max 3 pages = 60 results
            body = {"textQuery": text_query, "pageSize": 20}
            if page_token:
                body["pageToken"] = page_token

            headers = {
                "Content-Type": "application/json",
                "X-Goog-Api-Key": self.api_key,
                "X-Goog-FieldMask": self.FIELD_MASK,
            }

            resp = requests.post(self.API_URL, json=body, headers=headers, timeout=15)
            resp.raise_for_status()
            data = resp.json()

            for place in data.get("places", []):
                display = place.get("displayName", {})
                lead = self._make_lead(
                    business_name=display.get("text", ""),
                    name=display.get("text", ""),
                    phone=place.get("nationalPhoneNumber", ""),
                    address=place.get("formattedAddress", ""),
                    website=place.get("websiteUri", ""),
                    google_place_id=place.get("id", ""),
                    category=category,
                    location=location,
                    source_url=f"https://www.google.com/maps/place/?q=place_id:{place.get('id', '')}",
                    raw_data=json.dumps(place),
                )
                leads.append(lead)

            page_token = data.get("nextPageToken")
            if not page_token:
                break

        return leads
