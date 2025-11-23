from fastapi import APIRouter, Depends, status, HTTPException, Response, Query, Request,UploadFile, File, Depends, Body
from typing import List
from sqlmodel import Session, select
from db.database import get_session
from models import users_model
from fc_logger import get_logger
from auth.utils import encrypt_password
from auth.oauth2 import get_current_user
from services.formula import Bodyformula
import os
import shutil
import uuid

from slowapi import Limiter
from slowapi.util import get_remote_address

# Initialize the Limiter with Redis or default storage
limiter = Limiter(key_func=get_remote_address)

# Initialize logger
logger = get_logger("routers.profile")


# Router instance
router = APIRouter(
    tags=["Profile"]
)

ALLOWED_EXTENSIONS = {"jpeg", "jpg", "png"}

BaseURL="http://localhost:8000"

@router.post("/upload-image/")
async def upload_image(
    image: UploadFile = File(...),
    session: Session = Depends(get_session),
    current_user: users_model.TokenData = Depends(get_current_user)
):
    # Validate extension
    ext = image.filename.split(".")[-1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Only jpeg, jpg, png files are allowed.")

    # Get user profile
    profile = session.exec(
        select(users_model.Profile).where(users_model.Profile.user_id == current_user.user_id)
    ).first()

    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found for the current user")

    # Delete old image if exists
    if profile.image_url:
        old_path = profile.image_url.replace("/static/", "uploads/")
        if os.path.isfile(old_path):
            try:
                os.remove(old_path)
            except Exception as e:
                logger.warning(f"Failed to delete old image: {e}")

    # Save new image
    unique_filename = f"{uuid.uuid4()}.{ext}"
    upload_folder = "uploads/"
    os.makedirs(upload_folder, exist_ok=True)
    file_location = os.path.join(upload_folder, unique_filename)

    with open(file_location, "wb") as file_object:
        file_object.write(await image.read())

    # Store public URL path
    public_url = f"/static/{unique_filename}"
    profile.image_url = public_url

    session.add(profile)
    session.commit()
    session.refresh(profile)

    return {
        "message": "Image uploaded and profile updated",
        "image_url": f"{BaseURL}{public_url}"
    }



@router.post("/profile/", response_model=users_model.Profile, status_code=status.HTTP_201_CREATED)
def create_profile(
    profile_data: users_model.BodyProfile,
    session: Session = Depends(get_session),
    current_user: users_model.TokenData = Depends(get_current_user),
):
    # 1. Check if profile already exists for this user
    existing_profile = session.query(users_model.Profile).filter_by(user_id=current_user.user_id).first()
    if existing_profile:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Profile already exists for this user."
        )

    # 2. Calculate BMR
    bmr = Bodyformula.bmr(
        weight_kg=profile_data.current_weight,
        height=profile_data.height,
        age=profile_data.age,
        gender=profile_data.gender.value,
    )

    # 3. Calculate BMI
    bmi = Bodyformula.bmi(weight=profile_data.current_weight, height=profile_data.height)
    if 'value' not in bmi:
        raise ValueError("Invalid BMI calculation")

    # 4. Calculate TDEE
    maintainence_calories = Bodyformula.tdee(bmr=bmr, activity_level=profile_data.activity.value)

    # 5. Calculate body fat
    bodyfat = Bodyformula.bodyfat(
        waist=profile_data.waist,
        neck=profile_data.neck,
        height=profile_data.height,
        gender=profile_data.gender.value,
        hips=profile_data.hip or 0,
    )

    # 6. Create and store profile
    new_profile = users_model.Profile(
        image_url=profile_data.image_url,
        age=profile_data.age,
        gender=profile_data.gender.value,
        height=profile_data.height,
        neck=profile_data.neck,
        waist=profile_data.waist,
        hip=profile_data.hip,
        current_weight=profile_data.current_weight,
        activity=profile_data.activity.value if profile_data.activity else None,
        goal=profile_data.goal.value if profile_data.goal else None,
        goal_weight=profile_data.goal_weight,
        bmi=bmi['value'],
        bmr=bmr,
        maintainence_calories=maintainence_calories,
        bodyfat=bodyfat,
        user_id=current_user.user_id,
    )

    session.add(new_profile)
    session.commit()
    session.refresh(new_profile)

    return new_profile


@router.put("/profile/", response_model=users_model.Profile, status_code=status.HTTP_200_OK)
def update_profile(
    profile_data: users_model.BodyProfile,
    session: Session = Depends(get_session),
    current_user: users_model.TokenData = Depends(get_current_user),
):
    profile = session.query(users_model.Profile).filter_by(user_id=current_user.user_id).first()

    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No profile found to update."
        )

    # Recalculate values
    bmr = Bodyformula.bmr(
        weight_kg=profile_data.current_weight,
        height=profile_data.height,
        age=profile_data.age,
        gender=profile_data.gender.value,
    )

    bmi = Bodyformula.bmi(weight=profile_data.current_weight, height=profile_data.height)
    if 'value' not in bmi:
        raise HTTPException(status_code=422, detail="BMI calculation failed")

    maintainence_calories = Bodyformula.tdee(bmr=bmr, activity_level=profile_data.activity.value)

    try:
        bodyfat = Bodyformula.bodyfat(
            waist=profile_data.waist,
            neck=profile_data.neck,
            height=profile_data.height,
            gender=profile_data.gender.value,
            hips=profile_data.hip or 0,
        )
    except HTTPException as e:
        raise e
    except Exception:
        raise HTTPException(status_code=422, detail="Body fat calculation error")

    if not isinstance(bodyfat, float):
        raise HTTPException(status_code=422, detail="Invalid body fat result")

    # Update fields
    profile.image_url = profile_data.image_url
    profile.age = profile_data.age
    profile.gender = profile_data.gender.value
    profile.height = profile_data.height
    profile.neck = profile_data.neck
    profile.waist = profile_data.waist
    profile.hip = profile_data.hip
    profile.current_weight = profile_data.current_weight
    profile.activity = getattr(profile_data.activity, "value", None)
    profile.goal = getattr(profile_data.goal, "value", None)
    profile.goal_weight = profile_data.goal_weight
    profile.bmi = bmi["value"]
    profile.bmr = bmr
    profile.maintainence_calories = maintainence_calories
    profile.bodyfat = bodyfat

    session.commit()
    session.refresh(profile)

    return profile


@router.delete("/profile/", status_code=status.HTTP_204_NO_CONTENT)
def delete_profile(
    session: Session = Depends(get_session),
    current_user: users_model.TokenData = Depends(get_current_user),
):
    profile = session.query(users_model.Profile).filter_by(user_id=current_user.user_id).first()

    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found."
        )

    session.delete(profile)
    session.commit()
