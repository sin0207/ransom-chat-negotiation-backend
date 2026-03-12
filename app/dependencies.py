from typing import Annotated
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.models.user import User
from app.services.auth_service import AuthService

bearer_scheme = HTTPBearer()

async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(bearer_scheme)],
    auth_service: Annotated[AuthService, Depends(AuthService)],
) -> User:
    user = auth_service.get_authenticated_user(credentials.credentials)
    
    if user is None:
        raise HTTPException(status_code=401, detail="Invalid token or user not found")

    return user

async def require_authenticated(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    return current_user

async def require_admin(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")

    return current_user
