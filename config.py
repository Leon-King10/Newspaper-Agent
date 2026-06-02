import os
from dotenv import load_dotenv

load_dotenv()

def _require(key: str) -> str:
    val = os.getenv(key)
    if not val:
        raise ValueError(f"Missing required environment variable: {key}")
    return val

def _require_either(key1: str, key2: str) -> str:
    val = os.getenv(key1) or os.getenv(key2)
    if not val:
        raise ValueError(f"Missing required environment variable: {key1} or {key2}")
    return val

SENDER_EMAIL = _require("SENDER_EMAIL")
SENDER_APP_PASSWORD = _require("SENDER_APP_PASSWORD")
RECIPIENT_EMAILS = [e.strip() for e in _require_either("RECIPIENT_EMAILS", "RECIPIENT_EMAIL").split(",")]
GEMINI_API_KEY = _require("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
LOCAL_TIMEZONE = os.getenv("LOCAL_TIMEZONE", "Asia/Dhaka")

TOP_N = 20            # 4 sources × top 5 each
ARTICLES_PER_SOURCE = 15

# Daily window: include news published from this hour yesterday until this hour today
# (e.g. 9 → [yesterday 09:00, today 09:00) in LOCAL_TIMEZONE). Articles outside the
# window — including stale/cached feed entries — are discarded.
NEWS_WINDOW_START_HOUR = 9

NEWS_SOURCES = [
    {
        "name": "Al Jazeera",
        "rss_urls": ["https://www.aljazeera.com/xml/rss/all.xml"],
        "site_url": "https://www.aljazeera.com/",
        "enabled": True,
    },
    {
        "name": "Reuters",
        # Reuters shut down all of its own public RSS feeds. We source Reuters
        # headlines via Google News (scoped to reuters.com), which provides live
        # dates and a thumbnail. Google News appends " - Reuters" to each title.
        "rss_urls": [
            "https://news.google.com/rss/search?q=site:reuters.com+when:2d&hl=en-US&gl=US&ceid=US:en",
        ],
        "site_url": "https://www.reuters.com/",
        "strip_suffix": " - Reuters",
        "enabled": True,
    },
    {
        "name": "Daily Star",
        # NOTE: frontpage/rss.xml is dead (frozen at 2022) — do not use it.
        # These category feeds are live and merged together.
        "rss_urls": [
            "https://www.thedailystar.net/news/bangladesh/rss.xml",
            "https://www.thedailystar.net/business/rss.xml",
            "https://www.thedailystar.net/sports/rss.xml",
            "https://www.thedailystar.net/rss.xml",
        ],
        "site_url": "https://www.thedailystar.net/",
        "enabled": True,
    },
    {
        "name": "Prothom Alo",
        # Bangla feed (~85 entries) — the English feed is too thin (~9) to
        # reliably fill a top 5. Content is in Bengali.
        "rss_urls": ["https://www.prothomalo.com/feed"],
        "site_url": "https://www.prothomalo.com/",
        "enabled": True,
    },
    # To add another source, copy a block here and set enabled=True
]
