from fastapi import APIRouter

router = APIRouter()

@router.post("/food-log")
def get_items():
    return {"Message":"food log routes"}

