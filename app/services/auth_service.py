import bcrypt as _bcrypt
from fastapi import Depends

from app.models.user import User
from app.services.token_service import TokenService
from app.services.user_service import UserService

class AuthService:
    def __init__(
        self,
        user_service: UserService = Depends(UserService),
        token_service: TokenService = Depends(TokenService),
    ):
        self.user_service = user_service
        self.token_service = token_service

    def hash_password(self, plain: str) -> str:
        return _bcrypt.hashpw(plain.encode(), _bcrypt.gensalt()).decode()

    def verify_password(self, plain: str, hashed: str) -> bool:
        return _bcrypt.checkpw(plain.encode(), hashed.encode())

    def login(self, email: str, password: str) -> tuple[str, str] | None:
        user = self.user_service.get_by_email(email)

        if user is None or not self.verify_password(password, user.password):
            return None

        access_token = self.token_service.create_access_token(user.id)
        refresh_token = self.token_service.create_refresh_token(user.id)

        return access_token, refresh_token

    def get_authenticated_user(self, access_token: str) -> User | None:
        user_id = self.token_service.decode_access_token(access_token)

        if user_id is None:
            return None

        return self.user_service.get_by_id(user_id)
