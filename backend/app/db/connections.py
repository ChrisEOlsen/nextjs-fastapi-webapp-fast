import os
from app.logging_config import backend_logger as logger
from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import text
from app.secrets_loader import get_secret
from fastapi import HTTPException



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

@asynccontextmanager
async def get_session(schema_name: str):
    """
    Provides a transactional SQLAlchemy AsyncSession with the correct schema search_path.
    This is the main entry point for database sessions in the application.
    It automatically handles commit on success and rollback on failure.
    """
    engine = await get_engine()
    session = AsyncSessionFactory(bind=engine)
    try:
        # Begin a transaction. This is the core of the "Unit of Work" pattern.
        async with session.begin():
            # Set the search_path for this specific transaction
            safe_schema_name = f'"{schema_name}"'
            await session.execute(text(f"SET search_path TO {safe_schema_name}"))
            logger.debug(f"Session acquired with search_path set to {safe_schema_name}")
            # Yield the session to the 'with' block in the calling code (e.g., middleware, router)
            yield session
        # The 'async with session.begin()' block handles the commit automatically upon successful exit.
    except HTTPException as http_exc:
        # Re-raise HTTPException without logging it as a session error.
        # FastAPI will handle the response and logging.
        raise http_exc
    except Exception as e:
        logger.error(f"Session error in schema '{schema_name}': {e}", exc_info=True)
        # The 'async with session.begin()' context manager automatically handles rollback on error.
        raise
    finally:
        # Close the session to return its connection to the engine's connection pool.
        await session.close()
        logger.debug("Session closed and connection returned to the pool.")