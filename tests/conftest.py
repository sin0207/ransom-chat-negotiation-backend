import pytest
import bcrypt as _bcrypt
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

from app.database import Base, get_db
from app.main import app

TEST_DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/ransom_chat_test"

test_engine = create_engine(TEST_DATABASE_URL, poolclass=NullPool)
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

@pytest.fixture(autouse=True)
def setup_db():
    import app.models.user  # noqa: F401

    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)

def override_get_db():
    db = TestSessionLocal()

    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


@pytest.fixture
def db_session():
    db = TestSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def test_user(db_session):
    from tests.factories.user_factory import UserFactory

    UserFactory._meta.sqlalchemy_session = db_session
    return UserFactory.create(email="test@test.com")


@pytest.fixture
def admin_user(db_session):
    from tests.factories.user_factory import UserFactory

    UserFactory._meta.sqlalchemy_session = db_session
    return UserFactory.create(email="admin@test.com", role="admin")


def get_token_for(client, email: str, password: str = "test123") -> str:
    resp = client.post("/auth/login", json={"email": email, "password": password})
    return resp.json()["access_token"]
