import re
import time
import random

# --- Regex patterns ---

PHONE_PATTERN = re.compile(
    r"""(?:\+?1[-.\s]?)?          # optional country code
        (?:\(?\d{3}\)?[-.\s]?)    # area code
        \d{3}[-.\s]?\d{4}        # number
    """,
    re.VERBOSE,
)

EMAIL_PATTERN = re.compile(
    r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",
)


def extract_phones(text: str) -> list[str]:
    raw = PHONE_PATTERN.findall(text)
    cleaned = []
    for p in raw:
        digits = re.sub(r"\D", "", p)
        if len(digits) == 10:
            cleaned.append(f"({digits[:3]}) {digits[3:6]}-{digits[6:]}")
        elif len(digits) == 11 and digits[0] == "1":
            d = digits[1:]
            cleaned.append(f"({d[:3]}) {d[3:6]}-{d[6:]}")
    return list(dict.fromkeys(cleaned))  # dedupe preserving order


def extract_emails(text: str) -> list[str]:
    found = EMAIL_PATTERN.findall(text)
    # Filter out common false positives
    skip = {"example.com", "domain.com", "email.com", "test.com", "sentry.io"}
    return list(dict.fromkeys(
        e.lower() for e in found if not any(e.lower().endswith(f"@{s}") for s in skip)
    ))


class RateLimiter:
    """Simple rate limiter with random jitter."""

    def __init__(self, min_delay: float = 2.0, max_delay: float = 5.0):
        self.min_delay = min_delay
        self.max_delay = max_delay
        self._last_call = 0.0

    def wait(self):
        elapsed = time.time() - self._last_call
        delay = random.uniform(self.min_delay, self.max_delay)
        if elapsed < delay:
            time.sleep(delay - elapsed)
        self._last_call = time.time()


BROWSER_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}
