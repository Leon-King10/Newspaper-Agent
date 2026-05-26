import json
import logging
import re
from google import genai
import config

logger = logging.getLogger(__name__)

_client = genai.Client(api_key=config.GEMINI_API_KEY)

_SUMMARIZE_PROMPT = """You are a professional news summarizer. For each numbered headline below, write exactly 2 clear, informative sentences that explain:
- What happened (the key fact)
- Why it matters or what the context/impact is

Rules:
- Be factual and concise
- Do NOT repeat the headline word-for-word
- Each summary must be 2 sentences, no more, no less
- Return ONLY a JSON object mapping each number (as a string) to its 2-sentence summary

HEADLINES:
{headlines_block}

Return ONLY valid JSON like this:
{{"0": "First sentence. Second sentence.", "1": "First sentence. Second sentence."}}"""


def _build_headlines_block(articles: list[dict]) -> str:
    return "\n".join(
        f"{i}. [{a['source_name']}] {a['title']}"
        for i, a in enumerate(articles)
    )


def _parse_summaries(raw: str, n: int) -> dict[str, str]:
    """Extract JSON mapping from Gemini response."""
    # Try to find the JSON object
    match = re.search(r"\{[\s\S]*\}", raw)
    if not match:
        return {}
    try:
        data = json.loads(match.group())
        # Validate it's a str->str mapping
        return {str(k): str(v) for k, v in data.items() if str(k).isdigit() and int(k) < n}
    except (json.JSONDecodeError, TypeError, AttributeError):
        return {}


def enrich_summaries(articles: list[dict]) -> list[dict]:
    """
    Replace missing/weak article summaries with AI-generated 2-sentence summaries.
    Makes a single batched Gemini call for all articles.
    """
    if not articles:
        return articles

    headlines_block = _build_headlines_block(articles)
    prompt = _SUMMARIZE_PROMPT.format(headlines_block=headlines_block)

    try:
        response = _client.models.generate_content(
            model=config.GEMINI_MODEL,
            contents=prompt,
        )
        raw = response.text.strip()
        logger.debug(f"Gemini summarize response: {raw}")

        summaries = _parse_summaries(raw, len(articles))

        if not summaries:
            logger.warning("Summary parsing failed — keeping original summaries")
            return articles

        enriched = []
        for i, article in enumerate(articles):
            ai_summary = summaries.get(str(i), "").strip()
            if ai_summary:
                article = {**article, "summary": ai_summary}
            enriched.append(article)

        logger.info(f"Summaries enriched for {len(summaries)}/{len(articles)} articles")
        return enriched

    except Exception as e:
        logger.error(f"Summary enrichment failed: {e} — using original summaries")
        return articles
