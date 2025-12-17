from typing import List, Optional
from fastapi import APIRouter, Depends, Query, Body
from sqlalchemy.orm import Session
from sqlalchemy import or_, Float, func
from datetime import datetime, date
from app.core.database import get_session
from .models import Workout as Workout
from .models import Workout_Log as Workout_Log
from .models import Workout_Muscle as Workout_Muscle
from .models import Muscle as Muscle
from app.api.v1.user.models import User as user
from .schemas import WorkoutLogListGet, WorkoutLogListPatch, WorkoutLogListPost

router = APIRouter()


@router.get("/workout-log/get", response_model=list[WorkoutLogListGet])
def get_all_workout_logs(
    user_id: List[int] = Query(None),
    workout_name: Optional[List[str]] = Query(None),
    workout_date: Optional[List[datetime]] = Query(None),
    primary_muscle: Optional[List[str]] = Query(None),
    secondary_muscle: Optional[List[str]] = Query(None),
    workout_type: Optional[List[str]] = Query(None),
    is_super_set: Optional[bool] = Query(None),
    is_drop_set: Optional[bool] = Query(None),
    is_giant_set: Optional[bool] = Query(None),
    is_finisher: Optional[bool] = Query(None),
    is_warmup: Optional[bool] = Query(None),
    is_failure: Optional[bool] = Query(None),
    session: Session = Depends(get_session)
):
    query = session.query(Workout_Log)

    query = query.join(user, user.user_id == Workout_Log.user_id, isrouter = True)

    if workout_name or primary_muscle or secondary_muscle:  # workout_name is a list
        query = (
        session.query(
            Workout.id,
            Workout.name,
            Workout.description,
            Workout.met,
            func.string_agg(
                Muscle.name, ', '
            ).filter(Workout_Muscle.is_primary == True)
            .label("primary_muscle"),
            func.string_agg(
                Muscle.name, ', '
            ).filter(Workout_Muscle.is_primary == False)
            .label("secondary_muscle"),
            )
        .join(Workout_Muscle)
        .join(Muscle)
        .group_by(Workout.name)
        )
        if workout_name: 
            query = query.filter(or_(*[Workout.name.ilike(f"%{name}%") for name in workout_name])
    
            )

        if primary_muscle:
            query = query.filter(
                Workout.primary_muscle.in_(primary_muscle)
            )

        if secondary_muscle:
            query = query.filter(
                Workout.secondary_muscle.in_(secondary_muscle)
            )

    if workout_type:
        query = query.filter(
            Workout_Log.workout_type.in_(workout_type)
        )

    '''if is_super_set:
        query = query.filter(Workout_Log.is_super_set == is_super_set)

    if is_drop_set:
        query = query.filter(Workout_Log.is_drop_set == is_drop_set)

    if is_giant_set:
        query = query.filter(Workout_Log.is_giant_set == is_giant_set)

    if is_finisher:
        query = query.filter(Workout_Log.is_finisher == is_finisher)

    if is_warmup:
        query = query.filter(Workout_Log.is_warmup == is_warmup)

    if is_failure:
        query = query.filter(Workout_Log.is_failure == is_failure)'''

    workout_logs = query.all()
    return workout_logs


@router.patch("/workout-log/update",response_model=list[WorkoutLogListPatch])
def update_workout_logs(
    workout_log_id: int,
    payload: WorkoutLogListPatch = Body(...),
    session: Session = Depends(get_session),
):
    pass

@router.post("/workout-log/add",response_model=list[WorkoutLogListPost])
def add_workout_logs(
    payload: WorkoutLogListPost,
    session: Session = Depends(get_session)
):
    pass
