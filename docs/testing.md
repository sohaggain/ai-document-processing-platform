# Testing

## Strategy
| Layer | Tool | What it covers |
|---|---|---|
| Unit | pytest | Pydantic schema validation/coercion, confidence scoring, fail-closed threshold logic, HMAC signature roundtrip/tamper detection |
| Integration | pytest + FastAPI `TestClient` | Auth enforcement on protected endpoints, health check, DB-backed request flow (SQLite in-memory for CI speed) |

LLM calls are never made in tests — `src/ai/client.call_structured` is the natural mock boundary since classifier/extractor logic depends only on its return contract, not on network calls.

## Running Tests
```bash
pytest tests/unit -v
pytest tests/integration -v
pytest --cov=src tests/
ruff check src tests
```

## What Is and Isn't Covered
Covered: schema validation edge cases (partial data, invalid enum values, out-of-range confidence), fail-closed threshold boundaries, signature tampering detection, auth rejection.

Not yet covered (see [Future Improvements](../README.md#future-improvements)): OCR extraction against real scanned documents, full pipeline integration test with a mocked LLM response, n8n webhook delivery/retry behavior.
