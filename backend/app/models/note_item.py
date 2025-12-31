from sqlalchemy import Column, Integer, Text, String, Boolean, Float, Date, DateTime, Uuid
from app.db.base_class import Base

class NoteItem(Base):
    __tablename__ = "note_items"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    content = Column(String)
    is_folder = Column(Boolean, nullable=False)
    parent_id = Column(Integer)
    