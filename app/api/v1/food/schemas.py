from typing import Optional, List, Dict
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


# ==========================================
# Food Item Schemas
# ==========================================

class FoodItemCreate(BaseModel):
    name: str
    brand: Optional[str] = None
    serving_size: Optional[float] = 100.0
    serving_unit: Optional[str] = "g"
    calories: float
    protein: Optional[float] = 0.0
    carbs: Optional[float] = 0.0
    fat: Optional[float] = 0.0
    fiber: Optional[float] = 0.0
    sugar: Optional[float] = 0.0
    sodium: Optional[float] = 0.0
    barcode: Optional[str] = None
    is_verified: Optional[bool] = False


class FoodItemUpdate(BaseModel):
    name: Optional[str] = None
    brand: Optional[str] = None
    serving_size: Optional[float] = None
    serving_unit: Optional[str] = None
    calories: Optional[float] = None
    protein: Optional[float] = None
    carbs: Optional[float] = None
    fat: Optional[float] = None
    fiber: Optional[float] = None
    sugar: Optional[float] = None
    sodium: Optional[float] = None
    barcode: Optional[str] = None


class FoodItemResponse(BaseModel):
    id: int
    name: str
    brand: Optional[str] = None
    serving_size: float
    serving_unit: str
    calories: float
    protein: float
    carbs: float
    fat: float
    fiber: Optional[float] = 0.0
    sugar: Optional[float] = 0.0
    sodium: Optional[float] = 0.0
    barcode: Optional[str] = None
    is_verified: bool
    user_id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


# ==========================================
# Food Log Schemas
# ==========================================

class FoodLogCreate(BaseModel):
    food_id: Optional[int] = None
    food_name: str
    meal_type: str # 'breakfast', 'lunch', 'dinner', 'snack'
    log_date: Optional[datetime] = None
    servings: Optional[float] = 1.0
    serving_size: Optional[float] = 100.0
    serving_unit: Optional[str] = "g"
    calories: float
    protein: Optional[float] = 0.0
    carbs: Optional[float] = 0.0
    fat: Optional[float] = 0.0
    fiber: Optional[float] = 0.0


class FoodLogUpdate(BaseModel):
    food_name: Optional[str] = None
    meal_type: Optional[str] = None
    log_date: Optional[datetime] = None
    servings: Optional[float] = None
    serving_size: Optional[float] = None
    serving_unit: Optional[str] = None
    calories: Optional[float] = None
    protein: Optional[float] = None
    carbs: Optional[float] = None
    fat: Optional[float] = None
    fiber: Optional[float] = None


class FoodLogResponse(BaseModel):
    id: int
    user_id: int
    food_id: Optional[int] = None
    food_name: str
    meal_type: str
    log_date: datetime
    servings: float
    serving_size: Optional[float] = None
    serving_unit: Optional[str] = None
    calories: float
    protein: float
    carbs: float
    fat: float
    fiber: Optional[float] = 0.0
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class DailyMacroTotals(BaseModel):
    total_calories: float = 0.0
    total_protein: float = 0.0
    total_carbs: float = 0.0
    total_fat: float = 0.0
    total_fiber: float = 0.0


class DailyFoodSummaryResponse(BaseModel):
    date: str
    totals: DailyMacroTotals
    by_meal: Dict[str, List[FoodLogResponse]]


# ==========================================
# Meal Template Schemas
# ==========================================

class MealTemplateItemCreate(BaseModel):
    food_id: Optional[int] = None
    food_name: str
    serving_size: Optional[float] = 100.0
    serving_unit: Optional[str] = "g"
    quantity: Optional[float] = 1.0
    calories: float
    protein: Optional[float] = 0.0
    carbs: Optional[float] = 0.0
    fat: Optional[float] = 0.0


class MealTemplateItemResponse(MealTemplateItemCreate):
    id: int
    meal_template_id: int

    model_config = ConfigDict(from_attributes=True)


class MealTemplateCreate(BaseModel):
    name: str
    description: Optional[str] = None
    meal_type: Optional[str] = "any" # 'breakfast', 'lunch', 'dinner', 'snack', 'any'
    items: List[MealTemplateItemCreate] = []


class MealTemplateUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    meal_type: Optional[str] = None
    items: Optional[List[MealTemplateItemCreate]] = None


class MealTemplateResponse(BaseModel):
    id: int
    user_id: Optional[int] = None
    name: str
    description: Optional[str] = None
    meal_type: str
    total_calories: float
    total_protein: float
    total_carbs: float
    total_fat: float
    is_custom: bool
    items: List[MealTemplateItemResponse] = []
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class LogMealTemplateRequest(BaseModel):
    meal_type: Optional[str] = None # Overrides template meal_type if provided (e.g. log as 'breakfast')
    log_date: Optional[datetime] = None
