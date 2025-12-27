from fastapi import APIRouter
from app.api.v1.endpoints import users
from app.api.v1.endpoints import messages

api_router = APIRouter()
api_router.include_router(users.router)
api_router.include_router(messages.router)
