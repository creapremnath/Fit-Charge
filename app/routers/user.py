from fastapi import APIRouter, Depends, status, HTTPException, Response, Query, Request
from typing import List
from sqlmodel import Session, select
from db.database import get_session
from models import users_model
from fc_logger import get_logger
from auth.utils import encrypt_password

from slowapi import Limiter
from slowapi.util import get_remote_address

# Initialize the Limiter with Redis or default storage
limiter = Limiter(key_func=get_remote_address)

# Initialize logger
logger = get_logger("routers.user")

# Router instance
router = APIRouter(
    tags=["Users"]
)

@router.post("/users/", response_model=users_model.UserRead, status_code=status.HTTP_201_CREATED)
def create_user(user: users_model.User, session: Session = Depends(get_session)):
    user.password=encrypt_password(user.password)
    session.add(user)
    session.commit()
    session.refresh(user)
    logger.info("Db_inserted")
    return user


# If you REALLY need all users (with safety measures)
@router.get("/users/all", response_model=List[users_model.UserRead])
@limiter.limit("5/minute")  # Apply rate limiting
def list_all_users(request: Request, session: Session = Depends(get_session)):
    """
    Fetches all users from the database. Use with caution in large datasets.
    """
    try:
        all_users = session.exec(select(users_model.User)).all()
        logger.info(f"Fetched {len(all_users)} users from database")
        return all_users
    except Exception as e:
        logger.error(f"Error fetching all users: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching all users: {str(e)}"
        )


@router.post("/profile", response_model=users_model.Profile, status_code=status.HTTP_201_CREATED)
def create_profile(profile: users_model.Profile, session: Session = Depends(get_session)):
    session.add(profile)
    session.commit()
    session.refresh(profile)
    logger.info("Profile Added")
    return profile

@router.get("/profile", response_model=List[users_model.Profile])
def list_profile(request: Request, session: Session = Depends(get_session)):
    """list all profile of all users"""
    try:
        all_profiles = session.exec(select(users_model.Profile)).all()
        logger.info(f"Fetched {len(all_profiles)} users from database")
        return all_profiles

    except Exception as e:
        logger.error(f"Error fetching all users: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching all users: {str(e)}"
        )