from fastapi import APIRouter

router = APIRouter()

@router.get("/workouts")
def get_items():
    return {"Message":"workouts routes"}

