import os
from app.logging_config import backend_logger as logger
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.secrets_loader import get_secret


# --- Global Engine ---
_engine = None

async def get_database_url() -> str:
    """
    Constructs the database URL, logging its source.
    For production, the URL should be fetched from the secrets_loader.
    """
    database_url = os.getenv("DATABASE_URL")
    if database_url:
        logger.warning("Fetched 'database_url' from environment variable. For production, use secrets_loader.")
        return database_url

async def get_engine():
    """Returns the singleton async engine, creating it if necessary."""
    global _engine
    if _engine is None:
        DATABASE_URL = await get_database_url()
        logger.info("Creating new SQLAlchemy async engine.")
        # pool_pre_ping=True helps prevent connection errors on long-lived applications
        _engine = create_async_engine(DATABASE_URL, pool_pre_ping=True)
    return _engine

# --- Session Management ---
# Create a sessionmaker factory that will be used to create sessions.
AsyncSessionFactory = sessionmaker(
    class_=AsyncSession,
    expire_on_commit=False,
)

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency that provides a SQLAlchemy AsyncSession with automatic
    transaction management.
    - Commits the transaction if the request is successful.
    - Rolls back the transaction if an exception occurs.
    - Always closes the session.
    """
    engine = await get_engine()
    AsyncSessionFactory.configure(bind=engine)
    async with AsyncSessionFactory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()