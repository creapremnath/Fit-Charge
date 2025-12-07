from fastapi import APIRouter

router = APIRouter()

@router.post("/user-log")
def get_items():
    return {"Message":"user log routes"}

