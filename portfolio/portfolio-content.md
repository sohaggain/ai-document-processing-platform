# Portfolio Content — sohaggain.com

## Project Title
AI Document Processing Platform

## One-line description
An AI pipeline that turns invoices, contracts, resumes, and forms into validated structured data and routes it into business workflows via n8n.

## Problem
Teams manually re-key data from invoices, contracts, resumes, and intake forms into spreadsheets and business systems — slow, inconsistent, and impossible to audit.

## Solution
A FastAPI service that ingests documents (PDF/image), extracts text (native + OCR fallback), classifies the document type with Claude, extracts a type-specific structured schema, validates it with Pydantic and a confidence threshold, persists it to PostgreSQL, and triggers an n8n workflow for downstream routing — with a fail-closed `needs_review` path for anything the system isn't confident about.

## Key Features
- Multi-document-type classification and extraction (invoice, contract, resume, form)
- OCR fallback for scanned documents
- Confidence-gated, fail-closed validation
- Full audit log per document
- n8n webhook integration with HMAC-signed payloads
- Idempotent uploads via content hashing

## Tech Stack
Python, FastAPI, PostgreSQL, SQLAlchemy, Pydantic, Anthropic Claude, pdfplumber, Tesseract OCR, n8n, Docker, GitHub Actions

## Architecture Summary
Upload → text extraction (native/OCR) → LLM classification → LLM structured extraction → Pydantic validation + confidence scoring → PostgreSQL → n8n webhook → downstream business systems.

## Business Value
Designed to reduce manual document-processing effort and provide a consistent, auditable extraction pipeline that plugs into existing tools (CRM, ATS, accounting, Slack) instead of requiring a rebuild of those systems.

## GitHub
https://github.com/sohaggain/ai-document-processing-platform (TODO: update after publishing)

## Live Demo
Not publicly deployed yet.

## Demo Video
To be added after implementation.

## Project Category
AI Automation / Business Automation / Document Intelligence

## Difficulty
Flagship

## Skills Demonstrated
AI-assisted structured extraction, prompt injection-aware prompt design, fail-closed system design, OCR pipelines, REST API design, PostgreSQL schema design, webhook security (HMAC), Docker/CI, automated testing.
