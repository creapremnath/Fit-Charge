from typing import List, Optional
from fastapi import APIRouter, Depends, Query, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import or_, func
from sqlalchemy.exc import SQLAlchemyError

from app.core.database import get_session
from .models import Workout, Muscle, Workout_Muscle
from .schemas import WorkoutListGet
from app.core.fc_logger import get_logger

logger = get_logger("fitcharge.workout")

router = APIRouter()

@router.get("/workouts", response_model=list[WorkoutListGet])
def get_all_workouts(
    workout_name: Optional[List[str]] = Query(None),
    primary_muscle: Optional[List[str]] = Query(None),
    secondary_muscle: Optional[List[str]] = Query(None),
    session: Session = Depends(get_session)
):
    base_query = (
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

    subquery = base_query.subquery()

    query = session.query(subquery)


    if workout_name:
        query = query.filter(
            or_(*[subquery.c.name.ilike(f"%{name}%") for name in workout_name])
        )
        logger.debug('Workout(s) Present' + f"{subquery.c.name}")

    if primary_muscle:
        query = query.filter(
            or_(*[subquery.c.primary_muscle.ilike(f"%{muscle}%") for muscle in primary_muscle])
        )
        logger.debug('Primary Muscle(s) Present' + f"{subquery.c.primary_muscle}")

    if secondary_muscle:
        query = query.filter(
            or_(*[subquery.c.secondary_muscle.ilike(f"%{muscle}%") for muscle in secondary_muscle])
        )
        logger.debug('Secondary Muscle(s) Present' + f"{subquery.c.secondary_muscle}")

    try:
        workouts = query.all()
        logger.info('Query results: ' + f"{workouts}")
    except SQLAlchemyError: 
        logger.exception("Query execution failed")
        raise HTTPException(500, "Database error")

    if not workouts:
        return JSONResponse(
            status_code=404,
            content={"message": "No matching workouts found"}
        )

    return workouts
