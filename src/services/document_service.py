"""
Orchestrates the full document processing pipeline. This is the only
place that sequences OCR -> classify -> extract -> validate -> persist ->
trigger workflow. All side effects (DB writes, webhook calls) happen here
against already-validated, structured data — never against raw LLM output.
"""
import hashlib
import logging
import time
from pathlib import Path

from sqlalchemy.orm import Session

from src.ai.classifier import classify_document
from src.ai.client import LLMCallError
from src.ai.extractor import UnsupportedDocumentTypeError, extract_fields
from src.config import get_settings
from src.models import Document, DocumentStatus, DocumentType, ExtractionResult, ProcessingLog
from src.ocr.extractor import ExtractionError, extract_text
from src.services.validation_service import is_valid, score_extraction
from src.workflow.n8n_client import trigger_workflow

logger = logging.getLogger(__name__)
settings = get_settings()


def compute_hash(file_bytes: bytes) -> str:
    return hashlib.sha256(file_bytes).hexdigest()


def _log(db: Session, document_id: str, stage: str, status: str, message: str = "", latency_ms: int | None = None):
    db.add(ProcessingLog(document_id=document_id, stage=stage, status=status, message=message, latency_ms=latency_ms))
    db.commit()


def find_existing_by_hash(db: Session, content_hash: str) -> Document | None:
    return db.query(Document).filter(Document.content_hash == content_hash).first()


def create_document(db: Session, filename: str, file_path: str, mime_type: str, content_hash: str) -> Document:
    doc = Document(filename=filename, file_path=file_path, mime_type=mime_type, content_hash=content_hash)
    db.add(doc)
    db.commit()
    db.refresh(doc)
    return doc


def process_document(db: Session, document: Document) -> Document:
    """
    Runs the full pipeline for a single document. Idempotent from the
    caller's perspective: safe to call again on a failed document to retry.
    """
    try:
        # --- Text extraction ---
        document.status = DocumentStatus.EXTRACTING_TEXT
        db.commit()
        t0 = time.time()
        text = extract_text(document.file_path, document.mime_type)
        _log(db, document.id, "text_extraction", "success", latency_ms=int((time.time() - t0) * 1000))

        if not text.strip():
            document.status = DocumentStatus.FAILED
            db.commit()
            _log(db, document.id, "text_extraction", "failed", "No text could be extracted")
            return document

        # --- Classification ---
        document.status = DocumentStatus.CLASSIFYING
        db.commit()
        t0 = time.time()
        classification = classify_document(text)
        document.document_type = DocumentType(classification.document_type)
        document.classification_confidence = classification.confidence
        db.commit()
        _log(db, document.id, "classification", "success", classification.reasoning, int((time.time() - t0) * 1000))

        if classification.document_type == "unknown":
            document.status = DocumentStatus.NEEDS_REVIEW
            db.commit()
            _log(db, document.id, "classification", "needs_review", "Document type could not be determined")
            return document

        # --- Extraction ---
        document.status = DocumentStatus.EXTRACTING_FIELDS
        db.commit()
        t0 = time.time()
        model, raw = extract_fields(classification.document_type, text)
        confidence = score_extraction(model, classification.confidence)
        valid = is_valid(confidence, settings.confidence_threshold)

        result = ExtractionResult(
            document_id=document.id,
            extracted_data=model.model_dump(),
            raw_llm_output=str(raw),
            confidence=confidence,
            is_valid=valid,
        )
        db.add(result)
        _log(db, document.id, "extraction", "success", latency_ms=int((time.time() - t0) * 1000))

        document.status = DocumentStatus.COMPLETED if valid else DocumentStatus.NEEDS_REVIEW
        db.commit()

        if valid:
            # Workflow trigger failure must never roll back or block the
            # already-persisted, already-validated document record.
            try:
                trigger_workflow(document, result)
                _log(db, document.id, "n8n_trigger", "success")
            except Exception as exc:  # noqa: BLE001
                logger.warning("n8n webhook trigger failed for %s: %s", document.id, exc)
                _log(db, document.id, "n8n_trigger", "failed", str(exc))

        return document

    except (ExtractionError, LLMCallError, UnsupportedDocumentTypeError) as exc:
        document.status = DocumentStatus.FAILED
        db.commit()
        _log(db, document.id, "pipeline", "failed", str(exc))
        return document
    except Exception as exc:  # noqa: BLE001
        # Unexpected error: fail closed, never leave the record in a
        # half-processed state without a log entry explaining why.
        logger.exception("Unexpected pipeline error for document %s", document.id)
        document.status = DocumentStatus.FAILED
        db.commit()
        _log(db, document.id, "pipeline", "failed", f"Unexpected error: {exc}")
        return document


def save_upload(content: bytes, filename: str, mime_type: str) -> str:
    storage_dir = Path(settings.storage_path)
    storage_dir.mkdir(parents=True, exist_ok=True)
    content_hash = compute_hash(content)
    ext = Path(filename).suffix
    dest = storage_dir / f"{content_hash}{ext}"
    if not dest.exists():
        dest.write_bytes(content)
    return str(dest)
