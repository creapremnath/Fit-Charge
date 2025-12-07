from fastapi import APIRouter

router = APIRouter()

@router.get("/user")
def get_items():
    return {"Message":"user routes"}

