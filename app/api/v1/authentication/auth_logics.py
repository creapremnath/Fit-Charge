from fastapi import APIRouter, Depends
from pydantic import Json
from app.api.v1.user.models import User
from app.core.database import get_session
from sqlalchemy.orm import Session
from app.api.v1.authentication.schemas import SignUp
from fastapi.responses import JSONResponse
from app.auth.utils import encrypt_password
router = APIRouter(
    tags=["Authentication"]
)

@router.post("/login")
def get_items():
    return {"Message":"Login routes"}


@router.post("/signup")
def sign_up(request: SignUp, session: Session = Depends(get_session)):
    
    valid_user = session.query(User).filter(User.email == request.email).first()
    existing_mobile = (
        session.query(User)
        .filter(User.mobile == str(request.mobile), User.is_active == True)
        .first()
    )

    # Email is not pre-verified
    if not valid_user:
        return JSONResponse(
            status_code=400,
            content={"Message": "Verified Email ID not found"}
        )

    # User already created + active
    elif valid_user.is_active == True:
        return JSONResponse(
            status_code=400,
            content={"Message": "User with this Email ID already exists"}
        )

    # Mobile number already linked to another active user
    elif existing_mobile:
        return JSONResponse(
            status_code=400,
            content={"Message": "User with this mobile already exists"}
        )

    # Email verified → Update the existing user instead of creating a new one
    elif valid_user.is_verified == True:
        valid_user.username = request.username
        valid_user.password = encrypt_password(request.password)
        valid_user.gender = request.gender
        valid_user.date_of_birth = request.date_of_birth
        valid_user.age = request.age
        valid_user.height_cm = request.height_cm
        valid_user.weight_kg = request.weight_kg
        valid_user.chest_cm = request.chest_cm
        valid_user.neck_cm = request.neck_cm
        valid_user.biceps_cm = request.biceps_cm
        valid_user.hip_cm = request.hip_cm
        valid_user.waist_cm = request.waist_cm
        valid_user.profile_pic_url = request.profile_pic_url
        valid_user.country_code = request.country_code
        valid_user.mobile = request.mobile
        valid_user.is_active = True
        valid_user.region = request.region

        session.commit()
        session.refresh(valid_user)

        return JSONResponse(
            status_code=200,
            content={"Message": "Signup successful", "user_id": valid_user.user_id}
        )

    # Email exists but not verified
    else:
        return JSONResponse(
            status_code=400,
            content={"Message": "Email ID not verified. Please verify before signing up."}
        )



@router.post("/logout")
def logout():
    return {"Message":"Logout routes"}


@router.post("/refresh-token")
def refresh_token():
    return {"Message":"Refresh token routes"}


@router.post("/forgot-password")
def forgot_password():
    return {"Message":"Forgot password routes"}

@router.get("/reset-password")
def reset_password():
    return {"Message":"Reset password routes"}