"""
Triggers the downstream n8n workflow once a document has been fully
processed and validated. This module only ever sends already-validated,
structured data — never raw LLM output or unvalidated fields.
"""
import json
import logging

import httpx

from src.config import get_settings
from src.models import Document, ExtractionResult
from src.security import sign_payload

logger = logging.getLogger(__name__)
settings = get_settings()


def trigger_workflow(document: Document, result: ExtractionResult) -> None:
    if not settings.n8n_webhook_enabled or not settings.n8n_webhook_url:
        logger.info("n8n webhook disabled or not configured; skipping trigger")
        return

    payload = {
        "document_id": document.id,
        "filename": document.filename,
        "document_type": document.document_type.value,
        "confidence": result.confidence,
        "extracted_data": result.extracted_data,
    }
    body = json.dumps(payload).encode()
    signature = sign_payload(body)

    with httpx.Client(timeout=10.0) as client:
        response = client.post(
            settings.n8n_webhook_url,
            content=body,
            headers={"Content-Type": "application/json", "X-Signature": signature},
        )
        response.raise_for_status()
