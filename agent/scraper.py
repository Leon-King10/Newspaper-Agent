import logging
import re
import feedparser
import config

logger = logging.getLogger(__name__)


def _strip_html(text: str) -> str:
    return re.sub(r"<[^>]+>", "", text or "").strip()


def _fetch_rss(source: dict) -> list[dict]:
    urls = [source["rss_url"]]
    if "rss_url_alt" in source:
        urls.append(source["rss_url_alt"])

    for url in urls:
        try:
            feed = feedparser.parse(url)
            if feed.bozo and not feed.entries:
                continue
            if len(feed.entries) < 5:
                continue

            articles = []
            for entry in feed.entries[: config.ARTICLES_PER_SOURCE]:
                title = _strip_html(entry.get("title", "")).strip()
                summary = _strip_html(entry.get("summary") or entry.get("description") or "")
                if not title:
                    continue
                articles.append(
                    {
                        "title": title,
                        "summary": summary[:300],
                        "url": entry.get("link", ""),
                        "source_name": source["name"],
                    }
                )

            if articles:
                logger.info(f"RSS OK — {source['name']}: {len(articles)} articles from {url}")
                return articles

        except Exception as e:
            logger.warning(f"RSS failed for {source['name']} ({url}): {e}")

    return []


def _fetch_html(source: dict) -> list[dict]:
    try:
        import newspaper

        paper = newspaper.build(
            source["site_url"],
            memoize_articles=False,
            fetch_images=False,
            number_threads=4,
        )
        articles = []
        for article in paper.articles[: config.ARTICLES_PER_SOURCE]:
            try:
                article.download()
                article.parse()
                if not article.title:
                    continue
                articles.append(
                    {
                        "title": article.title.strip(),
                        "summary": (article.text or "")[:300],
                        "url": article.url,
                        "source_name": source["name"],
                    }
                )
            except Exception:
                continue

        logger.info(f"HTML fallback — {source['name']}: {len(articles)} articles")
        return articles

    except Exception as e:
        logger.error(f"HTML fallback failed for {source['name']}: {e}")
        return []


def fetch_all_articles() -> list[dict]:
    all_articles = []
    for source in config.NEWS_SOURCES:
        if not source.get("enabled"):
            continue

        articles = _fetch_rss(source)
        if not articles:
            logger.warning(f"RSS returned nothing for {source['name']}, trying HTML fallback")
            articles = _fetch_html(source)

        all_articles.extend(articles)

    logger.info(f"Total articles collected: {len(all_articles)}")
    return all_articles
