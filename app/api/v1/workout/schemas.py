from typing import Optional,List
from pydantic import BaseModel, ConfigDict
from datetime import datetime


class WorkoutList(BaseModel):
    workout_name: str
    workout_description: Optional[str] = None
    primary_muscle: str
    secondary_muscle: Optional[str] = None
    met: Optional[float] = None
    workout_id: int
    workout_created_at: Optional[datetime] = None
    workout_updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
