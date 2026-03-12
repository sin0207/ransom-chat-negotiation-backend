import pytest
import jwt

from app.config import JWT_SECRET, JWT_ALGORITHM
from app.services.auth_service import AuthService
from app.services.token_service import TokenService
from app.services.user_service import UserService
from tests.factories.user_factory import UserFactory

@pytest.fixture
def user_service(db_session):
    return UserService(db=db_session)

@pytest.fixture
def token_service(db_session):
    return TokenService(db=db_session)

@pytest.fixture
def auth_service(user_service, token_service):
    return AuthService(user_service=user_service, token_service=token_service)

@pytest.fixture
def user(db_session):
    UserFactory._meta.sqlalchemy_session = db_session
    return UserFactory.create(email="test@test.com")

class TestHashPassword:
    def test_returns_bcrypt_hash(self, auth_service):
        hashed = auth_service.hash_password("secret")
        assert hashed.startswith("$2b$")

    def test_different_calls_produce_different_hashes(self, auth_service):
        h1 = auth_service.hash_password("secret")
        h2 = auth_service.hash_password("secret")
        assert h1 != h2

class TestVerifyPassword:
    def test_correct_password_returns_true(self, auth_service):
        hashed = auth_service.hash_password("secret")
        assert auth_service.verify_password("secret", hashed) is True

    def test_wrong_password_returns_false(self, auth_service):
        hashed = auth_service.hash_password("secret")
        assert auth_service.verify_password("wrong", hashed) is False

class TestLogin:
    def test_valid_credentials_return_both_tokens(self, auth_service, user):
        result = auth_service.login("test@test.com", "test123")
        
        assert result is not None
        
        access_token, refresh_token = result
        payload = jwt.decode(access_token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        
        assert payload["sub"] == str(user.id)
        assert isinstance(refresh_token, str) and len(refresh_token) > 0

    def test_unknown_email_returns_none(self, auth_service):
        assert auth_service.login("nobody@test.com", "test123") is None

    def test_wrong_password_returns_none(self, auth_service, user):
        assert auth_service.login("test@test.com", "wrongpass") is None

class TestGetAuthenticatedUser:
    def test_valid_token_returns_user(self, auth_service, token_service, user):
        token = token_service.create_access_token(user.id)
        
        result = auth_service.get_authenticated_user(token)
        
        assert result is not None
        assert result.id == user.id

    def test_invalid_token_returns_none(self, auth_service):
        assert auth_service.get_authenticated_user("bad.token.here") is None

    def test_token_for_deleted_user_returns_none(self, auth_service, token_service, user, db_session):
        token = token_service.create_access_token(user.id)
        db_session.delete(user)
        db_session.commit()
        
        assert auth_service.get_authenticated_user(token) is None
