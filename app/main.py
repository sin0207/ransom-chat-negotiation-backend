from fastapi import Depends, FastAPI

from app.routers import auth

app = FastAPI()

app.include_router(
    auth.router,
    prefix="/auth",
    tags=["auth"],
)
