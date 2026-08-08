# Setup Guide

## Prerequisites
- Python 3.11+
- PostgreSQL 15+ (or Docker)
- Tesseract OCR + Poppler (`apt install tesseract-ocr poppler-utils` on Debian/Ubuntu)
- An Anthropic API key
- (Optional) an n8n instance with a webhook trigger node

## Local Setup
```bash
git clone https://github.com/sohaggain/ai-document-processing-platform.git
cd ai-document-processing-platform
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# edit .env: set ANTHROPIC_API_KEY, API_KEY, WEBHOOK_SIGNING_SECRET, DATABASE_URL
python scripts/init_db.py
uvicorn src.main:app --reload
```

Visit `http://localhost:8000/docs` for interactive Swagger UI.

## Docker Setup
```bash
cp .env.example .env
docker compose -f docker/docker-compose.yml up --build
```

## Verifying the Install
```bash
curl http://localhost:8000/health
# {"status": "ok"}

curl -X POST http://localhost:8000/documents/upload \
  -H "X-API-Key: <your API_KEY>" \
  -F "file=@sample_invoice.pdf"
```
