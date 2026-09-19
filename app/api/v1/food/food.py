from typing import List, Optional
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.core.database import get_session
from app.auth.oauth2 import get_current_user
from app.api.v1.authentication.schemas import TokenData
from .models import FoodItem
from .schemas import FoodItemCreate, FoodItemUpdate, FoodItemResponse

router = APIRouter()


@router.post("/items", response_model=FoodItemResponse, status_code=status.HTTP_201_CREATED)
def create_food_item(
    payload: FoodItemCreate,
    current_user: TokenData = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Create a new food item in the library (or user-created custom food).
    """
    new_food = FoodItem(
        name=payload.name,
        brand=payload.brand,
        serving_size=payload.serving_size or 100.0,
        serving_unit=payload.serving_unit or "g",
        calories=payload.calories,
        protein=payload.protein or 0.0,
        carbs=payload.carbs or 0.0,
        fat=payload.fat or 0.0,
        fiber=payload.fiber or 0.0,
        sugar=payload.sugar or 0.0,
        sodium=payload.sodium or 0.0,
        barcode=payload.barcode,
        is_verified=payload.is_verified or False,
        user_id=current_user.user_id
    )
    session.add(new_food)
    session.commit()
    session.refresh(new_food)
    return new_food


@router.get("/items", response_model=List[FoodItemResponse])
def search_food_items(
    query: Optional[str] = Query(None, description="Search by food name or brand"),
    barcode: Optional[str] = Query(None, description="Search by barcode"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: TokenData = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Search food database by keyword or barcode.
    """
    db_query = session.query(FoodItem)

    if barcode:
        db_query = db_query.filter(FoodItem.barcode == barcode)
    elif query:
        search_pattern = f"%{query.strip()}%"
        db_query = db_query.filter(
            or_(
                FoodItem.name.ilike(search_pattern),
                FoodItem.brand.ilike(search_pattern)
            )
        )

    # Return verified foods and user's own custom foods
    db_query = db_query.filter(
        or_(
            FoodItem.user_id == current_user.user_id,
            FoodItem.user_id.is_(None),
            FoodItem.is_verified == True
        )
    )

    foods = db_query.order_by(FoodItem.name.asc()).offset(offset).limit(limit).all()
    return foods


@router.get("/items/{food_id}", response_model=FoodItemResponse)
def get_single_food_item(
    food_id: int,
    current_user: TokenData = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Get detailed nutritional information for a specific food item.
    """
    food = session.query(FoodItem).filter(FoodItem.id == food_id).first()
    if not food:
        raise HTTPException(status_code=404, detail="Food item not found")
    return food


@router.patch("/items/{food_id}", response_model=FoodItemResponse)
def update_food_item(
    food_id: int,
    payload: FoodItemUpdate,
    current_user: TokenData = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Update a custom food item created by the user.
    """
    food = (
        session.query(FoodItem)
        .filter(FoodItem.id == food_id, FoodItem.user_id == current_user.user_id)
        .first()
    )
    if not food:
        raise HTTPException(status_code=404, detail="Food item not found or unauthorized")

    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if value is not None:
            setattr(food, field, value)

    food.updated_at = datetime.now(timezone.utc)
    session.commit()
    session.refresh(food)
    return food


# Legacy route preserved for compatibility
@router.post("/food")
def legacy_food():
    return {"Message": "food routes"}
