# from difflib import restore
# from turtle import distance
from typing import Optional,List
from pydantic import BaseModel, ConfigDict
from datetime import datetime
from sqlalchemy import Float


class WorkoutListGet(BaseModel):
    workout_id: int
    workout_name: str
    workout_description: Optional[str] = None
    primary_muscle: Optional[list] = None
    secondary_muscle: Optional[list] = None
    met: Optional[float] = None
    workout_created_at: Optional[datetime] = None
    workout_updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

class WorkoutLogListGet(BaseModel):
    workout_name: Optional[str] = None
    workout_log_id: Optional[int] = None
    user_name: str
    primary_muscle: Optional[str] = None
    secondary_muscle: Optional[str] = None
    tut: Optional[int] = None
    rest: Optional[int] = None
    weight: Optional[float] = None
    sets: Optional[int] = None
    rpe: Optional[float] = None
    distance: Optional[float] = None
    workout_type: Optional[str] = None
    is_super_set: Optional[bool] = None
    is_drop_set: Optional[bool] = None
    is_giant_set: Optional[bool] = None
    is_warmup: Optional[bool] = None
    is_finisher: Optional[bool] = None
    is_failure: Optional[bool] = None
    workout_created_at: Optional[datetime] = None
    workout_updated_at: Optional[datetime] = None

class WorkoutLogListPost(BaseModel):
    workout_name: str
    user_name: str
    tut: Optional[int] = None
    rest: Optional[int] = None
    weight: Optional[float] = None
    sets: Optional[int] = None
    rpe: Optional[float] = None
    distance: Optional[float] = None
    workout_type: Optional[str] = None
    is_super_set: Optional[bool] = None
    is_drop_set: Optional[bool] = None
    is_giant_set: Optional[bool] = None
    is_warmup: Optional[bool] = None
    is_finisher: Optional[bool] = None
    is_failure: Optional[bool] = None

    model_config = ConfigDict(from_attributes=True)

class WorkoutLogListPatch(BaseModel):
    workout_name: str = None
    user_name: str
    tut: Optional[int] = None
    rest: Optional[int] = None
    weight: Optional[float] = None
    sets: Optional[int] = None
    rpe: Optional[float] = None
    distance: Optional[int] = None
    workout_type: Optional[str] = None
    is_super_set: Optional[bool] = None
    is_drop_set: Optional[bool] = None
    is_giant_set: Optional[bool] = None
    is_warmup: Optional[bool] = None
    is_finisher: Optional[bool] = None
    is_failure: Optional[bool] = None

model_config = ConfigDict(from_attributes=True)
