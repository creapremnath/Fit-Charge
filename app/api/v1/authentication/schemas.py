from typing import Optional
from sqlmodel import SQLModel, Field, Relationship
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from enum import Enum
from datetime import datetime



class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)



class SignUp(BaseModel):
    username: str
    email: EmailStr
    password: str
    mobile: int
    gender: str
    date_of_birth: datetime
    age: int
    height_cm: float
    weight_kg: float
    chest_cm: float
    neck_cm: float
    biceps_cm: float
    hip_cm: float
    waist_cm: float
    region: str
    profile_pic_url: Optional[str] = None
    country_code: Optional[str] = None
    mobile: int



class Refresh_token(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    access_token: str
    token_type: str


class Token(Refresh_token):
    model_config = ConfigDict(from_attributes=True)
    
    refresh_token:str



class TokenData(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    user_id:Optional[int]=None
    username: Optional[str]=None
    role: Optional[int]=None



class OTPRequest(BaseModel):
    email: EmailStr


class OTPVerify(BaseModel):
    email: EmailStr
    otp:int