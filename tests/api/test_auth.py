import pytest
from datetime import datetime, timedelta, timezone
from tests.conftest import get_token_for

def login(client, email="test@test.com", password="test123"):
    resp = client.post("/auth/login", json={"email": email, "password": password})

    return resp

def test_login_unknown_email(client):
    response = client.post("/auth/login", json={"email": "nobody@test.com", "password": "whatever"})

    assert response.status_code == 400
    assert response.json() == {"error": {"message": "Invalid credential."}}

def test_login_valid_credentials(client, test_user):
    response = login(client)
    
    assert response.status_code == 200
    
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert isinstance(data["access_token"], str) and len(data["access_token"]) > 0
    assert isinstance(data["refresh_token"], str) and len(data["refresh_token"]) > 0

def test_login_wrong_password(client, test_user):
    response = client.post("/auth/login", json={"email": "test@test.com", "password": "wrongpass"})
    
    assert response.status_code == 400
    assert response.json() == {"error": {"message": "Invalid credential."}}

def test_refresh_returns_new_access_token(client, test_user):
    refresh_token = login(client).json()["refresh_token"]
    
    response = client.post("/auth/refresh", json={"refresh_token": refresh_token})
    
    assert response.status_code == 200
    
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" not in data

def test_refresh_invalid_token_returns_401(client):
    response = client.post("/auth/refresh", json={"refresh_token": "not-a-real-token"})
    
    assert response.status_code == 401

def test_refresh_expired_token_returns_401(client, test_user, db_session):
    from tests.factories.refresh_token_factory import RefreshTokenFactory
    
    RefreshTokenFactory._meta.sqlalchemy_session = db_session
    expired = RefreshTokenFactory.create(
        user_id=test_user.id,
        expires_at=datetime.now(timezone.utc) - timedelta(days=1),
    )
    
    response = client.post("/auth/refresh", json={"refresh_token": expired.token})
    
    assert response.status_code == 401

def test_logout_revokes_refresh_token(client, test_user):
    data = login(client).json()
    access_token = data["access_token"]
    refresh_token = data["refresh_token"]

    response = client.post("/auth/logout", headers={"Authorization": f"Bearer {access_token}"})

    assert response.status_code == 200
    assert response.json() == {}

    response = client.post("/auth/refresh", json={"refresh_token": refresh_token})
    assert response.status_code == 401


def test_logout_with_invalid_token_returns_401(client):
    response = client.post("/auth/logout", headers={"Authorization": "Bearer invalid-token"})

    assert response.status_code == 401
