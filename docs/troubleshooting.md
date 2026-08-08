# Troubleshooting

**"401 Unauthorized" on every request**
Check the `X-API-Key` header matches `API_KEY` in your `.env` exactly (no quotes, no trailing whitespace).

**Document stuck in `extracting_text` / OCR errors**
Confirm Tesseract is installed and `TESSERACT_CMD` points to the correct binary path (`which tesseract`). If using Docker, this is handled automatically by the provided `Dockerfile`.

**Document lands in `needs_review` for every upload**
Check `processing_logs` for that document — likely either classification confidence is low (poor scan quality, unusual document layout) or the extraction schema completeness is low. Inspect `extraction_results.raw_llm_output` to see exactly what the model returned.

**"Invalid JSON from LLM" errors**
The model occasionally wraps output in markdown fences or adds commentary despite instructions. The client already strips common fence patterns; if this persists, check `ANTHROPIC_MODEL` is a valid, current model string and consider lowering `max_tokens` truncation risk.

**n8n webhook never fires**
Confirm `N8N_WEBHOOK_ENABLED=true` and `N8N_WEBHOOK_URL` is reachable from the API container/host. Check `processing_logs` for a `n8n_trigger` stage entry — webhook failures are logged but never block or roll back the document record.

**Duplicate uploads not detected**
Dedup is by exact file content hash (SHA-256). A re-scanned or re-exported version of "the same" document will have a different hash and is treated as new — this is by design, not a bug.
