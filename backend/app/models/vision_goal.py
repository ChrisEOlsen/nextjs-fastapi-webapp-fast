from sqlalchemy import Column, Integer, Text, String, Boolean, Float, Date, DateTime, Uuid
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class VisionGoal(Base):
    __tablename__ = "vision_goals"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String)
    deadline = Column(DateTime, nullable=True)
    status = Column(String)

    subgoals = relationship("VisionSubgoal", back_populates="vision_goal", cascade="all, delete-orphan")
    