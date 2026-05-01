from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_session
from app.auth.oauth2 import get_current_user
from app.api.v1.authentication.schemas import TokenData
from .models import User, User_log
router = APIRouter()

@router.get("/user")
def get_items(current_user: TokenData = Depends(get_current_user)):
    return {"Message":"user routes", "current_user": current_user}


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

    return {
        "Message": "User detail fetched successfully",
        "data": {
            "user_id": user.user_id,
            "username": user.username,
            "email": user.email,
            "gender": user.gender,
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
            "latest_body_metrics": (
                {
                    "date_of_birth": latest_user_log.date_of_birth,
                    "height_cm": latest_user_log.height_cm,
                    "weight_kg": latest_user_log.weight_kg,
                    "chest_cm": latest_user_log.chest_cm,
                    "neck_cm": latest_user_log.neck_cm,
                    "biceps_cm": latest_user_log.biceps_cm,
                    "hip_cm": latest_user_log.hip_cm,
                    "waist_cm": latest_user_log.waist_cm,
                    "created_at": latest_user_log.created_at,
                }
                if latest_user_log
                else None
            ),
        },
    }

