from app.logging_config import backend_logger as logger
import os
from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.middleware import validate_tenant_middleware
from app.api.v1.routers import api_router
from app.db.connections import get_engine
from app.db.base_class import Base


# Init lifespan of FastAPI application
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 Starting application...")
    engine = await get_engine()
    async with engine.begin() as conn:
        logger.info("Creating database tables if they don't exist...")
        await conn.run_sync(Base.metadata.create_all)
        logger.info("Database tables checked/created successfully.")
    logger.info("🏁 App startup complete, ready to accept requests.")
    yield
    logger.info("🛑 App shutdown complete.")

# Initialize FastAPI app with lifespan management
app = FastAPI(lifespan=lifespan)

# Custom middleware to validate users and database schemas 
app.middleware("http")(validate_tenant_middleware)

# Include all API routers
app.include_router(api_router, prefix=os.getenv("API_PREFIX"))