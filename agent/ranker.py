import json
import logging
import re
from google import genai
import config

logger = logging.getLogger(__name__)

_client = genai.Client(api_key=config.GEMINI_API_KEY)

_RANKING_PROMPT = """You are a news editor. From the numbered list below, select the {top_n} most important stories.

Pick based on: significance, impact, recency, and reader interest.

Return ONLY a JSON array of item numbers in order of importance (most important first).
Example: [3, 0, 4, 1, 2]

ARTICLES:
{articles_block}

Return only the JSON array. No explanation."""


def _build_articles_block(articles: list[dict]) -> str:
    lines = []
    for i, a in enumerate(articles):
        snippet = a.get("summary", "")[:120].replace("\n", " ")
        line = f"{i}. {a['title']}"
        if snippet:
            line += f" — {snippet}"
        lines.append(line)
    return "\n".join(lines)


def _parse_ranked_indices(raw: str, max_index: int) -> list[int]:
    match = re.search(r"\[[\d,\s]+\]", raw)
    if not match:
        return []
    try:
        indices = json.loads(match.group())
        return [i for i in indices if isinstance(i, int) and 0 <= i <= max_index]
    except (json.JSONDecodeError, TypeError):
        return []


def _rank_group(articles: list[dict], top_n: int) -> list[dict]:
    """Rank a group of articles with Gemini and return the top_n."""
    if not articles:
        return []
    if len(articles) <= top_n:
        return articles

    articles_block = _build_articles_block(articles)
    prompt = _RANKING_PROMPT.format(top_n=top_n, articles_block=articles_block)

    try:
        response = _client.models.generate_content(
            model=config.GEMINI_MODEL,
            contents=prompt,
        )
        raw = response.text.strip()
        logger.debug(f"Gemini response: {raw}")
        indices = _parse_ranked_indices(raw, max_index=len(articles) - 1)
        if indices:
            ranked = [articles[i] for i in indices if i < len(articles)]
            logger.info(f"Gemini ranked {len(ranked)} articles from {articles[0].get('source_name', '?')}")
            return ranked[:top_n]
    except Exception as e:
        logger.error(f"Gemini ranking failed: {e} — using first {top_n}")

    return articles[:top_n]


def rank_articles(articles: list[dict]) -> list[dict]:
    # Group articles by source
    by_source: dict[str, list[dict]] = {}
    for a in articles:
        src = a.get("source_name", "Unknown")
        by_source.setdefault(src, []).append(a)

    sources = list(by_source.keys())
    n_sources = len(sources)

    if n_sources == 0:
        return []

    # Equal slots per source (floor division, then give extras to first sources)
    slots_per_source = config.TOP_N // n_sources
    extra = config.TOP_N % n_sources

    logger.info(f"Ranking {n_sources} sources equally — {slots_per_source} slots each (±{extra} extra)")

    result = []
    for idx, source in enumerate(sources):
        group = by_source[source]
        slots = slots_per_source + (1 if idx < extra else 0)
        ranked = _rank_group(group, slots)
        logger.info(f"  {source}: picked {len(ranked)}/{len(group)} articles")
        result.extend(ranked)

    logger.info(f"Ranking complete: {len(result)} total articles across {n_sources} sources")
    return result
