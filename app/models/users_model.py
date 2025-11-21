"""
Private License (fitcharge)

This script is privately licensed and confidential. It is not intended for
public distribution or use without explicit permission from the owner.

All rights reserved (c) 2025.
"""

__author__ = "Premnath Palanichamy, Karthikeyan Kabilan"
__collaborators__ = "Premnath Palanichamy <creativepremnath@gmail.com>, Karthikeyan Kabilan <karthik.codes.dev@gmail.com>"
__copyright__ = "Copyright 2025, fitcharge"
__license__ = "Refer Terms and Conditions"
__version__ = "1.0"
__maintainer__ = "Premnath Palanichamy"
__status__ = "Development"
__desc__ = "Fitcharge User and Profile Models"


from typing import Optional
from sqlmodel import SQLModel, Field, Relationship
from pydantic import EmailStr,BaseModel,conint,confloat
from enum import Enum
from datetime import datetime



# --------------------
# User Model
# --------------------
class User(SQLModel, table=True):
    user_id: Optional[int] = Field(default=None, primary_key=True)
    username: Optional[str]
    email: Optional[EmailStr]
    password: Optional[str]
    mobile: Optional[str]
    is_verified:Optional[bool]
    is_active:Optional[bool]
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationship: one user has one profile
    profile: Optional["Profile"] = Relationship(back_populates="user")


class SignUp(BaseModel):
    username: str
    email: EmailStr
    password: str
    mobile: int



class UserRead(SQLModel):
    user_id: int
    username: str
    email: str
    mobile: str



class Login(SQLModel):
    email:str
    password:str

# --------------------
# Profile Model
# --------------------
class Profile(SQLModel, table=True):
    profile_id: Optional[int] = Field(default=None, primary_key=True)
    image_url: Optional[str] = None
    age:int
    gender:str
    height:float
    neck:Optional[float] = None
    waist:Optional[float] = None
    hip:Optional[float] = None
    current_weight:float
    activity:Optional[str] = None
    goal:Optional[str] = None
    goal_weight:Optional[float] = None
    bmi:float = None
    bmr:float = None
    maintainence_calories:int
    suggested_weight:Optional[str]= None
    bodyfat:Optional[float] = None

    # Foreign Key
    user_id: int = Field(foreign_key="user.user_id")

    # Relationship
    user: Optional[User] = Relationship(back_populates="profile")



########################

class GenderEnum(str, Enum):
    male = "male"
    female = "female"

class ActivityEnum(str, Enum):
    sedentary = "sedentary"
    light = "light"
    moderate = "moderate"
    very_active = "very_active"
    extra_active = "extra_active"

class GoalEnum(str, Enum):
    weight_loss = "weight_loss"
    weight_gain = "weight_gain"
    maintenance = "maintenance"

########################


class BodyProfile(BaseModel):
    image_url: Optional[str] = None

    age: conint(gt=0)  # Age must be a positive integer
    gender: GenderEnum

    height: confloat(gt=0)  # Height in cm, must be > 0
    neck: Optional[confloat(gt=0)] = None  # Must be > 0 if provided
    waist: Optional[confloat(gt=0)] = None
    hip: Optional[confloat(gt=0)] = None

    current_weight: confloat(gt=0)  # Must be > 0

    activity: Optional[ActivityEnum] = None
    goal: Optional[GoalEnum] = None
    goal_weight: Optional[confloat(gt=0)] = None  # Must be > 0 if provided





class Refresh_token(BaseModel):
    access_token: str
    token_type: str

    class Config:
        from_attributes = True

class Token(Refresh_token):
    refresh_token:str
    class Config:
        from_attributes = True


class TokenData(BaseModel):
    user_id:Optional[int]=None
    username: Optional[str]=None


    class Config:
        from_attributes = True



class OTPRequest(BaseModel):
    email: EmailStr


class OTPVerify(BaseModel):
    email: EmailStr
    otp:int

class BodyProfilePatch(BaseModel):
    image_url: Optional[str]
    age: Optional[int]
    gender: Optional[GenderEnum]
    height: Optional[float]
    neck: Optional[float]
    waist: Optional[float]
    hip: Optional[float]
    current_weight: Optional[float]
    activity: Optional[ActivityEnum]
    goal: Optional[GoalEnum]
    goal_weight: Optional[float]