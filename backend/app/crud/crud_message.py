from app.db.base import CRUDBase
from app.models.message import Message
from app.db.schemas.message import MessageCreate, MessageUpdate

# Create a CRUD object for the Message model
crud_message = CRUDBase[Message, MessageCreate, MessageUpdate](Message)