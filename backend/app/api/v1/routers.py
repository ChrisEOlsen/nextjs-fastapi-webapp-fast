from app.api.v1.endpoints import vision_subgoals
from app.api.v1.endpoints import vision_goals
from app.api.v1.endpoints import todo_lists
from app.api.v1.endpoints import todo_items
from fastapi import APIRouter
from app.api.v1.endpoints import messages

api_router = APIRouter()
api_router.include_router(messages.router)

api_router.include_router(todo_items.router)
api_router.include_router(todo_lists.router)
api_router.include_router(vision_goals.router)
api_router.include_router(vision_subgoals.router)