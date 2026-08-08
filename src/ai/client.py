"""
Thin wrapper around the Anthropic client.

Keeping this isolated means:
- Only this module needs credentials/config for the LLM provider.
- Swapping providers (e.g. to OpenAI) means implementing this same
  interface elsewhere, not touching classifier/extractor logic.
- Retry/backoff policy lives in one place.
"""
import json
import logging

from anthropic import Anthropic
from tenacity import retry, stop_after_attempt, wait_exponential

from src.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

_client: Anthropic | None = None


def get_client() -> Anthropic:
    global _client
    if _client is None:
        _client = Anthropic(api_key=settings.anthropic_api_key)
    return _client


class LLMCallError(Exception):
    pass


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=8), reraise=True)
def call_structured(system_prompt: str, user_prompt: str, max_tokens: int = 1500) -> dict:
    """
    Calls Claude with a system prompt instructing strict JSON-only output.
    Returns the parsed dict. Raises LLMCallError if the response cannot be
    parsed as JSON — callers must treat that as an untrusted/failed result,
    never guess at partial data.
    """
    client = get_client()
    try:
        response = client.messages.create(
            model=settings.anthropic_model,
            max_tokens=max_tokens,
            system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}],
        )
    except Exception as exc:  # noqa: BLE001
        logger.error("LLM call failed: %s", exc)
        raise LLMCallError(str(exc)) from exc

    text_blocks = [block.text for block in response.content if block.type == "text"]
    raw_text = "".join(text_blocks).strip()

    cleaned = raw_text.removeprefix("```json").removeprefix("```").removesuffix("```").strip()

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError as exc:
        logger.error("LLM returned non-JSON output: %s", raw_text[:500])
        raise LLMCallError(f"Invalid JSON from LLM: {exc}") from exc
