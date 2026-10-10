import os

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# In Docker Compose, DATABASE_URL is injected via environment.
# Locally, it can be set in a .env file or exported in the shell.
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://orders:orders@localhost:5432/orders",
)

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

# Shared base for all domain models.
# Every domain imports this Base so a single metadata object
# tracks all tables — important for Base.metadata.create_all().
Base = declarative_base()


def get_db():
    """FastAPI dependency that yields a DB session per request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
