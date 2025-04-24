from typing import Optional
from sqlmodel import SQLModel, Field, Relationship
from pydantic import EmailStr
from datetime import datetime


class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str
    email: EmailStr
    password: str
    mobile: str
    created_at: datetime = Field(default_factory=datetime.utcnow)


class UserRead(SQLModel):
    id: int
    username: str
    email: str
    mobile: str

