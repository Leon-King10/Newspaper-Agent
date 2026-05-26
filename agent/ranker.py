import json
import logging
import re
from google import genai
import config

logger = logging.getLogger(__name__)

_client = genai.Client(api_key=config.GEMINI_API_KEY)

_RANKING_PROMPT = """You are a senior international news editor. From the numbered list below, select the {top_n} most globally important news items.

Priority order:
1. Humanitarian crises (famine, displacement, civilian casualties, war crimes)
2. Active wars and military conflicts
3. Major political events (elections, coups, assassinations, diplomatic crises)
4. Bangladesh news (any significant domestic event)
5. Global economy, climate disasters, and health emergencies

Return ONLY a JSON array of the item numbers in order of importance (most important first).
Example: [3, 17, 2, 9, 1, 14, 7, 22, 5, 11]

ARTICLES:
{articles_block}

Return only the JSON array. No explanation, no other text."""


def _build_articles_block(articles: list[dict]) -> str:
    lines = []
    for i, a in enumerate(articles):
        snippet = a.get("summary", "")[:120].replace("\n", " ")
        line = f"{i}. [{a['source_name']}] {a['title']}"
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


def rank_articles(articles: list[dict]) -> list[dict]:
    if len(articles) <= config.TOP_N:
        return articles

    articles_block = _build_articles_block(articles)
    prompt = _RANKING_PROMPT.format(top_n=config.TOP_N, articles_block=articles_block)

    try:
        response = _client.models.generate_content(
            model=config.GEMINI_MODEL,
            contents=prompt,
        )
        raw = response.text.strip()
        logger.debug(f"Gemini ranking response: {raw}")

        indices = _parse_ranked_indices(raw, max_index=len(articles) - 1)

        if not indices:
            logger.warning("Gemini ranking parse failed — falling back to first 10 articles")
            return articles[: config.TOP_N]

        ranked = [articles[i] for i in indices if i < len(articles)]
        logger.info(f"Ranking complete: selected {len(ranked)} articles")
        return ranked[: config.TOP_N]

    except Exception as e:
        logger.error(f"Gemini ranking failed: {e} — falling back to first 10 articles")
        return articles[: config.TOP_N]
