from fastapi import APIRouter

from ..dependencies import require_admin

router = APIRouter()

@router.post("/")
async def update_admin():
    return {"message": "Admin getting schwifty"}
