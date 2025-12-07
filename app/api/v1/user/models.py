from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float
from sqlalchemy.orm import declarative_base
from datetime import datetime
from sqlalchemy.orm import relationship
from sqlalchemy import ForeignKey

Base = declarative_base()

class User(Base):
    __tablename__ = "user"
    __table_args__ = {'extend_existing': True}

    user_id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String, nullable=True)
    email = Column(String, unique=True, nullable=True)
    password = Column(String, nullable=True)
    gender = Column(String, nullable=True)
    profile_pic_url = Column(String, nullable=True)
    country_code = Column(String, nullable=True)
    mobile = Column(String, nullable=True)
    role = Column(Integer,nullable=True, default=1)
    region = Column(String, nullable=True)
    country = Column(String, nullable=True)
    is_verified = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user_logs = relationship(
        "User_log",
        back_populates="user",
        cascade="all, delete-orphan"
    )


class User_log(Base):
    __tablename__ = "user_log"
    __table_args__ = {'extend_existing': True}

    user_log_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("user.user_id", ondelete="CASCADE"), nullable=False)
    date_of_birth = Column(DateTime, nullable=True)
    height_cm = Column(Float, nullable=True)
    weight_kg = Column(Float, nullable=True)
    chest_cm = Column(Float, nullable=True) 
    neck_cm = Column(Float, nullable=True)      # Neck measurement in cm
    biceps_cm = Column(Float, nullable=True)    # Biceps measurement in cm
    hip_cm = Column(Float, nullable=True)       # Hip measurement in cm
    waist_cm = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="user_logs")