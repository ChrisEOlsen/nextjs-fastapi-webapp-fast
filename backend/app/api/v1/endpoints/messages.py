from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.crud.crud_message import crud_message
from app.db.schemas.message import Message, MessageCreate, MessageUpdate
from app.db.connections import get_db

router = APIRouter(prefix="/messages", tags=["Messages"])

@router.get("/", response_model=List[Message])
async def read_messages(
    db: AsyncSession = Depends(get_db), skip: int = 0, limit: int = 100
):
    """
    Retrieve messages.
    """
    messages = await crud_message.get_multi(db, skip=skip, limit=limit)
    return messages

@router.post("/", response_model=Message)
async def create_message(
    *,
    db: AsyncSession = Depends(get_db),
    message_in: MessageCreate,
):
    """
    Create new message.
    """
    message = await crud_message.create(db=db, obj_in=message_in)
    return message

@router.put("/{message_id}", response_model=Message)
async def update_message(
    *,
    db: AsyncSession = Depends(get_db),
    message_id: int,
    message_in: MessageUpdate,
):
    """
    Update a message.
    """
    message = await crud_message.get(db=db, id=message_id)
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")
    message = await crud_message.update(db=db, db_obj=message, obj_in=message_in)
    return message

@router.delete("/{message_id}", response_model=Message)
async def delete_message(
    *,
    db: AsyncSession = Depends(get_db),
    message_id: int,
):
    """
    Delete a message.
    """
    message = await crud_message.delete(db=db, id=message_id)
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")
    return message
