from fastapi import APIRouter, Depends
from api.v1.user.models import User
from core.database import get_session
from sqlmodel import Session
from api.v1.authentication.schemas import SignUp
from fastapi.responses import JSONResponse
from auth.utils import encrypt_password
router = APIRouter(
    tags=["Authentication"]
)

@router.post("/login")
def get_items():
    return {"Message":"Login routes"}


@router.post("/signup")
def sign_up(request: SignUp, session: Session = Depends(get_session)):
    existing_user = session.query(User).filter(User.email == request.email, User.is_verified == True).first()
    not_verified_user = session.query(User).filter(User.email == request.email, User.is_verified == False).first()
    if existing_user:
        return JSONResponse(status_code=400, content={"Message": "User Email already exists"})
    if not_verified_user:
        return JSONResponse(status_code=400, content={"Message": "Email Id not verified, please verify your email first"})
    existing_mobile_user = session.query(User).filter(User.mobile == request.mobile, User.is_active == True).first()
    if existing_mobile_user:
        return JSONResponse(status_code=400, content={"Message": "Mobile number already exists"})
        
    user = User(
        username=request.username,
        email=request.email,
        password=encrypt_password(request.password),
        gender=request.gender,
        date_of_birth=request.date_of_birth,
        age=request.age,
        height_cm=request.height_cm,
        weight_kg=request.weight_kg,
        chest_cm=request.chest_cm,
        neck_cm=request.neck_cm,
        biceps_cm=request.biceps_cm,
        hip_cm=request.hip_cm,
        waist_cm=request.waist_cm,
        profile_pic_url=request.profile_pic_url,
        country_code=request.country_code,
        mobile=request.mobile,
        is_active=True,
        region=request.region,
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return JSONResponse(status_code=200, content={"Message": "Signup successful", "user_id": user.user_id})


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