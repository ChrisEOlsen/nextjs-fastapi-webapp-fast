from pydantic import BaseModel
from typing import Optional

# Pydantic model for creating a new NoteItem
class NoteItemCreate(BaseModel):
    title: str
    content: Optional[str] = None
    is_folder: bool
    parent_id: Optional[int] = None

# Pydantic model for updating a NoteItem
# All fields are optional for partial updates
class NoteItemUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    is_folder: Optional[bool] = None
    parent_id: Optional[int] = None

# Pydantic model for reading/returning a NoteItem
# This is the base model that includes fields present in the database
class NoteItem(BaseModel):
    id: int
    title: str
    content: Optional[str] = None
    is_folder: bool
    parent_id: Optional[int] = None

    class Config:
        from_attributes = True