from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float
from sqlalchemy.orm import declarative_base
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = "user"
    __table_args__ = {'extend_existing': True}

    user_id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String, nullable=True)
    email = Column(String, unique=True, nullable=True)
    password = Column(String, nullable=True)
    gender = Column(String, nullable=True)
    date_of_birth = Column(DateTime, nullable=True)
    age = Column(Integer, nullable=True)
    height_cm = Column(Float, nullable=True)
    weight_kg = Column(Float, nullable=True)
    chest_cm = Column(Float, nullable=True) 
    neck_cm = Column(Float, nullable=True)      # Neck measurement in cm
    biceps_cm = Column(Float, nullable=True)      # Biceps measurement in cm
    hip_cm = Column(Float, nullable=True)         # Hip measurement in cm
    waist_cm = Column(Float, nullable=True)       # Waist measurement in cm
    profile_pic_url = Column(String, nullable=True)
    country_code = Column(String, nullable=True)
    mobile = Column(String, nullable=True)
    region = Column(String, nullable=True)
    is_verified = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
