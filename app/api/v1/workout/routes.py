from fastapi import APIRouter
from .workout import router as workout_router
from .workout_log import router as workout_log_router

router = APIRouter(
    tags=["workout"],
    prefix="/workout"
    )

router.include_router(workout_router)
router.include_router(workout_log_router)
