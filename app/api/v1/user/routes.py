# app/api/v1/user/routes.py
from fastapi import APIRouter
from .user import router as user_router
from .user_log import router as user_log_router

router = APIRouter(tags=["user"],prefix="/user")

router.include_router(user_router)
router.include_router(user_log_router)
