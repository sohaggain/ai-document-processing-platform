# Configuration Notes

This project is configured entirely through environment variables (see `.env.example` at the repo root) via `src/config.py` (Pydantic Settings). There are no separate YAML/JSON config files — this keeps configuration 12-factor-compliant and identical across local, Docker, and CI environments.
