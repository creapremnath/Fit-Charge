from fastapi import APIRouter, Depends, Request, HTTPException, status
from pydantic import Json
from app.api.v1.user.models import User
from app.core.database import get_session
from sqlalchemy.orm import Session
from app.api.v1.authentication.schemas import SignUp, LoginRequest, SSOLoginResponse, SSOCallbackResponse
from fastapi.responses import JSONResponse
from app.auth.utils import encrypt_password, verify_password
from app.auth.oauth2 import create_access_token, create_refresh_token, verify_refresh_token
from app.core.config import settings


from google.oauth2 import id_token
from google.auth.transport import requests



# Optional SSO imports - handle gracefully if authlib is not installed
# Note: SSO endpoints use manual OAuth flow, so authlib is not required
try:
    from app.auth.sso import get_oauth_client
    from authlib.integrations.starlette_client import OAuthError
    SSO_AVAILABLE = True
except ImportError:
    SSO_AVAILABLE = True  # SSO endpoints work without authlib (using manual OAuth flow)
    OAuthError = Exception  # Fallback for type hints
router = APIRouter(
    tags=["Authentication"]
)

@router.post("/login")
def login(request: LoginRequest, session: Session = Depends(get_session)):
    valid_user = session.query(User).filter(User.email == request.email, User.is_active == True, User.is_verified == True).first()
    if not valid_user:
        return JSONResponse(
            status_code=400,
            content={"Message": "Verified Email ID not found"}
        )
    if not verify_password(valid_user.password, request.password):
        return JSONResponse(
            status_code=400,
            content={"Message": "Invalid password"}
        )

    user_data = {
        "user_id": valid_user.user_id,
        "username": valid_user.username,
        "role": valid_user.role,
    }
    access_token = create_access_token(user_data)
    refresh_token = create_refresh_token(user_data)
    return JSONResponse(
        status_code=200,
        content={"Message": "Login successful", "access_token": access_token, "refresh_token": refresh_token}
    )




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
def refresh_token(Token:str):
    token_data = verify_refresh_token(Token)
    user_data = {
        "user_id": token_data.user_id,
        "username": token_data.username,
        "role": token_data.role,
    }
    new_access_token = create_access_token(user_data)
    return JSONResponse(
        status_code=200,
        content={"Message":"New access token generated", "access_token": new_access_token}
    )

import time

# Simple in-memory state store (DEV / single-instance)
OAUTH_STATE_STORE = {}
STATE_TTL_SECONDS = 300  # 5 minutes


@router.get("/sso-login", response_model=SSOLoginResponse)
async def sso_login(request: Request):
    try:
        from urllib.parse import urlencode
        import secrets

        base_url = str(request.base_url).rstrip('/')
        callback_url = f"{base_url}/api/v1/sso-callback"

        # Generate state
        state = secrets.token_urlsafe(32)

        # ✅ STORE STATE SERVER-SIDE (NOT SESSION)
        OAUTH_STATE_STORE[state] = time.time()

        auth_endpoint = "https://accounts.google.com/o/oauth2/v2/auth"
        params = {
            "response_type": "code",
            "client_id": settings.client_id,
            "redirect_uri": callback_url,
            "scope": "openid profile email",
            "access_type": "offline",
            "state": state,
        }

        authorization_url = f"{auth_endpoint}?{urlencode(params)}"

        return SSOLoginResponse(
            authorization_url=authorization_url,
            message="Redirect user to Google login"
        )

    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"Message": f"Failed to initiate SSO login: {str(e)}"}
        )

@router.get("/sso-callback", response_model=SSOCallbackResponse)
async def sso_callback(request: Request, session: Session = Depends(get_session)):
    query_params = dict(request.query_params)
    received_state = query_params.get("state")
    code = query_params.get("code")

    if not received_state or not code:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"Message": "OAuth error: Missing state or code"}
        )

    # ✅ VERIFY STATE FROM SERVER STORE
    state_time = OAUTH_STATE_STORE.pop(received_state, None)
    if not state_time or time.time() - state_time > STATE_TTL_SECONDS:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"Message": "OAuth error: mismatching_state or expired state"}
        )

    try:
        import httpx

        # ✅ MANUAL TOKEN EXCHANGE (NO AUTHLIB STATE)
        async with httpx.AsyncClient() as client:
            token_resp = await client.post(
                "https://oauth2.googleapis.com/token",
                data={
                    "client_id": settings.client_id,
                    "client_secret": settings.client_secret,
                    "code": code,
                    "grant_type": "authorization_code",
                    "redirect_uri": f"{str(request.base_url).rstrip('/')}/api/v1/sso-callback",
                },
            )

        token_data = token_resp.json()
        id_token_value = token_data.get("id_token")

        if not id_token_value:
            raise Exception("Missing id_token from Google")

        from google.oauth2 import id_token
        from google.auth.transport import requests as google_requests

        id_info = id_token.verify_oauth2_token(
            id_token_value,
            google_requests.Request(),
            settings.client_id,
            clock_skew_in_seconds=300,  # Allow 5 minutes clock skew
        )

        email = id_info.get("email")
        name = id_info.get("name", "")
        picture = id_info.get("picture")

        if not email:
            raise Exception("Email not provided by Google")

        # ---- USER LOGIC (UNCHANGED) ----
        existing_user = session.query(User).filter(User.email == email).first()

        if existing_user:
            user = existing_user
        else:
            user = User(
                email=email,
                username=name or email.split("@")[0],
                profile_pic_url=picture,
                is_verified=True,
                is_active=True,
                role=1,
            )
            session.add(user)

        session.commit()
        session.refresh(user)

        user_data = {
            "user_id": user.user_id,
            "username": user.username,
            "role": user.role,
        }

        return SSOCallbackResponse(
            message="SSO login successful",
            access_token=create_access_token(user_data),
            refresh_token=create_refresh_token(user_data),
            user_id=user.user_id,
        )

    except Exception as e:
        session.rollback()
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"Message": f"Failed to process OAuth callback: {str(e)}"}
        )


@router.post("/forgot-password")
def forgot_password():
    return {"Message":"Forgot password routes"}

@router.get("/reset-password")
def reset_password():
    return {"Message":"Reset password routes"}