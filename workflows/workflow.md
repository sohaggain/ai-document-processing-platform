# n8n Automation Workflow

## Purpose
Once a document is fully processed and passes the confidence threshold, the API POSTs a signed JSON payload to an n8n webhook. n8n then continues the business process — this keeps "what happens after extraction" configurable per deployment without changing application code.

## Trigger
- **Type**: Webhook (POST)
- **Path**: matches `N8N_WEBHOOK_URL` in `.env`
- **Payload**:
```json
{
  "document_id": "b3f1...",
  "filename": "invoice_2026_01.pdf",
  "document_type": "invoice",
  "confidence": 0.91,
  "extracted_data": { "...": "..." }
}
```
- **Headers**: `X-Signature` — HMAC-SHA256 of the raw request body using `WEBHOOK_SIGNING_SECRET`. The n8n workflow's first node should verify this before acting on the payload.

## Recommended Node Flow
```text
Webhook Trigger
  ↓
Verify HMAC Signature (Function node) -- reject if invalid
  ↓
Switch on document_type
  ├─ invoice  → HTTP Request to accounting/CRM system → Slack notification
  ├─ contract → Create review task in Asana/Jira → Slack notification
  ├─ resume   → Create candidate record in ATS/CRM → Slack notification
  └─ form     → Write row to Google Sheets / Notion database
  ↓
Error Trigger (workflow-level) → Slack alert to #ops-alerts on any node failure
```

## Error Handling
- Signature verification failure → workflow stops immediately, no downstream action, optionally logs to a dead-letter Notion/Sheet
- Downstream system (CRM/ATS/etc.) failure → n8n's built-in retry-on-fail (configurable per node) with a final Slack alert if retries are exhausted
- The API's own webhook call has its own independent retry/failure logging (see `processing_logs`) — a downstream n8n failure does not affect the already-persisted document record

## Credentials
n8n credentials (Slack token, CRM API key, etc.) are configured directly in the n8n instance's credential store, never passed through this API or committed to this repository.
