import calendar
import logging
import re
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

import feedparser
import requests
from bs4 import BeautifulSoup
import config

logger = logging.getLogger(__name__)


def _news_window() -> tuple[datetime, datetime]:
    """Return (start, end) UTC datetimes for the current brief's news window.

    Morning brief  → [yesterday 09:00, today 09:00)  (fixed 24-hour window)
    Night brief    → [today 09:00, now)               (captures the day's new articles)

    Both windows are expressed in LOCAL_TIMEZONE then converted to UTC.
    """
    tz = ZoneInfo(config.LOCAL_TIMEZONE)
    now = datetime.now(tz)
    morning_anchor = now.replace(
        hour=config.NEWS_WINDOW_START_HOUR, minute=0, second=0, microsecond=0
    )
    if config.brief_type() == "morning":
        start_local = morning_anchor - timedelta(days=1)
        end_local = morning_anchor
    else:
        start_local = morning_anchor
        end_local = now
    return start_local.astimezone(timezone.utc), end_local.astimezone(timezone.utc)


def _entry_datetime(entry) -> datetime | None:
    """Parse an RSS entry's publish time into an aware UTC datetime, or None."""
    parsed = entry.get("published_parsed") or entry.get("updated_parsed")
    if not parsed:
        return None
    try:
        return datetime.fromtimestamp(calendar.timegm(parsed), tz=timezone.utc)
    except (ValueError, OverflowError, TypeError):
        return None


def _strip_html(text: str) -> str:
    return re.sub(r"<[^>]+>", "", text or "").strip()


def _title_tokens(title: str) -> set[str]:
    """Significant words of a headline, for cross-source duplicate detection."""
    words = re.sub(r"[^a-z0-9 ]", " ", (title or "").lower()).split()
    return {w for w in words if len(w) > 2}


def _dedupe_cross_source(articles: list[dict]) -> list[dict]:
    """Drop articles whose headline closely matches one already kept.

    Different outlets often run the same wire story. We keep the first
    occurrence (earlier sources in config.NEWS_SOURCES win) and discard
    later near-duplicates. Two headlines are treated as the same story when
    they share enough significant words (Jaccard >= 0.6 and >= 3 shared words).
    """
    kept: list[dict] = []
    kept_tokens: list[set[str]] = []
    dropped = 0

    for art in articles:
        tokens = _title_tokens(art["title"])
        is_dup = False
        for other in kept_tokens:
            shared = tokens & other
            union = tokens | other
            if not union:
                continue
            if len(shared) >= 3 and len(shared) / len(union) >= 0.6:
                is_dup = True
                break
        if is_dup:
            dropped += 1
            continue
        kept.append(art)
        kept_tokens.append(tokens)

    if dropped:
        logger.info(f"Cross-source dedupe: dropped {dropped} duplicate stories")
    return kept


_URL_DATE_RE = re.compile(r"/(20\d\d)/(\d{1,2})/(\d{1,2})/")


def _article_datetime(article, url: str) -> datetime | None:
    """Best-effort publish time for an HTML-scraped article, as aware UTC.

    Tries newspaper's parsed ``publish_date`` first, then a ``/YYYY/M/D/`` path
    in the URL. Returns None when no date can be determined — callers should
    treat undated HTML articles as unsafe (they may be stale homepage links).
    """
    pub = getattr(article, "publish_date", None)
    if pub is not None:
        try:
            if pub.tzinfo is None:
                pub = pub.replace(tzinfo=timezone.utc)
            return pub.astimezone(timezone.utc)
        except (ValueError, OverflowError, AttributeError):
            pass

    m = _URL_DATE_RE.search(url or "")
    if m:
        try:
            y, mo, d = (int(g) for g in m.groups())
            return datetime(y, mo, d, tzinfo=timezone.utc)
        except (ValueError, OverflowError):
            pass

    return None


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


