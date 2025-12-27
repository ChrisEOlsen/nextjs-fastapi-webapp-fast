from fastapi import APIRouter
from app.api.v1.endpoints import users
from app.api.v1.endpoints import hello

api_router = APIRouter()
api_router.include_router(hello.router)
api_router.include_router(users.router)

api_router.include_router(todo_items.router, prefix='/todo_items', tags=['TodoItem'])
api_router.include_router(todo_items.router, prefix='/todo_items', tags=['TodoItem'])