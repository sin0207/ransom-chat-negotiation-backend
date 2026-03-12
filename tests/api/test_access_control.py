from tests.conftest import get_token_for

class TestAdminAuthorization:
    def test_no_token_returns_403(self, client):
        response = client.post("/admin/")

        assert response.status_code == 403

    def test_invalid_token_returns_401(self, client):
        response = client.post("/admin/", headers={"Authorization": "Bearer invalid.token.here"})
        
        assert response.status_code == 401

    def test_learner_token_returns_403(self, client, test_user):
        token = get_token_for(client, "test@test.com")
        
        response = client.post("/admin/", headers={"Authorization": f"Bearer {token}"})
        
        assert response.status_code == 403

    def test_admin_token_grants_access(self, client, admin_user):
        token = get_token_for(client, "admin@test.com")
        
        response = client.post("/admin/", headers={"Authorization": f"Bearer {token}"})
        
        assert response.status_code == 200
