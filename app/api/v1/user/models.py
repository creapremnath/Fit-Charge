from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base


class User(Base):
    __tablename__ = "user"
    __table_args__ = {'extend_existing': True}

    user_id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String, nullable=True)
    email = Column(String, unique=True, nullable=True)
    password = Column(String, nullable=True)
    gender = Column(String, nullable=True)
    date_of_birth = Column(DateTime, nullable=True)
    is_details_completed = Column(Boolean, default=False, nullable=False)
    profile_pic_url = Column(String, nullable=True)
    country_code = Column(String, nullable=True)
    mobile = Column(String, nullable=True)
    role = Column(Integer, nullable=True, default=1)
    region = Column(String, nullable=True)
    country = Column(String, nullable=True)
    is_verified = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    settings = relationship(
        "UserSettings",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan"
    )

    user_logs = relationship(
        "User_log",
        back_populates="user",
        cascade="all, delete-orphan"
    )


class UserSettings(Base):
    __tablename__ = "user_settings"
    __table_args__ = {'extend_existing': True}

    user_settings_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("user.user_id", ondelete="CASCADE"), unique=True, nullable=False)
    weight_unit = Column(String, default="kg", nullable=False)       # 'kg' or 'lbs'
    height_unit = Column(String, default="cm", nullable=False)       # 'cm' or 'ft'
    distance_unit = Column(String, default="km", nullable=False)     # 'km' or 'miles'
    energy_unit = Column(String, default="kcal", nullable=False)     # 'kcal' or 'kj'
    theme = Column(String, default="dark", nullable=False)           # 'light', 'dark', 'system'
    notifications_enabled = Column(Boolean, default=True, nullable=False)
    workout_reminder_enabled = Column(Boolean, default=True, nullable=False)
    meal_reminder_enabled = Column(Boolean, default=True, nullable=False)
    rest_day_reminder_enabled = Column(Boolean, default=True, nullable=False)
    sound_effects_enabled = Column(Boolean, default=True, nullable=False)
    voice_coach_enabled = Column(Boolean, default=False, nullable=False)
    is_profile_public = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="settings")


class User_log(Base):
    __tablename__ = "user_log"
    __table_args__ = {'extend_existing': True}

    user_log_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("user.user_id", ondelete="CASCADE"), nullable=False)
    date_of_birth = Column(DateTime, nullable=True) # Kept for backward compatibility
    height_cm = Column(Float, nullable=True)
    weight_kg = Column(Float, nullable=True)
    body_fat_pct = Column(Float, nullable=True) # Body fat percentage
    chest_cm = Column(Float, nullable=True) 
    neck_cm = Column(Float, nullable=True)      # Neck measurement in cm
    biceps_cm = Column(Float, nullable=True)    # Biceps measurement in cm
    hip_cm = Column(Float, nullable=True)       # Hip measurement in cm
    waist_cm = Column(Float, nullable=True)
    thighs_cm = Column(Float, nullable=True)    # Thighs measurement in cm
    calves_cm = Column(Float, nullable=True)    # Calves measurement in cm
    shoulders_cm = Column(Float, nullable=True) # Shoulders measurement in cm
    notes = Column(String, nullable=True)       # Measurement notes or progress comments
    log_date = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="user_logs")