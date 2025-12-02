from fastapi import APIRouter
from .auth_logics import router as auth_router
from .validation_logics import router as validation_router
router = APIRouter()


router.include_router(validation_router)
router.include_router(auth_router)