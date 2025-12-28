from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.crud.crud_vision_subgoal import crud_vision_subgoal
from app.db.schemas.vision_subgoal import VisionSubgoal, VisionSubgoalCreate, VisionSubgoalUpdate
from app.db.connections import get_db

router = APIRouter()

@router.get("/vision_subgoals/", response_model=List[VisionSubgoal])
async def read_vision_subgoals(
    db: AsyncSession = Depends(get_db), skip: int = 0, limit: int = 100
):
    """
    Retrieve vision_subgoals.
    """
    items = await crud_vision_subgoal.get_multi(db, skip=skip, limit=limit)
    return items

@router.post("/vision_subgoals/", response_model=VisionSubgoal)
async def create_vision_subgoal(
    *,
    db: AsyncSession = Depends(get_db),
    item_in: VisionSubgoalCreate,
):
    """
    Create new vision_subgoal.
    """
    item = await crud_vision_subgoal.create(db=db, obj_in=item_in)
    return item

@router.put("/vision_subgoals/{item_id}", response_model=VisionSubgoal)
async def update_vision_subgoal(
    *,
    db: AsyncSession = Depends(get_db),
    item_id: int,
    item_in: VisionSubgoalUpdate,
):
    """
    Update a vision_subgoal.
    """
    item = await crud_vision_subgoal.get(db=db, id=item_id)
    if not item:
        raise HTTPException(status_code=404, detail="VisionSubgoal not found")
    item = await crud_vision_subgoal.update(db=db, db_obj=item, obj_in=item_in)
    return item

@router.delete("/vision_subgoals/{item_id}", response_model=VisionSubgoal)
async def delete_vision_subgoal(
    *,
    db: AsyncSession = Depends(get_db),
    item_id: int,
):
    """
    Delete a vision_subgoal.
    """
    item = await crud_vision_subgoal.delete(db=db, id=item_id)
    if not item:
        raise HTTPException(status_code=404, detail="VisionSubgoal not found")
    return item