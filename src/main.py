"""FastAPI application entrypoint."""
import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.api.routes import router
from src.config import get_settings
from src.database import Base, engine

settings = get_settings()

logging.basicConfig(level=settings.log_level)


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncGenerator[None, None]:
    # Convenience for local dev; production deployments should manage
    # schema migrations explicitly (see scripts/init_db.py / Alembic note in docs).
    if settings.app_env == "development":
        Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="AI Document Processing Platform",
    description="Upload -> OCR -> AI classification/extraction -> validation -> database -> n8n workflow",
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(router)
