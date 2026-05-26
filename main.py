import logging
import sys

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    stream=sys.stdout,
)
logger = logging.getLogger("newspaper_agent")

# Config import validates all required env vars immediately
import config  # noqa: E402
from agent.scraper import fetch_all_articles
from agent.ranker import rank_articles
from agent.formatter import format_digest
from agent.summarizer import enrich_summaries
from agent.sender import send_email


def run():
    logger.info("=== Newspaper Agent starting ===")

    logger.info("Step 1/4: Fetching articles from news sources...")
    articles = fetch_all_articles()
    if not articles:
        logger.error("No articles fetched — aborting")
        sys.exit(1)
    logger.info(f"Fetched {len(articles)} articles total")

    logger.info("Step 2/4: Ranking articles with Gemini AI...")
    ranked = rank_articles(articles)
    logger.info(f"Selected top {len(ranked)} articles")

    logger.info("Step 3/5: Enriching summaries with Gemini AI...")
    enriched = enrich_summaries(ranked)

    logger.info("Step 4/5: Formatting HTML email...")
    subject, html = format_digest(enriched)
    logger.info(f"Subject: {subject}")

    logger.info(f"Step 5/5: Sending email to {config.RECIPIENT_EMAILS}...")
    success = send_email(subject, html)

    if success:
        logger.info("=== Digest sent successfully ===")
        sys.exit(0)
    else:
        logger.error("=== Failed to send digest ===")
        sys.exit(1)


if __name__ == "__main__":
    run()
