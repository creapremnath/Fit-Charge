from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.core.database import get_session
from app.api.v1.workouts.models import Workout
from app.api.v1.workouts.schemas import WorkoutList

router = APIRouter()

@router.get("/workouts", response_model=list[WorkoutList])
def get_all_workouts(
    workout_name: Optional[List[str]] = Query(None),
    primary_muscle: Optional[List[str]] = Query(None),
    secondary_muscle: Optional[List[str]] = Query(None),
    session: Session = Depends(get_session)
):
    query = session.query(Workout)

    if workout_name:
        query = query.filter(
            or_(*[Workout.workout_name.ilike(f"%{name}%") for name in workout_name])
        )

    if primary_muscle:
        query = query.filter(
            Workout.primary_muscle.in_(primary_muscle)
        )

    if secondary_muscle:
        query = query.filter(
            Workout.secondary_muscle.in_(secondary_muscle)
        )

    workouts = query.all()
    return workouts
