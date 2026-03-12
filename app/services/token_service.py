import secrets
from datetime import datetime, timedelta, timezone
import jwt
from fastapi import Depends
from sqlalchemy.orm import Session

from app.config import JWT_SECRET, JWT_ALGORITHM, JWT_EXPIRE_MINUTES, REFRESH_TOKEN_EXPIRE_DAYS
from app.database import get_db
from app.models.refresh_token import RefreshToken

class TokenService:
    def __init__(self, db: Session = Depends(get_db)):
        self.db = db

    def create_access_token(self, user_id: int) -> str:
        expire = datetime.now(timezone.utc) + timedelta(minutes=JWT_EXPIRE_MINUTES)

        return jwt.encode({"sub": str(user_id), "exp": expire}, JWT_SECRET, algorithm=JWT_ALGORITHM)

    def decode_access_token(self, token: str) -> int | None:
        try:
            payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])

            return int(payload.get("sub"))
        except jwt.PyJWTError:
            return None

    def create_refresh_token(self, user_id: int) -> str:
        token = secrets.token_urlsafe(32)
        expires_at = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        self.db.add(RefreshToken(token=token, user_id=user_id, expires_at=expires_at))
        self.db.commit()

        return token

    def refresh_access_token(self, refresh_token: str) -> str | None:
        record = (
            self.db.query(RefreshToken)
            .filter(
                RefreshToken.token == refresh_token,
                RefreshToken.expires_at > datetime.now(timezone.utc),
            )
            .first()
        )

        if record is None:
            return None

        return self.create_access_token(record.user_id)

    def revoke_refresh_token(self, token: str) -> None:
        record = self.db.query(RefreshToken).filter(RefreshToken.token == token).first()

        if record:
            self.db.delete(record)
            self.db.commit()

    def revoke_all_user_refresh_tokens(self, user_id: int) -> None:
        self.db.query(RefreshToken).filter(RefreshToken.user_id == user_id).delete()
        self.db.commit()
