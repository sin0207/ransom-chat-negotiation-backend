import pytest
from tests.factories.user_factory import UserFactory
from app.services.user_service import UserService

@pytest.fixture
def user_service(db_session):
    return UserService(db=db_session)

@pytest.fixture
def user(db_session):
    UserFactory._meta.sqlalchemy_session = db_session

    return UserFactory.create(email="test@test.com")

class TestGetByEmail:
    def test_returns_user_when_found(self, user_service, user):
        result = user_service.get_by_email("test@test.com")
        
        assert result is not None
        assert result.id == user.id

    def test_returns_none_when_not_found(self, user_service):
        result = user_service.get_by_email("nobody@test.com")
        
        assert result is None

class TestGetById:
    def test_returns_user_when_found(self, user_service, user):
        result = user_service.get_by_id(user.id)
        
        assert result is not None
        assert result.email == user.email

    def test_returns_none_when_not_found(self, user_service):
        result = user_service.get_by_id(99999)
        
        assert result is None
