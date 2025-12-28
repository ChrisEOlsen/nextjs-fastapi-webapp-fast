from pydantic import BaseModel, field_validator
from typing import Optional
from datetime import datetime

# Pydantic model for creating a new VisionGoal
class VisionGoalCreate(BaseModel):
    title: str
    description: Optional[str] = None
    deadline: Optional[datetime] = None
    status: Optional[str] = None

    @field_validator('deadline')
    @classmethod
    def remove_timezone(cls, v):
        if v and v.tzinfo:
            return v.replace(tzinfo=None)
        return v

# Pydantic model for updating a VisionGoal
# All fields are optional for partial updates
class VisionGoalUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    deadline: Optional[datetime] = None
    status: Optional[str] = None

    @field_validator('deadline')
    @classmethod
    def remove_timezone(cls, v):
        if v and v.tzinfo:
            return v.replace(tzinfo=None)
        return v

# Pydantic model for reading/returning a VisionGoal
# This is the base model that includes fields present in the database
class VisionGoal(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    deadline: Optional[datetime] = None
    status: Optional[str] = None

    class Config:
        from_attributes = True