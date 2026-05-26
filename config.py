import os
from dotenv import load_dotenv

load_dotenv()

def _require(key: str) -> str:
    val = os.getenv(key)
    if not val:
        raise ValueError(f"Missing required environment variable: {key}")
    return val

SENDER_EMAIL = _require("SENDER_EMAIL")
SENDER_APP_PASSWORD = _require("SENDER_APP_PASSWORD")
RECIPIENT_EMAILS = [e.strip() for e in _require("RECIPIENT_EMAILS").split(",")]
GEMINI_API_KEY = _require("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
LOCAL_TIMEZONE = os.getenv("LOCAL_TIMEZONE", "Asia/Dhaka")

TOP_N = 10
ARTICLES_PER_SOURCE = 15

NEWS_SOURCES = [
    {
        "name": "Al Jazeera",
        "rss_url": "https://www.aljazeera.com/xml/rss/all.xml",
        "site_url": "https://www.aljazeera.com/",
        "enabled": True,
    },
    {
        "name": "Daily Star",
        "rss_url": "https://www.thedailystar.net/frontpage/rss.xml",
        "rss_url_alt": "https://www.thedailystar.net/rss.xml",
        "site_url": "https://www.thedailystar.net/",
        "enabled": True,
    },
    # To add a 3rd source, copy a block here and set enabled=True
]
