# Resume Entry

## AI Document Processing Platform
Multi-document-type AI extraction platform (invoices, contracts, resumes, forms) with automated business-workflow routing.

- Designed and built a FastAPI pipeline that classifies and extracts structured data from mixed document types using Claude, validated against strict Pydantic schemas before any persistence or downstream action.
- Implemented a fail-closed confidence-scoring system that routes low-confidence extractions to a `needs_review` state instead of writing unverified data, avoiding silent data-quality failures.
- Built OCR fallback (Tesseract + pdfplumber) so the pipeline handles both native-text and scanned PDFs without manual pre-processing.
- Integrated n8n via HMAC-signed webhooks to route completed extractions into downstream CRM/ATS/accounting workflows without coupling the core service to any one business tool.
- Delivered with automated tests (pytest), CI (GitHub Actions), Docker/docker-compose deployment, and full architecture/security/API documentation.
