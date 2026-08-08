"""Creates all tables. Run once against a fresh database (or use Alembic in production)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.database import Base, engine  # noqa: E402
from src import models  # noqa: E402, F401  (ensures models are registered)

if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)
    print("Database tables created.")
