from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.crud_user import user as crud_user
from app.db import connections
from app.db.schemas.user import User, UserCreate

router = APIRouter()
