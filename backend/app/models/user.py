from sqlalchemy import Column, String, Integer
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import Uuid
import uuid

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Uuid, default=uuid.uuid4, unique=True, nullable=False)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
