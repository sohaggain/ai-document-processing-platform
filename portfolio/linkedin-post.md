# LinkedIn Project Description

Built an AI Document Processing Platform: an automation pipeline that takes invoices, contracts, resumes, and forms and turns them into validated, structured data — automatically.

The problem: most teams still manually re-key data from PDFs into spreadsheets and business systems. Slow, inconsistent, and hard to audit.

The solution: FastAPI service → OCR/text extraction → Claude classifies and extracts structured fields → every extraction is re-validated against a strict schema and a confidence threshold before it's trusted → PostgreSQL for storage → n8n webhook to route completed records into CRM/ATS/accounting workflows.

Key engineering decision: fail closed. If the system isn't confident in an extraction, it never writes it as verified data — it flags it for human review instead.

Stack: Python, FastAPI, PostgreSQL, Pydantic, Anthropic Claude, Tesseract OCR, n8n, Docker, GitHub Actions.

GitHub: [link] (TODO)
