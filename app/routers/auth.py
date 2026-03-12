from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from app.dependencies import require_authenticated
from app.models.user import User
from app.services.auth_service import AuthService
from app.services.token_service import TokenService

router = APIRouter()

INVALID_CREDENTIAL_RESPONSE = JSONResponse(
    status_code=400,
    content={"error": {"message": "Invalid credential."}},
)

class LoginRequest(BaseModel):
    email: str
    password: str

class RefreshRequest(BaseModel):
    refresh_token: str


@router.post("/login")
async def login(body: LoginRequest, auth_service: Annotated[AuthService, Depends(AuthService)]):
    result = auth_service.login(body.email, body.password)

    if result is None:
        return INVALID_CREDENTIAL_RESPONSE
    
    access_token, refresh_token = result
    
    return {"access_token": access_token, "refresh_token": refresh_token}

@router.post("/refresh")
async def refresh(body: RefreshRequest, token_service: Annotated[TokenService, Depends(TokenService)]):
    access_token = token_service.refresh_access_token(body.refresh_token)
    
    if access_token is None:
        raise HTTPException(status_code=401, detail="Refresh token expired or invalid. Please log in again.")
    
    return {"access_token": access_token}

@router.post("/logout")
async def logout(
    current_user: Annotated[User, Depends(require_authenticated)],
    token_service: Annotated[TokenService, Depends(TokenService)],
):
    token_service.revoke_all_user_refresh_tokens(current_user.id)

    return {}
