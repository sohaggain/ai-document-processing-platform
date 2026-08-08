# Detailed Processing Workflow

## State Machine
```text
received
  → extracting_text
      → failed (no text extracted / OCR error)
      → classifying
          → needs_review (classified as "unknown")
          → extracting_fields
              → failed (LLM transport error, unsupported type)
              → completed (confidence >= threshold)
              → needs_review (confidence < threshold)
```

## Notes on Each Transition
- **received → extracting_text**: happens immediately after the document row is created; no LLM calls yet.
- **extracting_text → failed**: only when *no* text at all could be extracted (both native and OCR paths exhausted or errored).
- **classifying → needs_review**: the model explicitly returned `unknown`, or classification confidence combined with extraction completeness later falls below threshold.
- **extracting_fields → completed**: the extraction result passed Pydantic validation *and* scored at or above `CONFIDENCE_THRESHOLD`.
- **completed → n8n trigger**: happens after commit, in a try/except that cannot roll back the already-completed document if the webhook call fails.

`reprocess` resets a document to `received` and re-runs the entire pipeline from the top — useful after fixing an OCR/Tesseract install issue or after a transient LLM outage.
