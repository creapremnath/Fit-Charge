from typing import List, Optional
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_

from app.core.database import get_session
from app.auth.oauth2 import get_current_user
from app.api.v1.authentication.schemas import TokenData
from .models import MealTemplate, MealTemplateItem, Food_Log
from .schemas import (
    MealTemplateCreate,
    MealTemplateUpdate,
    MealTemplateResponse,
    LogMealTemplateRequest,
    FoodLogResponse
)

router = APIRouter()


@router.post("/meal-templates", response_model=MealTemplateResponse, status_code=status.HTTP_201_CREATED)
def create_meal_template(
    payload: MealTemplateCreate,
    current_user: TokenData = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Create a reusable meal template (e.g. 'Oatmeal & Protein Shake' or 'Post-Workout Chicken Rice').
    """
    # Compute totals from items
    total_cal = sum(item.calories * (item.quantity or 1.0) for item in payload.items)
    total_prot = sum(item.protein * (item.quantity or 1.0) for item in payload.items)
    total_carbs = sum(item.carbs * (item.quantity or 1.0) for item in payload.items)
    total_fat = sum(item.fat * (item.quantity or 1.0) for item in payload.items)

    new_template = MealTemplate(
        user_id=current_user.user_id,
        name=payload.name,
        description=payload.description,
        meal_type=payload.meal_type or "any",
        total_calories=round(total_cal, 1),
        total_protein=round(total_prot, 1),
        total_carbs=round(total_carbs, 1),
        total_fat=round(total_fat, 1),
        is_custom=True
    )
    session.add(new_template)
    session.flush()

    for item in payload.items:
        template_item = MealTemplateItem(
            meal_template_id=new_template.id,
            food_id=item.food_id,
            food_name=item.food_name,
            serving_size=item.serving_size or 100.0,
            serving_unit=item.serving_unit or "g",
            quantity=item.quantity or 1.0,
            calories=item.calories,
            protein=item.protein or 0.0,
            carbs=item.carbs or 0.0,
            fat=item.fat or 0.0
        )
        session.add(template_item)

    session.commit()

    created = (
        session.query(MealTemplate)
        .options(joinedload(MealTemplate.items))
        .filter(MealTemplate.id == new_template.id)
        .first()
    )
    return created


@router.get("/meal-templates", response_model=List[MealTemplateResponse])
def get_meal_templates(
    meal_type: Optional[str] = Query(None),
    current_user: TokenData = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    List reusable meal templates created by the user.
    """
    query = (
        session.query(MealTemplate)
        .options(joinedload(MealTemplate.items))
        .filter(
            or_(
                MealTemplate.user_id == current_user.user_id,
                MealTemplate.user_id.is_(None)
            )
        )
    )

    if meal_type:
        query = query.filter(or_(MealTemplate.meal_type == meal_type.lower(), MealTemplate.meal_type == "any"))

    templates = query.order_by(MealTemplate.name.asc()).all()
    return templates


@router.get("/meal-templates/{template_id}", response_model=MealTemplateResponse)
def get_single_meal_template(
    template_id: int,
    current_user: TokenData = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Get details of a single meal template.
    """
    template = (
        session.query(MealTemplate)
        .options(joinedload(MealTemplate.items))
        .filter(
            MealTemplate.id == template_id,
            or_(
                MealTemplate.user_id == current_user.user_id,
                MealTemplate.user_id.is_(None)
            )
        )
        .first()
    )
    if not template:
        raise HTTPException(status_code=404, detail="Meal template not found")
    return template


@router.patch("/meal-templates/{template_id}", response_model=MealTemplateResponse)
@router.put("/meal-templates/{template_id}", response_model=MealTemplateResponse)
def update_meal_template(
    template_id: int,
    payload: MealTemplateUpdate,
    current_user: TokenData = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Update a meal template owned by the user.
    """
    template = (
        session.query(MealTemplate)
        .filter(MealTemplate.id == template_id, MealTemplate.user_id == current_user.user_id)
        .first()
    )
    if not template:
        raise HTTPException(status_code=404, detail="Meal template not found or unauthorized")

    if payload.name is not None:
        template.name = payload.name
    if payload.description is not None:
        template.description = payload.description
    if payload.meal_type is not None:
        template.meal_type = payload.meal_type

    template.updated_at = datetime.now(timezone.utc)

    if payload.items is not None:
        # Delete old items
        for old_item in template.items:
            session.delete(old_item)
        session.flush()

        total_cal = 0.0
        total_prot = 0.0
        total_carbs = 0.0
        total_fat = 0.0

        for item in payload.items:
            qty = item.quantity or 1.0
            total_cal += item.calories * qty
            total_prot += (item.protein or 0.0) * qty
            total_carbs += (item.carbs or 0.0) * qty
            total_fat += (item.fat or 0.0) * qty

            new_item = MealTemplateItem(
                meal_template_id=template.id,
                food_id=item.food_id,
                food_name=item.food_name,
                serving_size=item.serving_size or 100.0,
                serving_unit=item.serving_unit or "g",
                quantity=qty,
                calories=item.calories,
                protein=item.protein or 0.0,
                carbs=item.carbs or 0.0,
                fat=item.fat or 0.0
            )
            session.add(new_item)

        template.total_calories = round(total_cal, 1)
        template.total_protein = round(total_prot, 1)
        template.total_carbs = round(total_carbs, 1)
        template.total_fat = round(total_fat, 1)

    session.commit()

    updated = (
        session.query(MealTemplate)
        .options(joinedload(MealTemplate.items))
        .filter(MealTemplate.id == template.id)
        .first()
    )
    return updated


@router.delete("/meal-templates/{template_id}")
def delete_meal_template(
    template_id: int,
    current_user: TokenData = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Delete a meal template.
    """
    template = (
        session.query(MealTemplate)
        .filter(MealTemplate.id == template_id, MealTemplate.user_id == current_user.user_id)
        .first()
    )
    if not template:
        raise HTTPException(status_code=404, detail="Meal template not found or unauthorized")

    session.delete(template)
    session.commit()
    return {"message": "Meal template deleted successfully", "deleted_id": template_id}


@router.post("/meal-templates/{template_id}/log", response_model=List[FoodLogResponse])
def log_entire_meal_template(
    template_id: int,
    payload: LogMealTemplateRequest = LogMealTemplateRequest(),
    current_user: TokenData = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    1-Click Log: Instantly records all food items in this meal template to today's food log!
    """
    template = (
        session.query(MealTemplate)
        .options(joinedload(MealTemplate.items))
        .filter(
            MealTemplate.id == template_id,
            or_(
                MealTemplate.user_id == current_user.user_id,
                MealTemplate.user_id.is_(None)
            )
        )
        .first()
    )
    if not template:
        raise HTTPException(status_code=404, detail="Meal template not found")

    target_meal_type = payload.meal_type or (template.meal_type if template.meal_type != "any" else "snack")
    target_date = payload.log_date or datetime.now(timezone.utc)

    logged_items = []
    for item in template.items:
        log_entry = Food_Log(
            user_id=current_user.user_id,
            food_id=item.food_id,
            food_name=item.food_name,
            meal_type=target_meal_type.lower(),
            log_date=target_date,
            servings=item.quantity or 1.0,
            serving_size=item.serving_size,
            serving_unit=item.serving_unit,
            calories=item.calories * (item.quantity or 1.0),
            protein=(item.protein or 0.0) * (item.quantity or 1.0),
            carbs=(item.carbs or 0.0) * (item.quantity or 1.0),
            fat=(item.fat or 0.0) * (item.quantity or 1.0),
            fiber=0.0
        )
        session.add(log_entry)
        logged_items.append(log_entry)

    session.commit()
    for log_entry in logged_items:
        session.refresh(log_entry)

    return logged_items
