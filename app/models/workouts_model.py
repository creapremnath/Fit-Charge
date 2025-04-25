from typing import Optional
from sqlmodel import SQLModel, Field, Relationship
from pydantic import EmailStr
from datetime import datetime


class Workout(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    workout: Optional[str] = Field(default=None)  # Nullable field
    workout_desc: Optional[str] = Field(default=None)  # Nullable field
    type: Optional[str] = Field(default=None)  # Nullable field
    bodypart: Optional[str] = Field(default=None)  # Nullable field
    equipment: Optional[str] = Field(default=None)  # Nullable field
    level: Optional[str] = Field(default=None)  # Nullable field
    rating: Optional[float] = Field(default=None)  # Nullable field
    rating_desc: Optional[str] = Field(default=None)  # Nullable field
