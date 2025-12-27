from sqlalchemy import Column, Integer, Text
from app.db.base_class import Base

class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text, nullable=False)
