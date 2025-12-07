from fastapi import APIRouter
from .food import router as food_router
from .food_log import router as food_log_router


router = APIRouter(
    tags=["Food"],
    prefix="/food"
)

router.include_router(food_router)
router.include_router(food_log_router)
