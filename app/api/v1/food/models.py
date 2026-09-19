from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base


class FoodItem(Base):
    __tablename__ = "food_item"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False, index=True)
    brand = Column(String, nullable=True)
    serving_size = Column(Float, default=100.0, nullable=False) # e.g. 100
    serving_unit = Column(String, default="g", nullable=False)   # 'g', 'ml', 'serving', 'piece', 'cup', 'oz'
    calories = Column(Float, nullable=False)                    # kcal per serving
    protein = Column(Float, default=0.0, nullable=False)        # grams
    carbs = Column(Float, default=0.0, nullable=False)          # grams
    fat = Column(Float, default=0.0, nullable=False)            # grams
    fiber = Column(Float, default=0.0, nullable=True)           # grams
    sugar = Column(Float, default=0.0, nullable=True)           # grams
    sodium = Column(Float, default=0.0, nullable=True)          # milligrams
    barcode = Column(String, nullable=True, index=True)
    is_verified = Column(Boolean, default=False, nullable=False)
    user_id = Column(Integer, ForeignKey("user.user_id", ondelete="SET NULL"), nullable=True) # None for verified system foods
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))


class Food_Log(Base):
    __tablename__ = "food_log"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("user.user_id", ondelete="CASCADE"), nullable=False)
    food_id = Column(Integer, ForeignKey("food_item.id", ondelete="SET NULL"), nullable=True)
    food_name = Column(String, nullable=False)
    meal_type = Column(String, nullable=False) # 'breakfast', 'lunch', 'dinner', 'snack'
    log_date = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    servings = Column(Float, default=1.0, nullable=False)
    serving_size = Column(Float, nullable=True)
    serving_unit = Column(String, nullable=True)
    calories = Column(Float, nullable=False)
    protein = Column(Float, default=0.0, nullable=False)
    carbs = Column(Float, default=0.0, nullable=False)
    fat = Column(Float, default=0.0, nullable=False)
    fiber = Column(Float, default=0.0, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    food_item = relationship("FoodItem")


class MealTemplate(Base):
    __tablename__ = "meal_template"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("user.user_id", ondelete="CASCADE"), nullable=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    meal_type = Column(String, default="any", nullable=False) # 'breakfast', 'lunch', 'dinner', 'snack', 'any'
    total_calories = Column(Float, default=0.0, nullable=False)
    total_protein = Column(Float, default=0.0, nullable=False)
    total_carbs = Column(Float, default=0.0, nullable=False)
    total_fat = Column(Float, default=0.0, nullable=False)
    is_custom = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    items = relationship(
        "MealTemplateItem",
        back_populates="meal_template",
        cascade="all, delete-orphan"
    )


class MealTemplateItem(Base):
    __tablename__ = "meal_template_item"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, autoincrement=True)
    meal_template_id = Column(Integer, ForeignKey("meal_template.id", ondelete="CASCADE"), nullable=False)
    food_id = Column(Integer, ForeignKey("food_item.id", ondelete="SET NULL"), nullable=True)
    food_name = Column(String, nullable=False)
    serving_size = Column(Float, default=100.0, nullable=False)
    serving_unit = Column(String, default="g", nullable=False)
    quantity = Column(Float, default=1.0, nullable=False) # Multiplier of serving size
    calories = Column(Float, default=0.0, nullable=False)
    protein = Column(Float, default=0.0, nullable=False)
    carbs = Column(Float, default=0.0, nullable=False)
    fat = Column(Float, default=0.0, nullable=False)

    meal_template = relationship("MealTemplate", back_populates="items")
    food_item = relationship("FoodItem")
