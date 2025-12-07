from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.v1.workout.models import Workout
from app.api.v1.workout.schemas import WorkoutList
from app.core.database import get_session

router = APIRouter()


@router.get("/workouts", response_model=list[WorkoutList])
def get_all_workouts(session: Session = Depends(get_session)):
    workouts = session.query(Workout).all()
    return workouts
