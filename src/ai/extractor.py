"""Type-specific structured extraction via LLM."""
from pathlib import Path

from pydantic import BaseModel

from src.ai.client import call_structured
from src.schemas import EXTRACTION_SCHEMAS

_PROMPTS_DIR = Path(__file__).resolve().parent.parent.parent / "prompts"

_PROMPT_FILES = {
    "invoice": "invoice_extraction_prompt.txt",
    "contract": "contract_extraction_prompt.txt",
    "resume": "resume_extraction_prompt.txt",
    "form": "form_extraction_prompt.txt",
}

MAX_TEXT_CHARS = 12000


class UnsupportedDocumentTypeError(Exception):
    pass


def extract_fields(document_type: str, text: str) -> tuple[BaseModel, dict]:
    """
    Runs extraction for the given document type and validates the LLM
    output against the matching Pydantic schema.

    Returns (validated_model, raw_dict). Raises UnsupportedDocumentTypeError
    for 'unknown'/unsupported types, LLMCallError on transport/parse
    failure, and pydantic.ValidationError on schema mismatch — all handled
    upstream by validation_service.
    """
    if document_type not in _PROMPT_FILES:
        raise UnsupportedDocumentTypeError(f"No extraction schema for type: {document_type}")

    prompt_path = _PROMPTS_DIR / _PROMPT_FILES[document_type]
    system_prompt = prompt_path.read_text()

    truncated = text[:MAX_TEXT_CHARS]
    raw = call_structured(system_prompt=system_prompt, user_prompt=truncated, max_tokens=2000)

    schema_cls = EXTRACTION_SCHEMAS[document_type]
    validated = schema_cls.model_validate(raw)
    return validated, raw
