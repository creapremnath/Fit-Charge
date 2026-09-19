from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


# ==========================================
# User Settings Schemas
# ==========================================

class UserSettingsBase(BaseModel):
    weight_unit: Optional[str] = "kg"
    height_unit: Optional[str] = "cm"
    distance_unit: Optional[str] = "km"
    energy_unit: Optional[str] = "kcal"
    theme: Optional[str] = "dark"
    notifications_enabled: Optional[bool] = True
    workout_reminder_enabled: Optional[bool] = True
    meal_reminder_enabled: Optional[bool] = True
    rest_day_reminder_enabled: Optional[bool] = True
    sound_effects_enabled: Optional[bool] = True
    voice_coach_enabled: Optional[bool] = False
    is_profile_public: Optional[bool] = False


class UserSettingsUpdate(BaseModel):
    weight_unit: Optional[str] = None
    height_unit: Optional[str] = None
    distance_unit: Optional[str] = None
    energy_unit: Optional[str] = None
    theme: Optional[str] = None
    notifications_enabled: Optional[bool] = None
    workout_reminder_enabled: Optional[bool] = None
    meal_reminder_enabled: Optional[bool] = None
    rest_day_reminder_enabled: Optional[bool] = None
    sound_effects_enabled: Optional[bool] = None
    voice_coach_enabled: Optional[bool] = None
    is_profile_public: Optional[bool] = None


class UserSettingsResponse(UserSettingsBase):
    user_settings_id: int
    user_id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


# ==========================================
# User Log / Measurement Schemas
# ==========================================

class UserLogCreate(BaseModel):
    height_cm: Optional[float] = None
    weight_kg: Optional[float] = None
    body_fat_pct: Optional[float] = None
    chest_cm: Optional[float] = None
    neck_cm: Optional[float] = None
    biceps_cm: Optional[float] = None
    hip_cm: Optional[float] = None
    waist_cm: Optional[float] = None
    thighs_cm: Optional[float] = None
    calves_cm: Optional[float] = None
    shoulders_cm: Optional[float] = None
    notes: Optional[str] = None
    log_date: Optional[datetime] = None


class UserLogUpdate(BaseModel):
    height_cm: Optional[float] = None
    weight_kg: Optional[float] = None
    body_fat_pct: Optional[float] = None
    chest_cm: Optional[float] = None
    neck_cm: Optional[float] = None
    biceps_cm: Optional[float] = None
    hip_cm: Optional[float] = None
    waist_cm: Optional[float] = None
    thighs_cm: Optional[float] = None
    calves_cm: Optional[float] = None
    shoulders_cm: Optional[float] = None
    notes: Optional[str] = None
    log_date: Optional[datetime] = None


class UserLogResponse(BaseModel):
    user_log_id: int
    user_id: int
    height_cm: Optional[float] = None
    weight_kg: Optional[float] = None
    body_fat_pct: Optional[float] = None
    chest_cm: Optional[float] = None
    neck_cm: Optional[float] = None
    biceps_cm: Optional[float] = None
    hip_cm: Optional[float] = None
    waist_cm: Optional[float] = None
    thighs_cm: Optional[float] = None
    calves_cm: Optional[float] = None
    shoulders_cm: Optional[float] = None
    notes: Optional[str] = None
    log_date: Optional[datetime] = None
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


# ==========================================
# User Onboarding & Profile Schemas
# ==========================================

class UserOnboardingRequest(BaseModel):
    gender: Optional[str] = None
    date_of_birth: Optional[datetime] = None
    height_cm: Optional[float] = None
    weight_kg: Optional[float] = None
    target_weight_kg: Optional[float] = None
    fitness_goal: Optional[str] = None          # 'Lose Fat', 'Build Muscle', 'Stay Fit', 'Gain Strength'
    workout_experience: Optional[str] = None    # 'Beginner', 'Intermediate', 'Advanced'
    workout_preference: Optional[str] = None    # 'Gym', 'Home', 'Both'
    workout_days_per_week: Optional[str] = None # '2-3', '4-5', '6+'
    height_unit: Optional[str] = "cm"
    weight_unit: Optional[str] = "kg"
    chest_cm: Optional[float] = None
    waist_cm: Optional[float] = None
    hip_cm: Optional[float] = None
    biceps_cm: Optional[float] = None
    neck_cm: Optional[float] = None


class UserProfileUpdate(BaseModel):
    username: Optional[str] = None
    gender: Optional[str] = None
    date_of_birth: Optional[datetime] = None
    profile_pic_url: Optional[str] = None
    country_code: Optional[str] = None
    mobile: Optional[str] = None
    region: Optional[str] = None
    country: Optional[str] = None
    is_details_completed: Optional[bool] = None
