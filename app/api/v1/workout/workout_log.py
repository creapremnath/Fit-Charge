from fastapi import APIRouter

router = APIRouter()

@router.get("/workout-log")
def get_items():
    return {"Message":"workoutlog routes"}

