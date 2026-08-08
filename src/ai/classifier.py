"""Document type classification via LLM."""
from pathlib import Path

from src.ai.client import call_structured
from src.schemas import ClassificationResult

_PROMPT_PATH = Path(__file__).resolve().parent.parent.parent / "prompts" / "classification_prompt.txt"
_SYSTEM_PROMPT = _PROMPT_PATH.read_text()

MAX_TEXT_CHARS = 6000  # keep classification cheap; full text used later for extraction


def classify_document(text: str) -> ClassificationResult:
    """
    Classifies extracted text into a document type.
    Raises LLMCallError on transport/parse failure, ValidationError on
    schema mismatch — both are caught by the caller (document_service)
    and routed to needs_review/failed rather than silently defaulting.
    """
    truncated = text[:MAX_TEXT_CHARS]
    raw = call_structured(system_prompt=_SYSTEM_PROMPT, user_prompt=truncated, max_tokens=300)
    return ClassificationResult.model_validate(raw)
