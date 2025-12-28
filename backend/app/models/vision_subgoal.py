from sqlalchemy import Column, Integer, Text, String, Boolean, Float, Date, DateTime, Uuid
from sqlalchemy.orm import relationship
from sqlalchemy.sql.schema import ForeignKey
from app.db.base_class import Base

class VisionSubgoal(Base):
    __tablename__ = "vision_subgoals"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    is_completed = Column(Boolean, nullable=False)

    vision_goal_id = Column(Integer, ForeignKey("vision_goals.id"), nullable=False)
    vision_goal = relationship("VisionGoal", back_populates="subgoals")
    