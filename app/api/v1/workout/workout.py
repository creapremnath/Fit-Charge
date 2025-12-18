from typing import List, Optional
from fastapi import APIRouter, Depends, Query, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import or_, func, select, ARRAY, String, cast
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

    if workout_name is not None:
        workout_name = [name.lower() for name in workout_name]
    if primary_muscle is not None:
        primary_muscle = [muscle.lower() for muscle in primary_muscle]
    if secondary_muscle is not None:
        secondary_muscle = [muscle.lower() for muscle in secondary_muscle]

    base_query = select(
        Workout.id.label("workout_id"),
        Workout.name.label("workout_name"),
        Workout.description.label("workout_description"),
        Workout.met.label("met"),
        func.array_agg(Muscle.name)
        .filter(Workout_Muscle.is_primary_muscle == True)
        .label("primary_muscle"),
        func.array_agg(Muscle.name)
        .filter(Workout_Muscle.is_primary_muscle == False)
        .label("secondary_muscle"),
    ).join(Workout_Muscle).join(Muscle).group_by(Workout.id, Workout.name, Workout.description, Workout.met)

    subquery = base_query.subquery()

    query = session.query(subquery)

    print(workout_name)
    print(primary_muscle)
    print(secondary_muscle)
    if workout_name:
        query = query.filter(
            or_(*[func.lower(subquery.c.workout_name).ilike(f"%{name}%") for name in workout_name])
        )
        logger.debug('Workout(s) Present' + f"{subquery.c.workout_name}")

    if primary_muscle:
        query = query.where(subquery.c.primary_muscle.op('&&')(cast(primary_muscle, ARRAY(String))))
        logger.debug('Primary Muscle(s) Present' + f"{subquery.c.primary_muscle}")

    if secondary_muscle:
        query = query.where(subquery.c.secondary_muscle.op('&&')(cast(secondary_muscle, ARRAY(String))))
        logger.debug('Secondary Muscle(s) Present' + f"{subquery.c.secondary_muscle}")

    try:
        workouts = session.execute(query).mappings().all()
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
