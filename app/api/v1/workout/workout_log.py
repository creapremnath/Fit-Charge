from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_
from datetime import DateTime, date
from app.core.database import get_session
from app.api.v1.workout.models import Workout as workout, Workout_log
from app.api.v1.user.models import User as user
from app.api.v1.workout.schemas import Workout_logList

router = APIRouter()

@router.get("/workout-log")
def get_items():
    return {"Message":"workoutlog routes"}

@router.get("/workout-log", response_model=list[Workout_logList])
def get_all_workout_logs(
    user_id: List[int] = Query(None),
    workout_name: Optional[List[int]] = Query(None),
    workout_date: Optional[List[DateTime]] = Query(None),
    primary_muscle: Optional[List[int]] = Query(None),
    secondary_muscle: Optional[List[int]] = Query(None),
    workout_type: Optional[List[int]] = Query(None),
    is_super_set: Optional[bool] = Query(None),
    is_drop_set: Optional[bool] = Query(None),
    is_giant_set: Optional[bool] = Query(None),
    is_finisher: Optional[bool] = Query(None),
    is_warmup: Optional[bool] = Query(None),
    is_failure: Optional[bool] = Query(None),
    session: Session = Depends(get_session)
):
    query = session.query(Workout_log)

    query = query.join(user, user.user_id == Workout_log.user_id, isrouter = True)

    if workout_name:  # workout_name is a list
        query = (
            query
            .join(workout, workout.workout_id == Workout_log.workout_id, isouter=True)
            .filter(or_(*[workout.workout_name.ilike(f"%{name}%") for name in workout_name]))
        )
    


    if primary_muscle:
        query = query.filter(
            workout.primary_muscle.in_(primary_muscle)
        )

    if secondary_muscle:
        query = query.filter(
            workout.secondary_muscle.in_(secondary_muscle)
        )

    if workout_type:
        query = query.filter(
            Workout_log.workout_type.in_(workout_type)
        )

    if is_super_set:
        query = query.filter(Workout_log.is_super_set == is_super_set)

    if is_drop_set:
        query = query.filter(Workout_log.is_drop_set == is_drop_set)

    if is_giant_set:
        query = query.filter(Workout_log.is_giant_set == is_giant_set)

    if is_finisher:
        query = query.filter(Workout_log.is_finisher == is_finisher)

    if is_warmup:
        query = query.filter(Workout_log.is_warmup == is_warmup)

    if is_failure:
        query = query.filter(Workout_log.is_failure == is_failure)

    Workout_log = query.all()
    return Workout_log


