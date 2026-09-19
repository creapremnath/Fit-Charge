from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from app.core.database import get_session
from app.auth.oauth2 import get_current_user
from app.api.v1.authentication.schemas import TokenData
from .models import User, UserSettings
from .schemas import UserSettingsUpdate, UserSettingsResponse

router = APIRouter()


@router.get("/settings", response_model=UserSettingsResponse)
def get_user_settings(
    current_user: TokenData = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Get current user settings. If settings do not exist for the user yet,
    initialize with default preferences.
    """
    settings = session.query(UserSettings).filter(UserSettings.user_id == current_user.user_id).first()
    
    if not settings:
        settings = UserSettings(user_id=current_user.user_id)
        session.add(settings)
        session.commit()
        session.refresh(settings)

    return settings


@router.patch("/settings", response_model=UserSettingsResponse)
@router.put("/settings", response_model=UserSettingsResponse)
def update_user_settings(
    payload: UserSettingsUpdate,
    current_user: TokenData = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Update settings/preferences for the current user.
    """
    settings = session.query(UserSettings).filter(UserSettings.user_id == current_user.user_id).first()
    
    if not settings:
        settings = UserSettings(user_id=current_user.user_id)
        session.add(settings)
        session.flush()

    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if value is not None:
            setattr(settings, field, value)

    session.commit()
    session.refresh(settings)
    return settings
