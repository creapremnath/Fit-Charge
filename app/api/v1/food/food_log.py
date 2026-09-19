from typing import List, Optional
from datetime import datetime, date, timezone, time
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.core.database import get_session
from app.auth.oauth2 import get_current_user
from app.api.v1.authentication.schemas import TokenData
from .models import Food_Log, FoodItem
from .schemas import (
    FoodLogCreate,
    FoodLogUpdate,
    FoodLogResponse,
    DailyFoodSummaryResponse,
    DailyMacroTotals
)

router = APIRouter()


@router.post("/logs", response_model=FoodLogResponse, status_code=status.HTTP_201_CREATED)
def create_food_log(
    payload: FoodLogCreate,
    current_user: TokenData = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Log food consumed (breakfast, lunch, dinner, snack).
    """
    log_time = payload.log_date or datetime.now(timezone.utc)
    
    calories = payload.calories
    protein = payload.protein or 0.0
    carbs = payload.carbs or 0.0
    fat = payload.fat or 0.0
    fiber = payload.fiber or 0.0

    new_log = Food_Log(
        user_id=current_user.user_id,
        food_id=payload.food_id,
        food_name=payload.food_name,
        meal_type=payload.meal_type.lower(),
        log_date=log_time,
        servings=payload.servings or 1.0,
        serving_size=payload.serving_size,
        serving_unit=payload.serving_unit,
        calories=calories,
        protein=protein,
        carbs=carbs,
        fat=fat,
        fiber=fiber
    )
    session.add(new_log)
    session.commit()
    session.refresh(new_log)
    return new_log


@router.get("/logs", response_model=DailyFoodSummaryResponse)
def get_daily_food_logs(
    target_date: Optional[date] = Query(None, description="Date in YYYY-MM-DD format (defaults to today)"),
    current_user: TokenData = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Get all food logs for a given date, grouped by meal type, with total macro summaries.
    """
    query_date = target_date or datetime.now(timezone.utc).date()
    start_of_day = datetime.combine(query_date, time.min)
    end_of_day = datetime.combine(query_date, time.max)

    logs = (
        session.query(Food_Log)
        .filter(
            Food_Log.user_id == current_user.user_id,
            Food_Log.log_date >= start_of_day,
            Food_Log.log_date <= end_of_day
        )
        .order_by(Food_Log.log_date.asc())
        .all()
    )

    by_meal = {
        "breakfast": [],
        "lunch": [],
        "dinner": [],
        "snack": []
    }

    totals = DailyMacroTotals()

    for item in logs:
        m_type = item.meal_type.lower() if item.meal_type else "snack"
        if m_type not in by_meal:
            by_meal[m_type] = []
        by_meal[m_type].append(FoodLogResponse.model_validate(item))

        totals.total_calories += item.calories or 0.0
        totals.total_protein += item.protein or 0.0
        totals.total_carbs += item.carbs or 0.0
        totals.total_fat += item.fat or 0.0
        totals.total_fiber += item.fiber or 0.0

    # Round totals to 1 decimal place
    totals.total_calories = round(totals.total_calories, 1)
    totals.total_protein = round(totals.total_protein, 1)
    totals.total_carbs = round(totals.total_carbs, 1)
    totals.total_fat = round(totals.total_fat, 1)
    totals.total_fiber = round(totals.total_fiber, 1)

    return DailyFoodSummaryResponse(
        date=query_date.isoformat(),
        totals=totals,
        by_meal=by_meal
    )


@router.get("/logs/history", response_model=List[FoodLogResponse])
def get_food_log_history(
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    current_user: TokenData = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Get raw food log history entries with pagination.
    """
    query = session.query(Food_Log).filter(Food_Log.user_id == current_user.user_id)

    if start_date:
        query = query.filter(Food_Log.log_date >= start_date)
    if end_date:
        query = query.filter(Food_Log.log_date <= end_date)

    logs = query.order_by(desc(Food_Log.log_date)).offset(offset).limit(limit).all()
    return logs


@router.get("/logs/{log_id}", response_model=FoodLogResponse)
def get_single_food_log(
    log_id: int,
    current_user: TokenData = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Get a specific food log entry.
    """
    log = (
        session.query(Food_Log)
        .filter(Food_Log.id == log_id, Food_Log.user_id == current_user.user_id)
        .first()
    )
    if not log:
        raise HTTPException(status_code=404, detail="Food log not found")
    return log


@router.patch("/logs/{log_id}", response_model=FoodLogResponse)
@router.put("/logs/{log_id}", response_model=FoodLogResponse)
def update_food_log(
    log_id: int,
    payload: FoodLogUpdate,
    current_user: TokenData = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Update a logged food entry.
    """
    log = (
        session.query(Food_Log)
        .filter(Food_Log.id == log_id, Food_Log.user_id == current_user.user_id)
        .first()
    )
    if not log:
        raise HTTPException(status_code=404, detail="Food log not found")

    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if value is not None:
            if field == "meal_type":
                value = value.lower()
            setattr(log, field, value)

    log.updated_at = datetime.now(timezone.utc)
    session.commit()
    session.refresh(log)
    return log


@router.delete("/logs/{log_id}")
def delete_food_log(
    log_id: int,
    current_user: TokenData = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Delete a food log entry.
    """
    log = (
        session.query(Food_Log)
        .filter(Food_Log.id == log_id, Food_Log.user_id == current_user.user_id)
        .first()
    )
    if not log:
        raise HTTPException(status_code=404, detail="Food log not found")

    session.delete(log)
    session.commit()
    return {"message": "Food log deleted successfully", "deleted_id": log_id}


# Legacy route preserved for compatibility
@router.post("/food-log")
def legacy_food_log():
    return {"Message": "food log routes"}
