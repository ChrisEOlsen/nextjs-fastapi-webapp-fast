from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.crud.crud_note_item import crud_note_item
from app.db.schemas.note_item import NoteItem, NoteItemCreate, NoteItemUpdate
from app.db.connections import get_db

router = APIRouter()

@router.get("/note_items/", response_model=List[NoteItem])
async def read_note_items(
    db: AsyncSession = Depends(get_db), skip: int = 0, limit: int = 100
):
    """
    Retrieve note_items.
    """
    items = await crud_note_item.get_multi(db, skip=skip, limit=limit)
    return items

@router.post("/note_items/", response_model=NoteItem)
async def create_note_item(
    *,
    db: AsyncSession = Depends(get_db),
    item_in: NoteItemCreate,
):
    """
    Create new note_item.
    """
    item = await crud_note_item.create(db=db, obj_in=item_in)
    return item

@router.put("/note_items/{item_id}", response_model=NoteItem)
async def update_note_item(
    *,
    db: AsyncSession = Depends(get_db),
    item_id: int,
    item_in: NoteItemUpdate,
):
    """
    Update a note_item.
    """
    item = await crud_note_item.get(db=db, id=item_id)
    if not item:
        raise HTTPException(status_code=404, detail="NoteItem not found")
    item = await crud_note_item.update(db=db, db_obj=item, obj_in=item_in)
    return item

@router.delete("/note_items/{item_id}", response_model=NoteItem)
async def delete_note_item(
    *,
    db: AsyncSession = Depends(get_db),
    item_id: int,
):
    """
    Delete a note_item.
    """
    item = await crud_note_item.delete(db=db, id=item_id)
    if not item:
        raise HTTPException(status_code=404, detail="NoteItem not found")
    return item