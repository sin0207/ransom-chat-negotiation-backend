import secrets
from datetime import datetime, timedelta, timezone
import factory
from factory.alchemy import SQLAlchemyModelFactory

from app.models.refresh_token import RefreshToken

class RefreshTokenFactory(SQLAlchemyModelFactory):
    class Meta:
        model = RefreshToken
        sqlalchemy_session = None
        sqlalchemy_session_persistence = "commit"

    token = factory.LazyFunction(lambda: secrets.token_urlsafe(32))
    user_id = None  # must be provided by caller
    expires_at = factory.LazyFunction(lambda: datetime.now(timezone.utc) + timedelta(days=14))
