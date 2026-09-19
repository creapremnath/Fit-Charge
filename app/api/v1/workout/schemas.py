from typing import Optional, List
from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime


# ==========================================
# Exercise & Muscle Schemas
# ==========================================

class MuscleResponse(BaseModel):
    id: int
    name: str

    model_config = ConfigDict(from_attributes=True)


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


# ==========================================
# Workout Template Schemas
# ==========================================

class WorkoutTemplateExerciseCreate(BaseModel):
    workout_id: Optional[int] = None
    exercise_name: str
    sets: Optional[int] = 3
    reps: Optional[int] = 10
    weight: Optional[float] = 0.0
    rest_seconds: Optional[int] = 60
    order_index: Optional[int] = 1
    notes: Optional[str] = None


class WorkoutTemplateExerciseResponse(WorkoutTemplateExerciseCreate):
    id: int
    template_day_id: int

    model_config = ConfigDict(from_attributes=True)


class WorkoutTemplateDayCreate(BaseModel):
    day_name: str # e.g. 'Monday', 'Push Day', 'Day 1'
    day_order: Optional[int] = 1
    is_rest_day: Optional[bool] = False
    exercises: Optional[List[WorkoutTemplateExerciseCreate]] = []


class WorkoutTemplateDayResponse(BaseModel):
    id: int
    template_id: int
    day_name: str
    day_order: int
    is_rest_day: bool
    exercises: List[WorkoutTemplateExerciseResponse] = []

    model_config = ConfigDict(from_attributes=True)


class WorkoutTemplateCreate(BaseModel):
    name: str
    description: Optional[str] = None
    category: Optional[str] = "Hypertrophy"
    difficulty: Optional[str] = "Intermediate"
    is_public: Optional[bool] = False
    days: Optional[List[WorkoutTemplateDayCreate]] = []


class WorkoutTemplateUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    difficulty: Optional[str] = None
    is_public: Optional[bool] = None
    days: Optional[List[WorkoutTemplateDayCreate]] = None


class WorkoutTemplateResponse(BaseModel):
    id: int
    user_id: Optional[int] = None
    name: str
    description: Optional[str] = None
    category: Optional[str] = None
    difficulty: Optional[str] = None
    is_custom: bool
    is_public: bool
    days: List[WorkoutTemplateDayResponse] = []
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


# ==========================================
# Workout Log & Set Schemas
# ==========================================

class WorkoutLogDetailCreate(BaseModel):
    workout_id: Optional[int] = None
    exercise_name: Optional[str] = None
    set_number: Optional[int] = 1
    set_type: Optional[str] = "normal" # 'normal', 'warmup', 'drop_set', 'failure', 'super_set'
    reps: Optional[int] = 10
    weight: Optional[float] = 0.0
    tut: Optional[int] = None
    rest: Optional[int] = None
    rpe: Optional[float] = None
    is_completed: Optional[bool] = True
    detail: Optional[str] = None


class WorkoutLogDetailResponse(WorkoutLogDetailCreate):
    id: int
    workout_log_id: int
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class WorkoutLogCreate(BaseModel):
    workout_id: Optional[int] = None
    template_id: Optional[int] = None
    workout_name: Optional[str] = None
    workout_date: Optional[datetime] = None
    tut: Optional[int] = None
    rest: Optional[int] = None
    rpe: Optional[float] = None
    sets: Optional[int] = None
    reps: Optional[int] = None
    weight: Optional[float] = None
    volume: Optional[float] = None
    distance: Optional[float] = None
    duration_minutes: Optional[int] = None
    notes: Optional[str] = None
    details: Optional[List[WorkoutLogDetailCreate]] = []


class WorkoutLogUpdate(BaseModel):
    workout_id: Optional[int] = None
    template_id: Optional[int] = None
    workout_name: Optional[str] = None
    workout_date: Optional[datetime] = None
    tut: Optional[int] = None
    rest: Optional[int] = None
    rpe: Optional[float] = None
    sets: Optional[int] = None
    reps: Optional[int] = None
    weight: Optional[float] = None
    volume: Optional[float] = None
    distance: Optional[float] = None
    duration_minutes: Optional[int] = None
    notes: Optional[str] = None
    details: Optional[List[WorkoutLogDetailCreate]] = None


class WorkoutLogResponse(BaseModel):
    id: int
    user_id: int
    workout_id: Optional[int] = None
    template_id: Optional[int] = None
    workout_name: Optional[str] = None
    workout_date: Optional[datetime] = None
    tut: Optional[int] = None
    rest: Optional[int] = None
    rpe: Optional[float] = None
    sets: Optional[int] = None
    reps: Optional[int] = None
    weight: Optional[float] = None
    volume: Optional[float] = None
    distance: Optional[float] = None
    duration_minutes: Optional[int] = None
    notes: Optional[str] = None
    details: List[WorkoutLogDetailResponse] = []
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


# Legacy schemas kept for backward compatibility
class WorkoutLogListGet(BaseModel):
    workout_name: Optional[str] = None
    workout_log_id: Optional[int] = None
    user_name: Optional[str] = None
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

    model_config = ConfigDict(from_attributes=True)


class WorkoutLogListPost(BaseModel):
    workout_name: str
    user_name: Optional[str] = None
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
    workout_name: Optional[str] = None
    user_name: Optional[str] = None
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
