from app.logging_config import backend_logger as logger
import os
from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.api.v1.routers import api_router


# Init lifespan of FastAPI application
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🏁 App startup complete, ready to accept requests.")
    yield
    logger.info("🛑 App shutdown complete.")

# Initialize FastAPI app with lifespan management
app = FastAPI(lifespan=lifespan)

# Include all API routers
app.include_router(api_router)