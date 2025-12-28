from pydantic import BaseModel
from typing import Optional

# Pydantic model for creating a new VisionSubgoal
class VisionSubgoalCreate(BaseModel):
    title: str
    is_completed: bool
    vision_goal_id: int

# Pydantic model for updating a VisionSubgoal
# All fields are optional for partial updates
class VisionSubgoalUpdate(BaseModel):
    title: Optional[str] = None
    is_completed: Optional[bool] = None
    vision_goal_id: Optional[int] = None

# Pydantic model for reading/returning a VisionSubgoal
# This is the base model that includes fields present in the database
class VisionSubgoal(BaseModel):
    id: int
    title: str
    is_completed: bool
    vision_goal_id: int

    class Config:
        from_attributes = True