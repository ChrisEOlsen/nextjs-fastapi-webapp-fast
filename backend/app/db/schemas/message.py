from pydantic import BaseModel
from typing import Optional

# Schema for creating a new message
class MessageCreate(BaseModel):
    content: str

# Schema for updating an existing message
class MessageUpdate(BaseModel):
    content: Optional[str] = None

# Schema for reading/returning a message
class Message(BaseModel):
    id: int
    content: str

    class Config:
        orm_mode = True