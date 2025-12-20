# from fastapi import FastAPI
# from fastapi.templating import Jinja2Templates
# from starlette.requests import Request
# from starlette.responses import RedirectResponse
# from starlette.middleware.sessions import SessionMiddleware
# from authlib.integrations.starlette_client import OAuth, OAuthError
# from .config import CLIENT_ID, CLIENT_SECRET
# from fastapi.staticfiles import StaticFiles


# app = FastAPI()
# app.add_middleware(SessionMiddleware, secret_key="Password@123")
# app.mount("/static", StaticFiles(directory="static"), name="static")
# app.mount("/app-static", StaticFiles(directory="app/static"), name="app_static")
# oauth = OAuth()
# oauth.register(
#     name="google",
#     client_id=CLIENT_ID,
#     client_secret=CLIENT_SECRET,
#     server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
#     client_kwargs={
#         "scope": "openid email profile",
#         "redirect_uri": "http://localhost:8000/auth"
#         },
#     access_token_url="https://accounts.google.com/o/oauth2/token",
# )

# templates = Jinja2Templates(directory="templates")

# @app.get("/")
# def read_root(request: Request):
#     user = request.session.get('user')
#     if user:
#         return RedirectResponse('welcome')
#     return templates.TemplateResponse(
#         name='home.html', 
#         context={"request": request}
#         )

# @app.get("/login")
# async def login(request: Request):
#     url = request.url_for("auth")
#     return await oauth.google.authorize_redirect(request, url)


# @app.get('/welcome')
# def welcome(request: Request):
#     user = request.session.get('user')
#     if not user:
#         return RedirectResponse(url='/')
#     return templates.TemplateResponse(
#             name='welcome.html',
#             context={'request': request, 'user': dict(user)}
#             )
    



# @app.get("/auth")
# async def auth(request: Request):
#     try:
#         token = await oauth.google.authorize_access_token(
#             request,
#             claims_options={
#                 "iss": {"values": ["https://accounts.google.com", "accounts.google.com"]}
#             },
#             leeway=300,  # allow 5 minutes clock skew for iat/exp/nbf validation
#         )
#     except OAuthError as e:
#         return templates.TemplateResponse(
#             name='error.html',
#             context={'request': request}
#             )

#     user = token.get('userinfo')
#     if user:
#         request.session['user'] = dict(user)
#     return templates.TemplateResponse(
#         name='welcome.html',
#         context={'request': request, 'user': dict(user)}
#         )


# @app.get('/logout')
# def logout(request: Request):
#     request.session.pop('user')
#     request.session.clear()
#     return RedirectResponse('/')


"""
SSO OAuth utility module for Google OAuth integration.
This module provides OAuth setup and helper functions for SSO authentication.
"""
try:
    from authlib.integrations.starlette_client import OAuth
    from app.core.config import settings
except ImportError:
    OAuth = None
    settings = None


def get_oauth_client():
    """
    Creates and returns a configured OAuth client for Google authentication.
    
    Returns:
        OAuth: Configured OAuth client instance
    
    Raises:
        ImportError: If authlib is not installed
    """
    if OAuth is None:
        raise ImportError("authlib is not installed. Please install it with: pip install authlib")
    
    oauth = OAuth()
    oauth.register(
        name="google",
        client_id=settings.client_id,
        client_secret=settings.client_secret,
        server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
        client_kwargs={"scope": "openid email profile"},
    )
    return oauth
