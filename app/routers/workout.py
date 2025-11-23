from fastapi import APIRouter, Depends, status, HTTPException, Response,Query
from typing import List,Optional
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
def list_all_workouts(
    session: Session = Depends(get_session),
    skip: int = Query(0, ge=0),  # Default to skip 0 (first page)
    limit: int = Query(100, le=1000),  # Default to limit 100, max 1000
    workout_name: Optional[str] = Query(None),  # Optional: Filter by workout name
    body_muscle: Optional[str] = Query(None),  # Optional: Filter by body muscle
    workout_level: Optional[str] = Query(None)  # Optional: Filter by workout level
):
    """
    List workouts from the database with optional filtering by name and level, and pagination.
    """
    try:
        # Build the query, with explicit ordering by 'id' and selecting only needed fields
        query = select(Workout).offset(skip).limit(limit).order_by(Workout.id)

        # Apply filters
        if workout_name:
            query = query.filter(Workout.workout.ilike(f"%{workout_name}%"))  # Case-insensitive search for name
        if workout_level:
            query = query.filter(Workout.level == workout_level)  # Exact match for workout level
        if body_muscle:
            query = query.filter(Workout.bodypart.ilike(f"%{body_muscle}%")) # Exact match for body muscle

        # Execute the query
        workouts = session.exec(query).all()

        return workouts

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail="An error occurred while fetching workouts."
        )

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
