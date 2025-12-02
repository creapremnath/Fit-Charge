from fastapi import APIRouter

router = APIRouter()

@router.post("/food")
def get_items():
    return {"Message":"food routes"}

