import pytest
import jwt
from datetime import datetime, timedelta, timezone

from app.config import JWT_SECRET, JWT_ALGORITHM
from app.services.token_service import TokenService
from tests.factories.user_factory import UserFactory
from tests.factories.refresh_token_factory import RefreshTokenFactory

@pytest.fixture
def token_service(db_session):
    return TokenService(db=db_session)

@pytest.fixture
def user(db_session):
    UserFactory._meta.sqlalchemy_session = db_session
    return UserFactory.create()

class TestCreateAccessToken:
    def test_returns_valid_jwt(self, token_service):
        token = token_service.create_access_token(42)
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        
        assert payload["sub"] == "42"

    def test_token_includes_expiry(self, token_service):
        token = token_service.create_access_token(1)
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        
        assert "exp" in payload

class TestDecodeAccessToken:
    def test_valid_token_returns_user_id(self, token_service):
        token = token_service.create_access_token(7)
        
        assert token_service.decode_access_token(token) == 7

    def test_invalid_token_returns_none(self, token_service):
        assert token_service.decode_access_token("not.a.token") is None

    def test_tampered_token_returns_none(self, token_service):
        token = token_service.create_access_token(1)
        tampered = token[:-4] + "xxxx"
        
        assert token_service.decode_access_token(tampered) is None


class TestCreateRefreshToken:
    def test_returns_token_string(self, token_service, user):
        token = token_service.create_refresh_token(user.id)
        
        assert isinstance(token, str) and len(token) > 0

    def test_persists_to_db(self, token_service, user, db_session):
        from app.models.refresh_token import RefreshToken
        token = token_service.create_refresh_token(user.id)
        
        record = db_session.query(RefreshToken).filter(RefreshToken.token == token).first()
        
        assert record is not None
        assert record.user_id == user.id

    def test_expires_in_14_days(self, token_service, user, db_session):
        from app.models.refresh_token import RefreshToken
        token = token_service.create_refresh_token(user.id)
        
        record = db_session.query(RefreshToken).filter(RefreshToken.token == token).first()
        
        delta = record.expires_at - datetime.now(timezone.utc)
        assert 13 * 24 * 3600 < delta.total_seconds() <= 14 * 24 * 3600


class TestRefreshAccessToken:
    def test_valid_refresh_token_returns_new_access_token(self, token_service, user):
        refresh_token = token_service.create_refresh_token(user.id)
        access_token = token_service.refresh_access_token(refresh_token)
        
        assert access_token is not None
        
        payload = jwt.decode(access_token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        
        assert payload["sub"] == str(user.id)

    def test_invalid_token_returns_none(self, token_service):
        assert token_service.refresh_access_token("not-a-real-token") is None

    def test_expired_token_returns_none(self, token_service, user, db_session):
        RefreshTokenFactory._meta.sqlalchemy_session = db_session
        
        expired = RefreshTokenFactory.create(
            user_id=user.id,
            expires_at=datetime.now(timezone.utc) - timedelta(days=1),
        )
        
        assert token_service.refresh_access_token(expired.token) is None

    def test_refresh_token_unchanged_after_use(self, token_service, user, db_session):
        from app.models.refresh_token import RefreshToken
        refresh_token = token_service.create_refresh_token(user.id)
        
        token_service.refresh_access_token(refresh_token)
        
        record = db_session.query(RefreshToken).filter(RefreshToken.token == refresh_token).first()
        assert record is not None  # still exists, not consumed


class TestRevokeRefreshToken:
    def test_removes_token_from_db(self, token_service, user, db_session):
        from app.models.refresh_token import RefreshToken
        refresh_token = token_service.create_refresh_token(user.id)
        
        token_service.revoke_refresh_token(refresh_token)
        
        record = db_session.query(RefreshToken).filter(RefreshToken.token == refresh_token).first()
        assert record is None

    def test_unknown_token_does_not_raise(self, token_service):
        token_service.revoke_refresh_token("unknown-token")  # should not raise
