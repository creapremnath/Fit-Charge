from typing import List, Optional
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Query, Body, status
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import desc, func

from app.core.database import get_session
from app.auth.oauth2 import get_current_user
from app.api.v1.authentication.schemas import TokenData
from .models import Workout, Workout_Log, Workout_Log_Detail
from .schemas import (
    WorkoutLogCreate,
    WorkoutLogUpdate,
    WorkoutLogResponse,
    WorkoutLogListGet,
    WorkoutLogListPatch,
    WorkoutLogListPost
)

router = APIRouter()


@router.post("/logs", response_model=WorkoutLogResponse, status_code=status.HTTP_201_CREATED)
def create_workout_log(
    payload: WorkoutLogCreate,
    current_user: TokenData = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Log a completed workout session with set details and volume metrics.
    """
    # Calculate volume if not provided
    calculated_volume = payload.volume or 0.0
    if not calculated_volume and payload.details:
        calculated_volume = sum((d.reps or 0) * (d.weight or 0.0) for d in payload.details if d.is_completed)

    new_log = Workout_Log(
        user_id=current_user.user_id,
        workout_id=payload.workout_id,
        template_id=payload.template_id,
        workout_name=payload.workout_name,
        workout_date=payload.workout_date or datetime.now(timezone.utc),
        tut=payload.tut,
        rest=payload.rest,
        rpe=payload.rpe,
        sets=payload.sets or (len(payload.details) if payload.details else 1),
        reps=payload.reps or 0,
        weight=payload.weight or 0.0,
        volume=calculated_volume,
        distance=payload.distance,
        duration_minutes=payload.duration_minutes,
        notes=payload.notes
    )
    session.add(new_log)
    session.flush()

    if payload.details:
        for idx, set_item in enumerate(payload.details):
            detail_row = Workout_Log_Detail(
                workout_log_id=new_log.id,
                workout_id=set_item.workout_id or payload.workout_id,
                exercise_name=set_item.exercise_name or payload.workout_name,
                set_number=set_item.set_number or (idx + 1),
                set_type=set_item.set_type or "normal",
                reps=set_item.reps or 0,
                weight=set_item.weight or 0.0,
                tut=set_item.tut,
                rest=set_item.rest,
                rpe=set_item.rpe,
                is_completed=set_item.is_completed if set_item.is_completed is not None else True,
                detail=set_item.detail or f"Set {set_item.set_number or (idx + 1)}: {set_item.reps or 0} reps @ {set_item.weight or 0.0} kg"
            )
            session.add(detail_row)

    session.commit()

    created_log = (
        session.query(Workout_Log)
        .options(joinedload(Workout_Log.details))
        .filter(Workout_Log.id == new_log.id)
        .first()
    )
    return created_log


@router.get("/logs", response_model=List[WorkoutLogResponse])
def get_user_workout_logs(
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    current_user: TokenData = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Get user workout logs with set details, sorted by date descending.
    """
    query = (
        session.query(Workout_Log)
        .options(joinedload(Workout_Log.details))
        .filter(Workout_Log.user_id == current_user.user_id)
    )

    if start_date:
        query = query.filter(Workout_Log.workout_date >= start_date)
    if end_date:
        query = query.filter(Workout_Log.workout_date <= end_date)

    logs = query.order_by(desc(Workout_Log.workout_date)).offset(offset).limit(limit).all()
    return logs


@router.get("/logs/{log_id}", response_model=WorkoutLogResponse)
def get_single_workout_log(
    log_id: int,
    current_user: TokenData = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Get single workout log by ID with all set details.
    """
    log = (
        session.query(Workout_Log)
        .options(joinedload(Workout_Log.details))
        .filter(Workout_Log.id == log_id, Workout_Log.user_id == current_user.user_id)
        .first()
    )
    if not log:
        raise HTTPException(status_code=404, detail="Workout log not found")
    return log


@router.patch("/logs/{log_id}", response_model=WorkoutLogResponse)
@router.put("/logs/{log_id}", response_model=WorkoutLogResponse)
def update_workout_log(
    log_id: int,
    payload: WorkoutLogUpdate,
    current_user: TokenData = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Update a workout log entry.
    """
    log = (
        session.query(Workout_Log)
        .filter(Workout_Log.id == log_id, Workout_Log.user_id == current_user.user_id)
        .first()
    )
    if not log:
        raise HTTPException(status_code=404, detail="Workout log not found")

    if payload.workout_name is not None:
        log.workout_name = payload.workout_name
    if payload.workout_date is not None:
        log.workout_date = payload.workout_date
    if payload.tut is not None:
        log.tut = payload.tut
    if payload.rest is not None:
        log.rest = payload.rest
    if payload.rpe is not None:
        log.rpe = payload.rpe
    if payload.sets is not None:
        log.sets = payload.sets
    if payload.reps is not None:
        log.reps = payload.reps
    if payload.weight is not None:
        log.weight = payload.weight
    if payload.volume is not None:
        log.volume = payload.volume
    if payload.distance is not None:
        log.distance = payload.distance
    if payload.duration_minutes is not None:
        log.duration_minutes = payload.duration_minutes
    if payload.notes is not None:
        log.notes = payload.notes
    
    log.updated_at = datetime.now(timezone.utc)

    if payload.details is not None:
        for old_detail in log.details:
            session.delete(old_detail)
        session.flush()

        for idx, set_item in enumerate(payload.details):
            detail_row = Workout_Log_Detail(
                workout_log_id=log.id,
                workout_id=set_item.workout_id or log.workout_id,
                exercise_name=set_item.exercise_name or log.workout_name,
                set_number=set_item.set_number or (idx + 1),
                set_type=set_item.set_type or "normal",
                reps=set_item.reps or 0,
                weight=set_item.weight or 0.0,
                tut=set_item.tut,
                rest=set_item.rest,
                rpe=set_item.rpe,
                is_completed=set_item.is_completed if set_item.is_completed is not None else True,
                detail=set_item.detail or f"Set {set_item.set_number or (idx + 1)}: {set_item.reps or 0} reps @ {set_item.weight or 0.0} kg"
            )
            session.add(detail_row)

    session.commit()

    updated_log = (
        session.query(Workout_Log)
        .options(joinedload(Workout_Log.details))
        .filter(Workout_Log.id == log.id)
        .first()
    )
    return updated_log


@router.delete("/logs/{log_id}")
def delete_workout_log(
    log_id: int,
    current_user: TokenData = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Delete a workout log session.
    """
    log = (
        session.query(Workout_Log)
        .filter(Workout_Log.id == log_id, Workout_Log.user_id == current_user.user_id)
        .first()
    )
    if not log:
        raise HTTPException(status_code=404, detail="Workout log not found")

    session.delete(log)
    session.commit()
    return {"message": "Workout log deleted successfully", "deleted_id": log_id}


# ==========================================
# Legacy Route Compatibility Endpoints
# ==========================================

@router.get("/workout-log/get", response_model=List[WorkoutLogResponse])
def legacy_get_workout_logs(
    current_user: TokenData = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    logs = (
        session.query(Workout_Log)
        .options(joinedload(Workout_Log.details))
        .filter(Workout_Log.user_id == current_user.user_id)
        .order_by(desc(Workout_Log.workout_date))
        .all()
    )
    return logs


@router.post("/workout-log/add", response_model=WorkoutLogResponse)
def legacy_add_workout_logs(
    payload: WorkoutLogCreate,
    current_user: TokenData = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    return create_workout_log(payload, current_user, session)


@router.patch("/workout-log/update", response_model=WorkoutLogResponse)
def legacy_update_workout_logs(
    workout_log_id: int = Query(...),
    payload: WorkoutLogUpdate = Body(...),
    current_user: TokenData = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    return update_workout_log(workout_log_id, payload, current_user, session)
