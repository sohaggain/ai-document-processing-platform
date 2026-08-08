# Interview Preparation

## Project-Specific Questions

**1. Why did you build a single pipeline for four document types instead of four separate services?**
The pipeline stages (extract text → classify → extract fields → validate → persist → trigger) are identical across document types; only the classification outcome and the extraction schema/prompt differ. A single service with a type-keyed schema registry (`EXTRACTION_SCHEMAS`) avoids duplicating the same orchestration logic four times.

**2. How does the system handle a document that doesn't match any known type?**
Classification includes an explicit `unknown` category. If the model returns `unknown`, or the confidence is below threshold, the document is marked `needs_review` and never reaches the extraction stage — there's no attempt to force it into one of the four schemas.

**3. Why store `raw_llm_output` alongside the validated `extracted_data`?**
So a human reviewing a `needs_review` record can see exactly what the model produced without re-running the LLM call, which matters both for debugging and for building a future evaluation dataset.

**4. What happens if the same document is uploaded twice?**
The SHA-256 hash of the file content is unique-indexed in the database. A duplicate upload returns the existing record's current status instead of reprocessing — this makes the upload endpoint safe to retry from a flaky client.

**5. Why is OCR only used as a fallback, not always?**
Native PDF text extraction (pdfplumber) is fast, free, and more accurate than OCR for digitally-created PDFs. OCR only runs when native extraction yields too little text, keeping both cost and latency down for the common case.

**6. How would a client add a new document type, e.g. purchase orders?**
Add a Pydantic schema to `EXTRACTION_SCHEMAS`, add a classification category, and add an extraction prompt file — the orchestration in `document_service.py` doesn't change.

**7. What's stored in `processing_logs` and why?**
One row per pipeline stage per document (text_extraction, classification, extraction, n8n_trigger, etc.) with status, message, and latency. It's the primary tool for answering "why is this document stuck / what happened to it" without reproducing the run.

**8. Why does the extraction schema allow every field to be null?**
Real documents are messy — not every invoice has a due date, not every resume lists years of experience explicitly. Requiring fields would force the model to fabricate values to satisfy validation, which is worse than an honest null.

**9. How is the classification confidence combined with extraction quality into one number?**
`score_extraction()` blends classification confidence (40%) with schema completeness — fraction of non-null top-level fields (60%). It's a simple, inspectable heuristic rather than a second LLM grading its own work.

**10. What would you change before handling real client PII at scale?**
Add encryption at rest for `storage/uploads`, a data retention/deletion policy, and likely move file storage to S3 with server-side encryption rather than local disk.

## Architecture Questions

**11. Why FastAPI + SQLAlchemy instead of a framework like Django?**
The service is a narrow API surface with no admin UI or templating needs — FastAPI's async support and native Pydantic integration fit a validation-heavy pipeline better with less overhead.

**12. Why is the LLM client isolated in its own module?**
So a provider swap (Anthropic → OpenAI, or adding a second provider) only touches `src/ai/client.py`'s `call_structured()` implementation — classifier and extractor logic depend only on that function's contract, not on any SDK specifics.

**13. Why does `document_service.py` own all the side effects instead of the API layer?**
Keeping orchestration in a service module (not the route handler) makes the pipeline testable and reusable — e.g. the `reprocess` endpoint calls the exact same `process_document()` function as the initial upload.

**14. How would you scale this to handle thousands of uploads per hour?**
Move processing off the request/response cycle into a background task queue (Celery/RQ/Arq) so `POST /upload` returns immediately after storage + hashing, with a worker pool consuming the queue. The current synchronous-in-request design was a deliberate simplicity trade-off for the current scope.

**15. Why PostgreSQL over a NoSQL store for extracted data?**
The schema (documents → extraction_results → processing_logs) is naturally relational, and PostgreSQL's `JSON` column type still lets `extracted_data` stay flexible per document type without needing a fully schemaless database.

## AI/Automation Questions

**16. How do you prevent the LLM from executing instructions hidden in a document?**
Every prompt explicitly frames document text as untrusted data, not instructions, and the model's only affordance is producing schema-constrained JSON — it has no tool-calling or action capability that injected text could hijack.

**17. What happens if the LLM returns malformed JSON?**
`call_structured()` raises `LLMCallError` on `json.loads` failure — no partial-JSON recovery is attempted. The pipeline catches this and marks the document `failed`, logging the raw text for debugging.

**18. Why not just trust a high-confidence LLM classification without the completeness check?**
A model can be confident about the document type while still missing most of the actual field values (e.g., a low-quality scan). Blending confidence with completeness catches that case that classification confidence alone would miss.

**19. Why n8n instead of hardcoding CRM/Slack integrations into the API?**
n8n keeps "what happens after a document is processed" configurable per deployment/client without redeploying the core service — a new client can rewire the downstream workflow without touching Python code.

**20. How would you evaluate extraction accuracy over time?**
Build a labeled sample set per document type and diff expected vs. extracted fields per run — not implemented in this version, listed explicitly under Future Improvements rather than left implicit.

## Security Questions

**21. How is the API protected from unauthorized use?**
A shared `X-API-Key` header, checked with `hmac.compare_digest` for constant-time comparison, required on every endpoint except `/health`.

**22. How do you know a webhook payload from your API actually reached n8n unmodified?**
Every outbound payload is signed with HMAC-SHA256 using `WEBHOOK_SIGNING_SECRET`; the n8n workflow's first node verifies the `X-Signature` header before acting on the payload.

**23. What stops someone from uploading an oversized file to exhaust resources?**
`MAX_UPLOAD_SIZE_MB` is enforced immediately after reading the upload, before OCR or any LLM call — an oversized file never reaches the expensive parts of the pipeline.

**24. Are there SQL injection risks given raw document text is processed?**
No — all database access goes through SQLAlchemy's ORM/parameterized queries; document text is only ever passed to the LLM as prompt content, never interpolated into SQL.

**25. How are secrets kept out of the codebase?**
All credentials come from environment variables (`.env`, gitignored); `.env.example` documents required variables with empty placeholders, and nothing is logged at the secret level.

## Failure / Scalability Questions

**26. What happens if the n8n webhook is unreachable?**
The failure is caught, logged to `processing_logs` as a `n8n_trigger` failure, and does not roll back or block the document record, which is already `completed` and valid at that point.

**27. What happens if the database is temporarily unavailable during processing?**
Currently an unhandled exception surfaces as a 500 — this is a known gap; a production deployment should add connection retry/backoff at the SQLAlchemy engine level.

**28. How would you handle a burst of 500 uploads at once?**
Move to the background-queue architecture described in Q14; the synchronous design in this version is appropriate for the current scope but not for high-concurrency bursts.

**29. What's the failure mode if Tesseract isn't installed on the host?**
`extract_text()` raises `ExtractionError`, caught by `process_document()`, which marks the document `failed` and logs the specific error — never a silent empty-text pass-through.

**30. How do you avoid double-charging LLM costs if a request is retried?**
The content-hash dedup check happens before any LLM call — a duplicate upload never reaches classification or extraction, so retried uploads of the same file don't incur duplicate LLM cost.
