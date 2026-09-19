from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from app.core.database import get_session
from app.auth.oauth2 import get_current_user
from app.api.v1.authentication.schemas import TokenData
from app.services.cloudinary_service import upload_profile_image
from .models import User, User_log, UserSettings
from .schemas import UserOnboardingRequest, UserProfileUpdate

router = APIRouter()


@router.get("/user")
def get_items(current_user: TokenData = Depends(get_current_user)):
    return {"Message": "user routes", "current_user": current_user}


@router.get("/detail")
def get_user_detail(
    current_user: TokenData = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    user = (
        session.query(User)
        .filter(User.user_id == current_user.user_id, User.is_active == True)
        .first()
    )

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    latest_user_log = (
        session.query(User_log)
        .filter(User_log.user_id == current_user.user_id)
        .order_by(User_log.created_at.desc())
        .first()
    )

    user_settings = (
        session.query(UserSettings)
        .filter(UserSettings.user_id == current_user.user_id)
        .first()
    )

    return {
        "Message": "User detail fetched successfully",
        "data": {
            "user_id": user.user_id,
            "username": user.username,
            "email": user.email,
            "gender": user.gender,
            "date_of_birth": user.date_of_birth,
            "is_details_completed": bool(user.is_details_completed),
            "profile_pic_url": user.profile_pic_url,
            "country_code": user.country_code,
            "mobile": user.mobile,
            "role": user.role,
            "region": user.region,
            "country": user.country,
            "is_verified": user.is_verified,
            "is_active": user.is_active,
            "created_at": user.created_at,
            "updated_at": user.updated_at,
            "settings": (
                {
                    "user_settings_id": user_settings.user_settings_id,
                    "weight_unit": user_settings.weight_unit,
                    "height_unit": user_settings.height_unit,
                    "distance_unit": user_settings.distance_unit,
                    "energy_unit": user_settings.energy_unit,
                    "theme": user_settings.theme,
                    "notifications_enabled": user_settings.notifications_enabled,
                    "workout_reminder_enabled": user_settings.workout_reminder_enabled,
                    "meal_reminder_enabled": user_settings.meal_reminder_enabled,
                    "rest_day_reminder_enabled": user_settings.rest_day_reminder_enabled,
                    "sound_effects_enabled": user_settings.sound_effects_enabled,
                    "voice_coach_enabled": user_settings.voice_coach_enabled,
                    "is_profile_public": user_settings.is_profile_public,
                }
                if user_settings
                else None
            ),
            "latest_body_metrics": (
                {
                    "height_cm": latest_user_log.height_cm,
                    "weight_kg": latest_user_log.weight_kg,
                    "body_fat_pct": latest_user_log.body_fat_pct,
                    "chest_cm": latest_user_log.chest_cm,
                    "neck_cm": latest_user_log.neck_cm,
                    "biceps_cm": latest_user_log.biceps_cm,
                    "hip_cm": latest_user_log.hip_cm,
                    "waist_cm": latest_user_log.waist_cm,
                    "thighs_cm": latest_user_log.thighs_cm,
                    "calves_cm": latest_user_log.calves_cm,
                    "shoulders_cm": latest_user_log.shoulders_cm,
                    "notes": latest_user_log.notes,
                    "created_at": latest_user_log.created_at,
                }
                if latest_user_log
                else None
            ),
        },
    }


@router.post("/onboard")
def complete_onboarding(
    payload: UserOnboardingRequest,
    current_user: TokenData = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Save initial user onboarding details (DOB, gender, height, weight, units, preferences),
    create initial measurement log, initialize user settings, and mark details as completed.
    """
    user = session.query(User).filter(User.user_id == current_user.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Update user table fields
    if payload.gender:
        user.gender = payload.gender
    if payload.date_of_birth:
        user.date_of_birth = payload.date_of_birth
    
    user.is_details_completed = True
    user.updated_at = datetime.now(timezone.utc)

    # Update or create user settings
    settings = session.query(UserSettings).filter(UserSettings.user_id == current_user.user_id).first()
    if not settings:
        settings = UserSettings(user_id=current_user.user_id)
        session.add(settings)
    
    if payload.height_unit:
        settings.height_unit = payload.height_unit
    if payload.weight_unit:
        settings.weight_unit = payload.weight_unit

    # Record initial measurement log if height or weight provided
    if payload.height_cm is not None or payload.weight_kg is not None:
        initial_log = User_log(
            user_id=current_user.user_id,
            height_cm=payload.height_cm,
            weight_kg=payload.weight_kg,
            chest_cm=payload.chest_cm,
            waist_cm=payload.waist_cm,
            hip_cm=payload.hip_cm,
            biceps_cm=payload.biceps_cm,
            neck_cm=payload.neck_cm,
            notes=f"Initial Onboarding - Goal: {payload.fitness_goal or 'N/A'}, Experience: {payload.workout_experience or 'N/A'}",
            log_date=datetime.now(timezone.utc)
        )
        session.add(initial_log)

    session.commit()
    session.refresh(user)

    return {
        "status_code": 200,
        "message": "User onboarding completed successfully",
        "data": {
            "user_id": user.user_id,
            "username": user.username,
            "email": user.email,
            "gender": user.gender,
            "date_of_birth": user.date_of_birth,
            "is_details_completed": user.is_details_completed,
        }
    }


@router.patch("/profile")
def update_user_profile(
    payload: UserProfileUpdate,
    current_user: TokenData = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Update core user profile information.
    """
    user = session.query(User).filter(User.user_id == current_user.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if value is not None:
            setattr(user, field, value)

    user.updated_at = datetime.now(timezone.utc)
    session.commit()
    session.refresh(user)

    return {
        "status_code": 200,
        "message": "User profile updated successfully",
        "data": {
            "user_id": user.user_id,
            "username": user.username,
            "email": user.email,
            "gender": user.gender,
            "date_of_birth": user.date_of_birth,
            "is_details_completed": user.is_details_completed,
            "profile_pic_url": user.profile_pic_url,
            "mobile": user.mobile,
            "region": user.region,
            "country": user.country,
        }
    }


@router.get("/all-users")
def get_all_users(
    current_user: TokenData = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    users = (
        session.query(User)
        .filter(User.is_active == True)
        .order_by(User.created_at.desc())
        .all()
    )

    return {
        "Message": "Users fetched successfully",
        "data": [
            {
                "user_id": user.user_id,
                "username": user.username,
                "email": user.email,
                "profile_pic_url": user.profile_pic_url,
                "region": user.region,
            }
            for user in users
        ],
    }


@router.post("/upload-profile-pic")
async def upload_user_profile_pic(
    file: UploadFile = File(...),
    current_user: TokenData = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """
    Upload a new profile picture to Cloudinary and update the user's profile_pic_url.
    """
    user = session.query(User).filter(User.user_id == current_user.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    file_bytes = await file.read()
    if not file_bytes:
        raise HTTPException(status_code=400, detail="Empty file uploaded")

    content_type = file.content_type or "image/jpeg"
    upload_result = upload_profile_image(
        file_bytes=file_bytes,
        content_type=content_type,
        user_id=user.user_id,
        filename=file.filename or "avatar.jpg",
    )

    user.profile_pic_url = upload_result["secure_url"]
    user.updated_at = datetime.now(timezone.utc)
    session.commit()
    session.refresh(user)

    return {
        "status_code": 200,
        "message": "Profile picture uploaded successfully",
        "data": {
            "user_id": user.user_id,
            "username": user.username,
            "profile_pic_url": user.profile_pic_url,
            "cloudinary_details": upload_result,
        },
    }

