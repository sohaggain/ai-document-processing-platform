# Database Schema

## ER Diagram
```mermaid
erDiagram
    DOCUMENTS ||--o{ EXTRACTION_RESULTS : has
    DOCUMENTS ||--o{ PROCESSING_LOGS : has

    DOCUMENTS {
        string id PK
        string filename
        string content_hash UK
        string file_path
        string mime_type
        enum document_type
        enum status
        float classification_confidence
        datetime created_at
        datetime updated_at
    }

    EXTRACTION_RESULTS {
        string id PK
        string document_id FK
        json extracted_data
        text raw_llm_output
        float confidence
        bool is_valid
        json validation_errors
        datetime created_at
    }

    PROCESSING_LOGS {
        int id PK
        string document_id FK
        string stage
        string status
        text message
        int latency_ms
        json token_usage
        datetime created_at
    }
```

## Notes
- `documents.content_hash` has a unique index — this is what makes upload idempotent (a duplicate upload returns the existing record instead of creating a new one).
- `extraction_results` keeps `raw_llm_output` alongside the validated `extracted_data` specifically so a `needs_review` record can be inspected by a human without re-calling the LLM.
- `processing_logs` is append-only and gives a full audit trail per document; it is the primary tool for debugging a stuck pipeline.
- No hard delete cascade beyond `documents` → its children (`cascade="all, delete-orphan"`), since a document without its extraction/log history has little value.
