from app.db.base import CRUDBase
from app.models.vision_subgoal import VisionSubgoal
from app.db.schemas.vision_subgoal import VisionSubgoalCreate, VisionSubgoalUpdate

# Create a CRUD object for the VisionSubgoal model,
# inheriting all the basic CRUD methods from the CRUDBase.
crud_vision_subgoal = CRUDBase[VisionSubgoal, VisionSubgoalCreate, VisionSubgoalUpdate](VisionSubgoal)