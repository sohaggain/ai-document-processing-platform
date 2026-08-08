"""HTTP endpoints for the document processing platform."""
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from src.config import get_settings
from src.database import get_db
from src.models import Document, DocumentStatus, ExtractionResult
from src.schemas import DocumentResponse, ExtractionResponse, UploadResponse
from src.security import verify_api_key
from src.services.document_service import (
    compute_hash,
    create_document,
    find_existing_by_hash,
    process_document,
    save_upload,
)

router = APIRouter()
settings = get_settings()

_MIME_MAP = {
    ".pdf": "application/pdf",
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
}


@router.get("/health")
def health_check():
    return {"status": "ok"}


@router.post("/documents/upload", response_model=UploadResponse, status_code=status.HTTP_202_ACCEPTED)
async def upload_document(
    file: UploadFile,
    db: Session = Depends(get_db),
    _: None = Depends(verify_api_key),
):
    ext = Path(file.filename).suffix.lower().lstrip(".")
    if ext not in settings.allowed_extensions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file type '.{ext}'. Allowed: {settings.allowed_extensions}",
        )

    content = await file.read()
    size_mb = len(content) / (1024 * 1024)
    if size_mb > settings.max_upload_size_mb:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File exceeds max size of {settings.max_upload_size_mb}MB",
        )

    content_hash = compute_hash(content)
    existing = find_existing_by_hash(db, content_hash)
    if existing:
        return UploadResponse(
            document_id=existing.id,
            filename=existing.filename,
            status=existing.status.value,
            message="Duplicate upload detected; returning existing document (idempotent).",
        )

    file_path = save_upload(content, file.filename, _MIME_MAP.get(f".{ext}", "application/octet-stream"))
    document = create_document(
        db=db,
        filename=file.filename,
        file_path=file_path,
        mime_type=_MIME_MAP.get(f".{ext}", "application/octet-stream"),
        content_hash=content_hash,
    )

    process_document(db, document)
    db.refresh(document)

    return UploadResponse(
        document_id=document.id,
        filename=document.filename,
        status=document.status.value,
        message="Document received and processed.",
    )


@router.get("/documents/{document_id}", response_model=DocumentResponse)
def get_document(document_id: str, db: Session = Depends(get_db), _: None = Depends(verify_api_key)):
    doc = db.get(Document, document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return DocumentResponse(
        id=doc.id,
        filename=doc.filename,
        document_type=doc.document_type.value,
        status=doc.status.value,
        classification_confidence=doc.classification_confidence,
        created_at=doc.created_at.isoformat(),
    )


@router.get("/documents/{document_id}/extraction", response_model=ExtractionResponse)
def get_extraction(document_id: str, db: Session = Depends(get_db), _: None = Depends(verify_api_key)):
    doc = db.get(Document, document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    result = (
        db.query(ExtractionResult)
        .filter(ExtractionResult.document_id == document_id)
        .order_by(ExtractionResult.created_at.desc())
        .first()
    )
    if not result:
        raise HTTPException(status_code=404, detail="No extraction result available for this document")
    return ExtractionResponse(
        id=result.id,
        document_id=document_id,
        document_type=doc.document_type.value,
        extracted_data=result.extracted_data,
        confidence=result.confidence,
        is_valid=result.is_valid,
        validation_errors=result.validation_errors,
    )


@router.post("/documents/{document_id}/reprocess", response_model=UploadResponse)
def reprocess_document(document_id: str, db: Session = Depends(get_db), _: None = Depends(verify_api_key)):
    doc = db.get(Document, document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    doc.status = DocumentStatus.RECEIVED
    db.commit()
    process_document(db, doc)
    db.refresh(doc)
    return UploadResponse(
        document_id=doc.id,
        filename=doc.filename,
        status=doc.status.value,
        message="Document reprocessed.",
    )
