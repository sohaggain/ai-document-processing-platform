# Security

## Authentication
All state-changing and read endpoints (except `/health`) require an `X-API-Key` header, checked with a constant-time comparison (`hmac.compare_digest`) to avoid timing attacks. This is a single shared key suitable for service-to-service use (e.g. n8n or an internal upload UI) — see [Future Improvements](../README.md#future-improvements) for multi-tenant auth.

## Webhook Security
Outbound payloads to n8n are signed with HMAC-SHA256 (`WEBHOOK_SIGNING_SECRET`) via an `X-Signature` header, so the receiving n8n workflow can verify the payload actually came from this service and wasn't tampered with in transit.

## Input Validation
- File extension allow-list (`ALLOWED_FILE_TYPES`), enforced before any processing
- File size cap (`MAX_UPLOAD_SIZE_MB`), enforced before OCR/LLM calls to avoid resource exhaustion
- All LLM output re-validated through Pydantic before it is trusted (see [AI Architecture](ai-architecture.md))

## Prompt Injection
Document content is the primary untrusted input to the LLM. Every extraction/classification prompt explicitly instructs the model to treat document text as data, not instructions, and the model's only affordance is producing schema-constrained JSON — it has no tool-calling ability that could be hijacked.

## Secrets Management
- No secrets are committed to the repository; `.env` is gitignored, `.env.example` documents required variables with empty/placeholder values
- API keys and the webhook signing secret are read from environment variables only, never logged

## Data Privacy / PII
Uploaded documents (invoices, resumes, contracts) frequently contain PII. Current version:
- Files are stored on local/attached disk under `STORAGE_PATH`, not shared publicly
- No PII redaction or retention policy is implemented yet — deployments handling real PII should add a retention/deletion policy and consider encryption at rest (see Future Improvements)

## Rate Limiting
Not implemented at the application layer in this version — recommended to add at the reverse proxy/API gateway layer in production (e.g. via a WAF or API gateway rate-limit rule).
