from typing import List, Optional
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.core.database import get_session
from app.auth.oauth2 import get_current_user
from app.api.v1.authentication.schemas import TokenData
from .models import User, User_log
from .schemas import UserLogCreate, UserLogUpdate, UserLogResponse

router = APIRouter()


@router.post("/logs", response_model=UserLogResponse, status_code=status.HTTP_201_CREATED)
def create_user_log(
    payload: UserLogCreate,
    current_user: TokenData = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Record a new body measurement / progress log for the user.
    """
    user = session.query(User).filter(User.user_id == current_user.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    new_log = User_log(
        user_id=current_user.user_id,
        height_cm=payload.height_cm,
        weight_kg=payload.weight_kg,
        body_fat_pct=payload.body_fat_pct,
        chest_cm=payload.chest_cm,
        neck_cm=payload.neck_cm,
        biceps_cm=payload.biceps_cm,
        hip_cm=payload.hip_cm,
        waist_cm=payload.waist_cm,
        thighs_cm=payload.thighs_cm,
        calves_cm=payload.calves_cm,
        shoulders_cm=payload.shoulders_cm,
        notes=payload.notes,
        log_date=payload.log_date or datetime.now(timezone.utc)
    )

    session.add(new_log)
    session.commit()
    session.refresh(new_log)
    return new_log


@router.get("/logs", response_model=List[UserLogResponse])
def get_user_logs(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    current_user: TokenData = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Get user body measurement logs history ordered by date descending.
    """
    logs = (
        session.query(User_log)
        .filter(User_log.user_id == current_user.user_id)
        .order_by(desc(User_log.created_at))
        .offset(offset)
        .limit(limit)
        .all()
    )
    return logs


@router.get("/logs/latest", response_model=Optional[UserLogResponse])
def get_latest_user_log(
    current_user: TokenData = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Get the most recent body measurement log for the user.
    """
    latest_log = (
        session.query(User_log)
        .filter(User_log.user_id == current_user.user_id)
        .order_by(desc(User_log.created_at))
        .first()
    )
    if not latest_log:
        return None
    return latest_log


@router.get("/logs/{log_id}", response_model=UserLogResponse)
def get_single_user_log(
    log_id: int,
    current_user: TokenData = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Get a specific measurement log by its ID.
    """
    log = (
        session.query(User_log)
        .filter(User_log.user_log_id == log_id, User_log.user_id == current_user.user_id)
        .first()
    )
    if not log:
        raise HTTPException(status_code=404, detail="Measurement log not found")
    return log


@router.patch("/logs/{log_id}", response_model=UserLogResponse)
@router.put("/logs/{log_id}", response_model=UserLogResponse)
def update_user_log(
    log_id: int,
    payload: UserLogUpdate,
    current_user: TokenData = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Update an existing body measurement log.
    """
    log = (
        session.query(User_log)
        .filter(User_log.user_log_id == log_id, User_log.user_id == current_user.user_id)
        .first()
    )
    if not log:
        raise HTTPException(status_code=404, detail="Measurement log not found")

    update_data = payload.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        if value is not None:
            setattr(log, key, value)

    session.commit()
    session.refresh(log)
    return log


@router.delete("/logs/{log_id}")
def delete_user_log(
    log_id: int,
    current_user: TokenData = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Delete a body measurement log entry.
    """
    log = (
        session.query(User_log)
        .filter(User_log.user_log_id == log_id, User_log.user_id == current_user.user_id)
        .first()
    )
    if not log:
        raise HTTPException(status_code=404, detail="Measurement log not found")

    session.delete(log)
    session.commit()
    return {"message": "Measurement log deleted successfully", "deleted_id": log_id}


# Legacy route preserved for compatibility
@router.post("/user-log")
def legacy_user_log():
    return {"Message": "user log routes"}
