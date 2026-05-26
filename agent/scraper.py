import logging
import re
import feedparser
import requests
from bs4 import BeautifulSoup
import config

logger = logging.getLogger(__name__)


def _strip_html(text: str) -> str:
    return re.sub(r"<[^>]+>", "", text or "").strip()


def _fetch_og_image(url: str) -> str:
    """Fetch the og:image URL from an article page. Returns empty string on failure."""
    if not url:
        return ""
    try:
        resp = requests.get(url, timeout=5, headers={
            "User-Agent": "Mozilla/5.0 (compatible; NewsBot/1.0)"
        })
        if resp.status_code != 200:
            return ""
        soup = BeautifulSoup(resp.text, "html.parser")
        og = soup.find("meta", property="og:image") or soup.find("meta", attrs={"name": "twitter:image"})
        if og and og.get("content"):
            return og["content"].strip()
    except Exception:
        pass
    return ""


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

            entries = feed.entries[: config.ARTICLES_PER_SOURCE]

            # Build base article dicts first
            articles = []
            for entry in entries:
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
                        "image_url": "",  # filled below
                    }
                )

            # Fetch og:image for all articles in parallel
            if articles:
                from concurrent.futures import ThreadPoolExecutor, as_completed
                article_urls = [a["url"] for a in articles]
                with ThreadPoolExecutor(max_workers=8) as pool:
                    futures = {pool.submit(_fetch_og_image, u): i for i, u in enumerate(article_urls)}
                    for future in as_completed(futures):
                        idx = futures[future]
                        try:
                            articles[idx]["image_url"] = future.result()
                        except Exception:
                            pass
                logger.info(f"RSS OK — {source['name']}: {len(articles)} articles from {url}")
                imgs = sum(1 for a in articles if a["image_url"])
                logger.info(f"  Images found: {imgs}/{len(articles)}")
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
