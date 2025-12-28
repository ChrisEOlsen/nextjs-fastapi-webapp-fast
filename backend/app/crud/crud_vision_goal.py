from app.db.base import CRUDBase
from app.models.vision_goal import VisionGoal
from app.db.schemas.vision_goal import VisionGoalCreate, VisionGoalUpdate

# Create a CRUD object for the VisionGoal model,
# inheriting all the basic CRUD methods from the CRUDBase.
crud_vision_goal = CRUDBase[VisionGoal, VisionGoalCreate, VisionGoalUpdate](VisionGoal)