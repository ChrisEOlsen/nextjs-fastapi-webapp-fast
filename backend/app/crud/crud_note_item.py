from app.db.base import CRUDBase
from app.models.note_item import NoteItem
from app.db.schemas.note_item import NoteItemCreate, NoteItemUpdate

# Create a CRUD object for the NoteItem model,
# inheriting all the basic CRUD methods from the CRUDBase.
crud_note_item = CRUDBase[NoteItem, NoteItemCreate, NoteItemUpdate](NoteItem)