from fastapi import APIRouter, HTTPException,BackgroundTasks,Depends
from services.email_sender import mail_engine
from fastapi.responses import JSONResponse
from sqlmodel import Session, select
from auth.otp import generate_otp, verify_otp
from models import users_model
from db.database import get_session


# Router instance
router = APIRouter(
    tags=["Verification"]
)

@router.post("/send-otp/")
async def send_otp(
    background_tasks: BackgroundTasks,
    request: users_model.OTPRequest,
    session: Session = Depends(get_session)
):
    existing_user = session.query(users_model.User).filter(
        (users_model.User.email == request.email)
    ).first()

    if existing_user:
        return {"Message":"Email has already taken"}
    else:
        otp = generate_otp(request.email)
        background_tasks.add_task(mail_engine.send_otp_email, request.email, otp)
        return {"message": "OTP sent successfully", "otp": otp}






@router.post("/verify-otp/")
async def send_otp(
    background_tasks: BackgroundTasks,
    request: users_model.OTPVerify,
    session: Session = Depends(get_session)
):
    existing_user_mail = session.query(users_model.User).filter(
        (users_model.User.email == request.email)
    ).first()
    result=verify_otp(email=request.email,otp=request.otp)

    if existing_user_mail:
        return JSONResponse(status_code=400, content={"detail": "User Email already exists"})
    elif result == True:
        new_user= users_model.User(
            email=request.email,
            is_verified=True,
            is_active=False,
        )
        session.add(new_user)
        session.commit()
        session.refresh(new_user)

        return JSONResponse(status_code=200, content={"Message":"OTP verified Successfully"})
    else:
        return result