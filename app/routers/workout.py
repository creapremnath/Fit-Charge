from fastapi import APIRouter, Depends, status, HTTPException, Response
from typing import List
from sqlmodel import Session, select
from db.database import get_session
from models.workouts_model import Workout
from fc_logger import get_logger

# Initialize logger
logger = get_logger("routers.workout")

# Router instance
router = APIRouter(
    tags=["Workouts"]
)

@router.post("/workouts/", response_model=Workout, status_code=status.HTTP_201_CREATED)
def create_workout(workout: Workout, session: Session = Depends(get_session)):
    """
    Create a new workout in the database.
    """
    session.add(workout)
    session.commit()
    session.refresh(workout)
    logger.info(f"Workout {workout.workout} created")
    return workout

@router.get("/workouts/{workout_id}", response_model=Workout)
def get_workout(workout_id: int, session: Session = Depends(get_session)):
    """
    Get a specific workout by ID.
    """
    workout = session.exec(select(Workout).where(Workout.id == workout_id)).first()
    if not workout:
        logger.error(f"Workout {workout_id} not found")
        raise HTTPException(status_code=404, detail="Workout not found")
    logger.info(f"Fetched workout {workout.workout} with ID {workout_id}")
    return workout

@router.get("/workouts/", response_model=List[Workout])
def list_all_workouts(session: Session = Depends(get_session)):
    """
    List all workouts from the database.
    """
    workouts = session.exec(select(Workout)).all()
    logger.info(f"Fetched {len(workouts)} workouts")
    return workouts

@router.put("/workouts/{workout_id}", response_model=Workout)
def update_workout(workout_id: int, updated_workout: Workout, session: Session = Depends(get_session)):
    """
    Update an existing workout by ID.
    """
    workout = session.exec(select(Workout).where(Workout.id == workout_id)).first()
    if not workout:
        logger.error(f"Workout {workout_id} not found for update")
        raise HTTPException(status_code=404, detail="Workout not found")

    workout.workout = updated_workout.workout
    workout.workout_desc = updated_workout.workout_desc
    workout.type = updated_workout.type
    workout.bodypart = updated_workout.bodypart
    workout.equipment = updated_workout.equipment
    workout.level = updated_workout.level
    workout.rating = updated_workout.rating
    workout.rating_desc = updated_workout.rating_desc

    session.commit()
    session.refresh(workout)
    logger.info(f"Workout {workout_id} updated")
    return workout

@router.delete("/workouts/{workout_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_workout(workout_id: int, session: Session = Depends(get_session)):
    """
    Delete a workout from the database by ID.
    """
    workout = session.exec(select(Workout).where(Workout.id == workout_id)).first()
    if not workout:
        logger.error(f"Workout {workout_id} not found for deletion")
        raise HTTPException(status_code=404, detail="Workout not found")

    session.delete(workout)
    session.commit()
    logger.info(f"Workout {workout_id} deleted")
    return Response(status_code=status.HTTP_204_NO_CONTENT)
