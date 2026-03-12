from fastapi import Depends, FastAPI

from app.dependencies import require_admin
from app.routers import auth, admin

app = FastAPI()

app.include_router(
    auth.router,
    prefix="/auth",
    tags=["auth"],
)

app.include_router(
    admin.router,
    prefix="/admin",
    tags=["admin"],
    dependencies=[Depends(require_admin)],
)
