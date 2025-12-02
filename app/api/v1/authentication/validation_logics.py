from fastapi import APIRouter, Depends, BackgroundTasks, HTTPException
from api.v1.authentication.schemas import OTPRequest, OTPVerify
from api.v1.user.models import User
from core.database import get_session
from auth.otp import generate_otp, verify_otp as otp_verify_func
from sqlmodel import Session
from fastapi.responses import JSONResponse
from services.email_sender import mail_engine  # Import mail engine

router = APIRouter(
    tags=["Validation"]
)

@router.post("/send-otp")
def send_otp(
    request: OTPRequest, 
    session: Session = Depends(get_session), 
    background_tasks: BackgroundTasks = None
):
    existing_user = session.query(User).filter(User.email == request.email).first()
    if existing_user:
        return JSONResponse(status_code=400, content={"Message": "Email has already been taken"})
    otp = generate_otp(request.email)
    if background_tasks is not None:
        background_tasks.add_task(mail_engine.send_otp_email, request.email, otp)
    else:
        # fallback: send immediately if no background_tasks provided (for sync use/testing)
        mail_engine.send_otp_email(request.email, otp)
    return {"Message": "OTP sent successfully", "otp": otp}

@router.post("/verify-otp")
def verify_otp(request: OTPVerify, session: Session = Depends(get_session)):
    existing_user_mail = session.query(User).filter(User.email == request.email).first()
    if existing_user_mail:
        return JSONResponse(status_code=400, content={"Message": "User Email already exists"})
    
    result = otp_verify_func(email=request.email, otp=request.otp)
    if result is True:
        new_user = User(
            email=request.email,
            is_verified=True,
            is_active=False,
        )
        session.add(new_user)
        session.commit()
        session.refresh(new_user)
        return JSONResponse(status_code=200, content={"Message": "OTP verified Successfully"})
    else:
        return JSONResponse(status_code=400, content={"Message": str(result)})

