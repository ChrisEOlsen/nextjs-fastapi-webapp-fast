from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.crud.crud_vision_goal import crud_vision_goal
from app.db.schemas.vision_goal import VisionGoal, VisionGoalCreate, VisionGoalUpdate
from app.db.connections import get_db

router = APIRouter()

@router.get("/vision_goals/", response_model=List[VisionGoal])
async def read_vision_goals(
    db: AsyncSession = Depends(get_db), skip: int = 0, limit: int = 100
):
    """
    Retrieve vision_goals.
    """
    items = await crud_vision_goal.get_multi(db, skip=skip, limit=limit)
    return items

@router.post("/vision_goals/", response_model=VisionGoal)
async def create_vision_goal(
    *,
    db: AsyncSession = Depends(get_db),
    item_in: VisionGoalCreate,
):
    """
    Create new vision_goal.
    """
    item = await crud_vision_goal.create(db=db, obj_in=item_in)
    return item

@router.put("/vision_goals/{item_id}", response_model=VisionGoal)
async def update_vision_goal(
    *,
    db: AsyncSession = Depends(get_db),
    item_id: int,
    item_in: VisionGoalUpdate,
):
    """
    Update a vision_goal.
    """
    item = await crud_vision_goal.get(db=db, id=item_id)
    if not item:
        raise HTTPException(status_code=404, detail="VisionGoal not found")
    item = await crud_vision_goal.update(db=db, db_obj=item, obj_in=item_in)
    return item

@router.delete("/vision_goals/{item_id}", response_model=VisionGoal)
async def delete_vision_goal(
    *,
    db: AsyncSession = Depends(get_db),
    item_id: int,
):
    """
    Delete a vision_goal.
    """
    item = await crud_vision_goal.delete(db=db, id=item_id)
    if not item:
        raise HTTPException(status_code=404, detail="VisionGoal not found")
    return item