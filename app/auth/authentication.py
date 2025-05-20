from fastapi import APIRouter, Depends, status, HTTPException, Response, Query, Request,BackgroundTasks
from typing import List
from sqlmodel import Session, select
from db.database import get_session
from models import users_model
from fc_logger import get_logger
from auth.utils import verify_password,encrypt_password
from auth.oauth2 import create_access_token,create_refresh_token
from auth.otp import generate_otp, verify_otp
from services.email_sender import mail_engine

from slowapi import Limiter
from slowapi.util import get_remote_address

# Initialize the Limiter with Redis or default storage
limiter = Limiter(key_func=get_remote_address)

# Initialize logger
logger = get_logger("auth.authentication")


def normalize_email(email: str) -> str:
    return email.strip().lower()


# Router instance
router = APIRouter(
    tags=["Authentication"]
)
from fastapi import HTTPException, status

@router.post('/login', response_model=users_model.Token)
def login(user_credentials: users_model.Login, db: Session = Depends(get_session)):
    """Login as a user, return minimal token payload with user_id and username."""

    # Normalize email to avoid case mismatch
    email = user_credentials.email.strip().lower()

    # Query user
    user = (
        db.query(users_model.User)
        .filter(users_model.User.email == email)
        .first()
    )


    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='User not found')

    if not verify_password(user_credentials.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid Credentials')

    # Create minimal tokens
    access_token = create_access_token(data={
        "user_id": user.user_id,
        "username": user.username,
        "token_type": "access_token"# adjust to .username if that’s your actual field
    })

    refresh_token = create_refresh_token(data={
        "user_id": user.user_id,
        "username": user.username,
        "token_type":"refresh_token"
    })

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }



@router.post("/sign-up", status_code=status.HTTP_200_OK)
def sign_up(SignUpData: users_model.SignUp, session: Session = Depends(get_session)):
    user_email = normalize_email(SignUpData.email)
    user_mobile = str(SignUpData.mobile)

    # 1. Check if mobile is already in use by any active user
    existing_mobile_user = session.query(users_model.User).filter(
        users_model.User.mobile == user_mobile,
        users_model.User.is_active == True
    ).first()

    if existing_mobile_user:
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail="Mobile number is already in use by an active user."
        )

    # 2. Find existing user with same email
    existing_user = session.query(users_model.User).filter(
        users_model.User.email == user_email
    ).first()

    if existing_user:
        if existing_user.is_verified and not existing_user.is_active and not existing_user.username:
            # ✅ Update allowed
            existing_user.username = SignUpData.username
            existing_user.mobile = user_mobile
            existing_user.password = encrypt_password(SignUpData.password)
            existing_user.is_active = True

            session.commit()
            return {"message": "User profile completed successfully."}
        elif not existing_user.is_verified:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email is not verified yet."
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User with this email already exists."
            )
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No such verified user found to update."
        )