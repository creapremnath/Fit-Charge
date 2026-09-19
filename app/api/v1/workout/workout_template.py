from typing import List, Optional
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_

from app.core.database import get_session
from app.auth.oauth2 import get_current_user
from app.api.v1.authentication.schemas import TokenData
from .models import WorkoutTemplate, WorkoutTemplateDay, WorkoutTemplateExercise
from .schemas import (
    WorkoutTemplateCreate,
    WorkoutTemplateUpdate,
    WorkoutTemplateResponse
)

router = APIRouter()


@router.post("/templates", response_model=WorkoutTemplateResponse, status_code=status.HTTP_201_CREATED)
def create_workout_template(
    payload: WorkoutTemplateCreate,
    current_user: TokenData = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Create a new custom workout template with days and exercises.
    """
    new_template = WorkoutTemplate(
        user_id=current_user.user_id,
        name=payload.name,
        description=payload.description,
        category=payload.category,
        difficulty=payload.difficulty,
        is_custom=True,
        is_public=payload.is_public or False
    )
    session.add(new_template)
    session.flush()

    if payload.days:
        for d_idx, day_data in enumerate(payload.days):
            day_entry = WorkoutTemplateDay(
                template_id=new_template.id,
                day_name=day_data.day_name,
                day_order=day_data.day_order or (d_idx + 1),
                is_rest_day=day_data.is_rest_day or False
            )
            session.add(day_entry)
            session.flush()

            if day_data.exercises:
                for e_idx, ex_data in enumerate(day_data.exercises):
                    exercise_entry = WorkoutTemplateExercise(
                        template_day_id=day_entry.id,
                        workout_id=ex_data.workout_id,
                        exercise_name=ex_data.exercise_name,
                        sets=ex_data.sets or 3,
                        reps=ex_data.reps or 10,
                        weight=ex_data.weight or 0.0,
                        rest_seconds=ex_data.rest_seconds or 60,
                        order_index=ex_data.order_index or (e_idx + 1),
                        notes=ex_data.notes
                    )
                    session.add(exercise_entry)

    session.commit()
    
    # Reload with relationships
    created_template = (
        session.query(WorkoutTemplate)
        .options(
            joinedload(WorkoutTemplate.days).joinedload(WorkoutTemplateDay.exercises)
        )
        .filter(WorkoutTemplate.id == new_template.id)
        .first()
    )
    return created_template


@router.get("/templates", response_model=List[WorkoutTemplateResponse])
def get_workout_templates(
    category: Optional[str] = Query(None),
    difficulty: Optional[str] = Query(None),
    include_presets: bool = Query(True),
    current_user: TokenData = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    List workout templates available to the current user (both their custom templates and system presets).
    """
    filters = []
    if include_presets:
        filters.append(or_(WorkoutTemplate.user_id == current_user.user_id, WorkoutTemplate.user_id.is_(None), WorkoutTemplate.is_public == True))
    else:
        filters.append(WorkoutTemplate.user_id == current_user.user_id)

    if category:
        filters.append(WorkoutTemplate.category.ilike(f"%{category}%"))
    if difficulty:
        filters.append(WorkoutTemplate.difficulty.ilike(f"%{difficulty}%"))

    templates = (
        session.query(WorkoutTemplate)
        .options(
            joinedload(WorkoutTemplate.days).joinedload(WorkoutTemplateDay.exercises)
        )
        .filter(*filters)
        .order_by(WorkoutTemplate.id.desc())
        .all()
    )
    return templates


@router.get("/templates/{template_id}", response_model=WorkoutTemplateResponse)
def get_single_workout_template(
    template_id: int,
    current_user: TokenData = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Get a single workout template by ID with all days and exercises.
    """
    template = (
        session.query(WorkoutTemplate)
        .options(
            joinedload(WorkoutTemplate.days).joinedload(WorkoutTemplateDay.exercises)
        )
        .filter(
            WorkoutTemplate.id == template_id,
            or_(
                WorkoutTemplate.user_id == current_user.user_id,
                WorkoutTemplate.user_id.is_(None),
                WorkoutTemplate.is_public == True
            )
        )
        .first()
    )
    if not template:
        raise HTTPException(status_code=404, detail="Workout template not found")
    return template


@router.put("/templates/{template_id}", response_model=WorkoutTemplateResponse)
@router.patch("/templates/{template_id}", response_model=WorkoutTemplateResponse)
def update_workout_template(
    template_id: int,
    payload: WorkoutTemplateUpdate,
    current_user: TokenData = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Update a custom workout template owned by the user.
    """
    template = (
        session.query(WorkoutTemplate)
        .filter(WorkoutTemplate.id == template_id, WorkoutTemplate.user_id == current_user.user_id)
        .first()
    )
    if not template:
        raise HTTPException(status_code=404, detail="Workout template not found or unauthorized")

    if payload.name is not None:
        template.name = payload.name
    if payload.description is not None:
        template.description = payload.description
    if payload.category is not None:
        template.category = payload.category
    if payload.difficulty is not None:
        template.difficulty = payload.difficulty
    if payload.is_public is not None:
        template.is_public = payload.is_public
    
    template.updated_at = datetime.now(timezone.utc)

    # If new days provided, replace existing days
    if payload.days is not None:
        # Delete existing days
        for old_day in template.days:
            session.delete(old_day)
        session.flush()

        for d_idx, day_data in enumerate(payload.days):
            day_entry = WorkoutTemplateDay(
                template_id=template.id,
                day_name=day_data.day_name,
                day_order=day_data.day_order or (d_idx + 1),
                is_rest_day=day_data.is_rest_day or False
            )
            session.add(day_entry)
            session.flush()

            if day_data.exercises:
                for e_idx, ex_data in enumerate(day_data.exercises):
                    exercise_entry = WorkoutTemplateExercise(
                        template_day_id=day_entry.id,
                        workout_id=ex_data.workout_id,
                        exercise_name=ex_data.exercise_name,
                        sets=ex_data.sets or 3,
                        reps=ex_data.reps or 10,
                        weight=ex_data.weight or 0.0,
                        rest_seconds=ex_data.rest_seconds or 60,
                        order_index=ex_data.order_index or (e_idx + 1),
                        notes=ex_data.notes
                    )
                    session.add(exercise_entry)

    session.commit()

    updated_template = (
        session.query(WorkoutTemplate)
        .options(
            joinedload(WorkoutTemplate.days).joinedload(WorkoutTemplateDay.exercises)
        )
        .filter(WorkoutTemplate.id == template.id)
        .first()
    )
    return updated_template


@router.delete("/templates/{template_id}")
def delete_workout_template(
    template_id: int,
    current_user: TokenData = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Delete a custom workout template owned by the user.
    """
    template = (
        session.query(WorkoutTemplate)
        .filter(WorkoutTemplate.id == template_id, WorkoutTemplate.user_id == current_user.user_id)
        .first()
    )
    if not template:
        raise HTTPException(status_code=404, detail="Workout template not found or unauthorized")

    session.delete(template)
    session.commit()
    return {"message": "Workout template deleted successfully", "deleted_id": template_id}
