from typing import Optional
from sqlmodel import SQLModel, Field, Relationship
from pydantic import EmailStr
from datetime import datetime



# --------------------
# Workout Model
# --------------------
class Workout(SQLModel, table=True):
    """This is SQLModel of Workout Table which includes
        Pydantic and 
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    workout: Optional[str] = Field(default=None)  # Nullable field
    workout_desc: Optional[str] = Field(default=None)  # Nullable field
    type: Optional[str] = Field(default=None)  # Nullable field
    bodypart: Optional[str] = Field(default=None)  # Nullable field
    equipment: Optional[str] = Field(default=None)  # Nullable field
    level: Optional[str] = Field(default=None)  # Nullable field
    rating: Optional[float] = Field(default=None)  # Nullable field
    rating_desc: Optional[str] = Field(default=None)  # Nullable field