def _fetch_rss(source: dict, window: tuple[datetime, datetime]) -> list[dict]:
    urls = source.get("rss_urls") or [source["rss_url"]]
    if source.get("rss_url_alt"):
        urls = urls + [source["rss_url_alt"]]

    start, end = window
    suffix = source.get("strip_suffix")
    articles: list[dict] = []
    seen_urls: set[str] = set()
    stale_count = 0
    undated_count = 0

    url_filter = source.get("url_filter", "")

    for url in urls:
        try:
            feed = feedparser.parse(url, agent="Mozilla/5.0 (compatible; NewsBot/1.0)")
            if feed.bozo and not feed.entries:
                logger.warning(f"RSS unparseable for {source['name']} ({url})")
                continue

            for entry in feed.entries:
                title = _strip_html(entry.get("title", "")).strip()
                if suffix and title.endswith(suffix):
                    title = title[: -len(suffix)].strip()
                link = entry.get("link", "")
                if not title or not link or link in seen_urls:
                    continue
                if url_filter and url_filter not in link:
                    continue

                published = _entry_datetime(entry)
                if published is None:
                    undated_count += 1
                    continue
                if not (start <= published < end):
                    stale_count += 1
                    continue

                seen_urls.add(link)
                summary = _strip_html(entry.get("summary") or entry.get("description") or "")
                articles.append(
                    {
                        "title": title,
                        "summary": summary[:300],
                        "url": link,
                        "source_name": source["name"],
                        "published": published,
                        "image_url": "",  # filled below
                    }
                )
        except Exception as e:
            logger.warning(f"RSS failed for {source['name']} ({url}): {e}")

    # Newest first, then cap per source
    articles.sort(key=lambda a: a["published"], reverse=True)
    articles = articles[: config.ARTICLES_PER_SOURCE]

    logger.info(
        f"RSS — {source['name']}: {len(articles)} in-window articles "
        f"(dropped {stale_count} out-of-window, {undated_count} undated)"
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
        imgs = sum(1 for a in articles if a["image_url"])
        logger.info(f"  Images found: {imgs}/{len(articles)}")

    return articles


def _fetch_html(source: dict, window: tuple[datetime, datetime]) -> list[dict]:
    start, end = window
    try:
        import newspaper

        paper = newspaper.build(
            source["site_url"],
            memoize_articles=False,
            fetch_images=False,
            number_threads=4,
        )
        articles = []
        seen_urls: set[str] = set()
        stale_count = 0
        undated_count = 0
        # Scan more than we need — many will be dropped as undated/out-of-window.
        for article in paper.articles[: config.ARTICLES_PER_SOURCE * 4]:
            if len(articles) >= config.ARTICLES_PER_SOURCE:
                break
            try:
                if article.url in seen_urls:
                    continue
                article.download()
                article.parse()
                if not article.title:
                    continue

                published = _article_datetime(article, article.url)
                if published is None:
                    undated_count += 1
                    continue
                if not (start <= published < end):
                    stale_count += 1
                    continue

                seen_urls.add(article.url)
                articles.append(
                    {
                        "title": article.title.strip(),
                        "summary": (article.text or "")[:300],
                        "url": article.url,
                        "source_name": source["name"],
                        "published": published,
                        "image_url": "",
                    }
                )
            except Exception:
                continue

        logger.info(
            f"HTML fallback — {source['name']}: {len(articles)} in-window articles "
            f"(dropped {stale_count} out-of-window, {undated_count} undated)"
        )

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
            imgs = sum(1 for a in articles if a["image_url"])
            logger.info(f"  Images found: {imgs}/{len(articles)}")

        return articles

    except Exception as e:
        logger.error(f"HTML fallback failed for {source['name']}: {e}")
        return []


def fetch_all_articles() -> list[dict]:
    window = _news_window()
    tz = ZoneInfo(config.LOCAL_TIMEZONE)
    logger.info(
        "News window (local): "
        f"{window[0].astimezone(tz):%Y-%m-%d %H:%M} → "
        f"{window[1].astimezone(tz):%Y-%m-%d %H:%M} {config.LOCAL_TIMEZONE}"
    )

    all_articles = []
    for source in config.NEWS_SOURCES:
        if not source.get("enabled"):
            continue

        articles = _fetch_rss(source, window)
        if not articles:
            logger.warning(f"No in-window RSS articles for {source['name']}, trying HTML fallback")
            articles = _fetch_html(source, window)

        all_articles.extend(articles)

    logger.info(f"Total articles collected: {len(all_articles)}")
    all_articles = _dedupe_cross_source(all_articles)
    logger.info(f"After cross-source dedupe: {len(all_articles)} articles")
    return all_articles
