# API Documentation

All endpoints except `/health` require an `X-API-Key` header matching the `API_KEY` environment variable. Interactive docs are also available at `/docs` (Swagger) and `/redoc`.

## `GET /health`
- **Auth**: none
- **Response 200**: `{"status": "ok"}`

## `POST /documents/upload`
- **Auth**: required
- **Body**: `multipart/form-data`, field `file` (pdf/png/jpg/jpeg, max `MAX_UPLOAD_SIZE_MB`)
- **Response 202**:
```json
{
  "document_id": "b3f1...",
  "filename": "invoice_2026_01.pdf",
  "status": "completed",
  "message": "Document received and processed."
}
```
- **Duplicate upload**: same content hash returns the existing record's current status instead of reprocessing (idempotent).
- **Error responses**:
  - `400` unsupported file type
  - `401` missing/invalid API key
  - `413` file exceeds `MAX_UPLOAD_SIZE_MB`

## `GET /documents/{document_id}`
- **Auth**: required
- **Response 200**:
```json
{
  "id": "b3f1...",
  "filename": "invoice_2026_01.pdf",
  "document_type": "invoice",
  "status": "completed",
  "classification_confidence": 0.94,
  "created_at": "2026-08-08T10:00:00"
}
```
- **Error**: `404` if not found

## `GET /documents/{document_id}/extraction`
- **Auth**: required
- **Response 200**:
```json
{
  "id": "e91a...",
  "document_id": "b3f1...",
  "document_type": "invoice",
  "extracted_data": { "invoice_number": "INV-1001", "total_amount": 540.00, "...": "..." },
  "confidence": 0.88,
  "is_valid": true,
  "validation_errors": null
}
```
- **Error**: `404` if no document or no extraction result exists yet

## `POST /documents/{document_id}/reprocess`
- **Auth**: required
- Re-runs the full pipeline for an existing document (useful after a transient failure). Same response shape as upload.
